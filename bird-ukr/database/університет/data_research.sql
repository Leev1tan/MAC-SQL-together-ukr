-- Data for University Research (Наукові дослідження університету)
-- Created for Ukrainian Text-to-SQL dataset

-- ======================================
-- Create tables for university research
-- ======================================

-- Research projects (наукові_дослідження)
CREATE TABLE наукові_дослідження (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    опис TEXT,
    тип VARCHAR(100) NOT NULL, -- фундаментальне, прикладне, розробка, тощо
    статус VARCHAR(50) NOT NULL DEFAULT 'активне', -- активне, завершене, призупинене, планується
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    бюджет DECIMAL(12, 2),
    джерело_фінансування VARCHAR(100),
    кафедра_ід INTEGER REFERENCES кафедри(ід),
    керівник_ід INTEGER REFERENCES викладачі(ід),
    пріоритетність INTEGER DEFAULT 3, -- 1-найвища, 5-найнижча
    номер_держреєстрації VARCHAR(50),
    примітки TEXT,
    CONSTRAINT дати_дослідження_check CHECK (дата_початку <= дата_закінчення OR дата_закінчення IS NULL)
);

-- Publications (публікації)
CREATE TABLE публікації (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    тип VARCHAR(100) NOT NULL, -- стаття, монографія, тези, патент, тощо
    видання VARCHAR(200),
    рік INTEGER NOT NULL,
    том VARCHAR(50),
    номер VARCHAR(50),
    сторінки VARCHAR(50),
    doi VARCHAR(100),
    url VARCHAR(255),
    імпакт_фактор DECIMAL(5, 3),
    індексація VARCHAR(255), -- Scopus, Web of Science, тощо
    цитування_кількість INTEGER DEFAULT 0,
    дослідження_ід INTEGER REFERENCES наукові_дослідження(ід),
    примітки TEXT
);

-- Research grants (гранти)
CREATE TABLE гранти (
    ід SERIAL PRIMARY KEY,
    назва VARCHAR(255) NOT NULL,
    організація VARCHAR(200) NOT NULL, -- грантодавець
    тип VARCHAR(100) NOT NULL, -- науковий, освітній, інфраструктурний, тощо
    сума DECIMAL(12, 2) NOT NULL,
    валюта VARCHAR(10) DEFAULT 'UAH',
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    статус VARCHAR(50) NOT NULL DEFAULT 'активний', -- активний, завершений, відхилений, підготовка
    дослідження_ід INTEGER REFERENCES наукові_дослідження(ід),
    керівник_гранту_ід INTEGER REFERENCES викладачі(ід),
    опис TEXT,
    умови TEXT,
    примітки TEXT,
    CONSTRAINT дати_гранту_check CHECK (дата_початку <= дата_закінчення OR дата_закінчення IS NULL)
);

-- Researchers-Research relationships (дослідники_дослідження)
CREATE TABLE дослідники_дослідження (
    ід SERIAL PRIMARY KEY,
    дослідження_ід INTEGER NOT NULL REFERENCES наукові_дослідження(ід) ON DELETE CASCADE,
    викладач_ід INTEGER NOT NULL REFERENCES викладачі(ід) ON DELETE CASCADE,
    роль VARCHAR(100) NOT NULL, -- керівник, виконавець, консультант, тощо
    дата_початку DATE NOT NULL,
    дата_закінчення DATE,
    навантаження DECIMAL(5, 2), -- відсоток ставки або годин на тиждень
    примітки TEXT,
    UNIQUE (дослідження_ід, викладач_ід, роль),
    CONSTRAINT дати_участі_check CHECK (дата_початку <= дата_закінчення OR дата_закінчення IS NULL)
);

-- Publication authors (автори_публікацій)
CREATE TABLE автори_публікацій (
    ід SERIAL PRIMARY KEY,
    публікація_ід INTEGER NOT NULL REFERENCES публікації(ід) ON DELETE CASCADE,
    викладач_ід INTEGER REFERENCES викладачі(ід) ON DELETE CASCADE,
    зовнішній_автор_прізвище VARCHAR(100),
    зовнішній_автор_імя VARCHAR(100),
    зовнішній_автор_установа VARCHAR(200),
    порядок_авторів INTEGER NOT NULL,
    є_кореспондуючим BOOLEAN DEFAULT FALSE,
    примітки TEXT,
    CONSTRAINT автор_check CHECK (
        (викладач_ід IS NOT NULL AND зовнішній_автор_прізвище IS NULL AND зовнішній_автор_імя IS NULL) OR
        (викладач_ід IS NULL AND зовнішній_автор_прізвище IS NOT NULL AND зовнішній_автор_імя IS NOT NULL)
    )
);

-- Conference participations (участь_у_конференціях)
CREATE TABLE участь_у_конференціях (
    ід SERIAL PRIMARY KEY,
    викладач_ід INTEGER NOT NULL REFERENCES викладачі(ід),
    назва_конференції VARCHAR(255) NOT NULL,
    місце_проведення VARCHAR(255) NOT NULL,
    дата_початку DATE NOT NULL,
    дата_закінчення DATE NOT NULL,
    тип_участі VARCHAR(100) NOT NULL, -- доповідач, слухач, організатор, член комітету
    назва_доповіді VARCHAR(255),
    публікація_ід INTEGER REFERENCES публікації(ід),
    фінансування_ід INTEGER REFERENCES гранти(ід),
    примітки TEXT,
    CONSTRAINT дати_конференції_check CHECK (дата_початку <= дата_закінчення)
);

-- ======================================
-- Populate tables with sample data
-- ======================================

-- Insert research projects
INSERT INTO наукові_дослідження (назва, опис, тип, статус, дата_початку, дата_закінчення, бюджет, джерело_фінансування, кафедра_ід, керівник_ід, пріоритетність, номер_держреєстрації) VALUES
('Розробка квантових алгоритмів для вирішення NP-повних задач', 'Дослідження спрямоване на створення нових квантових алгоритмів для ефективного розв''язання NP-повних задач комбінаторної оптимізації', 'фундаментальне', 'активне', '2022-03-01', NULL, 1250000.00, 'Державний фонд фундаментальних досліджень', 5, 15, 1, 'ДР0122U007865'),
('Методи машинного навчання в аналізі великих даних медичної діагностики', 'Застосування методів глибокого навчання для аналізу медичних зображень та діагностики захворювань', 'прикладне', 'активне', '2021-09-01', '2023-08-31', 950000.00, 'МОН України', 3, 8, 2, 'ДР0121U004523'),
('Розробка енергоефективних алгоритмів для мобільних пристроїв', 'Створення оптимізованих алгоритмів для мінімізації споживання енергії у мобільних застосунках', 'розробка', 'активне', '2022-01-15', '2023-01-15', 750000.00, 'Корпоративне фінансування', 5, 23, 2, 'ДР0122U001234'),
('Дослідження нових методів синтезу наноматеріалів', 'Синтез та характеризація нових наноматеріалів з унікальними електронними та оптичними властивостями', 'фундаментальне', 'активне', '2021-05-01', '2024-04-30', 2000000.00, 'Національний фонд досліджень України', 7, 31, 1, 'ДР0121U008976'),
('Розробка українських корпусів текстів для NLP', 'Створення розмічених корпусів українських текстів для задач обробки природньої мови', 'прикладне', 'завершене', '2020-03-01', '2022-02-28', 600000.00, 'МОН України', 4, 18, 3, 'ДР0120U002345'),
('Архітектурні патерни програмування для розподілених систем', 'Дослідження та розробка нових архітектурних патернів для розподілених та мікросервісних систем', 'прикладне', 'планується', '2023-01-01', NULL, 850000.00, 'Грант ЄС', 5, 9, 2, NULL),
('Застосування штучного інтелекту в аграрному секторі', 'Розробка систем підтримки прийняття рішень на основі ШІ для оптимізації сільськогосподарського виробництва', 'розробка', 'активне', '2022-04-01', '2024-03-31', 1100000.00, 'Міністерство аграрної політики', 3, 22, 2, 'ДР0122U005678');

-- Insert publications
INSERT INTO публікації (назва, тип, видання, рік, том, номер, сторінки, doi, url, імпакт_фактор, індексація, цитування_кількість, дослідження_ід) VALUES
('Оптимізація квантових схем для задач факторизації великих чисел', 'стаття', 'Ukrainian Journal of Computer Science', 2022, '4', '3', '112-128', '10.1234/ujcs.2022.40312', 'https://ujcs.example.org/article12345', 1.423, 'Scopus, Web of Science', 5, 1),
('Порівняльний аналіз алгоритмів машинного навчання для класифікації медичних зображень', 'стаття', 'Medical Cybernetics', 2022, '8', '2', '45-63', '10.5678/mc.2022.8245', 'https://medcyber.example.org/article8245', 2.105, 'Scopus, Web of Science', 8, 2),
('Енергоефективна обробка зображень на мобільних пристроях', 'тези', 'Праці конференції "Комп''ютерні науки та інформаційні технології"', 2022, NULL, NULL, '156-158', NULL, 'https://csit.example.org/proc2022', NULL, 'НБУВ', 1, 3),
('Розробка когерентних наноструктур для оптоелектронних пристроїв', 'стаття', 'Journal of Materials Science', 2022, '43', '5', '2234-2245', '10.3456/jms.2022.435022', 'https://jms.example.org/v43/i5/22', 3.876, 'Scopus, Web of Science', 12, 4),
('Квантовий метод розв''язання задачі комівояжера', 'монографія', 'Наукова думка', 2022, NULL, NULL, '1-158', NULL, NULL, NULL, NULL, 3, 1),
('Корпус українських текстів для задач аналізу тональності', 'стаття', 'Computational Linguistics', 2021, '12', '4', '345-360', '10.9876/cl.2021.12434', 'https://complingv.example.org/12434', 1.987, 'Scopus', 10, 5),
('Мікросервісна архітектура для систем управління знаннями', 'патент', 'Державне патентне відомство України', 2022, NULL, 'UA123456', NULL, NULL, 'https://patent.example.ua/UA123456', NULL, NULL, 0, 6),
('Застосування глибоких нейронних мереж для прогнозування врожайності', 'стаття', 'Вісник аграрних наук', 2022, '25', '3', '78-94', '10.8765/van.2022.25378', 'https://van.example.org/2022/3/7', 0.754, 'Index Copernicus', 2, 7);

-- Insert grants
INSERT INTO гранти (назва, організація, тип, сума, валюта, дата_початку, дата_закінчення, статус, дослідження_ід, керівник_гранту_ід, опис, умови) VALUES
('Розвиток квантових обчислень в Україні', 'Національний фонд досліджень України', 'науковий', 2500000.00, 'UAH', '2022-03-01', '2025-02-28', 'активний', 1, 15, 'Грант на розвиток квантових обчислень та їх застосування у розв''язанні складних задач', 'Річні звіти, публікації у виданнях Q1/Q2, підготовка PhD студентів'),
('Інноваційні технології машинного навчання', 'Horizon Europe', 'науковий', 350000.00, 'EUR', '2021-09-01', '2024-08-31', 'активний', 2, 8, 'Міжнародний грант на розвиток інноваційних методів машинного навчання', 'Міжнародне співробітництво, спільні публікації, обмін студентами'),
('Оптимізація споживання енергії у мобільних застосунках', 'MobTech Inc.', 'корпоративний', 500000.00, 'UAH', '2022-01-15', '2023-01-15', 'активний', 3, 23, 'Корпоративний грант на розробку енергоефективних алгоритмів', 'Створення прототипу, патентування, комерціалізація'),
('Передові матеріали для оптоелектроніки', 'МОН України', 'науковий', 1800000.00, 'UAH', '2021-05-01', '2024-04-30', 'активний', 4, 31, 'Дослідження нових наноматеріалів та їх застосування в оптоелектроніці', 'Щоквартальні звіти, 5+ публікацій у виданнях Scopus/WoS'),
('NLP для української мови', 'Google AI Research', 'науковий', 100000.00, 'USD', '2020-03-01', '2022-02-28', 'завершений', 5, 18, 'Грант на розвиток ресурсів NLP для української мови', 'Відкритий доступ до результатів, публікація датасетів'),
('ШI в аграрному секторі України', 'Міністерство аграрної політики', 'прикладний', 1250000.00, 'UAH', '2022-04-01', '2024-03-31', 'активний', 7, 22, 'Впровадження ШІ технологій у сільське господарство України', 'Створення 3 прототипів систем, впровадження на 5+ підприємствах');

-- Insert researcher-research relationships
INSERT INTO дослідники_дослідження (дослідження_ід, викладач_ід, роль, дата_початку, дата_закінчення, навантаження) VALUES
(1, 15, 'керівник', '2022-03-01', NULL, 30.0),
(1, 16, 'виконавець', '2022-03-01', NULL, 50.0),
(1, 17, 'виконавець', '2022-03-01', NULL, 40.0),
(1, 20, 'консультант', '2022-03-01', '2022-09-30', 10.0),
(2, 8, 'керівник', '2021-09-01', NULL, 25.0),
(2, 11, 'виконавець', '2021-09-01', NULL, 40.0),
(2, 18, 'консультант', '2021-09-01', NULL, 15.0),
(3, 23, 'керівник', '2022-01-15', NULL, 20.0),
(3, 25, 'виконавець', '2022-01-15', NULL, 45.0),
(3, 27, 'виконавець', '2022-01-15', NULL, 30.0),
(4, 31, 'керівник', '2021-05-01', NULL, 35.0),
(4, 32, 'виконавець', '2021-05-01', NULL, 50.0),
(4, 33, 'виконавець', '2021-05-01', NULL, 40.0),
(5, 18, 'керівник', '2020-03-01', '2022-02-28', 25.0),
(5, 19, 'виконавець', '2020-03-01', '2022-02-28', 45.0),
(6, 9, 'керівник', '2023-01-01', NULL, 30.0),
(6, 10, 'виконавець', '2023-01-01', NULL, 40.0),
(7, 22, 'керівник', '2022-04-01', NULL, 30.0),
(7, 21, 'виконавець', '2022-04-01', NULL, 45.0),
(7, 8, 'консультант', '2022-04-01', NULL, 15.0);

-- Insert publication authors
INSERT INTO автори_публікацій (публікація_ід, викладач_ід, зовнішній_автор_прізвище, зовнішній_автор_імя, зовнішній_автор_установа, порядок_авторів, є_кореспондуючим) VALUES
(1, 15, NULL, NULL, NULL, 1, TRUE),
(1, 16, NULL, NULL, NULL, 2, FALSE),
(1, 17, NULL, NULL, NULL, 3, FALSE),
(1, NULL, 'Ковальчук', 'Олег', 'Інститут кібернетики НАН України', 4, FALSE),
(2, 8, NULL, NULL, NULL, 1, TRUE),
(2, 11, NULL, NULL, NULL, 2, FALSE),
(2, NULL, 'Петренко', 'Марія', 'Національний інститут раку', 3, FALSE),
(3, 23, NULL, NULL, NULL, 1, TRUE),
(3, 25, NULL, NULL, NULL, 2, FALSE),
(3, 27, NULL, NULL, NULL, 3, FALSE),
(4, 31, NULL, NULL, NULL, 1, TRUE),
(4, 32, NULL, NULL, NULL, 2, FALSE),
(4, 33, NULL, NULL, NULL, 3, FALSE),
(4, NULL, 'Шевченко', 'Ірина', 'Інститут фізики напівпровідників НАН України', 4, FALSE),
(5, 15, NULL, NULL, NULL, 1, TRUE),
(5, 16, NULL, NULL, NULL, 2, FALSE),
(5, 20, NULL, NULL, NULL, 3, FALSE),
(6, 18, NULL, NULL, NULL, 1, TRUE),
(6, 19, NULL, NULL, NULL, 2, FALSE),
(6, NULL, 'Мельник', 'Андрій', 'Львівська політехніка', 3, FALSE),
(7, 9, NULL, NULL, NULL, 1, TRUE),
(7, 10, NULL, NULL, NULL, 2, FALSE),
(8, 22, NULL, NULL, NULL, 1, TRUE),
(8, 21, NULL, NULL, NULL, 2, FALSE),
(8, 8, NULL, NULL, NULL, 3, FALSE);

-- Insert conference participations
INSERT INTO участь_у_конференціях (викладач_ід, назва_конференції, місце_проведення, дата_початку, дата_закінчення, тип_участі, назва_доповіді, публікація_ід, фінансування_ід) VALUES
(15, 'International Quantum Computing Conference', 'Цюрих, Швейцарія', '2022-06-15', '2022-06-18', 'доповідач', 'Quantum Approaches to NP-Complete Problems', 1, 1),
(16, 'International Quantum Computing Conference', 'Цюрих, Швейцарія', '2022-06-15', '2022-06-18', 'доповідач', 'Optimization of Quantum Circuits', NULL, 1),
(8, 'Medical AI Conference', 'Київ, Україна', '2022-04-20', '2022-04-22', 'доповідач', 'Machine Learning for Medical Image Analysis', 2, 2),
(11, 'Medical AI Conference', 'Київ, Україна', '2022-04-20', '2022-04-22', 'доповідач', 'Deep Learning in Healthcare', NULL, 2),
(23, 'Комп''ютерні науки та інформаційні технології', 'Львів, Україна', '2022-09-10', '2022-09-12', 'доповідач', 'Енергоефективна обробка зображень на мобільних пристроях', 3, 3),
(31, 'Materials Science and Engineering Conference', 'Варшава, Польща', '2022-05-25', '2022-05-28', 'доповідач', 'Novel Nanostructures for Optoelectronic Devices', 4, 4),
(18, 'NLP Conference', 'Барселона, Іспанія', '2021-10-05', '2021-10-08', 'доповідач', 'Sentiment Analysis Corpus for Ukrainian Language', 6, 5),
(19, 'NLP Conference', 'Барселона, Іспанія', '2021-10-05', '2021-10-08', 'слухач', NULL, NULL, 5),
(9, 'Software Architecture Summit', 'Берлін, Німеччина', '2022-11-15', '2022-11-17', 'доповідач', 'Microservice Patterns for Knowledge Management Systems', 7, NULL),
(22, 'Smart Agriculture Conference', 'Київ, Україна', '2022-10-10', '2022-10-12', 'доповідач', 'AI-based Crop Yield Prediction', 8, 6),
(21, 'Smart Agriculture Conference', 'Київ, Україна', '2022-10-10', '2022-10-12', 'слухач', NULL, NULL, 6); 