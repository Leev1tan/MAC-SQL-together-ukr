-- Дані для таблиці позицій замовлення для бази даних "Інтернет-магазин"
-- Кодування: UTF-8

-- ==================================
-- Очищення таблиці перед імпортом
-- ==================================

TRUNCATE TABLE позиції_замовлення CASCADE;

-- Скидання лічильника автоінкременту
ALTER SEQUENCE позиції_замовлення_ід_seq RESTART WITH 1;

-- ==================================
-- Імпорт даних про позиції замовлень
-- ==================================

INSERT INTO позиції_замовлення (
    замовлення_ід, товар_ід, артикул, назва_товару, 
    ціна_за_одиницю, кількість, сума, сума_знижки
) VALUES
-- Позиції для замовлення #1 (iPhone 14)
(1, 1, 'IPH14-128-BLK', 'Apple iPhone 14 128GB Чорний', 
 32999.99, 1, 32999.99, 0.00),

-- Позиції для замовлення #2 (POCO F5)
(2, 7, 'XIA-POCO-F5-12-256-BLK', 'Xiaomi POCO F5 12/256GB Чорний', 
 15999.99, 1, 15999.99, 0.00),

(2, NULL, 'ACC-SCRPROT-XIA-F5', 'Захисне скло для Xiaomi POCO F5', 
 999.99, 1, 999.99, 0.00),

-- Позиції для замовлення #3 (Samsung Galaxy S23)
(3, 4, 'SAM-S23-8-256-BLK', 'Samsung Galaxy S23 8/256GB Чорний', 
 31999.99, 1, 31999.99, 6000.00),

-- Позиції для замовлення #4 (MacBook Air + аксесуари)
(4, 8, 'LP-MAC-AIR-M2-8-256', 'Apple MacBook Air 13.6" M2 8/256GB 2022', 
 45999.99, 1, 45999.99, 0.00),

(4, NULL, 'ACC-MACBOOK-CASE', 'Чохол для MacBook Air 13.6"', 
 1999.99, 1, 1999.99, 0.00),

(4, NULL, 'ACC-MACBOOK-ADAPTER', 'Адаптер USB-C до USB-A/HDMI для MacBook', 
 2999.99, 1, 2999.99, 0.00),

-- Позиції для замовлення #5 (Процесор AMD)
(5, 10, 'CPU-AMD-7800X3D', 'AMD Ryzen 7 7800X3D 4.2GHz/5.0GHz AM5', 
 23999.99, 1, 23999.99, 0.00),

-- Позиції для замовлення #6 (MacBook Air + iPhone 14 Pro)
(6, 8, 'LP-MAC-AIR-M2-8-256', 'Apple MacBook Air 13.6" M2 8/256GB 2022', 
 45999.99, 1, 45999.99, 2000.00),

(6, 3, 'IPH14PRO-256-GOLD', 'Apple iPhone 14 Pro 256GB Золотий', 
 44999.99, 1, 44999.99, 0.00),

-- Позиції для замовлення #7 (Процесор Intel)
(7, 11, 'CPU-INT-13900K', 'Intel Core i9-13900K 3.0GHz/5.8GHz LGA1700', 
 24999.99, 1, 24999.99, 0.00),

-- Позиції для замовлення #8 (POCO F5)
(8, 7, 'XIA-POCO-F5-12-256-BLK', 'Xiaomi POCO F5 12/256GB Чорний', 
 15999.99, 1, 15999.99, 0.00),

-- Позиції для замовлення #9 (корпоративне замовлення ноутбуків)
(9, 9, 'LP-ASUS-VIVOBOOK-i5-8-512', 'ASUS VivoBook 15 i5-12500H 8/512GB', 
 19999.99, 15, 299999.85, 30000.00),

-- Позиції для замовлення #10 (корпоративне замовлення відеокарт)
(10, 12, 'GPU-NV-RTX4070TI-12GB', 'NVIDIA GeForce RTX 4070 Ti 12GB GDDR6X', 
 29999.99, 6, 179999.94, 18000.00),

(10, NULL, 'ACC-POWER-ADAPTER', 'Додатковий блок живлення 750W', 
 3999.99, 1, 3999.99, 0.00);

-- ==================================
-- Встановлення правильного значення для послідовності
-- ==================================

-- Оновлення послідовності для уникнення конфліктів при подальшому додаванні
SELECT setval('позиції_замовлення_ід_seq', (SELECT MAX(ід) FROM позиції_замовлення), true); 