import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from bot.config import settings
from bot.handlers.common import router as common_router
from bot.handlers.habit_create import router as habit_create_router
from bot.handlers.habit_manage import router as habit_manage_router
from bot.middlewares.db import DatabaseMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize bot and dispatcher
async def main() -> None:
    # Initialize Bot instance with default properties
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    
    # Dispatcher is a root router
    dp = Dispatcher(storage=MemoryStorage())

    # Register database middleware
    dp.update.middleware(DatabaseMiddleware())

    # Register all routers
    dp.include_router(common_router)
    dp.include_router(habit_create_router)
    dp.include_router(habit_manage_router)

    # Start bot
    if settings.WEBHOOK_ENABLED:
        # Webhook mode
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        await bot.set_webhook(
            url=settings.WEBHOOK_URL + settings.WEBHOOK_PATH,
            drop_pending_updates=True
        )

        web.run_app(
            app,
            host=settings.WEBAPP_HOST,
            port=settings.WEBAPP_PORT
        )
    else:
        # Polling mode
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!") 