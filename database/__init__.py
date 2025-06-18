#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРАВИЛЬНІ ЕКСПОРТИ DATABASE МОДУЛЯ 🧠😂🔥
ЗАМІНІТЬ ВЕСЬ ІСНУЮЧИЙ database/__init__.py НА ЦЕЙ КОД
"""

import logging
logger = logging.getLogger(__name__)

# ===== ІМПОРТ ВСІХ ФУНКЦІЙ З database.py =====
try:
    from .database import (
        # Основні функції
        init_db,
        get_db_session,
        check_if_migration_needed,
        migrate_database,
        verify_database_integrity,
        
        # Користувачі
        get_or_create_user,
        get_user_by_id,
        update_user_points,
        get_user_stats,
        calculate_user_rank,
        get_rank_info,
        
        # Контент
        add_content_for_moderation,
        get_pending_content,
        moderate_content,
        get_content_by_id,
        get_random_approved_content,
        
        # Рейтинги
        add_content_rating,
        get_content_rating,
        update_content_rating,
        
        # Рекомендації
        get_recommended_content,
        record_content_view,
        
        # Статистика
        get_bot_statistics,
        update_bot_statistics,
        
        # Дуелі
        create_duel,
        get_active_duels,
        vote_in_duel,
        
        # Допоміжні
        ensure_admin_exists,
        add_initial_data,
        add_sample_content,
        
        # Legacy
        submit_content,
        update_user_stats
    )
    
    logger.info("✅ Всі функції database.py імпортовано успішно")
    FUNCTIONS_LOADED = True
    
except ImportError as e:
    logger.error(f"❌ Помилка імпорту функцій: {e}")
    FUNCTIONS_LOADED = False
    
    # Створити заглушки
    async def init_db():
        logger.warning("⚠️ init_db заглушка")
        
    def get_db_session():
        logger.warning("⚠️ get_db_session заглушка")
        return None
        
    async def get_or_create_user(*args, **kwargs):
        logger.warning("⚠️ get_or_create_user заглушка")
        return None
        
    async def add_content_for_moderation(*args, **kwargs):
        logger.warning("⚠️ add_content_for_moderation заглушка")
        return None
        
    async def get_pending_content(*args, **kwargs):
        logger.warning("⚠️ get_pending_content заглушка")
        return []
        
    async def moderate_content(*args, **kwargs):
        logger.warning("⚠️ moderate_content заглушка")
        return False
        
    async def add_content_rating(*args, **kwargs):
        logger.warning("⚠️ add_content_rating заглушка")
        return True
        
    async def get_content_rating(*args, **kwargs):
        logger.warning("⚠️ get_content_rating заглушка")
        return None
        
    async def update_content_rating(*args, **kwargs):
        logger.warning("⚠️ update_content_rating заглушка")
        return True
        
    async def get_recommended_content(*args, **kwargs):
        logger.warning("⚠️ get_recommended_content заглушка")
        return None
        
    async def record_content_view(*args, **kwargs):
        logger.warning("⚠️ record_content_view заглушка")
        return True
        
    async def get_bot_statistics(*args, **kwargs):
        logger.warning("⚠️ get_bot_statistics заглушка")
        return {"total_users": 0, "total_content": 0, "today_ratings": 0}
        
    async def update_bot_statistics(*args, **kwargs):
        logger.warning("⚠️ update_bot_statistics заглушка")
        return True
        
    async def get_user_by_id(*args, **kwargs):
        logger.warning("⚠️ get_user_by_id заглушка")
        return None
        
    async def update_user_points(*args, **kwargs):
        logger.warning("⚠️ update_user_points заглушка")
        return None
        
    async def get_user_stats(*args, **kwargs):
        logger.warning("⚠️ get_user_stats заглушка")
        return {}
        
    async def get_content_by_id(*args, **kwargs):
        logger.warning("⚠️ get_content_by_id заглушка")
        return None
        
    async def get_random_approved_content(*args, **kwargs):
        logger.warning("⚠️ get_random_approved_content заглушка")
        return None
        
    async def create_duel(*args, **kwargs):
        logger.warning("⚠️ create_duel заглушка")
        return None
        
    async def get_active_duels(*args, **kwargs):
        logger.warning("⚠️ get_active_duels заглушка")
        return []
        
    async def vote_in_duel(*args, **kwargs):
        logger.warning("⚠️ vote_in_duel заглушка")
        return False
        
    async def ensure_admin_exists(*args, **kwargs):
        logger.warning("⚠️ ensure_admin_exists заглушка")
        return True
        
    async def add_initial_data(*args, **kwargs):
        logger.warning("⚠️ add_initial_data заглушка")
        
    async def add_sample_content(*args, **kwargs):
        logger.warning("⚠️ add_sample_content заглушка")
        
    async def submit_content(*args, **kwargs):
        logger.warning("⚠️ submit_content заглушка")
        return None
        
    async def update_user_stats(*args, **kwargs):
        logger.warning("⚠️ update_user_stats заглушка")
        return True
        
    async def verify_database_integrity(*args, **kwargs):
        logger.warning("⚠️ verify_database_integrity заглушка")
        
    async def check_if_migration_needed(*args, **kwargs):
        logger.warning("⚠️ check_if_migration_needed заглушка")
        return False
        
    async def migrate_database(*args, **kwargs):
        logger.warning("⚠️ migrate_database заглушка")
        
    def calculate_user_rank(*args, **kwargs):
        logger.warning("⚠️ calculate_user_rank заглушка")
        return "Новачок"
        
    def get_rank_info(*args, **kwargs):
        logger.warning("⚠️ get_rank_info заглушка")
        return {}

# ===== ІМПОРТ МОДЕЛЕЙ =====
try:
    from .models import (
        Base, User, Content, Rating, Duel, DuelVote,
        AdminAction, BotStatistics, ContentType, ContentStatus, UserRank
    )
    logger.info("✅ Моделі імпортовано успішно")
    MODELS_LOADED = True
    
except ImportError as e:
    logger.warning(f"⚠️ Помилка імпорту моделей: {e}")
    MODELS_LOADED = False
    
    # Створити заглушки моделей
    from enum import Enum
    
    class ContentType(Enum):
        JOKE = "joke"
        MEME = "meme"
    
    class ContentStatus(Enum):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
    
    class UserRank(Enum):
        NEWBIE = "Новачок"
        JOKER = "Жартівник"
        COMEDIAN = "Комік"
        HUMORIST = "Гуморист"
        MASTER = "Майстер сміху"
        EXPERT = "Експерт гумору"
        VIRTUOSO = "Віртуоз жартів"
        LEGEND = "Легенда гумору"
    
    Base = None
    User = None
    Content = None
    Rating = None
    Duel = None
    DuelVote = None
    AdminAction = None
    BotStatistics = None

# ===== ЕКСПОРТ ВСІХ ФУНКЦІЙ =====
__all__ = [
    # Основні функції
    'init_db',
    'get_db_session',
    'check_if_migration_needed',
    'migrate_database',
    'verify_database_integrity',
    
    # Користувачі
    'get_or_create_user',
    'get_user_by_id',
    'update_user_points',
    'get_user_stats',
    'calculate_user_rank',
    'get_rank_info',
    
    # Контент
    'add_content_for_moderation',
    'get_pending_content',
    'moderate_content',
    'get_content_by_id',
    'get_random_approved_content',
    
    # Рейтинги
    'add_content_rating',
    'get_content_rating',
    'update_content_rating',
    
    # Рекомендації
    'get_recommended_content',
    'record_content_view',
    
    # Статистика
    'get_bot_statistics',
    'update_bot_statistics',
    
    # Дуелі
    'create_duel',
    'get_active_duels',
    'vote_in_duel',
    
    # Допоміжні
    'ensure_admin_exists',
    'add_initial_data',
    'add_sample_content',
    
    # Legacy
    'submit_content',
    'update_user_stats',
    
    # Моделі
    'Base',
    'User',
    'Content',
    'Rating',
    'Duel',
    'DuelVote',
    'AdminAction',
    'BotStatistics',
    
    # Енуми
    'ContentType',
    'ContentStatus',
    'UserRank'
]

# ===== ФІНАЛЬНА ІНФОРМАЦІЯ =====
__version__ = "2.0.1"
__status__ = f"Функції: {'✅' if FUNCTIONS_LOADED else '❌'}, Моделі: {'✅' if MODELS_LOADED else '❌'}"

logger.info(f"📦 Database модуль ініціалізовано (v{__version__})")
logger.info(f"📋 Статус: {__status__}")
logger.info(f"🎯 Експортовано {len(__all__)} об'єктів")#!/usr/bin/env python3
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