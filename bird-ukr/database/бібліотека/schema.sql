-- Schema for Library (бібліотека) database
-- Created for Ukrainian Text-to-SQL dataset

-- Languages (мови)
CREATE TABLE мови (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL UNIQUE,
    код VARCHAR(10) NOT NULL UNIQUE,
    опис TEXT
);

-- Publishers (видавництва)
CREATE TABLE видавництва (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    місто VARCHAR(50),
    країна VARCHAR(50),
    рік_заснування INTEGER,
    веб_сайт VARCHAR(100),
    електронна_пошта VARCHAR(100),
    телефон VARCHAR(20)
);

-- Genres (жанри)
CREATE TABLE жанри (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL UNIQUE,
    опис TEXT,
    батьківський_жанр_ід INTEGER REFERENCES жанри(ід) ON DELETE SET NULL
);

-- Authors (автори)
CREATE TABLE автори (
    ід SERIAL PRIMARY KEY,
    імя VARCHAR(50) NOT NULL,
    прізвище VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE,
    країна VARCHAR(50),
    коротка_біографія TEXT,
    дата_смерті DATE,
    UNIQUE (імя, прізвище, по_батькові)
);

-- Reader categories (категорії_читачів)
CREATE TABLE категорії_читачів (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(50) NOT NULL UNIQUE,
    опис TEXT,
    макс_книг INTEGER,
    термін_днів INTEGER,
    вартість_обслуговування DECIMAL(10, 2),
    знижка_відсоток INTEGER
);

-- Positions (посади)
CREATE TABLE посади (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT,
    мінімальна_зарплата DECIMAL(10, 2),
    максимальна_зарплата DECIMAL(10, 2),
    вимоги TEXT
);

-- Books (книги)
CREATE TABLE книги (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(200) NOT NULL,
    видавництво_ід INTEGER REFERENCES видавництва(ід),
    рік_видання INTEGER,
    мова_ід INTEGER REFERENCES мови(ід),
    кількість_сторінок INTEGER,
    ISBN VARCHAR(20) UNIQUE,
    опис TEXT,
    рейтинг DECIMAL(3, 2),
    дата_додавання DATE DEFAULT CURRENT_DATE
);

-- Book-Author relationship (книга_автор)
CREATE TABLE книга_автор (
    ід SERIAL PRIMARY KEY,
    книга_ід INTEGER NOT NULL REFERENCES книги(ід) ON DELETE CASCADE,
    автор_ід INTEGER NOT NULL REFERENCES автори(ід) ON DELETE CASCADE,
    роль VARCHAR(50) DEFAULT 'автор',
    UNIQUE (книга_ід, автор_ід)
);

-- Book-Genre relationship (книга_жанр)
CREATE TABLE книга_жанр (
    ід SERIAL PRIMARY KEY,
    книга_ід INTEGER NOT NULL REFERENCES книги(ід) ON DELETE CASCADE,
    жанр_ід INTEGER NOT NULL REFERENCES жанри(ід) ON DELETE CASCADE,
    UNIQUE (книга_ід, жанр_ід)
);

-- Departments (відділи)
CREATE TABLE відділи (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL UNIQUE,
    опис TEXT,
    розташування VARCHAR(100),
    телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    часи_роботи VARCHAR(100),
    керівник_ід INTEGER REFERENCES працівники(ід) ON DELETE SET NULL
);

-- Employees (працівники)
CREATE TABLE працівники (
    ід SERIAL PRIMARY KEY,
    імя VARCHAR(50) NOT NULL,
    прізвище VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE,
    дата_прийняття DATE,
    дата_звільнення DATE,
    посада_ід INTEGER REFERENCES посади(ід),
    телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    адреса TEXT,
    освіта TEXT,
    зарплата DECIMAL(10, 2),
    активний BOOLEAN DEFAULT TRUE
);

-- Employee-Department relationship (працівник_відділ)
CREATE TABLE працівник_відділ (
    ід SERIAL PRIMARY KEY,
    працівник_ід INTEGER NOT NULL REFERENCES працівники(ід) ON DELETE CASCADE,
    відділ_ід INTEGER NOT NULL REFERENCES відділи(ід) ON DELETE CASCADE,
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    основний BOOLEAN DEFAULT TRUE,
    примітки TEXT,
    UNIQUE (працівник_ід, відділ_ід, дата_початку)
    
);

-- Readers (читачі)
CREATE TABLE читачі (
    ід SERIAL PRIMARY KEY,
    імя VARCHAR(50) NOT NULL,
    прізвище VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE,
    адреса TEXT,
    телефон VARCHAR(20),
    електронна_пошта VARCHAR(100),
    дата_реєстрації DATE DEFAULT CURRENT_DATE,
    дата_закінчення DATE,
    категорія_ід INTEGER REFERENCES категорії_читачів(ід),
    номер_квитка VARCHAR(20) UNIQUE,
    заблокований BOOLEAN DEFAULT FALSE,
    примітки TEXT
);

-- Book copies (примірники)
CREATE TABLE примірники (
    ід SERIAL PRIMARY KEY,
    книга_ід INTEGER NOT NULL REFERENCES книги(ід) ON DELETE CASCADE,
    інвентарний_номер VARCHAR(20) UNIQUE,
    місце_зберігання VARCHAR(100),
    стан VARCHAR(50),
    дата_придбання DATE,
    ціна DECIMAL(10, 2),
    доступний BOOLEAN DEFAULT TRUE,
    списаний BOOLEAN DEFAULT FALSE,
    дата_списання DATE,
    примітки TEXT
);

-- Loans (видачі)
CREATE TABLE видачі (
    ід SERIAL PRIMARY KEY,
    примірник_ід INTEGER NOT NULL REFERENCES примірники(ід),
    читач_ід INTEGER NOT NULL REFERENCES читачі(ід),
    працівник_видав_ід INTEGER NOT NULL REFERENCES працівники(ід),
    працівник_прийняв_ід INTEGER REFERENCES працівники(ід),
    дата_видачі DATE NOT NULL,
    очікувана_дата_повернення DATE NOT NULL,
    дата_повернення DATE,
    продовжено BOOLEAN DEFAULT FALSE,
    кількість_продовжень INTEGER DEFAULT 0,
    статус VARCHAR(50) DEFAULT 'видано', -- видано, повернуто, прострочено, втрачено
    примітки TEXT
);

-- Reservations (резервації)
CREATE TABLE резервації (
    ід SERIAL PRIMARY KEY,
    книга_ід INTEGER NOT NULL REFERENCES книги(ід),
    читач_ід INTEGER NOT NULL REFERENCES читачі(ід),
    дата_резервації DATE NOT NULL,
    очікувана_дата_наявності DATE,
    статус VARCHAR(50) DEFAULT 'очікує', -- очікує, виконано, скасовано
    дата_закінчення DATE,
    дата_виконання DATE,
    примітки TEXT
);

-- Fines (штрафи)
CREATE TABLE штрафи (
    ід SERIAL PRIMARY KEY,
    видача_ід INTEGER NOT NULL REFERENCES видачі(ід),
    сума DECIMAL(10, 2) NOT NULL,
    дата_нарахування DATE NOT NULL DEFAULT CURRENT_DATE,
    причина VARCHAR(100) NOT NULL,
    статус VARCHAR(50) DEFAULT 'не оплачено', -- не оплачено, оплачено, скасовано
    дата_оплати DATE,
    працівник_ід INTEGER REFERENCES працівники(ід),
    примітки TEXT
);

-- Events (події)
CREATE TABLE події (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(200) NOT NULL,
    опис TEXT,
    дата_початку TIMESTAMP NOT NULL,
    дата_закінчення TIMESTAMP,
    відділ_ід INTEGER REFERENCES відділи(ід),
    організатор_ід INTEGER REFERENCES працівники(ід),
    місце VARCHAR(100),
    максимальна_кількість_учасників INTEGER,
    цільова_аудиторія VARCHAR(100),
    реєстрація_необхідна BOOLEAN DEFAULT FALSE,
    статус VARCHAR(50) DEFAULT 'плановано', -- плановано, проведено, скасовано
    примітки TEXT
);

-- Event registrations (реєстрації_подій)
CREATE TABLE реєстрації_подій (
    ід SERIAL PRIMARY KEY,
    подія_ід INTEGER NOT NULL REFERENCES події(ід) ON DELETE CASCADE,
    читач_ід INTEGER NOT NULL REFERENCES читачі(ід) ON DELETE CASCADE,
    дата_реєстрації TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    статус VARCHAR(50) DEFAULT 'зареєстровано', -- зареєстровано, відвідано, не з'явився, скасовано
    примітки TEXT,
    UNIQUE (подія_ід, читач_ід)
);

-- Services (послуги)
CREATE TABLE послуги (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    вартість DECIMAL(10, 2),
    тривалість_хвилин INTEGER,
    доступна BOOLEAN DEFAULT TRUE
);

-- Service usage (використання_послуг)
CREATE TABLE використання_послуг (
    ід SERIAL PRIMARY KEY,
    послуга_ід INTEGER NOT NULL REFERENCES послуги(ід),
    читач_ід INTEGER NOT NULL REFERENCES читачі(ід),
    працівник_ід INTEGER REFERENCES працівники(ід),
    дата_використання TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    статус VARCHAR(50) DEFAULT 'надано', -- замовлено, надано, скасовано
    оплачено BOOLEAN DEFAULT FALSE,
    сума DECIMAL(10, 2),
    примітки TEXT
);

-- Statistics (статистика)
CREATE TABLE статистика (
    ід SERIAL PRIMARY KEY,
    дата DATE NOT NULL DEFAULT CURRENT_DATE,
    кількість_відвідувачів INTEGER DEFAULT 0,
    кількість_виданих_книг INTEGER DEFAULT 0,
    кількість_повернених_книг INTEGER DEFAULT 0,
    кількість_нових_читачів INTEGER DEFAULT 0,
    кількість_нових_книг INTEGER DEFAULT 0,
    кількість_проведених_подій INTEGER DEFAULT 0,
    примітки TEXT,
    UNIQUE (дата)
);

-- Create indexes for better performance
CREATE INDEX idx_книги_назва ON книги(назва);
CREATE INDEX idx_автори_прізвище ON автори(прізвище);
CREATE INDEX idx_читачі_прізвище ON читачі(прізвище);
CREATE INDEX idx_видачі_дата_видачі ON видачі(дата_видачі);
CREATE INDEX idx_видачі_статус ON видачі(статус);
CREATE INDEX idx_примірники_доступний ON примірники(доступний);
CREATE INDEX idx_книга_автор_книга_ід ON книга_автор(книга_ід);
CREATE INDEX idx_книга_автор_автор_ід ON книга_автор(автор_ід);
CREATE INDEX idx_книга_жанр_книга_ід ON книга_жанр(книга_ід);
CREATE INDEX idx_книга_жанр_жанр_ід ON книга_жанр(жанр_ід);

-- Create view for available books
CREATE VIEW доступні_книги AS
SELECT к.ід, к.назва, к.ISBN, COUNT(п.ід) AS кількість_доступних_примірників
FROM книги к
JOIN примірники п ON к.ід = п.книга_ід
WHERE п.доступний = TRUE AND п.списаний = FALSE
GROUP BY к.ід, к.назва, к.ISBN;

-- Create view for overdue loans
CREATE VIEW прострочені_видачі AS
SELECT в.ід, в.дата_видачі, в.очікувана_дата_повернення, 
       к.назва AS книга_назва, 
       CONCAT(ч.прізвище, ' ', ч.імя) AS читач_пів,
       ч.телефон AS читач_телефон,
       CURRENT_DATE - в.очікувана_дата_повернення AS днів_прострочення
FROM видачі в
JOIN примірники п ON в.примірник_ід = п.ід
JOIN книги к ON п.книга_ід = к.ід
JOIN читачі ч ON в.читач_ід = ч.ід
WHERE в.дата_повернення IS NULL 
AND в.очікувана_дата_повернення < CURRENT_DATE;

-- Create view for active readers
CREATE VIEW активні_читачі AS
SELECT ч.ід, ч.прізвище, ч.імя, ч.електронна_пошта, ч.телефон,
       COUNT(в.ід) AS кількість_видач,
       MAX(в.дата_видачі) AS остання_видача
FROM читачі ч
JOIN видачі в ON ч.ід = в.читач_ід
WHERE в.дата_видачі >= (CURRENT_DATE - INTERVAL '6 months')
GROUP BY ч.ід, ч.прізвище, ч.імя, ч.електронна_пошта, ч.телефон
HAVING COUNT(в.ід) >= 3;

-- Create view for popular books
CREATE VIEW популярні_книги AS
SELECT к.ід, к.назва, COUNT(в.ід) AS кількість_видач
FROM книги к
JOIN примірники п ON к.ід = п.книга_ід
JOIN видачі в ON п.ід = в.примірник_ід
WHERE в.дата_видачі >= (CURRENT_DATE - INTERVAL '6 months')
GROUP BY к.ід, к.назва
ORDER BY кількість_видач DESC; 