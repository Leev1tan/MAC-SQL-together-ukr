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
import pandas as pd
import psycopg2
from psycopg2 import sql
from tqdm import tqdm
import numpy as np

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

def execute_query(conn, query):
    """
    Виконує SQL-запит і повертає результат
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(f"Помилка виконання запиту: {e}")
        print(f"Запит: {query}")
        return None

def connect_to_database(db_path):
    """
    Підключається до бази даних
    """
    # Визначаємо параметри підключення (з конфіг-файлу або змінних середовища)
    # В цьому прикладі використовуємо фіксовані значення для прикладу
    params = {
        'dbname': os.path.basename(db_path),
        'user': os.environ.get('PGUSER', 'postgres'),
        'password': os.environ.get('PGPASSWORD', ''),
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': os.environ.get('PGPORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print(f"Помилка підключення до бази даних: {e}")
        return None

def evaluate_execution_accuracy(predictions, gold_data, db_path):
    """
    Оцінює Execution Accuracy для набору передбачень
    
    Args:
        predictions: Список словників з передбаченими SQL-запитами
        gold_data: Список словників з еталонними SQL-запитами
        db_path: Шлях до директорії з базами даних
    
    Returns:
        Точність виконання (EX)
    """
    total = len(predictions)
    correct = 0
    
    # Створюємо словник для швидкого пошуку еталонних запитів
    gold_dict = {item['question_id']: item for item in gold_data}
    
    for pred in tqdm(predictions, desc="Оцінка EX"):
        question_id = pred['question_id']
        pred_sql = pred.get('predicted_sql', '')
        
        if question_id not in gold_dict:
            print(f"Попередження: question_id {question_id} не знайдено в еталонних даних")
            continue
        
        gold_item = gold_dict[question_id]
        gold_sql = gold_item['gold_sql']
        db_id = gold_item['db_id']
        
        # Підключаємось до бази даних
        db_full_path = os.path.join(db_path, db_id)
        conn = connect_to_database(db_full_path)
        if not conn:
            print(f"Не вдалося підключитися до бази даних {db_id}")
            continue
        
        # Виконуємо запити
        gold_result = execute_query(conn, gold_sql)
        pred_result = execute_query(conn, pred_sql)
        
        # Закриваємо з'єднання
        conn.close()
        
        # Якщо хоча б один запит не вдалося виконати, вважаємо результат неправильним
        if gold_result is None or pred_result is None:
            continue
        
        # Нормалізуємо результати
        norm_gold = normalize_query_result(gold_result)
        norm_pred = normalize_query_result(pred_result)
        
        # Порівнюємо результати
        if norm_gold == norm_pred:
            correct += 1
    
    # Обчислюємо точність
    accuracy = correct / total if total > 0 else 0
    return accuracy

def main():
    parser = argparse.ArgumentParser(description='Оцінка Execution Accuracy для BIRD-UKR')
    parser.add_argument('--predictions', required=True, help='Шлях до файлу з передбаченнями')
    parser.add_argument('--gold', default='bird-ukr/questions.json', help='Шлях до файлу з еталонними запитами')
    parser.add_argument('--db_path', default='bird-ukr/database', help='Шлях до директорії з базами даних')
    parser.add_argument('--output', help='Шлях для збереження результатів оцінки')
    
    args = parser.parse_args()
    
    # Завантажуємо передбачення та еталонні дані
    with open(args.predictions, 'r', encoding='utf-8') as f:
        predictions = json.load(f)
    
    with open(args.gold, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    
    # Оцінюємо точність
    ex_score = evaluate_execution_accuracy(predictions, gold_data, args.db_path)
    
    print(f"Execution Accuracy: {ex_score:.4f}")
    
    # Зберігаємо результати, якщо вказано шлях
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'execution_accuracy': ex_score}, f, indent=2)

if __name__ == "__main__":
    main() 