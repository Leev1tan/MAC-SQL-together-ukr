-- Schema for Hospital (лікарня) database
-- Created for Ukrainian Text-to-SQL dataset

-- Create database with UTF-8 encoding for Ukrainian language support
SET client_encoding = 'UTF8';

-- Departments (відділення)
CREATE TABLE відділення (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    скорочення VARCHAR(20),
    опис TEXT,
    поверх INTEGER NOT NULL,
    корпус VARCHAR(20) NOT NULL,
    кількість_палат INTEGER NOT NULL,
    кількість_ліжок INTEGER NOT NULL,
    завідувач_ід INTEGER, -- FK to лікарі, додасться пізніше через ALTER TABLE
    телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    активне BOOLEAN DEFAULT TRUE
);

-- Staff positions (посади_персоналу)
CREATE TABLE посади_персоналу (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    категорія VARCHAR(50) NOT NULL, -- 'лікар', 'медсестра', 'санітар', 'адміністрація', 'технічний персонал'
    опис TEXT,
    мінімальна_зарплата DECIMAL(10, 2) NOT NULL,
    максимальна_зарплата DECIMAL(10, 2) NOT NULL,
    вимагає_вищу_освіту BOOLEAN DEFAULT TRUE,
    вимагає_медичну_освіту BOOLEAN DEFAULT TRUE
);

-- Staff (персонал)
CREATE TABLE персонал (
    ід SERIAL PRIMARY KEY,
    табельний_номер VARCHAR(20) NOT NULL UNIQUE,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    стать CHAR(1) NOT NULL, -- 'Ч' або 'Ж'
    дата_народження DATE NOT NULL,
    посада_ід INTEGER NOT NULL REFERENCES посади_персоналу(ід),
    відділення_ід INTEGER REFERENCES відділення(ід),
    дата_прийняття DATE NOT NULL,
    дата_звільнення DATE,
    електронна_пошта VARCHAR(100),
    телефон VARCHAR(20) NOT NULL,
    адреса TEXT,
    освіта TEXT,
    спеціалізація VARCHAR(100),
    категорія VARCHAR(50), -- 'вища', 'перша', 'друга'
    наукова_ступінь VARCHAR(50),
    зарплата DECIMAL(10, 2) NOT NULL,
    графік_роботи VARCHAR(100), -- 'повний день', 'часткова зайнятість', 'змінний графік'
    фото_url VARCHAR(200),
    активний BOOLEAN DEFAULT TRUE,
    примітки TEXT
);

-- Add foreign key to відділення
ALTER TABLE відділення ADD CONSTRAINT fk_відділення_завідувач
    FOREIGN KEY (завідувач_ід) REFERENCES персонал(ід);

-- Doctors (лікарі) - view of персонал for convenience
CREATE VIEW лікарі AS
SELECT п.*
FROM персонал п
JOIN посади_персоналу пп ON п.посада_ід = пп.ід
WHERE пп.категорія = 'лікар';

-- Specializations (спеціалізації)
CREATE TABLE спеціалізації (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT,
    код VARCHAR(20) UNIQUE
);

-- Doctor specializations (спеціалізації_лікарів)
CREATE TABLE спеціалізації_лікарів (
    лікар_ід INTEGER NOT NULL REFERENCES персонал(ід),
    спеціалізація_ід INTEGER NOT NULL REFERENCES спеціалізації(ід),
    дата_отримання DATE NOT NULL,
    сертифікат_номер VARCHAR(50),
    дійсна_до DATE,
    PRIMARY KEY (лікар_ід, спеціалізація_ід)
);

-- Patients (пацієнти)
CREATE TABLE пацієнти (
    ід SERIAL PRIMARY KEY,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    стать CHAR(1) NOT NULL, -- 'Ч' або 'Ж'
    дата_народження DATE NOT NULL,
    ідентифікаційний_код VARCHAR(20) UNIQUE,
    паспорт_серія VARCHAR(10),
    паспорт_номер VARCHAR(20),
    поліс_номер VARCHAR(50),
    група_крові VARCHAR(10),
    резус_фактор CHAR(1), -- '+' або '-'
    адреса TEXT,
    телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    контактна_особа VARCHAR(100),
    контактний_телефон VARCHAR(20),
    дата_реєстрації DATE NOT NULL DEFAULT CURRENT_DATE,
    алергії TEXT,
    хронічні_захворювання TEXT,
    примітки TEXT
);

-- Insurance companies (страхові_компанії)
CREATE TABLE страхові_компанії (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    адреса TEXT,
    телефон VARCHAR(20) NOT NULL,
    електронна_пошта VARCHAR(100),
    контактна_особа VARCHAR(100),
    номер_договору VARCHAR(50),
    дата_початку_договору DATE,
    дата_закінчення_договору DATE,
    умови_співпраці TEXT,
    активна BOOLEAN DEFAULT TRUE
);

-- Patient insurance (страховки_пацієнтів)
CREATE TABLE страховки_пацієнтів (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    страхова_компанія_ід INTEGER NOT NULL REFERENCES страхові_компанії(ід),
    номер_поліса VARCHAR(50) NOT NULL,
    дата_початку DATE NOT NULL,
    дата_закінчення DATE NOT NULL,
    тип VARCHAR(50) NOT NULL, -- 'базова', 'розширена', 'преміум'
    покриття DECIMAL(10, 2) NOT NULL, -- максимальна сума покриття
    умови TEXT,
    активна BOOLEAN DEFAULT TRUE,
    UNIQUE (пацієнт_ід, страхова_компанія_ід, номер_поліса)
);

-- Disease types (типи_хвороб)
CREATE TABLE типи_хвороб (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT
);

-- Diseases (хвороби)
CREATE TABLE хвороби (
    ід SERIAL PRIMARY KEY,
    код_мкх VARCHAR(20) NOT NULL UNIQUE, -- Код по МКХ-10
    назва VARCHAR(200) NOT NULL,
    тип_ід INTEGER NOT NULL REFERENCES типи_хвороб(ід),
    опис TEXT,
    симптоми TEXT,
    рекомендації TEXT,
    тривалість_лікування_днів INTEGER,
    інфекційна BOOLEAN DEFAULT FALSE,
    спадкова BOOLEAN DEFAULT FALSE,
    хронічна BOOLEAN DEFAULT FALSE
);

-- Visits (візити)
CREATE TABLE візити (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    лікар_ід INTEGER NOT NULL REFERENCES персонал(ід),
    дата_час TIMESTAMP NOT NULL,
    тип VARCHAR(50) NOT NULL, -- 'первинний', 'повторний', 'консультація', 'процедура'
    причина TEXT,
    тривалість_хвилин INTEGER DEFAULT 30,
    статус VARCHAR(50) NOT NULL DEFAULT 'запланований', -- 'запланований', 'в процесі', 'завершений', 'скасований', 'неявка'
    скарги TEXT,
    рекомендації TEXT,
    наступний_візит_дата DATE,
    примітки TEXT
);

-- Diagnoses (діагнози)
CREATE TABLE діагнози (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    хвороба_ід INTEGER NOT NULL REFERENCES хвороби(ід),
    лікар_ід INTEGER NOT NULL REFERENCES персонал(ід),
    візит_ід INTEGER REFERENCES візити(ід),
    дата_встановлення DATE NOT NULL,
    тип VARCHAR(50) NOT NULL, -- 'первинний', 'уточнений', 'заключний'
    опис TEXT,
    тяжкість VARCHAR(20), -- 'легка', 'середня', 'тяжка'
    ускладнення TEXT,
    статус VARCHAR(50) NOT NULL DEFAULT 'активний', -- 'активний', 'вилікуваний', 'хронічний', 'в ремісії'
    дата_закриття DATE,
    примітки TEXT
);

-- Diagnosis symptoms (симптоми_діагнозу)
CREATE TABLE симптоми_діагнозу (
    ід SERIAL PRIMARY KEY,
    діагноз_ід INTEGER NOT NULL REFERENCES діагнози(ід),
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    тяжкість VARCHAR(20), -- 'легка', 'середня', 'тяжка'
    дата_початку DATE,
    дата_закінчення DATE
);

-- Hospitalizations (госпіталізації)
CREATE TABLE госпіталізації (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    відділення_ід INTEGER NOT NULL REFERENCES відділення(ід),
    лікар_ід INTEGER NOT NULL REFERENCES персонал(ід),
    діагноз_ід INTEGER REFERENCES діагнози(ід),
    дата_надходження TIMESTAMP NOT NULL,
    дата_виписки TIMESTAMP,
    тип_госпіталізації VARCHAR(50) NOT NULL, -- 'планова', 'екстрена', 'переведення'
    стан_при_надходженні VARCHAR(50) NOT NULL, -- 'задовільний', 'середньої тяжкості', 'тяжкий', 'критичний'
    стан_при_виписці VARCHAR(50), -- 'одужання', 'покращення', 'без змін', 'погіршення', 'смерть'
    палата VARCHAR(20),
    ліжко VARCHAR(20),
    примітки TEXT
);

-- Medications (медикаменти)
CREATE TABLE медикаменти (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    назва_міжнародна VARCHAR(100),
    виробник VARCHAR(100),
    форма_випуску VARCHAR(50) NOT NULL, -- 'таблетки', 'капсули', 'ін'єкції', 'сироп'
    дозування VARCHAR(50) NOT NULL,
    одиниця_виміру VARCHAR(20) NOT NULL, -- 'мг', 'мл', 'г'
    кількість_в_упаковці INTEGER NOT NULL,
    код_атх VARCHAR(20) UNIQUE, -- Anatomical Therapeutic Chemical код
    рецептурний BOOLEAN DEFAULT FALSE,
    опис TEXT,
    показання TEXT,
    протипоказання TEXT,
    побічні_ефекти TEXT,
    ціна DECIMAL(10, 2) NOT NULL,
    наявність INTEGER DEFAULT 0,
    активний BOOLEAN DEFAULT TRUE
);

-- Prescriptions (рецепти)
CREATE TABLE рецепти (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    лікар_ід INTEGER NOT NULL REFERENCES персонал(ід),
    діагноз_ід INTEGER NOT NULL REFERENCES діагнози(ід),
    візит_ід INTEGER REFERENCES візити(ід),
    госпіталізація_ід INTEGER REFERENCES госпіталізації(ід),
    дата_виписки DATE NOT NULL,
    дійсний_до DATE NOT NULL,
    номер VARCHAR(50) UNIQUE,
    статус VARCHAR(50) NOT NULL DEFAULT 'активний', -- 'активний', 'закритий', 'скасований'
    примітки TEXT
);

-- Prescription items (позиції_рецепту)
CREATE TABLE позиції_рецепту (
    ід SERIAL PRIMARY KEY,
    рецепт_ід INTEGER NOT NULL REFERENCES рецепти(ід),
    медикамент_ід INTEGER NOT NULL REFERENCES медикаменти(ід),
    дозування VARCHAR(50) NOT NULL,
    частота_прийому VARCHAR(100) NOT NULL, -- '3 рази на день', 'кожні 4 години'
    тривалість_днів INTEGER NOT NULL,
    інструкції TEXT,
    кількість INTEGER NOT NULL
);

-- Services (послуги)
CREATE TABLE послуги (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    категорія VARCHAR(50) NOT NULL, -- 'консультація', 'діагностика', 'процедура', 'операція', 'лабораторний аналіз'
    тривалість_хвилин INTEGER,
    опис TEXT,
    ціна DECIMAL(10, 2) NOT NULL,
    необхідна_спеціалізація_ід INTEGER REFERENCES спеціалізації(ід),
    код VARCHAR(20) UNIQUE,
    інструкції TEXT,
    протипоказання TEXT,
    підготовка TEXT,
    активна BOOLEAN DEFAULT TRUE
);

-- Provided services (надані_послуги)
CREATE TABLE надані_послуги (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    послуга_ід INTEGER NOT NULL REFERENCES послуги(ід),
    лікар_ід INTEGER NOT NULL REFERENCES персонал(ід),
    асистент_ід INTEGER REFERENCES персонал(ід),
    візит_ід INTEGER REFERENCES візити(ід),
    госпіталізація_ід INTEGER REFERENCES госпіталізації(ід),
    дата_час TIMESTAMP NOT NULL,
    результат TEXT,
    примітки TEXT,
    ціна DECIMAL(10, 2) NOT NULL,
    статус VARCHAR(50) NOT NULL DEFAULT 'запланована', -- 'запланована', 'в процесі', 'виконана', 'скасована'
    оплачена BOOLEAN DEFAULT FALSE
);

-- Laboratory test types (типи_аналізів)
CREATE TABLE типи_аналізів (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    категорія VARCHAR(50) NOT NULL, -- 'кров', 'сеча', 'біохімія', 'мікробіологія', 'генетика'
    опис TEXT,
    код VARCHAR(20) UNIQUE,
    підготовка_пацієнта TEXT,
    термін_виконання VARCHAR(50), -- '1 день', '3 дні', '1 тиждень'
    ціна DECIMAL(10, 2) NOT NULL,
    активний BOOLEAN DEFAULT TRUE
);

-- Laboratory tests (аналізи)
CREATE TABLE аналізи (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    тип_аналізу_ід INTEGER NOT NULL REFERENCES типи_аналізів(ід),
    замовлення_дата TIMESTAMP NOT NULL,
    забір_зразка_дата TIMESTAMP,
    результат_дата TIMESTAMP,
    результат TEXT,
    висновок TEXT,
    лаборант_ід INTEGER REFERENCES персонал(ід),
    лікар_направив_ід INTEGER NOT NULL REFERENCES персонал(ід),
    візит_ід INTEGER REFERENCES візити(ід),
    госпіталізація_ід INTEGER REFERENCES госпіталізації(ід),
    статус VARCHAR(50) NOT NULL DEFAULT 'замовлено', -- 'замовлено', 'зразок взято', 'в обробці', 'виконано', 'скасовано'
    примітки TEXT,
    ціна DECIMAL(10, 2) NOT NULL,
    оплачено BOOLEAN DEFAULT FALSE
);

-- Analysis parameters (параметри_аналізу)
CREATE TABLE параметри_аналізу (
    ід SERIAL PRIMARY KEY,
    аналіз_ід INTEGER NOT NULL REFERENCES аналізи(ід),
    назва VARCHAR(100) NOT NULL,
    значення VARCHAR(100) NOT NULL,
    одиниця_виміру VARCHAR(20),
    референтний_діапазон VARCHAR(100), -- нормальні значення
    поза_нормою BOOLEAN DEFAULT FALSE, -- результат поза референтним діапазоном
    інтерпретація TEXT
);

-- Payments (оплати)
CREATE TABLE оплати (
    ід SERIAL PRIMARY KEY,
    пацієнт_ід INTEGER NOT NULL REFERENCES пацієнти(ід),
    сума DECIMAL(10, 2) NOT NULL,
    дата_час TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    тип VARCHAR(50) NOT NULL, -- 'консультація', 'аналіз', 'послуга', 'госпіталізація', 'медикаменти'
    опис TEXT,
    страховка_ід INTEGER REFERENCES страховки_пацієнтів(ід),
    сума_страхування DECIMAL(10, 2) DEFAULT 0,
    спосіб_оплати VARCHAR(50) NOT NULL, -- 'готівка', 'картка', 'страховка'
    статус VARCHAR(50) NOT NULL DEFAULT 'оплачено', -- 'оплачено', 'частково оплачено', 'очікує оплати', 'скасовано'
    квитанція_номер VARCHAR(50),
    примітки TEXT
);

-- Payment details (деталі_оплати)
CREATE TABLE деталі_оплати (
    ід SERIAL PRIMARY KEY,
    оплата_ід INTEGER NOT NULL REFERENCES оплати(ід),
    послуга_ід INTEGER REFERENCES послуги(ід),
    аналіз_ід INTEGER REFERENCES аналізи(ід),
    госпіталізація_ід INTEGER REFERENCES госпіталізації(ід),
    рецепт_ід INTEGER REFERENCES рецепти(ід),
    візит_ід INTEGER REFERENCES візити(ід),
    сума DECIMAL(10, 2) NOT NULL,
    примітки TEXT,
    CHECK (
        (послуга_ід IS NOT NULL AND аналіз_ід IS NULL AND госпіталізація_ід IS NULL AND рецепт_ід IS NULL AND візит_ід IS NULL) OR
        (послуга_ід IS NULL AND аналіз_ід IS NOT NULL AND госпіталізація_ід IS NULL AND рецепт_ід IS NULL AND візит_ід IS NULL) OR
        (послуга_ід IS NULL AND аналіз_ід IS NULL AND госпіталізація_ід IS NOT NULL AND рецепт_ід IS NULL AND візит_ід IS NULL) OR
        (послуга_ід IS NULL AND аналіз_ід IS NULL AND госпіталізація_ід IS NULL AND рецепт_ід IS NOT NULL AND візит_ід IS NULL) OR
        (послуга_ід IS NULL AND аналіз_ід IS NULL AND госпіталізація_ід IS NULL AND рецепт_ід IS NULL AND візит_ід IS NOT NULL)
    )
);

-- Create indexes for better performance
CREATE INDEX idx_персонал_посада ON персонал(посада_ід);
CREATE INDEX idx_персонал_відділення ON персонал(відділення_ід);
CREATE INDEX idx_спеціалізації_лікарів_лікар ON спеціалізації_лікарів(лікар_ід);
CREATE INDEX idx_спеціалізації_лікарів_спеціалізація ON спеціалізації_лікарів(спеціалізація_ід);
CREATE INDEX idx_страховки_пацієнтів_пацієнт ON страховки_пацієнтів(пацієнт_ід);
CREATE INDEX idx_страховки_пацієнтів_страхова_компанія ON страховки_пацієнтів(страхова_компанія_ід);
CREATE INDEX idx_хвороби_тип ON хвороби(тип_ід);
CREATE INDEX idx_візити_пацієнт ON візити(пацієнт_ід);
CREATE INDEX idx_візити_лікар ON візити(лікар_ід);
CREATE INDEX idx_візити_дата_час ON візити(дата_час);
CREATE INDEX idx_діагнози_пацієнт ON діагнози(пацієнт_ід);
CREATE INDEX idx_діагнози_хвороба ON діагнози(хвороба_ід);
CREATE INDEX idx_діагнози_лікар ON діагнози(лікар_ід);
CREATE INDEX idx_діагнози_візит ON діагнози(візит_ід);
CREATE INDEX idx_симптоми_діагнозу_діагноз ON симптоми_діагнозу(діагноз_ід);
CREATE INDEX idx_госпіталізації_пацієнт ON госпіталізації(пацієнт_ід);
CREATE INDEX idx_госпіталізації_відділення ON госпіталізації(відділення_ід);
CREATE INDEX idx_госпіталізації_лікар ON госпіталізації(лікар_ід);
CREATE INDEX idx_госпіталізації_діагноз ON госпіталізації(діагноз_ід);
CREATE INDEX idx_рецепти_пацієнт ON рецепти(пацієнт_ід);
CREATE INDEX idx_рецепти_лікар ON рецепти(лікар_ід);
CREATE INDEX idx_рецепти_діагноз ON рецепти(діагноз_ід);
CREATE INDEX idx_рецепти_візит ON рецепти(візит_ід);
CREATE INDEX idx_рецепти_госпіталізація ON рецепти(госпіталізація_ід);
CREATE INDEX idx_позиції_рецепту_рецепт ON позиції_рецепту(рецепт_ід);
CREATE INDEX idx_позиції_рецепту_медикамент ON позиції_рецепту(медикамент_ід);
CREATE INDEX idx_надані_послуги_пацієнт ON надані_послуги(пацієнт_ід);
CREATE INDEX idx_надані_послуги_послуга ON надані_послуги(послуга_ід);
CREATE INDEX idx_надані_послуги_лікар ON надані_послуги(лікар_ід);
CREATE INDEX idx_надані_послуги_візит ON надані_послуги(візит_ід);
CREATE INDEX idx_надані_послуги_госпіталізація ON надані_послуги(госпіталізація_ід);
CREATE INDEX idx_аналізи_пацієнт ON аналізи(пацієнт_ід);
CREATE INDEX idx_аналізи_тип ON аналізи(тип_аналізу_ід);
CREATE INDEX idx_аналізи_лаборант ON аналізи(лаборант_ід);
CREATE INDEX idx_аналізи_лікар ON аналізи(лікар_направив_ід);
CREATE INDEX idx_аналізи_візит ON аналізи(візит_ід);
CREATE INDEX idx_аналізи_госпіталізація ON аналізи(госпіталізація_ід);
CREATE INDEX idx_параметри_аналізу_аналіз ON параметри_аналізу(аналіз_ід);
CREATE INDEX idx_оплати_пацієнт ON оплати(пацієнт_ід);
CREATE INDEX idx_оплати_страховка ON оплати(страховка_ід);
CREATE INDEX idx_деталі_оплати_оплата ON деталі_оплати(оплата_ід);
CREATE INDEX idx_деталі_оплати_послуга ON деталі_оплати(послуга_ід);
CREATE INDEX idx_деталі_оплати_аналіз ON деталі_оплати(аналіз_ід);
CREATE INDEX idx_деталі_оплати_госпіталізація ON деталі_оплати(госпіталізація_ід);
CREATE INDEX idx_деталі_оплати_рецепт ON деталі_оплати(рецепт_ід);
CREATE INDEX idx_деталі_оплати_візит ON деталі_оплати(візит_ід); 