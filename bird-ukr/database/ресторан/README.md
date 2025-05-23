# База даних "Ресторан"

> **Примітка**: Ця база даних є частиною українського набору даних для задач Text-to-SQL, аналогічного англомовному набору BIRD (Benchmarking Intermediate Reasoning for text-to-SQL). Проект спрямований на створення повноцінного українського бенчмарку для оцінки здатності моделей штучного інтелекту розуміти природну мову українською та генерувати відповідні SQL-запити.

## Опис
База даних "Ресторан" розроблена для управління операціями ресторанного бізнесу, включаючи обслуговування клієнтів, управління персоналом, обробку замовлень, резервацію столиків та відстеження меню.

## Структура бази даних

### Таблиці

1. **категорії** - Категорії страв у меню ресторану
   - ід (PK) - унікальний ідентифікатор категорії
   - назва - назва категорії
   - опис - опис категорії
   - батьківська_категорія_ід (FK) - посилання на батьківську категорію
   - порядок_сортування - порядок відображення в меню
   - зображення_url - посилання на зображення категорії
   - активна - статус активності категорії

2. **страви** - Страви та напої, що пропонуються в ресторані
   - ід (PK) - унікальний ідентифікатор страви
   - назва - назва страви
   - опис - опис страви
   - категорія_ід (FK) - категорія, до якої належить страва
   - ціна - ціна страви
   - вага_гр - вага страви в грамах
   - час_приготування_хв - середній час приготування в хвилинах
   - вегетаріанська - чи є страва вегетаріанською
   - гостра - чи є страва гострою
   - фото_url - посилання на фото страви
   - активна - статус активності страви

3. **персонал** - Співробітники ресторану
   - ід (PK) - унікальний ідентифікатор співробітника
   - посада - посада співробітника
   - прізвище, ім_я, по_батькові - ПІБ співробітника
   - дата_народження - дата народження
   - телефон - контактний телефон
   - адреса - адреса проживання
   - електронна_пошта - електронна пошта
   - дата_прийому - дата прийому на роботу
   - дата_звільнення - дата звільнення (якщо звільнений)
   - ставка_за_годину - погодинна ставка
   - активний - статус активності співробітника
   - примітки - додаткові примітки

4. **зміни_персоналу** - Робочі зміни співробітників
   - ід (PK) - унікальний ідентифікатор зміни
   - співробітник_ід (FK) - ідентифікатор співробітника
   - дата - дата зміни
   - час_початку - запланований час початку зміни
   - час_закінчення - запланований час закінчення зміни
   - фактичний_час_початку - фактичний час початку зміни
   - фактичний_час_закінчення - фактичний час закінчення зміни
   - перерва_хв - тривалість перерви в хвилинах
   - оплата_за_зміну - сума оплати за зміну
   - примітки - додаткові примітки

5. **столики** - Столики в ресторані
   - ід (PK) - унікальний ідентифікатор столика
   - номер - номер столика
   - зона - зона розташування столика
   - кількість_місць - кількість місць за столиком
   - статус - поточний статус столика (вільний, зайнятий, зарезервовано)
   - опис - додатковий опис столика

6. **клієнти** - Постійні клієнти ресторану
   - ід (PK) - унікальний ідентифікатор клієнта
   - прізвище, ім_я, по_батькові - ПІБ клієнта
   - телефон - контактний телефон
   - електронна_пошта - електронна пошта
   - дата_народження - дата народження
   - дата_реєстрації - дата реєстрації в системі
   - кількість_відвідувань - кількість відвідувань ресторану
   - загальна_сума_замовлень - загальна сума всіх замовлень
   - примітки - додаткові примітки

7. **резервації** - Резервації столиків
   - ід (PK) - унікальний ідентифікатор резервації
   - стіл_ід (FK) - ідентифікатор зарезервованого столика
   - клієнт_ім_я - ім'я клієнта
   - контактний_телефон - контактний телефон клієнта
   - дата_час - дата та час резервації
   - тривалість_хв - тривалість резервації в хвилинах
   - кількість_гостей - кількість гостей
   - статус - статус резервації
   - коментар - додатковий коментар

8. **замовлення** - Замовлення в ресторані
   - ід (PK) - унікальний ідентифікатор замовлення
   - стіл_ід (FK) - ідентифікатор столика
   - клієнт_ід (FK) - ідентифікатор клієнта (якщо це постійний клієнт)
   - офіціант_ід (FK) - ідентифікатор офіціанта
   - дата_час - дата та час створення замовлення
   - статус - статус замовлення
   - спосіб_оплати - спосіб оплати замовлення
   - сума - загальна сума замовлення
   - чайові - сума чайових
   - коментар - додатковий коментар

9. **позиції_замовлення** - Позиції в замовленнях
   - ід (PK) - унікальний ідентифікатор позиції
   - замовлення_ід (FK) - ідентифікатор замовлення
   - страва_ід (FK) - ідентифікатор страви
   - кількість - кількість замовлених одиниць
   - ціна_за_одиницю - ціна за одиницю на момент замовлення
   - статус - статус позиції (замовлено, готується, подано)
   - коментар - додатковий коментар (побажання клієнта)

## Зв'язки між таблицями

- **категорії** мають зв'язок самі з собою (батьківська категорія)
- **страви** належать до **категорій**
- **позиції_замовлення** посилаються на **замовлення** та **страви**
- **замовлення** посилаються на **столики**, **клієнти** та **персонал** (офіціант)
- **резервації** посилаються на **столики**
- **зміни_персоналу** посилаються на **персонал**

## Типові запити до бази даних

База даних містить приклади запитів трьох рівнів складності:

### Прості запити (рівень 1)
- Отримання списку активних страв у меню
- Пошук вільних столиків
- Перегляд категорій страв
- Список активного персоналу
- Резервації на конкретну дату

### Запити середньої складності (рівень 2)
- Найпопулярніші страви за кількістю замовлень
- Статистика продажів по офіціантах
- Аналіз вегетаріанських страв за категоріями
- Інформація про замовлення та їх позиції
- Статистика резервацій за днями тижня

### Складні запити (рівень 3)
- Аналіз продажів за категоріями страв з динамікою по місяцях
- Звіт про ефективність персоналу з урахуванням замовлень та чайових
- Аналіз завантаженості ресторану за годинами та днями тижня
- Рекомендації страв на основі спільних замовлень
- Аналіз LTV клієнтів з сегментацією

## Файли даних

1. `schema.sql` - Схема бази даних з описом таблиць та індексів
2. `data_categories.sql` - Дані про категорії страв
3. `data_dishes.sql` - Дані про страви
4. `data_staff.sql` - Дані про персонал та робочі зміни
5. `data_tables_reservations.sql` - Дані про столики та резервації
6. `data_customers.sql` - Дані про постійних клієнтів
7. `data_orders.sql` - Дані про замовлення та їх позиції
8. `queries.sql` - Приклади запитів різної складності

## Використання

Для налаштування бази даних необхідно виконати SQL-скрипти в такому порядку:

1. `schema.sql` - Створення таблиць та індексів
2. `data_categories.sql` - Завантаження даних про категорії
3. `data_dishes.sql` - Завантаження даних про страви
4. `data_staff.sql` - Завантаження даних про персонал
5. `data_tables_reservations.sql` - Завантаження даних про столики та резервації
6. `data_customers.sql` - Завантаження даних про клієнтів
7. `data_orders.sql` - Завантаження даних про замовлення

Після завантаження даних можна виконувати запити з файлу `queries.sql`. 