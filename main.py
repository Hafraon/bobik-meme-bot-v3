#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Точка входу україномовного Telegram-бота 🧠😂🔥
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
        # Імпорт головного модуля бота
        from bobik_bot import main as bot_main
        
        # Запуск бота
        asyncio.run(bot_main())
        
    except ImportError as e:
        print("❌ Помилка імпорту!")
        print(f"Деталі: {e}")
        print("📝 Переконайтеся, що всі залежності встановлені:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Бот зупинено користувачем")
        
    except Exception as e:
        print(f"💥 Критична помилка: {e}")
        logging.exception("Критична помилка:")
        sys.exit(1)

if __name__ == "__main__":
    main()