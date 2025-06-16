#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Конфігурація україномовного Telegram-бота 🧠😂🔥
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    """Налаштування бота"""
    
    # Telegram Bot API
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    
    # Канал для публікацій
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    # База даних
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
    
    # OpenAI API (опціонально для генерації контенту)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Налаштування гейміфікації
    POINTS_FOR_REACTION: int = int(os.getenv("POINTS_FOR_REACTION", "5"))
    POINTS_FOR_SUBMISSION: int = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
    POINTS_FOR_APPROVAL: int = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
    POINTS_FOR_TOP_JOKE: int = int(os.getenv("POINTS_FOR_TOP_JOKE", "50"))
    
    # Ранги користувачів
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
    
    # Налаштування модерації
    MAX_PENDING_SUBMISSIONS: int = int(os.getenv("MAX_PENDING_SUBMISSIONS", "100"))
    AUTO_APPROVE_THRESHOLD: int = int(os.getenv("AUTO_APPROVE_THRESHOLD", "1000"))
    
    # Час для щоденної розсилки
    DAILY_BROADCAST_HOUR: int = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
    DAILY_BROADCAST_MINUTE: int = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
    
    # Максимальна довжина тексту
    MAX_JOKE_LENGTH: int = int(os.getenv("MAX_JOKE_LENGTH", "1000"))
    MAX_MEME_CAPTION_LENGTH: int = int(os.getenv("MAX_MEME_CAPTION_LENGTH", "200"))
    
    # Налаштування дуелей
    DUEL_VOTING_TIME: int = int(os.getenv("DUEL_VOTING_TIME", "300"))  # 5 хвилин
    MIN_VOTES_FOR_DUEL: int = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
    
    # Логування
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Веб-сервер (для Railway)
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Режим розробки
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    def __post_init__(self):
        """Валідація налаштувань"""
        if not self.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN не може бути порожнім")
        if not self.ADMIN_ID:
            raise ValueError("❌ ADMIN_ID не може бути 0")

# Створення глобального екземпляру налаштувань
settings = Settings()

# Емодзі для різних функцій
EMOJI = {
    "brain": "🧠",
    "laugh": "😂", 
    "fire": "🔥",
    "star": "⭐",
    "trophy": "🏆",
    "crown": "👑",
    "rocket": "🚀",
    "heart": "❤️",
    "like": "👍",
    "dislike": "👎",
    "thinking": "🤔",
    "cool": "😎",
    "wink": "😉",
    "party": "🎉",
    "boom": "💥",
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "new": "🆕",
    "top": "🔝",
    "vs": "⚔️",
    "time": "⏰",
    "calendar": "📅",
    "stats": "📊",
    "profile": "👤",
    "settings": "⚙️",
    "help": "❓",
    "hand": "✋"
}

# Тексти привітань та інформації
TEXTS = {
    "start": (
        f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю в україномовному боті мемів та анекдотів!</b>\n\n"
        f"{EMOJI['star']} <b>Що я вмію:</b>\n"
        f"{EMOJI['laugh']} /meme - випадковий мем\n"
        f"{EMOJI['brain']} /anekdot - український анекдот\n"
        f"{EMOJI['fire']} /submit - надіслати свій жарт\n"
        f"{EMOJI['calendar']} /daily - щоденна розсилка\n"
        f"{EMOJI['profile']} /profile - твій профіль\n"
        f"{EMOJI['top']} /top - таблиця лідерів\n"
        f"{EMOJI['vs']} /duel - дуель жартів\n"
        f"{EMOJI['help']} /help - допомога\n\n"
        f"{EMOJI['party']} <b>Отримуй бали за активність і ставай легендою гумору!</b>"
    ),
    
    "help": (
        f"{EMOJI['help']} <b>ДОВІДКА ПО БОТУ</b> {EMOJI['help']}\n\n"
        f"{EMOJI['brain']} <b>ОСНОВНІ КОМАНДИ:</b>\n"
        f"• /meme - отримати випадковий мем\n"
        f"• /anekdot - отримати український анекдот\n"
        f"• /submit - надіслати свій мем або анекдот\n"
        f"• /daily - підписатися/відписатися від щоденної розсилки\n\n"
        f"{EMOJI['fire']} <b>ГЕЙМФІКАЦІЯ:</b>\n"
        f"• /profile - переглянути свій профіль\n"
        f"• /top - таблиця лідерів\n"
        f"• /duel - започаткувати дуель жартів\n\n"
        f"{EMOJI['star']} <b>БАЛИ ЗА АКТИВНІСТЬ:</b>\n"
        f"• +5 балів - за реакцію на мем\n"
        f"• +10 балів - за надісланий жарт\n"
        f"• +20 балів - якщо жарт схвалено\n"
        f"• +50 балів - якщо жарт потрапив до ТОПу\n\n"
        f"{EMOJI['rocket']} <b>Дякуємо за використання бота!</b>"
    ),
    
    "no_content": f"{EMOJI['thinking']} Упс! Контент закінчився. Спробуй пізніше або надішли свій жарт!",
    
    "submission_received": (
        f"{EMOJI['check']} <b>Дякую за твій жарт!</b>\n\n"
        f"{EMOJI['brain']} Він відправлений на модерацію\n"
        f"{EMOJI['fire']} Ти отримав +{settings.POINTS_FOR_SUBMISSION} балів\n"
        f"{EMOJI['time']} Очікуй результат протягом 24 годин"
    ),
    
    "submission_approved": (
        f"{EMOJI['party']} <b>УРА! Твій жарт схвалено!</b>\n\n"
        f"{EMOJI['star']} Він додано до загальної бази\n"
        f"{EMOJI['fire']} Ти отримав додатково +{settings.POINTS_FOR_APPROVAL} балів!"
    ),
    
    "submission_rejected": (
        f"{EMOJI['cross']} <b>Твій жарт не пройшов модерацію</b>\n\n"
        f"{EMOJI['thinking']} Можливо, він не відповідає правилам або вже є в базі\n"
        f"{EMOJI['heart']} Спробуй надіслати інший!"
    )
}

# Привітання залежно від часу дня
TIME_GREETINGS = {
    "morning": [f"{EMOJI['fire']} Доброго ранку!", f"{EMOJI['brain']} Ранковий заряд гумору!"],
    "day": [f"{EMOJI['laugh']} Гарного дня!", f"{EMOJI['star']} Денний мем для настрою!"], 
    "evening": [f"{EMOJI['cool']} Доброго вечора!", f"{EMOJI['party']} Вечірній релакс з гумором!"],
    "night": [f"{EMOJI['wink']} Доброї ночі!", f"{EMOJI['thinking']} Нічний жарт для сну!"]
}