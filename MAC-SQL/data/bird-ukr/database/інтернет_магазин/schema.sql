-- Схема бази даних "Інтернет-магазин"
-- Кодування: UTF-8

-- ==================================
-- Видалення існуючих таблиць (якщо вони існують)
-- ==================================

DROP TABLE IF EXISTS відгуки CASCADE;
DROP TABLE IF EXISTS позиції_замовлення CASCADE;
DROP TABLE IF EXISTS замовлення CASCADE;
DROP TABLE IF EXISTS кошики_товари CASCADE;
DROP TABLE IF EXISTS кошики CASCADE;
DROP TABLE IF EXISTS платежі CASCADE;
DROP TABLE IF EXISTS доставки CASCADE;
DROP TABLE IF EXISTS знижки CASCADE;
DROP TABLE IF EXISTS товари CASCADE;
DROP TABLE IF EXISTS категорії CASCADE;
DROP TABLE IF EXISTS клієнти CASCADE;
DROP TABLE IF EXISTS адреси CASCADE;
DROP TABLE IF EXISTS статуси_замовлень CASCADE;
DROP TABLE IF EXISTS методи_оплати CASCADE;
DROP TABLE IF EXISTS методи_доставки CASCADE;

-- ==================================
-- Створення довідникових таблиць
-- ==================================

CREATE TABLE статуси_замовлень (
    код VARCHAR(20) PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT
);

CREATE TABLE методи_оплати (
    код VARCHAR(20) PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    активний BOOLEAN DEFAULT TRUE
);

CREATE TABLE методи_доставки (
    код VARCHAR(20) PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    вартість DECIMAL(10,2) NOT NULL,
    термін_доставки_днів INT,
    активний BOOLEAN DEFAULT TRUE
);

-- ==================================
-- Створення основних таблиць
-- ==================================

CREATE TABLE категорії (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    батьківська_категорія_ід INT REFERENCES категорії(ід) ON DELETE SET NULL,
    зображення_url VARCHAR(255),
    порядок_сортування INT DEFAULT 0,
    активна BOOLEAN DEFAULT TRUE,
    дата_створення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_оновлення TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE товари (
    ід SERIAL PRIMARY KEY,
    артикул VARCHAR(50) UNIQUE NOT NULL,
    назва VARCHAR(255) NOT NULL,
    опис TEXT,
    ціна DECIMAL(10, 2) NOT NULL,
    стара_ціна DECIMAL(10, 2),
    кількість_на_складі INT NOT NULL DEFAULT 0,
    категорія_ід INT REFERENCES категорії(ід) ON DELETE SET NULL,
    бренд VARCHAR(100),
    вага DECIMAL(10, 3), -- вага в кг
    розміри VARCHAR(50), -- формат: ширина x висота x глибина
    колір VARCHAR(50),
    матеріал VARCHAR(100),
    особливості TEXT,
    зображення_url VARCHAR(255),
    додаткові_зображення TEXT[], -- масив URL-адрес додаткових зображень
    рейтинг DECIMAL(3, 2) DEFAULT 0,
    кількість_відгуків INT DEFAULT 0,
    популярність INT DEFAULT 0, -- кількість переглядів
    активний BOOLEAN DEFAULT TRUE,
    новинка BOOLEAN DEFAULT FALSE,
    хіт_продажу BOOLEAN DEFAULT FALSE,
    на_розпродажі BOOLEAN DEFAULT FALSE,
    дата_створення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_оновлення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_price CHECK (ціна >= 0),
    CONSTRAINT valid_stock CHECK (кількість_на_складі >= 0),
    CONSTRAINT valid_rating CHECK (рейтинг >= 0 AND рейтинг <= 5)
);

CREATE TABLE клієнти (
    ід SERIAL PRIMARY KEY,
    емейл VARCHAR(100) UNIQUE NOT NULL,
    пароль_хеш VARCHAR(255) NOT NULL,
    прізвище VARCHAR(100),
    імя VARCHAR(100),
    по_батькові VARCHAR(100),
    телефон VARCHAR(20),
    дата_народження DATE,
    стать CHAR(1) CHECK (стать IN ('Ч', 'Ж')),
    дата_реєстрації TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    останній_вхід TIMESTAMP,
    активований BOOLEAN DEFAULT FALSE,
    токен_активації VARCHAR(100),
    токен_відновлення_паролю VARCHAR(100),
    термін_дії_токену TIMESTAMP,
    бонусні_бали INT DEFAULT 0,
    рівень_лояльності VARCHAR(20) DEFAULT 'Стандарт',
    примітки TEXT
);

CREATE TABLE адреси (
    ід SERIAL PRIMARY KEY,
    клієнт_ід INT REFERENCES клієнти(ід) ON DELETE CASCADE,
    назва VARCHAR(100), -- наприклад "Домашня", "Робоча"
    країна VARCHAR(100) DEFAULT 'Україна',
    область VARCHAR(100),
    місто VARCHAR(100) NOT NULL,
    поштовий_індекс VARCHAR(10),
    вулиця VARCHAR(255) NOT NULL,
    будинок VARCHAR(20) NOT NULL,
    квартира VARCHAR(20),
    за_замовчуванням BOOLEAN DEFAULT FALSE,
    контактна_особа VARCHAR(200),
    контактний_телефон VARCHAR(20),
    примітки TEXT,
    дата_створення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_оновлення TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE кошики (
    ід SERIAL PRIMARY KEY,
    клієнт_ід INT REFERENCES клієнти(ід) ON DELETE SET NULL,
    сесія_ід VARCHAR(100),
    дата_створення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_оновлення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT require_client_or_session CHECK (
        (клієнт_ід IS NOT NULL) OR (сесія_ід IS NOT NULL)
    )
);

CREATE TABLE кошики_товари (
    ід SERIAL PRIMARY KEY,
    кошик_ід INT REFERENCES кошики(ід) ON DELETE CASCADE,
    товар_ід INT REFERENCES товари(ід) ON DELETE CASCADE,
    кількість INT NOT NULL DEFAULT 1,
    дата_додавання TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_cart_product UNIQUE (кошик_ід, товар_ід),
    CONSTRAINT valid_quantity CHECK (кількість > 0)
);

CREATE TABLE знижки (
    ід SERIAL PRIMARY KEY,
    код VARCHAR(50) UNIQUE,
    тип VARCHAR(20) NOT NULL CHECK (тип IN ('відсоткова', 'фіксована', 'безкоштовна_доставка')),
    значення DECIMAL(10, 2),
    мінімальна_сума_замовлення DECIMAL(10, 2),
    максимальна_сума_знижки DECIMAL(10, 2),
    категорія_ід INT REFERENCES категорії(ід) ON DELETE SET NULL,
    товар_ід INT REFERENCES товари(ід) ON DELETE SET NULL,
    опис TEXT,
    активна BOOLEAN DEFAULT TRUE,
    одноразова BOOLEAN DEFAULT FALSE,
    дата_початку TIMESTAMP NOT NULL,
    дата_завершення TIMESTAMP,
    обмеження_використань INT,
    поточні_використання INT DEFAULT 0,
    
    CONSTRAINT dates_order CHECK (дата_початку <= дата_завершення)
);

CREATE TABLE замовлення (
    ід SERIAL PRIMARY KEY,
    номер VARCHAR(20) UNIQUE NOT NULL,
    клієнт_ід INT REFERENCES клієнти(ід) ON DELETE SET NULL,
    адреса_доставки_ід INT REFERENCES адреси(ід) ON DELETE SET NULL,
    загальна_сума DECIMAL(10, 2) NOT NULL,
    сума_знижки DECIMAL(10, 2) DEFAULT 0,
    вартість_доставки DECIMAL(10, 2) DEFAULT 0,
    кількість_товарів INT NOT NULL,
    статус VARCHAR(20) REFERENCES статуси_замовлень(код) ON DELETE RESTRICT,
    знижка_ід INT REFERENCES знижки(ід) ON DELETE SET NULL,
    примітки TEXT,
    метод_доставки VARCHAR(20) REFERENCES методи_доставки(код) ON DELETE RESTRICT,
    дата_замовлення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_підтвердження TIMESTAMP,
    бажана_дата_доставки DATE,
    дата_відправлення TIMESTAMP,
    дата_доставки TIMESTAMP,
    
    CONSTRAINT valid_order_amount CHECK (загальна_сума >= 0),
    CONSTRAINT valid_discount_amount CHECK (сума_знижки >= 0),
    CONSTRAINT valid_shipping_cost CHECK (вартість_доставки >= 0),
    CONSTRAINT valid_product_count CHECK (кількість_товарів > 0)
);

CREATE TABLE позиції_замовлення (
    ід SERIAL PRIMARY KEY,
    замовлення_ід INT REFERENCES замовлення(ід) ON DELETE CASCADE,
    товар_ід INT REFERENCES товари(ід) ON DELETE SET NULL,
    назва_товару VARCHAR(255) NOT NULL, -- збереження назви на момент замовлення
    артикул VARCHAR(50) NOT NULL, -- збереження артикулу на момент замовлення
    ціна_за_одиницю DECIMAL(10, 2) NOT NULL,
    кількість INT NOT NULL,
    сума DECIMAL(10, 2) NOT NULL,
    сума_знижки DECIMAL(10, 2) DEFAULT 0,
    
    CONSTRAINT unique_order_product UNIQUE (замовлення_ід, товар_ід),
    CONSTRAINT valid_item_price CHECK (ціна_за_одиницю >= 0),
    CONSTRAINT valid_item_quantity CHECK (кількість > 0),
    CONSTRAINT valid_item_total CHECK (сума >= 0),
    CONSTRAINT valid_item_discount CHECK (сума_знижки >= 0)
);

CREATE TABLE платежі (
    ід SERIAL PRIMARY KEY,
    замовлення_ід INT REFERENCES замовлення(ід) ON DELETE CASCADE,
    метод VARCHAR(20) REFERENCES методи_оплати(код) ON DELETE RESTRICT,
    сума DECIMAL(10, 2) NOT NULL,
    статус VARCHAR(20) NOT NULL CHECK (
        статус IN ('очікується', 'оброблюється', 'успішний', 'відхилений', 'повернення')
    ),
    транзакція_ід VARCHAR(100),
    дата_платежу TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_підтвердження TIMESTAMP,
    примітки TEXT,
    
    CONSTRAINT valid_payment_amount CHECK (сума > 0)
);

CREATE TABLE доставки (
    ід SERIAL PRIMARY KEY,
    замовлення_ід INT REFERENCES замовлення(ід) ON DELETE CASCADE,
    метод VARCHAR(20) REFERENCES методи_доставки(код) ON DELETE RESTRICT,
    відстеження_номер VARCHAR(100),
    статус VARCHAR(20) NOT NULL CHECK (
        статус IN ('очікується', 'підготовлено', 'відправлено', 'в_дорозі', 'доставлено', 'повернення')
    ),
    імя_отримувача VARCHAR(200),
    телефон_отримувача VARCHAR(20),
    вага DECIMAL(10, 2),
    вартість DECIMAL(10, 2) NOT NULL,
    дата_створення TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_відправлення TIMESTAMP,
    орієнтовна_дата_доставки DATE,
    фактична_дата_доставки TIMESTAMP,
    особливі_вказівки TEXT,
    
    CONSTRAINT valid_shipping_cost CHECK (вартість >= 0)
);

CREATE TABLE відгуки (
    ід SERIAL PRIMARY KEY,
    товар_ід INT REFERENCES товари(ід) ON DELETE CASCADE,
    клієнт_ід INT REFERENCES клієнти(ід) ON DELETE SET NULL,
    замовлення_ід INT REFERENCES замовлення(ід) ON DELETE SET NULL,
    рейтинг INT NOT NULL CHECK (рейтинг BETWEEN 1 AND 5),
    заголовок VARCHAR(255),
    текст TEXT,
    переваги TEXT,
    недоліки TEXT,
    відповідь_адміністратора TEXT,
    дата_відгуку TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    дата_відповіді TIMESTAMP,
    модерований BOOLEAN DEFAULT FALSE,
    опубліковано BOOLEAN DEFAULT FALSE,
    корисно_голосів INT DEFAULT 0,
    неправдивий_голосів INT DEFAULT 0,
    
    CONSTRAINT unique_customer_review UNIQUE (товар_ід, клієнт_ід, замовлення_ід)
);

-- ==================================
-- Створення індексів
-- ==================================

CREATE INDEX idx_товари_категорія ON товари(категорія_ід);
CREATE INDEX idx_товари_назва ON товари(назва);
CREATE INDEX idx_товари_ціна ON товари(ціна);
CREATE INDEX idx_товари_активний ON товари(активний);
CREATE INDEX idx_товари_на_складі ON товари(кількість_на_складі) WHERE кількість_на_складі > 0;
CREATE INDEX idx_товари_популярність ON товари(популярність DESC);
CREATE INDEX idx_товари_рейтинг ON товари(рейтинг DESC);

CREATE INDEX idx_клієнти_емейл ON клієнти(емейл);
CREATE INDEX idx_клієнти_прізвище ON клієнти(прізвище, імя);
CREATE INDEX idx_клієнти_телефон ON клієнти(телефон);
CREATE INDEX idx_клієнти_дата_реєстрації ON клієнти(дата_реєстрації DESC);

CREATE INDEX idx_адреси_клієнт ON адреси(клієнт_ід);
CREATE INDEX idx_адреси_місто ON адреси(місто);

CREATE INDEX idx_кошики_клієнт ON кошики(клієнт_ід);
CREATE INDEX idx_кошики_сесія ON кошики(сесія_ід);

CREATE INDEX idx_знижки_код ON знижки(код);
CREATE INDEX idx_знижки_активна ON знижки(активна, дата_початку, дата_завершення);

CREATE INDEX idx_замовлення_клієнт ON замовлення(клієнт_ід);
CREATE INDEX idx_замовлення_статус ON замовлення(статус);
CREATE INDEX idx_замовлення_дата ON замовлення(дата_замовлення DESC);
CREATE INDEX idx_замовлення_номер ON замовлення(номер);

CREATE INDEX idx_позиції_замовлення ON позиції_замовлення(замовлення_ід);
CREATE INDEX idx_позиції_товар ON позиції_замовлення(товар_ід);

CREATE INDEX idx_платежі_замовлення ON платежі(замовлення_ід);
CREATE INDEX idx_платежі_статус ON платежі(статус);
CREATE INDEX idx_платежі_дата ON платежі(дата_платежу DESC);

CREATE INDEX idx_доставки_замовлення ON доставки(замовлення_ід);
CREATE INDEX idx_доставки_статус ON доставки(статус);
CREATE INDEX idx_доставки_номер ON доставки(відстеження_номер);

CREATE INDEX idx_відгуки_товар ON відгуки(товар_ід);
CREATE INDEX idx_відгуки_клієнт ON відгуки(клієнт_ід);
CREATE INDEX idx_відгуки_рейтинг ON відгуки(рейтинг DESC);
CREATE INDEX idx_відгуки_дата ON відгуки(дата_відгуку DESC);
CREATE INDEX idx_відгуки_опубліковано ON відгуки(опубліковано) WHERE опубліковано = TRUE;

-- ==================================
-- Функції та тригери
-- ==================================

-- Функція для оновлення рейтингу та кількості відгуків товару
CREATE OR REPLACE FUNCTION оновити_рейтинг_товару()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.опубліковано = TRUE THEN
        UPDATE товари
        SET рейтинг = (
                SELECT COALESCE(AVG(рейтинг), 0)
                FROM відгуки
                WHERE товар_ід = NEW.товар_ід
                AND опубліковано = TRUE
            ),
            кількість_відгуків = (
                SELECT COUNT(*)
                FROM відгуки
                WHERE товар_ід = NEW.товар_ід
                AND опубліковано = TRUE
            )
        WHERE ід = NEW.товар_ід;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.опубліковано <> NEW.опубліковано OR OLD.рейтинг <> NEW.рейтинг THEN
            UPDATE товари
            SET рейтинг = (
                    SELECT COALESCE(AVG(рейтинг), 0)
                    FROM відгуки
                    WHERE товар_ід = NEW.товар_ід
                    AND опубліковано = TRUE
                ),
                кількість_відгуків = (
                    SELECT COUNT(*)
                    FROM відгуки
                    WHERE товар_ід = NEW.товар_ід
                    AND опубліковано = TRUE
                )
            WHERE ід = NEW.товар_ід;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE товари
        SET рейтинг = (
                SELECT COALESCE(AVG(рейтинг), 0)
                FROM відгуки
                WHERE товар_ід = OLD.товар_ід
                AND опубліковано = TRUE
            ),
            кількість_відгуків = (
                SELECT COUNT(*)
                FROM відгуки
                WHERE товар_ід = OLD.товар_ід
                AND опубліковано = TRUE
            )
        WHERE ід = OLD.товар_ід;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER тригер_оновлення_рейтингу_товару
AFTER INSERT OR UPDATE OR DELETE ON відгуки
FOR EACH ROW EXECUTE FUNCTION оновити_рейтинг_товару();

-- Функція для оновлення дати в батьківських сутностях
CREATE OR REPLACE FUNCTION оновити_дату_оновлення()
RETURNS TRIGGER AS $$
BEGIN
    NEW.дата_оновлення = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER тригер_оновлення_дати_товари
BEFORE UPDATE ON товари
FOR EACH ROW EXECUTE FUNCTION оновити_дату_оновлення();

CREATE TRIGGER тригер_оновлення_дати_категорії
BEFORE UPDATE ON категорії
FOR EACH ROW EXECUTE FUNCTION оновити_дату_оновлення();

CREATE TRIGGER тригер_оновлення_дати_адреси
BEFORE UPDATE ON адреси
FOR EACH ROW EXECUTE FUNCTION оновити_дату_оновлення();

CREATE TRIGGER тригер_оновлення_дати_кошики
BEFORE UPDATE ON кошики
FOR EACH ROW EXECUTE FUNCTION оновити_дату_оновлення(); 