#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def register_all_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів бота"""
    
    try:
        # Реєстрація контент хендлерів
        from .content_handlers import register_content_handlers
        register_content_handlers(dp)
        logger.info("✅ Content handlers registered")
    except ImportError as e:
        logger.warning(f"⚠️ Could not import content handlers: {e}")
    except Exception as e:
        logger.error(f"❌ Error registering content handlers: {e}")
    
    try:
        # Реєстрація адмін хендлерів
        from .admin_handlers import register_admin_handlers
        register_admin_handlers(dp)
        logger.info("✅ Admin handlers registered")
    except ImportError as e:
        logger.warning(f"⚠️ Could not import admin handlers: {e}")
    except Exception as e:
        logger.error(f"❌ Error registering admin handlers: {e}")
    
    # Тут будуть додаватися інші хендлери в наступних кроках:
    # - gamification_handlers (дуелі, турніри)
    # - scheduler_handlers (автоматичні розсилки)
    # - special_events_handlers (особливі події)
    
    logger.info("📋 All available handlers registered successfully")

# Експорт для використання
__all__ = ['register_all_handlers']