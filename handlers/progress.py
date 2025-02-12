from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command
from utils.data_manager import load_user_data

router = Router()


@router.message(Command('check_progress'))
async def check_progress(message: Message):
    user_id = message.from_user.id
    user_data = load_user_data(user_id)

    if user_data:
        water_consumed = user_data.get('logged_water', 0)
        water_goal = user_data.get('water_goal', 2400)
        calories_consumed = user_data.get('logged_calories', 0)
        calories_burned = user_data.get('calories_burned', 0)
        calorie_goal = user_data.get('calories_goal', 2500)

        water_remaining = water_goal - water_consumed
        calorie_balance = calorie_goal - (calories_consumed - calories_burned)

        progress_message = (
            "📊 Прогресс:\n"
            "Вода:\n"
            f"- Выпито: {water_consumed} мл из {water_goal} мл.\n"
            f"- Осталось: {water_remaining} мл.\n\n"
            "Калории:\n"
            f"- Потреблено: {calories_consumed} ккал из {calorie_goal} ккал.\n"
            f"- Сожжено: {calories_burned} ккал.\n"
            f"- Баланс: {calorie_balance} ккал."
        )
        await message.reply(progress_message)
    else:
        await message.reply("Профиль не найден. Пожалуйста, создайте его с помощью команды /set_profile.")