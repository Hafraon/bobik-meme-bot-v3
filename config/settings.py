#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Конфігурація україномовного бота 🧠😂🔥
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    """Налаштування бота"""
    
    # ===== ОСНОВНІ НАЛАШТУВАННЯ TELEGRAM =====
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")  # Для публікацій (якщо потрібно)
    
    # ===== БАЗА ДАНИХ =====
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
    
    # ===== AI НАЛАШТУВАННЯ =====
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # ===== СЕРЕДОВИЩЕ ТА ЛОГУВАННЯ =====
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Kiev")
    
    # ===== ВЕБ-СЕРВЕР =====
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # ===== НАЛАШТУВАННЯ ГЕЙМІФІКАЦІЇ =====
    POINTS_FOR_REACTION: int = int(os.getenv("POINTS_FOR_REACTION", "5"))
    POINTS_FOR_SUBMISSION: int = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
    POINTS_FOR_APPROVAL: int = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
    POINTS_FOR_TOP_JOKE: int = int(os.getenv("POINTS_FOR_TOP_JOKE", "50"))
    
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
    
    # ===== БЕЗПЕКА ТА RATE LIMITING =====
    RATE_LIMIT_MESSAGES: int = int(os.getenv("RATE_LIMIT_MESSAGES", "3"))
    RATE_LIMIT_CALLBACKS: int = int(os.getenv("RATE_LIMIT_CALLBACKS", "5"))
    
    def __post_init__(self):
        """Валідація налаштувань після ініціалізації"""
        errors = []
        
        # Перевірка обов'язкових параметрів
        if not self.BOT_TOKEN:
            errors.append("BOT_TOKEN не може бути порожнім")
        if not self.ADMIN_ID:
            errors.append("ADMIN_ID не може бути 0")
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL не може бути порожнім")
        
        # Перевірка валідності часу розсилки
        if not (0 <= self.DAILY_BROADCAST_HOUR <= 23):
            errors.append("DAILY_BROADCAST_HOUR має бути від 0 до 23")
        if not (0 <= self.DAILY_BROADCAST_MINUTE <= 59):
            errors.append("DAILY_BROADCAST_MINUTE має бути від 0 до 59")
        
        if errors:
            raise ValueError("Помилки конфігурації:\n" + "\n".join(f"- {error}" for error in errors))
    
    @property
    def is_production(self) -> bool:
        """Чи працює бот у production режимі"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Чи працює бот у development режимі"""
        return self.ENVIRONMENT.lower() == "development"

# Створення глобального екземпляру налаштувань
settings = Settings()

# ===== ЕМОДЗІ ДЛЯ ІНТЕРФЕЙСУ =====
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
    "help": "❓"
}

# ===== ТЕКСТИ ІНТЕРФЕЙСУ =====
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
        f"• +{settings.POINTS_FOR_REACTION} балів - за реакцію на мем\n"
        f"• +{settings.POINTS_FOR_SUBMISSION} балів - за надісланий жарт\n"
        f"• +{settings.POINTS_FOR_APPROVAL} балів - якщо жарт схвалено\n"
        f"• +{settings.POINTS_FOR_TOP_JOKE} балів - якщо жарт потрапив до ТОПу\n\n"
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

# ===== КОНТЕКСТНІ ПРИВІТАННЯ =====
TIME_GREETINGS = {
    "morning": [
        f"{EMOJI['fire']} Доброго ранку!", 
        f"{EMOJI['brain']} Ранковий заряд гумору!",
        f"{EMOJI['star']} Доброго ранку! Починаємо день з посмішки!"
    ],
    "day": [
        f"{EMOJI['laugh']} Гарного дня!", 
        f"{EMOJI['star']} Денний мем для настрою!",
        f"{EMOJI['cool']} Приємного дня з гумором!"
    ], 
    "evening": [
        f"{EMOJI['cool']} Доброго вечора!", 
        f"{EMOJI['party']} Вечірній релакс з гумором!",
        f"{EMOJI['wink']} Доброго вечора! Час розслабитися!"
    ],
    "night": [
        f"{EMOJI['wink']} Доброї ночі!", 
        f"{EMOJI['thinking']} Нічний жарт для сну!",
        f"{EMOJI['heart']} Солодких снів з гумором!"
    ]
}