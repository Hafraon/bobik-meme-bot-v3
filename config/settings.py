#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Професійна конфігурація україномовного бота з діагностикою 🧠😂🔥
"""

import os
import sys
from typing import Optional, Dict
from pathlib import Path

class Settings:
    """Професійний клас налаштувань бота з розширеною діагностикою"""
    
    def __init__(self):
        print("🔧 Ініціалізація налаштувань...")
        
        # Діагностика змінних середовища
        self._debug_environment()
        
        # Завантаження .env файлу якщо є
        self._load_dotenv()
        
        # ===============================
        # ОСНОВНІ НАЛАШТУВАННЯ
        # ===============================
        self.BOT_TOKEN = self._get_env_var("BOT_TOKEN", "", required=True)
        self.ADMIN_ID = self._get_env_int("ADMIN_ID", 0, required=True)
        
        # ===============================
        # КАНАЛ ТА ЧАТИ
        # ===============================
        self.CHANNEL_ID = self._get_env_var("CHANNEL_ID", "@BobikFun")
        
        # ===============================
        # БАЗА ДАНИХ
        # ===============================
        # Railway автоматично встановлює DATABASE_URL для PostgreSQL
        self.DATABASE_URL = self._get_env_var("DATABASE_URL", "sqlite:///ukrainian_bot.db")
        
        # ===============================
        # AI ГЕНЕРАЦІЯ
        # ===============================
        self.OPENAI_API_KEY = self._get_env_var("OPENAI_API_KEY")
        self.OPENAI_MODEL = self._get_env_var("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # ===============================
        # ГЕЙМІФІКАЦІЯ
        # ===============================
        self.POINTS_FOR_REACTION = self._get_env_int("POINTS_FOR_REACTION", 5)
        self.POINTS_FOR_SUBMISSION = self._get_env_int("POINTS_FOR_SUBMISSION", 10)
        self.POINTS_FOR_APPROVAL = self._get_env_int("POINTS_FOR_APPROVAL", 20)
        self.POINTS_FOR_TOP_JOKE = self._get_env_int("POINTS_FOR_TOP_JOKE", 50)
        
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
        self.DAILY_BROADCAST_HOUR = self._get_env_int("DAILY_BROADCAST_HOUR", 9)
        self.DAILY_BROADCAST_MINUTE = self._get_env_int("DAILY_BROADCAST_MINUTE", 0)
        
        # ===============================
        # ОБМЕЖЕННЯ КОНТЕНТУ
        # ===============================
        self.MAX_JOKE_LENGTH = self._get_env_int("MAX_JOKE_LENGTH", 1000)
        self.MAX_MEME_CAPTION_LENGTH = self._get_env_int("MAX_MEME_CAPTION_LENGTH", 200)
        self.MAX_PENDING_SUBMISSIONS = self._get_env_int("MAX_PENDING_SUBMISSIONS", 100)
        
        # ===============================
        # ДУЕЛІ
        # ===============================
        self.DUEL_VOTING_TIME = self._get_env_int("DUEL_VOTING_TIME", 300)  # 5 хвилин
        self.MIN_VOTES_FOR_DUEL = self._get_env_int("MIN_VOTES_FOR_DUEL", 3)
        
        # ===============================
        # СИСТЕМНІ НАЛАШТУВАННЯ
        # ===============================
        self.DEBUG = self._get_env_bool("DEBUG", False)
        self.LOG_LEVEL = self._get_env_var("LOG_LEVEL", "INFO")
        self.TIMEZONE = self._get_env_var("TIMEZONE", "Europe/Kiev")
        
        # ===============================
        # БЕЗПЕКА ТА АНТИ-СПАМ
        # ===============================
        self.RATE_LIMIT_MESSAGES = self._get_env_int("RATE_LIMIT_MESSAGES", 3)
        self.RATE_LIMIT_CALLBACKS = self._get_env_int("RATE_LIMIT_CALLBACKS", 5)
        
        # ===============================
        # WEBHOOK НАЛАШТУВАННЯ (для майбутнього)
        # ===============================
        self.WEBHOOK_URL = self._get_env_var("WEBHOOK_URL")
        self.WEBHOOK_PATH = self._get_env_var("WEBHOOK_PATH", "/webhook")
        self.WEBAPP_HOST = self._get_env_var("WEBAPP_HOST", "0.0.0.0")
        self.WEBAPP_PORT = self._get_env_int("PORT", 8080)  # Railway використовує PORT
        
        # Валідація налаштувань
        self._validate()
        
        # Виведення статусу
        self._print_status()
    
    def _debug_environment(self):
        """Діагностика змінних середовища"""
        print("🔍 ДІАГНОСТИКА ЗМІННИХ СЕРЕДОВИЩА:")
        
        # Важливі змінні для перевірки
        important_vars = [
            "BOT_TOKEN", "ADMIN_ID", "DATABASE_URL", "OPENAI_API_KEY", 
            "CHANNEL_ID", "PORT", "RAILWAY_ENVIRONMENT"
        ]
        
        for var in important_vars:
            value = os.getenv(var)
            if value:
                # Маскуємо секретні дані
                if any(secret in var.upper() for secret in ["TOKEN", "KEY", "PASSWORD"]):
                    masked_value = value[:10] + "..." + value[-5:] if len(value) > 15 else value[:5] + "..."
                    print(f"  ✅ {var}: {masked_value}")
                else:
                    print(f"  ✅ {var}: {value}")
            else:
                print(f"  ❌ {var}: НЕ ВСТАНОВЛЕНО")
        
        # Перевірка середовища Railway
        if os.getenv("RAILWAY_ENVIRONMENT"):
            print(f"  🚂 Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT')}")
        
        print()
    
    def _load_dotenv(self):
        """Завантаження .env файлу якщо є"""
        try:
            from dotenv import load_dotenv
            
            # Пошук .env файлу
            env_path = Path(".env")
            if env_path.exists():
                load_dotenv(env_path)
                print(f"📁 Завантажено .env файл: {env_path.absolute()}")
            else:
                print("📁 .env файл не знайдено (використовуємо системні змінні)")
        except ImportError:
            print("⚠️ python-dotenv не встановлено, використовуємо системні змінні")
    
    def _get_env_var(self, key: str, default: str = "", required: bool = False) -> str:
        """Отримання змінної середовища з перевіркою"""
        value = os.getenv(key, default)
        
        if required and not value:
            print(f"❌ КРИТИЧНА ПОМИЛКА: Змінна {key} обов'язкова але не встановлена!")
            print(f"   Встановіть змінну {key} в Railway або в .env файлі")
            # Не кидаємо винятку тут, залишаємо для _validate()
        
        return value
    
    def _get_env_int(self, key: str, default: int, required: bool = False) -> int:
        """Отримання числової змінної середовища"""
        value = os.getenv(key)
        
        if value:
            try:
                return int(value)
            except ValueError:
                print(f"⚠️ Некоректне значення для {key}: {value}, використовуємо {default}")
                return default
        else:
            if required and not value:
                print(f"❌ КРИТИЧНА ПОМИЛКА: Змінна {key} обов'язкова але не встановлена!")
            return default
    
    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Отримання булевої змінної середовища"""
        value = os.getenv(key, "").lower()
        return value in ("true", "1", "yes", "on") if value else default
    
    def _validate(self):
        """Валідація критично важливих налаштувань"""
        print("✅ Валідація налаштувань...")
        
        errors = []
        
        if not self.BOT_TOKEN:
            errors.append("BOT_TOKEN не може бути порожнім!")
        elif not self.BOT_TOKEN.count(":") == 1:
            errors.append("BOT_TOKEN має неправильний формат (потрібно: число:токен)")
        
        if not self.ADMIN_ID:
            errors.append("ADMIN_ID не може бути 0!")
        elif self.ADMIN_ID < 0:
            errors.append("ADMIN_ID має бути позитивним числом!")
        
        if errors:
            print("\n🚨 КРИТИЧНІ ПОМИЛКИ КОНФІГУРАЦІЇ:")
            for error in errors:
                print(f"   ❌ {error}")
            print("\n📝 Для виправлення:")
            print("   1. Перевірте змінні середовища в Railway:")
            print("      - BOT_TOKEN: отримайте у @BotFather")
            print("      - ADMIN_ID: ваш Telegram ID від @userinfobot")
            print("   2. Або створіть .env файл локально")
            print()
            raise ValueError("Критичні помилки в конфігурації бота!")
    
    def _print_status(self):
        """Виведення статусу налаштувань"""
        print("🎯 СТАТУС НАЛАШТУВАНЬ:")
        print(f"  🤖 Бот: {self.BOT_TOKEN[:10]}...{self.BOT_TOKEN[-5:]}")
        print(f"  👤 Адмін: {self.ADMIN_ID}")
        print(f"  📺 Канал: {self.CHANNEL_ID}")
        
        # Database
        if "postgresql" in self.DATABASE_URL.lower():
            print(f"  💾 База даних: PostgreSQL (Railway)")
        elif "sqlite" in self.DATABASE_URL.lower():
            print(f"  💾 База даних: SQLite (локально)")
        else:
            print(f"  💾 База даних: {self.DATABASE_URL[:30]}...")
        
        # AI
        if self.OPENAI_API_KEY:
            print(f"  🧠 AI: Активний ({self.OPENAI_MODEL})")
        else:
            print(f"  🧠 AI: Вимкнений")
        
        # Environment
        if os.getenv("RAILWAY_ENVIRONMENT"):
            print(f"  🌍 Середовище: Railway ({os.getenv('RAILWAY_ENVIRONMENT')})")
        else:
            print(f"  🌍 Середовище: Локальне")
        
        print(f"  🔧 Debug режим: {'Увімкнений' if self.DEBUG else 'Вимкнений'}")
        print()

# Створення глобального екземпляру налаштувань
try:
    settings = Settings()
except Exception as e:
    print(f"\n💥 ФАТАЛЬНА ПОМИЛКА ІНІЦІАЛІЗАЦІЇ: {e}")
    print("\n🔧 РЕКОМЕНДАЦІЇ ПО ВИПРАВЛЕННЮ:")
    print("1. Перевірте змінні середовища в Railway Dashboard")
    print("2. Перевірте формат BOT_TOKEN (має містити ':')")
    print("3. Перевірте що ADMIN_ID є числом")
    print("4. Передеплойте проект після змін")
    sys.exit(1)

# ===============================
# ЕМОДЗІ ДЛЯ ІНТЕРФЕЙСУ
# ===============================
EMOJI = {
    "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐",
    "trophy": "🏆", "crown": "👑", "rocket": "🚀", "heart": "❤️",
    "like": "👍", "dislike": "👎", "thinking": "🤔", "cool": "😎",
    "wink": "😉", "party": "🎉", "boom": "💥", "check": "✅",
    "cross": "❌", "warning": "⚠️", "info": "ℹ️", "new": "🆕",
    "top": "🔝", "vs": "⚔️", "time": "⏰", "calendar": "📅",
    "stats": "📊", "profile": "👤", "settings": "⚙️", "help": "❓",
    "money": "💰", "gift": "🎁", "link": "🔗", "shield": "🛡️",
    "gem": "💎", "magic": "✨", "target": "🎯", "pin": "📍"
}

# ===============================
# ПРОФЕСІЙНІ ТЕКСТИ ІНТЕРФЕЙСУ
# ===============================
TEXTS = {
    "start": (
        f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю в україномовному боті мемів та анекдотів!</b>\n\n"
        f"{EMOJI['magic']} <b>Що я вмію:</b>\n"
        f"{EMOJI['laugh']} /meme - випадковий мем з колекції\n"
        f"{EMOJI['brain']} /anekdot - свіжий український анекдот\n" 
        f"{EMOJI['fire']} /submit - надіслати свій жарт на модерацію\n"
        f"{EMOJI['calendar']} /daily - підписка на щоденну розсилку\n"
        f"{EMOJI['profile']} /profile - твій ігровий профіль\n"
        f"{EMOJI['top']} /top - таблиця лідерів гумору\n"
        f"{EMOJI['vs']} /duel - епічна дуель жартів\n"
        f"{EMOJI['help']} /help - повна довідка функцій\n\n"
        f"{EMOJI['party']} <b>Заробляй бали, підвищуй ранг і ставай легендою українського гумору!</b>\n"
        f"{EMOJI['target']} <b>Канал:</b> {settings.CHANNEL_ID}"
    ),
    
    "help": (
        f"{EMOJI['help']} <b>ПОВНА ДОВІДКА УКРАЇНОМОВНОГО БОТА</b> {EMOJI['help']}\n\n"
        f"{EMOJI['brain']} <b>КОНТЕНТ:</b>\n"
        f"• /meme - отримати випадковий мем з бази\n"
        f"• /anekdot - отримати свіжий український анекдот\n"
        f"• /submit - надіслати свій мем або анекдот\n"
        f"• /daily - щоденна розсилка найкращого контенту\n\n"
        f"{EMOJI['fire']} <b>ГЕЙМІФІКАЦІЯ:</b>\n"
        f"• /profile - детальний профіль з статистикою\n"
        f"• /top - рейтинг найкращих гумористів\n"
        f"• /duel - змагання між двома жартами\n\n"
        f"{EMOJI['star']} <b>СИСТЕМА БАЛІВ:</b>\n"
        f"• +{settings.POINTS_FOR_REACTION} балів - за реакцію на контент\n"
        f"• +{settings.POINTS_FOR_SUBMISSION} балів - за надісланий жарт\n"
        f"• +{settings.POINTS_FOR_APPROVAL} балів - за схвалений жарт\n"
        f"• +{settings.POINTS_FOR_TOP_JOKE} балів - за хіт тижня\n\n"
        f"{EMOJI['crown']} <b>РАНГИ:</b> Новачок → Сміхун → Гуморист → Комік → Мастер Рофлу → Король Гумору → Легенда Мемів → Геній\n\n"
        f"{EMOJI['rocket']} <b>Підтримка:</b> зв'язок з адміном через бота\n"
        f"{EMOJI['heart']} <b>Дякуємо що робите україномовний інтернет смішнішим!</b>"
    ),
    
    "no_content": (
        f"{EMOJI['thinking']} <b>Упс! Контент тимчасово закінчився</b>\n\n"
        f"{EMOJI['magic']} Але ти можеш:\n"
        f"• Надіслати свій жарт через /submit\n"
        f"• Спробувати через кілька хвилин\n"
        f"• Переглянути свій профіль /profile"
    ),
    
    "submission_received": (
        f"{EMOJI['check']} <b>Дякую за твій жарт!</b>\n\n"
        f"{EMOJI['magic']} Твоя заявка №{{}}_ID відправлена на модерацію\n"
        f"{EMOJI['fire']} Ти отримав +{settings.POINTS_FOR_SUBMISSION} балів за активність\n"
        f"{EMOJI['time']} Очікуй результат протягом 24 годин\n"
        f"{EMOJI['info']} Модератори перевірять відповідність правилам"
    ),
    
    "submission_approved": (
        f"{EMOJI['party']} <b>ВІТАЄМО! Твій жарт схвалено!</b>\n\n"
        f"{EMOJI['star']} Твоя творчість додана до бази та доступна всім\n"
        f"{EMOJI['fire']} Ти отримав додатково +{settings.POINTS_FOR_APPROVAL} балів\n"
        f"{EMOJI['rocket']} Продовжуй ділитися гумором - ти талановитий!"
    ),
    
    "submission_rejected": (
        f"{EMOJI['cross']} <b>Твій жарт не пройшов модерацію</b>\n\n"
        f"{EMOJI['thinking']} Можливі причини:\n"
        f"• Не відповідає правилам спільноти\n"
        f"• Вже є в нашій базі\n"
        f"• Потребує доопрацювання\n\n"
        f"{EMOJI['heart']} Не засмучуйся! Спробуй надіслати інший жарт"
    ),
    
    "daily_enabled": (
        f"{EMOJI['check']} <b>Щоденну розсилку увімкнено!</b>\n\n"
        f"{EMOJI['calendar']} Щодня о {settings.DAILY_BROADCAST_HOUR}:00 по київському часу отримуватимеш:\n"
        f"• {EMOJI['brain']} Найкращий анекдот дня\n"
        f"• {EMOJI['laugh']} Топовий мем з високим рейтингом\n"
        f"• {EMOJI['fire']} Мотиваційне повідомлення\n"
        f"• {EMOJI['stats']} Цікаву статистику\n\n"
        f"{EMOJI['star']} Бонус: +2 бали за щоденну активність!"
    ),
    
    "daily_disabled": (
        f"{EMOJI['cross']} <b>Щоденну розсилку вимкнено</b>\n\n"
        f"{EMOJI['thinking']} Ти завжди можеш:\n"
        f"• Увімкнути знову командою /daily\n"
        f"• Отримувати контент вручну /meme /anekdot\n"
        f"• Слідкувати за каналом {settings.CHANNEL_ID}"
    ),
    
    "rate_limit": (
        f"{EMOJI['warning']} <b>Забагато запитів!</b>\n\n"
        f"{EMOJI['time']} Зачекай трохи перед наступною командою\n"
        f"{EMOJI['thinking']} Це захист від спаму для комфорту всіх користувачів"
    ),
    
    "premium_info": (
        f"{EMOJI['gem']} <b>ПРЕМІУМ ПІДПИСКА 'ЗОЛОТИЙ ГУМОРИСТ'</b>\n\n"
        f"{EMOJI['star']} <b>Ексклюзивні переваги:</b>\n"
        f"• Доступ до преміум мемів та анекдотів\n"
        f"• Пріоритет у дуелях та голосуванні\n" 
        f"• Подвійні бали за всі дії\n"
        f"• Персональні рекомендації AI\n"
        f"• Спеціальний значок у профілі\n"
        f"• Безлімітні команди\n\n"
        f"{EMOJI['money']} <b>Вартість:</b> $2.99/місяць\n"
        f"{EMOJI['gift']} <b>Перший тиждень безкоштовно!</b>\n\n"
        f"{EMOJI['info']} Для підключення зв'яжіться з адміністратором"
    ),
    
    "support_info": (
        f"{EMOJI['heart']} <b>ПІДТРИМКА УКРАЇНОМОВНОГО ГУМОРУ</b>\n\n"
        f"{EMOJI['target']} <b>Допоможи розвитку проекту:</b>\n\n"
        f"{EMOJI['money']} <b>Monobank:</b> <code>5375 4141 xxxx xxxx</code>\n"
        f"{EMOJI['money']} <b>PrivatBank:</b> <code>5168 7554 xxxx xxxx</code>\n"
        f"{EMOJI['link']} <b>PayPal:</b> donate@ukrainian-humor.com\n"
        f"{EMOJI['rocket']} <b>USDT TRC20:</b> <code>TxxxXXXxxxXXX</code>\n\n"
        f"{EMOJI['gift']} <b>Донати $5+:</b> Спеціальний ранг 'Меценат Гумору'\n"
        f"{EMOJI['star']} <b>Донати $25+:</b> Безлімітний доступ на рік\n"
        f"{EMOJI['crown']} <b>Донати $100+:</b> Персональна подяка та ранг 'Легенда'"
    )
}

# ===============================
# РОЗУМНІ КОНТЕКСТНІ ПРИВІТАННЯ
# ===============================  
TIME_GREETINGS = {
    "morning": [
        f"{EMOJI['fire']} Доброго ранку! Заряджайся гумором на день!", 
        f"{EMOJI['brain']} Ранковий boost настрою готовий!",
        f"{EMOJI['star']} Гарного ранку! Час для сміху!"
    ],
    "day": [
        f"{EMOJI['laugh']} Гарного дня! Ідеальний час для мему!", 
        f"{EMOJI['star']} Денна порція гумору подається!",
        f"{EMOJI['fire']} Привіт! Розвантажуємо робочий день!"
    ], 
    "evening": [
        f"{EMOJI['cool']} Доброго вечора! Релакс з гумором!", 
        f"{EMOJI['party']} Вечірня розрядка після важкого дня!",
        f"{EMOJI['wink']} Добрий вечір! Час посміятися!"
    ],
    "night": [
        f"{EMOJI['wink']} Доброї ночі! Солодкі сни з усмішкою!", 
        f"{EMOJI['thinking']} Нічний жарт для гарного сну!",
        f"{EMOJI['star']} Останній сміх перед сном!"
    ]
}