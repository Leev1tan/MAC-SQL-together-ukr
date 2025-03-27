-- Sample queries for Library (бібліотека) database
-- Created for Ukrainian Text-to-SQL dataset

-- Query 1: Simple query - Find all books
-- Запит 1: Простий запит - Знайти всі книги
SELECT * FROM книги;

-- Query 2: Filter by condition - Find books published after 2015
-- Запит 2: Фільтрація за умовою - Знайти книги, видані після 2015 року
SELECT ід, назва, рік_видання FROM книги WHERE рік_видання > 2015;

-- Query 3: Sorting - Find all authors sorted by surname alphabetically
-- Запит 3: Сортування - Знайти всіх авторів, відсортованих за прізвищем за алфавітом
SELECT ід, прізвище, імя FROM автори ORDER BY прізвище, імя;

-- Query 4: Aggregation - Count books by language
-- Запит 4: Агрегація - Порахувати книги за мовою
SELECT м.назва AS мова, COUNT(*) AS кількість_книг 
FROM книги к
JOIN мови м ON к.мова_ід = м.ід
GROUP BY м.назва
ORDER BY кількість_книг DESC;

-- Query 5: Simple JOIN - Find books with their authors
-- Запит 5: Простий JOIN - Знайти книги з їхніми авторами
SELECT к.назва AS книга, CONCAT(а.прізвище, ' ', а.імя) AS автор
FROM книги к
JOIN книга_автор ка ON к.ід = ка.книга_ід
JOIN автори а ON ка.автор_ід = а.ід
ORDER BY к.назва;

-- Query 6: Multiple JOINs - Find all loans with book, reader, and librarian information
-- Запит 6: Кілька JOIN-ів - Знайти всі видачі з інформацією про книгу, читача та бібліотекаря
SELECT в.ід, в.дата_видачі, в.очікувана_дата_повернення,
       к.назва AS книга,
       CONCAT(ч.прізвище, ' ', ч.імя) AS читач,
       CONCAT(п.прізвище, ' ', п.імя) AS бібліотекар
FROM видачі в
JOIN примірники пр ON в.примірник_ід = пр.ід
JOIN книги к ON пр.книга_ід = к.ід
JOIN читачі ч ON в.читач_ід = ч.ід
JOIN працівники п ON в.працівник_видав_ід = п.ід;

-- Query 7: Filtering with JOIN - Find all reservations for a specific reader
-- Запит 7: Фільтрація з JOIN - Знайти всі резервації для конкретного читача
SELECT р.ід, к.назва AS книга, р.дата_резервації, р.статус
FROM резервації р
JOIN книги к ON р.книга_ід = к.ід
WHERE р.читач_ід = 3;

-- Query 8: Aggregation with GROUP BY - Count books by genre
-- Запит 8: Агрегація з GROUP BY - Порахувати книги за жанром
SELECT ж.назва AS жанр, COUNT(*) AS кількість_книг
FROM книга_жанр кж
JOIN жанри ж ON кж.жанр_ід = ж.ід
GROUP BY ж.назва
ORDER BY кількість_книг DESC;

-- Query 9: Subquery - Find readers who have never borrowed a book
-- Запит 9: Підзапит - Знайти читачів, які ніколи не брали книг
SELECT ід, прізвище, імя, дата_реєстрації
FROM читачі
WHERE ід NOT IN (SELECT DISTINCT читач_ід FROM видачі);

-- Query 10: HAVING clause - Find genres with more than 5 books
-- Запит 10: Клауза HAVING - Знайти жанри з більше ніж 5 книгами
SELECT ж.назва AS жанр, COUNT(*) AS кількість_книг
FROM книга_жанр кж
JOIN жанри ж ON кж.жанр_ід = ж.ід
GROUP BY ж.назва
HAVING COUNT(*) > 5
ORDER BY кількість_книг DESC;

-- Query 11: Complex JOINs - Find most popular books with their authors and genres
-- Запит 11: Складні JOIN-и - Знайти найпопулярніші книги з їхніми авторами та жанрами
SELECT к.назва AS книга, 
       STRING_AGG(DISTINCT CONCAT(а.прізвище, ' ', а.імя), ', ') AS автори,
       STRING_AGG(DISTINCT ж.назва, ', ') AS жанри,
       COUNT(DISTINCT в.ід) AS кількість_видач
FROM книги к
JOIN примірники пр ON к.ід = пр.книга_ід
JOIN видачі в ON пр.ід = в.примірник_ід
JOIN книга_автор ка ON к.ід = ка.книга_ід
JOIN автори а ON ка.автор_ід = а.ід
JOIN книга_жанр кж ON к.ід = кж.книга_ід
JOIN жанри ж ON кж.жанр_ід = ж.ід
GROUP BY к.ід, к.назва
HAVING COUNT(DISTINCT в.ід) > 2
ORDER BY кількість_видач DESC;

-- Query 12: Window function - Rank books by number of copies within each genre
-- Запит 12: Віконна функція - Ранжувати книги за кількістю примірників у межах кожного жанру
SELECT ж.назва AS жанр, к.назва AS книга,
       COUNT(п.ід) AS кількість_примірників,
       RANK() OVER (PARTITION BY ж.ід ORDER BY COUNT(п.ід) DESC) AS ранг_у_жанрі
FROM жанри ж
JOIN книга_жанр кж ON ж.ід = кж.жанр_ід
JOIN книги к ON кж.книга_ід = к.ід
JOIN примірники п ON к.ід = п.книга_ід
GROUP BY ж.ід, ж.назва, к.ід, к.назва;

-- Query 13: EXISTS - Find employees who have handled at least one loan
-- Запит 13: EXISTS - Знайти працівників, які обслужили принаймні одну видачу
SELECT п.ід, п.прізвище, п.імя, пос.назва AS посада
FROM працівники п
JOIN посади пос ON п.посада_ід = пос.ід
WHERE EXISTS (
    SELECT 1 FROM видачі в WHERE в.працівник_видав_ід = п.ід
);

-- Query 14: UNION - List all events and services available in the library
-- Запит 14: UNION - Список всіх подій та послуг, доступних у бібліотеці
SELECT назва, дата_початку AS дата, 'подія' AS тип
FROM події
WHERE статус = 'плановано' AND дата_початку > CURRENT_DATE
UNION
SELECT назва, NULL AS дата, 'послуга' AS тип
FROM послуги
WHERE доступна = TRUE
ORDER BY тип, дата;

-- Query 15: CTE (Common Table Expression) - Find readers with overdue books
-- Запит 15: CTE (Загальне Табличне Вираження) - Знайти читачів з простроченими книгами
WITH прострочення AS (
    SELECT в.читач_ід, в.дата_видачі, в.очікувана_дата_повернення,
           к.назва AS книга,
           CURRENT_DATE - в.очікувана_дата_повернення AS днів_прострочення
    FROM видачі в
    JOIN примірники п ON в.примірник_ід = п.ід
    JOIN книги к ON п.книга_ід = к.ід
    WHERE в.дата_повернення IS NULL 
    AND в.очікувана_дата_повернення < CURRENT_DATE
)
SELECT ч.прізвище, ч.імя, ч.телефон, 
       COUNT(*) AS кількість_прострочених,
       MAX(п.днів_прострочення) AS максимальне_прострочення,
       STRING_AGG(п.книга, ', ') AS прострочені_книги
FROM читачі ч
JOIN прострочення п ON ч.ід = п.читач_ід
GROUP BY ч.ід, ч.прізвище, ч.імя, ч.телефон
ORDER BY максимальне_прострочення DESC;

-- Query 16: Self-join - Find employees in the same department
-- Запит 16: Self-join - Знайти працівників з того самого відділу
SELECT п1.прізвище AS працівник1, п2.прізвище AS працівник2, в.назва AS відділ
FROM працівник_відділ пв1
JOIN працівник_відділ пв2 ON пв1.відділ_ід = пв2.відділ_ід AND пв1.працівник_ід < пв2.працівник_ід
JOIN працівники п1 ON пв1.працівник_ід = п1.ід
JOIN працівники п2 ON пв2.працівник_ід = п2.ід
JOIN відділи в ON пв1.відділ_ід = в.ід
WHERE пв1.основний = TRUE AND пв2.основний = TRUE;

-- Query 17: CASE expression - Categorize books by age
-- Запит 17: Вираз CASE - Категоризувати книги за віком
SELECT назва,
       CASE 
           WHEN рік_видання >= 2020 THEN 'Нова'
           WHEN рік_видання >= 2010 THEN 'Сучасна'
           WHEN рік_видання >= 2000 THEN 'Відносно нова'
           WHEN рік_видання >= 1980 THEN 'Класика'
           ELSE 'Старовинна'
       END AS категорія_віку
FROM книги
ORDER BY рік_видання DESC;

-- Query 18: INTERSECT - Find readers who have both active loans and reservations
-- Запит 18: INTERSECT - Знайти читачів, які мають як активні видачі, так і резервації
SELECT ч.ід, ч.прізвище, ч.імя
FROM читачі ч
WHERE ч.ід IN (SELECT читач_ід FROM видачі WHERE дата_повернення IS NULL)
  AND ч.ід IN (SELECT читач_ід FROM резервації WHERE статус = 'очікує');

-- Query 19: Outer join - List all books with loan information, including those never loaned
-- Запит 19: Зовнішнє об'єднання - Список всіх книг з інформацією про видачі, включаючи ті, які ніколи не видавалися
SELECT к.назва, COUNT(в.ід) AS кількість_видач,
       MAX(в.дата_видачі) AS остання_видача
FROM книги к
LEFT JOIN примірники п ON к.ід = п.книга_ід
LEFT JOIN видачі в ON п.ід = в.примірник_ід
GROUP BY к.ід, к.назва
ORDER BY кількість_видач DESC;

-- Query 20: EXCEPT - Find books that have copies but have never been loaned
-- Запит 20: EXCEPT - Знайти книги, які мають примірники, але ніколи не видавалися
SELECT к.ід, к.назва
FROM книги к
JOIN примірники п ON к.ід = п.книга_ід
EXCEPT
SELECT к.ід, к.назва
FROM книги к
JOIN примірники п ON к.ід = п.книга_ід
JOIN видачі в ON п.ід = в.примірник_ід; 