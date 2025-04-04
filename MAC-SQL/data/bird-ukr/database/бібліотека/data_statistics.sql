-- Data for Library Statistics (статистика)
-- Created for Ukrainian Text-to-SQL dataset

-- Statistics (статистика)
INSERT INTO статистика (дата, відділ_ід, кількість_відвідувачів, кількість_виданих_книг, кількість_повернутих_книг, кількість_нових_читачів, кількість_продовжених_абонементів, кількість_наданих_послуг, примітки)
VALUES 
    -- Жовтень 2023 - перший тиждень
    ('2023-10-01', 1, 45, 32, 28, 3, 2, 8, 'Звичайний недільний день'),
    ('2023-10-02', 1, 78, 53, 41, 5, 4, 12, 'Початок навчального тижня, висока відвідуваність'),
    ('2023-10-03', 1, 65, 42, 37, 2, 3, 9, 'Звичайний робочий день'),
    ('2023-10-04', 1, 72, 48, 45, 4, 2, 11, 'Проведено літературний вечір'),
    ('2023-10-05', 1, 69, 51, 39, 3, 5, 10, 'Звичайний робочий день'),
    ('2023-10-06', 1, 80, 59, 47, 6, 3, 15, 'П''ятниця, підвищена відвідуваність'),
    ('2023-10-07', 1, 52, 38, 35, 2, 1, 7, 'Звичайний суботній день'),
    
    -- Жовтень 2023 - другий тиждень
    ('2023-10-08', 2, 38, 25, 22, 1, 0, 5, 'Недільний день, низька відвідуваність'),
    ('2023-10-09', 2, 72, 48, 41, 4, 3, 11, 'Початок тижня, висока відвідуваність'),
    ('2023-10-10', 2, 61, 40, 35, 2, 2, 8, 'Звичайний робочий день'),
    ('2023-10-11', 2, 58, 42, 38, 3, 1, 9, 'Звичайний робочий день'),
    ('2023-10-12', 2, 64, 45, 40, 2, 4, 10, 'Проведено майстер-клас з каліграфії'),
    ('2023-10-13', 2, 75, 53, 48, 5, 2, 14, 'П''ятниця, підвищена відвідуваність'),
    ('2023-10-14', 2, 48, 35, 30, 1, 0, 6, 'Звичайний суботній день'),
    
    -- Жовтень 2023 - третій тиждень
    ('2023-10-15', 3, 41, 28, 25, 2, 1, 7, 'Недільний день, проведено дитяче читання'),
    ('2023-10-16', 3, 68, 45, 42, 3, 2, 10, 'Початок тижня, звичайна відвідуваність'),
    ('2023-10-17', 3, 63, 41, 37, 2, 3, 9, 'Звичайний робочий день'),
    ('2023-10-18', 3, 59, 39, 35, 1, 2, 8, 'Звичайний робочий день'),
    ('2023-10-19', 3, 61, 42, 38, 3, 1, 9, 'Звичайний робочий день'),
    ('2023-10-20', 3, 73, 51, 44, 4, 3, 12, 'П''ятниця, підвищена відвідуваність'),
    ('2023-10-21', 3, 49, 36, 31, 2, 1, 7, 'Звичайний суботній день'),
    
    -- Жовтень 2023 - четвертий тиждень
    ('2023-10-22', 4, 42, 30, 27, 1, 2, 6, 'Недільний день, звичайна відвідуваність'),
    ('2023-10-23', 4, 70, 50, 43, 4, 3, 11, 'Початок тижня, звичайна відвідуваність'),
    ('2023-10-24', 4, 65, 44, 39, 3, 2, 10, 'Звичайний робочий день'),
    ('2023-10-25', 4, 62, 42, 38, 2, 3, 9, 'Звичайний робочий день'),
    ('2023-10-26', 4, 66, 45, 40, 3, 1, 10, 'Звичайний робочий день'),
    ('2023-10-27', 4, 78, 55, 48, 5, 4, 14, 'П''ятниця, підвищена відвідуваність'),
    ('2023-10-28', 4, 52, 38, 33, 2, 1, 8, 'Звичайний суботній день'),
    
    -- Листопад 2023 - перший тиждень
    ('2023-11-01', 5, 76, 52, 46, 4, 3, 12, 'Початок місяця, висока відвідуваність'),
    ('2023-11-02', 5, 69, 48, 42, 3, 2, 10, 'Звичайний робочий день'),
    ('2023-11-03', 5, 84, 60, 52, 6, 4, 15, 'П''ятниця, підвищена відвідуваність'),
    ('2023-11-04', 5, 56, 40, 35, 2, 1, 8, 'Звичайний суботній день'),
    ('2023-11-05', 5, 44, 31, 27, 1, 2, 7, 'Недільний день, звичайна відвідуваність'),
    
    -- Листопад 2023 - другий тиждень
    ('2023-11-06', 6, 74, 50, 45, 5, 3, 12, 'Початок тижня, висока відвідуваність'),
    ('2023-11-07', 6, 67, 46, 40, 3, 2, 10, 'Звичайний робочий день'),
    ('2023-11-08', 6, 63, 43, 38, 2, 3, 9, 'Звичайний робочий день'),
    ('2023-11-09', 6, 60, 41, 36, 3, 1, 9, 'Звичайний робочий день'),
    ('2023-11-10', 6, 79, 56, 49, 5, 4, 14, 'П''ятниця, підвищена відвідуваність'),
    ('2023-11-11', 6, 53, 38, 34, 2, 1, 8, 'Звичайний суботній день'),
    ('2023-11-12', 6, 45, 32, 28, 1, 2, 7, 'Недільний день, звичайна відвідуваність'),
    
    -- Листопад 2023 - третій тиждень
    ('2023-11-13', 2, 71, 48, 43, 4, 3, 11, 'Початок тижня, звичайна відвідуваність'),
    ('2023-11-14', 2, 66, 45, 39, 3, 2, 10, 'Звичайний робочий день'),
    ('2023-11-15', 2, 64, 43, 38, 2, 3, 9, 'Звичайний робочий день'),
    ('2023-11-16', 2, 62, 42, 37, 3, 1, 9, 'Звичайний робочий день'),
    ('2023-11-17', 2, 80, 57, 50, 5, 4, 14, 'П''ятниця, підвищена відвідуваність'),
    ('2023-11-18', 2, 54, 39, 34, 2, 1, 8, 'Звичайний суботній день'),
    ('2023-11-19', 2, 46, 33, 29, 1, 2, 7, 'Недільний день, звичайна відвідуваність'),
    
    -- Листопад 2023 - четвертий тиждень
    ('2023-11-20', 4, 73, 49, 44, 4, 3, 12, 'Початок тижня, звичайна відвідуваність'),
    ('2023-11-21', 4, 67, 46, 40, 3, 2, 10, 'Звичайний робочий день'),
    ('2023-11-22', 4, 65, 44, 39, 2, 3, 9, 'Звичайний робочий день'),
    ('2023-11-23', 4, 63, 43, 38, 3, 1, 9, 'Звичайний робочий день'),
    ('2023-11-24', 4, 81, 58, 51, 5, 4, 15, 'П''ятниця, підвищена відвідуваність'),
    ('2023-11-25', 4, 55, 40, 35, 2, 1, 8, 'Звичайний суботній день'),
    ('2023-11-26', 4, 47, 34, 30, 1, 2, 7, 'Недільний день, звичайна відвідуваність'),
    
    -- Грудень 2023 - початок
    ('2023-12-01', 1, 86, 61, 55, 7, 5, 16, 'Початок грудня, підвищена відвідуваність'),
    ('2023-12-02', 1, 58, 42, 37, 2, 1, 9, 'Звичайний суботній день'),
    ('2023-12-03', 1, 49, 35, 31, 1, 2, 8, 'Недільний день, звичайна відвідуваність'); 