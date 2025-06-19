#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add app/ to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Ukrainian Telegram Bot...")
    
    try:
        if not app_dir.exists():
            logger.error("app/ directory not found!")
            return await run_minimal_bot()
        
        logger.info("Importing app/main.py...")
        
        try:
            import main as app_main
            
            if hasattr(app_main, 'main'):
                logger.info("Found main() function in app/main.py")
                return await app_main.main()
            elif hasattr(app_main, 'UkrainianTelegramBot'):
                logger.info("Found UkrainianTelegramBot class")
                bot = app_main.UkrainianTelegramBot()
                return await bot.main()
            else:
                logger.warning("No entry point found in app/main.py")
                return await run_minimal_bot()
                
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return await run_minimal_bot()
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return await run_minimal_bot()
            
    except Exception as e:
        logger.error(f"Critical error: {e}")
        return await run_minimal_bot()

async def run_minimal_bot():
    logger.info("Starting minimal bot...")
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from aiogram.filters import Command
        from aiogram.types import Message
        
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.error("BOT_TOKEN not found!")
            return False
        
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        
        @dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer("Minimal bot mode - working!")
        
        @dp.message(Command("status"))
        async def cmd_status(message: Message):
            await message.answer("Status: Minimal mode active")
        
        logger.info("Minimal bot ready")
        await dp.start_polling(bot, skip_updates=True)
        return True
        
    except Exception as e:
        logger.error(f"Minimal bot error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Stopped by Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)