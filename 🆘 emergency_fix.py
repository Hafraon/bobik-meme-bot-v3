#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🆘 СКРИПТ ЕКСТРЕНОГО ВИПРАВЛЕННЯ УКРАЇНСЬКОГО TELEGRAM БОТА

Автоматично виправляє критичні помилки:
✅ Видаляє неіснуючий sqlalchemy-pool з requirements.txt
✅ Виправляє async/await в main.py
✅ Створює правильний Procfile
✅ Перевіряє UTF-8 кодування файлів
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def print_header():
    print("🆘" * 25)
    print("\n🚨 ЕКСТРЕНЕ ВИПРАВЛЕННЯ КРИТИЧНИХ ПОМИЛОК")
    print("Автоматичне виправлення Railway deployment помилок")
    print("🆘" * 25)
    print()

def backup_files():
    """Створює резервні копії файлів"""
    print("💾 СТВОРЕННЯ РЕЗЕРВНИХ КОПІЙ:")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backup_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = ['main.py', 'requirements.txt', 'Procfile']
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_dir / file_path)
            print(f"✅ {file_path} → {backup_dir}/{file_path}")
        else:
            print(f"⚠️ {file_path} не існує")
    
    print(f"📁 Резервні копії збережено в: {backup_dir}")

def fix_requirements():
    """Виправляє requirements.txt"""
    print("\n📦 ВИПРАВЛЕННЯ REQUIREMENTS.TXT:")
    
    # Читаємо поточний файл
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print("❌ requirements.txt не знайдено!")
        return False
    
    with open(requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Видаляємо проблемний рядок
    if 'sqlalchemy-pool' in content:
        print("🔍 Знайдено проблемний sqlalchemy-pool")
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if 'sqlalchemy-pool' in line:
                print(f"🗑️ Видаляємо: {line.strip()}")
                fixed_lines.append(f"# ❌ ВИДАЛЕНО: {line.strip()} - пакет не існує!")
            else:
                fixed_lines.append(line)
        
        # Записуємо виправлений файл
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print("✅ requirements.txt виправлено!")
        return True
    else:
        print("✅ sqlalchemy-pool не знайдено - все гаразд")
        return True

def fix_main_py():
    """Виправляє main.py з правильним async/await"""
    print("\n🚀 ВИПРАВЛЕННЯ MAIN.PY:")
    
    main_content = '''#!/usr/bin/env python3
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
    asyncio.run(main())'''
    
    # Записуємо виправлений main.py
    with open("main.py", 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    print("✅ main.py виправлено з правильним async/await")

def create_procfile():
    """Створює правильний Procfile"""
    print("\n🚢 СТВОРЕННЯ PROCFILE:")
    
    procfile_content = "web: python main.py"
    
    with open("Procfile", 'w', encoding='utf-8') as f:
        f.write(procfile_content)
    
    print("✅ Procfile створено")

def check_utf8_files():
    """Перевіряє кодування файлів"""
    print("\n🔤 ПЕРЕВІРКА UTF-8 КОДУВАННЯ:")
    
    critical_files = [
        "main.py", "requirements.txt", "Procfile", 
        "app/main.py", "app/config/settings.py"
    ]
    
    for file_path in critical_files:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    f.read()
                print(f"✅ {file_path} - UTF-8 OK")
            except UnicodeDecodeError:
                print(f"❌ {file_path} - UTF-8 ПРОБЛЕМИ!")
                try:
                    # Спроба виправлення
                    with open(path, 'r', encoding='cp1251') as f:
                        content = f.read()
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"🔧 {file_path} - перекодовано в UTF-8")
                except Exception as e:
                    print(f"❌ Не вдалося виправити {file_path}: {e}")
        else:
            print(f"⚠️ {file_path} - не існує")

def verify_fixes():
    """Перевіряє чи всі виправлення застосовані"""
    print("\n✅ ПЕРЕВІРКА ВИПРАВЛЕНЬ:")
    
    issues = []
    
    # Перевірка requirements.txt
    try:
        with open("requirements.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        if 'sqlalchemy-pool' in content and not content.count('❌ ВИДАЛЕНО:'):
            issues.append("sqlalchemy-pool досі присутній")
        else:
            print("✅ requirements.txt виправлено")
    except Exception as e:
        issues.append(f"Помилка читання requirements.txt: {e}")
    
    # Перевірка main.py
    try:
        with open("main.py", 'r', encoding='utf-8') as f:
            content = f.read()
        if 'asyncio.run(main())' in content:
            print("✅ main.py має правильний async запуск")
        else:
            issues.append("main.py не має asyncio.run()")
    except Exception as e:
        issues.append(f"Помилка читання main.py: {e}")
    
    # Перевірка Procfile
    if Path("Procfile").exists():
        print("✅ Procfile існує")
    else:
        issues.append("Procfile відсутній")
    
    return issues

def main():
    """Головна функція екстреного виправлення"""
    print_header()
    
    try:
        # Резервні копії
        backup_files()
        
        # Виправлення
        fix_requirements()
        fix_main_py()
        create_procfile()
        check_utf8_files()
        
        # Перевірка
        issues = verify_fixes()
        
        print("\n🎯 ПІДСУМОК ВИПРАВЛЕНЬ:")
        print("=" * 50)
        
        if not issues:
            print("🎉 ВСІ КРИТИЧНІ ПОМИЛКИ ВИПРАВЛЕНО!")
            print("✅ Готово до deploy на Railway")
            print("\n🚀 НАСТУПНІ КРОКИ:")
            print("1. git add .")
            print("2. git commit -m '🆘 Critical fixes: removed sqlalchemy-pool, fixed async/await'")
            print("3. git push")
            print("4. Railway автоматично перезапустить")
        else:
            print("⚠️ ЗАЛИШИЛИСЬ ПРОБЛЕМИ:")
            for issue in issues:
                print(f"- {issue}")
    
    except Exception as e:
        print(f"❌ Помилка виправлення: {e}")
        return False
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)