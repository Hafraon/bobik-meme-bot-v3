#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 АВТОМАТИЗОВАНИЙ ПЛАНУВАЛЬНИК - ВИПРАВЛЕНІ АРГУМЕНТИ 🤖
"""

import logging

logger = logging.getLogger(__name__)

class AutomatedScheduler:
    """✅ ВИПРАВЛЕНА версія з правильними аргументами"""
    
    def __init__(self, bot, db_available: bool = False):
        """
        ✅ ВИПРАВЛЕНО: Правильні аргументи ініціалізації
        
        Args:
            bot: Інстанс Telegram бота
            db_available: Чи доступна база даних
        """
        self.bot = bot
        self.db_available = db_available
        self.is_running = False
        
        logger.info(f"🤖 AutomatedScheduler ініціалізовано (БД: {'✅' if db_available else '❌'})")

    async def start(self) -> bool:
        """Запуск планувальника"""
        try:
            self.is_running = True
            logger.info("🚀 Автоматизований планувальник запущено!")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка запуску: {e}")
            return False

    async def stop(self):
        """Зупинка планувальника"""
        self.is_running = False
        logger.info("⏹️ Планувальник зупинено")

async def create_automated_scheduler(bot, db_available: bool = False):
    """✅ Фабрична функція для створення планувальника"""
    scheduler = AutomatedScheduler(bot, db_available)
    await scheduler.start()
    return scheduler

__all__ = ['AutomatedScheduler', 'create_automated_scheduler']
