import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birthday TEXT NOT NULL,
            manager_id INTEGER NOT NULL  -- ID руководителя
        )
    ''')
    conn.commit()
    conn.close()

def add_employee(name, birthday, manager_id):
    birthday_db_format = datetime.strptime(birthday, "%d.%m.%Y").strftime("%Y-%m-%d")
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO employees (name, birthday, manager_id) VALUES (?, ?, ?)', (name, birthday_db_format, manager_id))
    conn.commit()
    conn.close()

def remove_employee(name, manager_id):
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employees WHERE name = ? AND manager_id = ?', (name, manager_id))
    conn.commit()
    conn.close()

def get_employees(manager_id):
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, birthday FROM employees WHERE manager_id = ?', (manager_id,))
    employees = cursor.fetchall()
    conn.close()

    formatted_employees = [(name, datetime.strptime(birthday, "%Y-%m-%d").strftime("%d.%m.%Y")) for name, birthday in employees]
    return formatted_employees