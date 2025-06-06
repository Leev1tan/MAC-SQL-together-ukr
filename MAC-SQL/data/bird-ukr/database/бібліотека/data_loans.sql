-- Data for Loans (видачі)
-- Created for Ukrainian Text-to-SQL dataset

-- Loans (видачі)
INSERT INTO видачі (примірник_ід, читач_ід, працівник_видав_ід, працівник_прийняв_ід, дата_видачі, очікувана_дата_повернення, дата_повернення, продовжено, кількість_продовжень, статус, примітки)
VALUES 
    -- Активні видачі
    (2, 3, 26, NULL, '2023-11-15', '2023-12-15', NULL, FALSE, 0, 'видано', NULL),
    (4, 5, 27, NULL, '2023-11-20', '2023-12-20', NULL, FALSE, 0, 'видано', NULL),
    (6, 2, 26, NULL, '2023-11-25', '2023-12-25', NULL, FALSE, 0, 'видано', 'Попередня резервація'),
    (8, 7, 28, NULL, '2023-11-28', '2023-12-28', NULL, FALSE, 0, 'видано', NULL),
    (10, 8, 27, NULL, '2023-12-01', '2024-01-01', NULL, FALSE, 0, 'видано', NULL),
    (13, 10, 29, NULL, '2023-12-03', '2024-01-03', NULL, FALSE, 0, 'видано', NULL),
    (16, 4, 26, NULL, '2023-12-05', '2024-01-05', NULL, FALSE, 0, 'видано', NULL),
    (19, 9, 28, NULL, '2023-12-07', '2024-01-07', NULL, FALSE, 0, 'видано', NULL),
    (22, 12, 29, NULL, '2023-12-09', '2024-01-09', NULL, FALSE, 0, 'видано', NULL),
    (25, 11, 27, NULL, '2023-12-11', '2024-01-11', NULL, FALSE, 0, 'видано', NULL),
    (27, 6, 26, NULL, '2023-12-12', '2024-01-12', NULL, FALSE, 0, 'видано', 'Науковий проект'),
    (30, 14, 29, NULL, '2023-12-14', '2024-01-14', NULL, FALSE, 0, 'видано', NULL),
    
    -- Повернуті вчасно
    (1, 1, 25, 25, '2023-10-01', '2023-11-01', '2023-10-30', FALSE, 0, 'повернуто', NULL),
    (3, 2, 25, 26, '2023-10-05', '2023-11-05', '2023-11-03', FALSE, 0, 'повернуто', NULL),
    (5, 3, 26, 27, '2023-10-08', '2023-11-08', '2023-11-07', FALSE, 0, 'повернуто', NULL),
    (7, 4, 27, 28, '2023-10-10', '2023-11-10', '2023-11-09', FALSE, 0, 'повернуто', NULL),
    (9, 5, 28, 25, '2023-10-12', '2023-11-12', '2023-11-10', FALSE, 0, 'повернуто', NULL),
    (11, 6, 29, 26, '2023-10-15', '2023-11-15', '2023-11-14', FALSE, 0, 'повернуто', NULL),
    (12, 7, 25, 27, '2023-10-18', '2023-11-18', '2023-11-17', FALSE, 0, 'повернуто', NULL),
    (14, 8, 26, 28, '2023-10-20', '2023-11-20', '2023-11-19', FALSE, 0, 'повернуто', NULL),
    (15, 9, 27, 29, '2023-10-22', '2023-11-22', '2023-11-20', FALSE, 0, 'повернуто', NULL),
    (17, 10, 28, 25, '2023-10-25', '2023-11-25', '2023-11-24', FALSE, 0, 'повернуто', NULL),
    (18, 11, 29, 26, '2023-10-28', '2023-11-28', '2023-11-26', FALSE, 0, 'повернуто', NULL),
    (20, 12, 25, 27, '2023-10-30', '2023-11-30', '2023-11-29', FALSE, 0, 'повернуто', NULL),
    
    -- Повернуті із запізненням
    (21, 13, 26, 28, '2023-09-01', '2023-10-01', '2023-10-10', FALSE, 0, 'повернуто', 'Запізнення 9 днів'),
    (23, 14, 27, 29, '2023-09-05', '2023-10-05', '2023-10-20', FALSE, 0, 'повернуто', 'Запізнення 15 днів'),
    (24, 15, 28, 25, '2023-09-10', '2023-10-10', '2023-10-15', FALSE, 0, 'повернуто', 'Запізнення 5 днів'),
    (26, 1, 29, 26, '2023-09-15', '2023-10-15', '2023-10-25', FALSE, 0, 'повернуто', 'Запізнення 10 днів'),
    (28, 2, 25, 27, '2023-09-20', '2023-10-20', '2023-10-30', FALSE, 0, 'повернуто', 'Запізнення 10 днів'),
    (29, 3, 26, 28, '2023-09-25', '2023-10-25', '2023-10-28', FALSE, 0, 'повернуто', 'Запізнення 3 дні'),
    (31, 4, 27, 29, '2023-09-30', '2023-10-30', '2023-11-05', FALSE, 0, 'повернуто', 'Запізнення 6 днів'),
    
    -- Історія книг, які часто видаються
    (1, 5, 25, 26, '2023-08-01', '2023-09-01', '2023-08-29', FALSE, 0, 'повернуто', NULL),
    (1, 8, 27, 28, '2023-07-01', '2023-08-01', '2023-07-30', FALSE, 0, 'повернуто', NULL),
    (1, 10, 29, 25, '2023-06-01', '2023-07-01', '2023-06-29', FALSE, 0, 'повернуто', NULL),
    (5, 7, 26, 27, '2023-08-05', '2023-09-05', '2023-09-03', FALSE, 0, 'повернуто', NULL),
    (5, 9, 28, 29, '2023-07-05', '2023-08-05', '2023-08-02', FALSE, 0, 'повернуто', NULL),
    (5, 11, 25, 26, '2023-06-05', '2023-07-05', '2023-07-05', FALSE, 0, 'повернуто', NULL),
    (9, 4, 27, 28, '2023-08-10', '2023-09-10', '2023-09-08', FALSE, 0, 'повернуто', NULL),
    (9, 6, 29, 25, '2023-07-10', '2023-08-10', '2023-08-09', FALSE, 0, 'повернуто', NULL),
    (9, 12, 26, 27, '2023-06-10', '2023-07-10', '2023-07-05', FALSE, 0, 'повернуто', NULL); 