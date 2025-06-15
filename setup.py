#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Швидке налаштування україномовного Telegram-бота 🧠😂🔥

Цей скрипт автоматизує процес встановлення та початкового налаштування бота.

Використання:
    python setup.py
    python setup.py --dev  (для розробки)
    python setup.py --production  (для production)
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path
import asyncio

def print_header():
    """Виведення заголовка"""
    print("🧠😂🔥" * 20)
    print("🚀 ШВИДКЕ НАЛАШТУВАННЯ УКРАЇНОМОВНОГО TELEGRAM-БОТА 🚀")
    print("🧠😂🔥" * 20)
    print()

def check_python_version():
    """Перевірка версії Python"""
    print("🐍 Перевірка версії Python...")
    if sys.version_info < (3, 9):
        print("❌ Потрібна версія Python 3.9 або вища!")
        print(f"   Поточна версія: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} - OK")

def create_virtual_environment():
    """Створення віртуального середовища"""
    print("\n🌟 Створення віртуального середовища...")
    
    if Path("venv").exists():
        print("⚠️ Віртуальне середовище вже існує")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Віртуальне середовище створено")
    except subprocess.CalledProcessError:
        print("❌ Помилка створення віртуального середовища")
        sys.exit(1)

def install_dependencies():
    """Встановлення залежностей"""
    print("\n📦 Встановлення залежностей...")
    
    pip_path = "venv/Scripts/pip" if os.name == "nt" else "venv/bin/pip"
    
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Залежності встановлено")
    except subprocess.CalledProcessError:
        print("❌ Помилка встановлення залежностей")
        sys.exit(1)

def create_config_file():
    """Створення конфігураційного файлу"""
    print("\n⚙️ Створення конфігурації...")
    
    if Path(".env").exists():
        print("⚠️ Файл .env вже існує")
        return
    
    if Path(".env.example").exists():
        shutil.copy(".env.example", ".env")
        print("✅ Файл .env створено з шаблону")
        print("📝 Відредагуйте .env файл з вашими налаштуваннями!")
    else:
        create_basic_env_file()

def create_basic_env_file():
    """Створення базового .env файлу"""
    env_content = """# 🧠😂🔥 Конфігурація україномовного бота 🧠😂🔥

# ОБОВ'ЯЗКОВІ НАЛАШТУВАННЯ
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here

# БАЗА ДАНИХ
DATABASE_URL=sqlite:///ukrainian_bot.db

# AI ГЕНЕРАЦІЯ (опціонально)
OPENAI_API_KEY=

# ДОДАТКОВІ НАЛАШТУВАННЯ
DEBUG=True
LOG_LEVEL=INFO
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ Базовий .env файл створено")

def create_directories():
    """Створення необхідних директорій"""
    print("\n📁 Створення директорій...")
    
    directories = [
        "logs",
        "data",
        "backups",
        "uploads",
        "alembic/versions"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Створення .gitkeep файлів
        gitkeep_file = Path(directory) / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.touch()
    
    print("✅ Директорії створено")

async def initialize_database():
    """Ініціалізація бази даних"""
    print("\n💾 Ініціалізація бази даних...")
    
    try:
        # Імпорт тут щоб уникнути помилок до встановлення залежностей
        sys.path.insert(0, ".")
        from database.database import init_db
        
        await init_db()
        print("✅ База даних ініціалізована")
    except Exception as e:
        print(f"❌ Помилка ініціалізації БД: {e}")
        print("   Це нормально, якщо ви ще не налаштували BOT_TOKEN")

def create_launch_scripts():
    """Створення скриптів запуску"""
    print("\n🚀 Створення скриптів запуску...")
    
    # Windows batch файл
    if os.name == "nt":
        batch_content = """@echo off
echo 🧠😂🔥 Запуск україномовного Telegram-бота 🧠😂🔥
call venv\\Scripts\\activate
python main.py
pause
"""
        with open("start_bot.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("✅ start_bot.bat створено")
    
    # Unix shell script
    shell_content = """#!/bin/bash
echo "🧠😂🔥 Запуск україномовного Telegram-бота 🧠😂🔥"
source venv/bin/activate
python main.py
"""
    with open("start_bot.sh", "w", encoding="utf-8") as f:
        f.write(shell_content)
    
    # Зробити executable на Unix
    if os.name != "nt":
        os.chmod("start_bot.sh", 0o755)
    
    print("✅ start_bot.sh створено")

def setup_development_tools():
    """Налаштування інструментів розробки"""
    print("\n🛠️ Налаштування інструментів розробки...")
    
    # Pre-commit hooks (опціонально)
    precommit_config = """repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
"""
    
    with open(".pre-commit-config.yaml", "w") as f:
        f.write(precommit_config)
    
    print("✅ Pre-commit конфігурацію створено")

def print_next_steps():
    """Виведення наступних кроків"""
    print("\n🎉 УСТАНОВКА ЗАВЕРШЕНА! 🎉")
    print("\n📋 НАСТУПНІ КРОКИ:")
    print("1. 🤖 Створіть Telegram бота через @BotFather")
    print("2. 📝 Відредагуйте .env файл з вашими налаштуваннями:")
    print("   - BOT_TOKEN=ваш_токен_бота")
    print("   - ADMIN_ID=ваш_telegram_id")
    print("3. 🚀 Запустіть бота:")
    
    if os.name == "nt":
        print("   - Windows: запустіть start_bot.bat")
        print("   - Або: venv\\Scripts\\activate && python main.py")
    else:
        print("   - Linux/Mac: ./start_bot.sh")
        print("   - Або: source venv/bin/activate && python main.py")
    
    print("\n📚 КОРИСНІ КОМАНДИ:")
    print("   python scripts/manage.py health  - перевірка здоров'я")
    print("   python scripts/manage.py stats   - статистика бота")
    print("   python scripts/backup.py create  - створити backup")
    print("\n🌐 ДЕПЛОЙМЕНТ:")
    print("   - Railway: підключіть GitHub репозиторій")
    print("   - Heroku: git push heroku main")
    print("   - Docker: docker-compose up")
    print("\n🧠😂🔥 Удачі з вашим ботом! 🧠😂🔥")

def main():
    """Головна функція"""
    parser = argparse.ArgumentParser(description="Швидке налаштування бота")
    parser.add_argument("--dev", action="store_true", help="Налаштування для розробки")
    parser.add_argument("--production", action="store_true", help="Налаштування для production")
    parser.add_argument("--skip-venv", action="store_true", help="Пропустити створення venv")
    parser.add_argument("--skip-deps", action="store_true", help="Пропустити встановлення залежностей")
    
    args = parser.parse_args()
    
    print_header()
    
    try:
        # Основні кроки
        check_python_version()
        
        if not args.skip_venv:
            create_virtual_environment()
        
        if not args.skip_deps:
            install_dependencies()
        
        create_config_file()
        create_directories()
        
        # Ініціалізація БД
        try:
            asyncio.run(initialize_database())
        except Exception as e:
            print(f"⚠️ БД буде ініціалізована при першому запуску: {e}")
        
        create_launch_scripts()
        
        if args.dev:
            setup_development_tools()
        
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Установка перервана користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Помилка установки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()