-- Data for Library Readers (читачі)
-- Created for Ukrainian Text-to-SQL dataset

-- Readers (читачі)
INSERT INTO читачі (номер_квитка, прізвище, імя, по_батькові, дата_народження, стать, категорія_ід, дата_реєстрації, термін_дії_до, адреса, телефон, електронна_пошта, місце_роботи, посада, освіта, статус, примітки)
VALUES 
    ('KB000001', 'Петренко', 'Олександр', 'Іванович', '1985-06-15', 'Ч', 1, '2020-01-10', '2025-01-09', 'м. Київ, вул. Хрещатик 10, кв. 15', '+380671234567', 'petrenko@gmail.com', 'ТОВ "Інфосистеми"', 'Програміст', 'Вища', 'активний', NULL),
    
    ('KB000002', 'Іваненко', 'Марія', 'Петрівна', '1990-03-20', 'Ж', 1, '2020-01-15', '2025-01-14', 'м. Київ, вул. Володимирська 25, кв. 32', '+380672345678', 'ivanenko@gmail.com', 'Видавництво "Основи"', 'Редактор', 'Вища', 'активний', NULL),
    
    ('KB000003', 'Коваленко', 'Андрій', 'Олегович', '1979-11-07', 'Ч', 1, '2020-02-05', '2025-02-04', 'м. Київ, вул. Саксаганського 45, кв. 18', '+380673456789', 'kovalenko@ukr.net', 'Київський університет імені Бориса Грінченка', 'Викладач', 'Вища', 'активний', NULL),
    
    ('KB000004', 'Мельник', 'Олена', 'Василівна', '1992-08-12', 'Ж', 2, '2020-02-20', '2025-02-19', 'м. Київ, проспект Науки 12, кв. 5', '+380674567890', 'melnyk@gmail.com', 'КНП "Центр первинної медичної допомоги"', 'Лікар', 'Вища', 'активний', NULL),
    
    ('KB000005', 'Шевченко', 'Ігор', 'Миколайович', '1987-04-28', 'Ч', 1, '2020-03-10', '2025-03-09', 'м. Київ, вул. Антоновича 15, кв. 8', '+380675678901', 'shevchenko@gmail.com', 'Національний банк України', 'Економіст', 'Вища', 'активний', NULL),
    
    ('KB000006', 'Бондаренко', 'Наталія', 'Олександрівна', '1983-09-30', 'Ж', 1, '2020-03-25', '2025-03-24', 'м. Київ, вул. Лесі Українки 25, кв. 12', '+380676789012', 'bondarenko@ukr.net', 'Київська міська адміністрація', 'Держслужбовець', 'Вища', 'активний', NULL),
    
    ('KB000007', 'Ткаченко', 'Василь', 'Петрович', '1975-12-05', 'Ч', 1, '2020-04-15', '2025-04-14', 'м. Київ, проспект Перемоги 22, кв. 35', '+380677890123', 'tkachenko@gmail.com', 'Інститут історії України', 'Науковий співробітник', 'Вища', 'активний', NULL),
    
    ('KB000008', 'Савченко', 'Тетяна', 'Вікторівна', '1995-02-15', 'Ж', 3, '2020-05-10', '2025-05-09', 'м. Київ, вул. Богдана Хмельницького 10, кв. 41', '+380678901234', 'savchenko@gmail.com', 'Київський національний університет імені Тараса Шевченка', 'Студент', 'Незакінчена вища', 'активний', NULL),
    
    ('KB000009', 'Кравченко', 'Микола', 'Ігорович', '1998-07-21', 'Ч', 3, '2020-05-25', '2025-05-24', 'м. Київ, вул. Ярославів Вал 20, кв. 15', '+380679012345', 'kravchenko@ukr.net', 'Національний університет "Києво-Могилянська академія"', 'Студент', 'Незакінчена вища', 'активний', NULL),
    
    ('KB000010', 'Лисенко', 'Вікторія', 'Андріївна', '1997-06-18', 'Ж', 3, '2020-06-10', '2025-06-09', 'м. Київ, вул. Велика Васильківська 45, кв. 27', '+380680123456', 'lysenko@gmail.com', 'Київський політехнічний інститут ім. Ігоря Сікорського', 'Студент', 'Незакінчена вища', 'активний', NULL),
    
    ('KB000011', 'Марченко', 'Сергій', 'Валерійович', '2010-03-27', 'Ч', 4, '2020-07-05', '2025-07-04', 'м. Київ, вул. Михайлівська 22, кв. 31', '+380681234567', NULL, 'Ліцей №100', 'Учень', 'Початкова', 'активний', 'Супроводжується матір''ю'),
    
    ('KB000012', 'Руденко', 'Софія', 'Олексіївна', '2009-05-15', 'Ж', 4, '2020-07-20', '2025-07-19', 'м. Київ, вул. Софіївська 15, кв. 19', '+380682345678', NULL, 'Гімназія №153', 'Учень', 'Початкова', 'активний', 'Супроводжується батьком'),
    
    ('KB000013', 'Павленко', 'Дмитро', 'Ігорович', '2008-11-30', 'Ч', 4, '2020-08-10', '2025-08-09', 'м. Київ, вул. Пушкінська 30, кв. 22', '+380683456789', NULL, 'Школа №135', 'Учень', 'Неповна середня', 'активний', NULL),
    
    ('KB000014', 'Гончаренко', 'Анастасія', 'Володимирівна', '2006-09-12', 'Ж', 4, '2020-08-25', '2025-08-24', 'м. Київ, вул. Драгомирова 14, кв. 7', '+380684567890', NULL, 'Гімназія №178', 'Учень', 'Неповна середня', 'активний', NULL),
    
    ('KB000015', 'Даниленко', 'Олег', 'Степанович', '1965-08-10', 'Ч', 5, '2020-09-05', '2025-09-04', 'м. Київ, вул. Грушевського 28, кв. 44', '+380685678901', 'danylenko@ukr.net', 'На пенсії', NULL, 'Вища', 'активний', NULL),
    
    ('KB000016', 'Захарчук', 'Людмила', 'Петрівна', '1962-04-25', 'Ж', 5, '2020-09-18', '2025-09-17', 'м. Київ, вул. Бульварно-Кудрявська 11, кв. 5', '+380686789012', 'zakharchuk@gmail.com', 'На пенсії', NULL, 'Вища', 'активний', NULL),
    
    ('KB000017', 'Тимошенко', 'Григорій', 'Іванович', '1968-11-15', 'Ч', 5, '2020-10-01', '2025-09-30', 'м. Київ, вул. Дегтярівська 20, кв. 33', '+380687890123', NULL, 'На пенсії', NULL, 'Середня спеціальна', 'активний', NULL),
    
    ('KB000018', 'Романюк', 'Зінаїда', 'Михайлівна', '1960-03-08', 'Ж', 5, '2020-10-15', '2025-10-14', 'м. Київ, вул. Щорса 18, кв. 29', '+380688901234', NULL, 'На пенсії', NULL, 'Середня спеціальна', 'активний', NULL),
    
    ('KB000019', 'Юрченко', 'Валентин', 'Олександрович', '1980-07-22', 'Ч', 6, '2020-11-05', '2025-11-04', 'м. Київ, вул. Предславинська 25, кв. 18', '+380689012345', 'yurchenko@gmail.com', 'Інститут літератури ім. Т.Г. Шевченка', 'Науковий співробітник', 'Вища', 'активний', 'Готує докторську дисертацію'),
    
    ('KB000020', 'Карпенко', 'Оксана', 'Валеріївна', '1982-09-14', 'Ж', 6, '2020-11-20', '2025-11-19', 'м. Київ, вул. Ревуцького 7, кв. 52', '+380690123456', 'karpenko@ukr.net', 'Інститут історії України', 'Науковий співробітник', 'Вища', 'активний', 'Досліджує міжнародні відносини XX століття'),
    
    ('KB000021', 'Романенко', 'Віктор', 'Михайлович', '1976-03-30', 'Ч', 6, '2020-12-05', '2025-12-04', 'м. Київ, вул. Оболонська 12, кв. 15', '+380691234567', 'romanenko@gmail.com', 'Київський університет імені Бориса Грінченка', 'Доцент', 'Вища', 'активний', 'Пише монографію про сучасну українську літературу'),
    
    ('KB000022', 'Мазур', 'Лариса', 'Олегівна', '1985-05-17', 'Ж', 6, '2020-12-20', '2025-12-19', 'м. Київ, проспект Маяковського 31, кв. 22', '+380692345678', 'mazur@gmail.com', 'Національний педагогічний університет імені М.П. Драгоманова', 'Доцент', 'Вища', 'активний', 'Досліджує методику викладання української мови'),
    
    ('KB000023', 'Федоренко', 'Михайло', 'Ігорович', '1983-02-14', 'Ч', 7, '2021-01-10', '2026-01-09', 'м. Київ, вул. Щербаківського 52, кв. 8', '+380693456789', 'fedorenko@gmail.com', 'Спілка письменників України', 'Письменник', 'Вища', 'активний', 'Автор трьох романів та збірки оповідань'),
    
    ('KB000024', 'Гнатюк', 'Ірина', 'Василівна', '1988-07-28', 'Ж', 7, '2021-01-25', '2026-01-24', 'м. Київ, вул. Ушинського 15, кв. 36', '+380694567890', 'hnatiuk@ukr.net', 'Журнал "Сучасність"', 'Редактор', 'Вища', 'активний', 'Поетеса, автор двох збірок'),
    
    ('KB000025', 'Соколов', 'Денис', 'Олексійович', '1978-09-19', 'Ч', 7, '2021-02-10', '2026-02-09', 'м. Київ, вул. Стеценка 8, кв. 14', '+380695678901', 'sokolov@gmail.com', 'Видавництво "Смолоскип"', 'Редактор', 'Вища', 'активний', 'Літературний критик, автор численних статей'); 