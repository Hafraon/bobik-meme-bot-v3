#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ ЦЕНТРАЛІЗОВАНА КОНФІГУРАЦІЯ УКРАЇНСЬКОГО TELEGRAM БОТА ⚙️

Всі налаштування проекту в одному місці з підтримкою:
✅ Environment variables
✅ Fallback значення для розробки
✅ Валідація конфігурації
✅ Різні режими (development, production)
✅ Детальне логування налаштувань
"""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

# Налаштування логування для конфігурації
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== РЕЖИМ РОБОТИ =====
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, production, testing
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

logger.info(f"🔧 Завантаження конфігурації для режиму: {ENVIRONMENT}")

# ===== TELEGRAM BOT НАЛАШТУВАННЯ =====

# Основні налаштування бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "BobikFun_bot")

# Адміністратори (можна додати кілька через кому)
ADMIN_ID = int(os.getenv("ADMIN_ID", "603047391"))
ADDITIONAL_ADMINS = os.getenv("ADDITIONAL_ADMINS", "").split(",") if os.getenv("ADDITIONAL_ADMINS") else []
ALL_ADMIN_IDS = [ADMIN_ID] + [int(aid.strip()) for aid in ADDITIONAL_ADMINS if aid.strip().isdigit()]

# Налаштування webhook (для production)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", f"/webhook/{BOT_TOKEN}" if BOT_TOKEN else "/webhook")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("PORT", os.getenv("WEBHOOK_PORT", "8000")))

# Налаштування polling (для development)
POLLING_TIMEOUT = int(os.getenv("POLLING_TIMEOUT", "30"))
POLLING_LIMIT = int(os.getenv("POLLING_LIMIT", "100"))

logger.info(f"🤖 Bot налаштування: Username={BOT_USERNAME}, Admins={len(ALL_ADMIN_IDS)}")

# ===== БАЗА ДАНИХ =====

# PostgreSQL (основна БД для production)
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLite (fallback для розробки)
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/bot.db")

# Налаштування connection pool
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
DB_ECHO = os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes")

# Timeout'и
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
DB_QUERY_TIMEOUT = int(os.getenv("DB_QUERY_TIMEOUT", "30"))

logger.info(f"💾 Database: {'PostgreSQL' if DATABASE_URL else 'SQLite fallback'}")

# ===== АВТОМАТИЗАЦІЯ ТА ПЛАНУВАЛЬНИК =====

# Часова зона для планувальника
TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")

# Налаштування завдань (можна вимкнути окремі завдання)
AUTOMATION_ENABLED = os.getenv("AUTOMATION_ENABLED", "true").lower() in ("true", "1", "yes")
MORNING_BROADCAST_ENABLED = os.getenv("MORNING_BROADCAST_ENABLED", "true").lower() in ("true", "1", "yes")
EVENING_STATS_ENABLED = os.getenv("EVENING_STATS_ENABLED", "true").lower() in ("true", "1", "yes")
WEEKLY_TOURNAMENT_ENABLED = os.getenv("WEEKLY_TOURNAMENT_ENABLED", "true").lower() in ("true", "1", "yes")
DAILY_CLEANUP_ENABLED = os.getenv("DAILY_CLEANUP_ENABLED", "true").lower() in ("true", "1", "yes")
DUEL_CHECK_ENABLED = os.getenv("DUEL_CHECK_ENABLED", "true").lower() in ("true", "1", "yes")

# Розклад автоматичних завдань
MORNING_BROADCAST_TIME = {"hour": int(os.getenv("MORNING_BROADCAST_HOUR", "9")), "minute": 0}
EVENING_STATS_TIME = {"hour": int(os.getenv("EVENING_STATS_HOUR", "20")), "minute": 0}
WEEKLY_TOURNAMENT_TIME = {"day_of_week": 4, "hour": 19, "minute": 0}  # П'ятниця
DAILY_CLEANUP_TIME = {"hour": 3, "minute": 0}
WEEKLY_DIGEST_TIME = {"day_of_week": 6, "hour": 18, "minute": 0}  # Неділя
MONTHLY_SUMMARY_TIME = {"day": 1, "hour": 12, "minute": 0}

# Інтервали перевірок (хвилини)
DUEL_CHECK_INTERVAL = int(os.getenv("DUEL_CHECK_INTERVAL", "1"))
DUEL_REMINDER_INTERVAL = int(os.getenv("DUEL_REMINDER_INTERVAL", "15"))
ACHIEVEMENT_CHECK_INTERVAL = int(os.getenv("ACHIEVEMENT_CHECK_INTERVAL", "30"))

logger.info(f"🤖 Автоматизація: {'Активна' if AUTOMATION_ENABLED else 'Вимкнена'}")

# ===== ГЕЙМІФІКАЦІЯ ТА БАЛИ =====

# Нарахування балів
POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "5"))      # За подачу контенту
POINTS_FOR_APPROVAL = int(os.getenv("POINTS_FOR_APPROVAL", "15"))         # За схвалення
POINTS_FOR_LIKE = int(os.getenv("POINTS_FOR_LIKE", "1"))                  # За лайк
POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "20"))         # За перемогу в дуелі
POINTS_FOR_DUEL_PARTICIPATION = int(os.getenv("POINTS_FOR_DUEL_PARTICIPATION", "2"))  # За участь
POINTS_FOR_VOTE = int(os.getenv("POINTS_FOR_VOTE", "1"))                  # За голосування
POINTS_FOR_COMMENT = int(os.getenv("POINTS_FOR_COMMENT", "1"))            # За коментар
POINTS_FOR_DAILY_STREAK = int(os.getenv("POINTS_FOR_DAILY_STREAK", "5"))  # За щоденну активність

# Штрафні бали
POINTS_PENALTY_REJECTION = int(os.getenv("POINTS_PENALTY_REJECTION", "-2"))  # За відхилення
POINTS_PENALTY_SPAM = int(os.getenv("POINTS_PENALTY_SPAM", "-10"))           # За спам
POINTS_PENALTY_INAPPROPRIATE = int(os.getenv("POINTS_PENALTY_INAPPROPRIATE", "-5"))  # За неприйнятний контент

# Ранги та їх мінімальні бали
RANK_REQUIREMENTS = {
    "🤡 Новачок": 0,
    "😄 Сміхун": int(os.getenv("RANK_JOKER_POINTS", "100")),
    "😂 Гуморист": int(os.getenv("RANK_COMEDIAN_POINTS", "250")),
    "🎭 Комік": int(os.getenv("RANK_HUMORIST_POINTS", "500")),
    "👑 Мастер Рофлу": int(os.getenv("RANK_MASTER_POINTS", "1000")),
    "🏆 Король Гумору": int(os.getenv("RANK_EXPERT_POINTS", "2500")),
    "🌟 Легенда Мемів": int(os.getenv("RANK_VIRTUOSO_POINTS", "5000")),
    "🚀 Гумористичний Геній": int(os.getenv("RANK_LEGEND_POINTS", "10000"))
}

logger.info(f"🎮 Гейміфікація: {len(RANK_REQUIREMENTS)} рангів, {POINTS_FOR_APPROVAL} балів за схвалення")

# ===== КОНТЕНТ ТА МОДЕРАЦІЯ =====

# Типи контенту
CONTENT_TYPES = ["joke", "meme", "anekdot"]
CONTENT_STATUSES = ["pending", "approved", "rejected"]

# Ліміти контенту
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "2000"))         # Максимальна довжина тексту
MAX_SUBMISSIONS_PER_DAY = int(os.getenv("MAX_SUBMISSIONS_PER_DAY", "10")) # Максимум подач на день
MAX_PENDING_CONTENT = int(os.getenv("MAX_PENDING_CONTENT", "100"))        # Максимум в черзі модерації

# Автомодерація
AUTO_MODERATION_ENABLED = os.getenv("AUTO_MODERATION_ENABLED", "false").lower() in ("true", "1", "yes")
AUTO_REJECT_PROFANITY = os.getenv("AUTO_REJECT_PROFANITY", "true").lower() in ("true", "1", "yes")
AUTO_REJECT_SPAM = os.getenv("AUTO_REJECT_SPAM", "true").lower() in ("true", "1", "yes")

# Час очікування модерації (години)
MODERATION_TIMEOUT_HOURS = int(os.getenv("MODERATION_TIMEOUT_HOURS", "24"))

logger.info(f"📝 Контент: {len(CONTENT_TYPES)} типів, макс {MAX_SUBMISSIONS_PER_DAY} подач/день")

# ===== ДУЕЛІ ТА ЗМАГАННЯ =====

# Налаштування дуелей
DUEL_ENABLED = os.getenv("DUEL_ENABLED", "true").lower() in ("true", "1", "yes")
DUEL_DURATION_HOURS = int(os.getenv("DUEL_DURATION_HOURS", "24"))         # Тривалість дуелі
DUEL_MIN_VOTES = int(os.getenv("DUEL_MIN_VOTES", "5"))                    # Мінімум голосів для визначення переможця
DUEL_MAX_PARTICIPANTS = int(os.getenv("DUEL_MAX_PARTICIPANTS", "100"))    # Максимум учасників голосування

# Турніри
TOURNAMENT_ENABLED = os.getenv("TOURNAMENT_ENABLED", "true").lower() in ("true", "1", "yes")
TOURNAMENT_MIN_PARTICIPANTS = int(os.getenv("TOURNAMENT_MIN_PARTICIPANTS", "4"))
TOURNAMENT_DURATION_DAYS = int(os.getenv("TOURNAMENT_DURATION_DAYS", "7"))

# Швидкі дуелі
QUICK_DUEL_ENABLED = os.getenv("QUICK_DUEL_ENABLED", "true").lower() in ("true", "1", "yes")
QUICK_DUEL_DURATION_MINUTES = int(os.getenv("QUICK_DUEL_DURATION_MINUTES", "30"))

logger.info(f"⚔️ Дуелі: {'Активні' if DUEL_ENABLED else 'Вимкнені'}, тривалість {DUEL_DURATION_HOURS}г")

# ===== РОЗСИЛКИ ТА ПОВІДОМЛЕННЯ =====

# Налаштування розсилок
BROADCAST_ENABLED = os.getenv("BROADCAST_ENABLED", "true").lower() in ("true", "1", "yes")
BROADCAST_RATE_LIMIT = int(os.getenv("BROADCAST_RATE_LIMIT", "30"))       # Повідомлень на секунду
BROADCAST_CHUNK_SIZE = int(os.getenv("BROADCAST_CHUNK_SIZE", "100"))       # Розмір батчу

# Типи повідомлень
DAILY_DIGEST_ENABLED = os.getenv("DAILY_DIGEST_ENABLED", "true").lower() in ("true", "1", "yes")
WEEKLY_DIGEST_ENABLED = os.getenv("WEEKLY_DIGEST_ENABLED", "true").lower() in ("true", "1", "yes")
ACHIEVEMENT_NOTIFICATIONS = os.getenv("ACHIEVEMENT_NOTIFICATIONS", "true").lower() in ("true", "1", "yes")
DUEL_NOTIFICATIONS = os.getenv("DUEL_NOTIFICATIONS", "true").lower() in ("true", "1", "yes")

# Шаблони повідомлень
WELCOME_MESSAGE_ENABLED = os.getenv("WELCOME_MESSAGE_ENABLED", "true").lower() in ("true", "1", "yes")

logger.info(f"📢 Розсилки: {'Активні' if BROADCAST_ENABLED else 'Вимкнені'}, {BROADCAST_RATE_LIMIT} msg/sec")

# ===== БЕЗПЕКА ТА АНТИ-СПАМ =====

# Захист від спаму
RATE_LIMITING_ENABLED = os.getenv("RATE_LIMITING_ENABLED", "true").lower() in ("true", "1", "yes")
MAX_MESSAGES_PER_MINUTE = int(os.getenv("MAX_MESSAGES_PER_MINUTE", "10"))  # Максимум повідомлень від користувача
SPAM_DETECTION_ENABLED = os.getenv("SPAM_DETECTION_ENABLED", "true").lower() in ("true", "1", "yes")

# Система попереджень
WARNING_SYSTEM_ENABLED = os.getenv("WARNING_SYSTEM_ENABLED", "true").lower() in ("true", "1", "yes")
MAX_WARNINGS_BEFORE_BAN = int(os.getenv("MAX_WARNINGS_BEFORE_BAN", "3"))
AUTO_BAN_DURATION_HOURS = int(os.getenv("AUTO_BAN_DURATION_HOURS", "24"))

# Фільтрація контенту
CONTENT_FILTER_ENABLED = os.getenv("CONTENT_FILTER_ENABLED", "true").lower() in ("true", "1", "yes")
PROFANITY_FILTER_ENABLED = os.getenv("PROFANITY_FILTER_ENABLED", "true").lower() in ("true", "1", "yes")

logger.info(f"🛡️ Безпека: Rate limiting {'ON' if RATE_LIMITING_ENABLED else 'OFF'}, {MAX_WARNINGS_BEFORE_BAN} попереджень до бану")

# ===== КЕШУВАННЯ ТА ПРОДУКТИВНІСТЬ =====

# Redis кеш (опціонально)
REDIS_URL = os.getenv("REDIS_URL")
CACHE_ENABLED = bool(REDIS_URL) and os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))            # 1 година за замовчуванням

# In-memory кеш (fallback)
MEMORY_CACHE_SIZE = int(os.getenv("MEMORY_CACHE_SIZE", "1000"))            # Максимум об'єктів в кеші

# Налаштування продуктивності
ASYNC_WORKERS = int(os.getenv("ASYNC_WORKERS", "4"))                      # Кількість async worker'ів
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))

logger.info(f"⚡ Продуктивність: {ASYNC_WORKERS} worker'ів, кеш {'Redis' if REDIS_URL else 'Memory'}")

# ===== ЛОГУВАННЯ ТА МОНІТОРИНГ =====

# Рівні логування
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = os.getenv("LOG_FILE")  # Шлях до файлу логів (опціонально)

# Sentry для моніторингу помилок (опціонально)
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENABLED = bool(SENTRY_DSN)

# Метрики
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "false").lower() in ("true", "1", "yes")
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))

logger.info(f"📊 Логування: {LOG_LEVEL}, Sentry {'ON' if SENTRY_ENABLED else 'OFF'}")

# ===== ФАЙЛИ ТА МЕДІА =====

# Шляхи до файлів
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MEDIA_DIR = DATA_DIR / "media"
BACKUP_DIR = DATA_DIR / "backups"
LOGS_DIR = DATA_DIR / "logs"

# Створення директорій
for directory in [DATA_DIR, MEDIA_DIR, BACKUP_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Ліміти файлів
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))               # Максимальний розмір файлу
ALLOWED_MEDIA_TYPES = os.getenv("ALLOWED_MEDIA_TYPES", "photo,video,document").split(",")

# Очистка старих файлів
AUTO_CLEANUP_ENABLED = os.getenv("AUTO_CLEANUP_ENABLED", "true").lower() in ("true", "1", "yes")
CLEANUP_OLDER_THAN_DAYS = int(os.getenv("CLEANUP_OLDER_THAN_DAYS", "30"))

logger.info(f"📁 Файли: {DATA_DIR}, макс {MAX_FILE_SIZE_MB}MB, очистка через {CLEANUP_OLDER_THAN_DAYS} днів")

# ===== ІНТЕГРАЦІЇ ТА API =====

# Зовнішні API (опціонально)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")                             # Для AI генерації жартів
TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY")                   # Для перекладу
ANALYTICS_API_KEY = os.getenv("ANALYTICS_API_KEY")                       # Для аналітики

# Webhook інтеграції
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")                   # Для сповіщень в Discord
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")                       # Для сповіщень в Slack

logger.info(f"🔗 Інтеграції: OpenAI {'ON' if OPENAI_API_KEY else 'OFF'}, Discord {'ON' if DISCORD_WEBHOOK_URL else 'OFF'}")

# ===== ВАЛІДАЦІЯ КОНФІГУРАЦІЇ =====

def validate_config() -> List[str]:
    """Валідація критичних налаштувань"""
    errors = []
    
    # Критичні налаштування
    if not BOT_TOKEN:
        errors.append("❌ BOT_TOKEN не встановлено!")
    
    if not DATABASE_URL and ENVIRONMENT == "production":
        errors.append("⚠️ DATABASE_URL не встановлено для production!")
    
    if ADMIN_ID <= 0:
        errors.append("❌ ADMIN_ID має бути валідним Telegram User ID!")
    
    # Перевірка діапазонів значень
    if not (1 <= DUEL_DURATION_HOURS <= 168):  # 1 година - 1 тиждень
        errors.append(f"⚠️ DUEL_DURATION_HOURS ({DUEL_DURATION_HOURS}) поза допустимим діапазоном (1-168)")
    
    if not (1 <= BROADCAST_RATE_LIMIT <= 100):
        errors.append(f"⚠️ BROADCAST_RATE_LIMIT ({BROADCAST_RATE_LIMIT}) поза допустимим діапазоном (1-100)")
    
    return errors

# ===== КОНФІГУРАЦІЯ ДЛЯ РІЗНИХ РЕЖИМІВ =====

if ENVIRONMENT == "development":
    # Налаштування для розробки
    DB_ECHO = True  # Показувати SQL запити
    CACHE_TTL_SECONDS = 60  # Короткий час кешування
    MAX_SUBMISSIONS_PER_DAY = 100  # Більше подач для тестування
    
elif ENVIRONMENT == "production":
    # Налаштування для production
    DB_ECHO = False  # Не показувати SQL запити
    RATE_LIMITING_ENABLED = True  # Строгий rate limiting
    AUTO_CLEANUP_ENABLED = True  # Автоматична очистка
    
elif ENVIRONMENT == "testing":
    # Налаштування для тестування
    AUTOMATION_ENABLED = False  # Вимкнути автоматизацію
    BROADCAST_ENABLED = False   # Вимкнути розсилки
    MAX_SUBMISSIONS_PER_DAY = 1000  # Необмежені подачі для тестів

# ===== ЕКСПОРТ КОНФІГУРАЦІЇ =====

# Словник з усіма налаштуваннями для легкого доступу
CONFIG = {
    "environment": ENVIRONMENT,
    "debug": DEBUG,
    "bot": {
        "token": BOT_TOKEN,
        "username": BOT_USERNAME,
        "admin_ids": ALL_ADMIN_IDS,
        "webhook": {
            "url": WEBHOOK_URL,
            "path": WEBHOOK_PATH,
            "host": WEBHOOK_HOST,
            "port": WEBHOOK_PORT
        }
    },
    "database": {
        "url": DATABASE_URL,
        "pool_size": DB_POOL_SIZE,
        "echo": DB_ECHO
    },
    "automation": {
        "enabled": AUTOMATION_ENABLED,
        "timezone": TIMEZONE,
        "schedules": {
            "morning_broadcast": MORNING_BROADCAST_TIME,
            "evening_stats": EVENING_STATS_TIME,
            "weekly_tournament": WEEKLY_TOURNAMENT_TIME
        }
    },
    "gamification": {
        "points": {
            "submission": POINTS_FOR_SUBMISSION,
            "approval": POINTS_FOR_APPROVAL,
            "duel_win": POINTS_FOR_DUEL_WIN
        },
        "ranks": RANK_REQUIREMENTS
    },
    "content": {
        "types": CONTENT_TYPES,
        "max_length": MAX_CONTENT_LENGTH,
        "max_per_day": MAX_SUBMISSIONS_PER_DAY
    },
    "duels": {
        "enabled": DUEL_ENABLED,
        "duration_hours": DUEL_DURATION_HOURS,
        "min_votes": DUEL_MIN_VOTES
    },
    "security": {
        "rate_limiting": RATE_LIMITING_ENABLED,
        "max_messages_per_minute": MAX_MESSAGES_PER_MINUTE,
        "max_warnings": MAX_WARNINGS_BEFORE_BAN
    }
}

# ===== ЛОГУВАННЯ КОНФІГУРАЦІЇ =====

def log_config_summary():
    """Логування резюме конфігурації при запуску"""
    logger.info("⚙️" + "="*50)
    logger.info("⚙️ КОНФІГУРАЦІЯ УКРАЇНСЬКОГО TELEGRAM БОТА")
    logger.info("⚙️" + "="*50)
    logger.info(f"🎯 Режим: {ENVIRONMENT.upper()}")
    logger.info(f"🤖 Бот: @{BOT_USERNAME}")
    logger.info(f"👑 Адмінів: {len(ALL_ADMIN_IDS)}")
    logger.info(f"💾 БД: {'PostgreSQL' if DATABASE_URL else 'SQLite'}")
    logger.info(f"🤖 Автоматизація: {'ON' if AUTOMATION_ENABLED else 'OFF'}")
    logger.info(f"⚔️ Дуелі: {'ON' if DUEL_ENABLED else 'OFF'}")
    logger.info(f"📢 Розсилки: {'ON' if BROADCAST_ENABLED else 'OFF'}")
    logger.info(f"🛡️ Безпека: {'ON' if RATE_LIMITING_ENABLED else 'OFF'}")
    logger.info(f"⚡ Кеш: {'Redis' if REDIS_URL else 'Memory'}")
    logger.info("⚙️" + "="*50)
    
    # Перевірка та логування помилок конфігурації
    config_errors = validate_config()
    if config_errors:
        logger.error("🚨 ПОМИЛКИ КОНФІГУРАЦІЇ:")
        for error in config_errors:
            logger.error(f"   {error}")
        logger.error("🚨 ВИПРАВТЕ ПОМИЛКИ ПЕРЕД ЗАПУСКОМ!")
    else:
        logger.info("✅ Конфігурація валідна!")

# Виконати логування при імпорті
if __name__ != "__main__":
    log_config_summary()

# ===== ФУНКЦІЇ ДОПОМІЖНИКІВ =====

def get_config(key_path: str, default: Any = None) -> Any:
    """
    Отримати значення конфігурації по шляху з крапками
    
    Args:
        key_path: Шлях до значення, напр. "bot.webhook.port"
        default: Значення за замовчуванням
    
    Returns:
        Значення конфігурації або default
    """
    try:
        keys = key_path.split(".")
        value = CONFIG
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def is_admin(user_id: int) -> bool:
    """Перевірити чи користувач є адміністратором"""
    return user_id in ALL_ADMIN_IDS

def get_points_for_action(action: str) -> int:
    """Отримати кількість балів за дію"""
    points_map = {
        "submission": POINTS_FOR_SUBMISSION,
        "approval": POINTS_FOR_APPROVAL,
        "like": POINTS_FOR_LIKE,
        "duel_win": POINTS_FOR_DUEL_WIN,
        "duel_participation": POINTS_FOR_DUEL_PARTICIPATION,
        "vote": POINTS_FOR_VOTE,
        "comment": POINTS_FOR_COMMENT,
        "daily_streak": POINTS_FOR_DAILY_STREAK,
        "rejection": POINTS_PENALTY_REJECTION,
        "spam": POINTS_PENALTY_SPAM,
        "inappropriate": POINTS_PENALTY_INAPPROPRIATE
    }
    return points_map.get(action, 0)

def get_rank_for_points(points: int) -> str:
    """Отримати ранг для кількості балів"""
    for rank, min_points in reversed(list(RANK_REQUIREMENTS.items())):
        if points >= min_points:
            return rank
    return "🤡 Новачок"

# ===== ЕКСПОРТ =====
__all__ = [
    # Основні налаштування
    "ENVIRONMENT", "DEBUG", "BOT_TOKEN", "BOT_USERNAME", "ALL_ADMIN_IDS",
    
    # База даних
    "DATABASE_URL", "DB_POOL_SIZE", "DB_ECHO",
    
    # Автоматизація
    "AUTOMATION_ENABLED", "TIMEZONE", 
    "MORNING_BROADCAST_TIME", "EVENING_STATS_TIME", "WEEKLY_TOURNAMENT_TIME",
    
    # Гейміфікація
    "POINTS_FOR_SUBMISSION", "POINTS_FOR_APPROVAL", "POINTS_FOR_DUEL_WIN",
    "RANK_REQUIREMENTS",
    
    # Контент
    "CONTENT_TYPES", "MAX_CONTENT_LENGTH", "MAX_SUBMISSIONS_PER_DAY",
    
    # Дуелі
    "DUEL_ENABLED", "DUEL_DURATION_HOURS", "DUEL_MIN_VOTES",
    
    # Безпека
    "RATE_LIMITING_ENABLED", "MAX_MESSAGES_PER_MINUTE", "MAX_WARNINGS_BEFORE_BAN",
    
    # Утиліти
    "CONFIG", "get_config", "is_admin", "get_points_for_action", "get_rank_for_points",
    "validate_config", "log_config_summary"
]

logger.info(f"⚙️ Settings модуль завантажено: {len(__all__)} налаштувань")