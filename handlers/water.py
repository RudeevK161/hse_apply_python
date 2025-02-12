from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
import aiohttp
from config import API_KEY
from utils.data_manager import load_user_data, save_user_data

router = Router()


async def get_current_temperature(city: str, api_key: str) -> float:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['main']['temp']
            else:
                return None


@router.message(Command('log_water'))
async def log_water(message: Message):
    user_id = message.from_user.id

    user_data = load_user_data(user_id)

    if user_data is None:
        await message.reply("Ваш профиль не найден. Пожалуйста, сначала настройте профиль с помощью /set_profile.")
        return

    base_water_intake = user_data['weight'] * 30
    activity_increase = (user_data['activity'] // 30) * 500

    city = user_data['city']
    current_temperature = await get_current_temperature(city, API_KEY)

    if current_temperature is None:
        await message.reply("Не удалось получить текущую температуру. Пожалуйста, попробуйте позже.")
        return

    weather_increase = 500 if current_temperature > 25 else 0
    total_water_intake = base_water_intake + activity_increase + weather_increase
    user_data['water_goal'] = total_water_intake
    try:
        water_logged = float(message.text.split(maxsplit=1)[1]) if len(message.text.split()) > 1 else None
    except ValueError:
        await message.reply("Пожалуйста, укажите корректное количество воды в миллилитрах. Пример: /log_water 250")
        return

    if 'logged_water' not in user_data:
        user_data['logged_water'] = 0

    user_data['logged_water'] += water_logged

    remaining_water = user_data['water_goal'] - user_data['logged_water']

    save_user_data(user_id, user_data)

    if remaining_water > 0:
        await message.reply(f"Вы выпили {water_logged} мл воды. Осталось {remaining_water} мл до выполнения нормы.")
    else:
        await message.reply(f"Вы выпили {water_logged} мл воды. Вы достигли своей нормы потребления воды! 🎉")