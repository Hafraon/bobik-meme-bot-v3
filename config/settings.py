#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Спрощена конфігурація україномовного бота 🧠😂🔥
"""

import os
from typing import Optional, Dict

class Settings:
    """Клас налаштувань бота"""
    
    def __init__(self):
        # ===============================
        # ОСНОВНІ НАЛАШТУВАННЯ
        # ===============================
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        self.ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        
        # ===============================
        # БАЗА ДАНИХ
        # ===============================
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        
        # ===============================
        # AI ГЕНЕРАЦІЯ
        # ===============================
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # ===============================
        # ГЕЙМІФІКАЦІЯ
        # ===============================
        self.POINTS_FOR_REACTION = int(os.getenv("POINTS_FOR_REACTION", "5"))
        self.POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
        self.POINTS_FOR_APPROVAL = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
        self.POINTS_FOR_TOP_JOKE = int(os.getenv("POINTS_FOR_TOP_JOKE", "50"))
        
        # ===============================
        # РАНГИ КОРИСТУВАЧІВ
        # ===============================
        self.RANKS = {
            0: "🤡 Новачок",
            50: "😄 Сміхун", 
            150: "😂 Гуморист",
            350: "🎭 Комік",
            750: "👑 Мастер Рофлу",
            1500: "🏆 Король Гумору",
            3000: "🌟 Легенда Мемів",
            5000: "🚀 Гумористичний Геній"
        }
        
        # ===============================
        # ЩОДЕННА РОЗСИЛКА
        # ===============================
        self.DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
        self.DAILY_BROADCAST_MINUTE = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
        
        # ===============================
        # ОБМЕЖЕННЯ КОНТЕНТУ
        # ===============================
        self.MAX_JOKE_LENGTH = int(os.getenv("MAX_JOKE_LENGTH", "1000"))
        self.MAX_MEME_CAPTION_LENGTH = int(os.getenv("MAX_MEME_CAPTION_LENGTH", "200"))
        self.MAX_PENDING_SUBMISSIONS = int(os.getenv("MAX_PENDING_SUBMISSIONS", "100"))
        
        # ===============================
        # ДУЕЛІ
        # ===============================
        self.DUEL_VOTING_TIME = int(os.getenv("DUEL_VOTING_TIME", "300"))  # 5 хвилин
        self.MIN_VOTES_FOR_DUEL = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
        
        # ===============================
        # ДОДАТКОВІ НАЛАШТУВАННЯ
        # ===============================
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")
        
        # ===============================
        # БЕЗПЕКА ТА АНТИ-СПАМ
        # ===============================
        self.RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "3"))
        self.RATE_LIMIT_CALLBACKS = int(os.getenv("RATE_LIMIT_CALLBACKS", "5"))
        
        # Валідація
        self._validate()
    
    def _validate(self):
        """Валідація налаштувань"""
        if not self.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN не може бути порожнім! Додайте токен до .env файлу")
        if not self.ADMIN_ID:
            raise ValueError("❌ ADMIN_ID не може бути 0! Додайте ваш Telegram ID до .env файлу")
        
        print(f"✅ Налаштування завантажено")
        print(f"🤖 Бот токен: {self.BOT_TOKEN[:10]}...")
        print(f"👤 Адміністратор: {self.ADMIN_ID}")
        if self.OPENAI_API_KEY:
            print(f"🧠 AI активний: {self.OPENAI_MODEL}")
        else:
            print("⚠️ AI вимкнений (немає OpenAI API ключа)")

# Створення глобального екземпляру налаштувань
settings = Settings()

# ===============================
# ЕМОДЗІ ДЛЯ ІНТЕРФЕЙСУ
# ===============================
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
    "money": "💰",
    "gift": "🎁",
    "link": "🔗",
    "shield": "🛡️",
    "gem": "💎"
}

# ===============================
# ТЕКСТИ ІНТЕРФЕЙСУ
# ===============================
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
        f"{EMOJI['fire']} <b>ГЕЙМІФІКАЦІЯ:</b>\n"
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
    ),
    
    "daily_enabled": (
        f"{EMOJI['check']} <b>Щоденну розсилку увімкнено!</b>\n\n"
        f"{EMOJI['calendar']} Щодня о {settings.DAILY_BROADCAST_HOUR}:00 ти отримуватимеш:\n"
        f"{EMOJI['brain']} Найкращий анекдот дня\n"
        f"{EMOJI['laugh']} Топовий мем\n"
        f"{EMOJI['fire']} Мотиваційне повідомлення\n\n"
        f"{EMOJI['star']} За щоденну активність: +2 бали!"
    ),
    
    "daily_disabled": (
        f"{EMOJI['cross']} <b>Щоденну розсилку вимкнено</b>\n\n"
        f"{EMOJI['thinking']} Ти завжди можеш увімкнути її знову через /daily"
    ),
    
    "rate_limit": f"{EMOJI['warning']} Забагато запитів! Зачекай трохи перед наступною командою.",
    
    "premium_info": (
        f"{EMOJI['gem']} <b>ПРЕМІУМ ПІДПИСКА</b>\n\n"
        f"{EMOJI['star']} Що входить:\n"
        f"• Ексклюзивні меми\n"
        f"• Пріоритет в дуелях\n" 
        f"• Додаткові бали\n"
        f"• Без обмежень\n\n"
        f"{EMOJI['money']} Вартість: $2.99/міс\n"
        f"{EMOJI['info']} Зв'яжіться з адміністратором"
    ),
    
    "support_info": (
        f"{EMOJI['heart']} <b>ПІДТРИМКА ПРОЕКТУ</b>\n\n"
        f"{EMOJI['star']} Допоможи розвитку бота:\n"
        f"{EMOJI['money']} Monobank: 5375 4141 xxxx xxxx\n"
        f"{EMOJI['money']} PrivatBank: 5168 7554 xxxx xxxx\n"
        f"{EMOJI['link']} PayPal: donate@example.com\n\n"
        f"{EMOJI['gift']} За донат від $5 - спеціальний ранг!"
    )
}

# ===============================
# КОНТЕКСТНІ ПРИВІТАННЯ
# ===============================  
TIME_GREETINGS = {
    "morning": [
        f"{EMOJI['fire']} Доброго ранку!", 
        f"{EMOJI['brain']} Ранковий заряд гумору!",
        f"{EMOJI['star']} Гарного ранку!"
    ],
    "day": [
        f"{EMOJI['laugh']} Гарного дня!", 
        f"{EMOJI['star']} Денний мем для настрою!",
        f"{EMOJI['fire']} Привіт!"
    ], 
    "evening": [
        f"{EMOJI['cool']} Доброго вечора!", 
        f"{EMOJI['party']} Вечірній релакс з гумором!",
        f"{EMOJI['wink']} Добрий вечір!"
    ],
    "night": [
        f"{EMOJI['wink']} Доброї ночі!", 
        f"{EMOJI['thinking']} Нічний жарт для сну!",
        f"{EMOJI['star']} Солодких снів!"
    ]
}