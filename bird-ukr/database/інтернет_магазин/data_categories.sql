-- Дані для таблиці категорій для бази даних "Інтернет-магазин"
-- Кодування: UTF-8

-- ==================================
-- Очищення таблиці перед імпортом
-- ==================================

TRUNCATE TABLE категорії CASCADE;

-- Скидання лічильника автоінкременту
ALTER SEQUENCE категорії_ід_seq RESTART WITH 1;

-- ==================================
-- Імпорт даних про основні категорії
-- ==================================

-- Головні категорії (батьківська_категорія_ід = NULL)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Електроніка', 'Електронні пристрої та аксесуари', NULL, 'https://example.com/images/electronics.jpg', 1, TRUE),
('Комп''ютери', 'Комп''ютери, ноутбуки та комплектуючі', NULL, 'https://example.com/images/computers.jpg', 2, TRUE),
('Побутова техніка', 'Побутова техніка для дому', NULL, 'https://example.com/images/home-appliances.jpg', 3, TRUE),
('Одяг', 'Чоловічий, жіночий та дитячий одяг', NULL, 'https://example.com/images/clothing.jpg', 4, TRUE),
('Взуття', 'Чоловіче, жіноче та дитяче взуття', NULL, 'https://example.com/images/footwear.jpg', 5, TRUE),
('Спорт і відпочинок', 'Товари для спорту та активного відпочинку', NULL, 'https://example.com/images/sports.jpg', 6, TRUE),
('Дім і сад', 'Товари для дому та саду', NULL, 'https://example.com/images/home-garden.jpg', 7, TRUE),
('Краса і здоров''я', 'Товари для краси та здоров''я', NULL, 'https://example.com/images/beauty-health.jpg', 8, TRUE),
('Дитячі товари', 'Товари для дітей та немовлят', NULL, 'https://example.com/images/kids.jpg', 9, TRUE),
('Продукти харчування', 'Продукти та напої', NULL, 'https://example.com/images/food.jpg', 10, TRUE);

-- ==================================
-- Імпорт даних про підкатегорії електроніки
-- ==================================

-- Підкатегорії для "Електроніка" (ід = 1)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Смартфони', 'Мобільні телефони та смартфони', 1, 'https://example.com/images/smartphones.jpg', 1, TRUE),
('Планшети', 'Планшетні комп''ютери', 1, 'https://example.com/images/tablets.jpg', 2, TRUE),
('Аудіотехніка', 'Навушники, колонки та аудіосистеми', 1, 'https://example.com/images/audio.jpg', 3, TRUE),
('Фото та відео', 'Фотоапарати, відеокамери та аксесуари', 1, 'https://example.com/images/photo-video.jpg', 4, TRUE),
('Телевізори', 'Телевізори та аксесуари', 1, 'https://example.com/images/tvs.jpg', 5, TRUE),
('Ігрові консолі', 'Ігрові приставки та аксесуари', 1, 'https://example.com/images/gaming.jpg', 6, TRUE),
('Носії інформації', 'Карти пам''яті, флеш-накопичувачі, жорсткі диски', 1, 'https://example.com/images/storage.jpg', 7, TRUE),
('Аксесуари для електроніки', 'Чохли, захисні плівки, зарядні пристрої', 1, 'https://example.com/images/accessories.jpg', 8, TRUE);

-- ==================================
-- Імпорт даних про підкатегорії комп'ютерів
-- ==================================

-- Підкатегорії для "Комп'ютери" (ід = 2)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Ноутбуки', 'Портативні комп''ютери різних брендів', 2, 'https://example.com/images/laptops.jpg', 1, TRUE),
('Настільні комп''ютери', 'Готові комп''ютерні системи', 2, 'https://example.com/images/desktops.jpg', 2, TRUE),
('Монітори', 'Комп''ютерні монітори різних розмірів', 2, 'https://example.com/images/monitors.jpg', 3, TRUE),
('Комплектуючі', 'Процесори, материнські плати, відеокарти та інше', 2, 'https://example.com/images/components.jpg', 4, TRUE),
('Периферія', 'Клавіатури, миші, колонки, веб-камери', 2, 'https://example.com/images/peripherals.jpg', 5, TRUE),
('Мережеве обладнання', 'Роутери, модеми, комутатори', 2, 'https://example.com/images/networking.jpg', 6, TRUE),
('Програмне забезпечення', 'Операційні системи, офісні програми, антивіруси', 2, 'https://example.com/images/software.jpg', 7, TRUE);

-- ==================================
-- Імпорт даних про підкатегорії побутової техніки
-- ==================================

-- Підкатегорії для "Побутова техніка" (ід = 3)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Велика побутова техніка', 'Холодильники, пральні машини, плити', 3, 'https://example.com/images/large-appliances.jpg', 1, TRUE),
('Кухонна техніка', 'Мікрохвильовки, блендери, кавоварки', 3, 'https://example.com/images/kitchen-appliances.jpg', 2, TRUE),
('Кліматична техніка', 'Кондиціонери, обігрівачі, вентилятори', 3, 'https://example.com/images/climate.jpg', 3, TRUE),
('Техніка для прибирання', 'Пилососи, пароочисники, мийки високого тиску', 3, 'https://example.com/images/cleaning.jpg', 4, TRUE),
('Техніка для догляду за собою', 'Фени, плойки, електробритви', 3, 'https://example.com/images/personal-care.jpg', 5, TRUE);

-- ==================================
-- Імпорт даних про підкатегорії одягу
-- ==================================

-- Підкатегорії для "Одяг" (ід = 4)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Чоловічий одяг', 'Футболки, сорочки, штани, куртки для чоловіків', 4, 'https://example.com/images/mens-clothing.jpg', 1, TRUE),
('Жіночий одяг', 'Сукні, блузи, спідниці, штани для жінок', 4, 'https://example.com/images/womens-clothing.jpg', 2, TRUE),
('Дитячий одяг', 'Одяг для дітей різного віку', 4, 'https://example.com/images/kids-clothing.jpg', 3, TRUE),
('Спортивний одяг', 'Одяг для спорту та активного відпочинку', 4, 'https://example.com/images/sports-clothing.jpg', 4, TRUE),
('Нижня білизна', 'Чоловіча та жіноча нижня білизна', 4, 'https://example.com/images/underwear.jpg', 5, TRUE),
('Аксесуари для одягу', 'Шарфи, рукавички, головні убори', 4, 'https://example.com/images/clothing-accessories.jpg', 6, TRUE);

-- ==================================
-- Імпорт даних про підкатегорії третього рівня
-- ==================================

-- Підкатегорії для "Смартфони" (ід = 11)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Apple iPhone', 'Смартфони від компанії Apple', 11, 'https://example.com/images/iphone.jpg', 1, TRUE),
('Samsung Galaxy', 'Смартфони серії Galaxy від Samsung', 11, 'https://example.com/images/samsung.jpg', 2, TRUE),
('Xiaomi', 'Смартфони від компанії Xiaomi', 11, 'https://example.com/images/xiaomi.jpg', 3, TRUE),
('Huawei', 'Смартфони від компанії Huawei', 11, 'https://example.com/images/huawei.jpg', 4, TRUE),
('Google Pixel', 'Смартфони від Google', 11, 'https://example.com/images/pixel.jpg', 5, TRUE),
('Інші бренди', 'Смартфони інших виробників', 11, 'https://example.com/images/other-smartphones.jpg', 6, TRUE);

-- Підкатегорії для "Комплектуючі" (ід = 20)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Процесори', 'CPU для настільних комп''ютерів і ноутбуків', 20, 'https://example.com/images/processors.jpg', 1, TRUE),
('Материнські плати', 'Материнські плати різних форм-факторів і виробників', 20, 'https://example.com/images/motherboards.jpg', 2, TRUE),
('Відеокарти', 'Графічні адаптери для комп''ютерів', 20, 'https://example.com/images/videocards.jpg', 3, TRUE),
('Оперативна пам''ять', 'Модулі пам''яті RAM різних типів', 20, 'https://example.com/images/ram.jpg', 4, TRUE),
('Накопичувачі', 'SSD, HDD та інші пристрої зберігання даних', 20, 'https://example.com/images/storage-devices.jpg', 5, TRUE),
('Корпуси', 'Комп''ютерні корпуси різних форм-факторів', 20, 'https://example.com/images/cases.jpg', 6, TRUE),
('Блоки живлення', 'Блоки живлення для комп''ютерів', 20, 'https://example.com/images/power-supplies.jpg', 7, TRUE),
('Системи охолодження', 'Кулери, радіатори та системи рідинного охолодження', 20, 'https://example.com/images/cooling.jpg', 8, TRUE);

-- Підкатегорії для "Кухонна техніка" (ід = 26)
INSERT INTO категорії (назва, опис, батьківська_категорія_ід, зображення_url, порядок_сортування, активна) VALUES
('Мікрохвильові печі', 'Мікрохвильові печі різних типів і розмірів', 26, 'https://example.com/images/microwaves.jpg', 1, TRUE),
('Кавоварки та кавомашини', 'Пристрої для приготування кави', 26, 'https://example.com/images/coffee-makers.jpg', 2, TRUE),
('Блендери та міксери', 'Пристрої для змішування та подрібнення продуктів', 26, 'https://example.com/images/blenders.jpg', 3, TRUE),
('Тостери', 'Пристрої для приготування тостів', 26, 'https://example.com/images/toasters.jpg', 4, TRUE),
('Мультиварки', 'Багатофункціональні пристрої для приготування їжі', 26, 'https://example.com/images/multicookers.jpg', 5, TRUE),
('Електрочайники', 'Пристрої для кип''ятіння води', 26, 'https://example.com/images/kettles.jpg', 6, TRUE),
('М''ясорубки', 'Пристрої для подрібнення м''яса', 26, 'https://example.com/images/meat-grinders.jpg', 7, TRUE),
('Хлібопічки', 'Пристрої для випікання хліба', 26, 'https://example.com/images/bread-makers.jpg', 8, TRUE);

-- ==================================
-- Встановлення правильного значення для послідовності
-- ==================================

-- Оновлення послідовності для уникнення конфліктів при подальшому додаванні
SELECT setval('категорії_ід_seq', (SELECT MAX(ід) FROM категорії), true); 