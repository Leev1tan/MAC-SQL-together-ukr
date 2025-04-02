#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для перевірки виконуваності SQL-запитів з бенчмарку BIRD-UKR на PostgreSQL.
Перевіряє, чи всі gold_sql запити успішно виконуються на відповідних базах даних.
"""

import json
import os
import psycopg2
import argparse
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# Add mapping for database names to handle transliteration
DB_NAME_MAPPING = {
    # Latin to Cyrillic mappings
    "library": "бібліотека",
    "hospital": "лікарня",
    "university": "університет",
    "restaurant": "ресторан",
    "sports_club": "спортивний_клуб",
    "travel_agency": "туристичне_агентство",
    "online_store": "інтернет_магазин",
    "airline": "авіакомпанія"
}

def connect_to_database(db_id):
    """
    Підключається до бази даних PostgreSQL
    
    Args:
        db_id: Ідентифікатор бази даних
        
    Returns:
        Об'єкт з'єднання або None у випадку помилки
    """
    try:
        conn = psycopg2.connect(
            dbname=db_id,
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASSWORD", ""),
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "5432")
        )
        conn.autocommit = True  # Set autocommit mode to prevent cascading errors
        return conn
    except Exception as e:
        print(f"Помилка підключення до бази даних {db_id}: {e}")
        return None

def execute_query(conn, query):
    """
    Виконує SQL-запит
    
    Args:
        conn: З'єднання з базою даних
        query: SQL-запит
        
    Returns:
        True у випадку успішного виконання, (False, error_message) у випадку помилки
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.close()
        return True
    except Exception as e:
        # Log the error with the query for better debugging
        error_msg = str(e)
        return False, error_msg

def verify_queries(questions_file, limit=None, db_filter=None, output_errors=None):
    """
    Перевіряє виконуваність SQL-запитів для всіх питань
    
    Args:
        questions_file: Шлях до файлу з питаннями
        limit: Обмеження кількості запитів для тестування (опціонально)
        db_filter: Фільтр за назвою бази даних (опціонально)
        output_errors: Шлях до файлу для збереження детальної інформації про помилки
        
    Returns:
        Словник з результатами тестування
    """
    # Map the db_filter if it's a transliterated name
    if db_filter and db_filter in DB_NAME_MAPPING:
        db_filter = DB_NAME_MAPPING[db_filter]
    
    # Завантаження питань
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Фільтрація питань, якщо вказано db_filter
    if db_filter:
        questions = [q for q in questions if q.get('db_id') == db_filter]
    
    # Обмеження кількості запитів, якщо вказано limit
    if limit and limit > 0:
        questions = questions[:limit]
    
    results = {
        'total': len(questions),
        'successful': 0,
        'failed': 0,
        'errors': [],
        'by_database': {},
        'detailed_errors': []  # Store detailed error info for each query
    }
    
    # Групування питань за базою даних
    questions_by_db = {}
    for q in questions:
        db_id = q.get('db_id')
        if db_id not in questions_by_db:
            questions_by_db[db_id] = []
        questions_by_db[db_id].append(q)
    
    # Ініціалізація статистики по базах даних
    for db_id in questions_by_db:
        results['by_database'][db_id] = {
            'total': len(questions_by_db[db_id]),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
    
    # Тестування запитів для кожної бази даних
    for db_id, db_questions in questions_by_db.items():
        print(f"Тестування запитів для бази даних: {db_id}")
        
        # Підключення до бази даних
        conn = connect_to_database(db_id)
        if not conn:
            # Запис помилки для всіх запитів цієї бази даних
            error_message = f"Не вдалося підключитися до бази даних {db_id}"
            results['by_database'][db_id]['failed'] = len(db_questions)
            results['by_database'][db_id]['errors'].append(error_message)
            results['failed'] += len(db_questions)
            results['errors'].append(error_message)
            continue
        
        # Тестування запитів - use a new connection for each query to avoid transaction errors
        for q in tqdm(db_questions, desc=f"Запити для {db_id}"):
            # Create a new connection for each query to avoid transaction problems
            query_conn = connect_to_database(db_id)
            if not query_conn:
                error_message = f"Не вдалося підключитися до бази даних {db_id} для запиту {q.get('question_id', 'Unknown')}"
                results['errors'].append(error_message)
                results['by_database'][db_id]['errors'].append(error_message)
                results['failed'] += 1
                results['by_database'][db_id]['failed'] += 1
                continue
                
            query_id = q.get('question_id', 'Unknown')
            gold_sql = q.get('gold_sql', '')
            
            # Виконання запиту
            result = execute_query(query_conn, gold_sql)
            
            # Close the connection
            query_conn.close()
            
            # Обробка результату
            if result is True:
                results['successful'] += 1
                results['by_database'][db_id]['successful'] += 1
            else:
                results['failed'] += 1
                results['by_database'][db_id]['failed'] += 1
                
                error_message = f"Помилка в запиті {query_id}: {result[1]}"
                results['errors'].append(error_message)
                results['by_database'][db_id]['errors'].append(error_message)
                
                # Save detailed error info
                results['detailed_errors'].append({
                    'question_id': query_id,
                    'db_id': db_id,
                    'question': q.get('question', ''),
                    'sql': gold_sql,
                    'error': result[1],
                    'error_context': None
                })
        
        # Закриття з'єднання
        if conn:
            conn.close()
    
    # Save detailed errors to file if requested
    if output_errors and results['detailed_errors']:
        with open(output_errors, 'w', encoding='utf-8') as f:
            json.dump(results['detailed_errors'], f, indent=2, ensure_ascii=False)
        print(f"Detailed errors saved to: {output_errors}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Перевірка виконуваності SQL-запитів BIRD-UKR')
    parser.add_argument('--questions', default='bird-ukr/all_questions.json', 
                      help='Шлях до файлу з питаннями (за замовчуванням: bird-ukr/all_questions.json)')
    parser.add_argument('--limit', type=int, default=0,
                      help='Обмеження кількості запитів для тестування (за замовчуванням: без обмежень)')
    parser.add_argument('--db', type=str, default=None,
                      help='Тестувати запити тільки для конкретної бази даних (напр. "library" замість "бібліотека")')
    parser.add_argument('--output', type=str, default=None,
                      help='Зберегти результати в JSON файл')
    parser.add_argument('--errors', type=str, default='error_analysis/detailed_errors.json',
                      help='Зберегти детальну інформацію про помилки в JSON файл')
    
    args = parser.parse_args()
    
    # Виконання перевірки
    results = verify_queries(args.questions, args.limit, args.db, args.errors)
    
    # Виведення результатів
    print("\nРезультати перевірки:")
    print(f"Всього запитів: {results['total']}")
    print(f"Успішно виконано: {results['successful']} ({results['successful']/results['total']*100:.2f}%)")
    print(f"Помилки виконання: {results['failed']} ({results['failed']/results['total']*100:.2f}%)")
    
    # Виведення статистики по базах даних
    print("\nРезультати по базах даних:")
    for db_id, db_results in results['by_database'].items():
        success_rate = db_results['successful'] / db_results['total'] * 100
        print(f"  {db_id}: {db_results['successful']}/{db_results['total']} успішно ({success_rate:.2f}%)")
    
    # Виведення помилок (обмежено для зручності)
    if results['failed'] > 0:
        print("\nПерші 10 помилок:")
        for error in results['errors'][:10]:
            print(f"  - {error}")
        if len(results['errors']) > 10:
            print(f"  ... та ще {len(results['errors']) - 10} помилок.")
    
    # Збереження результатів у файл, якщо вказано
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nРезультати збережено в файл: {args.output}")

if __name__ == "__main__":
    main() 