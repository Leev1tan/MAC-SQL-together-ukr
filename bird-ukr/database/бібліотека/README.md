# Library Database (База даних бібліотеки)

This directory contains SQL files for creating and populating a library database in PostgreSQL. The database is designed for a Ukrainian library management system and includes tables for books, authors, readers, employees, loans, reservations, events, and more.

## Database Structure

The database consists of the following main components:
- Books, authors, and genres management
- Library departments and employee records
- Reader registration and categorization
- Book loans and reservations
- Fines and payments
- Events and services
- Library activity statistics

## Files Description

- `schema.sql` - Contains the database schema with table definitions, constraints, indexes, and views
- `data.sql` - Basic reference data (languages, publishers, genres, reader categories, positions)
- `data_departments.sql` - Library departments data
- `data_employees.sql` - Staff members data
- `data_employee_departments.sql` - Employee-department assignments
- `data_book_genres.sql` - Book genres definitions
- `data_book_authors.sql` - Author information
- `data_books.sql` - Book records
- `data_book_copies.sql` - Physical book copies information
- `data_readers.sql` - Library readers/members records
- `data_loans.sql` - Book loan records
- `data_reservations.sql` - Book reservation records
- `data_fines.sql` - Fine records for late returns or damages
- `data_events.sql` - Library events data
- `data_services.sql` - Additional library services information
- `data_statistics.sql` - Library usage statistics
- `sample_queries.sql` - Example SQL queries demonstrating various database operations
- `import.sql` - Script for importing all SQL files in the correct order

## Installation

To set up the library database:

1. Make sure PostgreSQL is installed on your system
2. Create a new database:
   ```
   createdb library
   ```
3. Import the database using the import script:
   ```
   psql -U [username] -d library -f import.sql
   ```
   
Alternatively, you can execute each script individually in the following order:
1. `schema.sql`
2. `data.sql` 
3. The remaining data files in the order specified in `import.sql`

## Sample Queries

The `sample_queries.sql` file contains example queries that demonstrate how to perform various operations on the database, such as:
- Simple data retrieval
- Filtering and sorting
- Joining multiple tables
- Aggregation functions
- Subqueries and complex queries

These sample queries can be used as a reference for building your own queries against the database.

## Database Features

The library database includes several advanced PostgreSQL features:
- Foreign key constraints to maintain data integrity
- Indexes for optimized query performance
- Views for simplified access to commonly needed data
- Complex relationships between entities (many-to-many)
- Temporal data tracking (dates for loans, employment periods, etc.)

## Character Set and Collation

This database uses UTF-8 encoding to properly support Ukrainian characters. If you encounter any issues with character display, ensure your PostgreSQL instance is configured to use UTF-8. 