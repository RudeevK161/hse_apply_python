from aiogram.filters import Command
from aiogram.types import Message
from states import Form
from aiogram import Router
from aiogram.fsm.context import FSMContext
from utils.data_manager import save_user_data

router = Router()


@router.message(Command('set_profile'))
async def cmd_start(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (кг):")
    await state.set_state(Form.weight)


@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    weight = int(message.text)
    await state.update_data(weight=weight)
    await message.reply("Введите ваш рост (см):")
    await state.set_state(Form.height)


@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    height = int(message.text)
    await state.update_data(height=height)
    await message.reply("Введите ваш возраст (лет):")
    await state.set_state(Form.age)


@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    age = int(message.text)
    await state.update_data(age=age)
    await message.reply("Введите уровень активности (0-100):")
    await state.set_state(Form.activity)


@router.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    activity = int(message.text)
    await state.update_data(activity=activity)
    await message.reply("Введите ваш город:")
    await state.set_state(Form.city)


@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    user_data = await state.get_data()
    save_user_data(message.from_user.id, user_data)
    await message.reply("Ваш профиль успешно сохранен!")
    await state.clear()