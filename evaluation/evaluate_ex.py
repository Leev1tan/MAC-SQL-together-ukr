#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для оцінки Execution Accuracy (EX) для BIRD-UKR бенчмарку

Execution Accuracy оцінює правильність результату виконання згенерованого SQL-запиту
порівняно з результатом виконання еталонного запиту.
"""

import os
import json
import argparse
import sqlite3
import pandas as pd
import psycopg2
from psycopg2 import sql
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Налаштування підключення до PostgreSQL
PG_USER = os.environ.get('PG_USER', 'postgres')
PG_PASSWORD = os.environ.get('PG_PASSWORD', 'superuser')
PG_HOST = os.environ.get('PG_HOST', 'localhost')
PG_PORT = os.environ.get('PG_PORT', '5432')

# Константи
DB_TYPE_SQLITE = 'sqlite'
DB_TYPE_POSTGRES = 'postgres'

def normalize_query_result(result):
    """
    Нормалізує результат запиту для порівняння
    """
    if isinstance(result, list):
        # Конвертуємо всі елементи в рядки для однакового порівняння
        return sorted([str(item).strip() if item is not None else 'NULL' for item in result])
    elif isinstance(result, pd.DataFrame):
        # Якщо результат - DataFrame, конвертуємо його в список рядків
        result_list = []
        for _, row in result.iterrows():
            row_values = [str(val).strip() if val is not None else 'NULL' for val in row]
            result_list.append(tuple(row_values))
        return sorted(result_list)
    return result

def execute_query_sqlite(conn, query):
    """
    Виконує SQL-запит через SQLite і повертає результат
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return True, result
    except Exception as e:
        return False, f"SQLite помилка: {str(e)}"

def execute_query_postgres(conn, query):
    """
    Виконує SQL-запит через PostgreSQL і повертає результат
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return True, result
    except Exception as e:
        # Відкочуємо транзакцію у випадку помилки
        conn.rollback()
        return False, f"PostgreSQL помилка: {str(e)}"

def execute_query(conn, query, db_type):
    """
    Виконує SQL-запит і повертає результат залежно від типу бази даних
    """
    if db_type == DB_TYPE_SQLITE:
        return execute_query_sqlite(conn, query)
    elif db_type == DB_TYPE_POSTGRES:
        return execute_query_postgres(conn, query)
    else:
        return False, f"Непідтримуваний тип бази даних: {db_type}"

def connect_to_sqlite(db_path):
    """
    Підключається до бази даних SQLite
    """
    try:
        # Перевіряємо, чи існує файл бази даних
        if not os.path.exists(db_path):
            return None, f"Файл бази даних не знайдено: {db_path}"
        
        conn = sqlite3.connect(db_path)
        return conn, None
    except Exception as e:
        return None, f"Помилка підключення до SQLite бази даних: {str(e)}"

def connect_to_postgres(db_name):
    """
    Підключається до бази даних PostgreSQL
    """
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        return conn, None
    except Exception as e:
        return None, f"Помилка підключення до PostgreSQL бази даних: {str(e)}"

def connect_to_database(db_path, db_type):
    """
    Підключається до бази даних відповідного типу
    """
    if db_type == DB_TYPE_SQLITE:
        return connect_to_sqlite(db_path)
    elif db_type == DB_TYPE_POSTGRES:
        # Для PostgreSQL використовуємо ім'я бази даних замість шляху
        db_name = os.path.basename(db_path)
        return connect_to_postgres(db_name)
    else:
        return None, f"Непідтримуваний тип бази даних: {db_type}"

def evaluate_execution_accuracy(predictions, gold_data, db_path, db_type=DB_TYPE_POSTGRES):
    """
    Оцінює Execution Accuracy для набору передбачень
    
    Args:
        predictions: Список словників з передбаченими SQL-запитами
        gold_data: Список словників з еталонними SQL-запитами
        db_path: Шлях до директорії з базами даних
        db_type: Тип бази даних (sqlite або postgres)
    
    Returns:
        Точність виконання (EX), словник з деталізованими результатами
    """
    total = len(predictions)
    correct = 0
    detailed_results = {}
    
    # Лічильники для типів помилок
    error_stats = {
        "gold_connection_error": 0,
        "gold_execution_error": 0,
        "pred_execution_error": 0,
        "result_mismatch": 0
    }
    
    # Статистика по базах даних
    db_stats = {}
    
    # Створюємо словник для швидкого пошуку еталонних запитів
    gold_dict = {item['question_id']: item for item in gold_data}
    
    for pred in tqdm(predictions, desc="Оцінка EX"):
        question_id = pred['question_id']
        pred_sql = pred.get('predicted_sql', '')
        
        if question_id not in gold_dict:
            print(f"Попередження: question_id {question_id} не знайдено в еталонних даних")
            continue
        
        gold_item = gold_dict[question_id]
        gold_sql = gold_item['sql']  # Змінено з 'gold_sql' на 'sql' для відповідності формату
        db_id = gold_item['db_id']
        
        # Ініціалізуємо статистику для бази даних, якщо вона ще не існує
        if db_id not in db_stats:
            db_stats[db_id] = {
                "total": 0,
                "correct": 0,
                "errors": 0
            }
        
        db_stats[db_id]["total"] += 1
        
        # Підключаємось до бази даних
        db_full_path = os.path.join(db_path, db_id)
        if db_type == DB_TYPE_SQLITE:
            db_full_path = os.path.join(db_full_path, f"{db_id}.sqlite")
        
        conn, conn_error = connect_to_database(db_full_path, db_type)
        if conn_error:
            print(f"Не вдалося підключитися до бази даних {db_id}: {conn_error}")
            error_stats["gold_connection_error"] += 1
            db_stats[db_id]["errors"] += 1
            detailed_results[question_id] = {
                "status": "error",
                "error_type": "connection_error",
                "message": conn_error
            }
            continue
        
        # Виконуємо еталонний запит
        gold_success, gold_result = execute_query(conn, gold_sql, db_type)
        
        if not gold_success:
            print(f"Помилка виконання еталонного запиту для {question_id}: {gold_result}")
            error_stats["gold_execution_error"] += 1
            db_stats[db_id]["errors"] += 1
            detailed_results[question_id] = {
                "status": "error",
                "error_type": "gold_execution_error",
                "message": gold_result
            }
            conn.close()
            continue
        
        # Виконуємо передбачений запит
        pred_success, pred_result = execute_query(conn, pred_sql, db_type)
        
        # Закриваємо з'єднання
        conn.close()
        
        # Якщо не вдалося виконати передбачений запит
        if not pred_success:
            error_stats["pred_execution_error"] += 1
            db_stats[db_id]["errors"] += 1
            detailed_results[question_id] = {
                "status": "error",
                "error_type": "pred_execution_error",
                "message": pred_result
            }
            continue
        
        # Нормалізуємо результати
        norm_gold = normalize_query_result(gold_result)
        norm_pred = normalize_query_result(pred_result)
        
        # Порівнюємо результати
        if norm_gold == norm_pred:
            correct += 1
            db_stats[db_id]["correct"] += 1
            detailed_results[question_id] = {
                "status": "success",
                "match": True
            }
        else:
            error_stats["result_mismatch"] += 1
            detailed_results[question_id] = {
                "status": "error",
                "error_type": "result_mismatch",
                "gold_result": str(norm_gold[:5]) + "..." if len(norm_gold) > 5 else str(norm_gold),
                "pred_result": str(norm_pred[:5]) + "..." if len(norm_pred) > 5 else str(norm_pred)
            }
    
    # Обчислюємо точність
    accuracy = correct / total if total > 0 else 0
    
    # Додаємо відсоток успішності для кожної бази даних
    for db_id in db_stats:
        if db_stats[db_id]["total"] > 0:
            db_stats[db_id]["accuracy"] = db_stats[db_id]["correct"] / db_stats[db_id]["total"]
        else:
            db_stats[db_id]["accuracy"] = 0
    
    # Формуємо повний звіт
    report = {
        "execution_accuracy": accuracy,
        "total_queries": total,
        "correct_queries": correct,
        "error_stats": error_stats,
        "db_stats": db_stats,
        "detailed_results": detailed_results
    }
    
    return accuracy, report

def main():
    parser = argparse.ArgumentParser(description='Оцінка Execution Accuracy для BIRD-UKR')
    parser.add_argument('--predictions', required=True, help='Шлях до файлу з передбаченнями')
    parser.add_argument('--gold', default='bird-ukr/all_questions.json', help='Шлях до файлу з еталонними запитами')
    parser.add_argument('--db_path', default='bird-ukr/database', help='Шлях до директорії з базами даних')
    parser.add_argument('--db_type', choices=[DB_TYPE_SQLITE, DB_TYPE_POSTGRES], default=DB_TYPE_POSTGRES, 
                      help='Тип бази даних для використання (sqlite або postgres)')
    parser.add_argument('--output', help='Шлях для збереження результатів оцінки')
    parser.add_argument('--detailed_output', help='Шлях для збереження детальних результатів оцінки')
    
    args = parser.parse_args()
    
    # Завантажуємо передбачення та еталонні дані
    with open(args.predictions, 'r', encoding='utf-8') as f:
        predictions = json.load(f)
    
    with open(args.gold, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    
    # Оцінюємо точність
    ex_score, report = evaluate_execution_accuracy(predictions, gold_data, args.db_path, args.db_type)
    
    print(f"Execution Accuracy: {ex_score:.4f}")
    print(f"Загальна кількість запитів: {report['total_queries']}")
    print(f"Правильно виконаних запитів: {report['correct_queries']}")
    
    print("\nСтатистика помилок:")
    for error_type, count in report['error_stats'].items():
        print(f"  {error_type}: {count}")
    
    print("\nСтатистика по базах даних:")
    for db_id, stats in report['db_stats'].items():
        print(f"  {db_id}: точність = {stats['accuracy']:.4f} ({stats['correct']}/{stats['total']})")
    
    # Зберігаємо результати, якщо вказано шлях
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'execution_accuracy': ex_score}, f, indent=2)
    
    # Зберігаємо детальний звіт, якщо вказано шлях
    if args.detailed_output:
        with open(args.detailed_output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main() 