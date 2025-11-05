"""
Main entry point for Telegram Bot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import redis.asyncio as redis

from config import config
from middlewares.i18n import I18nMiddleware
from middlewares.auth import AuthMiddleware
from handlers import start, booking, my_appointments, documents, payments, feedback, support, profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Actions on bot startup"""
    logger.info("Bot starting...")
    
    if config.USE_WEBHOOK:
        # Set webhook
        webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=config.WEBHOOK_SECRET,
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to {webhook_url}")
    else:
        # Delete webhook if using polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Using polling mode")


async def on_shutdown(bot: Bot):
    """Actions on bot shutdown"""
    logger.info("Bot shutting down...")
    await bot.session.close()


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher"""
    # Create Redis storage for FSM
    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB
    )
    storage = RedisStorage(redis=redis_client)
    
    # Create dispatcher
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.update.outer_middleware(I18nMiddleware())
    dp.update.outer_middleware(AuthMiddleware())
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(my_appointments.router)
    dp.include_router(documents.router)
    dp.include_router(payments.router)
    dp.include_router(feedback.router)
    dp.include_router(support.router)
    dp.include_router(profile.router)
    
    # Register startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    return dp


async def main():
    """Main function"""
    # Validate config
    config.validate()
    
    # Create bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = create_dispatcher()
    
    if config.USE_WEBHOOK:
        # Webhook mode
        app = web.Application()
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=config.WEBHOOK_SECRET
        )
        webhook_handler.register(app, path=config.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        logger.info(f"Starting webhook server on {config.WEBAPP_HOST}:{config.WEBAPP_PORT}")
        web.run_app(app, host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)
    else:
        # Polling mode
        logger.info("Starting polling mode")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")

