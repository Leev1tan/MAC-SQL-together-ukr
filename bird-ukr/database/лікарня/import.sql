-- Import file for Hospital (лікарня) database
-- Created for Ukrainian Text-to-SQL dataset

-- First load the schema
\i 'schema.sql'

-- Then load the base data
\i 'data.sql'

-- Load the additional data files in order to maintain referential integrity
\i 'data_departments.sql'
\i 'data_disease_types.sql'
\i 'data_diseases.sql'
\i 'data_doctor_specializations.sql'
\i 'data_insurance_companies.sql'
\i 'data_staff.sql'
\i 'data_patients.sql'
\i 'data_patient_insurances.sql'
\i 'data_diagnoses.sql'
\i 'data_hospitalizations.sql'
\i 'data_procedures.sql'
\i 'data_labresults.sql'
\i 'data_analysis.sql'
\i 'data_prescriptions.sql'
\i 'data_services.sql'
\i 'data_payments.sql'

-- Load sample queries (optional, for reference only)
-- \i 'sample_queries.sql'

-- Note: To import the entire database, run:
-- psql -U [username] -d [database_name] -f import.sql 