#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def register_all_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів бота"""
    
    try:
        # Спроба реєстрації контент хендлерів
        from .content_handlers import register_content_handlers
        register_content_handlers(dp)
        logger.info("✅ Content handlers registered")
    except ImportError as e:
        logger.warning(f"⚠️ Could not import content handlers: {e}")
    except Exception as e:
        logger.error(f"❌ Error registering content handlers: {e}")
    
    # Тут будуть додаватися інші хендлери в наступних кроках:
    # - gamification_handlers (профіль, топ, дуелі)
    # - moderation_handlers (адмін функції)
    # - admin_panel_handlers (повна адмін панель)
    
    logger.info("📋 All available handlers registered")

# Експорт для використання
__all__ = ['register_all_handlers']