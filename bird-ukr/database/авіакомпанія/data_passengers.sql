-- Імпорт даних про пасажирів для бази даних "Авіакомпанія"

-- Вставка даних про пасажирів
INSERT INTO пасажири (
    прізвище, 
    імя, 
    по_батькові, 
    дата_народження, 
    стать, 
    громадянство, 
    номер_паспорта, 
    серія_паспорта, 
    телефон, 
    email, 
    адреса, 
    примітки
) VALUES
-- Українські пасажири
('Петренко', 'Олександр', 'Михайлович', '1985-07-15', 'Ч', 'Україна', '123456789', 'МС', '+380971234567', 'petrenko@example.com', 'м. Київ, вул. Хрещатик, 10, кв. 5', NULL),
('Коваленко', 'Ірина', 'Василівна', '1990-03-22', 'Ж', 'Україна', '234567890', 'МТ', '+380972345678', 'kovalenko@example.com', 'м. Львів, вул. Личаківська, 15, кв. 7', NULL),
('Шевченко', 'Микола', 'Петрович', '1978-11-10', 'Ч', 'Україна', '345678901', 'КМ', '+380973456789', 'shevchenko@example.com', 'м. Одеса, вул. Дерибасівська, 12, кв. 3', NULL),
('Бондаренко', 'Тетяна', 'Іванівна', '1995-05-30', 'Ж', 'Україна', '456789012', 'ТН', '+380974567890', 'bondarenko@example.com', 'м. Харків, вул. Сумська, 25, кв. 10', NULL),
('Ткаченко', 'Андрій', 'Олегович', '1982-09-18', 'Ч', 'Україна', '567890123', 'ВМ', '+380975678901', 'tkachenko@example.com', 'м. Дніпро, просп. Гагаріна, 30, кв. 15', NULL),
('Кравченко', 'Юлія', 'Сергіївна', '1988-04-05', 'Ж', 'Україна', '678901234', 'КС', '+380976789012', 'kravchenko@example.com', 'м. Запоріжжя, вул. Соборна, 18, кв. 22', NULL),
('Мельник', 'Віталій', 'Олександрович', '1975-12-25', 'Ч', 'Україна', '789012345', 'ММ', '+380977890123', 'melnyk@example.com', 'м. Вінниця, вул. Пирогова, 8, кв. 9', NULL),
('Романенко', 'Наталія', 'Дмитрівна', '1992-08-14', 'Ж', 'Україна', '890123456', 'РД', '+380978901234', 'romanenko@example.com', 'м. Полтава, вул. Європейська, 5, кв. 12', NULL),
('Лисенко', 'Олег', 'Анатолійович', '1980-02-28', 'Ч', 'Україна', '901234567', 'ЛА', '+380979012345', 'lysenko@example.com', 'м. Чернівці, вул. Кобилянської, 14, кв. 6', NULL),
('Савченко', 'Марина', 'Ігорівна', '1993-06-17', 'Ж', 'Україна', '012345678', 'СІ', '+380970123456', 'savchenko@example.com', 'м. Івано-Франківськ, вул. Незалежності, 20, кв. 8', NULL),

-- Пасажири з інших країн
('Сміт', 'Джон', NULL, '1982-04-12', 'Ч', 'США', 'US123456', NULL, '+1-555-123-4567', 'jsmith@example.com', '123 Main St, New York, NY, USA', NULL),
('Шмідт', 'Ганс', NULL, '1975-09-30', 'Ч', 'Німеччина', 'DE987654', NULL, '+49-30-12345678', 'hschmidt@example.com', 'Friedrichstraße 123, Berlin, Germany', NULL),
('Мартін', 'Софі', NULL, '1988-11-15', 'Ж', 'Франція', 'FR654321', NULL, '+33-1-23456789', 'smartin@example.com', '15 Rue de Rivoli, Paris, France', NULL),
('Новак', 'Анджей', NULL, '1979-07-20', 'Ч', 'Польща', 'PL456789', NULL, '+48-22-1234567', 'anowak@example.com', 'ul. Marszałkowska 45, Warsaw, Poland', 'Часто подорожує'),
('Йоргенсен', 'Карен', NULL, '1990-03-05', 'Ж', 'Данія', 'DK234567', NULL, '+45-33-123456', 'kjorgensen@example.com', 'Nyhavn 17, Copenhagen, Denmark', NULL),
('Танака', 'Хіроші', NULL, '1985-12-10', 'Ч', 'Японія', 'JP789012', NULL, '+81-3-12345678', 'htanaka@example.com', '1-1-1 Roppongi, Minato-ku, Tokyo, Japan', NULL),
('Гарсія', 'Мігель', NULL, '1980-05-22', 'Ч', 'Іспанія', 'ES345678', NULL, '+34-91-2345678', 'mgarcia@example.com', 'Calle Gran Vía 25, Madrid, Spain', NULL),
('Россі', 'Джулія', NULL, '1993-08-18', 'Ж', 'Італія', 'IT567890', NULL, '+39-06-12345678', 'grossi@example.com', 'Via del Corso 12, Rome, Italy', NULL),
('Чен', 'Лі', NULL, '1986-01-28', 'Ч', 'Китай', 'CN678901', NULL, '+86-10-12345678', 'lchen@example.com', '123 Wangfujing Street, Beijing, China', NULL),
('Сінгх', 'Раджеш', NULL, '1983-09-07', 'Ч', 'Індія', 'IN890123', NULL, '+91-11-12345678', 'rsingh@example.com', '45 Connaught Place, New Delhi, India', NULL),

-- Бізнес-мандрівники
('Ковальчук', 'Сергій', 'Вікторович', '1977-04-15', 'Ч', 'Україна', '123789456', 'КВ', '+380991234567', 'kovalchuk@corp.com', 'м. Київ, просп. Перемоги, 50, кв. 30', 'Часто літає бізнес-класом'),
('Іванова', 'Олена', 'Андріївна', '1984-08-22', 'Ж', 'Україна', '987456321', 'ІА', '+380992345678', 'ivanova@corp.com', 'м. Київ, вул. Велика Васильківська, 45, кв. 18', 'Постійний клієнт, член програми лояльності'),
('Поліщук', 'Дмитро', 'Сергійович', '1980-03-10', 'Ч', 'Україна', '654123789', 'ПС', '+380993456789', 'polishchuk@corp.com', 'м. Львів, вул. Федьковича, 20, кв. 5', 'Часто літає до Європи'),
('Броварчук', 'Анастасія', 'Олександрівна', '1986-11-30', 'Ж', 'Україна', '321789654', 'БО', '+380994567890', 'brovarchuk@corp.com', 'м. Одеса, вул. Катерининська, 10, кв. 7', 'Представник фармацевтичної компанії'),
('Білик', 'Максим', 'Григорович', '1978-12-05', 'Ч', 'Україна', '789123654', 'БГ', '+380995678901', 'bilyk@corp.com', 'м. Дніпро, вул. Глінки, 12, кв. 45', 'IT-консультант'),

-- Сім'ї з дітьми
('Данилюк', 'Василь', 'Іванович', '1982-06-20', 'Ч', 'Україна', '546789123', 'ДІ', '+380961234567', 'danyliuk@example.com', 'м. Київ, вул. Тростянецька, 12, кв. 57', 'Подорожує з родиною'),
('Данилюк', 'Ольга', 'Петрівна', '1984-09-15', 'Ж', 'Україна', '678123945', 'ДП', '+380962345678', 'danyliuk_o@example.com', 'м. Київ, вул. Тростянецька, 12, кв. 57', 'Подорожує з родиною'),
('Данилюк', 'Софія', 'Василівна', '2015-03-25', 'Ж', 'Україна', 'дитячий', 'ДВ', NULL, NULL, 'м. Київ, вул. Тростянецька, 12, кв. 57', 'Дитина 9 років'),
('Данилюк', 'Максим', 'Васильович', '2018-07-10', 'Ч', 'Україна', 'дитячий', 'ДВ', NULL, NULL, 'м. Київ, вул. Тростянецька, 12, кв. 57', 'Дитина 6 років'),

-- Пасажири з особливими потребами
('Гончарук', 'Валентина', 'Степанівна', '1955-02-10', 'Ж', 'Україна', '213456789', 'ГС', '+380981234567', 'honcharuk@example.com', 'м. Київ, вул. Бажана, 24, кв. 12', 'Потребує інвалідний візок'),
('Вербицький', 'Олексій', 'Павлович', '1990-11-12', 'Ч', 'Україна', '312456789', 'ВП', '+380982345678', 'verbytskyi@example.com', 'м. Львів, вул. Франка, 15, кв. 3', 'Слабозорий, потребує супроводу'),

-- Пасажири, що часто літають
('Корнієнко', 'Богдан', 'Тарасович', '1979-05-17', 'Ч', 'Україна', '413256789', 'КТ', '+380983456789', 'korniienko@example.com', 'м. Київ, вул. Антоновича, 50, кв. 14', 'Член програми лояльності Platinum'),
('Зінченко', 'Аліна', 'Романівна', '1988-10-30', 'Ж', 'Україна', '513246789', 'ЗР', '+380984567890', 'zinchenko@example.com', 'м. Київ, вул. Ломоносова, 33, кв. 25', 'Член програми лояльності Gold'),
('Войтенко', 'Роман', 'Євгенович', '1985-07-08', 'Ч', 'Україна', '612345789', 'ВЄ', '+380985678901', 'voitenko@example.com', 'м. Київ, вул. Солом''янська, 10, кв. 8', 'Член програми лояльності Silver'); 