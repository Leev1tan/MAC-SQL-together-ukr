-- Схема бази даних "Ресторан"
-- Кодування: UTF-8
-- Частина українського набору даних для задач Text-to-SQL (BIRD-type benchmark)

-- =============================================
-- Налаштування бази даних
-- =============================================

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- Видалення таблиць, якщо вони існують (для чистого імпорту)
DROP TABLE IF EXISTS постачання CASCADE;
DROP TABLE IF EXISTS використання_інгредієнтів CASCADE;
DROP TABLE IF EXISTS інгредієнти CASCADE;
DROP TABLE IF EXISTS постачальники CASCADE;
DROP TABLE IF EXISTS позиції_замовлення CASCADE;
DROP TABLE IF EXISTS замовлення CASCADE;
DROP TABLE IF EXISTS резервації CASCADE;
DROP TABLE IF EXISTS столики CASCADE;
DROP TABLE IF EXISTS страви CASCADE;
DROP TABLE IF EXISTS категорії CASCADE;
DROP TABLE IF EXISTS зміни_персоналу CASCADE;
DROP TABLE IF EXISTS персонал CASCADE;
DROP TABLE IF EXISTS посади CASCADE;
DROP TABLE IF EXISTS статуси_замовлень CASCADE;
DROP TABLE IF EXISTS статуси_резервацій CASCADE;
DROP TABLE IF EXISTS методи_оплати CASCADE;
DROP TABLE IF EXISTS клієнти CASCADE;

-- =============================================
-- Створення довідникових таблиць
-- =============================================

-- Посади персоналу ресторану
CREATE TABLE посади (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT,
    базова_зарплата DECIMAL(10, 2),
    додатковий_відсоток DECIMAL(5, 2) DEFAULT 0.0,
    CONSTRAINT посади_унікальні_назви UNIQUE (назва)
);

-- Статуси замовлень
CREATE TABLE статуси_замовлень (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT,
    є_фінальним BOOLEAN DEFAULT FALSE,
    CONSTRAINT статуси_замовлень_унікальні_назви UNIQUE (назва)
);

-- Статуси резервацій
CREATE TABLE статуси_резервацій (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT,
    є_фінальним BOOLEAN DEFAULT FALSE,
    CONSTRAINT статуси_резервацій_унікальні_назви UNIQUE (назва)
);

-- Методи оплати
CREATE TABLE методи_оплати (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT,
    активний BOOLEAN DEFAULT TRUE,
    комісія_відсоток DECIMAL(5, 2) DEFAULT 0.0,
    CONSTRAINT методи_оплати_унікальні_назви UNIQUE (назва)
);

-- =============================================
-- Створення основних таблиць
-- =============================================

-- Персонал ресторану
CREATE TABLE персонал (
    ід SERIAL PRIMARY KEY,
    посада_ід INTEGER NOT NULL REFERENCES посади(ід),
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE,
    телефон VARCHAR(15),
    адреса TEXT,
    email VARCHAR(100),
    дата_прийому DATE NOT NULL,
    дата_звільнення DATE,
    ставка_зарплати DECIMAL(10, 2) NOT NULL,
    активний BOOLEAN DEFAULT TRUE,
    примітки TEXT,
    CONSTRAINT персонал_дати_роботи_перевірка CHECK (дата_прийому <= дата_звільнення OR дата_звільнення IS NULL)
);

-- Робочі зміни персоналу
CREATE TABLE зміни_персоналу (
    ід SERIAL PRIMARY KEY,
    персонал_ід INTEGER NOT NULL REFERENCES персонал(ід),
    дата DATE NOT NULL,
    час_початку TIME NOT NULL,
    час_кінця TIME NOT NULL,
    фактичний_час_початку TIME,
    фактичний_час_кінця TIME,
    перерва_хвилин INTEGER DEFAULT 0,
    оплата_за_зміну DECIMAL(10, 2),
    примітки TEXT,
    CONSTRAINT зміни_персоналу_час_перевірка CHECK (час_початку < час_кінця),
    CONSTRAINT зміни_персоналу_фактичний_час_перевірка CHECK (
        (фактичний_час_початку IS NULL AND фактичний_час_кінця IS NULL) OR
        (фактичний_час_початку IS NOT NULL AND фактичний_час_кінця IS NOT NULL AND фактичний_час_початку < фактичний_час_кінця)
    )
);

-- Категорії страв
CREATE TABLE категорії (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    батьківська_категорія_ід INTEGER REFERENCES категорії(ід),
    порядок_сортування INTEGER DEFAULT 0,
    зображення_url VARCHAR(255),
    активна BOOLEAN DEFAULT TRUE,
    CONSTRAINT категорії_унікальні_назви UNIQUE (назва)
);

-- Страви (меню)
CREATE TABLE страви (
    ід SERIAL PRIMARY KEY,
    категорія_ід INTEGER NOT NULL REFERENCES категорії(ід),
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    ціна DECIMAL(10, 2) NOT NULL,
    вага_грам INTEGER,
    час_приготування_хвилин INTEGER,
    калорійність INTEGER,
    вегетаріанська BOOLEAN DEFAULT FALSE,
    гостра BOOLEAN DEFAULT FALSE,
    безглютенова BOOLEAN DEFAULT FALSE,
    зображення_url VARCHAR(255),
    порядок_в_меню INTEGER DEFAULT 0,
    активна BOOLEAN DEFAULT TRUE,
    дата_додавання DATE DEFAULT CURRENT_DATE,
    дата_оновлення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    примітки TEXT,
    CONSTRAINT страви_ціна_перевірка CHECK (ціна > 0)
);

-- Столики ресторану
CREATE TABLE столики (
    ід SERIAL PRIMARY KEY,
    номер VARCHAR(10) NOT NULL,
    опис TEXT,
    кількість_місць INTEGER NOT NULL,
    розташування VARCHAR(100),
    для_курців BOOLEAN DEFAULT FALSE,
    активний BOOLEAN DEFAULT TRUE,
    примітки TEXT,
    CONSTRAINT столики_унікальні_номери UNIQUE (номер),
    CONSTRAINT столики_місця_перевірка CHECK (кількість_місць > 0)
);

-- Резервації столиків
CREATE TABLE резервації (
    ід SERIAL PRIMARY KEY,
    столик_ід INTEGER NOT NULL REFERENCES столики(ід),
    статус_ід INTEGER NOT NULL REFERENCES статуси_резервацій(ід),
    дата DATE NOT NULL,
    час_початку TIME NOT NULL,
    час_кінця TIME NOT NULL,
    прізвище_клієнта VARCHAR(50) NOT NULL,
    імя_клієнта VARCHAR(50) NOT NULL,
    телефон_клієнта VARCHAR(15) NOT NULL,
    кількість_гостей INTEGER NOT NULL,
    особливі_побажання TEXT,
    створено TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    резервацію_прийняв_ід INTEGER REFERENCES персонал(ід),
    відмітка_про_відвідування BOOLEAN,
    примітки TEXT,
    CONSTRAINT резервації_час_перевірка CHECK (час_початку < час_кінця),
    CONSTRAINT резервації_гості_перевірка CHECK (кількість_гостей > 0)
);

-- Замовлення
CREATE TABLE замовлення (
    ід SERIAL PRIMARY KEY,
    резервація_ід INTEGER REFERENCES резервації(ід),
    столик_ід INTEGER REFERENCES столики(ід),
    статус_ід INTEGER NOT NULL REFERENCES статуси_замовлень(ід),
    офіціант_ід INTEGER REFERENCES персонал(ід),
    дата_час TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    кількість_клієнтів INTEGER NOT NULL,
    загальна_сума DECIMAL(10, 2) DEFAULT 0,
    сума_знижки DECIMAL(10, 2) DEFAULT 0,
    фінальна_сума DECIMAL(10, 2) DEFAULT 0,
    метод_оплати_ід INTEGER REFERENCES методи_оплати(ід),
    чайові DECIMAL(10, 2) DEFAULT 0,
    коментар_клієнта TEXT,
    примітки TEXT,
    CONSTRAINT замовлення_клієнти_перевірка CHECK (кількість_клієнтів > 0),
    CONSTRAINT замовлення_суми_перевірка CHECK (загальна_сума >= 0 AND сума_знижки >= 0 AND фінальна_сума >= 0),
    CONSTRAINT замовлення_референс_перевірка CHECK (
        (резервація_ід IS NOT NULL AND столик_ід IS NULL) OR
        (резервація_ід IS NULL AND столик_ід IS NOT NULL) OR
        (резервація_ід IS NOT NULL AND столик_ід IS NOT NULL)
    )
);

-- Позиції замовлення
CREATE TABLE позиції_замовлення (
    ід SERIAL PRIMARY KEY,
    замовлення_ід INTEGER NOT NULL REFERENCES замовлення(ід) ON DELETE CASCADE,
    страва_ід INTEGER NOT NULL REFERENCES страви(ід),
    кількість INTEGER NOT NULL DEFAULT 1,
    ціна_за_одиницю DECIMAL(10, 2) NOT NULL,
    загальна_ціна DECIMAL(10, 2) NOT NULL,
    знижка_відсоток DECIMAL(5, 2) DEFAULT 0,
    коментар TEXT,
    стан VARCHAR(50) DEFAULT 'нове', -- нове, готується, готове, подано, скасовано
    час_замовлення TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    час_приготування TIMESTAMP,
    час_подачі TIMESTAMP,
    CONSTRAINT позиції_замовлення_кількість_перевірка CHECK (кількість > 0),
    CONSTRAINT позиції_замовлення_ціни_перевірка CHECK (ціна_за_одиницю >= 0 AND загальна_ціна >= 0),
    CONSTRAINT позиції_замовлення_знижка_перевірка CHECK (знижка_відсоток >= 0 AND знижка_відсоток <= 100)
);

-- Постачальники
CREATE TABLE постачальники (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    контактна_особа VARCHAR(100),
    телефон VARCHAR(15),
    email VARCHAR(100),
    адреса TEXT,
    опис TEXT,
    умови_оплати TEXT,
    термін_доставки VARCHAR(50),
    активний BOOLEAN DEFAULT TRUE,
    дата_створення DATE DEFAULT CURRENT_DATE,
    примітки TEXT,
    CONSTRAINT постачальники_унікальні_назви UNIQUE (назва)
);

-- Інгредієнти
CREATE TABLE інгредієнти (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    одиниця_виміру VARCHAR(20) NOT NULL,
    кількість_на_складі DECIMAL(10, 2) DEFAULT 0,
    мінімальна_кількість DECIMAL(10, 2) DEFAULT 0,
    середня_ціна DECIMAL(10, 2),
    алерген BOOLEAN DEFAULT FALSE,
    категорія VARCHAR(50),
    постачальник_ід INTEGER REFERENCES постачальники(ід),
    термін_зберігання INTEGER, -- у днях
    умови_зберігання TEXT,
    активний BOOLEAN DEFAULT TRUE,
    примітки TEXT,
    CONSTRAINT інгредієнти_унікальні_назви UNIQUE (назва),
    CONSTRAINT інгредієнти_кількість_перевірка CHECK (кількість_на_складі >= 0 AND мінімальна_кількість >= 0)
);

-- Використання інгредієнтів у стравах
CREATE TABLE використання_інгредієнтів (
    ід SERIAL PRIMARY KEY,
    страва_ід INTEGER NOT NULL REFERENCES страви(ід) ON DELETE CASCADE,
    інгредієнт_ід INTEGER NOT NULL REFERENCES інгредієнти(ід),
    кількість DECIMAL(10, 3) NOT NULL,
    обовязковий BOOLEAN DEFAULT TRUE,
    замінний BOOLEAN DEFAULT FALSE,
    альтернативний_інгредієнт_ід INTEGER REFERENCES інгредієнти(ід),
    примітки TEXT,
    CONSTRAINT використання_інгредієнтів_унікальність UNIQUE (страва_ід, інгредієнт_ід),
    CONSTRAINT використання_інгредієнтів_кількість_перевірка CHECK (кількість > 0)
);

-- Постачання інгредієнтів
CREATE TABLE постачання (
    ід SERIAL PRIMARY KEY,
    постачальник_ід INTEGER NOT NULL REFERENCES постачальники(ід),
    інгредієнт_ід INTEGER NOT NULL REFERENCES інгредієнти(ід),
    дата_постачання DATE NOT NULL,
    кількість DECIMAL(10, 2) NOT NULL,
    ціна_за_одиницю DECIMAL(10, 2) NOT NULL,
    загальна_вартість DECIMAL(10, 2) NOT NULL,
    номер_накладної VARCHAR(50),
    примітки TEXT,
    CONSTRAINT постачання_кількість_перевірка CHECK (кількість > 0),
    CONSTRAINT постачання_ціни_перевірка CHECK (ціна_за_одиницю > 0 AND загальна_вартість > 0)
);

-- Таблиця клієнтів (постійних)
CREATE TABLE клієнти (
    ід INT PRIMARY KEY,
    прізвище VARCHAR(50) NOT NULL,
    ім_я VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    телефон VARCHAR(20) NOT NULL,
    електронна_пошта VARCHAR(100),
    дата_народження DATE,
    дата_реєстрації DATE NOT NULL,
    кількість_відвідувань INT DEFAULT 0,
    загальна_сума_замовлень DECIMAL(10,2) DEFAULT 0,
    примітки TEXT
);

-- =============================================
-- Створення індексів для оптимізації запитів
-- =============================================

-- Індекси для персоналу
CREATE INDEX персонал_прізвище_імя_idx ON персонал(прізвище, імя);
CREATE INDEX персонал_активний_idx ON персонал(активний);
CREATE INDEX персонал_посада_idx ON персонал(посада_ід);

-- Індекси для робочих змін
CREATE INDEX зміни_персоналу_дата_idx ON зміни_персоналу(дата);
CREATE INDEX зміни_персоналу_персонал_idx ON зміни_персоналу(персонал_ід);

-- Індекси для столиків та резервацій
CREATE INDEX столики_активний_місця_idx ON столики(активний, кількість_місць);
CREATE INDEX резервації_дата_час_idx ON резервації(дата, час_початку, час_кінця);
CREATE INDEX резервації_столик_idx ON резервації(столик_ід);
CREATE INDEX резервації_статус_idx ON резервації(статус_ід);
CREATE INDEX резервації_клієнт_idx ON резервації(прізвище_клієнта, телефон_клієнта);

-- Індекси для замовлень та позицій
CREATE INDEX замовлення_дата_час_idx ON замовлення(дата_час);
CREATE INDEX замовлення_статус_idx ON замовлення(статус_ід);
CREATE INDEX замовлення_офіціант_idx ON замовлення(офіціант_ід);
CREATE INDEX замовлення_столик_idx ON замовлення(столик_ід);
CREATE INDEX замовлення_резервація_idx ON замовлення(резервація_ід);
CREATE INDEX позиції_замовлення_замовлення_idx ON позиції_замовлення(замовлення_ід);
CREATE INDEX позиції_замовлення_страва_idx ON позиції_замовлення(страва_ід);
CREATE INDEX позиції_замовлення_стан_idx ON позиції_замовлення(стан);

-- Індекси для страв та категорій
CREATE INDEX страви_категорія_idx ON страви(категорія_ід);
CREATE INDEX страви_активна_idx ON страви(активна);
CREATE INDEX категорії_активна_idx ON категорії(активна);
CREATE INDEX категорії_батьківська_idx ON категорії(батьківська_категорія_ід);

-- Індекси для інгредієнтів та постачальників
CREATE INDEX інгредієнти_постачальник_idx ON інгредієнти(постачальник_ід);
CREATE INDEX інгредієнти_активний_idx ON інгредієнти(активний);
CREATE INDEX використання_інгредієнтів_страва_idx ON використання_інгредієнтів(страва_ід);
CREATE INDEX використання_інгредієнтів_інгредієнт_idx ON використання_інгредієнтів(інгредієнт_ід);
CREATE INDEX постачання_дата_idx ON постачання(дата_постачання);
CREATE INDEX постачання_постачальник_idx ON постачання(постачальник_ід);
CREATE INDEX постачання_інгредієнт_idx ON постачання(інгредієнт_ід);

-- =============================================
-- Створення тригерів і функцій
-- =============================================

-- Функція для оновлення загальної суми замовлення
CREATE OR REPLACE FUNCTION update_order_total() RETURNS TRIGGER AS $$
BEGIN
    -- Оновлення загальної суми замовлення
    UPDATE замовлення
    SET загальна_сума = (
        SELECT COALESCE(SUM(загальна_ціна), 0)
        FROM позиції_замовлення
        WHERE замовлення_ід = NEW.замовлення_ід
    ),
    фінальна_сума = (
        SELECT COALESCE(SUM(загальна_ціна), 0) - COALESCE(сума_знижки, 0)
        FROM позиції_замовлення
        WHERE замовлення_ід = NEW.замовлення_ід
    )
    WHERE ід = NEW.замовлення_ід;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Тригер для оновлення загальної суми замовлення при додаванні/зміні/видаленні позиції
CREATE TRIGGER update_order_total_trigger
AFTER INSERT OR UPDATE OR DELETE ON позиції_замовлення
FOR EACH ROW
EXECUTE FUNCTION update_order_total();

-- Функція для оновлення кількості інгредієнтів на складі при додаванні замовлення
CREATE OR REPLACE FUNCTION update_ingredient_quantity() RETURNS TRIGGER AS $$
BEGIN
    -- Якщо позиція замовлення переходить у стан "готується"
    IF NEW.стан = 'готується' AND (OLD.стан IS NULL OR OLD.стан = 'нове') THEN
        -- Зменшуємо кількість кожного інгредієнта на складі
        UPDATE інгредієнти i
        SET кількість_на_складі = кількість_на_складі - (vi.кількість * NEW.кількість)
        FROM використання_інгредієнтів vi
        WHERE vi.страва_ід = NEW.страва_ід AND vi.інгредієнт_ід = i.ід;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Тригер для оновлення кількості інгредієнтів на складі
CREATE TRIGGER update_ingredient_quantity_trigger
AFTER UPDATE ON позиції_замовлення
FOR EACH ROW
EXECUTE FUNCTION update_ingredient_quantity();

-- Функція для встановлення загальної ціни позиції замовлення
CREATE OR REPLACE FUNCTION set_order_item_total_price() RETURNS TRIGGER AS $$
BEGIN
    NEW.загальна_ціна = NEW.ціна_за_одиницю * NEW.кількість * (1 - COALESCE(NEW.знижка_відсоток, 0) / 100);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Тригер для встановлення загальної ціни позиції замовлення
CREATE TRIGGER set_order_item_total_price_trigger
BEFORE INSERT OR UPDATE ON позиції_замовлення
FOR EACH ROW
EXECUTE FUNCTION set_order_item_total_price(); 