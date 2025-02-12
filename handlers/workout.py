from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from utils.data_manager import load_user_data, save_user_data

router = Router()

workout_calories = {
    "бег": 10,
    "ходьба": 5,
    "велосипед": 8,
    "плавание": 7,
    "бокс": 9,
    "борьба": 8,

}


@router.message(Command('log_workout'))
async def log_workout(message: Message):
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.reply("Пожалуйста, укажите тип тренировки и время. Пример: /log_workout бег 30")
        return

    workout_type = args[1].lower()
    try:
        duration = int(args[2])
    except ValueError:
        await message.reply("Пожалуйста, введите корректное время в минутах.")
        return

    if workout_type not in workout_calories:
        await message.reply("Неизвестный тип тренировки. Пожалуйста, используйте: бег, ходьба, велосипед, плавание и т.д.")
        return

    calories_burned = workout_calories[workout_type] * duration
    additional_water = (duration // 30) * 200

    user_id = message.from_user.id
    user_data = load_user_data(user_id)

    if user_data is not None:
        if 'calories_burned' not in user_data:
            user_data['calories_burned'] = 0
        if 'logged_calories' in user_data and 'logged_water' in user_data:
            user_data['calories_burned'] += calories_burned
            user_data['logged_water'] += additional_water
    else:
        await message.reply("Ваш профиль не найден. Пожалуйста, сначала настройте профиль с помощью /set_profile.")
        return

    save_user_data(user_id, user_data)
    response_message = f" {workout_type.capitalize()} {duration} минут — {calories_burned} ккал. "
    if additional_water > 0:
        response_message += f"Дополнительно: выпейте {additional_water} мл воды."

    await message.reply(response_message)