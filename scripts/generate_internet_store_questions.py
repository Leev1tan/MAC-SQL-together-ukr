#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Генератор питань та SQL-запитів для бази даних "Інтернет магазин"

Цей скрипт створює різні типи питань та відповідні SQL-запити для бази даних
інтернет-магазину, базуючись на її схемі. Питання включають прості, середні
та складні запити, що відображають різні аспекти роботи інтернет-магазину.
"""

import json
import os
import random
from datetime import datetime

def add_question(questions, question_text, sql_query, difficulty, db_id="інтернет_магазин"):
    """Додає нове питання до списку питань"""
    question_id = f"{db_id}_{len(questions) + 1:03d}"
    questions.append({
        "question_id": question_id,
        "db_id": db_id,
        "question": question_text,
        "gold_sql": sql_query,
        "difficulty": difficulty
    })

def generate_questions():
    """Генерує питання та SQL-запити для бази даних інтернет-магазину"""
    questions = []
    
    # Прості питання (фільтрація та агрегація одної таблиці)
    add_question(
        questions,
        "Скільки всього активних товарів є в магазині?",
        "SELECT COUNT(*) FROM товари WHERE активний = TRUE;",
        "simple"
    )
    
    add_question(
        questions,
        "Які товари мають найвищий рейтинг?",
        "SELECT назва, рейтинг FROM товари ORDER BY рейтинг DESC LIMIT 5;",
        "simple"
    )
    
    add_question(
        questions,
        "Знайдіть середню ціну товарів у магазині.",
        "SELECT AVG(ціна) FROM товари WHERE активний = TRUE;",
        "simple"
    )
    
    add_question(
        questions,
        "Скільки клієнтів зареєструвалось у магазині?",
        "SELECT COUNT(*) FROM клієнти;",
        "simple"
    )
    
    add_question(
        questions,
        "Які методи доставки доступні в магазині?",
        "SELECT назва, вартість FROM методи_доставки WHERE активний = TRUE;",
        "simple"
    )
    
    add_question(
        questions,
        "Знайдіть товари, які закінчуються на складі (менше 10 штук).",
        "SELECT назва, кількість_на_складі FROM товари WHERE кількість_на_складі < 10 AND активний = TRUE;",
        "simple"
    )
    
    # Питання середньої складності (JOIN 2-3 таблиць, GROUP BY)
    add_question(
        questions,
        "Знайдіть 5 найпопулярніших категорій за кількістю товарів.",
        """
        SELECT к.назва, COUNT(т.ід) AS кількість_товарів
        FROM категорії к
        JOIN товари т ON к.ід = т.категорія_ід
        WHERE т.активний = TRUE
        GROUP BY к.назва
        ORDER BY кількість_товарів DESC
        LIMIT 5;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Обчисліть середню вартість замовлення для кожного методу доставки.",
        """
        SELECT мд.назва, AVG(з.загальна_сума) AS середня_вартість
        FROM замовлення з
        JOIN методи_доставки мд ON з.метод_доставки = мд.код
        GROUP BY мд.назва
        ORDER BY середня_вартість DESC;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Знайдіть 10 клієнтів, які зробили найбільше замовлень.",
        """
        SELECT к.прізвище, к.імя, COUNT(з.ід) AS кількість_замовлень
        FROM клієнти к
        JOIN замовлення з ON к.ід = з.клієнт_ід
        GROUP BY к.ід, к.прізвище, к.імя
        ORDER BY кількість_замовлень DESC
        LIMIT 10;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Для кожного товару знайдіть кількість залишених відгуків та середній рейтинг.",
        """
        SELECT т.назва, 
               COUNT(в.ід) AS кількість_відгуків, 
               AVG(в.рейтинг) AS середній_рейтинг
        FROM товари т
        LEFT JOIN відгуки в ON т.ід = в.товар_ід
        GROUP BY т.ід, т.назва
        HAVING COUNT(в.ід) > 0
        ORDER BY середній_рейтинг DESC;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Знайдіть кількість замовлень та загальну суму продажів по місяцях за останній рік.",
        """
        SELECT 
            EXTRACT(YEAR FROM дата_замовлення) AS рік,
            EXTRACT(MONTH FROM дата_замовлення) AS місяць,
            COUNT(*) AS кількість_замовлень,
            SUM(загальна_сума) AS загальна_сума_продажів
        FROM замовлення
        WHERE дата_замовлення >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY рік, місяць
        ORDER BY рік, місяць;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Знайдіть товари, які ще ніхто не замовляв.",
        """
        SELECT т.назва, т.ціна
        FROM товари т
        LEFT JOIN позиції_замовлення п ON т.ід = п.товар_ід
        WHERE п.ід IS NULL AND т.активний = TRUE;
        """,
        "medium"
    )
    
    # Складні питання (складні JOIN, підзапити, HAVING, агрегатні функції)
    add_question(
        questions,
        "Знайдіть топ-5 клієнтів за загальною сумою всіх замовлень та кількість їхніх замовлень.",
        """
        SELECT 
            к.прізвище,
            к.імя,
            COUNT(з.ід) AS кількість_замовлень,
            SUM(з.загальна_сума) AS загальна_сума
        FROM клієнти к
        JOIN замовлення з ON к.ід = з.клієнт_ід
        WHERE з.статус != 'скасовано'
        GROUP BY к.ід, к.прізвище, к.імя
        ORDER BY загальна_сума DESC
        LIMIT 5;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Для кожного товару визначте його популярність (кількість продажів) та прибуток.",
        """
        SELECT 
            т.назва,
            SUM(п.кількість) AS кількість_продажів,
            SUM(п.кількість * п.ціна_за_одиницю) AS загальний_прибуток
        FROM товари т
        JOIN позиції_замовлення п ON т.ід = п.товар_ід
        JOIN замовлення з ON п.замовлення_ід = з.ід
        WHERE з.статус IN ('виконано', 'доставлено')
        GROUP BY т.ід, т.назва
        ORDER BY загальний_прибуток DESC;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Знайдіть міста, де проживає найбільша кількість наших клієнтів.",
        """
        SELECT 
            а.місто,
            COUNT(DISTINCT к.ід) AS кількість_клієнтів
        FROM клієнти к
        JOIN адреси а ON к.ід = а.клієнт_ід
        GROUP BY а.місто
        ORDER BY кількість_клієнтів DESC
        LIMIT 10;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Порівняйте продажі товарів з різних категорій за останні 3 місяці та ранжуйте категорії за зростанням продажів.",
        """
        SELECT 
            к.назва AS категорія,
            SUM(CASE 
                WHEN з.дата_замовлення >= CURRENT_DATE - INTERVAL '1 month' 
                THEN п.кількість 
                ELSE 0 
            END) AS продажі_останній_місяць,
            SUM(CASE 
                WHEN з.дата_замовлення >= CURRENT_DATE - INTERVAL '3 month' 
                THEN п.кількість 
                ELSE 0 
            END) AS продажі_останні_3_місяці,
            SUM(п.кількість) AS загальні_продажі
        FROM категорії к
        JOIN товари т ON к.ід = т.категорія_ід
        JOIN позиції_замовлення п ON т.ід = п.товар_ід
        JOIN замовлення з ON п.замовлення_ід = з.ід
        WHERE з.статус != 'скасовано'
        GROUP BY к.ід, к.назва
        ORDER BY (продажі_останній_місяць - (продажі_останні_3_місяці - продажі_останній_місяць)/2.0) DESC;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Знайдіть клієнтів, які зробили замовлення всіма доступними методами доставки.",
        """
        SELECT 
            к.прізвище,
            к.імя
        FROM клієнти к
        WHERE (
            SELECT COUNT(DISTINCT мд.код)
            FROM методи_доставки мд
            WHERE мд.активний = TRUE
        ) = (
            SELECT COUNT(DISTINCT з.метод_доставки)
            FROM замовлення з
            WHERE з.клієнт_ід = к.ід
        );
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Для кожного товару знайдіть співвідношення між кількістю позитивних (4-5 зірок) та негативних (1-2 зірки) відгуків.",
        """
        SELECT 
            т.назва,
            SUM(CASE WHEN в.рейтинг >= 4 THEN 1 ELSE 0 END) AS позитивні_відгуки,
            SUM(CASE WHEN в.рейтинг <= 2 THEN 1 ELSE 0 END) AS негативні_відгуки,
            CASE 
                WHEN SUM(CASE WHEN в.рейтинг <= 2 THEN 1 ELSE 0 END) = 0 THEN 'Тільки позитивні'
                ELSE ROUND(SUM(CASE WHEN в.рейтинг >= 4 THEN 1 ELSE 0 END)::numeric / 
                      NULLIF(SUM(CASE WHEN в.рейтинг <= 2 THEN 1 ELSE 0 END), 0), 2)::text
            END AS співвідношення
        FROM товари т
        JOIN відгуки в ON т.ід = в.товар_ід
        GROUP BY т.ід, т.назва
        HAVING COUNT(в.ід) >= 5
        ORDER BY т.назва;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Знайдіть середній час між датою замовлення та датою доставки для різних методів доставки.",
        """
        SELECT 
            мд.назва AS метод_доставки,
            AVG(EXTRACT(EPOCH FROM (д.дата_доставки - з.дата_замовлення))/86400)::numeric(10,2) AS середній_час_доставки_днів
        FROM замовлення з
        JOIN методи_доставки мд ON з.метод_доставки = мд.код
        JOIN доставки д ON з.ід = д.замовлення_ід
        WHERE д.дата_доставки IS NOT NULL
        GROUP BY мд.назва
        ORDER BY середній_час_доставки_днів;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Знайдіть клієнтів, які зробили більше 5 замовлень за останні 6 місяців та обчисліть їхню загальну суму покупок за цей період.",
        """
        SELECT 
            к.прізвище,
            к.імя,
            COUNT(з.ід) AS кількість_замовлень,
            SUM(з.загальна_сума) AS загальна_сума_покупок
        FROM клієнти к
        JOIN замовлення з ON к.ід = з.клієнт_ід
        WHERE з.дата_замовлення >= CURRENT_DATE - INTERVAL '6 month'
        GROUP BY к.ід, к.прізвище, к.імя
        HAVING COUNT(з.ід) > 5
        ORDER BY загальна_сума_покупок DESC;
        """,
        "complex"
    )
    
    # Зберігаємо згенеровані питання у JSON файлі
    output_dir = "bird-ukr/questions"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "інтернет_магазин_questions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)
        
    print(f"Створено {len(questions)} питань та SQL-запитів для бази даних 'Інтернет магазин'")
    print(f"Збережено у файлі: {output_file}")

if __name__ == "__main__":
    generate_questions() 