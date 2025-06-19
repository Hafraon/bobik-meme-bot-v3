#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНІ НАЛАШТУВАННЯ УКРАЇНОМОВНОГО БОТА 🧠😂🔥
"""

import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class Settings:
    """Клас налаштувань бота з fallback механізмами"""
    
    def __init__(self):
        """Ініціалізація налаштувань"""
        self._load_all_settings()
        self._validate_critical_settings()
        logger.info("✅ Налаштування завантажено успішно")
    
    def _load_all_settings(self):
        """Завантажити всі налаштування"""
        # ===== ОСНОВНІ НАЛАШТУВАННЯ =====
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        self.ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        
        # ===== ДОДАТКОВІ СЕРВІСИ =====
        self.CHANNEL_ID = os.getenv("CHANNEL_ID", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
        
        # ===== НАЛАШТУВАННЯ СЕРЕДОВИЩА =====
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.PORT = int(os.getenv("PORT", "8000"))
        
        # ===== НАЛАШТУВАННЯ БАЗИ ДАНИХ =====
        self.DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
        self.DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"
        
        # ===== ГЕЙМІФІКАЦІЯ =====
        self.POINTS_FOR_VIEW = int(os.getenv("POINTS_FOR_VIEW", "1"))
        self.POINTS_FOR_REACTION = int(os.getenv("POINTS_FOR_REACTION", "5"))
        self.POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
        self.POINTS_FOR_APPROVAL = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
        self.POINTS_FOR_TOP_JOKE = int(os.getenv("POINTS_FOR_TOP_JOKE", "50"))
        self.POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
        self.POINTS_FOR_DUEL_PARTICIPATION = int(os.getenv("POINTS_FOR_DUEL_PARTICIPATION", "5"))
        self.POINTS_FOR_DAILY_ACTIVITY = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))
        self.POINTS_FOR_VOTING = int(os.getenv("POINTS_FOR_VOTING", "2"))
        
        # ===== ЩОДЕННА РОЗСИЛКА =====
        self.DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
        self.DAILY_BROADCAST_MINUTE = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
        self.DAILY_BROADCAST_ENABLED = os.getenv("DAILY_BROADCAST_ENABLED", "True").lower() == "true"
        
        # ===== ДУЕЛІ =====
        self.DUEL_VOTING_TIME = int(os.getenv("DUEL_VOTING_TIME", "300"))  # 5 хвилин
        self.MIN_VOTES_FOR_DUEL = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
        self.MAX_ACTIVE_DUELS = int(os.getenv("MAX_ACTIVE_DUELS", "10"))
        
        # ===== МОДЕРАЦІЯ =====
        self.AUTO_APPROVE_ADMIN_CONTENT = os.getenv("AUTO_APPROVE_ADMIN_CONTENT", "True").lower() == "true"
        self.MAX_PENDING_CONTENT_PER_USER = int(os.getenv("MAX_PENDING_CONTENT_PER_USER", "5"))
        self.CONTENT_MIN_LENGTH = int(os.getenv("CONTENT_MIN_LENGTH", "10"))
        self.CONTENT_MAX_LENGTH = int(os.getenv("CONTENT_MAX_LENGTH", "1000"))
        
        # ===== АНТИСПАМ =====
        self.RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "3"))
        self.RATE_LIMIT_CALLBACKS = int(os.getenv("RATE_LIMIT_CALLBACKS", "5"))
        self.SPAM_BAN_DURATION = int(os.getenv("SPAM_BAN_DURATION", "3600"))  # 1 година
        
        # ===== КЕШУВАННЯ =====
        self.REDIS_URL = os.getenv("REDIS_URL", "")
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 година
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
        
        # ===== МОНІТОРИНГ =====
        self.PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "False").lower() == "true"
        self.PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8001"))
        self.HEALTH_CHECK_ENABLED = os.getenv("HEALTH_CHECK_ENABLED", "True").lower() == "true"
        
        # ===== РОЗСИЛКА =====
        self.BROADCAST_DELAY = float(os.getenv("BROADCAST_DELAY", "0.1"))  # Затримка між повідомленнями
        self.MAX_BROADCAST_USERS = int(os.getenv("MAX_BROADCAST_USERS", "10000"))
        
        # ===== BACKUP =====
        self.BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "True").lower() == "true"
        self.BACKUP_INTERVAL_HOURS = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
        self.BACKUP_RETAIN_DAYS = int(os.getenv("BACKUP_RETAIN_DAYS", "7"))
        
        # ===== AI ГЕНЕРАЦІЯ =====
        self.AI_GENERATION_ENABLED = os.getenv("AI_GENERATION_ENABLED", "False").lower() == "true"
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "150"))
        self.AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.9"))
        
        # ===== ДОДАТКОВІ АДМІНИ =====
        additional_admins_str = os.getenv("ADDITIONAL_ADMINS", "")
        self.ADDITIONAL_ADMINS = []
        if additional_admins_str:
            try:
                self.ADDITIONAL_ADMINS = [int(admin_id.strip()) for admin_id in additional_admins_str.split(",")]
            except ValueError:
                logger.warning("⚠️ Невірний формат ADDITIONAL_ADMINS")
        
        # ===== ЗАБОРОНЕНІ СЛОВА =====
        banned_words_str = os.getenv("BANNED_WORDS", "")
        self.BANNED_WORDS = []
        if banned_words_str:
            self.BANNED_WORDS = [word.strip().lower() for word in banned_words_str.split(",")]
    
    def _validate_critical_settings(self):
        """Валідувати критично важливі налаштування"""
        errors = []
        
        if not self.BOT_TOKEN:
            errors.append("BOT_TOKEN не встановлено")
        
        if not self.ADMIN_ID:
            errors.append("ADMIN_ID не встановлено")
        
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL не встановлено")
        
        if self.DUEL_VOTING_TIME < 60:
            errors.append("DUEL_VOTING_TIME занадто малий (мінімум 60 секунд)")
        
        if self.RATE_LIMIT_MESSAGES < 1:
            errors.append("RATE_LIMIT_MESSAGES повинен бути >= 1")
        
        if errors:
            error_text = "\n".join(f"❌ {error}" for error in errors)
            logger.error(f"Критичні помилки налаштувань:\n{error_text}")
            raise ValueError(f"Критичні помилки налаштувань: {errors}")
    
    def get_all_admins(self) -> List[int]:
        """Отримати список всіх адміністраторів"""
        admins = [self.ADMIN_ID] if self.ADMIN_ID else []
        admins.extend(self.ADDITIONAL_ADMINS)
        return list(set(admins))  # Унікальні значення
    
    def is_admin(self, user_id: int) -> bool:
        """Перевірити чи є користувач адміністратором"""
        return user_id in self.get_all_admins()
    
    def get_database_config(self) -> Dict[str, Any]:
        """Отримати конфігурацію БД"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "echo": self.DB_ECHO
        }
    
    def get_points_config(self) -> Dict[str, int]:
        """Отримати конфігурацію балів"""
        return {
            "view": self.POINTS_FOR_VIEW,
            "reaction": self.POINTS_FOR_REACTION,
            "submission": self.POINTS_FOR_SUBMISSION,
            "approval": self.POINTS_FOR_APPROVAL,
            "top_joke": self.POINTS_FOR_TOP_JOKE,
            "duel_win": self.POINTS_FOR_DUEL_WIN,
            "duel_participation": self.POINTS_FOR_DUEL_PARTICIPATION,
            "daily_activity": self.POINTS_FOR_DAILY_ACTIVITY,
            "voting": self.POINTS_FOR_VOTING
        }
    
    def get_duel_config(self) -> Dict[str, Any]:
        """Отримати конфігурацію дуелів"""
        return {
            "voting_time": self.DUEL_VOTING_TIME,
            "min_votes": self.MIN_VOTES_FOR_DUEL,
            "max_active": self.MAX_ACTIVE_DUELS
        }
    
    def get_moderation_config(self) -> Dict[str, Any]:
        """Отримати конфігурацію модерації"""
        return {
            "auto_approve_admin": self.AUTO_APPROVE_ADMIN_CONTENT,
            "max_pending_per_user": self.MAX_PENDING_CONTENT_PER_USER,
            "min_length": self.CONTENT_MIN_LENGTH,
            "max_length": self.CONTENT_MAX_LENGTH,
            "banned_words": self.BANNED_WORDS
        }
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """Отримати конфігурацію планувальника"""
        return {
            "daily_broadcast_enabled": self.DAILY_BROADCAST_ENABLED,
            "broadcast_hour": self.DAILY_BROADCAST_HOUR,
            "broadcast_minute": self.DAILY_BROADCAST_MINUTE,
            "timezone": self.TIMEZONE
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертувати налаштування в словник (без секретів)"""
        safe_settings = {}
        
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                value = getattr(self, attr_name)
                
                # Приховати секретні дані
                if any(secret in attr_name.upper() for secret in ['TOKEN', 'KEY', 'SECRET', 'PASSWORD']):
                    if value:
                        safe_settings[attr_name] = f"{value[:8]}***"
                    else:
                        safe_settings[attr_name] = ""
                else:
                    safe_settings[attr_name] = value
        
        return safe_settings

# ===== ЕМОДЗІ ТА ТЕКСТИ =====

EMOJI = {
    # Основні емодзі
    "brain": "🧠",
    "laugh": "😂", 
    "fire": "🔥",
    "star": "⭐",
    "gem": "💎",
    "rocket": "🚀",
    "heart": "❤️",
    
    # Статуси
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "new": "🆕",
    
    # Користувачі та ролі
    "crown": "👑",
    "profile": "👤",
    "admin": "🛡️",
    "vip": "💎",
    
    # Контент
    "meme": "🖼️",
    "joke": "😄",
    "photo": "📸",
    "video": "🎬",
    
    # Активність
    "vs": "⚔️",
    "trophy": "🏆",
    "medal": "🥇",
    "calendar": "📅",
    "time": "⏰",
    "timer": "⏲️",
    
    # Реакції
    "thumbs_up": "👍",
    "thumbs_down": "👎",
    "like": "❤️",
    "dislike": "💔",
    
    # Статистика
    "stats": "📊",
    "chart": "📈",
    "graph": "📉",
    "percentage": "📋",
    
    # Навігація
    "home": "🏠",
    "back": "⬅️",
    "next": "➡️",
    "up": "⬆️",
    "down": "⬇️",
    
    # Час доби
    "morning": "🌅",
    "day": "☀️",
    "evening": "🌆",
    "night": "🌙",
    
    # Дії
    "send": "📤",
    "receive": "📥",
    "search": "🔍",
    "filter": "🔽",
    "refresh": "🔄",
    "settings": "⚙️",
    "edit": "✏️",
    "delete": "🗑️",
    
    # Гейміфікація
    "level_up": "📈",
    "achievement": "🏅",
    "badge": "🎖️",
    "reward": "🎁",
    
    # Модерація
    "approve": "✅",
    "reject": "❌",
    "pending": "⏳",
    "review": "👁‍🗨",
    
    # Спеціальні
    "bot": "🤖",
    "user": "👤",
    "group": "👥",
    "channel": "📢",
    "link": "🔗",
    "file": "📄",
    "folder": "📁",
    "database": "💾",
    "cloud": "☁️",
    "shield": "🛡️",
    "key": "🔑",
    "lock": "🔒",
    "unlock": "🔓"
}

TEXTS = {
    # Привітання
    "welcome": "Ласкаво просимо до українського бота мемів та анекдотів!",
    "welcome_back": "З поверненням!",
    "good_morning": "Доброго ранку",
    "good_day": "Гарного дня", 
    "good_evening": "Доброго вечора",
    "good_night": "Доброї ночі",
    
    # Помилки
    "error_general": "Сталася помилка. Спробуйте ще раз.",
    "error_network": "Помилка мережі. Перевірте з'єднання.",
    "error_database": "Помилка бази даних. Спробуйте пізніше.",
    "error_permissions": "Недостатньо прав для цієї дії.",
    "error_not_found": "Запитуваний ресурс не знайдено.",
    
    # Успіх
    "success_general": "Операція виконана успішно!",
    "success_save": "Дані збережено успішно!",
    "success_delete": "Видалено успішно!",
    "success_update": "Оновлено успішно!",
    
    # Модерація
    "moderation_approved": "Контент схвалено!",
    "moderation_rejected": "Контент відхилено.",
    "moderation_pending": "Контент очікує модерації.",
    
    # Дуелі
    "duel_created": "Дуель створено!",
    "duel_joined": "Ви приєдналися до дуелі!",
    "duel_won": "Вітаємо з перемогою!",
    "duel_lost": "Нічого страшного, спробуйте ще раз!",
    
    # Бали
    "points_awarded": "Бали нараховано!",
    "points_insufficient": "Недостатньо балів.",
    "rank_up": "Вітаємо з підвищенням рангу!",
    
    # Загальні
    "loading": "Завантаження...",
    "please_wait": "Будь ласка, зачекайте...",
    "try_again": "Спробуйте ще раз",
    "contact_admin": "Зверніться до адміністратора",
    
    # Команди
    "command_not_found": "Команда не знайдена. Використайте /help",
    "command_error": "Помилка виконання команди.",
    
    # Налаштування
    "settings_updated": "Налаштування оновлено!",
    "subscription_enabled": "Підписку увімкнено!",
    "subscription_disabled": "Підписку вимкнено.",
    
    # Контент
    "content_too_short": "Контент занадто короткий.",
    "content_too_long": "Контент занадто довгий.",
    "content_submitted": "Контент надіслано на модерацію!",
    "no_content": "Контент не знайдено.",
}

# Контекстні привітання за часом дня
TIME_GREETINGS = {
    "morning": ["Доброго ранку", "Гарного ранку", "Чудового ранку"],
    "day": ["Гарного дня", "Приємного дня", "Чудового дня"],
    "evening": ["Доброго вечора", "Приємного вечора", "Гарного вечора"],
    "night": ["Доброї ночі", "Солодких снів", "Спокійної ночі"]
}

# Мотиваційні фрази
MOTIVATIONAL_PHRASES = [
    "Продовжуйте в тому ж дусі!",
    "Ви на правильному шляху!",
    "Чудова робота!",
    "Ще трохи до наступного рангу!",
    "Ви справжня легенда гумору!",
    "Ваші жарти завжди смішні!",
    "Дякуємо за активність!",
    "Ви робите бота кращим!"
]

# Створити глобальний екземпляр налаштувань
settings = Settings()

# Експорт для зручності
__all__ = [
    'settings', 
    'Settings', 
    'EMOJI', 
    'TEXTS', 
    'TIME_GREETINGS', 
    'MOTIVATIONAL_PHRASES'
]