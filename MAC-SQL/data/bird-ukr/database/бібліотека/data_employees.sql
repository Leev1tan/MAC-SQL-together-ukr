-- Data for Library Employees (працівники)
-- Created for Ukrainian Text-to-SQL dataset

-- Employees (працівники)
INSERT INTO працівники (прізвище, імя, по_батькові, дата_народження, дата_прийняття, посада_ід, зарплата, адреса, телефон, електронна_пошта, освіта, активний)
VALUES 
    -- Адміністрація
    ('Петренко', 'Олена', 'Василівна', '1975-09-20', '2015-03-10', 1, 32000.00, 'м. Київ, вул. Хрещатик 15, кв. 45', '+380671234001', 'petrenko@library.ua', 'Київський національний університет культури і мистецтв, бібліотекознавство', TRUE),
    
    ('Коваленко', 'Ігор', 'Петрович', '1980-05-15', '2016-07-01', 2, 28000.00, 'м. Київ, вул. Володимирська 28, кв. 12', '+380671234002', 'kovalenko@library.ua', 'Національний університет "Києво-Могилянська академія", філологія', TRUE),
    
    ('Мельник', 'Тетяна', 'Олександрівна', '1978-11-30', '2017-02-15', 3, 26000.00, 'м. Київ, вул. Саксаганського 57, кв. 89', '+380671234003', 'melnyk@library.ua', 'Київський національний університет імені Тараса Шевченка, економіка', TRUE),
    
    -- Відділ обслуговування
    ('Іванчук', 'Марія', 'Степанівна', '1985-04-22', '2018-05-10', 4, 22000.00, 'м. Київ, проспект Перемоги 44, кв. 56', '+380671234004', 'ivanchuk@library.ua', 'Київський університет імені Бориса Грінченка, бібліотечна справа', TRUE),
    
    ('Ковальчук', 'Наталія', 'Ігорівна', '1990-08-14', '2019-03-01', 5, 18000.00, 'м. Київ, вул. Антоновича 15, кв. 23', '+380671234005', 'kovalchuk@library.ua', 'Київський національний університет культури і мистецтв, бібліотекознавство', TRUE),
    
    ('Шевченко', 'Олександр', 'Миколайович', '1987-06-25', '2019-04-15', 5, 18000.00, 'м. Київ, вул. Пушкінська 33, кв. 78', '+380671234006', 'shevchenko@library.ua', 'Київський університет імені Бориса Грінченка, історія', TRUE),
    
    -- Відділ художньої літератури
    ('Данилюк', 'Світлана', 'Віталіївна', '1982-03-18', '2017-08-01', 4, 23000.00, 'м. Київ, вул. Льва Толстого 9, кв. 45', '+380671234007', 'danyliuk@library.ua', 'Львівський національний університет імені Івана Франка, філологія', TRUE),
    
    ('Лисенко', 'Андрій', 'Валерійович', '1992-01-10', '2020-02-03', 5, 17500.00, 'м. Київ, вул. Велика Васильківська 102, кв. 17', '+380671234008', 'lysenko@library.ua', 'Київський національний університет імені Тараса Шевченка, філологія', TRUE),
    
    -- Відділ наукової та технічної літератури
    ('Бондаренко', 'Василь', 'Андрійович', '1976-09-28', '2016-11-15', 4, 23500.00, 'м. Київ, вул. Симона Петлюри 15, кв. 89', '+380671234009', 'bondarenko@library.ua', 'Національний технічний університет України "КПІ", інформаційні технології', TRUE),
    
    ('Ткаченко', 'Людмила', 'Олексіївна', '1988-12-05', '2018-07-20', 5, 18500.00, 'м. Київ, вул. Богдана Хмельницького 35, кв. 12', '+380671234010', 'tkachenko@library.ua', 'Національний університет "Києво-Могилянська академія", біологія', TRUE),
    
    -- Дитячий відділ
    ('Пономаренко', 'Оксана', 'Іванівна', '1983-05-15', '2017-05-10', 4, 22500.00, 'м. Київ, вул. Ярославів Вал 28, кв. 45', '+380671234011', 'ponomarenko@library.ua', 'Київський університет імені Бориса Грінченка, дошкільна освіта', TRUE),
    
    ('Романюк', 'Ірина', 'Павлівна', '1991-11-18', '2019-08-01', 5, 18000.00, 'м. Київ, вул. Оболонська 35, кв. 28', '+380671234012', 'romaniuk@library.ua', 'Національний педагогічний університет імені М.П. Драгоманова, дошкільна освіта', TRUE),
    
    -- Відділ іноземної літератури
    ('Савченко', 'Віктор', 'Григорович', '1979-07-23', '2017-03-15', 4, 24000.00, 'м. Київ, проспект Науки 15, кв. 56', '+380671234013', 'savchenko@library.ua', 'Київський національний лінгвістичний університет, переклад', TRUE),
    
    ('Білоус', 'Катерина', 'Дмитрівна', '1993-03-30', '2020-01-15', 5, 17800.00, 'м. Київ, вул. Лук''янівська 58, кв. 113', '+380671234014', 'bilous@library.ua', 'Київський національний лінгвістичний університет, германська філологія', TRUE),
    
    -- Відділ електронних ресурсів
    ('Кравчук', 'Максим', 'Олегович', '1985-02-12', '2018-01-20', 6, 26000.00, 'м. Київ, вул. Академіка Янгеля 7, кв. 33', '+380671234015', 'kravchuk@library.ua', 'Національний технічний університет України "КПІ", комп''ютерні науки', TRUE),
    
    ('Гончарук', 'Денис', 'Сергійович', '1990-09-05', '2019-05-15', 7, 22000.00, 'м. Київ, вул. Миколи Гринченка 4, кв. 78', '+380671234016', 'honcharuk@library.ua', 'Національний технічний університет України "КПІ", інформаційні технології', TRUE),
    
    -- Відділ періодики
    ('Дмитренко', 'Олег', 'Вікторович', '1980-11-07', '2017-06-01', 4, 22000.00, 'м. Київ, вул. Щекавицька 41, кв. 15', '+380671234017', 'dmytrenko@library.ua', 'Київський національний університет імені Тараса Шевченка, журналістика', TRUE),
    
    ('Захарчук', 'Анна', 'Романівна', '1994-04-28', '2021-02-01', 5, 17500.00, 'м. Київ, вул. Антоновича 47, кв. 89', '+380671234018', 'zakharchuk@library.ua', 'Київський національний університет імені Тараса Шевченка, соціальні комунікації', TRUE),
    
    -- Відділ каталогізації та комплектування
    ('Руденко', 'Юлія', 'Анатоліївна', '1981-08-15', '2017-04-15', 8, 24000.00, 'м. Київ, вул. Предславинська 38, кв. 25', '+380671234019', 'rudenko@library.ua', 'Київський національний університет культури і мистецтв, бібліотекознавство', TRUE),
    
    ('Яковенко', 'Тарас', 'Іванович', '1986-07-19', '2018-03-01', 9, 20000.00, 'м. Київ, вул. Тургенєвська 12, кв. 45', '+380671234020', 'yakovenko@library.ua', 'Київський національний університет культури і мистецтв, інформаційна справа', TRUE),
    
    -- Відділ рідкісних та цінних видань
    ('Кузьменко', 'Михайло', 'Андрійович', '1975-12-10', '2016-09-15', 10, 25000.00, 'м. Київ, вул. Січових Стрільців 52, кв. 17', '+380671234021', 'kuzmenko@library.ua', 'Київський національний університет імені Тараса Шевченка, історія', TRUE),
    
    ('Клименко', 'Дарія', 'Михайлівна', '1989-05-27', '2019-11-01', 11, 19000.00, 'м. Київ, вул. Рейтарська 20, кв. 33', '+380671234022', 'klymenko@library.ua', 'Львівський національний університет імені Івана Франка, музеєзнавство', TRUE),
    
    -- Допоміжний персонал
    ('Марченко', 'Сергій', 'Петрович', '1977-06-15', '2016-05-15', 12, 15000.00, 'м. Київ, вул. Феодосійська 5, кв. 112', '+380671234023', 'marchenko@library.ua', 'Київський коледж зв''язку', TRUE),
    
    ('Василенко', 'Валентина', 'Степанівна', '1968-09-12', '2015-07-01', 12, 12000.00, 'м. Київ, вул. Новопирогівська 25, кв. 45', '+380671234024', 'vasylenko@library.ua', 'Середня спеціальна', TRUE); 