-- Дані про розклад занять, записи та відвідування для бази даних "Спортивний клуб"
-- Призначення: Наповнення таблиць розкладу, записів на групові заняття та відвідувань клубу
-- Кодування: UTF-8

-- Очищення таблиць у зворотному порядку залежностей перед вставкою
DELETE FROM відвідування;
DELETE FROM записи_на_заняття;
DELETE FROM розклад_занять;

-- Оновлення лічильника послідовності для стовпця id таблиці розкладу ПЕРЕД вставкою
-- Це гарантує, що ID почнуться з 1, оскільки таблиця тепер точно порожня.
SELECT setval(pg_get_serial_sequence('розклад_занять', 'id'), 1, false);

-- Розклад занять
-- Створюємо розклад для групових занять
-- Примітка: ID групових занять (заняття_id) та тренерів (тренер_id) взяті з відповідних таблиць (data_classes.sql, data_trainers.sql)
-- ID приміщень (приміщення_id) взяті з data_facilities.sql
INSERT INTO розклад_занять (заняття_id, тренер_id, приміщення_id, день_тижня, час_початку, час_закінчення, дата_початку, максимальна_кількість_учасників, примітки) VALUES
-- Понеділок
(1, 2, 1, 'Понеділок', '08:00', '09:00', '2023-07-01', 15, 'Йога для початківців'), -- ID: 1
(2, 6, 2, 'Понеділок', '09:00', '10:00', '2023-07-01', 20, 'Аеробіка'), -- ID: 2
(3, 8, 1, 'Понеділок', '10:00', '11:00', '2023-07-01', 15, 'Пілатес'), -- ID: 3
(4, 7, 2, 'Понеділок', '12:00', '13:00', '2023-07-01', 18, 'Функціональне тренування'), -- ID: 4
(5, 6, 2, 'Понеділок', '17:00', '18:00', '2023-07-01', 20, 'Боді-памп'), -- ID: 5
(6, 2, 1, 'Понеділок', '18:00', '19:30', '2023-07-01', 15, 'Йога-флоу'), -- ID: 6
(7, 15, 3, 'Понеділок', '19:00', '20:00', '2023-07-01', 12, 'Кікбоксинг'), -- ID: 7
(8, 14, 1, 'Понеділок', '20:00', '21:00', '2023-07-01', 15, 'Стретчинг'), -- ID: 8
-- Вівторок
(9, 12, 4, 'Вівторок', '09:00', '10:00', '2023-07-01', 15, 'Аквааеробіка'); -- ID: 9
-- Додайте інші дні та заняття за потребою...

-- Оновлення лічильника послідовності для стовпця id таблиці записів ПЕРЕД вставкою
SELECT setval(pg_get_serial_sequence('записи_на_заняття', 'id'), 1, false);

-- Записи на заняття
-- Створюємо записи на заняття для різних клієнтів на різні дати
INSERT INTO записи_на_заняття (розклад_заняття_id, член_клубу_id, дата_запису, статус_id, примітки) VALUES
-- Записи на заняття з йоги для початківців (Понеділок)
(1, 4, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(1, 8, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(1, 12, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(1, 4, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(1, 8, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(1, 12, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(1, 22, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(1, 4, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(1, 8, '2023-07-17 00:00:00', 3, 'Скасовано клієнтом'),
(1, 12, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на заняття з аеробіки (Понеділок)
(2, 4, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(2, 10, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(2, 14, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(2, 18, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(2, 4, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(2, 10, '2023-07-10 00:00:00', 3, 'Скасовано клієнтом'),
(2, 14, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(2, 18, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(2, 20, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(2, 4, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(2, 10, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(2, 14, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на заняття з пілатесу (Понеділок)
(3, 4, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(3, 6, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(3, 8, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(3, 12, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(3, 22, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(3, 4, '2023-07-10 00:00:00', 3, 'Скасовано клієнтом'),
(3, 6, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(3, 8, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(3, 12, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(3, 4, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(3, 6, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(3, 8, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на функціональне тренування (Понеділок)
(4, 1, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(4, 3, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(4, 7, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(4, 9, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(4, 1, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(4, 3, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(4, 7, '2023-07-10 00:00:00', 3, 'Скасовано клієнтом'),
(4, 9, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(4, 11, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(4, 1, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(4, 3, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(4, 7, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на боді-памп (Понеділок)
(5, 2, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(5, 5, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(5, 9, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(5, 13, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(5, 15, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(5, 2, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(5, 5, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(5, 9, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(5, 13, '2023-07-10 00:00:00', 3, 'Скасовано клієнтом'),
(5, 15, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(5, 17, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(5, 19, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(5, 2, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(5, 5, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(5, 9, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на йога-флоу (Понеділок)
(6, 2, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(6, 4, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(6, 8, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(6, 10, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(6, 2, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(6, 4, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(6, 8, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(6, 10, '2023-07-10 00:00:00', 3, 'Скасовано клієнтом'),
(6, 2, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(6, 4, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(6, 8, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на кікбоксинг (Понеділок)
(7, 1, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(7, 3, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(7, 5, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(7, 9, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(7, 15, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(7, 1, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(7, 3, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(7, 5, '2023-07-10 00:00:00', 3, 'Скасовано клієнтом'),
(7, 9, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(7, 15, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(7, 1, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(7, 3, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(7, 5, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на стретчинг (Понеділок)
(8, 4, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(8, 6, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(8, 8, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(8, 10, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(8, 12, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(8, 14, '2023-07-03 00:00:00', 1, 'Запис підтверджено'),
(8, 4, '2023-07-10 00:00:00', 3, 'Скасовано клієнтом'),
(8, 6, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(8, 8, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(8, 10, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(8, 12, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(8, 14, '2023-07-10 00:00:00', 1, 'Запис підтверджено'),
(8, 4, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(8, 6, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),
(8, 8, '2023-07-17 00:00:00', 1, 'Запис підтверджено'),

-- Записи на аквааеробіку (Вівторок)
(9, 4, '2023-07-04 00:00:00', 1, 'Запис підтверджено'),
(9, 6, '2023-07-04 00:00:00', 1, 'Запис підтверджено'),
(9, 8, '2023-07-04 00:00:00', 1, 'Запис підтверджено'),
(9, 10, '2023-07-04 00:00:00', 1, 'Запис підтверджено'),
(9, 4, '2023-07-11 00:00:00', 1, 'Запис підтверджено'),
(9, 6, '2023-07-11 00:00:00', 1, 'Запис підтверджено'),
(9, 8, '2023-07-11 00:00:00', 3, 'Скасовано клієнтом'),
(9, 10, '2023-07-11 00:00:00', 1, 'Запис підтверджено'),
(9, 22, '2023-07-11 00:00:00', 1, 'Запис підтверджено'),
(9, 4, '2023-07-18 00:00:00', 1, 'Запис підтверджено'),
(9, 6, '2023-07-18 00:00:00', 1, 'Запис підтверджено'),
(9, 8, '2023-07-18 00:00:00', 1, 'Запис підтверджено');

-- Відвідування
-- Відвідування із записами на заняття (зазвичай відвідування з'являється після фактичного відвідування)
INSERT INTO відвідування (член_клубу_id, дата_відвідування, час_приходу, час_виходу, запис_на_заняття_id, примітки) VALUES
-- Відвідування для записів на заняття з йоги для початківців (Понеділок, 03.07.2023)
(4, '2023-07-03', '07:45', '09:15', 1, 'Відвідування заняття з йоги'),
(8, '2023-07-03', '07:50', '09:10', 2, 'Відвідування заняття з йоги'),
(12, '2023-07-03', '07:55', '09:05', 3, 'Відвідування заняття з йоги'),

-- Відвідування для записів на заняття з аеробіки (Понеділок, 03.07.2023)
(4, '2023-07-03', '08:50', '10:00', 11, 'Відвідування заняття з аеробіки'),
(10, '2023-07-03', '08:45', '09:55', 12, 'Відвідування заняття з аеробіки'),
(14, '2023-07-03', '08:50', '09:50', 13, 'Відвідування заняття з аеробіки'),
(18, '2023-07-03', '08:55', '10:05', 14, 'Відвідування заняття з аеробіки'),

-- Відвідування для записів на заняття з пілатесу (Понеділок, 03.07.2023)
(4, '2023-07-03', '09:45', '11:15', 23, 'Відвідування заняття з пілатесу'),
(6, '2023-07-03', '09:50', '11:10', 24, 'Відвідування заняття з пілатесу'),
(8, '2023-07-03', '09:55', '11:05', 25, 'Відвідування заняття з пілатесу'),
(12, '2023-07-03', '09:45', '11:15', 26, 'Відвідування заняття з пілатесу'),
(22, '2023-07-03', '09:50', '11:10', 27, 'Відвідування заняття з пілатесу'),

-- Відвідування для записів на функціональне тренування (Понеділок, 03.07.2023)
(1, '2023-07-03', '11:45', '13:00', 34, 'Відвідування функціонального тренування'),
(3, '2023-07-03', '11:50', '13:05', 35, 'Відвідування функціонального тренування'),
(7, '2023-07-03', '11:55', '13:10', 36, 'Відвідування функціонального тренування'),
(9, '2023-07-03', '11:45', '13:00', 37, 'Відвідування функціонального тренування'),

-- Відвідування для записів на боді-памп (Понеділок, 03.07.2023)
(2, '2023-07-03', '16:45', '18:15', 45, 'Відвідування заняття з боді-памп'),
(5, '2023-07-03', '16:50', '18:10', 46, 'Відвідування заняття з боді-памп'),
(9, '2023-07-03', '16:55', '18:05', 47, 'Відвідування заняття з боді-памп'),
(13, '2023-07-03', '16:45', '18:15', 48, 'Відвідування заняття з боді-памп'),
(15, '2023-07-03', '16:50', '18:10', 49, 'Відвідування заняття з боді-памп'),

-- Відвідування для записів на йога-флоу (Понеділок, 03.07.2023)
(2, '2023-07-03', '17:45', '19:30', 56, 'Відвідування заняття з йога-флоу'),
(4, '2023-07-03', '17:50', '19:25', 57, 'Відвідування заняття з йога-флоу'),
(8, '2023-07-03', '17:55', '19:20', 58, 'Відвідування заняття з йога-флоу'),
(10, '2023-07-03', '17:45', '19:30', 59, 'Відвідування заняття з йога-флоу'),

-- Відвідування для записів на кікбоксинг (Понеділок, 03.07.2023)
(1, '2023-07-03', '18:45', '20:15', 67, 'Відвідування заняття з кікбоксингу'),
(3, '2023-07-03', '18:50', '20:10', 68, 'Відвідування заняття з кікбоксингу'),
(5, '2023-07-03', '18:55', '20:05', 69, 'Відвідування заняття з кікбоксингу'),
(9, '2023-07-03', '18:45', '20:15', 70, 'Відвідування заняття з кікбоксингу'),
(15, '2023-07-03', '18:50', '20:10', 71, 'Відвідування заняття з кікбоксингу'),

-- Відвідування для записів на стретчинг (Понеділок, 03.07.2023)
(4, '2023-07-03', '19:45', '21:00', 78, 'Відвідування заняття зі стретчингу'),
(6, '2023-07-03', '19:50', '20:55', 79, 'Відвідування заняття зі стретчингу'),
(8, '2023-07-03', '19:55', '20:50', 80, 'Відвідування заняття зі стретчингу'),
(10, '2023-07-03', '19:45', '21:00', 81, 'Відвідування заняття зі стретчингу'),
(12, '2023-07-03', '19:50', '20:55', 82, 'Відвідування заняття зі стретчингу'),
(14, '2023-07-03', '19:55', '20:50', 83, 'Відвідування заняття зі стретчингу'),

-- Відвідування для записів на аквааеробіку (Вівторок, 04.07.2023)
(4, '2023-07-04', '08:45', '10:00', 89, 'Відвідування заняття з аквааеробіки'),
(6, '2023-07-04', '08:50', '09:55', 90, 'Відвідування заняття з аквааеробіки'),
(8, '2023-07-04', '08:55', '09:50', 91, 'Відвідування заняття з аквааеробіки'),
(10, '2023-07-04', '08:45', '10:00', 92, 'Відвідування заняття з аквааеробіки'),

-- Відвідування без запису на заняття (звичайні відвідування тренажерного залу)
(1, '2023-07-03', '15:30', '17:00', NULL, 'Звичайне відвідування тренажерного залу'),
(2, '2023-07-03', '12:00', '13:30', NULL, 'Звичайне відвідування тренажерного залу'),
(3, '2023-07-03', '07:00', '08:30', NULL, 'Звичайне відвідування тренажерного залу'),
(5, '2023-07-03', '14:00', '15:30', NULL, 'Звичайне відвідування тренажерного залу'),
(7, '2023-07-03', '18:30', '20:00', NULL, 'Звичайне відвідування тренажерного залу'),
(11, '2023-07-03', '10:00', '11:30', NULL, 'Звичайне відвідування тренажерного залу'),
(13, '2023-07-03', '12:30', '14:00', NULL, 'Звичайне відвідування тренажерного залу'),
(15, '2023-07-03', '08:00', '09:30', NULL, 'Звичайне відвідування тренажерного залу'),
(16, '2023-07-03', '09:00', '10:30', NULL, 'Звичайне відвідування тренажерного залу'),
(17, '2023-07-03', '06:30', '08:00', NULL, 'Звичайне відвідування тренажерного залу'),
(19, '2023-07-03', '17:30', '19:00', NULL, 'Звичайне відвідування тренажерного залу'),
(20, '2023-07-03', '19:00', '20:30', NULL, 'Звичайне відвідування тренажерного залу'),

(1, '2023-07-04', '07:30', '09:00', NULL, 'Звичайне відвідування тренажерного залу'),
(2, '2023-07-04', '15:00', '16:30', NULL, 'Звичайне відвідування тренажерного залу'),
(3, '2023-07-04', '18:00', '19:30', NULL, 'Звичайне відвідування тренажерного залу'),
(5, '2023-07-04', '07:00', '08:30', NULL, 'Звичайне відвідування тренажерного залу'),
(7, '2023-07-04', '16:30', '18:00', NULL, 'Звичайне відвідування тренажерного залу'),
(9, '2023-07-04', '12:00', '13:30', NULL, 'Звичайне відвідування тренажерного залу'),
(11, '2023-07-04', '15:30', '17:00', NULL, 'Звичайне відвідування тренажерного залу'),
(13, '2023-07-04', '07:30', '09:00', NULL, 'Звичайне відвідування тренажерного залу'),
(15, '2023-07-04', '19:00', '20:30', NULL, 'Звичайне відвідування тренажерного залу'),
(17, '2023-07-04', '06:30', '08:00', NULL, 'Звичайне відвідування тренажерного залу'),
(19, '2023-07-04', '14:00', '15:30', NULL, 'Звичайне відвідування тренажерного залу'),
(20, '2023-07-04', '17:30', '19:00', NULL, 'Звичайне відвідування тренажерного залу'),

(1, '2023-07-05', '15:00', '16:30', NULL, 'Звичайне відвідування тренажерного залу'),
(2, '2023-07-05', '07:30', '09:00', NULL, 'Звичайне відвідування тренажерного залу'),
(3, '2023-07-05', '12:00', '13:30', NULL, 'Звичайне відвідування тренажерного залу'),
(5, '2023-07-05', '18:00', '19:30', NULL, 'Звичайне відвідування тренажерного залу'),
(7, '2023-07-05', '07:00', '08:30', NULL, 'Звичайне відвідування тренажерного залу'),
(9, '2023-07-05', '16:30', '18:00', NULL, 'Звичайне відвідування тренажерного залу'),
(11, '2023-07-05', '15:30', '17:00', NULL, 'Звичайне відвідування тренажерного залу'),
(13, '2023-07-05', '19:00', '20:30', NULL, 'Звичайне відвідування тренажерного залу'),
(15, '2023-07-05', '07:30', '09:00', NULL, 'Звичайне відвідування тренажерного залу'),
(17, '2023-07-05', '14:00', '15:30', NULL, 'Звичайне відвідування тренажерного залу'),
(19, '2023-07-05', '06:30', '08:00', NULL, 'Звичайне відвідування тренажерного залу'),
(20, '2023-07-05', '17:30', '19:00', NULL, 'Звичайне відвідування тренажерного залу'); 