-- Імпорт даних про персонал для бази даних "Авіакомпанія"

INSERT INTO персонал (прізвище, імя, по_батькові, дата_народження, стать, адреса, телефон, email, дата_прийому_на_роботу, посада_id, зарплата, статус) VALUES
-- Пілоти (капітани)
('Петренко', 'Олександр', 'Іванович', '1975-04-15', 'Ч', 'м. Київ, вул. Хрещатик, 10, кв. 25', '+380501234567', 'petrenko@airline.ua', '2010-03-10', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 85000.00, 'Активний'),
('Ковальчук', 'Василь', 'Петрович', '1978-06-22', 'Ч', 'м. Київ, вул. Володимирська, 15, кв. 42', '+380502345678', 'kovalchuk@airline.ua', '2011-05-18', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 82000.00, 'Активний'),
('Сидоренко', 'Ігор', 'Михайлович', '1980-08-10', 'Ч', 'м. Київ, вул. Саксаганського, 25, кв. 15', '+380503456789', 'sydorenko@airline.ua', '2012-07-25', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 81000.00, 'Активний'),
('Мельник', 'Андрій', 'Володимирович', '1982-09-05', 'Ч', 'м. Київ, вул. Льва Толстого, 8, кв. 30', '+380504567890', 'melnyk@airline.ua', '2013-04-12', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 80000.00, 'Активний'),
('Кравченко', 'Тарас', 'Олегович', '1979-11-20', 'Ч', 'м. Київ, вул. Богдана Хмельницького, 12, кв. 18', '+380505678901', 'kravchenko@airline.ua', '2011-11-15', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 83000.00, 'Активний'),
('Андрійчук', 'Оксана', 'Віталіївна', '1983-07-12', 'Ж', 'м. Київ, вул. Антоновича, 22, кв. 7', '+380506789012', 'andriichuk@airline.ua', '2014-06-20', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 79000.00, 'Активний'),
('Павленко', 'Сергій', 'Ігорович', '1977-12-08', 'Ч', 'м. Київ, вул. Ярославів Вал, 30, кв. 12', '+380507890123', 'pavlenko@airline.ua', '2010-09-22', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 84000.00, 'Активний'),
('Савченко', 'Дмитро', 'Олександрович', '1981-02-17', 'Ч', 'м. Київ, вул. Михайлівська, 16, кв. 35', '+380508901234', 'savchenko@airline.ua', '2013-08-15', (SELECT id FROM посади WHERE назва = 'Капітан' LIMIT 1), 81500.00, 'Активний'),

-- Пілоти (другі пілоти)
('Іваненко', 'Максим', 'Вікторович', '1985-03-25', 'Ч', 'м. Київ, вул. Велика Васильківська, 45, кв. 21', '+380509012345', 'ivanenko@airline.ua', '2015-05-10', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 60000.00, 'Активний'),
('Коваленко', 'Роман', 'Андрійович', '1987-01-14', 'Ч', 'м. Київ, вул. Златоустівська, 27, кв. 8', '+380510123456', 'kovalenko@airline.ua', '2016-03-18', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 59000.00, 'Активний'),
('Федоренко', 'Юрій', 'Степанович', '1986-05-30', 'Ч', 'м. Київ, вул. Тарасівська, 19, кв. 42', '+380511234567', 'fedorenko@airline.ua', '2015-11-20', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 59500.00, 'Активний'),
('Ткаченко', 'Віталій', 'Ігорович', '1988-09-12', 'Ч', 'м. Київ, вул. Пушкінська, 31, кв. 15', '+380512345678', 'tkachenko@airline.ua', '2017-01-30', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 58000.00, 'Активний'),
('Семенко', 'Олег', 'Дмитрович', '1986-11-05', 'Ч', 'м. Київ, вул. Жилянська, 25, кв. 10', '+380513456789', 'semenko@airline.ua', '2016-08-15', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 58500.00, 'Активний'),
('Бондаренко', 'Ірина', 'Михайлівна', '1988-04-18', 'Ж', 'м. Київ, вул. Лютеранська, 14, кв. 28', '+380514567890', 'bondarenko@airline.ua', '2017-05-22', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 57500.00, 'Активний'),
('Давиденко', 'Євген', 'Олександрович', '1985-08-27', 'Ч', 'м. Київ, вул. Еспланадна, 20, кв. 5', '+380515678901', 'davydenko@airline.ua', '2015-07-14', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 60500.00, 'Активний'),
('Марченко', 'Наталія', 'Вікторівна', '1987-06-09', 'Ж', 'м. Київ, вул. Інститутська, 18, кв. 32', '+380516789012', 'marchenko@airline.ua', '2016-10-11', (SELECT id FROM посади WHERE назва = 'Другий пілот' LIMIT 1), 59000.00, 'Активний'),

-- Бортпровідники (старші)
('Попова', 'Марія', 'Олександрівна', '1988-07-15', 'Ж', 'м. Київ, вул. Січових Стрільців, 22, кв. 17', '+380517890123', 'popova@airline.ua', '2016-04-20', (SELECT id FROM посади WHERE назва = 'Старший бортпровідник' LIMIT 1), 42000.00, 'Активний'),
('Соколов', 'Андрій', 'Миколайович', '1990-02-28', 'Ч', 'м. Київ, вул. Гончара, 15, кв. 9', '+380518901234', 'sokolov@airline.ua', '2017-06-15', (SELECT id FROM посади WHERE назва = 'Старший бортпровідник' LIMIT 1), 41500.00, 'Активний'),
('Бойко', 'Тетяна', 'Сергіївна', '1989-10-12', 'Ж', 'м. Київ, вул. Верхній Вал, 28, кв. 23', '+380519012345', 'boyko@airline.ua', '2017-03-10', (SELECT id FROM посади WHERE назва = 'Старший бортпровідник' LIMIT 1), 41800.00, 'Активний'),
('Руденко', 'Олексій', 'Ігорович', '1991-05-20', 'Ч', 'м. Київ, вул. Нижній Вал, 17, кв. 11', '+380520123456', 'rudenko@airline.ua', '2018-02-25', (SELECT id FROM посади WHERE назва = 'Старший бортпровідник' LIMIT 1), 41000.00, 'Активний'),
('Захарченко', 'Вікторія', 'Павлівна', '1990-09-08', 'Ж', 'м. Київ, вул. Андріївський узвіз, 10, кв. 14', '+380521234567', 'zakharchenko@airline.ua', '2017-09-18', (SELECT id FROM посади WHERE назва = 'Старший бортпровідник' LIMIT 1), 41200.00, 'Активний'),

-- Бортпровідники (звичайні)
('Шевченко', 'Ольга', 'Василівна', '1992-03-10', 'Ж', 'м. Київ, вул. Костьольна, 8, кв. 29', '+380522345678', 'shevchenko@airline.ua', '2018-05-20', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 32000.00, 'Активний'),
('Гончар', 'Діана', 'Олексіївна', '1993-06-15', 'Ж', 'м. Київ, вул. Рейтарська, 12, кв. 7', '+380523456789', 'honchar@airline.ua', '2019-01-15', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 31500.00, 'Активний'),
('Кузьменко', 'Валентина', 'Ігорівна', '1994-08-22', 'Ж', 'м. Київ, вул. Софіївська, 18, кв. 3', '+380524567890', 'kuzmenko@airline.ua', '2019-07-10', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 31000.00, 'Активний'),
('Литвиненко', 'Юлія', 'Віталіївна', '1995-01-28', 'Ж', 'м. Київ, вул. Хорива, 22, кв. 19', '+380525678901', 'lytvynenko@airline.ua', '2020-02-15', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 30500.00, 'Активний'),
('Дмитренко', 'Василь', 'Петрович', '1991-11-05', 'Ч', 'м. Київ, вул. Волоська, 15, кв. 25', '+380526789012', 'dmytrenko@airline.ua', '2018-08-20', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 32500.00, 'Активний'),
('Василенко', 'Микола', 'Андрійович', '1992-09-17', 'Ч', 'м. Київ, вул. Іллінська, 10, кв. 31', '+380527890123', 'vasylenko@airline.ua', '2018-11-12', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 32200.00, 'Активний'),
('Яковенко', 'Марина', 'Олегівна', '1993-12-30', 'Ж', 'м. Київ, вул. Набережно-Хрещатицька, 7, кв. 14', '+380528901234', 'yakovenko@airline.ua', '2019-03-25', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 31200.00, 'Активний'),
('Романенко', 'Світлана', 'Сергіївна', '1994-05-14', 'Ж', 'м. Київ, вул. Прорізна, 12, кв. 8', '+380529012345', 'romanenko@airline.ua', '2019-10-18', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 30800.00, 'Активний'),
('Тимошенко', 'Андрій', 'Юрійович', '1995-07-25', 'Ч', 'м. Київ, вул. Грінченка, 5, кв. 22', '+380530123456', 'tymoshenko@airline.ua', '2020-05-10', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 30000.00, 'Активний'),
('Дорошенко', 'Катерина', 'Іванівна', '1996-03-18', 'Ж', 'м. Київ, вул. Б. Грінченка, 9, кв. 16', '+380531234567', 'doroshenko@airline.ua', '2020-09-22', (SELECT id FROM посади WHERE назва = 'Бортпровідник' LIMIT 1), 29500.00, 'Активний'),

-- Авіатехніки (старші)
('Захаров', 'Сергій', 'Михайлович', '1980-04-12', 'Ч', 'м. Київ, вул. Деревлянська, 25, кв. 30', '+380532345678', 'zakharov@airline.ua', '2012-08-15', (SELECT id FROM посади WHERE назва = 'Старший авіатехнік' LIMIT 1), 58000.00, 'Активний'),
('Михайлов', 'Віктор', 'Олексійович', '1982-09-25', 'Ч', 'м. Київ, вул. Білоруська, 18, кв. 7', '+380533456789', 'mykhailov@airline.ua', '2013-06-20', (SELECT id FROM посади WHERE назва = 'Старший авіатехнік' LIMIT 1), 57500.00, 'Активний'),
('Григоренко', 'Іван', 'Петрович', '1981-06-30', 'Ч', 'м. Київ, вул. Глибочицька, 12, кв. 15', '+380534567890', 'hryhorenko@airline.ua', '2013-02-10', (SELECT id FROM посади WHERE назва = 'Старший авіатехнік' LIMIT 1), 57800.00, 'Активний'),

-- Авіатехніки (звичайні)
('Левченко', 'Олександр', 'Валентинович', '1985-08-15', 'Ч', 'м. Київ, вул. Овруцька, 10, кв. 18', '+380535678901', 'levchenko@airline.ua', '2015-04-22', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 47000.00, 'Активний'),
('Пономаренко', 'Віталій', 'Ігорович', '1987-11-20', 'Ч', 'м. Київ, вул. Кудрявська, 15, кв. 23', '+380536789012', 'ponomarenko@airline.ua', '2016-07-15', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 46500.00, 'Активний'),
('Кириленко', 'Михайло', 'Сергійович', '1986-03-08', 'Ч', 'м. Київ, вул. Татарська, 8, кв. 11', '+380537890123', 'kyrylenko@airline.ua', '2016-02-28', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 46800.00, 'Активний'),
('Степаненко', 'Антон', 'Олександрович', '1988-05-17', 'Ч', 'м. Київ, вул. Обсерваторна, 20, кв. 9', '+380538901234', 'stepanenko@airline.ua', '2017-09-10', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 46000.00, 'Активний'),
('Карпенко', 'Богдан', 'Андрійович', '1989-07-22', 'Ч', 'м. Київ, вул. Пирогова, 12, кв. 27', '+380539012345', 'karpenko@airline.ua', '2018-03-15', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 45500.00, 'Активний'),
-- Додано відсутнього техніка Василя Мельника
('Мельник', 'Василь', 'Олегович', '1988-01-10', 'Ч', 'м. Київ, вул. Басейна, 5, кв. 40', '+380539998877', 'v.melnyk@airline.ua', '2017-01-18', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 46200.00, 'Активний'),
-- Додано відсутніх техніків
('Коваль', 'Сергій', 'Андрійович', '1989-03-12', 'Ч', 'м. Київ, вул. Рейтарська, 20, кв. 5', '+380531112233', 's.koval@airline.ua', '2017-05-10', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 46300.00, 'Активний'),
('Бондаренко', 'Олег', 'Вікторович', '1990-07-25', 'Ч', 'м. Київ, вул. Гончара, 30, кв. 15', '+380534445566', 'o.bondarenko@airline.ua', '2018-01-20', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 45800.00, 'Активний'),
('Іванов', 'Петро', 'Миколайович', '1987-12-01', 'Ч', 'м. Київ, вул. Стрілецька, 14, кв. 22', '+380537778899', 'p.ivanov@airline.ua', '2016-11-05', (SELECT id FROM посади WHERE назва = 'Авіатехнік' LIMIT 1), 46700.00, 'Активний'),

-- Диспетчери
('Макаренко', 'Станіслав', 'Вікторович', '1985-04-15', 'Ч', 'м. Київ, вул. Шота Руставелі, 22, кв. 14', '+380540123456', 'makarenko@airline.ua', '2015-02-10', (SELECT id FROM посади WHERE назва = 'Диспетчер' LIMIT 1), 52000.00, 'Активний'),
('Гаврилюк', 'Тетяна', 'Олегівна', '1987-08-28', 'Ж', 'м. Київ, вул. Льва Толстого, 15, кв. 32', '+380541234567', 'gavryliuk@airline.ua', '2016-05-20', (SELECT id FROM посади WHERE назва = 'Диспетчер' LIMIT 1), 51500.00, 'Активний'),
('Назаренко', 'Олег', 'Ігорович', '1986-11-12', 'Ч', 'м. Київ, вул. Володимирська, 10, кв. 19', '+380542345678', 'nazarenko@airline.ua', '2016-03-15', (SELECT id FROM посади WHERE назва = 'Диспетчер' LIMIT 1), 51800.00, 'Активний'),
('Полішук', 'Вікторія', 'Андріївна', '1988-02-05', 'Ж', 'м. Київ, вул. Саксаганського, 17, кв. 8', '+380543456789', 'polishchuk@airline.ua', '2017-07-10', (SELECT id FROM посади WHERE назва = 'Диспетчер' LIMIT 1), 51000.00, 'Активний'),
('Романюк', 'Дмитро', 'Сергійович', '1987-05-23', 'Ч', 'м. Київ, вул. Паньківська, 11, кв. 25', '+380544567890', 'romaniuk@airline.ua', '2016-09-18', (SELECT id FROM посади WHERE назва = 'Диспетчер' LIMIT 1), 51300.00, 'Активний'); 