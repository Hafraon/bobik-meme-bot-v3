#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНІ ЕКСПОРТИ МОДУЛЯ DATABASE 🧠😂🔥
Повний набір функцій для україномовного Telegram-бота
"""

# ===== ОСНОВНІ ІМПОРТИ З database.py =====
from .database import (
    # Ініціалізація та сесії
    init_db,
    get_db_session,
    verify_database_integrity,
    
    # Користувачі - повний CRUD
    get_or_create_user,
    get_user_by_id,
    update_user_points,
    get_user_stats,
    calculate_user_rank,
    get_rank_info,
    
    # Контент - повний CRUD
    add_content_for_moderation,
    get_pending_content,
    moderate_content,
    get_content_by_id,
    get_random_approved_content,
    
    # Рейтинги та взаємодія
    add_content_rating,
    get_content_rating,
    update_content_rating,
    
    # Рекомендації та персоналізація
    get_recommended_content,
    record_content_view,
    
    # Статистика бота
    get_bot_statistics,
    update_bot_statistics,
    
    # Дуелі
    create_duel,
    get_active_duels,
    vote_in_duel,
    
    # Допоміжні функції
    ensure_admin_exists,
    add_initial_data,
    add_sample_content,
    
    # Legacy підтримка
    submit_content,
    update_user_stats
)

# ===== ІМПОРТИ МОДЕЛЕЙ =====
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
    UserRank
)

# ===== ЕКСПОРТ ВСІХ ФУНКЦІЙ ТА КЛАСІВ =====
__all__ = [
    # === ІНІЦІАЛІЗАЦІЯ ===
    'init_db',
    'get_db_session', 
    'verify_database_integrity',
    
    # === КОРИСТУВАЧІ ===
    'get_or_create_user',
    'get_user_by_id',
    'update_user_points',
    'get_user_stats',
    'calculate_user_rank',
    'get_rank_info',
    'update_user_stats',  # Legacy
    
    # === КОНТЕНТ ===
    'add_content_for_moderation',
    'get_pending_content',
    'moderate_content',
    'get_content_by_id',
    'get_random_approved_content',
    'submit_content',  # Legacy
    
    # === РЕЙТИНГИ ===
    'add_content_rating',
    'get_content_rating',
    'update_content_rating',
    
    # === РЕКОМЕНДАЦІЇ ===
    'get_recommended_content',
    'record_content_view',
    
    # === СТАТИСТИКА ===
    'get_bot_statistics',
    'update_bot_statistics',
    
    # === ДУЕЛІ ===
    'create_duel',
    'get_active_duels',
    'vote_in_duel',
    
    # === ДОПОМІЖНІ ===
    'ensure_admin_exists',
    'add_initial_data',
    'add_sample_content',
    
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
    'UserRank'
]

# ===== ВЕРСІЯ МОДУЛЯ =====
__version__ = "2.0.0"
__author__ = "Ukraine Telegram Bot Team"
__description__ = "Професійний модуль роботи з базою даних для україномовного Telegram-бота"

# ===== НАЛАШТУВАННЯ ЛОГУВАННЯ =====
import logging
logger = logging.getLogger(__name__)
logger.info(f"📦 Database модуль завантажено успішно (версія {__version__})")
logger.info(f"📋 Доступно {len(__all__)} функцій та класів")