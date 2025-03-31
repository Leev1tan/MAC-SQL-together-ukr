# BIRD-UKR: Ukrainian Benchmark for Text-to-SQL

[🇺🇦 Ukrainian version](README.md) | [🇬🇧 English version](README.en.md)

This project presents BIRD-UKR — the first large-scale Ukrainian benchmark for Text-to-SQL tasks, aimed at evaluating the ability of artificial intelligence models to understand queries in Ukrainian and generate appropriate SQL queries.

## Project Overview

BIRD-UKR is a collection of Ukrainian databases, natural language questions, and corresponding SQL queries, organized following the pattern of the English-language BIRD benchmark (Benchmarking Intermediate Reasoning for text-to-SQL). The project is designed to:

- Evaluate models' capabilities in processing Ukrainian language in the context of Text-to-SQL
- Create tools for comparing different approaches to solving Text-to-SQL tasks
- Support research and development in the field of natural language processing for the Ukrainian segment

## Data Structure

The benchmark includes:

- 8 unique database domains (hospital, university, sports club, etc.)
- 50-100 questions for each database
- Various levels of query complexity: simple, medium, complex
- Evaluation metrics: Execution Accuracy (EX) and Exact Match Accuracy (EM)

## Installation and Database Import

### Requirements
- PostgreSQL 11+
- Python 3.6+
- psycopg2 (Python library)

### Quick Start

#### Windows
```
cd scripts
import_databases.bat
```

#### macOS/Linux
```
cd scripts
chmod +x import_databases.sh
./import_databases.sh
```

### Manual Import

1. Install the required dependencies:
   ```
   pip install -r scripts/requirements.txt
   ```

2. Run the import script from the project root:
   ```
   python scripts/import_databases.py
   ```

3. Enter your PostgreSQL credentials when prompted

## Model Evaluation

To evaluate models on the BIRD-UKR benchmark, standard metrics are used:

- **Execution Accuracy (EX)**: Compares the execution results of the generated query with the reference
- **Exact Match Accuracy (EM)**: Compares the textual representation of queries

### Using Evaluation Scripts

```
python evaluation/benchmark.py --model your_model_name
```

## Project Structure

```
bird-ukr/                         # Benchmark directory
├── questions.json                # File with questions and queries
├── database/                     # Directory with databases
│   ├── спортивний_клуб/          # Each database is a separate directory
│   ├── лікарня/
│   ├── ...
├── tables.json                   # Database schema descriptions
└── column_meaning.json           # Description of each column's meaning
```

## Contributing to the Project

We welcome contributions to the project! If you want to improve existing databases, add new questions, or suggest new features, please create a pull request or open an issue.

## Authors and Acknowledgments

- Main developers: [Author names]
- Acknowledgments: [Organizations and people who helped]

## License

This project is distributed under the MIT license. See the LICENSE file for details. 