#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Ініціалізація пакету handlers з реєстрацією всіх хендлерів 🧠😂🔥
"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def register_all_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів бота"""
    
    try:
        # ===== ОСНОВНІ КОМАНДИ =====
        from .basic_commands import register_basic_handlers
        register_basic_handlers(dp)
        logger.info("✅ Зареєстровано основні команди")
        
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації основних команд: {e}")
    
    try:
        # ===== АДМІН-ПАНЕЛЬ =====
        from .admin_panel_handlers import register_admin_handlers
        register_admin_handlers(dp)
        logger.info("✅ Зареєстровано адмін-панель")
        
    except Exception as e:
        logger.warning(f"⚠️ Адмін-панель не завантажена: {e}")
    
    try:
        # ===== ГЕЙМІФІКАЦІЯ =====
        from .gamification_handlers import register_gamification_handlers
        register_gamification_handlers(dp)
        logger.info("✅ Зареєстровано гейміфікацію")
        
    except Exception as e:
        logger.warning(f"⚠️ Гейміфікація не завантажена: {e}")
    
    try:
        # ===== КОНТЕНТ =====
        from .content_handlers import register_content_handlers
        register_content_handlers(dp)
        logger.info("✅ Зареєстровано контент-хендлери")
        
    except Exception as e:
        logger.warning(f"⚠️ Контент-хендлери не завантажені: {e}")
    
    try:
        # ===== МОДЕРАЦІЯ =====
        from .moderation_handlers import register_moderation_handlers
        register_moderation_handlers(dp)
        logger.info("✅ Зареєстровано модерацію")
        
    except Exception as e:
        logger.warning(f"⚠️ Модерація не завантажена: {e}")
    
    try:
        # ===== ДУЕЛІ =====
        from .duel_handlers import register_duel_handlers
        register_duel_handlers(dp)
        logger.info("✅ Зареєстровано дуелі")
        
    except Exception as e:
        logger.warning(f"⚠️ Дуелі не завантажені: {e}")
    
    logger.info("🎯 Всі хендлери успішно зареєстровані!")

# Fallback функція для compatibility
def register_handlers(dp: Dispatcher):
    """Alias для register_all_handlers"""
    register_all_handlers(dp)

__all__ = ['register_all_handlers', 'register_handlers']