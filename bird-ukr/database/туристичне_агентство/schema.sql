-- Схема бази даних "Туристичне агентство"
-- Призначена для зберігання і управління даними туристичного агентства:
-- інформація про клієнтів, працівників, тури, готелі, транспорт, бронювання тощо

-- Налаштування кодування
SET client_encoding = 'UTF8';

-- Видалення таблиць, якщо вони існують
DROP TABLE IF EXISTS бронювання_турів CASCADE;
DROP TABLE IF EXISTS бронювання_готелів CASCADE;
DROP TABLE IF EXISTS бронювання_транспорту CASCADE;
DROP TABLE IF EXISTS платежі CASCADE;
DROP TABLE IF EXISTS тури CASCADE;
DROP TABLE IF EXISTS готелі CASCADE;
DROP TABLE IF EXISTS транспорт CASCADE;
DROP TABLE IF EXISTS країни CASCADE;
DROP TABLE IF EXISTS міста CASCADE;
DROP TABLE IF EXISTS клієнти CASCADE;
DROP TABLE IF EXISTS працівники CASCADE;
DROP TABLE IF EXISTS посади CASCADE;
DROP TABLE IF EXISTS відгуки CASCADE;
DROP TABLE IF EXISTS знижки CASCADE;
DROP TABLE IF EXISTS типи_кімнат CASCADE;
DROP TABLE IF EXISTS типи_транспорту CASCADE;
DROP TABLE IF EXISTS статуси_бронювання CASCADE;
DROP TABLE IF EXISTS методи_оплати CASCADE;
DROP TABLE IF EXISTS історія_пошуків CASCADE;

-- Створення таблиць

-- Таблиця "Посади"
CREATE TABLE посади (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    мін_зарплата DECIMAL(10, 2),
    макс_зарплата DECIMAL(10, 2)
);

-- Таблиця "Працівники"
CREATE TABLE працівники (
    id SERIAL PRIMARY KEY,
    прізвище VARCHAR(100) NOT NULL,
    імя VARCHAR(100) NOT NULL,
    по_батькові VARCHAR(100),
    дата_народження DATE,
    адреса TEXT,
    телефон VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    посада_id INTEGER REFERENCES посади(id),
    дата_прийому DATE NOT NULL,
    дата_звільнення DATE,
    зарплата DECIMAL(10, 2) NOT NULL,
    фото_url VARCHAR(255),
    CONSTRAINT перевірка_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Таблиця "Клієнти"
CREATE TABLE клієнти (
    id SERIAL PRIMARY KEY,
    прізвище VARCHAR(100) NOT NULL,
    імя VARCHAR(100) NOT NULL,
    по_батькові VARCHAR(100),
    дата_народження DATE,
    паспорт VARCHAR(20) NOT NULL,
    адреса TEXT,
    телефон VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE,
    примітки TEXT,
    дата_реєстрації DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT перевірка_email_клієнта CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Таблиця "Країни"
CREATE TABLE країни (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    код VARCHAR(3) NOT NULL UNIQUE,
    вимоги_для_візи TEXT,
    валюта VARCHAR(50),
    континент VARCHAR(50),
    мова VARCHAR(50)
);

-- Таблиця "Міста"
CREATE TABLE міста (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    країна_id INTEGER REFERENCES країни(id),
    опис TEXT,
    популярність INTEGER CHECK (популярність BETWEEN 1 AND 10),
    UNIQUE (назва, країна_id)
);

-- Таблиця "Типи кімнат"
CREATE TABLE типи_кімнат (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT
);

-- Таблиця "Готелі"
CREATE TABLE готелі (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(150) NOT NULL,
    адреса TEXT NOT NULL,
    місто_id INTEGER REFERENCES міста(id),
    зірок INTEGER CHECK (зірок BETWEEN 1 AND 5),
    опис TEXT,
    зручності TEXT,
    фото_url VARCHAR(255),
    веб_сайт VARCHAR(255),
    контактний_телефон VARCHAR(20),
    email VARCHAR(100),
    CONSTRAINT перевірка_email_готелю CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Таблиця "Типи транспорту"
CREATE TABLE типи_транспорту (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT
);

-- Таблиця "Транспорт"
CREATE TABLE транспорт (
    id SERIAL PRIMARY KEY,
    тип_id INTEGER REFERENCES типи_транспорту(id),
    компанія VARCHAR(150) NOT NULL,
    номер_рейсу VARCHAR(30),
    місто_відправлення_id INTEGER REFERENCES міста(id),
    місто_прибуття_id INTEGER REFERENCES міста(id),
    дата_відправлення TIMESTAMP NOT NULL,
    дата_прибуття TIMESTAMP NOT NULL,
    ціна DECIMAL(10, 2) NOT NULL,
    кількість_місць INTEGER NOT NULL,
    примітки TEXT,
    CONSTRAINT перевірка_дат CHECK (дата_прибуття > дата_відправлення)
);

-- Таблиця "Тури"
CREATE TABLE тури (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(200) NOT NULL,
    опис TEXT,
    країна_id INTEGER REFERENCES країни(id),
    місто_id INTEGER REFERENCES міста(id),
    готель_id INTEGER REFERENCES готелі(id),
    дата_початку DATE NOT NULL,
    дата_закінчення DATE NOT NULL,
    тривалість INTEGER GENERATED ALWAYS AS (date_part('day', дата_закінчення::timestamp - дата_початку::timestamp)) STORED,
    ціна DECIMAL(10, 2) NOT NULL,
    включено_харчування BOOLEAN DEFAULT false,
    тип_харчування VARCHAR(50),
    включені_екскурсії TEXT,
    максимальна_кількість_туристів INTEGER,
    активний BOOLEAN DEFAULT true,
    дата_створення DATE DEFAULT CURRENT_DATE,
    працівник_id INTEGER REFERENCES працівники(id),
    фото_url VARCHAR(255),
    CONSTRAINT перевірка_дат_туру CHECK (дата_закінчення > дата_початку)
);

-- Таблиця "Статуси бронювання"
CREATE TABLE статуси_бронювання (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL UNIQUE,
    опис TEXT
);

-- Таблиця "Методи оплати"
CREATE TABLE методи_оплати (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL UNIQUE,
    опис TEXT
);

-- Таблиця "Знижки"
CREATE TABLE знижки (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    відсоток DECIMAL(5, 2) NOT NULL,
    фіксована_сума DECIMAL(10, 2),
    дата_початку DATE,
    дата_закінчення DATE,
    активна BOOLEAN DEFAULT true,
    код VARCHAR(30) UNIQUE,
    CONSTRAINT перевірка_дат_знижки CHECK (дата_закінчення > дата_початку)
);

-- Таблиця "Бронювання турів"
CREATE TABLE бронювання_турів (
    id SERIAL PRIMARY KEY,
    клієнт_id INTEGER REFERENCES клієнти(id),
    тур_id INTEGER REFERENCES тури(id),
    дата_бронювання TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    кількість_осіб INTEGER NOT NULL DEFAULT 1,
    статус_id INTEGER REFERENCES статуси_бронювання(id),
    знижка_id INTEGER REFERENCES знижки(id),
    загальна_вартість DECIMAL(10, 2) NOT NULL,
    працівник_id INTEGER REFERENCES працівники(id),
    примітки TEXT,
    дата_підтвердження TIMESTAMP
);

-- Таблиця "Бронювання готелів"
CREATE TABLE бронювання_готелів (
    id SERIAL PRIMARY KEY,
    клієнт_id INTEGER REFERENCES клієнти(id),
    готель_id INTEGER REFERENCES готелі(id),
    тип_кімнати_id INTEGER REFERENCES типи_кімнат(id),
    дата_заїзду DATE NOT NULL,
    дата_виїзду DATE NOT NULL,
    кількість_кімнат INTEGER NOT NULL DEFAULT 1,
    кількість_осіб INTEGER NOT NULL DEFAULT 1,
    статус_id INTEGER REFERENCES статуси_бронювання(id),
    вартість DECIMAL(10, 2) NOT NULL,
    дата_бронювання TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    працівник_id INTEGER REFERENCES працівники(id),
    примітки TEXT,
    CONSTRAINT перевірка_дат_бронювання_готелю CHECK (дата_виїзду > дата_заїзду)
);

-- Таблиця "Бронювання транспорту"
CREATE TABLE бронювання_транспорту (
    id SERIAL PRIMARY KEY,
    клієнт_id INTEGER REFERENCES клієнти(id),
    транспорт_id INTEGER REFERENCES транспорт(id),
    дата_бронювання TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    кількість_місць INTEGER NOT NULL DEFAULT 1,
    статус_id INTEGER REFERENCES статуси_бронювання(id),
    вартість DECIMAL(10, 2) NOT NULL,
    працівник_id INTEGER REFERENCES працівники(id),
    примітки TEXT
);

-- Таблиця "Платежі"
CREATE TABLE платежі (
    id SERIAL PRIMARY KEY,
    бронювання_тур_id INTEGER REFERENCES бронювання_турів(id),
    бронювання_готель_id INTEGER REFERENCES бронювання_готелів(id),
    бронювання_транспорт_id INTEGER REFERENCES бронювання_транспорту(id),
    сума DECIMAL(10, 2) NOT NULL,
    дата_платежу TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    метод_оплати_id INTEGER REFERENCES методи_оплати(id),
    номер_транзакції VARCHAR(100),
    статус VARCHAR(50) DEFAULT 'Оплачено',
    примітки TEXT,
    працівник_id INTEGER REFERENCES працівники(id),
    CONSTRAINT один_тип_бронювання CHECK (
        (бронювання_тур_id IS NOT NULL AND бронювання_готель_id IS NULL AND бронювання_транспорт_id IS NULL) OR
        (бронювання_тур_id IS NULL AND бронювання_готель_id IS NOT NULL AND бронювання_транспорт_id IS NULL) OR
        (бронювання_тур_id IS NULL AND бронювання_готель_id IS NULL AND бронювання_транспорт_id IS NOT NULL)
    )
);

-- Таблиця "Відгуки"
CREATE TABLE відгуки (
    id SERIAL PRIMARY KEY,
    клієнт_id INTEGER REFERENCES клієнти(id),
    тур_id INTEGER REFERENCES тури(id),
    готель_id INTEGER REFERENCES готелі(id),
    оцінка INTEGER CHECK (оцінка BETWEEN 1 AND 5),
    коментар TEXT,
    дата_відгуку TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    модерований BOOLEAN DEFAULT false,
    фото_url VARCHAR(255),
    CONSTRAINT один_обєкт_відгуку CHECK (
        (тур_id IS NOT NULL AND готель_id IS NULL) OR
        (тур_id IS NULL AND готель_id IS NOT NULL)
    )
);

-- Таблиця "Історія пошуків"
CREATE TABLE історія_пошуків (
    id SERIAL PRIMARY KEY,
    клієнт_id INTEGER REFERENCES клієнти(id),
    пошуковий_запит TEXT NOT NULL,
    дата_пошуку TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    результати_знайдено INTEGER,
    ip_адреса VARCHAR(50),
    user_agent TEXT
);

-- Індекси для оптимізації запитів
CREATE INDEX idx_клієнти_прізвище ON клієнти(прізвище);
CREATE INDEX idx_тури_країна ON тури(країна_id);
CREATE INDEX idx_тури_місто ON тури(місто_id);
CREATE INDEX idx_тури_дати ON тури(дата_початку, дата_закінчення);
CREATE INDEX idx_бронювання_турів_клієнт ON бронювання_турів(клієнт_id);
CREATE INDEX idx_бронювання_турів_тур ON бронювання_турів(тур_id);
CREATE INDEX idx_бронювання_турів_статус ON бронювання_турів(статус_id);
CREATE INDEX idx_платежі_бронювання_тур ON платежі(бронювання_тур_id);
CREATE INDEX idx_відгуки_тур ON відгуки(тур_id);
CREATE INDEX idx_відгуки_готель ON відгуки(готель_id);
CREATE INDEX idx_відгуки_клієнт ON відгуки(клієнт_id);
CREATE INDEX idx_готелі_місто ON готелі(місто_id);
CREATE INDEX idx_міста_країна ON міста(країна_id);

-- Представлення для часто використовуваних запитів

-- Представлення "Активні тури з інформацією про країни та міста"
CREATE VIEW активні_тури AS
SELECT 
    т.id, т.назва, т.опис, т.дата_початку, т.дата_закінчення, т.тривалість, т.ціна,
    т.включено_харчування, т.тип_харчування, т.включені_екскурсії,
    к.назва AS країна, м.назва AS місто, г.назва AS готель, г.зірок AS зірок_готелю
FROM 
    тури т
    JOIN країни к ON т.країна_id = к.id
    JOIN міста м ON т.місто_id = м.id
    JOIN готелі г ON т.готель_id = г.id
WHERE 
    т.активний = true
    AND т.дата_початку > CURRENT_DATE;

-- Представлення "Інформація про всі бронювання"
CREATE VIEW інформація_про_бронювання AS
SELECT 
    б.id, б.дата_бронювання, б.кількість_осіб, б.загальна_вартість,
    к.прізвище || ' ' || к.імя AS клієнт, к.телефон AS телефон_клієнта,
    т.назва AS тур, т.дата_початку, т.дата_закінчення,
    кр.назва AS країна, м.назва AS місто,
    с.назва AS статус,
    п.прізвище || ' ' || п.імя AS працівник
FROM 
    бронювання_турів б
    JOIN клієнти к ON б.клієнт_id = к.id
    JOIN тури т ON б.тур_id = т.id
    JOIN країни кр ON т.країна_id = кр.id
    JOIN міста м ON т.місто_id = м.id
    JOIN статуси_бронювання с ON б.статус_id = с.id
    JOIN працівники п ON б.працівник_id = п.id;

-- Представлення "Рейтинг турів"
CREATE VIEW рейтинг_турів AS
SELECT 
    т.id, т.назва, к.назва AS країна, м.назва AS місто,
    ROUND(AVG(в.оцінка)::numeric, 1) AS середня_оцінка,
    COUNT(в.id) AS кількість_відгуків
FROM 
    тури т
    JOIN країни к ON т.країна_id = к.id
    JOIN міста м ON т.місто_id = м.id
    LEFT JOIN відгуки в ON т.id = в.тур_id
GROUP BY 
    т.id, т.назва, к.назва, м.назва
ORDER BY 
    середня_оцінка DESC;

-- Тригер для автоматичного оновлення вартості при наданні знижки
CREATE OR REPLACE FUNCTION розрахувати_вартість_зі_знижкою()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.знижка_id IS NOT NULL THEN
        SELECT INTO NEW.загальна_вартість
            CASE
                WHEN з.фіксована_сума IS NOT NULL THEN
                    т.ціна * NEW.кількість_осіб - з.фіксована_сума
                ELSE
                    т.ціна * NEW.кількість_осіб * (1 - з.відсоток / 100)
            END
        FROM тури т, знижки з
        WHERE т.id = NEW.тур_id AND з.id = NEW.знижка_id;
    ELSE
        SELECT INTO NEW.загальна_вартість т.ціна * NEW.кількість_осіб
        FROM тури т
        WHERE т.id = NEW.тур_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER тригер_розрахунку_вартості
BEFORE INSERT OR UPDATE OF знижка_id, кількість_осіб
ON бронювання_турів
FOR EACH ROW
EXECUTE FUNCTION розрахувати_вартість_зі_знижкою();

-- Тригер для логування змін статусів бронювання
CREATE TABLE логи_бронювань (
    id SERIAL PRIMARY KEY,
    бронювання_id INTEGER NOT NULL,
    тип_бронювання VARCHAR(20) NOT NULL, -- 'тур', 'готель', 'транспорт'
    старий_статус_id INTEGER,
    новий_статус_id INTEGER,
    дата_зміни TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    працівник_id INTEGER
);

CREATE OR REPLACE FUNCTION логувати_зміну_статусу()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.статус_id <> NEW.статус_id THEN
        INSERT INTO логи_бронювань (бронювання_id, тип_бронювання, старий_статус_id, новий_статус_id, працівник_id)
        VALUES (NEW.id, 'тур', OLD.статус_id, NEW.статус_id, NEW.працівник_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER тригер_зміни_статусу_бронювання_туру
AFTER UPDATE OF статус_id
ON бронювання_турів
FOR EACH ROW
EXECUTE FUNCTION логувати_зміну_статусу(); 