#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ПРОФЕСІЙНИЙ КОРЕНЕВИЙ MAIN.PY ДЛЯ RAILWAY 🚀

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

✅ Виправлене логування для Railway
✅ Професійна структура запуску
✅ Правильна передача stdout/stderr
✅ Heartbeat система для моніторингу
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

# ===== ОСНОВНА ФУНКЦІЯ ЗАПУСКУ =====

async def launch_app_main():
    """Запуск основного коду з app/main.py"""
    
    logger.info("🔄 Імпорт та запуск app/main.py...")
    print("🔄 Importing and launching app/main.py...", flush=True)
    
    try:
        # Імпорт основного модуля
        from main import main as app_main
        
        logger.info("✅ app/main.py успішно імпортовано")
        print("✅ app/main.py imported successfully", flush=True)
        
        # Запуск основного коду
        logger.info("🚀 Запуск основної функції бота...")
        print("🚀 Starting main bot function...", flush=True)
        
        await app_main()
        
        logger.info("✅ app/main.py завершено успішно")
        print("✅ app/main.py finished successfully", flush=True)
        
    except ImportError as e:
        logger.error(f"❌ Помилка імпорту app/main.py: {e}")
        print(f"❌ Import error app/main.py: {e}", flush=True)
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"❌ Помилка виконання app/main.py: {e}")
        print(f"❌ Execution error app/main.py: {e}", flush=True)
        logger.error(traceback.format_exc())
        raise

# ===== ГОЛОВНА ФУНКЦІЯ =====

async def main():
    """Головна функція кореневого main.py"""
    
    # Негайний сигнал Railway що ми почали
    print("=" * 80, flush=True)
    print("🧠😂🔥 UKRAINIAN TELEGRAM BOT - RAILWAY PROFESSIONAL LAUNCHER 🧠😂🔥", flush=True)
    print("=" * 80, flush=True)
    
    logger.info("🚀 Професійний запуск україномовного бота в Railway...")
    
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
        
        # 5. Запуск основного коду
        logger.info("🎯 Всі перевірки пройдені, запускаємо основний код...")
        print("🎯 All checks passed, launching main code...", flush=True)
        
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
    print("🟢 RAILWAY BOOT SEQUENCE INITIATED", flush=True)
    print(f"🐍 Python version: {sys.version}", flush=True)
    print(f"📂 Working directory: {os.getcwd()}", flush=True)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    
    # Запуск основної функції
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 RAILWAY BOOT FAILED: {e}", flush=True)
        sys.exit(1)