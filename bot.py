import re
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
import os

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен бота из переменных окружения
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверяем, что токен установлен
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")

# Создаем экземпляры бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Включаем логирование в aiogram
dp.middleware.setup(LoggingMiddleware())

# Подключение к SQLite базе данных
conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

# Создаем таблицу для хранения сотрудников
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        user_id INTEGER,
        first_name TEXT,
        last_name TEXT,
        patronymic TEXT,
        birthday TEXT
    )
''')
conn.commit()

# Регулярное выражение для команды /add
ADD_COMMAND_REGEX = re.compile(r"^/add\s+([a-zA-Zа-яА-ЯёЁ]+)\s+([a-zA-Zа-яА-ЯёЁ]+)\s+([a-zA-Zа-яА-ЯёЁ]+)\s+(\d{2}\.\d{2}\.\d{4})$")

# Команда /start - инструкция
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    instruction = (
        "Привет! Я бот, который напоминает о днях рождения сотрудников.\n\n"
        "Команды:\n"
        "/start - Показать эту инструкцию.\n"
        "/add <имя> <фамилия> <отчество> <дата(DD.MM.YYYY)> - Добавить нового сотрудника.\n"
        "/list - Показать список всех сотрудников.\n"
        "/delete <имя> <фамилия> - Удалить сотрудника по имени и фамилии.\n\n"
        "Пример команды /add:\n"
        "/add Иванов Иван Иванович 03.03.1993"
    )
    await message.reply(instruction)

# Команда /add - добавление сотрудника
@dp.message_handler(commands=['add'])
async def add_employee(message: types.Message):
    # Проверяем, соответствует ли сообщение регулярному выражению
    match = ADD_COMMAND_REGEX.match(message.text)
    
    if not match:
        await message.reply("Неверный формат. Используйте: /add <имя> <фамилия> <отчество> <дата(DD.MM.YYYY)>\n"
                            "Пример: /add Иванов Иван Иванович 03.03.1993")
        return
    
    # Получаем имя, фамилию, отчество и дату рождения
    first_name, last_name, patronymic, birthday = match.groups()
    
    # Получаем ID пользователя, который добавляет сотрудника
    user_id = message.from_user.id
    
    # Добавляем сотрудника в базу данных
    cursor.execute('''
        INSERT INTO employees (user_id, first_name, last_name, patronymic, birthday)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, first_name, last_name, patronymic, birthday))
    conn.commit()
    
    await message.reply(f"Сотрудник {first_name} {last_name} {patronymic} с датой рождения {birthday} добавлен.")

# Команда /list - показать всех сотрудников
@dp.message_handler(commands=['list'])
async def list_employees(message: types.Message):
    user_id = message.from_user.id
    
    # Извлекаем всех сотрудников для текущего пользователя
    cursor.execute('''
        SELECT first_name, last_name, patronymic, birthday
        FROM employees
        WHERE user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    
    if not rows:
        await message.reply("Ваш список сотрудников пуст.")
        return
    
    # Формируем список сотрудников
    employee_list = "\n".join(
        [f"{row[0]} {row[1]} {row[2]}, Дата рождения: {row[3]}" for row in rows]
    )
    
    await message.reply(f"Ваши сотрудники:\n\n{employee_list}")

# Команда /delete - удаление сотрудника
@dp.message_handler(commands=['delete'])
async def delete_employee(message: types.Message):
    # Получаем текст команды (например, "/delete Иванов Иван")
    args = message.text.split()
    
    # Проверяем, что передано правильное количество аргументов
    if len(args) != 3:
        await message.reply("Неверный формат. Используйте: /delete <имя> <фамилия>\nПример: /delete Иванов Иван")
        return
    
    # Извлекаем имя и фамилию
    first_name, last_name = args[1], args[2]
    user_id = message.from_user.id
    
    # Удаляем сотрудника из базы данных
    cursor.execute('''
        DELETE FROM employees
        WHERE user_id = ? AND first_name = ? AND last_name = ?
    ''', (user_id, first_name, last_name))
    conn.commit()
    
    if cursor.rowcount == 0:
        await message.reply(f"Сотрудник {first_name} {last_name} не найден.")
    else:
        await message.reply(f"Сотрудник {first_name} {last_name} удален.")

# Основная функция для запуска бота
if __name__ == '__main__':
    # Запускаем бота с использованием polling
    executor.start_polling(dp, skip_updates=True)