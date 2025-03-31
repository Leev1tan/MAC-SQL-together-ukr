#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Генератор метаданих для BIRD-UKR бенчмарку

Цей скрипт аналізує схеми баз даних та створює необхідні метадані:
1. tables.json - інформація про таблиці, колонки, ключі
2. column_meaning.json - опис значення кожного стовпця
"""

import os
import json
import re
import glob

def extract_table_info_from_schema(schema_content):
    """Вилучає інформацію про таблиці зі схеми бази даних"""
    table_info = {
        "table_names": [],
        "column_names": [],
        "column_types": [],
        "foreign_keys": [],
        "primary_keys": []
    }
    
    # Ідентифікатор колонки (для індексування)
    column_id = 0
    # Словник для відстеження ID колонок
    column_ids = {}
    # Словник для відстеження ID таблиць
    table_ids = {}
    # Словник для відстеження первинних ключів
    primary_keys = {}
    
    # Шаблон для пошуку визначень таблиць
    table_pattern = r"CREATE\s+TABLE\s+(\w+)\s*\("
    
    # Знаходимо всі таблиці
    tables = re.findall(table_pattern, schema_content, re.IGNORECASE)
    
    # Створюємо словник ID таблиць
    for i, table_name in enumerate(tables):
        table_ids[table_name] = i
        table_info["table_names"].append(table_name)
    
    # Шаблон для пошуку колонок та їх типів
    column_pattern = r"CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);"
    
    # Знаходимо всі визначення таблиць
    table_definitions = re.findall(column_pattern, schema_content, re.IGNORECASE | re.DOTALL)
    
    for table_name, definition in table_definitions:
        # Розділяємо визначення на окремі рядки
        lines = definition.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            
            # Пропускаємо порожні рядки та коментарі
            if not line or line.startswith("--"):
                continue
            
            # Шукаємо визначення PRIMARY KEY
            if "PRIMARY KEY" in line and not line.startswith("FOREIGN KEY"):
                if "PRIMARY KEY" in line.upper() and "(" in line:
                    # Це первинний ключ в форматі PRIMARY KEY (column)
                    pk_match = re.search(r"PRIMARY\s+KEY\s*\(\s*(\w+)\s*\)", line, re.IGNORECASE)
                    if pk_match:
                        pk_column = pk_match.group(1)
                        primary_keys[f"{table_name}.{pk_column}"] = True
                else:
                    # Це колонка з модифікатором PRIMARY KEY
                    column_match = re.match(r"\s*(\w+)\s+.*?PRIMARY\s+KEY", line, re.IGNORECASE)
                    if column_match:
                        pk_column = column_match.group(1)
                        primary_keys[f"{table_name}.{pk_column}"] = True
            
            # Шукаємо визначення FOREIGN KEY
            elif "FOREIGN KEY" in line:
                fk_match = re.search(r"FOREIGN\s+KEY\s*\(\s*(\w+)\s*\)\s*REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", line, re.IGNORECASE)
                if fk_match:
                    fk_column = fk_match.group(1)
                    ref_table = fk_match.group(2)
                    ref_column = fk_match.group(3)
                    
                    if f"{table_name}.{fk_column}" in column_ids and f"{ref_table}.{ref_column}" in column_ids:
                        fk_id = column_ids[f"{table_name}.{fk_column}"]
                        ref_id = column_ids[f"{ref_table}.{ref_column}"]
                        table_info["foreign_keys"].append([fk_id, ref_id])
            
            # Обробка звичайних колонок
            else:
                column_match = re.match(r"\s*(\w+)\s+([\w\(\)]+)", line)
                if column_match:
                    column_name = column_match.group(1)
                    column_type = column_match.group(2).lower()
                    
                    # Додаємо колонку до списку
                    table_info["column_names"].append([table_name, column_name])
                    
                    # Визначаємо базовий тип колонки
                    if any(t in column_type for t in ["int", "serial", "numeric", "decimal", "float", "double"]):
                        table_info["column_types"].append("number")
                    elif any(t in column_type for t in ["varchar", "text", "char"]):
                        table_info["column_types"].append("text")
                    elif any(t in column_type for t in ["date", "time", "timestamp"]):
                        table_info["column_types"].append("time")
                    elif "boolean" in column_type:
                        table_info["column_types"].append("boolean")
                    else:
                        table_info["column_types"].append("others")
                    
                    # Зберігаємо ID колонки
                    column_ids[f"{table_name}.{column_name}"] = column_id
                    
                    # Перевіряємо, чи є колонка первинним ключем
                    if f"{table_name}.{column_name}" in primary_keys:
                        table_info["primary_keys"].append(column_id)
                    
                    column_id += 1
    
    return table_info

def extract_column_meaning(schema_content):
    """Вилучає опис значення кожного стовпця зі схеми бази даних"""
    column_meaning = {}
    
    # Шаблон для пошуку визначень таблиць
    table_pattern = r"CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);"
    
    # Знаходимо всі визначення таблиць
    table_definitions = re.findall(table_pattern, schema_content, re.IGNORECASE | re.DOTALL)
    
    for table_name, definition in table_definitions:
        # Розділяємо визначення на окремі рядки
        lines = definition.strip().split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Пропускаємо порожні рядки та коментарі
            if not line or line.startswith("--"):
                continue
            
            # Шукаємо визначення колонок
            column_match = re.match(r"\s*(\w+)\s+([\w\(\)]+)", line)
            if column_match:
                column_name = column_match.group(1)
                column_key = f"{table_name}.{column_name}"
                
                # Шукаємо коментар для колонки (у тому ж рядку)
                comment_match = re.search(r"--\s*(.*?)$", line)
                if comment_match:
                    column_meaning[column_key] = comment_match.group(1).strip()
                else:
                    # Базовий опис на основі назви колонки
                    if column_name == "id":
                        column_meaning[column_key] = f"Унікальний ідентифікатор в таблиці {table_name}"
                    elif "ім" in column_name.lower() or "прізвище" in column_name.lower():
                        column_meaning[column_key] = f"Ім'я або прізвище в таблиці {table_name}"
                    elif "дата" in column_name.lower():
                        column_meaning[column_key] = f"Дата запису в таблиці {table_name}"
                    elif "ціна" in column_name.lower() or "вартість" in column_name.lower() or "сума" in column_name.lower():
                        column_meaning[column_key] = f"Вартість або ціна в таблиці {table_name}"
                    elif column_name.endswith("_id"):
                        ref_table = column_name[:-3]
                        column_meaning[column_key] = f"Зовнішній ключ до таблиці {ref_table}"
                    else:
                        column_meaning[column_key] = f"Значення поля {column_name} в таблиці {table_name}"
    
    return column_meaning

def generate_metadata():
    """Основна функція для генерації метаданих"""
    # Знаходимо всі файли схем баз даних
    schema_files = glob.glob("bird-ukr/database/*/schema.sql")
    
    # Структури для збереження метаданих
    tables_json = {}
    column_meaning_json = {}
    
    # Обробляємо кожну схему
    for schema_file in schema_files:
        # Визначаємо ім'я бази даних з шляху до файлу
        db_name = os.path.basename(os.path.dirname(schema_file))
        
        print(f"Обробка схеми бази даних '{db_name}'...")
        
        # Зчитуємо файл схеми
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # Вилучаємо інформацію про таблиці
        table_info = extract_table_info_from_schema(schema_content)
        tables_json[db_name] = table_info
        
        # Вилучаємо опис стовпців
        column_meanings = extract_column_meaning(schema_content)
        column_meaning_json[db_name] = column_meanings
    
    # Зберігаємо метадані у JSON файли
    with open("bird-ukr/tables.json", 'w', encoding='utf-8') as f:
        json.dump(tables_json, f, ensure_ascii=False, indent=4)
    
    with open("bird-ukr/column_meaning.json", 'w', encoding='utf-8') as f:
        json.dump(column_meaning_json, f, ensure_ascii=False, indent=4)
    
    print(f"Метадані успішно згенеровано.")
    print(f"- Файл tables.json містить інформацію про {len(tables_json)} баз даних")
    print(f"- Файл column_meaning.json містить описи колонок для {len(column_meaning_json)} баз даних")

if __name__ == "__main__":
    generate_metadata() 