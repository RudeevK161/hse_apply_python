from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import aiohttp
from states import FoodLogStates
from aiogram.fsm.context import FSMContext
from utils.data_manager import load_user_data, save_user_data

router = Router()


async def get_food_info(food_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={food_name}&json=true") as response:
            if response.status == 200:
                data = await response.json()
                if "products" in data and len(data["products"]) > 0:
                    product = data["products"][0]
                    name = product.get('product_name', 'Неизвестный продукт')
                    calories = product.get('nutriments', {}).get('energy-kcal_100g', 'Нет данных')
                    return name, calories
            return None, None


async def get_food(food_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={food_name}&json=true"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if "products" in data and len(data["products"]) > 0:
                    product = data["products"][0]
                    name = product.get("product_name", "Неизвестный продукт")
                    calories = product.get("nutriments", {}).get("energy-kcal_100g", "Нет данных")

                    return {
                        "name": name,
                        "calories": calories
                    }

    return None

@router.message(Command('log_food'))
async def log_food(message: Message, state: FSMContext):
    food_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if not food_name:
        await message.reply("Пожалуйста, укажите название продукта после команды, например: /log_food банан.")
        return

    await state.set_state(FoodLogStates.food_name)
    await state.update_data(food_name=food_name)

    name, calories = await get_food_info(food_name)

    if calories is None:
        await message.reply("Не удалось найти информацию о продукте. Пожалуйста, попробуйте другой продукт.")
        return

    await state.update_data(calories=calories)
    await state.set_state(FoodLogStates.food_weight)
    await message.reply(f" {name} — {calories} ккал на 100 г. Сколько грамм вы съели?")


@router.message(FoodLogStates.food_weight)
async def process_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = load_user_data(user_id)

    if user_data is None:
        await message.reply("Ваш профиль не найден. Пожалуйста, сначала настройте профиль с помощью /set_profile.")
        return

    if 'logged_calories' not in user_data:
        user_data['logged_calories'] = 0.0

    if 'calories_goal' not in user_data:
        user_data['calories_goal'] = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] + (user_data['activity'] // 30) * 100

    try:
        grams = float(message.text)
        data = await state.get_data()
        calories = data['calories']
        kcal = (grams / 100) * calories

        user_data['logged_calories'] += kcal
        save_user_data(user_id, user_data)

        await message.reply(f"Записано: {kcal:.2f} ккал.")
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число граммов.")
    finally:
        await state.clear()
