#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 DATABASE МОДУЛЬ - БЕЗ КОНФЛІКТІВ 📦
"""

import logging

logger = logging.getLogger(__name__)

# Флаги завантаження
MODELS_LOADED = False
FUNCTIONS_LOADED = False
DATABASE_AVAILABLE = False

# Безпечний імпорт моделей
try:
    from .models import Base, User, Content, ContentType, ContentStatus, DuelStatus
    MODELS_LOADED = True
    logger.info("✅ Models loaded")
except ImportError as e:
    MODELS_LOADED = False
    logger.error(f"❌ Models error: {e}")
    
    # Fallback енуми
    import enum
    class ContentType(enum.Enum):
        JOKE = "joke"
    class ContentStatus(enum.Enum):
        PENDING = "pending"
    class DuelStatus(enum.Enum):
        ACTIVE = "active"

# Безпечний імпорт функцій
if MODELS_LOADED:
    try:
        from .database import (
            init_db, get_or_create_user, get_random_approved_content,
            DATABASE_AVAILABLE as DB_AVAILABLE
        )
        FUNCTIONS_LOADED = True
        DATABASE_AVAILABLE = DB_AVAILABLE
        logger.info("✅ Functions loaded")
    except ImportError as e:
        FUNCTIONS_LOADED = False
        logger.error(f"❌ Functions error: {e}")

# Fallback функції тільки якщо реальні недоступні
if not FUNCTIONS_LOADED:
    async def init_db():
        return False
    
    async def get_or_create_user(telegram_id, **kwargs):
        return None
    
    async def get_random_approved_content(**kwargs):
        import types
        obj = types.SimpleNamespace()
        obj.text = "😂 Fallback жарт: Програміст заходить в кафе..."
        return obj

# Експорт
__all__ = [
    'init_db', 'get_or_create_user', 'get_random_approved_content',
    'ContentType', 'ContentStatus', 'DuelStatus',
    'MODELS_LOADED', 'FUNCTIONS_LOADED', 'DATABASE_AVAILABLE'
]

if MODELS_LOADED:
    __all__.extend(['Base', 'User', 'Content'])

logger.info(f"📦 Database module: Functions {'✅' if FUNCTIONS_LOADED else '❌'}, Models {'✅' if MODELS_LOADED else '❌'}")
