-- Data for University Library (Бібліотечний фонд університету)
-- Created for Ukrainian Text-to-SQL dataset

-- Create tables for university library

-- Library collection departments (бібліотечні_фонди)
CREATE TABLE бібліотечні_фонди (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    розташування VARCHAR(100),
    дата_створення DATE,
    відповідальний_ід INTEGER REFERENCES викладачі(ід),
    контактний_телефон VARCHAR(15),
    електронна_пошта VARCHAR(100),
    кількість_книг INTEGER DEFAULT 0,
    примітки TEXT
);

-- University books (книги_університету)
CREATE TABLE книги_університету (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(200) NOT NULL,
    автор VARCHAR(150),
    видавництво VARCHAR(100),
    рік_видання INTEGER,
    кількість_сторінок INTEGER,
    isbn VARCHAR(20),
    мова VARCHAR(50) DEFAULT 'українська',
    фонд_ід INTEGER NOT NULL REFERENCES бібліотечні_фонди(ід),
    дата_придбання DATE,
    вартість DECIMAL(10, 2),
    тип VARCHAR(50) DEFAULT 'підручник', -- підручник, посібник, монографія, тощо
    кількість_примірників INTEGER DEFAULT 1,
    доступна_кількість INTEGER DEFAULT 1,
    ключові_слова TEXT,
    опис TEXT,
    примітки TEXT
);

-- Borrowing records (позичання_книг)
CREATE TABLE позичання_книг (
    ід SERIAL PRIMARY KEY,
    книга_ід INTEGER NOT NULL REFERENCES книги_університету(ід),
    студент_ід INTEGER REFERENCES студенти(ід),
    викладач_ід INTEGER REFERENCES викладачі(ід),
    дата_видачі DATE NOT NULL,
    очікувана_дата_повернення DATE NOT NULL,
    дата_повернення DATE,
    продовжено_разів INTEGER DEFAULT 0,
    статус VARCHAR(50) DEFAULT 'видано', -- видано, повернуто, прострочено, втрачено
    видав_співробітник_ід INTEGER NOT NULL REFERENCES викладачі(ід),
    прийняв_співробітник_ід INTEGER REFERENCES викладачі(ід),
    примітки TEXT,
    CONSTRAINT користувач_check CHECK (
        (студент_ід IS NOT NULL AND викладач_ід IS NULL) OR
        (студент_ід IS NULL AND викладач_ід IS NOT NULL)
    )
);

-- Insert data into бібліотечні_фонди
INSERT INTO бібліотечні_фонди (назва, опис, розташування, дата_створення, відповідальний_ід, контактний_телефон, електронна_пошта, кількість_книг, примітки)
VALUES
(
    'Загальний фонд', 
    'Основний фонд бібліотеки університету, що містить літературу з усіх галузей знань',
    'Головний корпус, 2-й поверх, кімната 205-208',
    '1980-09-01',
    3, -- ID викладача-бібліотекаря
    '(044) 123-4567',
    'main.library@univ.edu.ua',
    24500,
    'Працює з понеділка по п''ятницю з 9:00 до 18:00'
),
(
    'Науковий фонд', 
    'Спеціалізований фонд наукової літератури, періодичних видань та дисертацій',
    'Головний корпус, 3-й поверх, кімната 305-307',
    '1985-03-15',
    5, -- ID викладача-бібліотекаря
    '(044) 123-4568',
    'science.library@univ.edu.ua',
    15800,
    'Доступ для викладачів та аспірантів без обмежень, для студентів - за рекомендацією наукового керівника'
),
(
    'Електронний фонд', 
    'Фонд електронних видань, баз даних та цифрових копій друкованих видань',
    'Головний корпус, 2-й поверх, кімната 210',
    '2010-09-01',
    10, -- ID викладача-бібліотекаря
    '(044) 123-4569',
    'e.library@univ.edu.ua',
    8500,
    'Доступ через університетську мережу або з домашніх комп''ютерів за логіном та паролем'
),
(
    'Фонд рідкісних видань', 
    'Колекція рідкісних та цінних видань, стародруків та архівних матеріалів',
    'Головний корпус, цокольний поверх, кімната 005',
    '1990-11-20',
    15, -- ID викладача-бібліотекаря
    '(044) 123-4570',
    'rare.books@univ.edu.ua',
    3200,
    'Доступ обмежений, тільки для наукової роботи за попереднім записом'
),
(
    'Навчальний фонд', 
    'Колекція підручників та навчальних посібників для студентів усіх факультетів',
    'Навчальний корпус №2, 1-й поверх, кімната 105-110',
    '1980-09-01',
    20, -- ID викладача-бібліотекаря
    '(044) 123-4571',
    'study.library@univ.edu.ua',
    18900,
    'Працює з понеділка по суботу з 8:30 до 19:00'
);

-- Insert data into книги_університету (sample books related to computer science, databases, etc.)
INSERT INTO книги_університету (назва, автор, видавництво, рік_видання, кількість_сторінок, isbn, мова, фонд_ід, дата_придбання, вартість, тип, кількість_примірників, доступна_кількість, ключові_слова, опис)
VALUES
(
    'Основи баз даних', 
    'Петренко В.М., Коваленко О.П.', 
    'Університетська книга', 
    2019, 
    412, 
    '9789660319264', 
    'українська', 
    5, -- Навчальний фонд
    '2019-08-15', 
    450.00, 
    'підручник', 
    30, 
    25, 
    'бази даних, SQL, проектування БД, нормалізація, СУБД',
    'Підручник охоплює основні концепції баз даних, проектування та нормалізацію, мову SQL та роботу з сучасними СУБД'
),
(
    'SQL: Повне керівництво', 
    'Грофф Дж., Вайнберг П., Оппель Е.', 
    'Діалектика', 
    2018, 
    960, 
    '9785907144811', 
    'українська', 
    1, -- Загальний фонд
    '2018-09-10', 
    950.00, 
    'посібник', 
    15, 
    12, 
    'SQL, бази даних, запити, транзакції, оптимізація',
    'Ґрунтовний посібник з SQL, що охоплює стандарт мови та особливості реалізації в різних СУБД'
),
(
    'Алгоритми та структури даних', 
    'Шевченко А.І., Мельник К.В.', 
    'Комп''ютерна література', 
    2020, 
    520, 
    '9789667483951', 
    'українська', 
    5, -- Навчальний фонд
    '2020-02-20', 
    580.00, 
    'підручник', 
    25, 
    20, 
    'алгоритми, структури даних, складність, аналіз алгоритмів',
    'Підручник містить теоретичні відомості та практичні приклади реалізації основних алгоритмів та структур даних'
),
(
    'Проектування інформаційних систем', 
    'Марченко О.І., Ткаченко М.В.', 
    'Університетська книга', 
    2021, 
    380, 
    '9789660324862', 
    'українська', 
    5, -- Навчальний фонд
    '2021-03-05', 
    480.00, 
    'підручник', 
    20, 
    18, 
    'інформаційні системи, проектування, архітектура, моделювання, UML',
    'Підручник охоплює всі етапи проектування інформаційних систем від аналізу вимог до впровадження та супроводу'
),
(
    'Штучний інтелект та машинне навчання', 
    'Іваненко І.І., Петров П.П.', 
    'ІТ-книга', 
    2021, 
    630, 
    '9789669876541', 
    'українська', 
    1, -- Загальний фонд
    '2021-06-15', 
    780.00, 
    'монографія', 
    10, 
    8, 
    'штучний інтелект, машинне навчання, нейронні мережі, глибоке навчання',
    'Монографія присвячена сучасним методам та алгоритмам штучного інтелекту та машинного навчання'
),
(
    'Програмування мовою Python', 
    'Бойко В.В., Семенченко О.О.', 
    'Комп''ютерна література', 
    2020, 
    480, 
    '9789667483968', 
    'українська', 
    5, -- Навчальний фонд
    '2020-08-10', 
    520.00, 
    'підручник', 
    35, 
    30, 
    'Python, програмування, алгоритми, об''єктно-орієнтоване програмування',
    'Підручник для вивчення мови програмування Python з нуля до професійного рівня'
),
(
    'Database Systems: The Complete Book', 
    'Hector Garcia-Molina, Jeffrey D. Ullman, Jennifer Widom', 
    'Pearson', 
    2014, 
    1152, 
    '9780133001501', 
    'англійська', 
    2, -- Науковий фонд
    '2015-02-10', 
    1200.00, 
    'підручник', 
    8, 
    5, 
    'database systems, DBMS, SQL, query optimization, database design',
    'Комплексний підручник з теорії та практики систем управління базами даних'
),
(
    'Математичні основи комп''ютерних наук', 
    'Кравченко І.О., Левчук С.М.', 
    'Наукова думка', 
    2019, 
    380, 
    '9789660211568', 
    'українська', 
    2, -- Науковий фонд
    '2019-09-05', 
    420.00, 
    'навчальний посібник', 
    15, 
    12, 
    'дискретна математика, логіка, теорія графів, комбінаторика',
    'Посібник охоплює математичні основи, необхідні для вивчення комп''ютерних наук'
),
(
    'Архітектура комп''ютерів', 
    'Паламар М.І., Стрембіцький М.О.', 
    'Технічна література', 
    2018, 
    450, 
    '9789669875421', 
    'українська', 
    5, -- Навчальний фонд
    '2018-10-20', 
    490.00, 
    'підручник', 
    20, 
    15, 
    'архітектура комп''ютерів, процесори, пам''ять, периферійні пристрої',
    'Підручник з основ архітектури комп''ютерів, організації обчислювальних систем та принципів їх роботи'
),
(
    'NoSQL: Нове покоління баз даних', 
    'Савченко Г.О., Литвиненко Т.В.', 
    'ІТ-книга', 
    2020, 
    340, 
    '9789669876558', 
    'українська', 
    1, -- Загальний фонд
    '2020-05-12', 
    540.00, 
    'монографія', 
    10, 
    7, 
    'NoSQL, MongoDB, Cassandra, Redis, розподілені бази даних',
    'Монографія присвячена нереляційним базам даних, їх видам, архітектурі та особливостям використання'
);

-- Insert data into позичання_книг
INSERT INTO позичання_книг (книга_ід, студент_ід, викладач_ід, дата_видачі, очікувана_дата_повернення, дата_повернення, продовжено_разів, статус, видав_співробітник_ід, прийняв_співробітник_ід, примітки)
VALUES
-- Студентські позичання
(1, 1, NULL, '2023-09-10', '2023-10-10', '2023-10-08', 0, 'повернуто', 3, 3, 'Повернуто вчасно'),
(2, 3, NULL, '2023-09-15', '2023-10-15', NULL, 1, 'прострочено', 3, NULL, 'Потрібно зв''язатися зі студентом'),
(3, 5, NULL, '2023-10-01', '2023-11-01', '2023-10-25', 0, 'повернуто', 3, 5, 'Повернуто вчасно'),
(4, 7, NULL, '2023-10-05', '2023-11-05', NULL, 0, 'видано', 5, NULL, NULL),
(5, 10, NULL, '2023-10-10', '2023-11-10', NULL, 0, 'видано', 5, NULL, 'Студент попросив продовжити термін'),
(6, 12, NULL, '2023-09-20', '2023-10-20', '2023-10-19', 0, 'повернуто', 5, 3, 'Повернуто з невеликими пошкодженнями'),
(6, 15, NULL, '2023-10-25', '2023-11-25', NULL, 0, 'видано', 3, NULL, NULL),
(8, 18, NULL, '2023-09-05', '2023-10-05', '2023-10-20', 1, 'повернуто', 5, 5, 'Повернуто із запізненням, сплачено штраф'),
(9, 20, NULL, '2023-10-15', '2023-11-15', NULL, 0, 'видано', 3, NULL, NULL),
(10, 22, NULL, '2023-10-20', '2023-11-20', NULL, 0, 'видано', 5, NULL, NULL),

-- Викладацькі позичання
(7, NULL, 2, '2023-09-01', '2023-12-01', NULL, 0, 'видано', 3, NULL, 'Для підготовки нового курсу'),
(8, NULL, 4, '2023-09-15', '2023-12-15', NULL, 0, 'видано', 5, NULL, NULL),
(9, NULL, 6, '2023-08-20', '2023-11-20', '2023-11-15', 0, 'повернуто', 3, 3, 'Використано для оновлення конспекту лекцій'),
(1, NULL, 8, '2023-10-01', '2024-01-01', NULL, 0, 'видано', 5, NULL, NULL),
(3, NULL, 10, '2023-09-10', '2023-12-10', NULL, 0, 'видано', 3, NULL, 'Для підготовки методичних рекомендацій');

-- Create index for faster searches
CREATE INDEX книги_університету_назва_автор_idx ON книги_університету (назва, автор);
CREATE INDEX позичання_книг_дати_idx ON позичання_книг (дата_видачі, очікувана_дата_повернення, дата_повернення);
CREATE INDEX позичання_книг_статус_idx ON позичання_книг (статус);
CREATE INDEX позичання_книг_студент_idx ON позичання_книг (студент_ід) WHERE студент_ід IS NOT NULL;
CREATE INDEX позичання_книг_викладач_idx ON позичання_книг (викладач_ід) WHERE викладач_ід IS NOT NULL;

-- Create a view for currently borrowed books
CREATE VIEW активні_позичання AS
SELECT 
    п.ід AS позичання_ід,
    к.назва AS назва_книги,
    к.автор,
    CASE 
        WHEN п.студент_ід IS NOT NULL THEN 'студент'
        WHEN п.викладач_ід IS NOT NULL THEN 'викладач'
    END AS тип_користувача,
    CASE 
        WHEN п.студент_ід IS NOT NULL THEN (SELECT с.прізвище || ' ' || с.імя FROM студенти с WHERE с.ід = п.студент_ід)
        WHEN п.викладач_ід IS NOT NULL THEN (SELECT в.прізвище || ' ' || в.імя FROM викладачі в WHERE в.ід = п.викладач_ід)
    END AS користувач,
    п.дата_видачі,
    п.очікувана_дата_повернення,
    п.статус,
    CASE 
        WHEN п.очікувана_дата_повернення < CURRENT_DATE AND п.дата_повернення IS NULL THEN 'так'
        ELSE 'ні'
    END AS прострочено,
    CASE 
        WHEN п.очікувана_дата_повернення < CURRENT_DATE AND п.дата_повернення IS NULL 
        THEN (CURRENT_DATE - п.очікувана_дата_повернення)
        ELSE 0
    END AS днів_прострочення
FROM 
    позичання_книг п
    JOIN книги_університету к ON п.книга_ід = к.ід
WHERE 
    п.дата_повернення IS NULL;

-- Create a view for library statistics
CREATE VIEW статистика_бібліотеки AS
SELECT 
    SUM(кількість_книг) AS загальна_кількість_книг,
    (SELECT COUNT(*) FROM книги_університету) AS кількість_найменувань,
    (SELECT SUM(кількість_примірників) FROM книги_університету) AS загальна_кількість_примірників,
    (SELECT COUNT(*) FROM позичання_книг WHERE дата_повернення IS NULL) AS кількість_виданих_книг,
    (SELECT COUNT(*) FROM позичання_книг WHERE статус = 'прострочено') AS кількість_прострочених,
    (SELECT COUNT(*) FROM позичання_книг WHERE дата_видачі >= CURRENT_DATE - INTERVAL '30 day') AS видано_за_останні_30_днів,
    (SELECT COUNT(DISTINCT студент_ід) FROM позичання_книг WHERE студент_ід IS NOT NULL AND дата_видачі >= CURRENT_DATE - INTERVAL '365 day') AS активних_студентів_читачів,
    (SELECT COUNT(DISTINCT викладач_ід) FROM позичання_книг WHERE викладач_ід IS NOT NULL AND дата_видачі >= CURRENT_DATE - INTERVAL '365 day') AS активних_викладачів_читачів
FROM 
    бібліотечні_фонди; 