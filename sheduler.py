from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from database import get_employees
from bot import bot

scheduler = AsyncIOScheduler()

async def send_birthday_reminder(name, birthday, manager_id):
    await bot.send_message(chat_id=manager_id, text=f"Скоро день рождения у {name}: {birthday}!")

def schedule_birthday_notifications():
    # Получаем всех сотрудников для каждого руководителя
    employees = get_employees()
    for name, birthday_str, manager_id in employees:
        birthday = datetime.strptime(birthday_str, "%d.%m.%Y")
        now = datetime.now()

        # Напоминания за 1 месяц, 2 недели и 1 неделю
        for days_before in [30, 14, 7]:
            reminder_date = birthday - timedelta(days=days_before)
            if reminder_date > now:
                scheduler.add_job(send_birthday_reminder, 'date', run_date=reminder_date, args=[name, birthday_str, manager_id])

def start_scheduler():
    schedule_birthday_notifications()
    scheduler.start()