-- Схема бази даних "Авіакомпанія"
CREATE SCHEMA IF NOT EXISTS авіакомпанія;

-- Видалення існуючих таблиць (якщо існують)
DROP TABLE IF EXISTS технічне_обслуговування CASCADE;
DROP TABLE IF EXISTS надані_послуги CASCADE;
DROP TABLE IF EXISTS рейси_персонал CASCADE;
DROP TABLE IF EXISTS бронювання_пасажири CASCADE;
DROP TABLE IF EXISTS бронювання CASCADE;
DROP TABLE IF EXISTS рейси CASCADE;
DROP TABLE IF EXISTS маршрути CASCADE;
DROP TABLE IF EXISTS пасажири CASCADE;
DROP TABLE IF EXISTS літаки CASCADE;
DROP TABLE IF EXISTS аеропорти CASCADE;
DROP TABLE IF EXISTS персонал CASCADE;
DROP TABLE IF EXISTS послуги CASCADE;
DROP TABLE IF EXISTS типи_літаків CASCADE;
DROP TABLE IF EXISTS статуси_рейсів CASCADE;
DROP TABLE IF EXISTS класи_обслуговування CASCADE;
DROP TABLE IF EXISTS посади CASCADE;
DROP TABLE IF EXISTS статуси_бронювань CASCADE;
DROP TABLE IF EXISTS статуси_техобслуговування CASCADE;
DROP TABLE IF EXISTS методи_оплати CASCADE;

-- Довідникові таблиці

-- Таблиця "Посади"
CREATE TABLE посади (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    базова_зарплата DECIMAL(10, 2) NOT NULL
);

-- Таблиця "Типи літаків"
CREATE TABLE типи_літаків (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    виробник VARCHAR(100) NOT NULL,
    максимальна_дальність_польоту INTEGER NOT NULL, -- у кілометрах
    максимальна_швидкість INTEGER NOT NULL, -- у км/год
    максимальна_висота_польоту INTEGER NOT NULL, -- у метрах
    максимальна_кількість_пасажирів INTEGER NOT NULL,
    максимальна_вантажопідйомність INTEGER NOT NULL -- у кілограмах
);

-- Таблиця "Статуси рейсів"
CREATE TABLE статуси_рейсів (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Таблиця "Класи обслуговування"
CREATE TABLE класи_обслуговування (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT,
    коефіцієнт_вартості DECIMAL(3, 2) NOT NULL
);

-- Таблиця "Статуси бронювань"
CREATE TABLE статуси_бронювань (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Таблиця "Статуси техобслуговування"
CREATE TABLE статуси_техобслуговування (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Таблиця "Методи оплати"
CREATE TABLE методи_оплати (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Основні таблиці

-- Таблиця "Персонал"
CREATE TABLE персонал (
    id SERIAL PRIMARY KEY,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE NOT NULL,
    стать CHAR(1) NOT NULL CHECK (стать IN ('Ч', 'Ж')),
    адреса TEXT,
    телефон VARCHAR(20),
    email VARCHAR(100),
    дата_прийому_на_роботу DATE NOT NULL,
    посада_id INTEGER NOT NULL REFERENCES посади(id),
    зарплата DECIMAL(10, 2) NOT NULL,
    статус VARCHAR(20) NOT NULL DEFAULT 'Активний' CHECK (статус IN ('Активний', 'У відпустці', 'На лікарняному', 'Звільнений')),
    примітки TEXT
);

-- Таблиця "Аеропорти"
CREATE TABLE аеропорти (
    id SERIAL PRIMARY KEY,
    код_іата CHAR(3) NOT NULL UNIQUE,
    код_ікао CHAR(4) NOT NULL UNIQUE,
    назва VARCHAR(200) NOT NULL,
    місто VARCHAR(100) NOT NULL,
    країна VARCHAR(100) NOT NULL,
    часовий_пояс VARCHAR(50) NOT NULL,
    кількість_терміналів INTEGER,
    кількість_злітно_посадкових_смуг INTEGER,
    географічні_координати VARCHAR(50),
    примітки TEXT
);

-- Таблиця "Літаки"
CREATE TABLE літаки (
    id SERIAL PRIMARY KEY,
    реєстраційний_номер VARCHAR(10) NOT NULL UNIQUE,
    серійний_номер VARCHAR(20) NOT NULL,
    тип_літака_id INTEGER NOT NULL REFERENCES типи_літаків(id),
    рік_випуску INTEGER NOT NULL,
    дата_останнього_капітального_ремонту DATE,
    дата_останнього_техогляду DATE,
    загальний_наліт_годин INTEGER NOT NULL DEFAULT 0,
    статус VARCHAR(20) NOT NULL DEFAULT 'Активний' CHECK (статус IN ('Активний', 'Техобслуговування', 'Ремонт', 'Утилізовано')),
    примітки TEXT
);

-- Таблиця "Маршрути"
CREATE TABLE маршрути (
    id SERIAL PRIMARY KEY,
    аеропорт_відправлення_id INTEGER NOT NULL REFERENCES аеропорти(id),
    аеропорт_призначення_id INTEGER NOT NULL REFERENCES аеропорти(id),
    відстань INTEGER NOT NULL, -- у кілометрах
    приблизний_час_польоту INTEGER NOT NULL, -- у хвилинах
    базова_вартість DECIMAL(10, 2) NOT NULL,
    CONSTRAINT різні_аеропорти CHECK (аеропорт_відправлення_id <> аеропорт_призначення_id)
);

-- Таблиця "Рейси"
CREATE TABLE рейси (
    id SERIAL PRIMARY KEY,
    номер_рейсу VARCHAR(10) NOT NULL,
    маршрут_id INTEGER NOT NULL REFERENCES маршрути(id),
    літак_id INTEGER NOT NULL REFERENCES літаки(id),
    дата_час_відправлення TIMESTAMP NOT NULL,
    дата_час_прибуття TIMESTAMP NOT NULL,
    фактичний_час_відправлення TIMESTAMP,
    фактичний_час_прибуття TIMESTAMP,
    статус_id INTEGER NOT NULL REFERENCES статуси_рейсів(id),
    кількість_місць_економ INTEGER NOT NULL,
    кількість_місць_бізнес INTEGER NOT NULL,
    кількість_місць_перший_клас INTEGER NOT NULL,
    доступно_місць_економ INTEGER NOT NULL,
    доступно_місць_бізнес INTEGER NOT NULL,
    доступно_місць_перший_клас INTEGER NOT NULL,
    вартість_економ DECIMAL(10, 2) NOT NULL,
    вартість_бізнес DECIMAL(10, 2) NOT NULL,
    вартість_перший_клас DECIMAL(10, 2) NOT NULL,
    погодні_умови TEXT,
    примітки TEXT,
    CONSTRAINT час_прибуття_пізніше_відправлення CHECK (дата_час_прибуття > дата_час_відправлення)
);

-- Таблиця "Пасажири"
CREATE TABLE пасажири (
    id SERIAL PRIMARY KEY,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE,
    стать CHAR(1) CHECK (стать IN ('Ч', 'Ж')),
    громадянство VARCHAR(50),
    номер_паспорта VARCHAR(20),
    серія_паспорта VARCHAR(10),
    телефон VARCHAR(20),
    email VARCHAR(100),
    адреса TEXT,
    примітки TEXT
);

-- Таблиця "Бронювання"
CREATE TABLE бронювання (
    id SERIAL PRIMARY KEY,
    номер_бронювання VARCHAR(20) NOT NULL UNIQUE,
    рейс_id INTEGER NOT NULL REFERENCES рейси(id),
    дата_бронювання TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    клас_обслуговування_id INTEGER NOT NULL REFERENCES класи_обслуговування(id),
    кількість_місць INTEGER NOT NULL,
    загальна_вартість DECIMAL(10, 2) NOT NULL,
    знижка_відсоток DECIMAL(5, 2) DEFAULT 0,
    статус_id INTEGER NOT NULL REFERENCES статуси_бронювань(id),
    метод_оплати_id INTEGER REFERENCES методи_оплати(id),
    примітки TEXT,
    CONSTRAINT позитивна_кількість_місць CHECK (кількість_місць > 0)
);

-- Таблиця "Бронювання_пасажири" (зв'язок між бронюваннями та пасажирами)
CREATE TABLE бронювання_пасажири (
    id SERIAL PRIMARY KEY,
    бронювання_id INTEGER NOT NULL REFERENCES бронювання(id),
    пасажир_id INTEGER NOT NULL REFERENCES пасажири(id),
    номер_місця VARCHAR(10),
    CONSTRAINT унікальне_місце_в_бронюванні UNIQUE (бронювання_id, номер_місця)
);

-- Таблиця "Рейси_персонал" (зв'язок між рейсами та персоналом)
CREATE TABLE рейси_персонал (
    id SERIAL PRIMARY KEY,
    рейс_id INTEGER NOT NULL REFERENCES рейси(id),
    персонал_id INTEGER NOT NULL REFERENCES персонал(id),
    роль VARCHAR(50),
    CONSTRAINT унікальний_персонал_на_рейсі UNIQUE (рейс_id, персонал_id)
);

-- Таблиця "Послуги"
CREATE TABLE послуги (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    вартість DECIMAL(10, 2) NOT NULL,
    доступність_в_класах VARCHAR(100) NOT NULL, -- наприклад: "економ, бізнес, перший клас"
    CONSTRAINT позитивна_вартість CHECK (вартість >= 0)
);

-- Таблиця "Надані послуги"
CREATE TABLE надані_послуги (
    id SERIAL PRIMARY KEY,
    бронювання_id INTEGER NOT NULL REFERENCES бронювання(id),
    послуга_id INTEGER NOT NULL REFERENCES послуги(id),
    кількість INTEGER NOT NULL DEFAULT 1,
    загальна_вартість DECIMAL(10, 2) NOT NULL,
    дата_надання TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT позитивна_кількість CHECK (кількість > 0),
    CONSTRAINT позитивна_загальна_вартість CHECK (загальна_вартість >= 0)
);

-- Таблиця "Технічне обслуговування"
CREATE TABLE технічне_обслуговування (
    id SERIAL PRIMARY KEY,
    літак_id INTEGER NOT NULL REFERENCES літаки(id),
    тип_обслуговування VARCHAR(100) NOT NULL,
    опис TEXT,
    дата_початку DATE NOT NULL,
    дата_завершення DATE,
    відповідальний_техніка_id INTEGER NOT NULL REFERENCES персонал(id),
    статус_id INTEGER NOT NULL REFERENCES статуси_техобслуговування(id),
    вартість DECIMAL(10, 2),
    примітки TEXT,
    CONSTRAINT позитивна_вартість_обслуговування CHECK (вартість >= 0)
);

-- Створення індексів для прискорення роботи з базою даних

-- Індекси для таблиці "Рейси"
CREATE INDEX idx_рейси_номер_рейсу ON рейси(номер_рейсу);
CREATE INDEX idx_рейси_дата_час_відправлення ON рейси(дата_час_відправлення);
CREATE INDEX idx_рейси_дата_час_прибуття ON рейси(дата_час_прибуття);
CREATE INDEX idx_рейси_статус_id ON рейси(статус_id);

-- Індекси для таблиці "Бронювання"
CREATE INDEX idx_бронювання_номер_бронювання ON бронювання(номер_бронювання);
CREATE INDEX idx_бронювання_рейс_id ON бронювання(рейс_id);
CREATE INDEX idx_бронювання_дата_бронювання ON бронювання(дата_бронювання);
CREATE INDEX idx_бронювання_статус_id ON бронювання(статус_id);

-- Індекси для таблиці "Пасажири"
CREATE INDEX idx_пасажири_прізвище_імя ON пасажири(прізвище, імя);
CREATE INDEX idx_пасажири_номер_паспорта ON пасажири(номер_паспорта);

-- Індекси для таблиці "Персонал"
CREATE INDEX idx_персонал_прізвище_імя ON персонал(прізвище, імя);
CREATE INDEX idx_персонал_посада_id ON персонал(посада_id);

-- Індекси для таблиці "Літаки"
CREATE INDEX idx_літаки_реєстраційний_номер ON літаки(реєстраційний_номер);
CREATE INDEX idx_літаки_тип_літака_id ON літаки(тип_літака_id);
CREATE INDEX idx_літаки_статус ON літаки(статус);

-- Індекси для таблиці "Аеропорти"
CREATE INDEX idx_аеропорти_код_іата ON аеропорти(код_іата);
CREATE INDEX idx_аеропорти_код_ікао ON аеропорти(код_ікао);
CREATE INDEX idx_аеропорти_місто_країна ON аеропорти(місто, країна);

-- Інші корисні індекси
CREATE INDEX idx_маршрути_аеропорти ON маршрути(аеропорт_відправлення_id, аеропорт_призначення_id);
CREATE INDEX idx_бронювання_пасажири_зв_язок ON бронювання_пасажири(бронювання_id, пасажир_id);
CREATE INDEX idx_рейси_персонал_зв_язок ON рейси_персонал(рейс_id, персонал_id);
CREATE INDEX idx_технічне_обслуговування_літак_статус ON технічне_обслуговування(літак_id, статус_id);
CREATE INDEX idx_надані_послуги_бронювання ON надані_послуги(бронювання_id); 