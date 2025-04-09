-- Temporary script to run the університет import
\set ON_ERROR_STOP on
\c 'університет'

\echo 'Connected to університет. Running import...'
\i './MAC-SQL/data/bird-ukr/database/університет/import.sql'

\echo 'Finished running import script.' 