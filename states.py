from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    logged_calories = State()
    logged_water = State()


class FoodLogStates(StatesGroup):
    food_name = State()
    food_weight = State()