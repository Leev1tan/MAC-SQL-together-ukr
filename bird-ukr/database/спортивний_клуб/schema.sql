-- Схема бази даних "Спортивний клуб"
-- Призначення: Визначення структури таблиць та зв'язків між ними
-- Кодування: UTF-8

-- Створення бази даних (якщо виконується як окремий скрипт)
-- DROP DATABASE IF EXISTS спортивний_клуб;
-- CREATE DATABASE спортивний_клуб CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE спортивний_клуб;

-- Очищення таблиць, якщо вони існують
DROP TABLE IF EXISTS відвідування;
DROP TABLE IF EXISTS записи_на_заняття;
DROP TABLE IF EXISTS оцінки_тренерів;
DROP TABLE IF EXISTS платежі;
DROP TABLE IF EXISTS розклад_занять;
DROP TABLE IF EXISTS індивідуальні_бронювання;
DROP TABLE IF EXISTS члени_клубу;
DROP TABLE IF EXISTS членства;
DROP TABLE IF EXISTS типи_абонементів;
DROP TABLE IF EXISTS групові_заняття;
DROP TABLE IF EXISTS тренери;
DROP TABLE IF EXISTS спеціалізації_тренерів;
DROP TABLE IF EXISTS обладнання_приміщень;
DROP TABLE IF EXISTS приміщення;
DROP TABLE IF EXISTS типи_приміщень;
DROP TABLE IF EXISTS обладнання;
DROP TABLE IF EXISTS рівні_складності;
DROP TABLE IF EXISTS статуси_записів;
DROP TABLE IF EXISTS статуси_бронювання;
DROP TABLE IF EXISTS статуси_платежів;
DROP TABLE IF EXISTS статуси_членства;

-- Таблиці-довідники

-- Таблиця: статуси_членства
CREATE TABLE статуси_членства (
    id INT PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Таблиця: статуси_платежів
CREATE TABLE статуси_платежів (
    id INT PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Таблиця: статуси_бронювання
CREATE TABLE статуси_бронювання (
    id INT PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Таблиця: статуси_записів
CREATE TABLE статуси_записів (
    id INT PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Таблиця: рівні_складності
CREATE TABLE рівні_складності (
    id INT PRIMARY KEY,
    назва VARCHAR(50) NOT NULL,
    опис TEXT
);

-- Основні таблиці

-- Таблиця: обладнання
CREATE TABLE обладнання (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    дата_придбання DATE,
    вартість DECIMAL(10, 2),
    термін_експлуатації INT, -- У місяцях
    стан VARCHAR(50),
    дата_останнього_обслуговування DATE,
    виробник VARCHAR(100)
);

-- Таблиця: типи_приміщень
CREATE TABLE типи_приміщень (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT
);

-- Таблиця: приміщення
CREATE TABLE приміщення (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    тип_приміщення_id INT NOT NULL,
    площа DECIMAL(8, 2), -- У квадратних метрах
    максимальна_кількість_осіб INT,
    поверх INT,
    опис TEXT,
    стан VARCHAR(50),
    доступність BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (тип_приміщення_id) REFERENCES типи_приміщень(id)
);

-- Таблиця: обладнання_приміщень
CREATE TABLE обладнання_приміщень (
    id SERIAL PRIMARY KEY,
    приміщення_id INT NOT NULL,
    обладнання_id INT NOT NULL,
    кількість INT NOT NULL DEFAULT 1,
    дата_встановлення DATE,
    примітки TEXT,
    FOREIGN KEY (приміщення_id) REFERENCES приміщення(id) ON DELETE CASCADE,
    FOREIGN KEY (обладнання_id) REFERENCES обладнання(id) ON DELETE CASCADE
);

-- Таблиця: спеціалізації_тренерів
CREATE TABLE спеціалізації_тренерів (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT
);

-- Таблиця: тренери
CREATE TABLE тренери (
    id SERIAL PRIMARY KEY,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE,
    стать VARCHAR(20) CHECK (стать IN ('Чоловіча', 'Жіноча', 'Інше')),
    телефон VARCHAR(20),
    email VARCHAR(100),
    фото VARCHAR(255), -- Шлях до файлу фото
    освіта TEXT,
    спеціалізація_id INT,
    досвід_роботи INT, -- У роках
    дата_найму DATE NOT NULL,
    дата_звільнення DATE,
    ставка_за_годину DECIMAL(10, 2),
    біографія TEXT,
    активний BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (спеціалізація_id) REFERENCES спеціалізації_тренерів(id)
);

-- Таблиця: групові_заняття
CREATE TABLE групові_заняття (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    тривалість INT NOT NULL, -- У хвилинах
    рівень_складності_id INT,
    максимальна_кількість_учасників INT,
    калорії_витрата INT, -- Приблизна витрата калорій
    спеціалізація_id INT,
    FOREIGN KEY (рівень_складності_id) REFERENCES рівні_складності(id),
    FOREIGN KEY (спеціалізація_id) REFERENCES спеціалізації_тренерів(id)
);

-- Таблиця: типи_абонементів
CREATE TABLE типи_абонементів (
    id SERIAL PRIMARY KEY,
    назва VARCHAR(100) NOT NULL,
    опис TEXT,
    тривалість INT NOT NULL, -- У днях
    вартість DECIMAL(10, 2) NOT NULL,
    кількість_відвідувань INT, -- Null означає необмежену кількість
    час_відвідування VARCHAR(100), -- Наприклад: "08:00-22:00" або "Будь-який час"
    групові_заняття BOOLEAN DEFAULT FALSE, -- Чи включені групові заняття
    індивідуальні_тренування INT DEFAULT 0, -- Кількість включених індивідуальних тренувань
    сауна BOOLEAN DEFAULT FALSE,
    басейн BOOLEAN DEFAULT FALSE,
    знижка_відсоток INT DEFAULT 0,
    активний BOOLEAN DEFAULT TRUE
);

-- Таблиця: членства
CREATE TABLE членства (
    id SERIAL PRIMARY KEY,
    тип_абонементу_id INT NOT NULL,
    дата_початку DATE NOT NULL,
    дата_завершення DATE NOT NULL,
    статус_id INT NOT NULL,
    дата_заморозки DATE,
    дата_розморозки DATE,
    залишок_відвідувань INT,
    залишок_індивідуальних_тренувань INT,
    вартість_фактична DECIMAL(10, 2) NOT NULL, -- Фактична вартість з урахуванням знижок
    FOREIGN KEY (тип_абонементу_id) REFERENCES типи_абонементів(id),
    FOREIGN KEY (статус_id) REFERENCES статуси_членства(id)
);

-- Таблиця: члени_клубу
CREATE TABLE члени_клубу (
    id SERIAL PRIMARY KEY,
    прізвище VARCHAR(50) NOT NULL,
    імя VARCHAR(50) NOT NULL,
    по_батькові VARCHAR(50),
    дата_народження DATE,
    стать VARCHAR(20) CHECK (стать IN ('Чоловіча', 'Жіноча', 'Інше')),
    телефон VARCHAR(20),
    email VARCHAR(100),
    адреса TEXT,
    фото VARCHAR(255), -- Шлях до файлу фото
    примітки TEXT,
    медичні_обмеження TEXT,
    рівень_підготовки VARCHAR(50),
    мета_тренувань TEXT,
    дата_реєстрації DATE NOT NULL,
    членство_id INT,
    кількість_відвідувань INT DEFAULT 0,
    активний BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (членство_id) REFERENCES членства(id)
);

-- Таблиця: індивідуальні_бронювання
CREATE TABLE індивідуальні_бронювання (
    id SERIAL PRIMARY KEY,
    член_клубу_id INT NOT NULL,
    тренер_id INT NOT NULL,
    дата DATE NOT NULL,
    час_початку TIME NOT NULL,
    час_закінчення TIME NOT NULL,
    статус_id INT NOT NULL,
    приміщення_id INT,
    мета_тренування TEXT,
    результати TEXT,
    примітки TEXT,
    списано_з_абонементу BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (член_клубу_id) REFERENCES члени_клубу(id),
    FOREIGN KEY (тренер_id) REFERENCES тренери(id),
    FOREIGN KEY (статус_id) REFERENCES статуси_бронювання(id),
    FOREIGN KEY (приміщення_id) REFERENCES приміщення(id)
);

-- Таблиця: розклад_занять
CREATE TABLE розклад_занять (
    id SERIAL PRIMARY KEY,
    заняття_id INT NOT NULL,
    тренер_id INT NOT NULL,
    приміщення_id INT NOT NULL,
    день_тижня VARCHAR(20) CHECK (день_тижня IN ('Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пятниця', 'Субота', 'Неділя')) NOT NULL,
    час_початку TIME NOT NULL,
    час_закінчення TIME NOT NULL,
    повторюваність VARCHAR(50) DEFAULT 'Щотижня',
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    максимальна_кількість_учасників INT,
    примітки TEXT,
    активний BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (заняття_id) REFERENCES групові_заняття(id),
    FOREIGN KEY (тренер_id) REFERENCES тренери(id),
    FOREIGN KEY (приміщення_id) REFERENCES приміщення(id)
);

-- Таблиця: платежі
CREATE TABLE платежі (
    id SERIAL PRIMARY KEY,
    член_клубу_id INT NOT NULL,
    сума DECIMAL(10, 2) NOT NULL,
    дата_платежу TIMESTAMP NOT NULL,
    спосіб_оплати VARCHAR(50),
    призначення VARCHAR(255),
    членство_id INT,
    статус VARCHAR(50),
    номер_транзакції VARCHAR(100),
    примітки TEXT,
    FOREIGN KEY (член_клубу_id) REFERENCES члени_клубу(id),
    FOREIGN KEY (членство_id) REFERENCES членства(id)
);

-- Таблиця: оцінки_тренерів
CREATE TABLE оцінки_тренерів (
    id SERIAL PRIMARY KEY,
    тренер_id INT NOT NULL,
    член_клубу_id INT NOT NULL,
    оцінка INT NOT NULL, -- За шкалою від 1 до 5
    коментар TEXT,
    дата_оцінки TIMESTAMP NOT NULL,
    FOREIGN KEY (тренер_id) REFERENCES тренери(id),
    FOREIGN KEY (член_клубу_id) REFERENCES члени_клубу(id)
);

-- Таблиця: записи_на_заняття
CREATE TABLE записи_на_заняття (
    id SERIAL PRIMARY KEY,
    член_клубу_id INT NOT NULL,
    розклад_заняття_id INT NOT NULL,
    дата_запису TIMESTAMP NOT NULL,
    статус_id INT NOT NULL,
    примітки TEXT,
    FOREIGN KEY (член_клубу_id) REFERENCES члени_клубу(id),
    FOREIGN KEY (розклад_заняття_id) REFERENCES розклад_занять(id),
    FOREIGN KEY (статус_id) REFERENCES статуси_бронювання(id)
);

-- Таблиця: відвідування
CREATE TABLE відвідування (
    id SERIAL PRIMARY KEY,
    член_клубу_id INT NOT NULL,
    дата_відвідування DATE NOT NULL,
    час_приходу TIME NOT NULL,
    час_виходу TIME,
    запис_на_заняття_id INT,
    індивідуальне_бронювання_id INT,
    примітки TEXT,
    FOREIGN KEY (член_клубу_id) REFERENCES члени_клубу(id),
    FOREIGN KEY (запис_на_заняття_id) REFERENCES записи_на_заняття(id),
    FOREIGN KEY (індивідуальне_бронювання_id) REFERENCES індивідуальні_бронювання(id)
);

-- Створення індексів для оптимізації запитів
CREATE INDEX idx_члени_клубу_активний ON члени_клубу(активний);
CREATE INDEX idx_тренери_активний ON тренери(активний);
CREATE INDEX idx_тренери_спеціалізація ON тренери(спеціалізація_id);
CREATE INDEX idx_членства_статус ON членства(статус_id);
CREATE INDEX idx_членства_дати ON членства(дата_початку, дата_завершення);
CREATE INDEX idx_платежі_член_клубу ON платежі(член_клубу_id);
CREATE INDEX idx_платежі_дата ON платежі(дата_платежу);
CREATE INDEX idx_розклад_занять_дати ON розклад_занять(день_тижня, дата_початку, дата_закінчення);
CREATE INDEX idx_записи_на_заняття_статус ON записи_на_заняття(статус_id);
CREATE INDEX idx_відвідування_дата ON відвідування(дата_відвідування);
CREATE INDEX idx_бронювання_статус ON індивідуальні_бронювання(статус_id);
CREATE INDEX idx_бронювання_дата ON індивідуальні_бронювання(дата, час_початку); 