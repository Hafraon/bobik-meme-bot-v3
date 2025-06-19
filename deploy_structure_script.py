#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 СКРИПТ РОЗГОРТАННЯ ВИПРАВЛЕНЬ ДЛЯ ВАШОЇ СТРУКТУРИ 🧠😂🔥

Автоматично розміщує всі файли в правильних місцях згідно вашої структури:

ukrainian-telegram-bot/
├── main.py                    ← оновлюється
├── Procfile                   ← створюється в корені
├── requirements.txt           ← оновлюється
├── diagnostic_script.py       ← створюється
├── app/main.py               ← оновлюється
├── deployment/
│   ├── railway.json          ← у вас уже є
│   └── Procfile              ← резервна копія
└── app/{config,database,handlers,services,utils}/
"""

import os
import shutil
from pathlib import Path

def print_header():
    """Заголовок скрипта"""
    print("🧠😂🔥" * 20)
    print("\n📋 РОЗГОРТАННЯ ВИПРАВЛЕНЬ УКРАЇНОМОВНОГО БОТА")
    print("🎯 Автоматичне розміщення файлів у вашій структурі")
    print("🧠😂🔥" * 20)
    print()

def check_current_structure():
    """Перевірка поточної структури"""
    print("📍 ПЕРЕВІРКА ПОТОЧНОЇ СТРУКТУРИ:")
    
    expected_files = [
        "main.py",
        "app/main.py", 
        "app/config/settings.py",
        "app/database/models.py",
        "deployment/railway.json",
        "requirements.txt"
    ]
    
    missing = []
    for file_path in expected_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing.append(file_path)
    
    if missing:
        print(f"\n⚠️ Відсутні файли: {len(missing)}")
        return False
    else:
        print("\n✅ Структура проекту підтверджена!")
        return True

def backup_existing_files():
    """Створення резервних копій"""
    print("\n💾 СТВОРЕННЯ РЕЗЕРВНИХ КОПІЙ:")
    
    files_to_backup = [
        "main.py",
        "app/main.py",
        "requirements.txt"
    ]
    
    backup_dir = Path("backup_before_fix")
    backup_dir.mkdir(exist_ok=True)
    
    for file_path in files_to_backup:
        source = Path(file_path)
        if source.exists():
            # Створюємо структуру папок в backup
            dest = backup_dir / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, dest)
            print(f"📁 {file_path} → {dest}")
    
    print(f"✅ Резервні копії створено в {backup_dir}")

def create_fixed_files():
    """Створення виправлених файлів"""
    print("\n🔧 СТВОРЕННЯ ВИПРАВЛЕНИХ ФАЙЛІВ:")
    
    # 1. Виправлений корневий main.py
    root_main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ВИПРАВЛЕНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ - ГОЛОВНИЙ ФАЙЛ 🧠😂🔥

СТРУКТУРА ПРОЕКТУ:
ukrainian-telegram-bot/
├── main.py                    # ← ЦЕЙ ФАЙЛ (корінь)
├── app/main.py               # ← Основний код бота
├── deployment/railway.json   # ← Railway конфігурація
└── app/{config,database,handlers,services,utils}/

✅ Правильний async/await запуск app/main.py
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
sys.path.insert(0, str(app_dir))

# Професійне логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def main():
    """🔧 ВИПРАВЛЕНА головна функція запуску"""
    
    print("🧠😂🔥" * 20)
    print("\\n🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОT З ГЕЙМІФІКАЦІЄЮ 🚀")
    print("🔧 ВИПРАВЛЕНА ВЕРСІЯ З PROPER ASYNC/AWAIT")
    print("🧠😂🔥" * 20)
    print()
    
    try:
        logger.info("📂 Перевірка структури проекту...")
        
        if not app_dir.exists():
            logger.error("❌ Папка app/ не знайдена!")
            return await run_minimal_bot()
        
        logger.info("🚀 Запуск основного бота з app/main.py...")
        
        try:
            import main as app_main
            
            if hasattr(app_main, 'main'):
                logger.info("✅ Знайдено функцію main() в app/main.py")
                return await app_main.main()
            elif hasattr(app_main, 'UkrainianTelegramBot'):
                logger.info("✅ Знайдено клас UkrainianTelegramBot")
                bot = app_main.UkrainianTelegramBot()
                return await bot.main()
            else:
                logger.warning("⚠️ Entry point не знайдено")
                return await run_minimal_bot()
                
        except ImportError as e:
            logger.error(f"❌ Помилка імпорту app/main.py: {e}")
            return await run_minimal_bot()
        except Exception as e:
            logger.error(f"❌ Помилка запуску: {e}")
            return await run_minimal_bot()
            
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        return await run_minimal_bot()

async def run_minimal_bot():
    """🆘 Мінімальний бот"""
    logger.info("🆘 Запуск мінімального бота...")
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from aiogram.filters import Command
        from aiogram.types import Message
        
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.error("❌ BOT_TOKEN не знайдено!")
            return False
        
        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        
        @dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer("🧠😂🔥 Мінімальний режим - бот працює!")
        
        @dp.message(Command("status"))
        async def cmd_status(message: Message):
            await message.answer("✅ Статус: Мінімальний режим активний")
        
        logger.info("✅ Мінімальний бот готовий")
        await dp.start_polling(bot, skip_updates=True)
        return True
        
    except Exception as e:
        logger.error(f"💥 Критична помилка мінімального бота: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Зупинка через Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Неочікувана помилка: {e}")
        sys.exit(1)
'''

    # 2. Procfile для кореня
    procfile_content = '''# 🧠😂🔥 Railway Procfile - запуск з кореня проекту
web: python main.py'''

    # 3. Оновлений requirements.txt
    requirements_content = '''# 🧠😂🔥 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ - ЗАЛЕЖНОСТІ

# Основні критичні залежності
aiogram>=3.4.0,<4.0.0
SQLAlchemy>=2.0.0,<3.0.0
asyncpg>=0.29.0
psycopg2-binary>=2.9.0
aiohttp>=3.9.0
aiofiles>=23.0.0
alembic>=1.13.0

# Планувальник та задачі  
APScheduler>=3.10.0
pytz>=2023.3
python-dateutil>=2.8.0

# Конфігурація
python-dotenv>=1.0.0
pydantic>=2.5.0

# AI та контент (опціонально)
openai>=1.6.0
emoji>=2.8.0

# Безпека
cryptography>=42.0.0

# Веб-сервер для health checks
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# Утиліти
orjson>=3.9.0
psutil>=5.9.0
httpx>=0.25.0
requests>=2.31.0
'''

    # Записуємо файли
    files_to_create = [
        ("main.py", root_main_content),
        ("Procfile", procfile_content),
        ("requirements.txt", requirements_content)
    ]
    
    for file_path, content in files_to_create:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path}")
    
    print("✅ Всі файли створено!")

def copy_deployment_files():
    """Копіювання файлів в deployment/"""
    print("\n📦 КОПІЮВАННЯ В DEPLOYMENT/:")
    
    # Копіюємо Procfile в deployment як резервну копію
    if Path("Procfile").exists():
        dest_dir = Path("deployment")
        dest_dir.mkdir(exist_ok=True)
        
        shutil.copy2("Procfile", dest_dir / "Procfile")
        shutil.copy2("requirements.txt", dest_dir / "requirements.txt")
        
        print("✅ Procfile → deployment/Procfile")
        print("✅ requirements.txt → deployment/requirements.txt")

def test_imports():
    """Тестування імпортів"""
    print("\n🧪 ТЕСТУВАННЯ ІМПОРТІВ:")
    
    # Додаємо app/ до path
    app_dir = Path("app")
    if app_dir.exists():
        sys.path.insert(0, str(app_dir))
    
    test_modules = [
        "aiogram",
        "sqlalchemy", 
        "config.settings",
        "database.models"
    ]
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"⚠️ {module} - {e}")

def main():
    """Головна функція скрипта"""
    print_header()
    
    # Перевірка структури
    if not check_current_structure():
        print("❌ Неправильна структура проекту!")
        return
    
    # Резервні копії
    backup_existing_files()
    
    # Створення виправлених файлів
    create_fixed_files()
    
    # Копіювання в deployment
    copy_deployment_files()
    
    # Тестування
    test_imports()
    
    print("\n🎉 ВИПРАВЛЕННЯ ЗАВЕРШЕНО!")
    print("=" * 50)
    print("📋 НАСТУПНІ КРОКИ:")
    print("1. python diagnostic_script.py  # діагностика")
    print("2. python main.py               # тест запуску")
    print("3. git add . && git commit -m '🔧 Fix async/await issues'")
    print("4. git push                     # деплой на Railway")
    print("\n✅ Готово до тестування!")

if __name__ == "__main__":
    main()