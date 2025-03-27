# Hospital Database (База даних лікарні)

This directory contains SQL files for creating and populating a hospital database in PostgreSQL. The database is designed for a Ukrainian hospital management system and includes tables for departments, staff, patients, appointments, diagnoses, treatments, and payments.

## Database Structure

The database consists of the following main components:
- Hospital departments and staff management
- Patient records
- Medical visits and appointments
- Diagnoses and diseases
- Hospitalizations and procedures
- Laboratory tests and results
- Prescriptions and medications
- Payment and billing

## Files Description

- `schema.sql` - Contains the database schema with table definitions, constraints, and indexes
- `data.sql` - Basic reference data (departments, specializations, staff positions)
- `data_staff.sql` - Staff members data
- `data_patients.sql` - Patient records
- `data_disease_types.sql` - Types of diseases
- `data_diseases.sql` - Diseases information
- `data_doctor_specializations.sql` - Doctor specializations
- `data_insurance_companies.sql` - Insurance companies
- `data_patient_insurances.sql` - Patient insurance policies
- `data_appointments.sql` - Patient appointments and visits
- `data_diagnoses.sql` - Patient diagnoses
- `data_hospitalizations.sql` - Patient hospitalizations
- `data_procedures.sql` - Medical procedures
- `data_labresults.sql` - Laboratory test results
- `data_analysis.sql` - Analysis data
- `data_prescriptions.sql` - Prescriptions for patients
- `data_services.sql` - Medical services
- `data_payments.sql` - Payment records and payment details
- `sample_queries.sql` - Example SQL queries demonstrating various database operations
- `import.sql` - Script for importing all SQL files in the correct order

## Installation

To set up the hospital database:

1. Make sure PostgreSQL is installed on your system
2. Create a new database:
   ```
   createdb hospital
   ```
3. Import the database using the import script:
   ```
   psql -U [username] -d hospital -f import.sql
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

## Character Set and Collation

This database uses UTF-8 encoding to properly support Ukrainian characters. If you encounter any issues with character display, ensure your PostgreSQL instance is configured to use UTF-8. 