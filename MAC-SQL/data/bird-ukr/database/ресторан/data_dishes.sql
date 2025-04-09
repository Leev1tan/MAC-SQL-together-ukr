-- Дані про страви для бази даних "Ресторан"
-- Кодування: UTF-8

-- =============================================
-- Вставка даних про страви
-- =============================================

-- Очищення даних з таблиці
DELETE FROM страви;

-- Define the columns matching the schema, excluding SERIAL id and columns with reliable defaults (дата_додавання, дата_оновлення)
-- INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES

-- Холодні закуски (категорія 10)
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Карпачо з яловичини', 'Тонкі скибочки маринованої яловичини з пармезаном та руколою', 10, 220.00, 150, 15, NULL, FALSE, FALSE, FALSE, 'dishes/beef_carpaccio.jpg', 0, TRUE, NULL),
('Тартар з лосося', 'Свіжий лосось з авокадо, каперсами та цитрусовою заправкою', 10, 250.00, 130, 20, NULL, FALSE, FALSE, TRUE, 'dishes/salmon_tartare.jpg', 0, TRUE, NULL),
('Асорті сирів', 'Вибір твердих та м''яких сирів з медом, горіхами та крекерами', 10, 320.00, 250, 10, NULL, TRUE, FALSE, FALSE, 'dishes/cheese_plate.jpg', 0, TRUE, NULL),
('М''ясне асорті', 'Нарізка в''ялених та копчених м''ясних делікатесів', 10, 290.00, 270, 15, NULL, FALSE, FALSE, TRUE, 'dishes/meat_assortment.jpg', 0, TRUE, NULL);

-- Гарячі закуски (категорія 11)
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Креветки в часниковому соусі', 'Тигрові креветки, обсмажені з часником та петрушкою', 11, 270.00, 180, 20, NULL, FALSE, FALSE, TRUE, 'dishes/garlic_shrimp.jpg', 0, TRUE, NULL),
('Смажений сир', 'Панірований сир камамбер з журавлинним соусом', 11, 190.00, 200, 15, NULL, TRUE, FALSE, FALSE, 'dishes/fried_cheese.jpg', 0, TRUE, NULL),
('Кальмари фрі', 'Хрусткі кільця кальмара з лимонним айолі', 11, 210.00, 170, 18, NULL, FALSE, FALSE, FALSE, 'dishes/calamari.jpg', 0, TRUE, NULL),
('Запечені гриби', 'Печериці, фаршировані сиром, часником та зеленню', 11, 180.00, 190, 25, NULL, TRUE, FALSE, TRUE, 'dishes/stuffed_mushrooms.jpg', 0, TRUE, NULL);

-- Супи (категорії 14-17)
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Грибний крем-суп', 'Оксамитовий крем-суп з білих грибів з трюфельною олією', 14, 160.00, 300, 20, NULL, TRUE, FALSE, TRUE, 'dishes/mushroom_soup.jpg', 0, TRUE, NULL),
('Курячий бульйон', 'Прозорий курячий бульйон з локшиною та овочами', 15, 130.00, 350, 25, NULL, FALSE, FALSE, FALSE, 'dishes/chicken_soup.jpg', 0, TRUE, NULL),
('Борщ український', 'Традиційний український борщ зі сметаною та пампушками з часником', 16, 150.00, 400, 30, NULL, FALSE, FALSE, FALSE, 'dishes/borsch.jpg', 0, TRUE, NULL),
('Гаспачо', 'Холодний суп з томатів та свіжих овочів', 17, 140.00, 280, 15, NULL, TRUE, FALSE, TRUE, 'dishes/gazpacho.jpg', 0, TRUE, NULL); -- Гаспачо is gluten-free

-- Салати (категорії 18-20)
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Грецький салат', 'Свіжі овочі з оливками та сиром фета', 18, 170.00, 250, 15, NULL, TRUE, FALSE, TRUE, 'dishes/greek_salad.jpg', 0, TRUE, NULL), -- Greek salad is gluten-free
('Цезар з куркою', 'Салат романо з куркою гриль, пармезаном та соусом цезар', 19, 210.00, 270, 20, NULL, FALSE, FALSE, FALSE, 'dishes/caesar_salad.jpg', 0, TRUE, NULL), -- Contains croutons, not gluten-free
('Салат з тунцем', 'Мікс салатів з тунцем, яйцем та свіжими овочами', 19, 220.00, 260, 18, NULL, FALSE, FALSE, TRUE, 'dishes/tuna_salad.jpg', 0, TRUE, NULL), -- Tuna salad usually gluten-free
('Теплий салат з телятиною', 'Теплий салат з смаженою телятиною та овочами гриль', 20, 240.00, 280, 25, NULL, FALSE, FALSE, TRUE, 'dishes/warm_beef_salad.jpg', 0, TRUE, NULL); -- Assumed gluten-free

-- Основні страви (категорії 21-25)
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Стейк рібай', 'Соковитий стейк з яловичини рібай з соусом з зеленого перцю', 21, 390.00, 300, 25, NULL, FALSE, FALSE, TRUE, 'dishes/ribeye_steak.jpg', 0, TRUE, NULL), -- Steak is gluten-free
('Курка по-київськи', 'Традиційний котлет по-київськи з вершковим маслом та зеленню', 21, 240.00, 280, 30, NULL, FALSE, FALSE, FALSE, 'dishes/chicken_kyiv.jpg', 0, TRUE, NULL), -- Breaded, not gluten-free
('Лосось з овочами', 'Філе лосося на грилі з сезонними овочами та лимонним соусом', 22, 320.00, 320, 25, NULL, FALSE, FALSE, TRUE, 'dishes/grilled_salmon.jpg', 0, TRUE, NULL), -- Grilled salmon is gluten-free
('Дорадо запечена', 'Ціла риба дорадо, запечена з лимоном та травами', 22, 340.00, 350, 30, NULL, FALSE, FALSE, TRUE, 'dishes/dorado.jpg', 0, TRUE, NULL), -- Baked fish is gluten-free
('Різото з грибами', 'Кремове різото з білими грибами та пармезаном', 23, 230.00, 300, 25, NULL, TRUE, FALSE, TRUE, 'dishes/mushroom_risotto.jpg', 0, TRUE, NULL), -- Risotto is typically gluten-free
('Овочі гриль', 'Асорті сезонних овочів, приготованих на грилі', 24, 180.00, 250, 20, NULL, TRUE, FALSE, TRUE, 'dishes/grilled_vegetables.jpg', 0, TRUE, NULL), -- Grilled vegetables are gluten-free
('Качина грудка з вишневим соусом', 'Соковита качина грудка з карамелізованими фруктами та вишневим соусом', 25, 350.00, 270, 35, NULL, FALSE, FALSE, TRUE, 'dishes/duck_breast.jpg', 0, TRUE, NULL); -- Assumed gluten-free, check sauce

-- Піца (категорії 26-28)
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Маргарита', 'Класична піца з томатним соусом, моцарелою та базиліком', 26, 170.00, 400, 20, NULL, TRUE, FALSE, FALSE, 'dishes/margherita.jpg', 0, TRUE, NULL), -- Pizza has gluten crust
('Пепероні', 'Піца з томатним соусом, моцарелою та пікантною салямі', 26, 190.00, 420, 20, NULL, FALSE, TRUE, FALSE, 'dishes/pepperoni.jpg', 0, TRUE, NULL), -- Pizza has gluten crust
('Чотири сири', 'Біла піца з моцарелою, горгонзолою, пармезаном та рікотою', 27, 210.00, 430, 20, NULL, TRUE, FALSE, FALSE, 'dishes/four_cheese.jpg', 0, TRUE, NULL), -- Pizza has gluten crust
('Піца від шефа', 'Фірмова піца з прошуто, руколою, пармезаном та трюфельною олією', 28, 250.00, 450, 25, NULL, FALSE, FALSE, FALSE, 'dishes/chef_pizza.jpg', 0, TRUE, NULL); -- Pizza has gluten crust

-- Десерти (категорії 35-38)
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Тірамісу', 'Класичний італійський десерт з маскарпоне та кавою', 35, 160.00, 180, 15, NULL, TRUE, FALSE, FALSE, 'dishes/tiramisu.jpg', 0, TRUE, NULL), -- Contains ladyfingers (gluten)
('Чізкейк', 'Ніжний чізкейк з ягідним соусом', 35, 170.00, 200, 15, NULL, TRUE, FALSE, FALSE, 'dishes/cheesecake.jpg', 0, TRUE, NULL), -- Typically has gluten crust
('Шоколадний фондан', 'Шоколадний кекс з рідкою серединкою та кулькою морозива', 35, 180.00, 150, 20, NULL, TRUE, FALSE, FALSE, 'dishes/fondant.jpg', 0, TRUE, NULL), -- Cake contains flour (gluten)
('Сорбет лимонний', 'Освіжаючий сорбет з лимона та лайма', 36, 120.00, 120, 10, NULL, TRUE, FALSE, TRUE, 'dishes/sorbet.jpg', 0, TRUE, NULL), -- Sorbet is gluten-free
('Фруктовий салат', 'Свіжі сезонні фрукти з м''ятою та медом', 37, 150.00, 250, 15, NULL, TRUE, FALSE, TRUE, 'dishes/fruit_salad.jpg', 0, TRUE, NULL), -- Fruit salad is gluten-free
('Налисники з сиром', 'Традиційні українські налисники з солодким сиром та родзинками', 38, 140.00, 200, 20, NULL, TRUE, FALSE, FALSE, 'dishes/nalysnyky.jpg', 0, TRUE, NULL); -- Nalysnyky (crepes) contain flour (gluten)

-- Напої (категорії 39-42)
-- Note: Most drinks are naturally gluten-free and vegetarian unless specified (e.g., beer). Calories, prep time etc. might vary.
INSERT INTO страви (назва, опис, категорія_ід, ціна, вага_грам, час_приготування_хвилин, калорійність, вегетаріанська, гостра, безглютенова, зображення_url, порядок_в_меню, активна, примітки) VALUES
('Фреш апельсиновий', 'Свіжовичавлений сік з апельсинів', 39, 90.00, 250, 5, NULL, TRUE, FALSE, TRUE, 'dishes/orange_juice.jpg', 0, TRUE, NULL),
('Лимонад домашній', 'Освіжаючий домашній лимонад з м''ятою та лаймом', 39, 80.00, 300, 10, NULL, TRUE, FALSE, TRUE, 'dishes/lemonade.jpg', 0, TRUE, NULL),
('Кава еспресо', 'Класичний італійський еспресо', 40, 60.00, 30, 5, NULL, TRUE, FALSE, TRUE, 'dishes/espresso.jpg', 0, TRUE, NULL),
('Капучино', 'Кава з молочною пінкою', 40, 75.00, 150, 7, NULL, TRUE, FALSE, TRUE, 'dishes/cappuccino.jpg', 0, TRUE, NULL),
('Чай фруктовий', 'Ароматний фруктовий чай з медом', 40, 70.00, 300, 7, NULL, TRUE, FALSE, TRUE, 'dishes/fruit_tea.jpg', 0, TRUE, NULL),
('Вино біле', 'Келих білого сухого вина', 41, 120.00, 150, 3, NULL, TRUE, FALSE, TRUE, 'dishes/white_wine.jpg', 0, TRUE, 'Вино зазвичай безглютенове'),
('Вино червоне', 'Келих червоного напівсухого вина', 41, 120.00, 150, 3, NULL, TRUE, FALSE, TRUE, 'dishes/red_wine.jpg', 0, TRUE, 'Вино зазвичай безглютенове'),
('Пиво крафтове', 'Крафтове пиво місцевої броварні', 41, 95.00, 330, 3, NULL, TRUE, FALSE, FALSE, 'dishes/craft_beer.jpg', 0, TRUE, 'Пиво містить глютен'),
('Мохіто', 'Коктейль з рому, м''яти, лайму та цукру', 42, 160.00, 300, 10, NULL, TRUE, FALSE, TRUE, 'dishes/mojito.jpg', 0, TRUE, NULL),
('Апероль Шприц', 'Освіжаючий коктейль з просекко та Апероль', 42, 170.00, 250, 7, NULL, TRUE, FALSE, TRUE, 'dishes/aperol_spritz.jpg', 0, TRUE, NULL); 