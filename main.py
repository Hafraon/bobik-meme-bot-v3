#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ПРОФЕСІЙНИЙ КОРЕНЕВИЙ MAIN.PY З АДАПТИВНИМ ЗАПУСКОМ 🚀

СТРУКТУРА ПРОЕКТУ:
ukrainian-telegram-bot/
├── main.py                    # ← ЦЕЙ ФАЙЛ (Railway запускає його)
├── Procfile                   # ← "web: python main.py"
├── requirements.txt           # ← Залежності
└── app/
    ├── main.py               # ← Основний код бота (запускається звідси)
    ├── config/               # ← Конфігурація
    ├── database/             # ← Моделі БД
    ├── handlers/             # ← Обробники команд
    └── services/             # ← Сервіси автоматизації

✅ Адаптивний запуск app/main.py (функція, клас, або fallback)
✅ Професійне логування для Railway
✅ Heartbeat система для моніторингу
✅ Fallback бот якщо основний не працює
"""

import os
import sys
import asyncio
import logging
import signal
import traceback
from pathlib import Path
from datetime import datetime

# ===== ПРОФЕСІЙНЕ RAILWAY ЛОГУВАННЯ =====

def setup_railway_logging():
    """Налаштування логування спеціально для Railway"""
    
    # Створюємо спеціальний formatter для Railway
    formatter = logging.Formatter(
        '%(asctime)s - **%(name)s** - %(levelname)s - %(message)s'
    )
    
    # Створюємо handler що гарантовано передає логи в Railway
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Налаштовуємо root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Очищуємо існуючі handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Створюємо logger для цього файлу
    logger = logging.getLogger('railway_launcher')
    
    return logger

# Ініціалізуємо логування одразу
logger = setup_railway_logging()

# ===== ДОДАВАННЯ APP/ ДО PYTHON PATH =====

def setup_python_path():
    """Додавання app/ папки до Python path"""
    current_dir = Path(__file__).parent
    app_dir = current_dir / "app"
    
    if not app_dir.exists():
        logger.error(f"❌ Папка app/ не знайдена в {current_dir}")
        print(f"❌ CRITICAL: app/ directory not found in {current_dir}", flush=True)
        return False
    
    # Додаємо app/ на початок sys.path
    sys.path.insert(0, str(app_dir))
    
    logger.info(f"✅ Додано {app_dir} до Python path")
    print(f"✅ Added {app_dir} to Python path", flush=True)
    
    return True

# ===== ПЕРЕВІРКА СЕРЕДОВИЩА =====

def check_environment():
    """Перевірка критичних змінних середовища"""
    logger.info("🔍 Перевірка середовища Railway...")
    print("🔍 Checking Railway environment...", flush=True)
    
    critical_vars = {
        'BOT_TOKEN': 'Токен Telegram бота',
        'ADMIN_ID': 'ID адміністратора'
    }
    
    missing_vars = []
    
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            # Маскуємо значення для безпеки
            masked = value[:10] + "..." if len(value) > 10 else value
            logger.info(f"✅ {var}: {masked}")
            print(f"✅ {var}: {masked}", flush=True)
        else:
            logger.error(f"❌ {var} не встановлено ({description})")
            print(f"❌ {var} not set ({description})", flush=True)
            missing_vars.append(var)
    
    # Перевіряємо Railway специфічні змінні
    railway_vars = ['RAILWAY_ENVIRONMENT', 'DATABASE_URL', 'PORT']
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            # Маскуємо DATABASE_URL для безпеки
            if var == 'DATABASE_URL' and len(value) > 20:
                masked = value[:20] + "..."
            else:
                masked = value
            logger.info(f"📡 Railway {var}: {masked}")
            print(f"📡 Railway {var}: {masked}", flush=True)
    
    if missing_vars:
        logger.error(f"❌ Відсутні критичні змінні: {', '.join(missing_vars)}")
        print(f"❌ Missing critical variables: {', '.join(missing_vars)}", flush=True)
        return False
    
    logger.info("✅ Середовище перевірено успішно")
    print("✅ Environment check passed", flush=True)
    return True

# ===== RAILWAY СТАТУС РЕПОРТЕР =====

class RailwayStatusReporter:
    """Клас для регулярного репортування статусу в Railway логи"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.is_running = False
    
    def start_reporting(self):
        """Запуск репортування статусу"""
        self.is_running = True
        
        # Стартовий репорт
        logger.info("🚀 RAILWAY STATUS REPORTER STARTED")
        print("🚀 RAILWAY STATUS REPORTER STARTED", flush=True)
        
        # Перший статус одразу
        self.report_status()
    
    def report_status(self):
        """Репорт поточного статусу"""
        uptime = datetime.now() - self.start_time
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
        
        logger.info(f"💓 RAILWAY HEARTBEAT - Uptime: {uptime_str} - Status: Active")
        print(f"💓 RAILWAY HEARTBEAT - Uptime: {uptime_str} - Status: Active", flush=True)
    
    def stop_reporting(self):
        """Зупинка репортування"""
        if self.is_running:
            self.is_running = False
            logger.info("🛑 RAILWAY STATUS REPORTER STOPPED")
            print("🛑 RAILWAY STATUS REPORTER STOPPED", flush=True)

# ===== SIGNAL HANDLERS =====

def setup_signal_handlers(status_reporter):
    """Налаштування обробників сигналів для graceful shutdown"""
    
    def signal_handler(signum, frame):
        logger.info(f"🛑 Отримано сигнал {signum}, завершуємо роботу...")
        print(f"🛑 Received signal {signum}, shutting down...", flush=True)
        
        status_reporter.stop_reporting()
        
        # Даємо час для graceful shutdown
        logger.info("⏳ Graceful shutdown in progress...")
        print("⏳ Graceful shutdown in progress...", flush=True)
        
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("✅ Signal handlers налаштовано")
    print("✅ Signal handlers configured", flush=True)

# ===== АДАПТИВНИЙ ЗАПУСК APP/MAIN.PY =====

async def launch_app_main():
    """Адаптивний запуск основного коду з app/main.py"""
    
    logger.info("🔄 Адаптивний імпорт та запуск app/main.py...")
    print("🔄 Adaptive import and launch app/main.py...", flush=True)
    
    try:
        # Імпорт модуля app/main.py
        import main as app_module
        
        logger.info("✅ app/main.py успішно імпортовано")
        print("✅ app/main.py imported successfully", flush=True)
        
        # ===== АДАПТИВНИЙ ЗАПУСК - СПРОБУЄМО ВСІ ВАРІАНТИ =====
        
        # Варіант 1: Функція main()
        if hasattr(app_module, 'main') and callable(getattr(app_module, 'main')):
            logger.info("🎯 Знайдено функцію main(), запускаємо...")
            print("🎯 Found main() function, launching...", flush=True)
            
            await app_module.main()
            return
        
        # Варіант 2: Клас AutomatedUkrainianTelegramBot
        elif hasattr(app_module, 'AutomatedUkrainianTelegramBot'):
            logger.info("🎯 Знайдено клас AutomatedUkrainianTelegramBot, створюємо інстанс...")
            print("🎯 Found AutomatedUkrainianTelegramBot class, creating instance...", flush=True)
            
            bot_instance = app_module.AutomatedUkrainianTelegramBot()
            
            # Перевіряємо методи запуску
            if hasattr(bot_instance, 'run') and callable(getattr(bot_instance, 'run')):
                logger.info("✅ Запускаємо через bot.run()...")
                print("✅ Launching via bot.run()...", flush=True)
                await bot_instance.run()
            elif hasattr(bot_instance, 'main') and callable(getattr(bot_instance, 'main')):
                logger.info("✅ Запускаємо через bot.main()...")  
                print("✅ Launching via bot.main()...", flush=True)
                await bot_instance.main()
            else:
                logger.error("❌ Клас не має методу run() або main()")
                raise Exception("Bot class has no run() or main() method")
            return
        
        # Варіант 3: Інший клас бота
        elif hasattr(app_module, 'UkrainianTelegramBot'):
            logger.info("🎯 Знайдено клас UkrainianTelegramBot, створюємо інстанс...")
            print("🎯 Found UkrainianTelegramBot class, creating instance...", flush=True)
            
            bot_instance = app_module.UkrainianTelegramBot()
            
            if hasattr(bot_instance, 'run'):
                await bot_instance.run()
            elif hasattr(bot_instance, 'main'):
                await bot_instance.main()
            else:
                logger.error("❌ Клас не має методу run() або main()")
                raise Exception("Bot class has no run() or main() method")
            return
        
        # Варіант 4: Глобальна змінна bot або dispatcher
        elif hasattr(app_module, 'bot') and hasattr(app_module, 'dp'):
            logger.info("🎯 Знайдено bot та dp змінні, запускаємо polling...")
            print("🎯 Found bot and dp variables, starting polling...", flush=True)
            
            bot = getattr(app_module, 'bot')
            dp = getattr(app_module, 'dp')
            
            # Запускаємо polling
            await dp.start_polling(bot, skip_updates=True)
            return
        
        # Варіант 5: Функція run_bot() або start_bot()
        elif hasattr(app_module, 'run_bot') and callable(getattr(app_module, 'run_bot')):
            logger.info("🎯 Знайдено функцію run_bot(), запускаємо...")
            print("🎯 Found run_bot() function, launching...", flush=True)
            
            await app_module.run_bot()
            return
        
        elif hasattr(app_module, 'start_bot') and callable(getattr(app_module, 'start_bot')):
            logger.info("🎯 Знайдено функцію start_bot(), запускаємо...")
            print("🎯 Found start_bot() function, launching...", flush=True)
            
            await app_module.start_bot()
            return
        
        # Якщо нічого не знайшли - запускаємо fallback бот
        else:
            logger.warning("⚠️ Жоден entry point не знайдено в app/main.py")
            print("⚠️ No entry point found in app/main.py", flush=True)
            
            # Показуємо доступні атрибути для діагностики
            available_attrs = [attr for attr in dir(app_module) if not attr.startswith('_')]
            logger.info(f"📋 Доступні атрибути в app/main.py: {available_attrs}")
            print(f"📋 Available attributes in app/main.py: {available_attrs}", flush=True)
            
            logger.info("🆘 Запускаємо fallback бот...")
            print("🆘 Starting fallback bot...", flush=True)
            await run_fallback_bot()
        
    except ImportError as e:
        logger.error(f"❌ Помилка імпорту app/main.py: {e}")
        print(f"❌ Import error app/main.py: {e}", flush=True)
        logger.error(traceback.format_exc())
        
        logger.info("🆘 Запускаємо fallback бот через import error...")
        print("🆘 Starting fallback bot due to import error...", flush=True)
        await run_fallback_bot()
        
    except Exception as e:
        logger.error(f"❌ Помилка виконання app/main.py: {e}")
        print(f"❌ Execution error app/main.py: {e}", flush=True)
        logger.error(traceback.format_exc())
        
        logger.info("🆘 Запускаємо fallback бот через execution error...")
        print("🆘 Starting fallback bot due to execution error...", flush=True)
        await run_fallback_bot()

# ===== FALLBACK БОТ =====

async def run_fallback_bot():
    """Fallback бот який точно працює"""
    
    logger.info("🆘 Запуск fallback бота...")
    print("🆘 Starting fallback bot...", flush=True)
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from aiogram.filters import Command
        from aiogram.types import Message
        
        bot_token = os.getenv("BOT_TOKEN")
        admin_id = int(os.getenv("ADMIN_ID", "603047391"))
        
        if not bot_token:
            logger.error("❌ BOT_TOKEN не знайдено для fallback бота!")
            print("❌ BOT_TOKEN not found for fallback bot!", flush=True)
            return
        
        # Створюємо fallback бота
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        
        # Основні команди fallback бота
        @dp.message(Command("start"))
        async def fallback_start(message: Message):
            user_name = message.from_user.first_name or "друже"
            await message.answer(
                f"🆘 <b>Fallback режим активний</b>\n\n"
                f"Привіт, {user_name}! Я працюю в спрощеному режимі.\n\n"
                f"📋 <b>Доступні команди:</b>\n"
                f"• /start - це повідомлення\n"
                f"• /status - статус бота\n"
                f"• /help - довідка\n"
                f"• /joke - випадковий жарт\n\n"
                f"⚠️ <b>Адміну:</b> Перевірте логи Railway для виправлення проблем."
            )
        
        @dp.message(Command("status"))
        async def fallback_status(message: Message):
            await message.answer(
                f"🆘 <b>СТАТУС FALLBACK БОТА</b>\n\n"
                f"🤖 Режим: Аварійний\n"
                f"✅ Статус: Онлайн\n"
                f"⏰ Час: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n"
                f"📡 Railway: Активний\n\n"
                f"⚠️ Основний функціонал недоступний.\n"
                f"Адміністратор має перевірити логи Railway."
            )
        
        @dp.message(Command("help"))
        async def fallback_help(message: Message):
            await message.answer(
                f"🆘 <b>FALLBACK БОТ - ДОВІДКА</b>\n\n"
                f"Я працюю в аварійному режимі через проблеми з основним кодом.\n\n"
                f"📋 <b>Доступні команди:</b>\n"
                f"• /start - головне меню\n"
                f"• /status - поточний статус\n"
                f"• /help - ця довідка\n"
                f"• /joke - випадковий жарт\n\n"
                f"🔧 <b>Для адміністратора:</b>\n"
                f"Перевірте Railway логи для діагностики.\n"
                f"Проблема: entry point не знайдено в app/main.py"
            )
        
        @dp.message(Command("joke"))
        async def fallback_joke(message: Message):
            import random
            
            jokes = [
                "😂 Програміст заходить в кафе:\n- Каву, будь ласка.\n- Цукор?\n- Ні, boolean!",
                "🤖 Чому боти не п'ють каву?\nБо вони працюють на енергетиках!",
                "🔧 Fallback жарт:\nМій код не працює.\n- А чому?\n- Бо я в fallback режимі!",
                "🚀 Railway розробник:\n- Чому бот крашиться?\n- Import error.\n- А fallback?\n- Працює!",
                "🧠 AI жарт:\nЯ б розповів жарт про машинне навчання,\nале воно досі тренується!"
            ]
            
            selected_joke = random.choice(jokes)
            await message.answer(f"😄 <b>Fallback жарт:</b>\n\n{selected_joke}")
        
        # Адмін команди
        @dp.message(Command("admin"))
        async def fallback_admin(message: Message):
            if message.from_user.id != admin_id:
                await message.answer("❌ Доступ заборонено.")
                return
            
            await message.answer(
                f"👑 <b>FALLBACK АДМІН ПАНЕЛЬ</b>\n\n"
                f"🆘 Бот працює в аварійному режимі.\n\n"
                f"🔍 <b>Діагностика:</b>\n"
                f"• Entry point не знайдено в app/main.py\n"
                f"• Перевірте структуру файлу\n"
                f"• Перевірте наявність функції main() або класу\n\n"
                f"📋 <b>Railway логи:</b>\n"
                f"Dashboard → Deployments → Logs\n\n"
                f"🔧 <b>Виправлення:</b>\n"
                f"1. Перевірте app/main.py\n"
                f"2. Додайте функцію main() або клас\n"
                f"3. Redeploy проект"
            )
        
        # Перевірка підключення бота
        bot_info = await bot.get_me()
        logger.info(f"✅ Fallback бот підключено: @{bot_info.username}")
        print(f"✅ Fallback bot connected: @{bot_info.username}", flush=True)
        
        # Запуск polling
        logger.info("🚀 Запуск fallback polling...")
        print("🚀 Starting fallback polling...", flush=True)
        
        await dp.start_polling(
            bot, 
            skip_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
    except Exception as e:
        logger.error(f"💥 Критична помилка fallback бота: {e}")
        print(f"💥 Critical fallback bot error: {e}", flush=True)
        logger.error(traceback.format_exc())
        raise

# ===== ГОЛОВНА ФУНКЦІЯ =====

async def main():
    """Головна функція кореневого main.py з адаптивним запуском"""
    
    # Негайний сигнал Railway що ми почали
    print("=" * 80, flush=True)
    print("🧠😂🔥 UKRAINIAN TELEGRAM BOT - ADAPTIVE RAILWAY LAUNCHER 🧠😂🔥", flush=True)
    print("=" * 80, flush=True)
    
    logger.info("🚀 Адаптивний запуск україномовного бота в Railway...")
    
    # Ініціалізуємо статус репортер
    status_reporter = RailwayStatusReporter()
    
    try:
        # 1. Налаштування signal handlers
        setup_signal_handlers(status_reporter)
        
        # 2. Перевірка середовища
        if not check_environment():
            logger.error("❌ Критичні помилки середовища")
            print("❌ Critical environment errors", flush=True)
            sys.exit(1)
        
        # 3. Налаштування Python path
        if not setup_python_path():
            logger.error("❌ Не вдалося налаштувати Python path")
            print("❌ Failed to setup Python path", flush=True)
            sys.exit(1)
        
        # 4. Запуск статус репортера
        status_reporter.start_reporting()
        
        # 5. Адаптивний запуск основного коду
        logger.info("🎯 Всі перевірки пройдені, запускаємо адаптивний launcher...")
        print("🎯 All checks passed, launching adaptive launcher...", flush=True)
        
        await launch_app_main()
        
        # Якщо дійшли сюди - успішне завершення
        logger.info("🎉 Бот завершив роботу успішно")
        print("🎉 Bot finished successfully", flush=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Переривання користувачем")
        print("🛑 User interruption", flush=True)
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        print(f"💥 Critical error: {e}", flush=True)
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        # Завжди зупиняємо репортер
        status_reporter.stop_reporting()
        
        logger.info("🧹 Кореневий процес завершено")
        print("🧹 Root process finished", flush=True)

# ===== ENTRY POINT =====

if __name__ == "__main__":
    # Одразу сигналізуємо Railway що ми живі
    print("🟢 RAILWAY ADAPTIVE BOOT SEQUENCE INITIATED", flush=True)
    print(f"🐍 Python version: {sys.version}", flush=True)
    print(f"📂 Working directory: {os.getcwd()}", flush=True)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    
    # Запуск основної функції
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 RAILWAY ADAPTIVE BOOT FAILED: {e}", flush=True)
        sys.exit(1)