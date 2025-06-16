#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Реєстрація всіх хендлерів україномовного бота 🧠😂🔥
"""

import logging
from aiogram import Dispatcher

# Імпорт всіх модулів хендлерів
from .basic_commands import register_basic_handlers
from .content_handlers import register_content_handlers  
from .gamification_handlers import register_gamification_handlers
from .moderation_handlers import register_moderation_handlers
from .duel_handlers import register_duel_handlers

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів бота"""
    
    try:
        logger.info("📝 Початок реєстрації хендлерів...")
        
        # 1. Основні команди (start, help, stats)
        register_basic_handlers(dp)
        logger.info("✅ Основні команди зареєстровано")
        
        # 2. Контент (meme, anekdot, submit)
        register_content_handlers(dp)
        logger.info("✅ Контент хендлери зареєстровано")
        
        # 3. Гейміфікація (profile, top, daily)
        register_gamification_handlers(dp)
        logger.info("✅ Гейміфікація зареєстровано")
        
        # 4. Модерація (approve, reject, admin)
        register_moderation_handlers(dp)
        logger.info("✅ Модерація зареєстровано")
        
        # 5. Дуелі (duel, voting)
        register_duel_handlers(dp)
        logger.info("✅ Дуелі зареєстровано")
        
        logger.info("🎉 Всі хендлери успішно зареєстровано!")
        
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації хендлерів: {e}")
        raise