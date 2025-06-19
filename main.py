#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 УКРАЇНОМОВНИЙ TELEGRAM-БОТ - ГОЛОВНИЙ ФАЙЛ 🧠😂🔥

Точка входу для Railway deployment
Запускає бота з папки app/
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Додаємо папку app/ до Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Налаштування професійного логування
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
        # Перевірка структури проекту
        logger.info("📂 Перевірка структури проекту...")
        
        if not app_dir.exists():
            logger.error("❌ Папка app/ не знайдена!")
            return run_minimal_bot()
        
        # Перевірка необхідних папок
        required_dirs = ["config", "database", "handlers"]
        for dir_name in required_dirs:
            dir_path = app_dir / dir_name
            if dir_path.exists():
                logger.info(f"✅ Знайдена папка app/{dir_name}/")
            else:
                logger.warning(f"⚠️ Папка app/{dir_name}/ не знайдена")
        
        # Спроба запуску основного бота з app/main.py
        logger.info("🚀 Запуск основного бота з app/main.py...")
        
        # Імпорт та запуск головної функції з app/main.py
        try:
            # Спроба імпорту main функції
            import main as app_main
            
            # Перевірка чи є функція main
            if hasattr(app_main, 'main'):
                logger.info("✅ Знайдено функцію main() в app/main.py")
                app_main.main()
            elif hasattr(app_main, 'UkrainianTelegramBot'):
                logger.info("✅ Знайдено клас UkrainianTelegramBot в app/main.py")
                bot = app_main.UkrainianTelegramBot()
                asyncio.run(bot.main())
            else:
                logger.warning("⚠️ Не знайдено entry point в app/main.py")
                # Пошук інших можливих entry points
                logger.info("🔍 Пошук альтернативних entry points...")
                
                # Спроба знайти і викликати будь-яку async функцію
                for attr_name in dir(app_main):
                    attr = getattr(app_main, attr_name)
                    if asyncio.iscoroutinefunction(attr) and not attr_name.startswith('_'):
                        logger.info(f"🎯 Спроба запуску {attr_name}()")
                        asyncio.run(attr())
                        return
                
                # Fallback до мінімального бота
                logger.warning("⚠️ Entry point не знайдено, запуск мінімального бота")
                return run_minimal_bot()
                
        except ImportError as e:
            logger.error(f"❌ Помилка імпорту app/main.py: {e}")
            return run_minimal_bot()
        except Exception as e:
            logger.error(f"❌ Помилка запуску app/main.py: {e}")
            return run_minimal_bot()
            
    except KeyboardInterrupt:
        logger.info("⏹️ Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        return run_minimal_bot()

def run_minimal_bot():
    """Мінімальний бот у випадку проблем з основним"""
    
    logger.info("🆘 Запуск мінімального бота...")
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from aiogram.filters import Command
        from aiogram.types import Message
        
        # Отримання токена
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.error("❌ BOT_TOKEN не знайдено в змінних середовища!")
            return
        
        admin_id = os.getenv("ADMIN_ID")
        
        # Створення бота з правильним API
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        )
        dp = Dispatcher()
        
        @dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                "🧠😂🔥 <b>Вітаю!</b>\n\n"
                "Це мінімальна версія україномовного бота.\n"
                "Основна функціональність тимчасово недоступна.\n\n"
                "🔧 <i>Звертайтеся до розробника для налаштування.</i>\n\n"
                f"👤 <b>Ваш ID:</b> <code>{message.from_user.id}</code>"
            )
            
            # Повідомлення адміністратору про використання fallback
            if admin_id:
                try:
                    await bot.send_message(
                        admin_id,
                        f"⚠️ <b>FALLBACK БОТ АКТИВНИЙ</b>\n\n"
                        f"Користувач {message.from_user.full_name} "
                        f"(ID: {message.from_user.id}) використав /start\n\n"
                        f"Основний бот недоступний - перевірте конфігурацію."
                    )
                except:
                    pass
        
        @dp.message(Command("help"))
        async def cmd_help(message: Message):
            await message.answer(
                "📱 <b>Доступні команди мінімального бота:</b>\n\n"
                "/start - початок роботи\n"
                "/help - ця довідка\n"
                "/status - статус бота\n\n"
                "🚧 <i>Основні функції у розробці...</i>"
            )
        
        @dp.message(Command("status"))
        async def cmd_status(message: Message):
            await message.answer(
                "🔧 <b>Статус мінімального бота:</b>\n\n"
                "✅ Базові команди працюють\n"
                "❌ Основна функціональність недоступна\n"
                "❌ База даних недоступна\n"
                "❌ Гейміфікація недоступна\n\n"
                "🔄 <i>Зверніться до адміністратора</i>"
            )
        
        # Запуск polling
        logger.info("🤖 Мінімальний бот запущено...")
        
        async def start_minimal_polling():
            try:
                # Тест з'єднання
                bot_info = await bot.get_me()
                logger.info(f"✅ Мінімальний бот підключений: @{bot_info.username}")
                
                # Повідомлення адміністратору
                if admin_id:
                    try:
                        await bot.send_message(
                            admin_id,
                            "🆘 <b>МІНІМАЛЬНИЙ БОТ ЗАПУЩЕНО</b>\n\n"
                            "Основна функціональність недоступна.\n"
                            "Перевірте конфігурацію app/main.py\n\n"
                            "🔧 Доступні команди: /start, /help, /status"
                        )
                    except:
                        pass
                
                # Polling
                await dp.start_polling(bot)
                
            except Exception as e:
                logger.error(f"❌ Помилка мінімального бота: {e}")
        
        asyncio.run(start_minimal_polling())
        
    except ImportError as e:
        logger.error(f"❌ Критична помилка - aiogram не встановлено: {e}")
    except Exception as e:
        logger.error(f"❌ Критична помилка мінімального бота: {e}")

if __name__ == "__main__":
    main()