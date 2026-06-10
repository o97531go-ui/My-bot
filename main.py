import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, ai_chat
from middlewares.safety import SafetyMiddleware
from middlewares.xp_system import XPMiddleware
from database.database import init_db
from aiohttp import web

async def health_check(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await init_db()
    asyncio.create_task(start_web_server())

    dp.message.middleware(SafetyMiddleware())
    dp.message.middleware(XPMiddleware())

    dp.include_router(start.router)
    dp.include_router(ai_chat.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
