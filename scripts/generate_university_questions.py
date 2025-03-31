#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Генератор питань та SQL-запитів для бази даних "Університет"

Цей скрипт створює різні типи питань та відповідні SQL-запити для бази даних
університету, базуючись на її схемі. Питання включають прості, середні
та складні запити, що відображають різні аспекти роботи університету.
"""

import json
import os
import random
from datetime import datetime

def add_question(questions, question_text, sql_query, difficulty, db_id="університет"):
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
    """Генерує питання та SQL-запити для бази даних університету"""
    questions = []
    
    # Прості питання (фільтрація та агрегація одної таблиці)
    add_question(
        questions,
        "Скільки викладачів працює в університеті?",
        "SELECT COUNT(*) FROM викладачі WHERE активний = TRUE;",
        "simple"
    )
    
    add_question(
        questions,
        "Які факультети є в університеті?",
        "SELECT назва, скорочення FROM факультети WHERE активний = TRUE ORDER BY назва;",
        "simple"
    )
    
    add_question(
        questions,
        "Скільки студентів навчається в кожній групі?",
        "SELECT назва, кількість_студентів FROM групи WHERE активна = TRUE ORDER BY кількість_студентів DESC;",
        "simple"
    )
    
    add_question(
        questions,
        "Які курси мають найбільшу кількість кредитів?",
        "SELECT назва, кількість_кредитів FROM курси WHERE активний = TRUE ORDER BY кількість_кредитів DESC LIMIT 5;",
        "simple"
    )
    
    add_question(
        questions,
        "Скільки студентів навчається на бюджеті?",
        "SELECT COUNT(*) FROM студенти WHERE фінансування = 'бюджет';",
        "simple"
    )
    
    add_question(
        questions,
        "Які аудиторії мають найбільшу місткість?",
        "SELECT номер, місткість, тип FROM аудиторії ORDER BY місткість DESC LIMIT 10;",
        "simple"
    )
    
    # Питання середньої складності (JOIN 2-3 таблиць, GROUP BY)
    add_question(
        questions,
        "Скільки студентів навчається на кожному факультеті?",
        """
        SELECT 
            ф.назва AS факультет, 
            COUNT(с.ід) AS кількість_студентів
        FROM факультети ф
        JOIN кафедри к ON ф.ід = к.факультет_ід
        JOIN напрями н ON к.ід = н.кафедра_ід
        JOIN групи г ON н.ід = г.напрям_ід
        JOIN студенти с ON г.ід = с.група_ід
        WHERE с.статус_ід = (SELECT ід FROM статуси_студентів WHERE назва = 'Активний')
        GROUP BY ф.ід, ф.назва
        ORDER BY кількість_студентів DESC;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Які викладачі ведуть найбільше курсів?",
        """
        SELECT 
            в.прізвище, 
            в.імя,
            COUNT(DISTINCT з.курс_ід) AS кількість_курсів
        FROM викладачі в
        JOIN заняття з ON в.ід = з.викладач_ід
        WHERE з.семестр_ід = (SELECT ід FROM семестри WHERE є_активним = TRUE)
        GROUP BY в.ід, в.прізвище, в.імя
        ORDER BY кількість_курсів DESC
        LIMIT 10;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Яка середня успішність студентів за факультетами?",
        """
        SELECT 
            ф.назва AS факультет,
            ROUND(AVG(CAST(о.оцінка AS NUMERIC)), 2) AS середній_бал,
            COUNT(DISTINCT с.ід) AS кількість_студентів
        FROM факультети ф
        JOIN кафедри к ON ф.ід = к.факультет_ід
        JOIN напрями н ON к.ід = н.кафедра_ід
        JOIN групи г ON н.ід = г.напрям_ід
        JOIN студенти с ON г.ід = с.група_ід
        JOIN записи_на_курси зк ON с.ід = зк.студент_ід
        JOIN оцінки о ON зк.ід = о.запис_на_курс_ід
        WHERE о.оцінка IS NOT NULL AND о.оцінка <> 'Н/З'
        GROUP BY ф.ід, ф.назва
        ORDER BY середній_бал DESC;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Яке навантаження у кожного викладача в поточному семестрі?",
        """
        SELECT 
            в.прізвище,
            в.імя,
            COUNT(з.ід) AS кількість_занять,
            SUM(CASE WHEN тз.назва = 'Лекція' THEN 1 ELSE 0 END) AS лекції,
            SUM(CASE WHEN тз.назва = 'Практичне' THEN 1 ELSE 0 END) AS практичні,
            SUM(CASE WHEN тз.назва = 'Лабораторна' THEN 1 ELSE 0 END) AS лабораторні,
            ROUND(SUM(EXTRACT(EPOCH FROM (рз.час_кінця - рз.час_початку))/3600), 2) AS загальні_години
        FROM викладачі в
        JOIN заняття з ON в.ід = з.викладач_ід
        JOIN типи_занять тз ON з.тип_заняття_ід = тз.ід
        JOIN розклад_занять рз ON з.ід = рз.заняття_ід
        WHERE рз.семестр_ід = (SELECT ід FROM семестри WHERE є_активним = TRUE)
        GROUP BY в.ід, в.прізвище, в.імя
        ORDER BY загальні_години DESC;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Які курси мають найнижчу успішність студентів?",
        """
        SELECT 
            к.назва AS курс,
            к.код,
            ROUND(AVG(CASE WHEN о.оцінка ~ '^[0-9]+$' THEN CAST(о.оцінка AS INTEGER) ELSE NULL END), 2) AS середній_бал,
            COUNT(DISTINCT зк.студент_ід) AS кількість_студентів,
            COUNT(CASE WHEN о.оцінка ~ '^[0-9]+$' AND CAST(о.оцінка AS INTEGER) < 60 THEN 1 ELSE NULL END) AS кількість_незадовільних
        FROM курси к
        JOIN записи_на_курси зк ON к.ід = зк.курс_ід
        JOIN оцінки о ON зк.ід = о.запис_на_курс_ід
        WHERE зк.семестр_ід = (SELECT ід FROM семестри WHERE є_активним = TRUE)
        GROUP BY к.ід, к.назва, к.код
        HAVING COUNT(DISTINCT зк.студент_ід) >= 5
        ORDER BY середній_бал ASC
        LIMIT 10;
        """,
        "medium"
    )
    
    add_question(
        questions,
        "Як розподілені аудиторії між факультетами?",
        """
        SELECT 
            ф.назва AS факультет,
            б.назва AS будівля,
            COUNT(DISTINCT а.ід) AS кількість_аудиторій,
            SUM(а.місткість) AS загальна_місткість,
            ROUND(AVG(а.місткість), 2) AS середня_місткість,
            STRING_AGG(DISTINCT а.тип, ', ') AS типи_аудиторій
        FROM факультети ф
        JOIN будівлі б ON ф.ід = б.факультет_ід
        JOIN аудиторії а ON б.ід = а.будівля_ід
        GROUP BY ф.ід, ф.назва, б.ід, б.назва
        ORDER BY кількість_аудиторій DESC;
        """,
        "medium"
    )
    
    # Складні питання (складні JOIN, підзапити, HAVING, агрегатні функції)
    add_question(
        questions,
        "Які студенти мають найвищу успішність на кожному факультеті?",
        """
        WITH студенти_успішність AS (
            SELECT 
                с.ід AS студент_ід,
                с.прізвище,
                с.імя,
                г.назва AS група,
                н.назва AS напрям,
                ф.ід AS факультет_ід,
                ф.назва AS факультет,
                ROUND(AVG(CASE WHEN о.оцінка ~ '^[0-9]+$' THEN CAST(о.оцінка AS INTEGER) ELSE NULL END), 2) AS середній_бал,
                COUNT(DISTINCT зк.курс_ід) AS кількість_курсів
            FROM студенти с
            JOIN групи г ON с.група_ід = г.ід
            JOIN напрями н ON г.напрям_ід = н.ід
            JOIN кафедри к ON н.кафедра_ід = к.ід
            JOIN факультети ф ON к.факультет_ід = ф.ід
            JOIN записи_на_курси зк ON с.ід = зк.студент_ід
            JOIN оцінки о ON зк.ід = о.запис_на_курс_ід
            WHERE о.оцінка IS NOT NULL 
            AND о.оцінка <> 'Н/З'
            AND с.статус_ід = (SELECT ід FROM статуси_студентів WHERE назва = 'Активний')
            GROUP BY с.ід, с.прізвище, с.імя, г.назва, н.назва, ф.ід, ф.назва
            HAVING COUNT(DISTINCT зк.курс_ід) >= 5
        ),
        ранжування AS (
            SELECT 
                студент_ід,
                прізвище,
                імя,
                група,
                напрям,
                факультет_ід,
                факультет,
                середній_бал,
                кількість_курсів,
                RANK() OVER (PARTITION BY факультет_ід ORDER BY середній_бал DESC) AS ранг
            FROM студенти_успішність
        )
        SELECT 
            факультет,
            прізвище,
            імя,
            група,
            напрям,
            середній_бал,
            кількість_курсів
        FROM ранжування
        WHERE ранг <= 3
        ORDER BY факультет, ранг;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Яке навантаження аудиторій в різні дні тижня?",
        """
        WITH завантаження_аудиторій AS (
            SELECT 
                а.ід AS аудиторія_ід,
                а.номер,
                а.тип,
                б.назва AS будівля,
                EXTRACT(DOW FROM рз.дата) AS день_тижня,
                TO_CHAR(рз.дата, 'Day') AS назва_дня,
                COUNT(рз.ід) AS кількість_занять,
                SUM(EXTRACT(EPOCH FROM (рз.час_кінця - рз.час_початку))/3600) AS загальні_години,
                COUNT(DISTINCT рз.заняття_ід) AS кількість_курсів
            FROM аудиторії а
            JOIN будівлі б ON а.будівля_ід = б.ід
            JOIN розклад_занять рз ON а.ід = рз.аудиторія_ід
            WHERE рз.семестр_ід = (SELECT ід FROM семестри WHERE є_активним = TRUE)
            GROUP BY а.ід, а.номер, а.тип, б.назва, EXTRACT(DOW FROM рз.дата), TO_CHAR(рз.дата, 'Day')
        ),
        загальне_навантаження AS (
            SELECT
                аудиторія_ід,
                SUM(загальні_години) AS загальні_години_за_тиждень
            FROM завантаження_аудиторій
            GROUP BY аудиторія_ід
        )
        SELECT 
            за.номер AS аудиторія,
            за.тип,
            за.будівля,
            за.назва_дня AS день_тижня,
            за.кількість_занять,
            ROUND(за.загальні_години, 2) AS годин_на_день,
            ROUND(зн.загальні_години_за_тиждень, 2) AS годин_на_тиждень,
            ROUND(за.загальні_години / NULLIF(зн.загальні_години_за_тиждень, 0) * 100, 2) AS відсоток_навантаження
        FROM завантаження_аудиторій за
        JOIN загальне_навантаження зн ON за.аудиторія_ід = зн.аудиторія_ід
        ORDER BY зн.загальні_години_за_тиждень DESC, за.аудиторія_ід, за.день_тижня;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Які кафедри найбільш ефективні за співвідношенням кількості студентів до кількості викладачів?",
        """
        WITH студенти_кафедр AS (
            SELECT 
                к.ід AS кафедра_ід,
                COUNT(DISTINCT с.ід) AS кількість_студентів
            FROM кафедри к
            JOIN напрями н ON к.ід = н.кафедра_ід
            JOIN групи г ON н.ід = г.напрям_ід
            JOIN студенти с ON г.ід = с.група_ід
            WHERE с.статус_ід = (SELECT ід FROM статуси_студентів WHERE назва = 'Активний')
            GROUP BY к.ід
        ),
        викладачі_кафедр AS (
            SELECT 
                к.ід AS кафедра_ід,
                COUNT(DISTINCT в.ід) AS кількість_викладачів
            FROM кафедри к
            JOIN викладачі в ON к.ід = в.кафедра_ід
            WHERE в.активний = TRUE
            GROUP BY к.ід
        ),
        курси_кафедр AS (
            SELECT 
                к.ід AS кафедра_ід,
                COUNT(DISTINCT кур.ід) AS кількість_курсів,
                SUM(кур.кількість_кредитів) AS загальна_кількість_кредитів
            FROM кафедри к
            JOIN курси кур ON к.ід = кур.кафедра_ід
            WHERE кур.активний = TRUE
            GROUP BY к.ід
        )
        SELECT 
            ф.назва AS факультет,
            к.назва AS кафедра,
            COALESCE(ск.кількість_студентів, 0) AS студентів,
            COALESCE(вк.кількість_викладачів, 0) AS викладачів,
            COALESCE(кк.кількість_курсів, 0) AS курсів,
            CASE 
                WHEN COALESCE(вк.кількість_викладачів, 0) = 0 THEN NULL
                ELSE ROUND(COALESCE(ск.кількість_студентів, 0)::numeric / COALESCE(вк.кількість_викладачів, 1), 2)
            END AS студентів_на_викладача,
            CASE 
                WHEN COALESCE(вк.кількість_викладачів, 0) = 0 THEN NULL
                ELSE ROUND(COALESCE(кк.кількість_курсів, 0)::numeric / COALESCE(вк.кількість_викладачів, 1), 2)
            END AS курсів_на_викладача,
            CASE 
                WHEN COALESCE(ск.кількість_студентів, 0) = 0 THEN NULL
                ELSE ROUND(COALESCE(кк.загальна_кількість_кредитів, 0)::numeric / COALESCE(ск.кількість_студентів, 1), 2)
            END AS кредитів_на_студента
        FROM кафедри к
        JOIN факультети ф ON к.факультет_ід = ф.ід
        LEFT JOIN студенти_кафедр ск ON к.ід = ск.кафедра_ід
        LEFT JOIN викладачі_кафедр вк ON к.ід = вк.кафедра_ід
        LEFT JOIN курси_кафедр кк ON к.ід = кк.кафедра_ід
        WHERE к.активна = TRUE
        ORDER BY студентів_на_викладача DESC NULLS LAST;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Як розподілені оцінки студентів за різними типами занять?",
        """
        WITH розподіл_оцінок AS (
            SELECT 
                тз.назва AS тип_заняття,
                CASE 
                    WHEN о.оцінка ~ '^[0-9]+$' AND CAST(о.оцінка AS INTEGER) >= 90 THEN 'A (відмінно)'
                    WHEN о.оцінка ~ '^[0-9]+$' AND CAST(о.оцінка AS INTEGER) >= 82 THEN 'B (дуже добре)'
                    WHEN о.оцінка ~ '^[0-9]+$' AND CAST(о.оцінка AS INTEGER) >= 74 THEN 'C (добре)'
                    WHEN о.оцінка ~ '^[0-9]+$' AND CAST(о.оцінка AS INTEGER) >= 64 THEN 'D (задовільно)'
                    WHEN о.оцінка ~ '^[0-9]+$' AND CAST(о.оцінка AS INTEGER) >= 60 THEN 'E (достатньо)'
                    WHEN о.оцінка ~ '^[0-9]+$' AND CAST(о.оцінка AS INTEGER) < 60 THEN 'F (незадовільно)'
                    ELSE о.оцінка
                END AS оцінка_літера,
                COUNT(*) AS кількість
            FROM заняття з
            JOIN типи_занять тз ON з.тип_заняття_ід = тз.ід
            JOIN записи_на_курси зк ON з.курс_ід = зк.курс_ід
            JOIN оцінки о ON зк.ід = о.запис_на_курс_ід AND з.ід = о.заняття_ід
            WHERE о.оцінка IS NOT NULL
            AND зк.семестр_ід = (SELECT ід FROM семестри WHERE є_активним = TRUE)
            GROUP BY тз.назва, оцінка_літера
        ),
        загальна_кількість AS (
            SELECT 
                тип_заняття,
                SUM(кількість) AS загальна_кількість
            FROM розподіл_оцінок
            GROUP BY тип_заняття
        )
        SELECT 
            ро.тип_заняття,
            ро.оцінка_літера,
            ро.кількість,
            ROUND(CAST(ро.кількість AS numeric) / зк.загальна_кількість * 100, 2) AS відсоток
        FROM розподіл_оцінок ро
        JOIN загальна_кількість зк ON ро.тип_заняття = зк.тип_заняття
        ORDER BY ро.тип_заняття, 
            CASE 
                WHEN ро.оцінка_літера = 'A (відмінно)' THEN 1
                WHEN ро.оцінка_літера = 'B (дуже добре)' THEN 2
                WHEN ро.оцінка_літера = 'C (добре)' THEN 3
                WHEN ро.оцінка_літера = 'D (задовільно)' THEN 4
                WHEN ро.оцінка_літера = 'E (достатньо)' THEN 5
                WHEN ро.оцінка_літера = 'F (незадовільно)' THEN 6
                ELSE 7
            END;
        """,
        "complex"
    )
    
    add_question(
        questions,
        "Який відсоток відвідуваності занять за різними курсами та групами?",
        """
        WITH розклад_курсів AS (
            SELECT 
                к.ід AS курс_ід,
                к.назва AS курс,
                г.ід AS група_ід,
                г.назва AS група,
                COUNT(DISTINCT рз.ід) AS загальна_кількість_занять
            FROM курси к
            JOIN заняття з ON к.ід = з.курс_ід
            JOIN розклад_занять рз ON з.ід = рз.заняття_ід
            JOIN записи_на_курси зк ON к.ід = зк.курс_ід
            JOIN студенти с ON зк.студент_ід = с.ід
            JOIN групи г ON с.група_ід = г.ід
            WHERE рз.семестр_ід = (SELECT ід FROM семестри WHERE є_активним = TRUE)
            AND рз.дата <= CURRENT_DATE
            GROUP BY к.ід, к.назва, г.ід, г.назва
        ),
        відвідуваність AS (
            SELECT 
                к.ід AS курс_ід,
                г.ід AS група_ід,
                COUNT(DISTINCT рз.ід) AS відвідані_заняття,
                COUNT(DISTINCT с.ід) AS кількість_студентів
            FROM курси к
            JOIN заняття з ON к.ід = з.курс_ід
            JOIN розклад_занять рз ON з.ід = рз.заняття_ід
            JOIN записи_на_курси зк ON к.ід = зк.курс_ід
            JOIN студенти с ON зк.студент_ід = с.ід
            JOIN групи г ON с.група_ід = г.ід
            LEFT JOIN навчальні_матеріали нм ON з.ід = нм.заняття_ід
            WHERE рз.семестр_ід = (SELECT ід FROM семестри WHERE є_активним = TRUE)
            AND рз.дата <= CURRENT_DATE
            AND EXISTS (
                SELECT 1 FROM оцінки о 
                WHERE о.запис_на_курс_ід = зк.ід 
                AND о.заняття_ід = з.ід 
                AND о.відвідування = TRUE
            )
            GROUP BY к.ід, г.ід
        )
        SELECT 
            рк.курс,
            рк.група,
            рк.загальна_кількість_занять,
            COALESCE(в.відвідані_заняття, 0) AS відвідані_заняття,
            COALESCE(в.кількість_студентів, 0) AS кількість_студентів,
            CASE 
                WHEN рк.загальна_кількість_занять = 0 THEN 0
                ELSE ROUND(COALESCE(в.відвідані_заняття, 0)::numeric / рк.загальна_кількість_занять * 100, 2)
            END AS відсоток_відвідуваності
        FROM розклад_курсів рк
        LEFT JOIN відвідуваність в ON рк.курс_ід = в.курс_ід AND рк.група_ід = в.група_ід
        ORDER BY відсоток_відвідуваності DESC;
        """,
        "complex"
    )
    
    # Зберігаємо згенеровані питання у JSON файлі
    output_dir = "bird-ukr/questions"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "університет_questions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)
        
    print(f"Створено {len(questions)} питань та SQL-запитів для бази даних 'Університет'")
    print(f"Збережено у файлі: {output_file}")

if __name__ == "__main__":
    generate_questions() 