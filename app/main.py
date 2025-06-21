#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ГОЛОВНИЙ ФАЙЛ УКРАЇНОМОВНОГО БОТА - ВИПРАВЛЕНИЙ 🚀
"""

import asyncio
import logging
import sys
from typing import Optional, List, Dict, Any, Union  # ✅ ВСІ TYPING ІМПОРТИ

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class AutomatedUkrainianTelegramBot:
    """🤖 УКРАЇНОМОВНИЙ ТЕЛЕГРАМ БОТ З АВТОМАТИЗАЦІЄЮ"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.scheduler = None
        self.db_available = False

    async def setup_bot(self) -> bool:
        """Налаштування бота"""
        try:
            from aiogram import Bot, Dispatcher
            from aiogram.client.default import DefaultBotProperties
            from aiogram.enums import ParseMode
            import os
            
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                try:
                    from config.settings import BOT_TOKEN
                    bot_token = BOT_TOKEN
                except ImportError:
                    logger.error("❌ BOT_TOKEN не знайдено!")
                    return False
            
            self.bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            self.dp = Dispatcher()
            
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Бот підключено: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка налаштування бота: {e}")
            return False

    async def setup_database(self) -> bool:
        """Налаштування БД"""
        try:
            from database import init_db
            self.db_available = await init_db()
            
            if self.db_available:
                logger.info("✅ Database initialized successfully")
            else:
                logger.warning("⚠️ Working without database")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Database warning: {e}")
            return True

    async def setup_automation(self) -> bool:
        """Налаштування автоматизації"""
        try:
            # ✅ ВИПРАВЛЕНО: Правильний імпорт та виклик
            from services.automated_scheduler import create_automated_scheduler
            
            # ✅ ВИПРАВЛЕНО: Правильні аргументи (2 параметри)
            self.scheduler = await create_automated_scheduler(self.bot, self.db_available)
            
            if self.scheduler:
                logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА - бот працює самостійно!")
            else:
                logger.warning("⚠️ Working without automation")
            
            return True
        except Exception as e:
            logger.warning(f"⚠️ Automation warning: {e}")
            return True

    async def setup_handlers(self):
        """Налаштування хендлерів"""
        try:
            from handlers import register_all_handlers
            register_all_handlers(self.dp)
            logger.info("✅ All handlers registered with automation support")
        except Exception as e:
            logger.warning(f"⚠️ Handlers warning: {e}")
            # Базові хендлери як fallback
            await self._register_basic_handlers()

    async def _register_basic_handlers(self):
        """Базові хендлери"""
        from aiogram.types import Message
        from aiogram.filters import Command
        
        @self.dp.message(Command("start"))
        async def start_handler(message: Message):
            await message.answer("🤖 Привіт! Я український мем-бот!")

    async def cleanup(self):
        """✅ ВИПРАВЛЕНО: Cleanup ресурсів"""
        try:
            if self.scheduler:
                await self.scheduler.stop()
            
            # ✅ ВИПРАВЛЕНО: Правильне закриття aiohttp сесії
            if self.bot and hasattr(self.bot, 'session') and self.bot.session:
                if not self.bot.session.closed:
                    await self.bot.session.close()
                    logger.info("✅ Bot session closed")
                    
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

    async def run(self) -> bool:
        """Запуск бота"""
        logger.info("🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОT З ГЕЙМІФІКАЦІЄЮ 🚀")
        
        try:
            # Поетапна ініціалізація
            if not await self.setup_bot():
                return False
            
            await self.setup_database()
            await self.setup_automation()
            await self.setup_handlers()
            
            logger.info("🎯 Bot fully initialized with automation support")
            
            # Запуск polling з graceful shutdown
            try:
                await self.dp.start_polling(self.bot)
            except KeyboardInterrupt:
                logger.info("⏹️ Bot stopped by user")
            
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            return False
        finally:
            # ✅ ВИПРАВЛЕНО: Cleanup ресурсів
            await self.cleanup()

async def main():
    """Точка входу"""
    bot = AutomatedUkrainianTelegramBot()
    await bot.run()

if __name__ == "__main__":
    try:
        # ✅ ВИПРАВЛЕНО: правильний запуск
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Program interrupted")
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {e}")
        sys.exit(1)
