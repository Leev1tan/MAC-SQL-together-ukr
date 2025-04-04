-- Імпорт даних про літаки для бази даних "Авіакомпанія"

INSERT INTO літаки (реєстраційний_номер, серійний_номер, тип_літака_id, рік_випуску, дата_останнього_капітального_ремонту, дата_останнього_техогляду, загальний_наліт_годин, статус, примітки) VALUES
-- Boeing 737-800
('UR-PSA', 'B738-38124', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 737-800'), 2016, '2022-06-15', '2023-04-10', 14500, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-PSB', 'B738-38256', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 737-800'), 2016, '2022-07-20', '2023-05-15', 15200, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-PSC', 'B738-38315', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 737-800'), 2017, '2022-08-10', '2023-06-05', 13800, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-PSD', 'B738-38427', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 737-800'), 2018, '2022-09-25', '2023-07-12', 12500, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-PSE', 'B738-38569', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 737-800'), 2019, '2022-10-30', '2023-08-18', 10200, 'Активний', 'У відмінному стані, виконує регулярні рейси'),

-- Airbus A320
('UR-AAA', 'A320-6547', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A320'), 2015, '2022-05-12', '2023-03-20', 16800, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-AAB', 'A320-6702', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A320'), 2016, '2022-06-18', '2023-04-15', 15600, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-AAC', 'A320-6845', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A320'), 2017, '2022-07-25', '2023-05-10', 14200, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-AAD', 'A320-7056', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A320'), 2018, '2022-09-02', '2023-06-22', 12800, 'Активний', 'У відмінному стані, виконує регулярні рейси'),
('UR-AAE', 'A320-7201', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A320'), 2019, '2022-10-15', '2023-07-30', 10500, 'Активний', 'У відмінному стані, виконує регулярні рейси'),

-- Boeing 787-9 Dreamliner
('UR-DRM', 'B789-42578', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 787-9 Dreamliner'), 2018, '2022-04-18', '2023-02-25', 11800, 'Активний', 'У відмінному стані, виконує дальні рейси'),
('UR-DRN', 'B789-42892', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 787-9 Dreamliner'), 2019, '2022-06-30', '2023-03-15', 9500, 'Активний', 'У відмінному стані, виконує дальні рейси'),
('UR-DRP', 'B789-43125', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 787-9 Dreamliner'), 2020, '2022-09-10', '2023-05-05', 7200, 'Активний', 'У відмінному стані, виконує дальні рейси'),

-- Airbus A330-300
('UR-WDL', 'A333-1548', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A330-300'), 2015, '2022-03-20', '2023-01-15', 18500, 'Активний', 'У відмінному стані, виконує дальні рейси'),
('UR-WDM', 'A333-1605', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A330-300'), 2016, '2022-05-25', '2023-02-28', 16200, 'Активний', 'У відмінному стані, виконує дальні рейси'),
('UR-WDN', 'A333-1724', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A330-300'), 2017, '2022-08-05', '2023-04-10', 14800, 'Активний', 'У відмінному стані, виконує дальні рейси'),

-- Embraer E190
('UR-EMB', 'E190-542', (SELECT id FROM типи_літаків WHERE назва = 'Embraer E190'), 2015, '2022-02-15', '2023-01-10', 19200, 'Активний', 'У відмінному стані, виконує регіональні рейси'),
('UR-EMC', 'E190-586', (SELECT id FROM типи_літаків WHERE назва = 'Embraer E190'), 2016, '2022-04-20', '2023-02-18', 17500, 'Активний', 'У відмінному стані, виконує регіональні рейси'),
('UR-EMD', 'E190-624', (SELECT id FROM типи_літаків WHERE назва = 'Embraer E190'), 2017, '2022-06-30', '2023-03-25', 15800, 'Активний', 'У відмінному стані, виконує регіональні рейси'),
('UR-EME', 'E190-675', (SELECT id FROM типи_літаків WHERE назва = 'Embraer E190'), 2018, '2022-09-12', '2023-05-02', 13600, 'Активний', 'У відмінному стані, виконує регіональні рейси'),

-- Antonov An-158
('UR-ANT', 'AN158-002', (SELECT id FROM типи_літаків WHERE назва = 'Antonov An-158'), 2013, '2022-01-25', '2023-01-05', 21500, 'Активний', 'У відмінному стані, виконує регіональні рейси'),
('UR-ANU', 'AN158-003', (SELECT id FROM типи_літаків WHERE назва = 'Antonov An-158'), 2014, '2022-03-30', '2023-02-12', 19800, 'Активний', 'У відмінному стані, виконує регіональні рейси'),
('UR-ANV', 'AN158-004', (SELECT id FROM типи_літаків WHERE назва = 'Antonov An-158'), 2015, '2022-06-15', '2023-03-20', 18200, 'Активний', 'У відмінному стані, виконує регіональні рейси'),

-- Bombardier CRJ-900
('UR-CRJ', 'CRJ9-15207', (SELECT id FROM типи_літаків WHERE назва = 'Bombardier CRJ-900'), 2015, '2022-02-10', '2023-01-08', 19500, 'Активний', 'У відмінному стані, виконує регіональні рейси'),
('UR-CRK', 'CRJ9-15384', (SELECT id FROM типи_літаків WHERE назва = 'Bombardier CRJ-900'), 2016, '2022-04-15', '2023-02-15', 17800, 'Активний', 'У відмінному стані, виконує регіональні рейси'),
('UR-CRL', 'CRJ9-15526', (SELECT id FROM типи_літаків WHERE назва = 'Bombardier CRJ-900'), 2017, '2022-07-25', '2023-03-28', 16200, 'Активний', 'У відмінному стані, виконує регіональні рейси'),

-- ATR 72-600
('UR-ATR', 'ATR72-1254', (SELECT id FROM типи_літаків WHERE назва = 'ATR 72-600'), 2016, '2022-01-20', '2023-01-05', 18200, 'Активний', 'У відмінному стані, виконує короткі регіональні рейси'),
('UR-ATS', 'ATR72-1318', (SELECT id FROM типи_літаків WHERE назва = 'ATR 72-600'), 2017, '2022-03-25', '2023-02-10', 16500, 'Активний', 'У відмінному стані, виконує короткі регіональні рейси'),
('UR-ATT', 'ATR72-1425', (SELECT id FROM типи_літаків WHERE назва = 'ATR 72-600'), 2018, '2022-05-30', '2023-03-15', 14800, 'Активний', 'У відмінному стані, виконує короткі регіональні рейси'),

-- Літаки на техобслуговуванні або з іншими статусами
('UR-PSF', 'B738-38712', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 737-800'), 2019, '2022-11-15', '2023-04-20', 9800, 'Техобслуговування', 'На плановому технічному обслуговуванні до 2023-12-15'),
('UR-AAF', 'A320-7345', (SELECT id FROM типи_літаків WHERE назва = 'Airbus A320'), 2020, '2022-12-05', '2023-05-15', 8500, 'Техобслуговування', 'На плановому технічному обслуговуванні до 2023-12-10'),
('UR-DRQ', 'B789-43267', (SELECT id FROM типи_літаків WHERE назва = 'Boeing 787-9 Dreamliner'), 2021, '2023-02-15', '2023-08-10', 5800, 'Техобслуговування', 'На плановому технічному обслуговуванні до 2023-12-20'),
('UR-EMF', 'E190-715', (SELECT id FROM типи_літаків WHERE назва = 'Embraer E190'), 2019, '2022-10-20', '2023-06-15', 11200, 'Ремонт', 'На позаплановому ремонті до 2023-12-25'),
('UR-ANW', 'AN158-005', (SELECT id FROM типи_літаків WHERE назва = 'Antonov An-158'), 2016, '2022-08-10', '2023-04-25', 16500, 'Ремонт', 'На позаплановому ремонті до 2023-12-30'); 