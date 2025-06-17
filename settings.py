#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Повна конфігурація бота з гейміфікацією 🧠😂🔥
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    """Налаштування бота"""
    
    # ===== TELEGRAM BOT API =====
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    # ===== БАЗА ДАНИХ =====
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
    
    # ===== AI ГЕНЕРАЦІЯ (ОПЦІОНАЛЬНО) =====
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # ===== НАЛАШТУВАННЯ ГЕЙМІФІКАЦІЇ =====
    POINTS_FOR_REACTION: int = int(os.getenv("POINTS_FOR_REACTION", "5"))
    POINTS_FOR_SUBMISSION: int = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
    POINTS_FOR_APPROVAL: int = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
    POINTS_FOR_TOP_JOKE: int = int(os.getenv("POINTS_FOR_TOP_JOKE", "50"))
    POINTS_FOR_DUEL_WIN: int = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
    POINTS_FOR_DAILY_ACTIVITY: int = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))
    POINTS_FOR_VIEW: int = int(os.getenv("POINTS_FOR_VIEW", "1"))
    
    # ===== РАНГИ КОРИСТУВАЧІВ =====
    RANKS = {
        0: "🤡 Новачок",
        50: "😄 Сміхун",
        150: "😂 Гуморист", 
        350: "🎭 Комік",
        750: "👑 Мастер Рофлу",
        1500: "🏆 Король Гумору",
        3000: "🌟 Легенда Мемів",
        5000: "🚀 Гумористичний Геній"
    }
    
    # ===== НАЛАШТУВАННЯ МОДЕРАЦІЇ =====
    MAX_PENDING_SUBMISSIONS: int = int(os.getenv("MAX_PENDING_SUBMISSIONS", "100"))
    AUTO_APPROVE_THRESHOLD: int = int(os.getenv("AUTO_APPROVE_THRESHOLD", "1000"))
    
    # ===== ЩОДЕННА РОЗСИЛКА =====
    DAILY_BROADCAST_HOUR: int = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
    DAILY_BROADCAST_MINUTE: int = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
    
    # ===== ОБМЕЖЕННЯ КОНТЕНТУ =====
    MAX_JOKE_LENGTH: int = int(os.getenv("MAX_JOKE_LENGTH", "1000"))
    MAX_MEME_CAPTION_LENGTH: int = int(os.getenv("MAX_MEME_CAPTION_LENGTH", "200"))
    
    # ===== НАЛАШТУВАННЯ ДУЕЛЕЙ =====
    DUEL_VOTING_TIME: int = int(os.getenv("DUEL_VOTING_TIME", "300"))  # 5 хвилин
    MIN_VOTES_FOR_DUEL: int = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
    
    # ===== ДОДАТКОВІ НАЛАШТУВАННЯ =====
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Kiev")
    
    def __post_init__(self):
        """Валідація налаштувань"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не може бути порожнім")
        if not self.ADMIN_ID:
            raise ValueError("ADMIN_ID не може бути 0")

# Створення глобального екземпляру налаштувань
settings = Settings()

# ===== ЕМОДЗІ ДЛЯ РІЗНИХ ФУНКЦІЙ =====
EMOJI = {
    # Основні
    "brain": "🧠",
    "laugh": "😂", 
    "fire": "🔥",
    "star": "⭐",
    "heart": "❤️",
    
    # Гейміфікація
    "trophy": "🏆",
    "crown": "👑",
    "rocket": "🚀",
    "party": "🎉",
    "boom": "💥",
    
    # Дії
    "like": "👍",
    "dislike": "👎",
    "thinking": "🤔",
    "cool": "😎",
    "wink": "😉",
    "eye": "👁️",
    
    # Статуси
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "new": "🆕",
    
    # Навігація
    "top": "🔝",
    "vs": "⚔️",
    "time": "⏰",
    "calendar": "📅",
    "stats": "📊",
    "profile": "👤",
    "settings": "⚙️",
    "help": "❓"
}

# ===== ТЕКСТИ ПРИВІТАНЬ ТА ІНФОРМАЦІЇ =====
TEXTS = {
    "start": (
        f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю в україномовному боті мемів та анекдотів!</b>\n\n"
        f"{EMOJI['star']} <b>Що я вмію:</b>\n"
        f"{EMOJI['laugh']} /meme - випадковий мем (+1 бал)\n"
        f"{EMOJI['brain']} /anekdot - український анекдот (+1 бал)\n"
        f"{EMOJI['fire']} /submit - надіслати свій жарт (+{settings.POINTS_FOR_SUBMISSION} балів)\n"
        f"{EMOJI['calendar']} /daily - щоденна розсилка (+{settings.POINTS_FOR_DAILY_ACTIVITY} бали)\n"
        f"{EMOJI['profile']} /profile - твій профіль та бали\n"
        f"{EMOJI['top']} /top - таблиця лідерів\n"
        f"{EMOJI['vs']} /duel - дуель жартів (+{settings.POINTS_FOR_DUEL_WIN} за перемогу)\n"
        f"{EMOJI['help']} /help - допомога\n\n"
        f"{EMOJI['party']} <b>Отримуй бали за активність і ставай легендою гумору!</b>"
    ),
    
    "help": (
        f"{EMOJI['help']} <b>ДОВІДКА ПО БОТУ</b> {EMOJI['help']}\n\n"
        f"{EMOJI['brain']} <b>ОСНОВНІ КОМАНДИ:</b>\n"
        f"• /meme - отримати випадковий мем (+{settings.POINTS_FOR_VIEW} бал)\n"
        f"• /anekdot - отримати український анекдот (+{settings.POINTS_FOR_VIEW} бал)\n"
        f"• /submit - надіслати свій мем або анекдот (+{settings.POINTS_FOR_SUBMISSION} балів)\n"
        f"• /daily - підписатися на щоденну розсилку\n\n"
        f"{EMOJI['fire']} <b>ГЕЙМІФІКАЦІЯ:</b>\n"
        f"• /profile - переглянути свій профіль та бали\n"
        f"• /top - таблиця лідерів\n"
        f"• /duel - започаткувати дуель жартів\n\n"
        f"{EMOJI['star']} <b>СИСТЕМА БАЛІВ:</b>\n"
        f"• +{settings.POINTS_FOR_VIEW} бал - за перегляд контенту\n"
        f"• +{settings.POINTS_FOR_REACTION} балів - за лайк мему/анекдоту\n"
        f"• +{settings.POINTS_FOR_SUBMISSION} балів - за надісланий жарт\n"
        f"• +{settings.POINTS_FOR_APPROVAL} балів - якщо жарт схвалено\n"
        f"• +{settings.POINTS_FOR_TOP_JOKE} балів - якщо жарт потрапив до ТОПу\n"
        f"• +{settings.POINTS_FOR_DUEL_WIN} балів - за перемогу в дуелі\n\n"
        f"{EMOJI['crown']} <b>РАНГИ:</b>\n"
        f"🤡 Новачок → 😄 Сміхун → 😂 Гуморист → 🎭 Комік\n"
        f"👑 Мастер Рофлу → 🏆 Король Гумору → 🌟 Легенда Мемів → 🚀 Геній\n\n"
        f"{EMOJI['rocket']} <b>Дякуємо за використання бота!</b>"
    ),
    
    "no_content": f"{EMOJI['thinking']} Упс! Контент закінчився. Спробуй пізніше або надішли свій жарт через /submit!",
    
    "submission_received": (
        f"{EMOJI['check']} <b>Дякую за твій жарт!</b>\n\n"
        f"{EMOJI['brain']} Він відправлений на модерацію\n"
        f"{EMOJI['fire']} Ти отримав +{settings.POINTS_FOR_SUBMISSION} балів\n"
        f"{EMOJI['time']} Очікуй результат протягом 24 годин\n\n"
        f"{EMOJI['info']} При схваленні отримаєш ще +{settings.POINTS_FOR_APPROVAL} балів!"
    ),
    
    "submission_approved": (
        f"{EMOJI['party']} <b>УРА! Твій жарт схвалено!</b>\n\n"
        f"{EMOJI['star']} Він додано до загальної бази\n"
        f"{EMOJI['fire']} Ти отримав додатково +{settings.POINTS_FOR_APPROVAL} балів!\n\n"
        f"{EMOJI['trophy']} Якщо він стане популярним, отримаєш ще +{settings.POINTS_FOR_TOP_JOKE} балів!"
    ),
    
    "submission_rejected": (
        f"{EMOJI['cross']} <b>Твій жарт не пройшов модерацію</b>\n\n"
        f"{EMOJI['thinking']} Можливо, він не відповідає правилам або вже є в базі\n"
        f"{EMOJI['heart']} Спробуй надіслати інший!\n\n"
        f"{EMOJI['info']} Бали за подачу залишаються у тебе"
    )
}

# ===== ВИБІР ЧАСІВ ДНЯ ДЛЯ КОНТЕКСТНИХ ПІДПИСІВ =====
TIME_GREETINGS = {
    "morning": [
        f"{EMOJI['fire']} Доброго ранку!", 
        f"{EMOJI['brain']} Ранковий заряд гумору!",
        f"{EMOJI['star']} Гарного ранку!"
    ],
    "day": [
        f"{EMOJI['laugh']} Гарного дня!", 
        f"{EMOJI['star']} Денний мем для настрою!",
        f"{EMOJI['fire']} Чудового дня!"
    ], 
    "evening": [
        f"{EMOJI['cool']} Доброго вечора!", 
        f"{EMOJI['party']} Вечірній релакс з гумором!",
        f"{EMOJI['wink']} Гарного вечора!"
    ],
    "night": [
        f"{EMOJI['thinking']} Доброї ночі!", 
        f"{EMOJI['brain']} Нічний жарт для сну!",
        f"{EMOJI['star']} Солодких снів!"
    ]
}

# ===== СПЕЦІАЛЬНІ НАЛАШТУВАННЯ ДЛЯ РІЗНИХ СЕРЕДОВИЩ =====
if settings.DEBUG:
    # Налаштування для розробки
    EMOJI["debug"] = "🔧"
    print(f"{EMOJI['warning']} Режим розробки активний!")

# ===== ФУНКЦІЇ ДЛЯ РОБОТИ З РАНГАМИ =====
def get_rank_by_points(points: int) -> str:
    """Визначення рангу по балах"""
    for min_points in sorted(settings.RANKS.keys(), reverse=True):
        if points >= min_points:
            return settings.RANKS[min_points]
    return settings.RANKS[0]

def get_next_rank_info(points: int) -> dict:
    """Інформація про наступний ранг"""
    current_rank = get_rank_by_points(points)
    
    for min_points in sorted(settings.RANKS.keys()):
        if min_points > points:
            return {
                "next_rank": settings.RANKS[min_points],
                "points_needed": min_points - points,
                "current_points": points
            }
    
    return {
        "next_rank": None,
        "points_needed": 0,
        "current_points": points
    }

# ===== ВАЛІДАЦІЯ НАЛАШТУВАНЬ ПРИ ЗАВАНТАЖЕННІ =====
def validate_settings():
    """Перевірка правильності налаштувань"""
    errors = []
    
    if not settings.BOT_TOKEN:
        errors.append("BOT_TOKEN не налаштовано")
    
    if not settings.ADMIN_ID:
        errors.append("ADMIN_ID не налаштовано")
    
    if settings.POINTS_FOR_SUBMISSION <= 0:
        errors.append("POINTS_FOR_SUBMISSION має бути більше 0")
    
    if errors:
        print(f"{EMOJI['cross']} Помилки конфігурації:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print(f"{EMOJI['check']} Конфігурація валідна!")
    return True

# Валідація при імпорті модуля
if __name__ != "__main__":
    validate_settings()