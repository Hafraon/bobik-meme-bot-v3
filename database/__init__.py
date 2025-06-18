#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 База даних пакет для україномовного бота (ВИПРАВЛЕНО) 🧠😂🔥
"""

# ===== ОСНОВНІ ІМПОРТИ =====
from .database import (
    # Ініціалізація
    init_db,
    get_db_session,
    
    # Користувачі
    get_or_create_user,
    update_user_points,
    update_user_stats,
    get_user_stats,
    get_user_by_id,
    
    # Контент
    add_content_for_moderation,
    submit_content,
    get_pending_content,
    moderate_content,
    get_random_approved_content,
    get_content_by_id,
    
    # Рейтинги
    add_content_rating,
    get_content_rating,
    update_content_rating,
    
    # Статистика
    get_bot_statistics,
    update_bot_statistics,
    
    # Дуелі (якщо є)
    create_duel,
    get_active_duels,
    vote_in_duel,
    
    # Допоміжні
    ensure_admin_exists,
    add_initial_data
)

from .models import (
    Base,
    User,
    Content, 
    Rating,
    Duel,
    DuelVote,
    AdminAction,
    BotStatistics,
    ContentType,
    ContentStatus,
    UserRank
)

# ===== ФУНКЦІЇ ЩО ВІДСУТНІ - ДОДАЄМО ЗАГЛУШКИ =====

async def get_recommended_content(user_id: int, content_type: str):
    """Заглушка для рекомендованого контенту"""
    return await get_random_approved_content(content_type)

async def record_content_view(user_id: int, content_id: int, source: str = "command"):
    """Заглушка для запису перегляду"""
    # Оновлюємо статистику користувача
    return await update_user_stats(user_id, {"views_count": 1})

async def get_user_content_history(user_id: int, limit: int = 10):
    """Заглушка для історії контенту користувача"""
    return []

async def get_trending_content(days: int = 7, limit: int = 10):
    """Заглушка для трендового контенту"""
    return await get_random_approved_content("mixed", limit)

# ===== ЕКСПОРТ ВСІХ ФУНКЦІЙ =====
__all__ = [
    # Основні
    'init_db',
    'get_db_session',
    
    # Користувачі  
    'get_or_create_user',
    'update_user_points',
    'update_user_stats', 
    'get_user_stats',
    'get_user_by_id',
    
    # Контент
    'add_content_for_moderation',
    'submit_content',
    'get_pending_content',
    'moderate_content',
    'get_random_approved_content',
    'get_content_by_id',
    'get_recommended_content',
    'record_content_view',
    'get_user_content_history',
    'get_trending_content',
    
    # Рейтинги
    'add_content_rating',
    'get_content_rating', 
    'update_content_rating',
    
    # Статистика
    'get_bot_statistics',
    'update_bot_statistics',
    
    # Дуелі
    'create_duel',
    'get_active_duels',
    'vote_in_duel',
    
    # Моделі
    'Base',
    'User',
    'Content',
    'Rating', 
    'Duel',
    'DuelVote',
    'AdminAction',
    'BotStatistics',
    'ContentType',
    'ContentStatus',
    'UserRank',
    
    # Допоміжні
    'ensure_admin_exists',
    'add_initial_data'
]