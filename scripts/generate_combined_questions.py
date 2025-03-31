#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для об'єднання індивідуальних JSON-файлів з питаннями в один файл.

Цей скрипт знаходить всі файли з питаннями в каталозі `bird-ukr/questions`
і об'єднує їх в один файл JSON `bird-ukr/all_questions.json`.
"""

import json
import os
import glob

def combine_questions():
    """
    Об'єднує всі файли питань в один JSON-файл.
    
    Функція знаходить всі файли *_questions.json в директорії bird-ukr/questions,
    читає їх вміст і об'єднує в один файл.
    """
    questions_dir = "bird-ukr/questions"
    output_file = "bird-ukr/all_questions.json"
    
    if not os.path.exists(questions_dir):
        print(f"Помилка: директорія {questions_dir} не існує")
        return
    
    # Знаходимо всі файли з питаннями
    question_files = glob.glob(os.path.join(questions_dir, "*_questions.json"))
    
    if not question_files:
        print("Помилка: не знайдено файлів з питаннями")
        return
    
    print("Початок об'єднання файлів питань...")
    print(f"Знайдено {len(question_files)} файлів з питаннями:")
    
    # Виводимо список знайдених файлів
    for file_path in question_files:
        filename = os.path.basename(file_path)
        print(f"  - {filename}")
    
    # Об'єднуємо дані з усіх файлів
    all_questions = []
    db_counts = {}
    
    for file_path in question_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                
                if not isinstance(questions, list):
                    print(f"Попередження: файл {file_path} не містить список питань. Пропускаємо.")
                    continue
                
                all_questions.extend(questions)
                
                # Отримуємо назву бази даних з імені файлу
                filename = os.path.basename(file_path)
                db_name = filename.replace("_questions.json", "")
                db_counts[db_name] = len(questions)
                
        except json.JSONDecodeError:
            print(f"Помилка: неможливо прочитати JSON з файлу {file_path}")
        except Exception as e:
            print(f"Помилка при обробці файлу {file_path}: {e}")
    
    # Виводимо кількість питань для кожної бази даних
    for db_name, count in db_counts.items():
        print(f"  - {db_name}: {count} питань")
    
    # Зберігаємо об'єднані дані
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)
    
    print(f"Об'єднано {len(all_questions)} питань з {len(db_counts)} баз даних")
    print(f"Результат збережено у файлі: {output_file}")

if __name__ == "__main__":
    combine_questions() 