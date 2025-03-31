#!/bin/bash

# BIRD-UKR Benchmark Database Import Tool

echo "=== BIRD-UKR Benchmark Database Import Tool ==="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3 before running this script."
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Found $PYTHON_VERSION"

# Check if psycopg2 is installed
if ! python3 -c "import psycopg2" &> /dev/null; then
    echo "WARNING: psycopg2 module not found. Attempting to install..."
    pip3 install -r "$(dirname "$0")/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install required packages. Please run manually:"
        echo "pip3 install -r $(dirname "$0")/requirements.txt"
        exit 1
    fi
    echo "Successfully installed required packages."
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "ERROR: PostgreSQL not found. Please install PostgreSQL and make sure psql is in your PATH."
    exit 1
fi

# Run the import script
echo
echo "Running database import script..."
echo

# Move to the project root directory
cd "$(dirname "$0")/.." || exit 1

# Run the script
python3 "$(dirname "$0")/import_databases.py"

# Check exit status
STATUS=$?
echo
if [ $STATUS -ne 0 ]; then
    echo "Import process completed with errors. See above for details."
else
    echo "Import process completed successfully!"
fi

# Make the script executable
chmod +x "$(dirname "$0")/import_databases.sh" 