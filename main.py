#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 УКРАЇНОМОВНИЙ TELEGRAM-БОТ - ВИПРАВЛЕНИЙ ЗАПУСК 🧠😂🔥
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Додаємо app/ до Python path
app_dir = Path(__file__).parent / "app"
if app_dir.exists():
    sys.path.insert(0, str(app_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def main():
    """ВИПРАВЛЕНА async функція запуску"""
    print("🧠😂🔥 Starting Ukrainian Telegram Bot...")
    
    try:
        # Перевірка змінних
        if not os.getenv('BOT_TOKEN'):
            logger.error("❌ BOT_TOKEN не встановлено!")
            return
        
        # Імпорт app/main.py
        logger.info("📂 Importing app/main.py...")
        from main import main as app_main
        
        logger.info("✅ Found main() function in app/main.py")
        
        # ПРАВИЛЬНИЙ async виклик
        await app_main()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        
        # Fallback мінімальний бот
        try:
            from aiogram import Bot, Dispatcher
            from aiogram.client.default import DefaultBotProperties
            from aiogram.enums import ParseMode
            from aiogram.filters import Command
            from aiogram.types import Message
            
            bot = Bot(
                token=os.getenv('BOT_TOKEN'),
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            dp = Dispatcher()
            
            @dp.message(Command("start"))
            async def start_cmd(message: Message):
                await message.answer("🤖 Bot is working in basic mode!")
            
            logger.info("✅ Fallback bot started")
            await dp.start_polling(bot)
            
        except Exception as fallback_error:
            logger.error(f"❌ Fallback error: {fallback_error}")

if __name__ == "__main__":
    asyncio.run(main())