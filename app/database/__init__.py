#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 Database модуль - ВИПРАВЛЕНИЙ ЕКСПОРТ

ВИПРАВЛЕННЯ:
✅ Graceful fallback при помилках імпорту
✅ Детальне логування кожного кроку
✅ Безпечна обробка відсутніх функцій
"""

import logging

logger = logging.getLogger(__name__)

# Флаги завантаження
FUNCTIONS_LOADED = False
MODELS_LOADED = False

# ===== БЕЗПЕЧНИЙ ІМПОРТ МОДЕЛЕЙ =====
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
        DuelStatus
    )
    
    MODELS_LOADED = True
    logger.info("✅ Database models завантажено успішно")
    
except ImportError as e:
    MODELS_LOADED = False
    logger.error(f"❌ Помилка імпорту models: {e}")

# ===== БЕЗПЕЧНИЙ ІМПОРТ ФУНКЦІЙ =====
try:
    from .database import (
        # Основні функції БД
        init_db,
        get_db_session,
        
        # Функції користувачів
        get_or_create_user,
        get_user_by_id,
        update_user_points,
        get_rank_by_points,
        
        # Функції контенту
        add_content_for_moderation,
        get_pending_content,
        moderate_content,
        get_random_approved_content,
        
        # Допоміжні функції
        ensure_admin_exists,
        add_initial_data
    )
    
    FUNCTIONS_LOADED = True
    logger.info("✅ Database functions завантажено успішно")
    
except ImportError as e:
    FUNCTIONS_LOADED = False
    logger.error(f"❌ Помилка імпорту database functions: {e}")

# ===== ДОДАТКОВІ ФУНКЦІЇ (ОПЦІОНАЛЬНО) =====
ADVANCED_FUNCTIONS_LOADED = False
try:
    from .database import (
        check_if_migration_needed,
        migrate_database,
        verify_database_integrity
    )
    ADVANCED_FUNCTIONS_LOADED = True
    logger.info("✅ Advanced database functions завантажено")
except ImportError:
    logger.warning("⚠️ Advanced database functions недоступні")

# ===== СТВОРЕННЯ FALLBACK ФУНКЦІЙ =====
if not FUNCTIONS_LOADED:
    logger.warning("⚠️ Створення fallback database functions")
    
    async def init_db():
        """Fallback функція ініціалізації БД"""
        logger.warning("⚠️ Using fallback init_db - database not fully available")
        return False
    
    def get_db_session():
        """Fallback session manager"""
        logger.warning("⚠️ Database session not available")
        from contextlib import contextmanager
        
        @contextmanager
        def dummy_session():
            yield None
        
        return dummy_session()
    
    async def get_or_create_user(telegram_id, username=None, first_name=None):
        """Fallback функція користувача"""
        logger.warning(f"⚠️ User {telegram_id} not saved - database not available")
        return None
    
    async def get_user_by_id(telegram_id):
        """Fallback отримання користувача"""
        return None
    
    async def update_user_points(telegram_id, points_delta):
        """Fallback оновлення балів"""
        logger.warning(f"⚠️ Points update for {telegram_id} skipped - database not available")
        return False
    
    async def get_rank_by_points(points):
        """Fallback ранг за балами"""
        if points >= 5000:
            return "🚀 Гумористичний Геній"
        elif points >= 3000:
            return "🌟 Легенда Мемів"
        elif points >= 1500:
            return "🏆 Король Гумору"
        elif points >= 750:
            return "👑 Мастер Рофлу"
        elif points >= 350:
            return "🎭 Комік"
        elif points >= 150:
            return "😂 Гуморист"
        elif points >= 50:
            return "😄 Сміхун"
        else:
            return "🤡 Новачок"
    
    async def add_content_for_moderation(author_id, content_type, text):
        """Fallback додавання контенту"""
        logger.warning(f"⚠️ Content from {author_id} not saved - database not available")
        return None
    
    async def get_pending_content():
        """Fallback отримання контенту на модерації"""
        return []
    
    async def moderate_content(content_id, approved, moderator_id, reason=None):
        """Fallback модерація"""
        logger.warning(f"⚠️ Content {content_id} moderation skipped - database not available")
        return False
    
    async def get_random_approved_content(content_type):
        """Fallback випадковий контент"""
        # Повертаємо демо контент
        if hasattr(content_type, 'name'):
            content_type_name = content_type.name
        else:
            content_type_name = str(content_type)
        
        demo_content = {
            'JOKE': [
                "🧠 Приходить программіст до лікаря:\n- Доктор, в мене болить рука!\n- А де саме?\n- В лівому кліку! 😂",
                "🔥 Зустрічаються два українці:\n- Як справи?\n- Та нормально, працюю в IT.\n- А що робиш?\n- Борщ доставляю через додаток! 😂"
            ],
            'MEME': [
                "😂 Коли бачиш що на роботі Wi-Fi швидший за домашній:\n*зображення здивованого кота*",
                "🤣 Мій настрій коли п'ятниця:\n*зображення танцюючої людини*"
            ],
            'ANEKDOT': [
                "😂 Учитель запитує:\n- Петрику, скільки буде 2+2?\n- А ви про що? Про гривні чи про долари? 🧠",
                "🔥 Покупець у магазині:\n- Скільки коштує хліб?\n- 20 гривень.\n- А вчора був 15!\n- Вчора ви його і не купили! 😂"
            ]
        }
        
        import random
        content_list = demo_content.get(content_type_name.upper(), demo_content['JOKE'])
        
        # Створюємо простий об'єкт для сумісності
        import types
        demo_obj = types.SimpleNamespace()
        demo_obj.text = random.choice(content_list)
        demo_obj.id = 0
        demo_obj.author_id = 1
        
        return demo_obj
    
    async def ensure_admin_exists():
        """Fallback створення адміна"""
        logger.warning("⚠️ Admin creation skipped - database not available")
        return
    
    async def add_initial_data():
        """Fallback початкові дані"""
        logger.warning("⚠️ Initial data skipped - database not available")
        return

# ===== FALLBACK ДЛ�Я ADVANCED ФУНКЦІЙ =====
if not ADVANCED_FUNCTIONS_LOADED:
    async def check_if_migration_needed():
        """Fallback перевірка міграції"""
        return False
    
    async def migrate_database():
        """Fallback міграція"""
        logger.warning("⚠️ Database migration skipped - not available")
        return
    
    async def verify_database_integrity():
        """Fallback перевірка цілісності"""
        return True

# ===== СТВОРЕННЯ FALLBACK МОДЕЛЕЙ =====
if not MODELS_LOADED:
    logger.warning("⚠️ Створення fallback models")
    
    # Створюємо базові заглушки для enum'ів
    import enum
    
    class ContentType(enum.Enum):
        JOKE = "joke"
        MEME = "meme"
        ANEKDOT = "anekdot"
    
    class ContentStatus(enum.Enum):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
    
    class DuelStatus(enum.Enum):
        ACTIVE = "active"
        FINISHED = "finished"
        CANCELLED = "cancelled"

# ===== ЕКСПОРТ ВСІХ ФУНКЦІЙ ТА КЛАСІВ =====
__all__ = [
    # === ІНІЦІАЛІЗАЦІЯ ===
    'init_db',
    'get_db_session',
    'check_if_migration_needed',
    'migrate_database',
    'verify_database_integrity',
    
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
    
    # === ЕНУМИ ===
    'ContentType',
    'ContentStatus',
    'DuelStatus',
    
    # === ФЛАГИ СТАТУСУ ===
    'FUNCTIONS_LOADED',
    'MODELS_LOADED',
    'ADVANCED_FUNCTIONS_LOADED'
]

# ===== ЕКСПОРТ МОДЕЛЕЙ (ЯКЩО ДОСТУПНІ) =====
if MODELS_LOADED:
    __all__.extend([
        'Base', 'User', 'Content', 'Rating', 
        'Duel', 'DuelVote', 'AdminAction', 'BotStatistics'
    ])

# ===== ВЕРСІЯ МОДУЛЯ =====
__version__ = "2.1.0"
__status__ = f"Functions: {'✅' if FUNCTIONS_LOADED else '❌'}, Models: {'✅' if MODELS_LOADED else '❌'}, Advanced: {'✅' if ADVANCED_FUNCTIONS_LOADED else '❌'}"

logger.info(f"📦 Database модуль ініціалізовано (v{__version__})")
logger.info(f"📋 Статус: {__status__}")
logger.info(f"🎯 Експортовано {len(__all__)} об'єктів")

# Логування доступних функцій
if FUNCTIONS_LOADED:
    logger.info("✅ Database functions: повний функціонал")
else:
    logger.warning("⚠️ Database functions: fallback режим")

if MODELS_LOADED:
    logger.info("✅ Database models: повний функціонал")
else:
    logger.warning("⚠️ Database models: fallback enum'и")

# Перевірка готовності до роботи
if FUNCTIONS_LOADED and MODELS_LOADED:
    logger.info("🎉 Database module: повністю готовий до роботи!")
elif FUNCTIONS_LOADED or MODELS_LOADED:
    logger.warning("⚠️ Database module: частково готовий (fallback режим)")
else:
    logger.warning("⚠️ Database module: fallback режим (база даних недоступна)")