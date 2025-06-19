#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import List, Dict, Any, Optional

class Settings:
    """Повні налаштування україномовного Telegram бота"""
    
    def __init__(self):
        # Основні налаштування бота
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        self.ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        self.CHANNEL_ID = os.getenv("CHANNEL_ID", "")
        
        # База даних
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        
        # AI та генерація контенту
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Система балів
        self.POINTS_FOR_VIEW = int(os.getenv("POINTS_FOR_VIEW", "1"))
        self.POINTS_FOR_REACTION = int(os.getenv("POINTS_FOR_REACTION", "5"))
        self.POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
        self.POINTS_FOR_APPROVAL = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
        self.POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
        self.POINTS_FOR_DAILY_ACTIVITY = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))
        
        # Дуелі
        self.DUEL_VOTING_TIME = int(os.getenv("DUEL_VOTING_TIME", "300"))
        self.MIN_VOTES_FOR_DUEL = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
        self.MAX_ACTIVE_DUELS = int(os.getenv("MAX_ACTIVE_DUELS", "10"))
        
        # Щоденна розсилка
        self.DAILY_BROADCAST_ENABLED = os.getenv("DAILY_BROADCAST_ENABLED", "True").lower() == "true"
        self.DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
        self.DAILY_BROADCAST_MINUTE = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
        
        # Система
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")
        self.PORT = int(os.getenv("PORT", "8080"))
        
        # Валідація критичних налаштувань
        self._validate()
    
    def _validate(self):
        """Валідація обов'язкових налаштувань"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN є обов'язковим!")
        
        if not self.ADMIN_ID:
            raise ValueError("ADMIN_ID є обов'язковим!")
    
    def is_admin(self, user_id: int) -> bool:
        """Перевірка чи є користувач адміністратором"""
        return user_id == self.ADMIN_ID
    
    def get_all_admins(self) -> List[int]:
        """Список всіх адміністраторів"""
        return [self.ADMIN_ID] if self.ADMIN_ID else []


# Глобальний екземпляр налаштувань
settings = Settings()

# Емодзі для інтерфейсу
EMOJI = {
    'brain': '🧠',
    'fire': '🔥', 
    'laugh': '😂',
    'rocket': '🚀',
    'star': '⭐',
    'crown': '👑',
    'trophy': '🏆',
    'medal': '🥇',
    'target': '🎯',
    'chart': '📊',
    'gear': '⚙️',
    'warning': '⚠️',
    'error': '❌',
    'success': '✅',
    'info': 'ℹ️',
    'heart': '❤️',
    'ukraine': '🇺🇦',
    'meme': '😄',
    'joke': '🤣',
    'duel': '⚔️',
    'vote': '🗳️',
    'users': '👥',
    'user': '👤',
    'admin': '👨‍💼',
    'bot': '🤖',
    'clock': '🕐',
    'calendar': '📅',
    'bell': '🔔',
    'mail': '📧',
    'link': '🔗',
    'folder': '📁',
    'file': '📄',
    'database': '💾',
    'server': '🖥️',
    'settings': '⚙️',
    'plus': '➕',
    'minus': '➖',
    'arrow_right': '➡️',
    'arrow_left': '⬅️',
    'back': '🔙',
    'refresh': '🔄',
    'search': '🔍',
    'edit': '✏️',
    'delete': '🗑️',
    'save': '💾',
    'download': '⬇️',
    'upload': '⬆️'
}

# Тексти інтерфейсу українською
TEXTS = {
    # Базові повідомлення
    'start_message': """🧠😂🔥 <b>Привіт! Я професійний україномовний бот!</b>

🎮 <b>Гейміфікація:</b>
• 📊 Система балів та рангів
• 🏆 Таблиця лідерів
• ⚔️ Дуелі жартів

📱 <b>Контент:</b>
• 😂 Меми та анекдоти
• 📝 Подача власного контенту
• 🤖 AI генерація

🛡️ <b>Модерація:</b>
• ✅ Автоматичне схвалення
• 📊 Статистика та аналітика
• 🔧 Адмін панель

Оберіть дію з меню нижче! 👇""",

    'help_message': """📖 <b>Довідка по командах:</b>

👤 <b>Користувацькі команди:</b>
/start - запуск бота
/profile - ваш профіль
/top - таблиця лідерів
/meme - випадковий мем
/anekdot - український анекдот
/duel - почати дуель жартів
/submit - подати свій жарт

🛡️ <b>Адмін команди:</b>
/admin_stats - статистика бота
/moderate - модерація контенту
/pending - контент на розгляді

❓ <b>Потрібна допомога?</b>
Звертайтеся до адміністратора!""",

    # Профіль та статистика
    'profile_template': """👤 <b>Ваш профіль</b>

🆔 ID: {user_id}
👋 Ім'я: {first_name}
📅 Реєстрація: {registration_date}

🎮 <b>Статистика:</b>
⭐ Бали: {points}
👑 Ранг: {rank}
📊 Місце в рейтингу: #{position}

🎯 <b>Активність:</b>
👀 Переглядів: {views}
👍 Лайків: {likes}
📝 Подань: {submissions}
✅ Схвалень: {approvals}
⚔️ Дуелей: {duels}

💡 <b>Досягнення:</b>
{achievements}""",

    # Помилки
    'no_content': """😔 <b>Контент не знайдено</b>

На жаль, немає доступного контенту цього типу.
Спробуйте пізніше або подайте свій варіант!""",

    'permission_denied': """🔒 <b>Недостатньо прав</b>

Ця команда доступна тільки адміністраторам.""",

    'rate_limit': """⏳ <b>Забагато запитів</b>

Зачекайте трохи перед наступною дією.""",

    # Успішні дії
    'content_submitted': """✅ <b>Контент відправлено на модерацію!</b>

Дякуємо за ваш внесок! Адміністратор розгляне його найближчим часом.
За схвалення ви отримаете {points} балів!""",

    'points_awarded': """🎉 <b>Нараховано бали!</b>

Ви отримали +{points} балів за {action}!
Ваш загальний рахунок: {total_points}""",

    # Дуелі
    'duel_start': """⚔️ <b>Дуель жартів розпочато!</b>

{joke1}

VS

{joke2}

Голосуйте за кращий жарт! Голосування триватиме {time} хвилин.""",

    'duel_result': """🏆 <b>Результати дуелі!</b>

Переможець: {winner_joke}
Голосів: {winner_votes}

🎉 Переможець отримує +{points} балів!""",

    # Система рангів
    'rank_up': """🎉 <b>Підвищення рангу!</b>

Вітаємо! Ви досягли нового рангу:
{new_rank}

Ваші бали: {points}
Продовжуйте в тому ж дусі! 🚀""",

    # Адмін панель
    'admin_stats': """📊 <b>Статистика бота</b>

👥 <b>Користувачі:</b>
Всього: {total_users}
Активних за день: {daily_active}
Активних за тиждень: {weekly_active}

📝 <b>Контент:</b>
Всього: {total_content}
На модерації: {pending_content}
Схвалено: {approved_content}

⚔️ <b>Дуелі:</b>
Всього: {total_duels}
Активних: {active_duels}

📈 <b>Активність:</b>
Повідомлень за день: {daily_messages}
Найактивніший час: {peak_hour}:00""",

    # Модерація
    'moderation_menu': """🛡️ <b>Панель модерації</b>

На розгляді: {pending_count} контенту

Оберіть дію:""",

    'content_approved': """✅ <b>Контент схвалено!</b>

Автор отримав +{points} балів.""",

    'content_rejected': """❌ <b>Контент відхилено</b>

Причина: {reason}""",

    # Помилки системи
    'system_error': """🔧 <b>Технічна помилка</b>

Вибачте за незручності. Спробуйте пізніше.""",

    'maintenance_mode': """🔧 <b>Технічне обслуговування</b>

Бот тимчасово недоступний.
Очікується відновлення незабаром."""
}

# Назви рангів
RANKS = [
    {"name": "🤡 Новачок", "min_points": 0},
    {"name": "😄 Сміхун", "min_points": 50},
    {"name": "😂 Гуморист", "min_points": 150},
    {"name": "🎭 Комік", "min_points": 350},
    {"name": "👑 Майстер Рофлу", "min_points": 750},
    {"name": "🏆 Король Гумору", "min_points": 1500},
    {"name": "🌟 Легенда Мемів", "min_points": 3000},
    {"name": "🚀 Гумористичний Геній", "min_points": 5000}
]

def get_rank_by_points(points: int) -> str:
    """Отримання рангу по балах"""
    for i in range(len(RANKS) - 1, -1, -1):
        if points >= RANKS[i]["min_points"]:
            return RANKS[i]["name"]
    return RANKS[0]["name"]