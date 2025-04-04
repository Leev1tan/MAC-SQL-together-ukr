-- Дані про платежі для бази даних "Туристичне агентство"

-- Налаштування кодування
SET client_encoding = 'UTF8';

-- Очищення таблиці перед додаванням даних
TRUNCATE TABLE платежі CASCADE;

-- Додавання платежів
INSERT INTO платежі (бронювання_id, сума, дата_платежу, тип_платежу, статус, номер_транзакції, примітки) VALUES
-- Платежі для бронювань зі статусом "Оплачено"
(1, 11600, '2023-03-15', 'Повна оплата', 'Успішно', 'TR23031501', 'Оплата кредитною карткою Visa'),
(2, 9500, '2023-02-22', 'Повна оплата', 'Успішно', 'TR23022201', 'Банківський переказ з ПриватБанку'),
(3, 22500, '2023-05-20', 'Повна оплата', 'Успішно', 'TR23052001', 'Оплата кредитною карткою MasterCard'),
(4, 7000, '2023-03-05', 'Повна оплата', 'Успішно', 'TR23030501', 'Оплата готівкою в офісі'),
(5, 48000, '2023-04-15', 'Повна оплата', 'Успішно', 'TR23041501', 'Банківський переказ з Ощадбанку'),
(6, 50000, '2023-03-28', 'Повна оплата', 'Успішно', 'TR23032801', 'Оплата кредитною карткою American Express'),
(7, 49000, '2023-08-18', 'Повна оплата', 'Успішно', 'TR23081801', 'Банківський переказ з Укрсиббанку'),
(8, 18500, '2023-07-12', 'Повна оплата', 'Успішно', 'TR23071201', 'Оплата кредитною карткою Visa'),
(9, 49000, '2023-09-08', 'Повна оплата', 'Успішно', 'TR23090801', 'Банківський переказ з Райффайзен Банку'),
(10, 70000, '2023-04-22', 'Повна оплата', 'Успішно', 'TR23042201', 'Оплата кредитною карткою MasterCard'),

-- Оплати іноземних клієнтів
(21, 15000, '2023-06-12', 'Повна оплата', 'Успішно', 'TR23061201', 'Оплата кредитною карткою Visa'),
(22, 5800, '2023-04-17', 'Повна оплата', 'Успішно', 'TR23041701', 'Банківський переказ з Bank of America'),
(23, 10500, '2023-03-22', 'Повна оплата', 'Успішно', 'TR23032201', 'Оплата кредитною карткою MasterCard'),
(24, 24000, '2023-05-28', 'Повна оплата', 'Успішно', 'TR23052801', 'Банківський переказ з Deutsche Bank'),
(25, 19000, '2023-04-05', 'Повна оплата', 'Успішно', 'TR23040501', 'Оплата кредитною карткою American Express'),

-- Попередні платежі (завдатки) для бронювань зі статусом "Підтверджено"
(11, 20000, '2023-05-08', 'Завдаток', 'Успішно', 'TR23050801', 'Завдаток 30% від загальної вартості'),
(12, 16000, '2023-08-28', 'Завдаток', 'Успішно', 'TR23082801', 'Завдаток 30% від загальної вартості'),
(13, 25000, '2023-01-18', 'Завдаток', 'Успішно', 'TR23011801', 'Завдаток 30% від загальної вартості'),
(14, 100000, '2023-02-03', 'Завдаток', 'Успішно', 'TR23020301', 'Завдаток 30% від загальної вартості'),
(15, 30000, '2023-07-20', 'Завдаток', 'Успішно', 'TR23072001', 'Завдаток 30% від загальної вартості'),

-- Платежі для скасованих бронювань (з поверненням коштів)
(16, 10000, '2023-09-26', 'Завдаток', 'Повернуто', 'TR23092601', 'Завдаток 30% повернуто'),
(17, 12000, '2023-05-11', 'Завдаток', 'Повернуто', 'TR23051101', 'Завдаток 30% повернуто'),
(18, 35000, '2023-03-16', 'Завдаток', 'Повернуто', 'TR23031601', 'Завдаток 30% повернуто'),
(19, 15000, '2023-06-21', 'Завдаток', 'Повернуто', 'TR23062101', 'Завдаток 30% повернуто'),
(20, 25000, '2023-04-26', 'Завдаток', 'Повернуто', 'TR23042601', 'Завдаток 30% повернуто'),

-- Повторні та додаткові платежі
(1, 2000, '2023-03-18', 'Додаткові послуги', 'Успішно', 'TR23031802', 'Оплата за додатковий трансфер'),
(3, 3500, '2023-05-25', 'Додаткові послуги', 'Успішно', 'TR23052502', 'Оплата за додаткову екскурсію'),
(6, 4500, '2023-03-30', 'Додаткові послуги', 'Успішно', 'TR23033002', 'Оплата за VIP-екскурсію'),
(9, 6000, '2023-09-12', 'Додаткові послуги', 'Успішно', 'TR23091202', 'Оплата за додаткові дайвінг-сесії'),
(10, 5500, '2023-04-25', 'Додаткові послуги', 'Успішно', 'TR23042502', 'Оплата за романтичну вечерю');

-- Оновлення послідовності ID
SELECT setval('платежі_id_seq', (SELECT MAX(id) FROM платежі));

-- Інформаційне повідомлення про успішне завершення імпорту
DO $$
BEGIN
    RAISE NOTICE 'Дані про платежі успішно імпортовано. Загальна кількість записів: %', (SELECT COUNT(*) FROM платежі);
END $$; 