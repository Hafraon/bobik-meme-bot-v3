#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Головний файл запуску Бобік 2.0 - AI Мем-Бот
"""

import asyncio
import logging
import sys
import os

# Додаємо поточну папку до Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Головна функція запуску бота"""
    
    try:
        # Поки що імпортуємо старий код
        from bobik_bot import main as old_main
        old_main()
    except ImportError:
        print("❌ Файл bobik_bot.py не знайдено!")
        print("📝 Створіть модульну структуру згідно документації")
        sys.exit(1)

if __name__ == "__main__":
    main()
