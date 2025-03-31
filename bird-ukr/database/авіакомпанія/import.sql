-- Скрипт для імпорту даних бази даних "Авіакомпанія"
-- Цей скрипт імпортує всі необхідні дані для функціонування бази даних

-- Очищення бази даних перед імпортом (якщо потрібно)
\echo 'Видалення існуючих даних з таблиць...'

DELETE FROM технічне_обслуговування CASCADE;
DELETE FROM надані_послуги CASCADE;
DELETE FROM рейси_персонал CASCADE;
DELETE FROM бронювання_пасажири CASCADE;
DELETE FROM бронювання CASCADE;
DELETE FROM рейси CASCADE;
DELETE FROM маршрути CASCADE;
DELETE FROM пасажири CASCADE;
DELETE FROM літаки CASCADE;
DELETE FROM аеропорти CASCADE;
DELETE FROM персонал CASCADE;
DELETE FROM послуги CASCADE;
DELETE FROM типи_літаків CASCADE;
DELETE FROM статуси_рейсів CASCADE;
DELETE FROM класи_обслуговування CASCADE;
DELETE FROM посади CASCADE;
DELETE FROM статуси_бронювань CASCADE;
DELETE FROM статуси_техобслуговування CASCADE;
DELETE FROM методи_оплати CASCADE;

-- Імпорт довідникових даних
\echo 'Імпорт довідникових даних...'

\i 'data_reference.sql'

-- Імпорт даних про персонал
\echo 'Імпорт даних про персонал...'

\i 'data_staff.sql'

-- Імпорт даних про літаки
\echo 'Імпорт даних про літаки...'

\i 'data_aircraft.sql'

-- Імпорт даних про аеропорти
\echo 'Імпорт даних про аеропорти...'

\i 'data_airports.sql'

-- Імпорт даних про маршрути
\echo 'Імпорт даних про маршрути...'

\i 'data_routes.sql'

-- Імпорт даних про рейси
\echo 'Імпорт даних про рейси...'

\i 'data_flights.sql'

-- Імпорт даних про пасажирів
\echo 'Імпорт даних про пасажирів...'

\i 'data_passengers.sql'

-- Імпорт даних про бронювання
\echo 'Імпорт даних про бронювання...'

\i 'data_bookings.sql'

-- Імпорт даних про послуги
\echo 'Імпорт даних про послуги...'

\i 'data_services.sql'

-- Імпорт даних про технічне обслуговування
\echo 'Імпорт даних про технічне обслуговування...'

\i 'data_maintenance.sql'

-- Перевірка коректності імпорту
\echo 'Перевірка коректності імпорту...'

SELECT COUNT(*) AS "Кількість посад" FROM посади;
SELECT COUNT(*) AS "Кількість типів літаків" FROM типи_літаків;
SELECT COUNT(*) AS "Кількість статусів рейсів" FROM статуси_рейсів;
SELECT COUNT(*) AS "Кількість класів обслуговування" FROM класи_обслуговування;
SELECT COUNT(*) AS "Кількість статусів бронювань" FROM статуси_бронювань;
SELECT COUNT(*) AS "Кількість методів оплати" FROM методи_оплати;
SELECT COUNT(*) AS "Кількість персоналу" FROM персонал;
SELECT COUNT(*) AS "Кількість аеропортів" FROM аеропорти;
SELECT COUNT(*) AS "Кількість літаків" FROM літаки;
SELECT COUNT(*) AS "Кількість маршрутів" FROM маршрути;
SELECT COUNT(*) AS "Кількість рейсів" FROM рейси;
SELECT COUNT(*) AS "Кількість пасажирів" FROM пасажири;
SELECT COUNT(*) AS "Кількість бронювань" FROM бронювання;
SELECT COUNT(*) AS "Кількість пасажирів у бронюваннях" FROM бронювання_пасажири;
SELECT COUNT(*) AS "Кількість персоналу на рейсах" FROM рейси_персонал;
SELECT COUNT(*) AS "Кількість послуг" FROM послуги;
SELECT COUNT(*) AS "Кількість наданих послуг" FROM надані_послуги;
SELECT COUNT(*) AS "Кількість технічних обслуговувань" FROM технічне_обслуговування;

\echo 'Імпорт даних завершено успішно!' 