#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для оцінки Exact Match Accuracy (EM) для BIRD-UKR бенчмарку

Exact Match Accuracy оцінює точну відповідність між нормалізованими
згенерованим та еталонним SQL-запитами.
"""

import json
import argparse
import re
from tqdm import tqdm

def normalize_sql(query):
    """
    Нормалізує SQL-запит для порівняння.
    
    Нормалізація включає:
    - Приведення до нижнього регістру
    - Видалення зайвих пробілів
    - Стандартизація лапок
    - Стандартизація порядку полів у SELECT
    - Стандартизація аліасів
    """
    if not query:
        return ""
    
    # Приводимо до нижнього регістру
    query = query.lower()
    
    # Видаляємо коментарі
    query = re.sub(r'--.*?(\n|$)', ' ', query)
    query = re.sub(r'/\*.*?\*/', ' ', query, flags=re.DOTALL)
    
    # Замінюємо всі типи лапок на стандартні одинарні
    query = re.sub(r'"([^"]*)"', r"'\1'", query)
    query = re.sub(r"`([^`]*)`", r"'\1'", query)
    
    # Видаляємо крапку з кінця запиту, якщо вона є
    query = query.rstrip(';').strip()
    
    # Видаляємо зайві пробіли
    query = re.sub(r'\s+', ' ', query)
    
    # Видаляємо пробіли біля дужок і операторів
    query = re.sub(r'\s*\(\s*', '(', query)
    query = re.sub(r'\s*\)\s*', ')', query)
    query = re.sub(r'\s*=\s*', '=', query)
    query = re.sub(r'\s*<\s*', '<', query)
    query = re.sub(r'\s*>\s*', '>', query)
    query = re.sub(r'\s*,\s*', ',', query)
    
    # Стандартизуємо ключові слова
    query = re.sub(r'\bselect\b', 'select', query)
    query = re.sub(r'\bfrom\b', 'from', query)
    query = re.sub(r'\bwhere\b', 'where', query)
    query = re.sub(r'\bgroup by\b', 'group by', query)
    query = re.sub(r'\border by\b', 'order by', query)
    query = re.sub(r'\bhaving\b', 'having', query)
    query = re.sub(r'\blimit\b', 'limit', query)
    
    # Стандартизуємо оператори з'єднання
    query = re.sub(r'\bjoin\b', 'join', query)
    query = re.sub(r'\binner join\b', 'join', query)
    query = re.sub(r'\bleft join\b', 'left join', query)
    query = re.sub(r'\bright join\b', 'right join', query)
    
    # Видаляємо AS для аліасів
    query = re.sub(r'\bas\s+([a-zA-Z0-9_]+)', r' \1', query)
    
    return query.strip()

def compute_exact_match(pred_sql, gold_sql):
    """
    Обчислює Exact Match між передбаченим і еталонним SQL-запитами
    """
    norm_pred = normalize_sql(pred_sql)
    norm_gold = normalize_sql(gold_sql)
    
    return norm_pred == norm_gold

def evaluate_exact_match_accuracy(predictions, gold_data):
    """
    Оцінює Exact Match Accuracy для набору передбачень
    
    Args:
        predictions: Список словників з передбаченими SQL-запитами
        gold_data: Список словників з еталонними SQL-запитами
    
    Returns:
        Точність Exact Match (EM)
    """
    total = len(predictions)
    correct = 0
    
    # Створюємо словник для швидкого пошуку еталонних запитів
    gold_dict = {item['question_id']: item for item in gold_data}
    
    for pred in tqdm(predictions, desc="Оцінка EM"):
        question_id = pred['question_id']
        pred_sql = pred.get('predicted_sql', '')
        
        if question_id not in gold_dict:
            print(f"Попередження: question_id {question_id} не знайдено в еталонних даних")
            continue
        
        gold_sql = gold_dict[question_id]['gold_sql']
        
        if compute_exact_match(pred_sql, gold_sql):
            correct += 1
    
    # Обчислюємо точність
    accuracy = correct / total if total > 0 else 0
    return accuracy

def main():
    parser = argparse.ArgumentParser(description='Оцінка Exact Match Accuracy для BIRD-UKR')
    parser.add_argument('--predictions', required=True, help='Шлях до файлу з передбаченнями')
    parser.add_argument('--gold', default='bird-ukr/questions.json', help='Шлях до файлу з еталонними запитами')
    parser.add_argument('--output', help='Шлях для збереження результатів оцінки')
    
    args = parser.parse_args()
    
    # Завантажуємо передбачення та еталонні дані
    with open(args.predictions, 'r', encoding='utf-8') as f:
        predictions = json.load(f)
    
    with open(args.gold, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    
    # Оцінюємо точність
    em_score = evaluate_exact_match_accuracy(predictions, gold_data)
    
    print(f"Exact Match Accuracy: {em_score:.4f}")
    
    # Зберігаємо результати, якщо вказано шлях
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'exact_match_accuracy': em_score}, f, indent=2)

if __name__ == "__main__":
    main() 