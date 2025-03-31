# PostgreSQL Database Import for Ukrainian BIRD Benchmark

This directory contains a unified script for importing the Ukrainian BIRD benchmark databases into PostgreSQL.

## Requirements

- PostgreSQL server installed and running
- Python 3.6+
- psycopg2 library (`pip install psycopg2` or `pip install psycopg2-binary`)
- PostgreSQL user with CREATE DATABASE privileges

## Quick Start

The simplest way to import all databases:

```bash
python import_databases.py
```

This will:
1. Prompt for PostgreSQL credentials
2. Check the database connection
3. Create necessary databases (if they don't exist)
4. Import all schemas using either the `psql` command or direct Python import

## Command-Line Options

The script supports several options to customize its behavior:

```bash
python import_databases.py [--convert] [--cleanup] [--check] [--import]
```

- `--convert`: Convert MySQL syntax to PostgreSQL syntax in all schema files
- `--cleanup`: Drop existing databases before import (clean slate)
- `--check`: Verify PostgreSQL connection and create databases
- `--import`: Import schemas (default if no options provided)
- `--help`: Show help message

## Common Workflows

### First-time Setup

For a first-time setup, use:

```bash
python import_databases.py --convert --check --import
```

This will convert MySQL syntax, create databases, and import schemas.

### Reimporting Databases

To drop existing databases and reimport:

```bash
python import_databases.py --cleanup --import
```

### Just Converting Schema Files

If you only want to convert the MySQL syntax to PostgreSQL:

```bash
python import_databases.py --convert
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to PostgreSQL:

1. Make sure PostgreSQL service is running
2. Verify your username and password
3. Check that PostgreSQL is accepting connections on the specified host/port

### MySQL vs PostgreSQL Syntax

The script automatically converts common MySQL syntax to PostgreSQL:

- `AUTO_INCREMENT` → `SERIAL`
- `ENUM` types → `VARCHAR` with `CHECK` constraints
- MySQL comments → PostgreSQL comments

### Table Already Exists

If you get "relation already exists" errors:

1. Use the `--cleanup` option to drop existing databases first:

```bash
python import_databases.py --cleanup --import
```

## Manual Commands

If needed, you can manually:

1. Create database: `CREATE DATABASE database_name;`
2. Import schema: `psql -U postgres -d database_name -f schema.sql`
3. Drop database: `DROP DATABASE database_name;` 