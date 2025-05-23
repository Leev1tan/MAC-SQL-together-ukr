-- Data for Library (бібліотека) database
-- Created for Ukrainian Text-to-SQL dataset

-- Languages (мови)
INSERT INTO мови (назва, код, оригінальна_назва)
VALUES 
    ('Українська', 'uk', 'Українська'),
    ('Англійська', 'en', 'English'),
    ('Французька', 'fr', 'Français'),
    ('Німецька', 'de', 'Deutsch'),
    ('Польська', 'pl', 'Polski'),
    ('Іспанська', 'es', 'Español'),
    ('Італійська', 'it', 'Italiano'),
    ('Російська', 'ru', 'Русский'),
    ('Японська', 'ja', '日本語'),
    ('Китайська', 'zh', '中文');

-- Publishers (видавництва)
INSERT INTO видавництва (назва, країна, місто, рік_заснування, електронна_пошта, телефон, веб_сайт)
VALUES 
    ('А-БА-БА-ГА-ЛА-МА-ГА', 'Україна', 'Київ', 1992, 'ababa@ukr.net', '+380441234567', 'www.ababahalamaha.com.ua'),
    ('Видавництво Старого Лева', 'Україна', 'Львів', 2001, 'info@starlev.com.ua', '+380321234567', 'www.starlev.com.ua'),
    ('Фоліо', 'Україна', 'Харків', 1991, 'info@folio.com.ua', '+380571234567', 'www.folio.com.ua'),
    ('Наш Формат', 'Україна', 'Київ', 2006, 'info@nashformat.ua', '+380441234568', 'www.nashformat.ua'),
    ('Клуб Сімейного Дозвілля', 'Україна', 'Харків', 2000, 'info@bookclub.ua', '+380571234568', 'www.bookclub.ua'),
    ('Віват', 'Україна', 'Харків', 2013, 'info@vivat.com.ua', '+380571234569', 'www.vivat.com.ua'),
    ('Ранок', 'Україна', 'Харків', 1997, 'info@ranok.com.ua', '+380571234570', 'www.ranok.com.ua'),
    ('Основи', 'Україна', 'Київ', 1992, 'info@osnovy.com.ua', '+380441234569', 'www.osnovy.com.ua'),
    ('Кальварія', 'Україна', 'Львів', 1998, 'info@calvaria.org', '+380321234568', 'www.calvaria.org'),
    ('Темпора', 'Україна', 'Київ', 1997, 'info@tempora.com.ua', '+380441234570', 'www.tempora.com.ua');

-- Genres (жанри)
INSERT INTO жанри (назва, опис)
VALUES 
    ('Роман', 'Великий за обсягом, складний за будовою прозовий твір, у якому широко охоплені життєві події, глибоко розкривається історія формування характерів багатьох персонажів.'),
    ('Детектив', 'Літературний твір або кінофільм, присвячений розкриттю заплутаної таємниці, пов''язаної зі злочином.'),
    ('Фантастика', 'Жанр художньої літератури, в якому за допомогою додавання фантастичних елементів створюється особливий вигаданий світ.'),
    ('Наукова фантастика', 'Різновид фантастики, що описує вигадані технології та наукові відкриття, контакт з нелюдським розумом, подорожі в часі тощо.'),
    ('Фентезі', 'Піджанр фантастичної літератури, заснований на використанні міфологічних і казкових мотивів.'),
    ('Пригоди', 'Характеризується напруженістю сюжету, різкими поворотами подій, несподіваністю розв''язок.'),
    ('Історичний роман', 'Роман, дія якого відбувається в минулому і який використовує реальні історичні події та особистості.'),
    ('Поезія', 'Художньо-образна словесна творчість, особливістю якої є ритмічна і звукова організація мовлення.'),
    ('Наукова література', 'Різновид літератури, що охоплює наукові твори, які містять відомості про досягнення науки.'),
    ('Біографія', 'Опис життя людини, створений іншими людьми або нею самою (автобіографія).'),
    ('Мемуари', 'Жанр документальної літератури, запис спогадів історичних осіб або очевидців про події, учасниками яких вони були.'),
    ('Дитяча література', 'Література, створена спеціально для дітей різного віку.'),
    ('Підліткова література', 'Література, орієнтована на підлітків віком від 12 до 18 років.'),
    ('Драма', 'Літературний твір, побудований у формі діалогу дійових осіб без авторської мови і призначений для виконання на сцені.'),
    ('Комедія', 'Вид драматичного твору, в якому зображуються комічні життєві положення і характери.'),
    ('Трагедія', 'Драматичний твір, у якому зображується гостра безкомпромісна боротьба героя з непереборними обставинами.'),
    ('Новела', 'Невеликий за обсягом прозовий епічний твір про незвичайну життєву подію з несподіваним фіналом.'),
    ('Оповідання', 'Невеликий прозовий твір, сюжет якого заснований на певному епізоді з життя одного або кількох персонажів.'),
    ('Казка', 'Розповідний народнопоетичний або авторський художній твір про вигадані події.'),
    ('Нехудожня література', 'Література, що містить переважно фактичну, а не вигадану інформацію.');

-- Insert child genres with parent references
INSERT INTO жанри (назва, батьківський_жанр_ід, опис)
VALUES 
    ('Любовний роман', 1, 'Художній твір, в якому основою сюжету є історія любовних відносин.'),
    ('Психологічний роман', 1, 'Роман, в якому аналізуються внутрішні переживання і мотиви поведінки героїв.'),
    ('Кримінальний детектив', 2, 'Детективний твір, що зосереджується на розкритті та розслідуванні злочину.'),
    ('Містичний детектив', 2, 'Детективний твір з елементами містики та надприродного.'),
    ('Космічна фантастика', 4, 'Піджанр наукової фантастики, дія якого відбувається в космосі.'),
    ('Кіберпанк', 4, 'Піджанр наукової фантастики, що зображує світ майбутнього з високим рівнем технологічного розвитку і низьким рівнем соціального благополуччя.'),
    ('Постапокаліптика', 4, 'Піджанр фантастики, що описує життя людей після глобальної катастрофи.'),
    ('Епічне фентезі', 5, 'Піджанр фентезі з масштабним сюжетом, що охоплює цілі вигадані світи.'),
    ('Міське фентезі', 5, 'Піджанр фентезі, дія якого відбувається в сучасному місті з елементами магії.'),
    ('Поетична драма', 8, 'Драматичний твір, написаний у віршованій формі.');

-- Authors (автори)
INSERT INTO автори (прізвище, імя, по_батькові, дата_народження, країна, коротка_біографія)
VALUES 
    ('Шевченко', 'Тарас', 'Григорович', '1814-03-09', 'Україна', 'Український поет, письменник, художник, громадський та політичний діяч. Національний герой України.'),
    ('Франко', 'Іван', 'Якович', '1856-08-27', 'Україна', 'Український письменник, поет, публіцист, перекладач, учений, громадський і політичний діяч.'),
    ('Українка', 'Леся', NULL, '1871-02-25', 'Україна', 'Українська письменниця, перекладачка, фольклористка, культурна діячка. Справжнє ім''я - Лариса Петрівна Косач-Квітка.'),
    ('Коцюбинський', 'Михайло', 'Михайлович', '1864-09-17', 'Україна', 'Український письменник, громадський діяч, голова "Просвіти" в Чернігові.'),
    ('Жадан', 'Сергій', 'Вікторович', '1974-08-23', 'Україна', 'Український поет, прозаїк, перекладач, громадський активіст.'),
    ('Роздобудько', 'Ірен', NULL, '1962-11-03', 'Україна', 'Українська письменниця, журналістка, сценаристка. Авторка романів, повістей, оповідань.'),
    ('Забужко', 'Оксана', 'Стефанівна', '1960-09-19', 'Україна', 'Українська письменниця, поетеса, есеїстка, публіцистка, науковиця, перекладачка.'),
    ('Дашвар', 'Люко', NULL, '1957-10-01', 'Україна', 'Українська письменниця, сценаристка. Справжнє ім''я - Ірина Іванівна Чернова.'),
    ('Кідрук', 'Макс', NULL, '1984-04-01', 'Україна', 'Український письменник, мандрівник. Автор науково-популярних книг та технотрилерів.'),
    ('Кокотюха', 'Андрій', 'Анатолійович', '1970-10-17', 'Україна', 'Український письменник, сценарист, журналіст.'),
    ('Шкляр', 'Василь', 'Миколайович', '1951-06-10', 'Україна', 'Український письменник, політичний діяч.'),
    ('Андрухович', 'Юрій', 'Ігорович', '1960-03-13', 'Україна', 'Український поет, прозаїк, перекладач, есеїст.'),
    ('Іздрик', 'Юрій', 'Романович', '1962-08-16', 'Україна', 'Український прозаїк, поет, художник, музикант. Один із представників станіславського феномену.'),
    ('Гербіш', 'Надійка', NULL, '1987-01-14', 'Україна', 'Українська письменниця, перекладачка, журналістка. Авторка низки книжок для підлітків.'),
    ('Положій', 'Євген', 'Вікторович', '1968-05-05', 'Україна', 'Український письменник, журналіст. Учасник революційних подій в Україні.'),
    ('Матіос', 'Марія', 'Василівна', '1959-12-19', 'Україна', 'Українська письменниця, публіцистка, громадсько-політична діячка.'),
    ('Малярчук', 'Таня', NULL, '1983-05-07', 'Україна', 'Українська письменниця, перекладачка. Живе та працює в Австрії.'),
    ('Дереш', 'Любко', NULL, '1984-07-03', 'Україна', 'Український письменник. Пише українською та англійською мовами.'),
    ('Винничук', 'Юрій', 'Павлович', '1952-03-18', 'Україна', 'Український письменник, журналіст, редактор.'),
    ('Карпа', 'Ірена', NULL, '1980-12-08', 'Україна', 'Українська письменниця, журналістка, співачка, сценаристка.'),
    ('Роулінґ', 'Джоан', 'Кетлін', '1965-07-31', 'Велика Британія', 'Британська письменниця, філантропка, кіно- і телепродюсерка. Авторка серії романів про Гаррі Поттера.'),
    ('Кінг', 'Стівен', 'Едвін', '1947-09-21', 'США', 'Американський письменник, автор багатьох бестселерів, написаних у жанрах жахів, фентезі, містики, трилера, поєднуючи їх з реалізмом.'),
    ('Гемінґвей', 'Ернест', 'Міллер', '1899-07-21', 'США', 'Американський письменник і журналіст, лауреат Нобелівської премії з літератури 1954 року.'),
    ('Ремарк', 'Еріх', 'Марія', '1898-06-22', 'Німеччина', 'Німецький письменник XX століття, представник «втраченого покоління».'),
    ('Тартт', 'Донна', NULL, '1963-12-23', 'США', 'Американська письменниця, авторка бестселера «Щиголь», лауреат Пулітцерівської премії.'),
    ('Сапковський', 'Анджей', NULL, '1948-06-21', 'Польща', 'Польський письменник-фантаст, автор саги про «Відьмака».');

-- Create categories for readers (категорії_читачів)
INSERT INTO категорії_читачів (назва, опис, макс_книг, термін_днів, вартість_обслуговування, знижка_відсоток)
VALUES 
    ('Стандартна', 'Базова категорія для всіх нових читачів', 5, 21, 50.00, NULL),
    ('Студентська', 'Для студентів вищих навчальних закладів', 7, 21, 25.00, NULL),
    ('Дитяча', 'Для дітей до 14 років', 3, 14, 0.00, NULL),
    ('Пенсійна', 'Для пенсіонерів', 5, 30, 10.00, NULL),
    ('Викладацька', 'Для викладачів та вчителів', 10, 30, 20.00, NULL),
    ('Наукова', 'Для наукових працівників та дослідників', 15, 45, 30.00, NULL),
    ('VIP', 'Преміум категорія з розширеними можливостями', 20, 60, 200.00, NULL);

-- Create positions (посади)
INSERT INTO посади (назва, опис, мінімальна_зарплата, максимальна_зарплата)
VALUES 
    ('Директор бібліотеки', 'Керівник бібліотеки', 20000.00, 30000.00),
    ('Заступник директора', 'Заступник керівника бібліотеки', 15000.00, 25000.00),
    ('Завідувач відділу', 'Керівник відділу бібліотеки', 12000.00, 18000.00),
    ('Головний бібліотекар', 'Старший спеціаліст з бібліотечної справи', 10000.00, 15000.00),
    ('Бібліотекар', 'Спеціаліст з обслуговування читачів та роботи з фондами', 8000.00, 12000.00),
    ('Бібліограф', 'Спеціаліст з бібліографії та каталогізації', 8500.00, 13000.00),
    ('Архіваріус', 'Спеціаліст з архівної справи', 8000.00, 12000.00),
    ('Реставратор', 'Спеціаліст з реставрації книг та документів', 9000.00, 14000.00),
    ('Системний адміністратор', 'Фахівець з інформаційних технологій', 12000.00, 20000.00),
    ('Адміністратор', 'Співробітник рецепції та адміністративної підтримки', 7500.00, 11000.00),
    ('Прибиральник', 'Працівник з прибирання приміщень', 6500.00, 8000.00),
    ('Охоронець', 'Співробітник служби безпеки', 7000.00, 10000.00); 