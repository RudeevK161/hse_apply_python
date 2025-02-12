import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import profile, progress, water, workout, food
from middlewares import LoggingMiddleware

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(LoggingMiddleware())
routers = [
    profile.router,
    progress.router,
    water.router,
    workout.router,
    food.router,
]

#dp.include_router(*routers)
for router in routers:
    dp.include_router(router)


async def main():
    print("Bot started!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())