# BIRD-UKR Quick Start Guide

This guide will help you quickly set up and import the BIRD-UKR databases.

## Prerequisites

Before you start, make sure you have:

1. **PostgreSQL** (version 11 or higher) installed and running
2. **Python** (version 3.6 or higher) installed
3. **psql** command-line client available in your PATH

## Step 1: Clone the Repository

If you haven't already, clone the repository:

```bash
git clone https://github.com/your-username/slowdown-macsql.git
cd slowdown-macsql
```

## Step 2: Install Required Python Packages

Install the required Python packages:

```bash
pip install -r scripts/requirements.txt
```

## Step 3: Import Databases

### Automatic Import (Recommended)

#### On Windows:

```bash
cd scripts
import_databases.bat
```

#### On macOS/Linux:

```bash
cd scripts
chmod +x import_databases.sh
./import_databases.sh
```

### Manual Import

If you prefer to import manually:

```bash
python scripts/import_databases.py
```

You'll be prompted to enter:
1. PostgreSQL username (default: postgres)
2. PostgreSQL password
3. Host (default: localhost)
4. Port (default: 5432)

## Step 4: Verify the Import

To verify that the databases were imported successfully, you can connect to PostgreSQL and list the databases:

```bash
psql -U postgres -c "\l"
```

You should see all the imported databases in the list.

## Troubleshooting

### Import Errors

If you encounter issues during import:

1. Ensure PostgreSQL is running
2. Check your PostgreSQL credentials
3. Make sure all required SQL files exist in the database directories
4. Verify that you have permissions to create databases

### Character Encoding Issues

If you see strange characters or encoding errors:

1. Ensure PostgreSQL was created with UTF-8 encoding
2. Make sure your terminal supports UTF-8 for Ukrainian characters
3. Use the `\encoding UTF8` command in psql if needed

### Missing Files

If the script reports missing files:

1. Check that all database directories have the complete set of SQL files
2. Verify that file references in import.sql files are correct
3. Ensure that all SQL files have the correct character encoding (UTF-8)

## Next Steps

After importing the databases, you can:

1. Explore the database schemas
2. Run sample queries provided in the documentation
3. Start using the benchmark to evaluate your Text-to-SQL models

For more detailed information, see the main [README.md](bird-ukr/README.md) file. 