-- Ukrainian University Database Schema
-- Encoding: UTF-8
-- Created: 2024-04-19
-- Author: AI Assistant

-- Use PostgreSQL syntax

SET client_encoding TO 'UTF8';

-- =====================================
-- DROP TABLES IF THEY EXIST (for clean setup)
-- =====================================

DROP TABLE IF EXISTS оцінки CASCADE;
DROP TABLE IF EXISTS записи_на_курси CASCADE;
DROP TABLE IF EXISTS розклад_занять CASCADE;
DROP TABLE IF EXISTS заняття CASCADE;
DROP TABLE IF EXISTS аудиторії CASCADE;
DROP TABLE IF EXISTS будівлі CASCADE;
DROP TABLE IF EXISTS навчальні_матеріали CASCADE;
DROP TABLE IF EXISTS курси CASCADE;
DROP TABLE IF EXISTS напрями CASCADE;
DROP TABLE IF EXISTS студенти CASCADE;
DROP TABLE IF EXISTS групи CASCADE;
DROP TABLE IF EXISTS викладачі CASCADE;
DROP TABLE IF EXISTS кафедри CASCADE;
DROP TABLE IF EXISTS факультети CASCADE;
DROP TABLE IF EXISTS посади CASCADE;
DROP TABLE IF EXISTS семестри CASCADE;
DROP TABLE IF EXISTS типи_занять CASCADE;
DROP TABLE IF EXISTS статуси_студентів CASCADE;
DROP TABLE IF EXISTS академічні_ступені CASCADE;
DROP TABLE IF EXISTS наукові_звання CASCADE;
DROP TABLE IF EXISTS стипендії CASCADE;
DROP TABLE IF EXISTS типи_стипендій CASCADE;
DROP TABLE IF EXISTS позичання_книг CASCADE;
DROP TABLE IF EXISTS книги_університету CASCADE;
DROP TABLE IF EXISTS бібліотечні_фонди CASCADE;
DROP TABLE IF EXISTS участь_у_конференціях CASCADE;
DROP TABLE IF EXISTS автори_публікацій CASCADE;
DROP TABLE IF EXISTS дослідники_дослідження CASCADE;
DROP TABLE IF EXISTS гранти CASCADE;
DROP TABLE IF EXISTS публікації CASCADE;
DROP TABLE IF EXISTS наукові_дослідження CASCADE;
DROP TABLE IF EXISTS спонсорство_конференцій;
DROP TABLE IF EXISTS учасники_конференцій;
DROP TABLE IF EXISTS доповідачі_конференцій;
DROP TABLE IF EXISTS секції_конференцій;
DROP TABLE IF EXISTS конференції;

-- =====================================
-- CREATE TABLES
-- =====================================

-- Довідникові таблиці

CREATE TABLE академічні_ступені (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    скорочення VARCHAR(10) NOT NULL,
    опис TEXT
);

CREATE TABLE наукові_звання (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    скорочення VARCHAR(10) NOT NULL,
    опис TEXT
);

CREATE TABLE статуси_студентів (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL UNIQUE,
    опис TEXT
);

CREATE TABLE типи_занять (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL UNIQUE,
    опис TEXT
);

CREATE TABLE семестри (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    дата_початку DATE NOT NULL,
    дата_кінця DATE NOT NULL,
    навчальний_рік VARCHAR(9) NOT NULL,
    є_активним BOOLEAN DEFAULT FALSE,
    CONSTRAINT семестри_дати_check CHECK (дата_початку < дата_кінця),
    UNIQUE (назва, навчальний_рік)
);

CREATE TABLE посади (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT,
    мінімальна_зарплата DECIMAL(10, 2),
    максимальна_зарплата DECIMAL(10, 2),
    CONSTRAINT посади_зарплата_check CHECK (
        мінімальна_зарплата IS NULL OR 
        максимальна_зарплата IS NULL OR 
        мінімальна_зарплата <= максимальна_зарплата
    )
);

-- Основні структурні таблиці

CREATE TABLE факультети (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    скорочення VARCHAR(10) NOT NULL UNIQUE,
    опис TEXT,
    дата_заснування DATE,
    декан_ід INTEGER,
    контактна_інформація TEXT,
    веб_сайт VARCHAR(255),
    активний BOOLEAN DEFAULT TRUE
);

CREATE TABLE кафедри (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    скорочення VARCHAR(10) NOT NULL,
    опис TEXT,
    дата_заснування DATE,
    факультет_ід INTEGER NOT NULL REFERENCES факультети(ід),
    завідувач_ід INTEGER,
    телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    розташування VARCHAR(255),
    активна BOOLEAN DEFAULT TRUE,
    UNIQUE (назва, факультет_ід),
    UNIQUE (скорочення, факультет_ід)
);

CREATE TABLE викладачі (
    ід SERIAL PRIMARY KEY,
    табельний_номер VARCHAR(20) NOT NULL UNIQUE,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    стать CHAR(1) CHECK (стать IN ('Ч', 'Ж')),
    дата_народження DATE,
    кафедра_ід INTEGER REFERENCES кафедри(ід),
    посада_ід INTEGER REFERENCES посади(ід),
    науковий_ступінь_ід INTEGER REFERENCES академічні_ступені(ід),
    вчене_звання_ід INTEGER REFERENCES наукові_звання(ід),
    дата_прийняття DATE NOT NULL,
    дата_звільнення DATE,
    контактний_телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    зарплата DECIMAL(10, 2),
    активний BOOLEAN DEFAULT TRUE,
    CONSTRAINT викладачі_дати_check CHECK (
        дата_звільнення IS NULL OR 
        дата_прийняття <= дата_звільнення
    )
);

-- Додавання зовнішніх ключів, які залежали від таблиці викладачі
ALTER TABLE факультети 
ADD CONSTRAINT факультети_декан_fk 
FOREIGN KEY (декан_ід) REFERENCES викладачі(ід);

ALTER TABLE кафедри 
ADD CONSTRAINT кафедри_завідувач_fk 
FOREIGN KEY (завідувач_ід) REFERENCES викладачі(ід);

CREATE TABLE напрями (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    код VARCHAR(20) NOT NULL,
    рівень VARCHAR(50) NOT NULL,
    опис TEXT,
    кафедра_ід INTEGER NOT NULL REFERENCES кафедри(ід),
    кількість_кредитів INTEGER NOT NULL,
    тривалість_навчання_роки NUMERIC(2,1) NOT NULL,
    активний BOOLEAN DEFAULT TRUE,
    UNIQUE (код, рівень)
);

CREATE TABLE групи (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(20) NOT NULL,
    рік_вступу INTEGER NOT NULL,
    напрям_ід INTEGER NOT NULL REFERENCES напрями(ід),
    куратор_ід INTEGER REFERENCES викладачі(ід),
    кількість_студентів INTEGER DEFAULT 0,
    активна BOOLEAN DEFAULT TRUE,
    UNIQUE (назва, рік_вступу)
);

CREATE TABLE студенти (
    ід SERIAL PRIMARY KEY,
    студентський_квиток VARCHAR(20) NOT NULL UNIQUE,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    стать CHAR(1) CHECK (стать IN ('Ч', 'Ж')),
    дата_народження DATE,
    група_ід INTEGER REFERENCES групи(ід),
    дата_вступу DATE NOT NULL,
    дата_випуску DATE,
    форма_навчання VARCHAR(20) NOT NULL CHECK (форма_навчання IN ('денна', 'заочна', 'вечірня', 'дистанційна')),
    фінансування VARCHAR(20) NOT NULL CHECK (фінансування IN ('бюджет', 'контракт')),
    статус_ід INTEGER NOT NULL REFERENCES статуси_студентів(ід),
    контактний_телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    адреса TEXT,
    середній_бал NUMERIC(4,2),
    чи_отримує_стипендію BOOLEAN DEFAULT FALSE,
    CONSTRAINT студенти_дати_check CHECK (
        дата_випуску IS NULL OR 
        дата_вступу <= дата_випуску
    )
);

-- Збільшуємо лічильник студентів в групі при додаванні студента
CREATE OR REPLACE FUNCTION update_group_student_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.група_ід IS NOT NULL THEN
        -- Якщо студент доданий до групи - збільшуємо лічильник
        IF OLD.група_ід IS NULL OR OLD.група_ід != NEW.група_ід THEN
            UPDATE групи SET кількість_студентів = кількість_студентів + 1
            WHERE ід = NEW.група_ід;
        END IF;
        
        -- Якщо студент переведений з іншої групи - зменшуємо лічильник старої групи
        IF OLD.група_ід IS NOT NULL AND OLD.група_ід != NEW.група_ід THEN
            UPDATE групи SET кількість_студентів = кількість_студентів - 1
            WHERE ід = OLD.група_ід;
        END IF;
    ELSIF OLD.група_ід IS NOT NULL THEN
        -- Якщо студент видалений з групи - зменшуємо лічильник
        UPDATE групи SET кількість_студентів = кількість_студентів - 1
        WHERE ід = OLD.група_ід;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER студенти_група_тригер
AFTER INSERT OR UPDATE OF група_ід ON студенти
FOR EACH ROW EXECUTE FUNCTION update_group_student_count();

CREATE TABLE курси (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    код VARCHAR(20) NOT NULL UNIQUE,
    опис TEXT,
    кафедра_ід INTEGER NOT NULL REFERENCES кафедри(ід),
    кількість_кредитів INTEGER NOT NULL,
    години_лекцій INTEGER DEFAULT 0,
    години_практичних INTEGER DEFAULT 0,
    години_лабораторних INTEGER DEFAULT 0,
    години_самостійної INTEGER DEFAULT 0,
    має_екзамен BOOLEAN DEFAULT TRUE,
    активний BOOLEAN DEFAULT TRUE,
    CONSTRAINT курси_години_check CHECK (
        години_лекцій >= 0 AND 
        години_практичних >= 0 AND 
        години_лабораторних >= 0 AND 
        години_самостійної >= 0
    )
);

CREATE TABLE навчальні_матеріали (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    тип VARCHAR(50) NOT NULL,
    опис TEXT,
    курс_ід INTEGER NOT NULL REFERENCES курси(ід),
    автор_ід INTEGER REFERENCES викладачі(ід),
    дата_створення DATE DEFAULT CURRENT_DATE,
    файл_url VARCHAR(255),
    рік_видання INTEGER,
    видавництво VARCHAR(100),
    примітки TEXT
);

CREATE TABLE будівлі (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    адреса TEXT NOT NULL,
    кількість_поверхів INTEGER NOT NULL,
    рік_побудови INTEGER,
    загальна_площа NUMERIC(10, 2),
    примітки TEXT
);

CREATE TABLE аудиторії (
    ід SERIAL PRIMARY KEY,
    номер VARCHAR(20) NOT NULL,
    будівля_ід INTEGER NOT NULL REFERENCES будівлі(ід),
    поверх INTEGER NOT NULL,
    тип VARCHAR(50) NOT NULL,
    місткість INTEGER NOT NULL,
    площа NUMERIC(8, 2),
    має_компютери BOOLEAN DEFAULT FALSE,
    має_проектор BOOLEAN DEFAULT FALSE,
    примітки TEXT,
    UNIQUE (номер, будівля_ід)
);

CREATE TABLE заняття (
    ід SERIAL PRIMARY KEY,
    курс_ід INTEGER NOT NULL REFERENCES курси(ід),
    викладач_ід INTEGER NOT NULL REFERENCES викладачі(ід),
    семестр_ід INTEGER NOT NULL REFERENCES семестри(ід),
    тип_заняття_ід INTEGER NOT NULL REFERENCES типи_занять(ід),
    група_ід INTEGER NOT NULL REFERENCES групи(ід),
    примітки TEXT,
    UNIQUE (курс_ід, викладач_ід, семестр_ід, тип_заняття_ід, група_ід)
);

CREATE TABLE розклад_занять (
    ід SERIAL PRIMARY KEY,
    заняття_ід INTEGER NOT NULL REFERENCES заняття(ід),
    день_тижня INTEGER NOT NULL CHECK (день_тижня BETWEEN 1 AND 7),
    час_початку TIME NOT NULL,
    час_кінця TIME NOT NULL,
    аудиторія_ід INTEGER NOT NULL REFERENCES аудиторії(ід),
    регулярність VARCHAR(20) DEFAULT 'щотижня' CHECK (регулярність IN ('щотижня', 'по чисельнику', 'по знаменнику')),
    дата_початку DATE,
    дата_кінця DATE,
    CONSTRAINT розклад_занять_час_check CHECK (час_початку < час_кінця)
);

CREATE TABLE записи_на_курси (
    ід SERIAL PRIMARY KEY,
    студент_ід INTEGER NOT NULL REFERENCES студенти(ід),
    заняття_ід INTEGER NOT NULL REFERENCES заняття(ід),
    дата_запису DATE NOT NULL DEFAULT CURRENT_DATE,
    статус VARCHAR(20) NOT NULL DEFAULT 'активний' CHECK (статус IN ('активний', 'завершений', 'відмінений')),
    UNIQUE (студент_ід, заняття_ід)
);

CREATE TABLE оцінки (
    ід SERIAL PRIMARY KEY,
    запис_на_курс_ід INTEGER NOT NULL REFERENCES записи_на_курси(ід),
    тип_оцінювання VARCHAR(50) NOT NULL,
    дата DATE NOT NULL,
    оцінка NUMERIC(4, 1) NOT NULL,
    максимальна_оцінка NUMERIC(4, 1) NOT NULL DEFAULT 100,
    коментар TEXT,
    викладач_ід INTEGER NOT NULL REFERENCES викладачі(ід),
    CONSTRAINT оцінки_значення_check CHECK (оцінка >= 0 AND оцінка <= максимальна_оцінка)
);

-- =====================================
-- CREATE INDEXES
-- =====================================

-- Індекси для пошуку по прізвищу
CREATE INDEX викладачі_прізвище_idx ON викладачі (прізвище);
CREATE INDEX студенти_прізвище_idx ON студенти (прізвище);

-- Індекси для пошуку по номеру документів
CREATE INDEX студенти_квиток_idx ON студенти (студентський_квиток);
CREATE INDEX викладачі_табель_idx ON викладачі (табельний_номер);

-- Індекси для оптимізації з'єднань
CREATE INDEX заняття_курс_семестр_idx ON заняття (курс_ід, семестр_ід);
CREATE INDEX заняття_викладач_семестр_idx ON заняття (викладач_ід, семестр_ід);
CREATE INDEX записи_на_курси_студент_idx ON записи_на_курси (студент_ід);
CREATE INDEX записи_на_курси_заняття_idx ON записи_на_курси (заняття_ід);
CREATE INDEX оцінки_запис_idx ON оцінки (запис_на_курс_ід);
CREATE INDEX розклад_занять_заняття_день_idx ON розклад_занять (заняття_ід, день_тижня);

-- =====================================
-- CREATE VIEWS
-- =====================================

-- Представлення для студентів з інформацією про групу та напрям
CREATE VIEW студенти_повна_інформація AS
SELECT 
    с.ід,
    с.студентський_квиток,
    с.прізвище,
    с.імя,
    с.по_батькові,
    с.прізвище || ' ' || с.імя || ' ' || COALESCE(с.по_батькові, '') AS повне_імя,
    с.стать,
    с.дата_народження,
    г.назва AS група,
    н.назва AS напрям,
    н.рівень,
    с.форма_навчання,
    с.фінансування,
    сс.назва AS статус,
    с.середній_бал,
    с.дата_вступу,
    с.дата_випуску
FROM 
    студенти с
    JOIN групи г ON с.група_ід = г.ід
    JOIN напрями н ON г.напрям_ід = н.ід
    JOIN статуси_студентів сс ON с.статус_ід = сс.ід;

-- Представлення для викладачів з інформацією про кафедру та факультет
CREATE VIEW викладачі_повна_інформація AS
SELECT 
    в.ід,
    в.табельний_номер,
    в.прізвище,
    в.імя,
    в.по_батькові,
    в.прізвище || ' ' || в.імя || ' ' || COALESCE(в.по_батькові, '') AS повне_імя,
    в.стать,
    к.назва AS кафедра,
    ф.назва AS факультет,
    п.назва AS посада,
    ас.назва AS науковий_ступінь,
    нз.назва AS вчене_звання,
    в.зарплата,
    в.дата_прийняття,
    в.дата_звільнення,
    в.активний
FROM 
    викладачі в
    JOIN кафедри к ON в.кафедра_ід = к.ід
    JOIN факультети ф ON к.факультет_ід = ф.ід
    JOIN посади п ON в.посада_ід = п.ід
    LEFT JOIN академічні_ступені ас ON в.науковий_ступінь_ід = ас.ід
    LEFT JOIN наукові_звання нз ON в.вчене_звання_ід = нз.ід;

-- Представлення для розкладу з повною інформацією
CREATE VIEW розклад_повна_інформація AS
SELECT 
    р.ід,
    к.назва AS курс,
    к.код AS код_курсу,
    тз.назва AS тип_заняття,
    в.прізвище || ' ' || в.імя || ' ' || COALESCE(в.по_батькові, '') AS викладач,
    г.назва AS група,
    CASE 
        WHEN р.день_тижня = 1 THEN 'Понеділок'
        WHEN р.день_тижня = 2 THEN 'Вівторок'
        WHEN р.день_тижня = 3 THEN 'Середа'
        WHEN р.день_тижня = 4 THEN 'Четвер'
        WHEN р.день_тижня = 5 THEN 'П''ятниця'
        WHEN р.день_тижня = 6 THEN 'Субота'
        WHEN р.день_тижня = 7 THEN 'Неділя'
    END AS день_тижня,
    р.час_початку,
    р.час_кінця,
    TO_CHAR(р.час_початку, 'HH24:MI') || '-' || TO_CHAR(р.час_кінця, 'HH24:MI') AS час,
    б.назва || ', ауд. ' || а.номер AS аудиторія,
    р.регулярність,
    с.назва AS семестр
FROM 
    розклад_занять р
    JOIN заняття з ON р.заняття_ід = з.ід
    JOIN курси к ON з.курс_ід = к.ід
    JOIN викладачі в ON з.викладач_ід = в.ід
    JOIN групи г ON з.група_іd = г.ід
    JOIN типи_занять тз ON з.тип_заняття_ід = тз.ід
    JOIN аудиторії а ON р.аудиторія_ід = а.ід
    JOIN будівлі б ON а.будівля_ід = б.ід
    JOIN семестри с ON з.семестр_ід = с.ід;

-- Представлення для оцінок студентів
CREATE VIEW оцінки_студентів AS
SELECT 
    с.студентський_квиток,
    с.прізвище || ' ' || с.імя || ' ' || COALESCE(с.по_батькові, '') AS студент,
    г.назва AS група,
    к.назва AS курс,
    к.код AS код_курсу,
    о.тип_оцінювання,
    о.оцінка,
    о.максимальна_оцінка,
    о.дата,
    в.прізвище || ' ' || в.імя || ' ' || COALESCE(в.по_батькові, '') AS викладач,
    семестр.назва AS семестр,
    семестр.навчальний_рік,
    зк.статус AS статус_запису
FROM 
    оцінки о
    JOIN записи_на_курси зк ON о.запис_на_курс_ід = зк.ід
    JOIN студенти с ON зк.студент_ід = с.ід
    JOIN групи г ON с.група_ід = г.ід
    JOIN заняття з ON зк.заняття_ід = з.ід
    JOIN курси к ON з.курс_ід = к.ід
    JOIN викладачі в ON о.викладач_ід = в.ід
    JOIN семестри семестр ON з.семестр_ід = семестр.ід;

-- Представлення для середніх оцінок студентів за семестр
CREATE VIEW середній_бал_семестру AS
SELECT 
    с.ід AS студент_ід,
    с.прізвище || ' ' || с.імя || ' ' || COALESCE(с.по_батькові, '') AS студент,
    г.назва AS група,
    семестр.назва AS семестр,
    семестр.навчальний_рік,
    ROUND(AVG(о.оцінка), 2) AS середній_бал,
    COUNT(DISTINCT з.курс_ід) AS кількість_курсів
FROM 
    оцінки о
    JOIN записи_на_курси зк ON о.запис_на_курс_ід = зк.ід
    JOIN студенти с ON зк.студент_ід = с.ід
    JOIN групи г ON с.група_ід = г.ід
    JOIN заняття з ON зк.заняття_ід = з.ід
    JOIN семестри семестр ON з.семестр_ід = семестр.ід
WHERE 
    о.тип_оцінювання IN ('екзамен', 'залік')
GROUP BY 
    с.ід, с.прізвище, с.імя, с.по_батькові, г.назва, семестр.назва, семестр.навчальний_рік;

-- Представлення для навантаження викладачів
CREATE VIEW навантаження_викладачів AS
SELECT 
    в.ід AS викладач_ід,
    в.прізвище || ' ' || в.імя || ' ' || COALESCE(в.по_батькові, '') AS викладач,
    к.назва AS кафедра,
    семестр.назва AS семестр,
    семестр.навчальний_рік,
    COUNT(DISTINCT з.ід) AS кількість_занять,
    SUM(CASE WHEN тз.назва = 'Лекція' THEN к.години_лекцій ELSE 0 END) AS години_лекцій,
    SUM(CASE WHEN тз.назва = 'Практичне заняття' THEN к.години_практичних ELSE 0 END) AS години_практичних,
    SUM(CASE WHEN тз.назва = 'Лабораторна робота' THEN к.години_лабораторних ELSE 0 END) AS години_лабораторних,
    SUM(к.години_лекцій + к.години_практичних + к.години_лабораторних) AS загальні_години
FROM 
    викладачі в
    JOIN заняття з ON в.ід = з.викладач_ід
    JOIN курси к ON з.курс_ід = к.ід
    JOIN кафедри каф ON в.кафедра_ід = каф.ід
    JOIN типи_занять тз ON з.тип_заняття_ід = тз.ід
    JOIN семестри семестр ON з.семестр_ід = семестр.ід
GROUP BY 
    в.ід, в.прізвище, в.імя, в.по_батькові, к.назва, семестр.назва, семестр.навчальний_рік;

-- =====================================
-- GRANT PERMISSIONS
-- =====================================

-- Припустимо, що у нас є ролі 'адміністратор', 'викладач', 'студент'
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO адміністратор;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO викладач;
-- GRANT SELECT ON студенти_повна_інформація, розклад_повна_інформація, оцінки_студентів TO студент;

-- Added Scholarship Tables
CREATE TABLE типи_стипендій (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT,
    кількість_виплат_на_рік INTEGER
);

CREATE TABLE стипендії (
    ід SERIAL PRIMARY KEY,
    студент_ід INTEGER NOT NULL REFERENCES студенти(ід) ON DELETE CASCADE,
    тип_стипендії_ід INTEGER NOT NULL REFERENCES типи_стипендій(ід) ON DELETE RESTRICT,
    розмір DECIMAL(10, 2) NOT NULL CHECK (розмір > 0),
    дата_початку DATE NOT NULL,
    дата_кінця DATE NOT NULL,
    підстава TEXT,
    CONSTRAINT стипендії_дати_check CHECK (дата_початку <= дата_кінця)
);

-- Added Library Tables
CREATE TABLE бібліотечні_фонди (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    розташування VARCHAR(100),
    дата_створення DATE,
    відповідальний_ід INTEGER REFERENCES викладачі(ід) ON DELETE SET NULL,
    контактний_телефон VARCHAR(15),
    електронна_пошта VARCHAR(100),
    кількість_книг INTEGER DEFAULT 0 CHECK (кількість_книг >= 0),
    примітки TEXT
);

CREATE TABLE книги_університету (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(200) NOT NULL,
    автор VARCHAR(150),
    видавництво VARCHAR(100),
    рік_видання INTEGER,
    кількість_сторінок INTEGER CHECK (кількість_сторінок > 0),
    isbn VARCHAR(20),
    мова VARCHAR(50) DEFAULT 'українська',
    фонд_ід INTEGER NOT NULL REFERENCES бібліотечні_фонди(ід) ON DELETE CASCADE,
    дата_придбання DATE,
    вартість DECIMAL(10, 2) CHECK (вартість >= 0),
    тип VARCHAR(50) DEFAULT 'підручник', -- підручник, посібник, монографія, тощо
    кількість_примірників INTEGER DEFAULT 1 CHECK (кількість_примірників >= 0),
    доступна_кількість INTEGER DEFAULT 1 CHECK (доступна_кількість >= 0),
    ключові_слова TEXT,
    опис TEXT,
    примітки TEXT,
    CONSTRAINT книги_доступна_кількість_check CHECK (доступна_кількість <= кількість_примірників)
);

CREATE TABLE позичання_книг (
    ід SERIAL PRIMARY KEY,
    книга_ід INTEGER NOT NULL REFERENCES книги_університету(ід) ON DELETE RESTRICT,
    студент_ід INTEGER REFERENCES студенти(ід) ON DELETE SET NULL,
    викладач_ід INTEGER REFERENCES викладачі(ід) ON DELETE SET NULL,
    дата_видачі DATE NOT NULL,
    очікувана_дата_повернення DATE NOT NULL,
    дата_повернення DATE,
    продовжено_разів INTEGER DEFAULT 0 CHECK (продовжено_разів >= 0),
    статус VARCHAR(50) DEFAULT 'видано' CHECK (статус IN ('видано', 'повернуто', 'прострочено', 'втрачено')),
    видав_співробітник_ід INTEGER NOT NULL REFERENCES викладачі(ід) ON DELETE RESTRICT,
    прийняв_співробітник_ід INTEGER REFERENCES викладачі(ід) ON DELETE SET NULL,
    примітки TEXT,
    CONSTRAINT позичання_дати_check CHECK (дата_видачі <= очікувана_дата_повернення),
    CONSTRAINT позичання_повернення_check CHECK (дата_повернення IS NULL OR дата_видачі <= дата_повернення),
    CONSTRAINT користувач_check CHECK (
        (студент_ід IS NOT NULL AND викладач_ід IS NULL) OR
        (студент_ід IS NULL AND викладач_ід IS NOT NULL)
    )
);

-- Indexes and Views for Library
CREATE INDEX книги_університету_назва_автор_idx ON книги_університету (назва, автор);
CREATE INDEX позичання_книг_дати_idx ON позичання_книг (дата_видачі, очікувана_дата_повернення, дата_повернення);
CREATE INDEX позичання_книг_статус_idx ON позичання_книг (статус);
CREATE INDEX позичання_книг_студент_idx ON позичання_книг (студент_ід) WHERE студент_ід IS NOT NULL;
CREATE INDEX позичання_книг_викладач_idx ON позичання_книг (викладач_ід) WHERE викладач_ід IS NOT NULL;

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

-- Added Research Tables
CREATE TABLE наукові_дослідження (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    опис TEXT,
    тип VARCHAR(100) NOT NULL, -- фундаментальне, прикладне, розробка, тощо
    статус VARCHAR(50) NOT NULL DEFAULT 'активне' CHECK (статус IN ('активне', 'завершене', 'призупинене', 'планується')),
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    бюджет DECIMAL(12, 2) CHECK (бюджет >= 0),
    джерело_фінансування VARCHAR(100),
    кафедра_ід INTEGER REFERENCES кафедри(ід) ON DELETE SET NULL,
    керівник_ід INTEGER REFERENCES викладачі(ід) ON DELETE SET NULL,
    пріоритетність INTEGER DEFAULT 3 CHECK (пріоритетність BETWEEN 1 AND 5),
    номер_держреєстрації VARCHAR(50),
    примітки TEXT,
    CONSTRAINT дати_дослідження_check CHECK (дата_початку <= дата_закінчення OR дата_закінчення IS NULL)
);

CREATE TABLE публікації (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    тип VARCHAR(100) NOT NULL, -- стаття, монографія, тези, патент, тощо
    видання VARCHAR(200),
    рік INTEGER NOT NULL CHECK (рік > 1900 AND рік < 2100),
    том VARCHAR(50),
    номер VARCHAR(50),
    сторінки VARCHAR(50),
    doi VARCHAR(100) UNIQUE,
    url VARCHAR(255),
    імпакт_фактор DECIMAL(5, 3) CHECK (імпакт_фактор >= 0),
    індексація VARCHAR(255), -- Scopus, Web of Science, тощо
    цитування_кількість INTEGER DEFAULT 0 CHECK (цитування_кількість >= 0),
    дослідження_ід INTEGER REFERENCES наукові_дослідження(ід) ON DELETE SET NULL,
    примітки TEXT
);

CREATE TABLE гранти (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    організація VARCHAR(200) NOT NULL, -- грантодавець
    тип VARCHAR(100) NOT NULL, -- науковий, освітній, інфраструктурний, тощо
    сума DECIMAL(12, 2) NOT NULL CHECK (сума > 0),
    валюта VARCHAR(10) DEFAULT 'UAH',
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    статус VARCHAR(50) NOT NULL DEFAULT 'активний' CHECK (статус IN ('активний', 'завершений', 'відхилений', 'підготовка')),
    дослідження_ід INTEGER REFERENCES наукові_дослідження(ід) ON DELETE SET NULL,
    керівник_гранту_ід INTEGER REFERENCES викладачі(ід) ON DELETE SET NULL,
    опис TEXT,
    умови TEXT,
    примітки TEXT,
    CONSTRAINT дати_гранту_check CHECK (дата_початку <= дата_закінчення OR дата_закінчення IS NULL)
);

CREATE TABLE дослідники_дослідження (
    ід SERIAL PRIMARY KEY,
    дослідження_ід INTEGER NOT NULL REFERENCES наукові_дослідження(ід) ON DELETE CASCADE,
    викладач_ід INTEGER NOT NULL REFERENCES викладачі(ід) ON DELETE CASCADE,
    роль VARCHAR(100) NOT NULL, -- керівник, виконавець, консультант, тощо
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    навантаження DECIMAL(5, 2) CHECK (навантаження >= 0 AND навантаження <= 100), -- відсоток ставки або годин на тиждень
    примітки TEXT,
    UNIQUE (дослідження_ід, викладач_ід, роль),
    CONSTRAINT дати_участі_check CHECK (дата_початку <= дата_закінчення OR дата_закінчення IS NULL)
);

CREATE TABLE автори_публікацій (
    ід SERIAL PRIMARY KEY,
    публікація_ід INTEGER NOT NULL REFERENCES публікації(ід) ON DELETE CASCADE,
    викладач_ід INTEGER REFERENCES викладачі(ід) ON DELETE CASCADE,
    зовнішній_автор_прізвище VARCHAR(100),
    зовнішній_автор_імя VARCHAR(100),
    зовнішній_автор_установа VARCHAR(200),
    порядок_авторів INTEGER NOT NULL CHECK (порядок_авторів > 0),
    є_кореспондуючим BOOLEAN DEFAULT FALSE,
    примітки TEXT,
    CONSTRAINT автор_check CHECK (
        (викладач_ід IS NOT NULL AND зовнішній_автор_прізвище IS NULL AND зовнішній_автор_імя IS NULL) OR
        (викладач_ід IS NULL AND зовнішній_автор_прізвище IS NOT NULL AND зовнішній_автор_імя IS NOT NULL)
    )
);

CREATE TABLE участь_у_конференціях (
    ід SERIAL PRIMARY KEY,
    викладач_ід INTEGER NOT NULL REFERENCES викладачі(ід),
    назва_конференції VARCHAR(255) NOT NULL,
    місце_проведення VARCHAR(255) NOT NULL,
    дата_початку DATE NOT NULL,
    дата_закінчення DATE NOT NULL,
    тип_участі VARCHAR(100) NOT NULL, -- доповідач, слухач, організатор, член комітету
    назва_доповіді VARCHAR(255),
    публікація_ід INTEGER REFERENCES публікації(ід) ON DELETE SET NULL,
    фінансування_ід INTEGER REFERENCES гранти(ід) ON DELETE SET NULL,
    примітки TEXT,
    CONSTRAINT дати_конференції_check CHECK (дата_початку <= дата_закінчення)
);

-- Conferences (конференції)
CREATE TABLE конференції (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    опис TEXT,
    тип VARCHAR(100) NOT NULL, -- міжнародна, всеукраїнська, регіональна, університетська
    дата_початку DATE NOT NULL,
    дата_закінчення DATE NOT NULL,
    місце_проведення VARCHAR(255) NOT NULL,
    організатор_кафедра_ід INTEGER REFERENCES кафедри(ід),
    головний_організатор_ід INTEGER REFERENCES викладачі(ід),
    формат VARCHAR(50) NOT NULL, -- офлайн, онлайн, гібридний
    вебсайт VARCHAR(255),
    емейл_контакт VARCHAR(100),
    телефон_контакт VARCHAR(20),
    максимум_учасників INTEGER,
    вартість_участі DECIMAL(10, 2),
    валюта VARCHAR(3) DEFAULT 'UAH',
    дедлайн_реєстрації DATE,
    дедлайн_тез DATE,
    статус VARCHAR(50) DEFAULT 'запланована', -- запланована, активна, завершена, скасована
    примітки TEXT,
    CONSTRAINT конференції_дати_check CHECK (дата_початку <= дата_закінчення),
    CONSTRAINT конференції_дедлайни_check CHECK (
        (дедлайн_реєстрації IS NULL OR дедлайн_реєстрації <= дата_початку) AND
        (дедлайн_тез IS NULL OR дедлайн_тез <= дата_початку)
    )
);

-- Conference sections (секції_конференцій)
CREATE TABLE секції_конференцій (
    ід SERIAL PRIMARY KEY,
    конференція_ід INTEGER NOT NULL REFERENCES конференції(ід) ON DELETE CASCADE,
    назва VARCHAR(255) NOT NULL,
    опис TEXT,
    голова_секції_ід INTEGER REFERENCES викладачі(ід),
    дата DATE,
    час_початку TIME,
    час_закінчення TIME,
    місце VARCHAR(255),
    максимум_доповідей INTEGER,
    примітки TEXT,
    CONSTRAINT секції_час_check CHECK (час_початку < час_закінчення OR час_початку IS NULL OR час_закінчення IS NULL)
);

-- Conference speakers (доповідачі_конференцій)
CREATE TABLE доповідачі_конференцій (
    ід SERIAL PRIMARY KEY,
    конференція_ід INTEGER NOT NULL REFERENCES конференції(ід) ON DELETE CASCADE,
    секція_ід INTEGER REFERENCES секції_конференцій(ід) ON DELETE CASCADE,
    викладач_ід INTEGER REFERENCES викладачі(ід),
    зовнішній_доповідач_прізвище VARCHAR(50),
    зовнішній_доповідач_імя VARCHAR(50),
    зовнішній_доповідач_установа VARCHAR(255),
    тема_доповіді VARCHAR(255) NOT NULL,
    тип_доповіді VARCHAR(50) NOT NULL, -- пленарна, секційна, стендова
    час_початку TIME,
    тривалість_хвилин INTEGER,
    короткий_опис TEXT,
    презентація_url VARCHAR(255),
    стаття_публікація_ід INTEGER REFERENCES публікації(ід),
    примітки TEXT,
    CONSTRAINT доповідачі_перевірка CHECK (
        (викладач_ід IS NOT NULL AND зовнішній_доповідач_прізвище IS NULL AND зовнішній_доповідач_імя IS NULL) OR
        (викладач_ід IS NULL AND зовнішній_доповідач_прізвище IS NOT NULL AND зовнішній_доповідач_імя IS NOT NULL)
    )
);

-- Conference participants (учасники_конференцій)
CREATE TABLE учасники_конференцій (
    ід SERIAL PRIMARY KEY,
    конференція_ід INTEGER NOT NULL REFERENCES конференції(ід) ON DELETE CASCADE,
    викладач_ід INTEGER REFERENCES викладачі(ід),
    студент_ід INTEGER REFERENCES студенти(ід),
    зовнішній_учасник_прізвище VARCHAR(50),
    зовнішній_учасник_імя VARCHAR(50),
    зовнішній_учасник_установа VARCHAR(255),
    роль VARCHAR(50) NOT NULL, -- учасник, організатор, доповідач, голова секції
    дата_реєстрації DATE NOT NULL DEFAULT CURRENT_DATE,
    оплата_статус VARCHAR(20) DEFAULT 'не оплачено', -- не оплачено, оплачено, не потрібна
    сертифікат_виданий BOOLEAN DEFAULT FALSE,
    примітки TEXT,
    CONSTRAINT учасники_перевірка CHECK (
        (викладач_ід IS NOT NULL AND студент_ід IS NULL AND зовнішній_учасник_прізвище IS NULL AND зовнішній_учасник_імя IS NULL) OR
        (викладач_ід IS NULL AND студент_ід IS NOT NULL AND зовнішній_учасник_прізвище IS NULL AND зовнішній_учасник_імя IS NULL) OR
        (викладач_ід IS NULL AND студент_ід IS NULL AND зовнішній_учасник_прізвище IS NOT NULL AND зовнішній_учасник_імя IS NOT NULL)
    )
);

-- Conference sponsorships (спонсорство_конференцій)
CREATE TABLE спонсорство_конференцій (
    ід SERIAL PRIMARY KEY,
    конференція_ід INTEGER NOT NULL REFERENCES конференції(ід) ON DELETE CASCADE,
    назва_організації VARCHAR(255) NOT NULL,
    тип_спонсорства VARCHAR(50) NOT NULL, -- головний, золотий, срібний, бронзовий, партнер
    сума_внеску DECIMAL(10, 2),
    валюта VARCHAR(3) DEFAULT 'UAH',
    контактна_особа VARCHAR(100),
    емейл VARCHAR(100),
    телефон VARCHAR(20),
    логотип_url VARCHAR(255),
    опис TEXT,
    примітки TEXT
); 