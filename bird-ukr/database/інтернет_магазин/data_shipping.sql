-- Дані для таблиці доставок для бази даних "Інтернет-магазин"
-- Кодування: UTF-8

-- ==================================
-- Очищення таблиці перед імпортом
-- ==================================

TRUNCATE TABLE доставки CASCADE;

-- Скидання лічильника автоінкременту
ALTER SEQUENCE доставки_ід_seq RESTART WITH 1;

-- ==================================
-- Імпорт даних про доставки
-- ==================================

INSERT INTO доставки (
    замовлення_ід, метод_доставки, номер_відстеження, статус, 
    адреса_доставки_ід, вартість, дата_створення, 
    дата_відправлення, дата_доставки, отримувач_прізвище,
    отримувач_імя, отримувач_телефон, примітки
) VALUES
-- Доставки для завершених замовлень
(1, 'нова_пошта', '59000123456789', 'доставлено', 
 1, 75.00, '2023-01-25 15:12:45', 
 '2023-01-26 10:15:22', '2023-01-27 12:30:00', 'Коваль',
 'Петро', '+380501234567', 'Відділення №5, Київ'),

(2, 'нова_пошта', '59000234567891', 'доставлено', 
 3, 75.00, '2023-02-03 10:22:30', 
 '2023-02-04 11:05:35', '2023-02-06 15:40:20', 'Шевченко',
 'Олена', '+380672345678', 'Відділення №12, Львів'),

(3, 'нова_пошта_кур''єр', '59000345678912', 'доставлено', 
 4, 0.00, '2023-02-17 19:05:12', 
 '2023-02-18 10:30:40', '2023-02-20 14:15:55', 'Бондар',
 'Іван', '+380503456789', 'Безкоштовна доставка'),

(4, 'кур''єр_магазину', NULL, 'доставлено', 
 6, 0.00, '2023-03-05 11:25:15', 
 '2023-03-05 16:30:45', '2023-03-06 12:45:20', 'Мельник',
 'Наталія', '+380674567890', 'VIP клієнт, особлива доставка'),

-- Доставки для активних замовлень
(5, 'нова_пошта', '59000456789123', 'в_дорозі', 
 8, 75.00, '2024-05-20 16:12:30', 
 '2024-05-21 09:45:15', NULL, 'Ткаченко',
 'Сергій', '+380505678901', 'Відділення №22, Дніпро'),

(6, 'нова_пошта_кур''єр', '59000567891234', 'підготовка_до_відправки', 
 10, 0.00, '2024-05-21 10:30:45', 
 NULL, NULL, 'Кравчук',
 'Тетяна', '+380679123456', 'Платиновий клієнт, особливе пакування'),

(7, 'нова_пошта_кур''єр', NULL, 'очікує_відправки', 
 12, 120.00, '2024-05-22 09:45:20', 
 NULL, NULL, 'Савчук',
 'Володимир', '+380501234567', 'Термінова доставка'),

-- Доставки для нових замовлень
(8, 'нова_пошта', NULL, 'очікує_обробки', 
 9, 75.00, '2024-05-23 14:22:35', 
 NULL, NULL, 'Даниленко',
 'Марія', '+380676789012', 'Перше замовлення нового клієнта'),

-- Доставки для корпоративних замовлень
(9, 'власний_транспорт', NULL, 'очікує_оплати', 
 14, 0.00, '2024-05-15 12:30:10', 
 NULL, NULL, 'Вітренко',
 'Олександр', '+380632345678', 'Корпоративна доставка власним транспортом після оплати'),

(10, 'нова_пошта_вантаж', '59000678912345', 'комплектується', 
 15, 0.00, '2024-05-10 10:45:15', 
 NULL, NULL, 'Коваленко',
 'Ірина', '+380504567890', 'Великогабаритний вантаж, потрібна попередня домовленість');

-- ==================================
-- Встановлення правильного значення для послідовності
-- ==================================

-- Оновлення послідовності для уникнення конфліктів при подальшому додаванні
SELECT setval('доставки_ід_seq', (SELECT MAX(ід) FROM доставки), true); 