#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Database модуль - професійний експорт (ВИПРАВЛЕНО) 🧠😂🔥
"""

import logging

logger = logging.getLogger(__name__)

# Флаги завантаження
FUNCTIONS_LOADED = False
MODELS_LOADED = False

# ===== ІМПОРТ ФУНКЦІЙ =====
try:
    from .database import (
        # Ініціалізація та сесії
        init_db,
        get_db_session,
        check_if_migration_needed,  # ✅ ДОДАНО
        migrate_database,           # ✅ ДОДАНО
        verify_database_integrity,  # ✅ ДОДАНО
        
        # Користувачі
        get_or_create_user,
        get_user_by_id,
        update_user_points,
        get_rank_by_points,
        
        # Контент
        add_content_for_moderation,
        get_pending_content,
        moderate_content,
        get_random_approved_content,
        
        # Допоміжні
        ensure_admin_exists,
        add_initial_data
    )
    
    logger.info("✅ Функції БД імпортовано успішно")
    FUNCTIONS_LOADED = True
    
except ImportError as e:
    logger.error(f"❌ Помилка імпорту функцій: {e}")
    FUNCTIONS_LOADED = False

# ===== ІМПОРТ МОДЕЛЕЙ =====
try:
    from .models import (
        # Базова модель
        Base,
        
        # Основні моделі
        User,
        Content,
        Rating,
        Duel,
        DuelVote,
        AdminAction,
        BotStatistics,
        
        # Енуми
        ContentType,
        ContentStatus,
        DuelStatus,
        UserRank  # ✅ ДОДАНО
    )
    
    logger.info("✅ Моделі БД імпортовано успішно")
    MODELS_LOADED = True
    
except ImportError as e:
    logger.error(f"❌ Помилка імпорту моделей: {e}")
    MODELS_LOADED = False

# ===== ЕКСПОРТ ВСІХ ФУНКЦІЙ ТА КЛАСІВ =====
__all__ = [
    # === ІНІЦІАЛІЗАЦІЯ ===
    'init_db',
    'get_db_session', 
    'check_if_migration_needed',  # ✅ ДОДАНО
    'migrate_database',           # ✅ ДОДАНО
    'verify_database_integrity',  # ✅ ДОДАНО
    
    # === КОРИСТУВАЧІ ===
    'get_or_create_user',
    'get_user_by_id',
    'update_user_points',
    'get_rank_by_points',
    
    # === КОНТЕНТ ===
    'add_content_for_moderation',
    'get_pending_content',
    'moderate_content',
    'get_random_approved_content',
    
    # === ДОПОМІЖНІ ===
    'ensure_admin_exists',
    'add_initial_data',
    
    # === МОДЕЛІ ===
    'Base',
    'User',
    'Content',
    'Rating',
    'Duel',
    'DuelVote',
    'AdminAction',
    'BotStatistics',
    
    # === ЕНУМИ ===
    'ContentType',
    'ContentStatus',
    'DuelStatus',
    'UserRank'  # ✅ ДОДАНО
]

# ===== ВЕРСІЯ МОДУЛЯ =====
__version__ = "2.0.2"
__status__ = f"Функції: {'✅' if FUNCTIONS_LOADED else '❌'}, Моделі: {'✅' if MODELS_LOADED else '❌'}"

logger.info(f"📦 Database модуль ініціалізовано (v{__version__})")
logger.info(f"📋 Статус: {__status__}")
logger.info(f"🎯 Експортовано {len(__all__)} об'єктів")