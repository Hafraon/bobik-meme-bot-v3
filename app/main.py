#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Optional

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class UkrainianTelegramBot:
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.startup_time = datetime.now()
    
    def load_settings(self):
        return {
            'bot_token': os.getenv('BOT_TOKEN'),
            'admin_id': int(os.getenv('ADMIN_ID', 0)),
            'database_url': os.getenv('DATABASE_URL', 'sqlite:///bot.db'),
            'debug': os.getenv('DEBUG', 'False').lower() == 'true'
        }
    
    def validate_settings(self, settings):
        if not settings.get('bot_token'):
            logger.error("BOT_TOKEN not found!")
            return False
        if not settings.get('admin_id'):
            logger.error("ADMIN_ID not found!")
            return False
        return True
    
    async def create_bot(self, settings):
        try:
            from aiogram import Bot, Dispatcher
            from aiogram.enums import ParseMode
            from aiogram.client.default import DefaultBotProperties
            
            self.bot = Bot(
                token=settings['bot_token'],
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            self.dp = Dispatcher()
            
            bot_info = await self.bot.get_me()
            logger.info(f"Bot created: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"Bot creation error: {e}")
            return False
    
    async def setup_handlers(self):
        try:
            from aiogram.filters import Command
            from aiogram.types import Message
            
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message):
                await message.answer("Bot is working in basic mode!")
            
            @self.dp.message(Command("status"))
            async def cmd_status(message: Message):
                uptime = datetime.now() - self.startup_time
                await message.answer(f"Status: OK\nUptime: {uptime}")
            
            logger.info("Basic handlers registered")
            return True
            
        except Exception as e:
            logger.error(f"Handlers setup error: {e}")
            return False
    
    async def main(self):
        logger.info("Starting Ukrainian Telegram Bot...")
        
        try:
            settings = self.load_settings()
            
            if not self.validate_settings(settings):
                return False
            
            if not await self.create_bot(settings):
                return False
            
            if not await self.setup_handlers():
                return False
            
            if settings.get('admin_id') and self.bot:
                try:
                    await self.bot.send_message(
                        settings['admin_id'],
                        "Bot started successfully!"
                    )
                except:
                    pass
            
            logger.info("Starting polling...")
            await self.dp.start_polling(self.bot, skip_updates=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Critical error: {e}")
            return False
        finally:
            if self.bot:
                await self.bot.session.close()

async def main():
    bot = UkrainianTelegramBot()
    try:
        result = await bot.main()
        return result
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        return True
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)