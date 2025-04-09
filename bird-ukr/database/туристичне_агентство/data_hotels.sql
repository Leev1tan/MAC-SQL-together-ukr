-- Дані про готелі для бази даних "Туристичне агентство"

-- Налаштування кодування
SET client_encoding = 'UTF8';

-- Очищення таблиці перед додаванням даних
TRUNCATE TABLE готелі CASCADE;

-- Додавання готелів
INSERT INTO готелі (назва, місто_id, адреса, опис, контактний_телефон, email, веб_сайт, зірок, зручності) VALUES
-- Готелі в Україні
-- Київ (id=1)
('Premier Palace Hotel', 1, 'бульвар Тараса Шевченка, 5-7', 'Розкішний 5-зірковий готель у самому серці Києва, з елегантними номерами та чудовою кухнею.', '+380442446911', 'info@premier-palace.com', 'www.premier-palace.com', 5, NULL),
('Hyatt Regency Kyiv', 1, 'вул. Алли Тарасової, 5', 'Сучасний 5-зірковий готель поблизу Софійського собору з панорамними видами на місто.', '+380444941234', 'kyiv.regency@hyatt.com', 'www.hyatt.com/kyiv', 5, NULL),
('Ibis Kyiv City Center', 1, 'бульвар Тараса Шевченка, 25', 'Сучасний 3-зірковий готель у центрі міста з комфортними номерами та доступними цінами.', '+380442876500', 'h7143@accor.com', 'www.ibis.com/kyiv', 3, NULL),

-- Львів (id=2)
('Leopolis Hotel', 2, 'вул. Театральна, 16', 'Розкішний бутік-готель у серці старого міста, який поєднує історичну атмосферу і сучасний комфорт.', '+380322956900', 'reception@leopolishotel.com', 'www.leopolishotel.com', 5, NULL),
('Hotel Atlas Deluxe', 2, 'вул. Городоцька, 45', 'Елегантний готель в історичній будівлі з вишуканим інтер''єром та зручним розташуванням.', '+380322426200', 'info@atlas-deluxe.com.ua', 'www.atlas-deluxe.com.ua', 4, NULL),
('Ibis Styles Lviv Center', 2, 'вул. Шухевича, 3', 'Яскравий та сучасний готель з креативним дизайном та комфортними номерами.', '+380322559500', 'h9709@accor.com', 'www.ibis.com/lviv', 3, NULL),

-- Одеса (id=3)
('Hotel Bristol', 3, 'вул. Пушкінська, 15', 'Історичний готель, побудований у 1899 році, з розкішним інтер''єром та відмінним сервісом.', '+380487965500', 'reception@bristol-hotel.com.ua', 'www.bristol-hotel.com.ua', 5, NULL),
('Mozart Hotel', 3, 'вул. Ланжеронівська, 13', 'Елегантний готель поблизу Оперного театру з затишними номерами та чудовою кухнею.', '+380487377444', 'info@mozart-hotel.com', 'www.mozart-hotel.com', 4, NULL),
('Black Sea Hotel', 3, 'вул. Рішельєвська, 59', 'Зручний готель у центрі Одеси з комфортними номерами та доступними цінами.', '+380487239090', 'bs.hotel@bs-hotel-group.com', 'www.bs-hotel-group.com', 3, NULL),

-- Готелі в Туреччині
-- Стамбул (id=49)
('Four Seasons Hotel Istanbul at Sultanahmet', 49, 'Tevkifhane Sokak No:1, Sultanahmet', 'Розкішний готель в історичній будівлі колишньої турецької в''язниці, неподалік від Блакитної мечеті та Айя-Софії.', '+902125188800', 'istanbul.sultanahmet@fourseasons.com', 'www.fourseasons.com/istanbul', 5, NULL),
('The Ritz-Carlton Istanbul', 49, 'Suzer Plaza, Askerocagi Cad. No:15', 'Елегантний готель з чудовим видом на Босфор та розкішним спа-центром.', '+902123344444', 'istanbul@ritzcarlton.com', 'www.ritzcarlton.com/istanbul', 5, NULL),
('Sura Hagia Sophia Hotel', 49, 'Divanyolu Cd. Alemdar Mh. Ticarethane Sk. No:10', 'Розташований у центрі історичного району з терасою та басейном, звідки відкривається чудовий вид на місто.', '+902125229900', 'info@surahotels.com', 'www.surahotels.com', 4, NULL),

-- Анталія (id=50)
('Rixos Premium Belek', 50, 'Ileribasi Mevkii Belek', 'Розкішний готель на березі моря з приватним пляжем, декількома басейнами та широким вибором розваг.', '+902423104100', 'belek@rixos.com', 'www.rixos.com/belek', 5, NULL),
('Maxx Royal Belek Golf Resort', 50, 'Iskele Mevkii, Belek', 'Ексклюзивний курорт з власним полем для гольфу, аквапарком та величезною територією.', '+902427105000', 'info@maxxroyal.com', 'www.maxxroyal.com', 5, NULL),
('Limak Atlantis Deluxe Hotel', 50, 'Kemeragzi Koyu, Lara', 'Готель з концепцією "все включено", розташований на пляжі Лара з великим аквапарком.', '+902423525454', 'info@limakhotels.com', 'www.limakhotels.com', 5, NULL),

-- Готелі в Єгипті
-- Шарм-ель-Шейх (id=62)
('Four Seasons Resort Sharm El Sheikh', 62, 'El Salam Road, Sharks Bay', 'Розкішний курорт на березі Червоного моря з приватним пляжем та кораловим рифом.', '+20693603555', 'reservations.sha@fourseasons.com', 'www.fourseasons.com/sharmelsheikh', 5, NULL),
('Rixos Sharm El Sheikh', 62, 'Nabq Bay', 'Готель з концепцією "ультра все включено" на власному пляжі з рифами.', '+20693710130', 'sharm@rixos.com', 'www.rixos.com/sharm', 5, NULL),
('Hilton Sharks Bay Resort', 62, 'Sharks Bay', 'Курорт у бухті Sharks Bay з різноманітними басейнами та водними видами спорту.', '+20693600130', 'sharksbay.reservations@hilton.com', 'www.hilton.com/sharksbay', 4, NULL),

-- Хургада (id=63)
('Steigenberger Al Dau Beach Hotel', 63, 'Yussif Affifi Road', 'Елегантний готель з приватним пляжем, полем для гольфу та яхт-клубом.', '+20653465400', 'reservation@steigenbergeraldaubeach.com', 'www.steigenbergeraldaubeach.com', 5, NULL),
('Sunrise Holidays Resort', 63, 'North Corniche Road', 'Готель тільки для дорослих з чудовим розташуванням на березі моря.', '+20653443850', 'info@sunrise-resorts.com', 'www.sunrise-resorts.com', 5, NULL),
('Jaz Aquamarine Resort', 63, 'Hurghada-Safaga Road', 'Величезний курорт з 18 басейнами, 3 аквапарками та власним пляжем.', '+20653461900', 'reservation@jazhotels.com', 'www.jazhotels.com', 5, NULL),

-- Готелі в Греції
-- Афіни (id=67)
('Grande Bretagne', 67, 'Constitution Square, Syntagma', 'Історичний готель у центрі Афін з видом на Акрополь та парламент.', '+302103330000', 'info@grandebretagne.gr', 'www.grandebretagne.gr', 5, NULL),
('Electra Palace Athens', 67, 'Navarchou Nikodimou Street, Plaka', 'Розкішний готель у районі Плака з басейном на даху та видом на Акрополь.', '+302103370000', 'reservations@electrahotels.gr', 'www.electrahotels.gr', 4, NULL),
('Amalia Hotel', 67, 'Amalias Avenue, Syntagma', 'Сучасний готель навпроти Національного саду і поруч з площею Синтагма.', '+302103237300', 'reservations@amaliahotels.gr', 'www.amaliahotels.gr', 4, NULL),

-- Санторіні (id=68)
('Canaves Oia Suites', 68, 'Main Street, Oia', 'Розкішний готель, вирізаний у скелі, з приголомшливим видом на кальдеру.', '+302286071844', 'info@canaves.com', 'www.canaves.com', 5, NULL),
('Andronis Luxury Suites', 68, 'Oia', 'Ексклюзивний бутік-готель з білосніжними номерами та приватними басейнами.', '+302286072041', 'info@andronis.com', 'www.andronis.com', 5, NULL),
('Santo Maris Oia', 68, 'Oia', 'Розкішний курорт з приватними басейнами та спа-центром з видом на знамениті заходи сонця.', '+302286600630', 'reservations@santomaris.gr', 'www.santomaris.gr', 5, NULL),

-- Готелі в Таїланді
-- Пхукет (id=74)
('Banyan Tree Phuket', 74, 'Laguna Phuket, Cherngtalay', 'Курорт класу люкс з віллами та приватними басейнами в лагуні Банг Тао.', '+6676372400', 'phuket@banyantree.com', 'www.banyantree.com/phuket', 5, NULL),
('Amanpuri', 74, 'Pansea Beach, Cherngtalay', 'Легендарний курорт на власному півострові з віллами в тайському стилі.', '+6676324333', 'amanpuri@aman.com', 'www.aman.com/amanpuri', 5, NULL),
('The Nai Harn', 74, 'Nai Harn Beach', 'Елегантний готель з видом на одну з найкрасивіших бухт Пхукета.', '+6677380200', 'reservations@thenaiharn.com', 'www.thenaiharn.com', 5, NULL),

-- Готелі в ОАЕ
-- Дубай (id=79)
('Burj Al Arab Jumeirah', 79, 'Jumeirah Beach Road', 'Один з найрозкішніших готелів світу, побудований у формі вітрила на штучному острові.', '+97143017777', 'baareservations@jumeirah.com', 'www.jumeirah.com/burjalarab', 5, NULL),
('Atlantis, The Palm', 79, 'Crescent Road, Palm Jumeirah', 'Знаменитий курорт на архіпелазі Пальма з власним аквапарком та підводним акваріумом.', '+97144260000', 'reservations@atlantisthepalm.com', 'www.atlantis.com/dubai', 5, NULL),
('JW Marriott Marquis Hotel Dubai', 79, 'Sheikh Zayed Road, Business Bay', 'Найвищий п''ятизірковий готель у світі з розкішними номерами та численними ресторанами.', '+97144140000', 'jwmarquis.dubai@marriott.com', 'www.marriott.com/dubai', 5, NULL),

-- Готелі на Мальдівах
-- Атол Арі (id=85)
('Conrad Maldives Rangali Island', 85, 'Rangali Island, South Ari Atoll', 'Розкішний курорт на двох островах з підводним рестораном та віллами на воді.', '+9606680629', 'mlehi.maldives@conradhotels.com', 'www.conradmaldives.com', 5, NULL),
('W Maldives', 85, 'Fesdu Island, North Ari Atoll', 'Стильний курорт з приватними басейнами та власним кораловим рифом.', '+9606743000', 'reservations.wmaldives@whotels.com', 'www.marriott.com/wmaldives', 5, NULL),
('Constance Moofushi', 85, 'Moofushi Island, South Ari Atoll', 'Курорт "все включено" на острові з білосніжним пляжем та чудовим домашнім рифом.', '+9606668800', 'reservation@constancehotels.com', 'www.constancehotels.com', 5, NULL);

-- Оновлення послідовності ID
SELECT setval('готелі_id_seq', (SELECT MAX(id) FROM готелі));

-- Інформаційне повідомлення про успішне завершення імпорту
DO $$
BEGIN
    RAISE NOTICE 'Дані про готелі успішно імпортовано. Загальна кількість записів: %', (SELECT COUNT(*) FROM готелі);
END $$; 