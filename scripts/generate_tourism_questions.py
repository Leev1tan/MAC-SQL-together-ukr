#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Генератор питань та SQL-запитів для бази даних "Туристичне агентство"

Цей скрипт створює різні типи питань та відповідні SQL-запити для бази даних
туристичного агентства, базуючись на її схемі. Питання включають прості, середні
та складні запити, що відображають різні аспекти роботи агентства.
"""

import json
import os
import random
from datetime import datetime

def add_question(questions, question_text, sql_query, difficulty, db_id="туристичне_агентство"):
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
    """Генерує питання та SQL-запити для бази даних туристичного агентства"""
    questions = []
    
    # Прості питання (фільтрація та агрегація одної таблиці)
    add_question(
        questions,
        "Скільки активних турів пропонує агентство?",
        "SELECT COUNT(*) FROM тури WHERE активний = true;",
        "simple"
    )
    
    add_question(
        questions,
        "Які готелі з 5 зірками є в базі даних?",
        "SELECT назва, адреса FROM готелі WHERE зірок = 5;",
        "simple"
    )
    
    add_question(
        questions,
        "Які країни представлені в агентстві?",
        "SELECT назва, континент FROM країни ORDER BY назва;",
        "simple"
    )
    
    add_question(
        questions,
        "Скільки клієнтів зареєстровано в агентстві за останній рік?",
        "SELECT COUNT(*) FROM клієнти WHERE дата_реєстрації >= CURRENT_DATE - INTERVAL '1 year';",
        "simple"
    )
    
    add_question(
        questions,
        "Які працівники мають найвищу зарплату?",
        "SELECT прізвище, імя, зарплата FROM працівники ORDER BY зарплата DESC LIMIT 5;",
        "simple"
    )
    
    add_question(
        questions,
        "Які методи оплати доступні клієнтам?",
        "SELECT назва, опис FROM методи_оплати;",
        "simple"
    )
    
    # Питання середньої складності (JOIN 2-3 таблиць, GROUP BY)
    add_question(
        questions,
        "Які тури доступні для бронювання в Італії на наступний місяць?",
        """
        SELECT т.назва, т.дата_початку, т.дата_закінчення, т.ціна, г.назва AS готель
        FROM тури т
        JOIN країни к ON т.країна_id = к.id
        LEFT JOIN готелі г ON т.готель_id = г.id
        WHERE к.назва = 'Італія'
        AND т.дата_початку BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '1 month')
        AND т.активний = true;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Скільки бронювань оформив кожен працівник за останній квартал?",
        """
        SELECT 
            п.прізвище, 
            п.імя, 
            COUNT(б.id) AS кількість_бронювань
        FROM працівники п
        LEFT JOIN бронювання_турів б ON п.id = б.працівник_id
        WHERE б.дата_бронювання >= CURRENT_DATE - INTERVAL '3 months'
        GROUP BY п.id, п.прізвище, п.імя
        ORDER BY кількість_бронювань DESC;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Які готелі найпопулярніші серед клієнтів (за кількістю бронювань)?",
        """
        SELECT 
            г.назва AS готель, 
            м.назва AS місто, 
            к.назва AS країна,
            г.зірок,
            COUNT(бг.id) AS кількість_бронювань
        FROM готелі г
        JOIN міста м ON г.місто_id = м.id
        JOIN країни к ON м.країна_id = к.id
        LEFT JOIN бронювання_готелів бг ON г.id = бг.готель_id
        GROUP BY г.id, г.назва, м.назва, к.назва, г.зірок
        ORDER BY кількість_бронювань DESC
        LIMIT 10;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Яка середня вартість бронювання туру по країнах?",
        """
        SELECT 
            к.назва AS країна, 
            ROUND(AVG(бт.загальна_вартість), 2) AS середня_вартість,
            COUNT(бт.id) AS кількість_бронювань
        FROM бронювання_турів бт
        JOIN тури т ON бт.тур_id = т.id
        JOIN країни к ON т.країна_id = к.id
        GROUP BY к.id, к.назва
        HAVING COUNT(бт.id) > 0
        ORDER BY середня_вартість DESC;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Які клієнти здійснили найбільше бронювань за останній рік?",
        """
        SELECT 
            к.прізвище, 
            к.імя, 
            COUNT(DISTINCT бт.id) AS бронювань_турів,
            COUNT(DISTINCT бг.id) AS бронювань_готелів,
            COUNT(DISTINCT бтр.id) AS бронювань_транспорту,
            (COUNT(DISTINCT бт.id) + COUNT(DISTINCT бг.id) + COUNT(DISTINCT бтр.id)) AS всього_бронювань
        FROM клієнти к
        LEFT JOIN бронювання_турів бт ON к.id = бт.клієнт_id AND бт.дата_бронювання >= CURRENT_DATE - INTERVAL '1 year'
        LEFT JOIN бронювання_готелів бг ON к.id = бг.клієнт_id AND бг.дата_бронювання >= CURRENT_DATE - INTERVAL '1 year'
        LEFT JOIN бронювання_транспорту бтр ON к.id = бтр.клієнт_id AND бтр.дата_бронювання >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY к.id, к.прізвище, к.імя
        HAVING (COUNT(DISTINCT бт.id) + COUNT(DISTINCT бг.id) + COUNT(DISTINCT бтр.id)) > 0
        ORDER BY всього_бронювань DESC
        LIMIT 10;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Які типи кімнат найчастіше бронюють у готелях?",
        """
        SELECT 
            тк.назва AS тип_кімнати, 
            COUNT(бг.id) AS кількість_бронювань
        FROM типи_кімнат тк
        JOIN бронювання_готелів бг ON тк.id = бг.тип_кімнати_id
        GROUP BY тк.id, тк.назва
        ORDER BY кількість_бронювань DESC;
        """,
        "medium"
    )
    
    # Складні питання (складні JOIN, підзапити, HAVING, агрегатні функції)
    add_question(
        questions,
        "Які місяці є найпопулярнішими для подорожей до різних країн?",
        """
        WITH місячні_тури AS (
            SELECT 
                к.назва AS країна,
                EXTRACT(MONTH FROM т.дата_початку) AS місяць,
                COUNT(*) AS кількість_турів,
                COUNT(DISTINCT бт.id) AS кількість_бронювань
            FROM тури т
            JOIN країни к ON т.країна_id = к.id
            LEFT JOIN бронювання_турів бт ON т.id = бт.тур_id
            WHERE т.дата_початку >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY к.назва, EXTRACT(MONTH FROM т.дата_початку)
        ),
        рейтинг_місяців AS (
            SELECT 
                країна,
                місяць,
                кількість_турів,
                кількість_бронювань,
                RANK() OVER (PARTITION BY країна ORDER BY кількість_бронювань DESC) AS ранг
            FROM місячні_тури
        )
        SELECT 
            країна,
            місяць,
            TO_CHAR(TO_DATE(місяць::text, 'MM'), 'Month') AS назва_місяця,
            кількість_турів,
            кількість_бронювань
        FROM рейтинг_місяців
        WHERE ранг = 1
        ORDER BY країна;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Які країни мають найкраще співвідношення позитивних відгуків до загальної кількості відгуків?",
        """
        WITH відгуки_країн AS (
            SELECT 
                к.id AS країна_id,
                к.назва AS країна,
                в.оцінка,
                CASE WHEN в.оцінка >= 4 THEN 1 ELSE 0 END AS позитивний_відгук
            FROM відгуки в
            JOIN готелі г ON в.готель_id = г.id
            JOIN міста м ON г.місто_id = м.id
            JOIN країни к ON м.країна_id = к.id
            UNION ALL
            SELECT 
                к.id AS країна_id,
                к.назва AS країна,
                в.оцінка,
                CASE WHEN в.оцінка >= 4 THEN 1 ELSE 0 END AS позитивний_відгук
            FROM відгуки в
            JOIN тури т ON в.тур_id = т.id
            JOIN країни к ON т.країна_id = к.id
        )
        SELECT 
            країна,
            COUNT(*) AS всього_відгуків,
            SUM(позитивний_відгук) AS позитивних_відгуків,
            ROUND(AVG(оцінка), 2) AS середня_оцінка,
            ROUND((SUM(позитивний_відгук)::float / COUNT(*)) * 100, 2) AS відсоток_позитивних
        FROM відгуки_країн
        GROUP BY країна_id, країна
        HAVING COUNT(*) >= 10
        ORDER BY відсоток_позитивних DESC, середня_оцінка DESC
        LIMIT 10;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Які працівники принесли найбільший прибуток агентству за останній рік?",
        """
        WITH доходи_працівників AS (
            -- Доходи від бронювання турів
            SELECT 
                п.id AS працівник_id,
                п.прізвище,
                п.імя,
                SUM(бт.загальна_вартість) AS дохід_від_турів,
                COUNT(DISTINCT бт.id) AS кількість_турів
            FROM працівники п
            JOIN бронювання_турів бт ON п.id = бт.працівник_id
            WHERE бт.дата_бронювання >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY п.id, п.прізвище, п.імя
        ),
        доходи_від_готелів AS (
            -- Доходи від бронювання готелів
            SELECT 
                п.id AS працівник_id,
                SUM(бг.вартість) AS дохід_від_готелів,
                COUNT(DISTINCT бг.id) AS кількість_готелів
            FROM працівники п
            JOIN бронювання_готелів бг ON п.id = бг.працівник_id
            WHERE бг.дата_бронювання >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY п.id
        ),
        доходи_від_транспорту AS (
            -- Доходи від бронювання транспорту
            SELECT 
                п.id AS працівник_id,
                SUM(бт.вартість) AS дохід_від_транспорту,
                COUNT(DISTINCT бт.id) AS кількість_транспорту
            FROM працівники п
            JOIN бронювання_транспорту бт ON п.id = бт.працівник_id
            WHERE бт.дата_бронювання >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY п.id
        )
        SELECT 
            дп.прізвище,
            дп.імя,
            пос.назва AS посада,
            COALESCE(дп.дохід_від_турів, 0) AS дохід_від_турів,
            COALESCE(дг.дохід_від_готелів, 0) AS дохід_від_готелів,
            COALESCE(дт.дохід_від_транспорту, 0) AS дохід_від_транспорту,
            COALESCE(дп.дохід_від_турів, 0) + COALESCE(дг.дохід_від_готелів, 0) + COALESCE(дт.дохід_від_транспорту, 0) AS загальний_дохід,
            COALESCE(дп.кількість_турів, 0) AS кількість_турів,
            COALESCE(дг.кількість_готелів, 0) AS кількість_готелів,
            COALESCE(дт.кількість_транспорту, 0) AS кількість_транспорту
        FROM доходи_працівників дп
        LEFT JOIN доходи_від_готелів дг ON дп.працівник_id = дг.працівник_id
        LEFT JOIN доходи_від_транспорту дт ON дп.працівник_id = дт.працівник_id
        JOIN посади пос ON (SELECT посада_id FROM працівники WHERE id = дп.працівник_id) = пос.id
        ORDER BY загальний_дохід DESC
        LIMIT 10;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Проаналізуйте прибутковість турів за тривалістю та типом харчування.",
        """
        WITH статистика_турів AS (
            SELECT 
                т.id AS тур_id,
                т.тривалість,
                т.тип_харчування,
                CASE 
                    WHEN т.тривалість <= 3 THEN 'Короткий (до 3 днів)'
                    WHEN т.тривалість <= 7 THEN 'Середній (4-7 днів)'
                    WHEN т.тривалість <= 14 THEN 'Довгий (8-14 днів)'
                    ELSE 'Дуже довгий (більше 14 днів)'
                END AS категорія_тривалості,
                COALESCE(т.тип_харчування, 'Без харчування') AS категорія_харчування,
                COUNT(DISTINCT бт.id) AS кількість_бронювань,
                SUM(бт.загальна_вартість) AS загальний_дохід,
                CASE WHEN COUNT(DISTINCT бт.id) > 0 
                    THEN SUM(бт.загальна_вартість) / COUNT(DISTINCT бт.id) 
                    ELSE 0 
                END AS середня_вартість_бронювання
            FROM тури т
            LEFT JOIN бронювання_турів бт ON т.id = бт.тур_id
            WHERE т.дата_початку >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY т.id, т.тривалість, т.тип_харчування
        )
        SELECT 
            категорія_тривалості,
            категорія_харчування,
            COUNT(DISTINCT тур_id) AS кількість_турів,
            SUM(кількість_бронювань) AS загальна_кількість_бронювань,
            ROUND(SUM(загальний_дохід), 2) AS загальний_дохід,
            ROUND(AVG(CASE WHEN кількість_бронювань > 0 THEN кількість_бронювань ELSE NULL END), 2) AS середня_кількість_бронювань_на_тур,
            ROUND(AVG(CASE WHEN середня_вартість_бронювання > 0 THEN середня_вартість_бронювання ELSE NULL END), 2) AS середня_вартість_бронювання
        FROM статистика_турів
        GROUP BY категорія_тривалості, категорія_харчування
        ORDER BY категорія_тривалості, категорія_харчування;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Які туристичні напрямки демонструють найбільший ріст популярності за останній рік?",
        """
        WITH квартальні_бронювання AS (
            SELECT 
                к.назва AS країна,
                м.назва AS місто,
                EXTRACT(QUARTER FROM бт.дата_бронювання) AS квартал,
                EXTRACT(YEAR FROM бт.дата_бронювання) AS рік,
                COUNT(DISTINCT бт.id) AS кількість_бронювань
            FROM бронювання_турів бт
            JOIN тури т ON бт.тур_id = т.id
            JOIN країни к ON т.країна_id = к.id
            JOIN міста м ON т.місто_id = м.id
            WHERE бт.дата_бронювання >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY к.назва, м.назва, EXTRACT(QUARTER FROM бт.дата_бронювання), EXTRACT(YEAR FROM бт.дата_бронювання)
        ),
        зведені_дані AS (
            SELECT 
                країна,
                місто,
                SUM(CASE WHEN (рік = EXTRACT(YEAR FROM CURRENT_DATE) AND квартал = EXTRACT(QUARTER FROM CURRENT_DATE)) 
                    OR (рік = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '3 months') AND квартал = EXTRACT(QUARTER FROM CURRENT_DATE - INTERVAL '3 months'))
                    THEN кількість_бронювань ELSE 0 END) AS останній_квартал,
                SUM(CASE WHEN (рік = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '3 months') AND квартал = EXTRACT(QUARTER FROM CURRENT_DATE - INTERVAL '3 months'))
                    OR (рік = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '6 months') AND квартал = EXTRACT(QUARTER FROM CURRENT_DATE - INTERVAL '6 months'))
                    THEN кількість_бронювань ELSE 0 END) AS передостанній_квартал,
                SUM(кількість_бронювань) AS загальна_кількість_бронювань
            FROM квартальні_бронювання
            GROUP BY країна, місто
            HAVING SUM(кількість_бронювань) >= 10
        )
        SELECT 
            країна,
            місто,
            останній_квартал,
            передостанній_квартал,
            CASE 
                WHEN передостанній_квартал = 0 THEN 100
                ELSE ROUND(((останній_квартал - передостанній_квартал)::float / передостанній_квартал) * 100, 2)
            END AS відсоток_росту,
            загальна_кількість_бронювань
        FROM зведені_дані
        WHERE останній_квартал > передостанній_квартал
        ORDER BY відсоток_росту DESC
        LIMIT 10;
        """,
        "complex"
    )
    
    # Зберігаємо згенеровані питання у JSON файлі
    output_dir = "bird-ukr/questions"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "туристичне_агентство_questions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)
        
    print(f"Створено {len(questions)} питань та SQL-запитів для бази даних 'Туристичне агентство'")
    print(f"Збережено у файлі: {output_file}")

if __name__ == "__main__":
    generate_questions() 