#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 УКРАЇНОМОВНИЙ TELEGRAM-БОТ - ГОЛОВНИЙ ФАЙЛ 🧠😂🔥

Точка входу для Railway deployment
Імпортує та запускає бота з папки app/
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Додаємо папку app/ до Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Налаштування базового логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Головна функція запуску"""
    
    print("🧠😂🔥" * 20)
    print("\n🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОT З ГЕЙМІФІКАЦІЄЮ 🚀\n")
    print("🧠😂🔥" * 20)
    print()
    
    try:
        # Спроба імпорту з app/
        logger.info("📂 Підключення модулів з app/...")
        
        # Перевірка наявності app/ папки
        if not app_dir.exists():
            logger.error("❌ Папка app/ не знайдена!")
            logger.info("📁 Поточна директорія:", os.getcwd())
            logger.info("📁 Список файлів:", os.listdir("."))
            return
        
        # Перевірка структури app/
        required_dirs = ["config", "database", "handlers"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = app_dir / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
                logger.warning(f"⚠️ Папка app/{dir_name}/ не знайдена")
            else:
                logger.info(f"✅ Знайдена папка app/{dir_name}/")
        
        if missing_dirs:
            logger.error(f"❌ Відсутні критичні папки: {missing_dirs}")
            logger.info("🔄 Спроба запуску fallback версії...")
            return run_fallback_bot()
        
        # Імпорт основного бота з app/
        try:
            from main import UkrainianTelegramBot
            logger.info("✅ Успішно імпортовано UkrainianTelegramBot з app/main.py")
        except ImportError as e:
            logger.error(f"❌ Помилка імпорту з app/main.py: {e}")
            return run_fallback_bot()
        
        # Запуск бота
        logger.info("🚀 Запуск основного бота...")
        bot = UkrainianTelegramBot()
        asyncio.run(bot.start())
        
    except KeyboardInterrupt:
        logger.info("⏹️ Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        logger.exception("Детальна інформація про помилку:")
        return run_fallback_bot()

def run_fallback_bot():
    """Fallback версія бота з мінімальною функціональністю"""
    
    logger.info("🆘 Запуск FALLBACK бота...")
    
    try:
        # Спроба імпорту bobik_bot.py з кореня
        if os.path.exists("bobik_bot.py"):
            logger.info("✅ Знайдено bobik_bot.py, запускаю...")
            import bobik_bot
            bobik_bot.main()
            return
        
        # Якщо немає bobik_bot.py, створюємо мінімальний бот
        logger.info("🔧 Створення мінімального бота...")
        return run_minimal_bot()
        
    except Exception as e:
        logger.error(f"❌ Fallback бот також не запустився: {e}")
        logger.info("📱 Перевірте налаштування BOT_TOKEN в змінних середовища")

def run_minimal_bot():
    """Мінімальний бот тільки з базовими функціями"""
    
    import os
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.filters import Command
    from aiogram.types import Message
    
    # Отримання токена
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("❌ BOT_TOKEN не знайдено в змінних середовища!")
        return
    
    # Створення бота
    bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer(
            "🧠😂🔥 <b>Вітаю!</b>\n\n"
            "Це мінімальна версія україномовного бота.\n"
            "Повна функціональність тимчасово недоступна.\n\n"
            "🔧 <i>Зверніться до розробника для налаштування.</i>"
        )
    
    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        await message.answer(
            "📱 <b>Доступні команди:</b>\n\n"
            "/start - початок роботи\n"
            "/help - ця довідка\n\n"
            "🚧 <i>Інші функції у розробці...</i>"
        )
    
    # Запуск поллінгу
    logger.info("🤖 Мінімальний бот запущено в режимі polling...")
    
    async def start_polling():
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"❌ Помилка polling: {e}")
    
    asyncio.run(start_polling())

if __name__ == "__main__":
    main()