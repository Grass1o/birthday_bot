from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from database import add_employee, remove_employee, get_employees
from datetime import datetime
import os

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['add'])
async def add_employee_handler(message: types.Message):
    try:
        _, name, birthday = message.text.split()
        datetime.strptime(birthday, "%d.%м.%Y")  # Проверяем корректность даты
        manager_id = message.from_user.id  # Используем Telegram ID как идентификатор руководителя
        add_employee(name, birthday, manager_id)
        await message.reply(f"Сотрудник {name} добавлен с датой рождения {birthday}.")
    except ValueError:
        await message.reply("Неверный формат. Используйте: /add <имя> <дата(DD.MM.YYYY)>")

@dp.message_handler(commands=['remove'])
async def remove_employee_handler(message: types.Message):
    _, name = message.text.split()
    manager_id = message.from_user.id
    remove_employee(name, manager_id)
    await message.reply(f"Сотрудник {name} удалён.")

@dp.message_handler(commands=['list'])
async def list_employees_handler(message: types.Message):
    manager_id = message.from_user.id
    employees = get_employees(manager_id)
    if employees:
        response = "\n".join([f"{name}: {birthday}" for name, birthday in employees])
    else:
        response = "У вас нет добавленных сотрудников."
    await message.reply(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)