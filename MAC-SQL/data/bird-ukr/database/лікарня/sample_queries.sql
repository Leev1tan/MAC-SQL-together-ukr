-- Sample queries for Hospital (лікарня) database
-- Created for Ukrainian Text-to-SQL dataset

-- Query 1: Simple query - Find all departments
-- Запит 1: Простий запит - Знайти всі відділення
SELECT * FROM відділення;

-- Query 2: Filter by condition - Find all active doctors
-- Запит 2: Фільтрація за умовою - Знайти всіх активних лікарів
SELECT * FROM лікарі WHERE активний = TRUE;

-- Query 3: Sorting - Find all patients sorted by registration date (newest first)
-- Запит 3: Сортування - Знайти всіх пацієнтів, відсортованих за датою реєстрації (від найновіших)
SELECT * FROM пацієнти ORDER BY дата_реєстрації DESC;

-- Query 4: Aggregation - Count patients by gender
-- Запит 4: Агрегація - Порахувати пацієнтів за статтю
SELECT стать, COUNT(*) AS кількість FROM пацієнти GROUP BY стать;

-- Query 5: Simple JOIN - Find all doctors with their department names
-- Запит 5: Простий JOIN - Знайти всіх лікарів з назвами їхніх відділень
SELECT л.ід, л.прізвище, л.імя, в.назва AS відділення
FROM лікарі л
JOIN відділення в ON л.відділення_ід = в.ід;

-- Query 6: Multiple JOINs - Find all visits with patient and doctor information
-- Запит 6: Кілька JOIN-ів - Знайти всі візити з інформацією про пацієнта та лікаря
SELECT в.ід, в.дата_час, 
       п.прізвище AS пацієнт_прізвище, п.імя AS пацієнт_імя,
       л.прізвище AS лікар_прізвище, л.імя AS лікар_імя
FROM візити в
JOIN пацієнти п ON в.пацієнт_ід = п.ід
JOIN персонал л ON в.лікар_ід = л.ід;

-- Query 7: Filtering with JOIN - Find all diagnoses for a specific patient
-- Запит 7: Фільтрація з JOIN - Знайти всі діагнози для конкретного пацієнта
SELECT д.ід, х.назва AS діагноз, д.дата_встановлення, д.статус
FROM діагнози д
JOIN хвороби х ON д.хвороба_ід = х.ід
WHERE д.пацієнт_ід = 3;

-- Query 8: Aggregation with GROUP BY - Count diagnoses by disease type
-- Запит 8: Агрегація з GROUP BY - Порахувати діагнози за типом захворювання
SELECT тх.назва AS тип_хвороби, COUNT(*) AS кількість_діагнозів
FROM діагнози д
JOIN хвороби х ON д.хвороба_ід = х.ід
JOIN типи_хвороб тх ON х.тип_ід = тх.ід
GROUP BY тх.назва
ORDER BY кількість_діагнозів DESC;

-- Query 9: Subquery - Find patients who have never had a hospitalization
-- Запит 9: Підзапит - Знайти пацієнтів, які ніколи не були госпіталізовані
SELECT * FROM пацієнти
WHERE ід NOT IN (SELECT DISTINCT пацієнт_ід FROM госпіталізації);

-- Query 10: HAVING clause - Find departments with more than 5 doctors
-- Запит 10: Клауза HAVING - Знайти відділення з більше ніж 5 лікарями
SELECT в.назва AS відділення, COUNT(*) AS кількість_лікарів
FROM персонал п
JOIN відділення в ON п.відділення_ід = в.ід
JOIN посади_персоналу пп ON п.посада_ід = пп.ід
WHERE пп.категорія = 'лікар'
GROUP BY в.назва
HAVING COUNT(*) > 5;

-- Query 11: Complex JOINs - Find all payments with patient, service, and insurance information
-- Запит 11: Складні JOIN-и - Знайти всі оплати з інформацією про пацієнта, послугу та страхування
SELECT о.ід, о.дата_час, о.сума, о.сума_страхування,
       п.прізвище AS пацієнт_прізвище, п.імя AS пацієнт_імя,
       COALESCE(пос.назва, 'Немає') AS назва_послуги,
       COALESCE(ск.назва, 'Без страхування') AS страхова_компанія
FROM оплати о
JOIN пацієнти п ON о.пацієнт_ід = п.ід
LEFT JOIN деталі_оплати до ON о.ід = до.оплата_ід
LEFT JOIN послуги пос ON до.послуга_ід = пос.ід
LEFT JOIN страховки_пацієнтів сп ON о.страховка_ід = сп.ід
LEFT JOIN страхові_компанії ск ON сп.страхова_компанія_ід = ск.ід;

-- Query 12: Window function - Rank doctors by salary within each department
-- Запит 12: Віконна функція - Ранжування лікарів за зарплатою в межах кожного відділення
SELECT л.прізвище, л.імя, л.зарплата, в.назва AS відділення,
       RANK() OVER (PARTITION BY л.відділення_ід ORDER BY л.зарплата DESC) AS ранг_по_зарплаті
FROM лікарі л
JOIN відділення в ON л.відділення_ід = в.ід;

-- Query 13: EXISTS - Find patients who have at least one diagnosis
-- Запит 13: EXISTS - Знайти пацієнтів, які мають принаймні один діагноз
SELECT п.ід, п.прізвище, п.імя
FROM пацієнти п
WHERE EXISTS (SELECT 1 FROM діагнози д WHERE д.пацієнт_ід = п.ід);

-- Query 14: UNION - List all contact emails (staff and patients)
-- Запит 14: UNION - Список всіх контактних електронних адрес (персонал та пацієнти)
SELECT прізвище, імя, електронна_пошта, 'персонал' AS тип
FROM персонал
WHERE електронна_пошта IS NOT NULL
UNION
SELECT прізвище, імя, електронна_пошта, 'пацієнт' AS тип
FROM пацієнти
WHERE електронна_пошта IS NOT NULL;

-- Query 15: CTE (Common Table Expression) - Find the average payment amount by payment type
-- Запит 15: CTE (Загальне Табличне Вираження) - Знайти середню суму оплати за типом оплати
WITH платежі_за_типом AS (
    SELECT тип, сума, спосіб_оплати
    FROM оплати
    WHERE статус = 'оплачено'
)
SELECT тип, спосіб_оплати, 
       COUNT(*) AS кількість, 
       AVG(сума) AS середня_сума,
       MIN(сума) AS мінімальна_сума,
       MAX(сума) AS максимальна_сума
FROM платежі_за_типом
GROUP BY тип, спосіб_оплати
ORDER BY тип, середня_сума DESC; 