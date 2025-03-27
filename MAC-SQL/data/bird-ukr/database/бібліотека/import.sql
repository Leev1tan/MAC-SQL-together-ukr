-- Import file for Library (бібліотека) database
-- Created for Ukrainian Text-to-SQL dataset

-- First load the schema
\i 'schema.sql'

-- Then load the base data
\i 'data.sql'

-- Load the additional data files in order to maintain referential integrity
\i 'data_departments.sql'
\i 'data_employee_departments.sql'
\i 'data_employees.sql'
\i 'data_book_genres.sql'
\i 'data_book_authors.sql'
\i 'data_books.sql'
\i 'data_book_copies.sql'
\i 'data_readers.sql'
\i 'data_loans.sql'
\i 'data_reservations.sql'
\i 'data_fines.sql'
\i 'data_events.sql'
\i 'data_services.sql'
\i 'data_statistics.sql'

-- Load sample queries (optional, for reference only)
-- \i 'sample_queries.sql'

-- Note: To import the entire database, run:
-- psql -U [username] -d [database_name] -f import.sql 