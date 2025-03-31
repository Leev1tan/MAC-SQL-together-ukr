-- Файл імпорту бази даних "Університет"
-- Encoding: UTF-8
-- Цей файл визначає порядок імпорту SQL-файлів для бази даних університету

-- ==========================================
-- Імпорт схеми бази даних
-- ==========================================
\echo 'Імпорт схеми бази даних університету...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/schema.sql'

-- ==========================================
-- Імпорт базових довідникових даних
-- ==========================================
\echo 'Імпорт базових довідникових даних...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data.sql'

-- ==========================================
-- Імпорт основних даних у порядку залежностей
-- ==========================================
\echo 'Імпорт основних даних...'

-- Структурні та організаційні дані
\echo '  Імпорт даних про факультети...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_faculties.sql'

\echo '  Імпорт даних про кафедри...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_departments.sql'

\echo '  Імпорт даних про викладачів...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_teachers.sql'

-- Після імпорту викладачів треба оновити інформацію про керівників
\echo '  Оновлення даних про керівників...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_managers_update.sql'

\echo '  Імпорт даних про студентів...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_students.sql'

\echo '  Імпорт даних про курси...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_courses.sql'

-- Дані про заняття та розклад
\echo '  Імпорт даних про розклад занять...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_schedules.sql'

-- Дані про записи на курси та оцінки
\echo '  Імпорт даних про оцінки...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_grades.sql'

\echo '  Імпорт даних про стипендії...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_scholarships.sql'

\echo '  Імпорт даних про бібліотечний фонд...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_library.sql'

\echo '  Імпорт даних про наукові дослідження...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_research.sql'

\echo '  Імпорт даних про конференції...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/data_conferences.sql'

-- ==========================================
-- Імпорт прикладів запитів
-- ==========================================
\echo 'Імпорт прикладів запитів...'
\i 'F:/univ/praktika/projects/slowdown-macsql/MAC-SQL/data/bird-ukr/database/університет/sample_queries.sql'

-- ==========================================
-- Завершення імпорту
-- ==========================================
\echo 'Імпорт бази даних університету завершено успішно!'

-- Примітка: Для імпорту використовуйте команду:
-- psql -U username -d database_name -f import.sql 