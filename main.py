#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ВИПРАВЛЕНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ - ГОЛОВНИЙ ФАЙЛ 🧠😂🔥

СТРУКТУРА ПРОЕКТУ:
ukrainian-telegram-bot/
├── main.py                    # ← ЦЕЙ ФАЙЛ (корінь)
├── app/main.py               # ← Основний код бота
├── deployment/
│   ├── railway.json          # ← Railway конфігурація
│   ├── Procfile              # ← Процеси
│   └── requirements.txt      # ← Залежності deployment
├── requirements.txt          # ← Основні залежності
└── app/{config,database,handlers,services,utils}/

ВИПРАВЛЕННЯ:
✅ Правильний async/await запуск app/main.py
✅ Обробка помилок імпорту з правильною структурою
✅ Fallback до мінімального бота
✅ Професійне логування
✅ Сумісність з Railway deployment
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Додаємо папку app/ до Python path (з урахуванням структури)
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(current_dir))

# Налаштування професійного логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """🔧 ВИПРАВЛЕНА головна функція запуску"""
    
    print("🧠😂🔥" * 20)
    print("\n🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОT З ГЕЙМІФІКАЦІЄЮ 🚀")
    print("🔧 ВИПРАВЛЕНА ВЕРСІЯ З PROPER ASYNC/AWAIT")
    print("🧠😂🔥" * 20)
    print()
    
    try:
        # Перевірка структури проекту
        logger.info("📂 Перевірка структури проекту...")
        
        if not app_dir.exists():
            logger.error("❌ Папка app/ не знайдена!")
            return await run_minimal_bot()
        
        # Перевірка необхідних папок
        required_dirs = ["config", "database", "handlers"]
        for dir_name in required_dirs:
            dir_path = app_dir / dir_name
            if dir_path.exists():
                logger.info(f"✅ Знайдена папка app/{dir_name}/")
            else:
                logger.warning(f"⚠️ Папка app/{dir_name}/ не знайдена")
        
        # 🔧 ВИПРАВЛЕННЯ: Правильний асинхронний запуск основного бота
        logger.info("🚀 Запуск основного бота з app/main.py...")
        
        try:
            # Спроба імпорту main функції
            import main as app_main
            
            # Перевірка чи є функція main
            if hasattr(app_main, 'main'):
                logger.info("✅ Знайдено функцію main() в app/main.py")
                # 🔧 КРИТИЧНЕ ВИПРАВЛЕННЯ: await замість синхронного виклику
                return await app_main.main()
                
            elif hasattr(app_main, 'UkrainianTelegramBot'):
                logger.info("✅ Знайдено клас UkrainianTelegramBot в app/main.py")
                bot = app_main.UkrainianTelegramBot()
                return await bot.main()
            else:
                logger.warning("⚠️ Не знайдено entry point в app/main.py")
                # Пошук інших можливих entry points
                logger.info("🔍 Пошук альтернативних entry points...")
                
                # Спроба знайти і викликати будь-яку async функцію
                for attr_name in dir(app_main):
                    attr = getattr(app_main, attr_name)
                    if asyncio.iscoroutinefunction(attr) and not attr_name.startswith('_'):
                        logger.info(f"🎯 Спроба запуску {attr_name}()")
                        return await attr()
                
                # Fallback до мінімального бота
                logger.warning("⚠️ Entry point не знайдено, запуск мінімального бота")
                return await run_minimal_bot()
                
        except ImportError as e:
            logger.error(f"❌ Помилка імпорту app/main.py: {e}")
            return await run_minimal_bot()
        except Exception as e:
            logger.error(f"❌ Помилка запуску app/main.py: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return await run_minimal_bot()
            
    except KeyboardInterrupt:
        logger.info("⏹️ Бот зупинено користувачем")
        return True
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return await run_minimal_bot()

async def run_minimal_bot():
    """🆘 Мінімальний бот у випадку проблем з основним"""
    
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
            return False
        
        admin_id = os.getenv("ADMIN_ID")
        
        # Створення бота з правильними налаштуваннями
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )
        
        dp = Dispatcher()
        
        # Основні команди мінімального бота
        @dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                "🧠😂🔥 <b>Мінімальний режим роботи</b>\n\n"
                "Бот працює в базовому режимі через технічні роботи.\n"
                "Скоро всі функції будуть відновлені!"
            )
        
        @dp.message(Command("help"))
        async def cmd_help(message: Message):
            await message.answer(
                "🤖 <b>Доступні команди:</b>\n\n"
                "/start - запуск бота\n"
                "/help - ця довідка\n"
                "/status - статус бота"
            )
        
        @dp.message(Command("status"))
        async def cmd_status(message: Message):
            await message.answer(
                "⚠️ <b>Мінімальний режим</b>\n\n"
                "Статус: Працює в базовому режимі\n"
                "Режим: Відновлення після помилки\n"
                "Час: Кілька хвилин"
            )
        
        # Повідомлення адміністратора про мінімальний режим
        if admin_id:
            try:
                await bot.send_message(
                    int(admin_id),
                    "⚠️ <b>БОТ ЗАПУЩЕНО В МІНІМАЛЬНОМУ РЕЖИМІ</b>\n\n"
                    "Причина: Помилка завантаження основного модуля\n"
                    "Перевірте логи для деталей"
                )
            except:
                pass
        
        logger.info("✅ Мінімальний бот готовий до роботи")
        
        # Запуск polling
        await dp.start_polling(bot, skip_updates=True)
        return True
        
    except Exception as e:
        logger.error(f"💥 Критична помилка мінімального бота: {e}")
        return False

def sync_main():
    """Синхронна точка входу для Python"""
    try:
        # 🔧 ВИПРАВЛЕННЯ: Правильний запуск async функції
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Зупинка через Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Неочікувана помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_main()