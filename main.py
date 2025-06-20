#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ВИПРАВЛЕНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ - ГОЛОВНИЙ ФАЙЛ 🧠😂🔥

КРИТИЧНІ ВИПРАВЛЕННЯ:
✅ Proper async/await запуск app/main.py  
✅ UTF-8 Safe кодування
✅ Правильна обробка помилок
✅ Сумісність з Railway deployment
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Додаємо папку app/ до Python path
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
if app_dir.exists():
    sys.path.insert(0, str(app_dir))

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Перевірка критичних змінних середовища"""
    required_vars = ['BOT_TOKEN', 'ADMIN_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Відсутні змінні середовища: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Змінні середовища перевірені")
    return True

async def start_bot():
    """Запуск основного бота з app/main.py"""
    try:
        logger.info("🔍 Імпорт модуля app/main.py...")
        
        # Імпорт головної функції з app/main.py
        from main import main as app_main
        
        logger.info("✅ Знайдено функцію main() в app/main.py")
        
        # ПРАВИЛЬНИЙ async/await виклик
        logger.info("🚀 Запуск україномовного бота...")
        await app_main()
        
    except ImportError as e:
        logger.error(f"❌ Помилка імпорту app/main.py: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Помилка запуску бота: {e}")
        raise

async def fallback_mode():
    """Мінімальний бот при критичних помилках"""
    logger.warning("⚠️ Запуск у fallback режимі...")
    
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
        async def start_handler(message: Message):
            await message.answer(
                "🤖 Бот працює в базовому режимі.\n"
                "Перевірте логи для деталей."
            )
        
        logger.info("✅ Fallback бот налаштований")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Навіть fallback режим не працює: {e}")

async def main():
    """Головна функція - ПРАВИЛЬНИЙ async/await"""
    print("🧠😂🔥" * 20)
    print("\n🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОТ З ПРОФЕСІЙНИМИ ФУНКЦІЯМИ 🚀")
    print("🔧 ВИПРАВЛЕНА ВЕРСІЯ - CRITICAL FIXES APPLIED")
    print("🧠😂🔥" * 20)
    print()
    
    try:
        # Перевірка середовища
        if not check_environment():
            logger.error("❌ Критичні помилки конфігурації!")
            return
        
        # Перевірка структури
        if not app_dir.exists():
            logger.error("❌ Папка app/ не знайдена!")
            logger.info("📁 Поточна структура:")
            for item in current_dir.iterdir():
                logger.info(f"  - {item.name}")
            return
        
        logger.info("✅ Структура проекту перевірена")
        
        # Запуск основного бота
        await start_bot()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}")
        logger.info("🔄 Спроба запуску у fallback режимі...")
        
        try:
            await fallback_mode()
        except Exception as fallback_error:
            logger.error(f"❌ Fallback також не працює: {fallback_error}")

if __name__ == "__main__":
    # ПРАВИЛЬНИЙ запуск async функції
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Програма зупинена")
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        sys.exit(1)