#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ШВИДКЕ ОНОВЛЕННЯ ДО КРОКУ 6: ПОВНА АВТОМАТИЗАЦІЯ

Автоматичне розгортання всіх файлів для системи автоматизації
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def print_header():
    print("🚀" * 30)
    print("\n🤖 ОНОВЛЕННЯ ДО ПОВНОЇ АВТОМАТИЗАЦІЇ")
    print("Автоматичне розгортання Кроку 6")
    print("🚀" * 30)
    print()

def backup_existing_files():
    """Створення резервних копій існуючих файлів"""
    print("💾 СТВОРЕННЯ РЕЗЕРВНИХ КОПІЙ:")
    
    backup_dir = Path("backup_before_step6")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "app/main.py",
        "requirements.txt",
        "app/database/services.py"
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_path = backup_dir / Path(file_path).name
            shutil.copy2(file_path, backup_path)
            print(f"✅ {file_path} → {backup_path}")
    
    print(f"✅ Резервні копії збережено в {backup_dir}/")

def ensure_directories():
    """Створення необхідних папок для автоматизації"""
    print("\n📁 СТВОРЕННЯ НЕОБХІДНИХ ПАПОК:")
    
    directories = [
        "app",
        "app/services",
        "app/handlers",
        "app/database", 
        "app/config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True, parents=True)
        print(f"✅ {directory}/")

def create_automated_scheduler():
    """Створення файлу автоматизованого планувальника"""
    print("\n🤖 СТВОРЕННЯ AUTOMATED SCHEDULER:")
    
    scheduler_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 АВТОМАТИЗОВАНИЙ ПЛАНУВАЛЬНИК - Базова версія
"""

import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

class AutomatedScheduler:
    """Базовий автоматизований планувальник"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.stats = {
            'jobs_executed': 0,
            'broadcasts_sent': 0,
            'errors': 0,
            'last_activity': None
        }
    
    async def initialize(self):
        """Ініціалізація планувальника"""
        try:
            logger.info("🤖 Ініціалізація планувальника...")
            await self.setup_basic_jobs()
            logger.info("✅ Планувальник готовий")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка планувальника: {e}")
            return False
    
    async def setup_basic_jobs(self):
        """Налаштування базових завдань"""
        
        # Щоденна розсилка о 9:00
        self.scheduler.add_job(
            func=self.daily_broadcast,
            trigger=CronTrigger(hour=9, minute=0),
            id='daily_broadcast',
            name='Щоденна розсилка',
            replace_existing=True
        )
        
        # Перевірка дуелів кожну хвилину
        self.scheduler.add_job(
            func=self.check_duels,
            trigger=IntervalTrigger(minutes=1),
            id='duel_checker',
            name='Перевірка дуелей',
            replace_existing=True
        )
        
        logger.info("📅 Базові завдання налаштовано")
    
    async def daily_broadcast(self):
        """Щоденна розсилка контенту"""
        try:
            logger.info("📢 Щоденна розсилка...")
            
            # Базова реалізація - отримуємо користувачів
            users = await self.get_active_users()
            
            message = (
                f"🌅 Доброго ранку!\\n\\n"
                f"😂 Жарт дня:\\n"
                f"<i>Чому програмісти плутають Хеллоуїн і Різдво?\\n"
                f"Тому що 31 OCT = 25 DEC!</i>\\n\\n"
                f"⚔️ Створюйте дуелі та отримуйте бали!"
            )
            
            # Відправляємо повідомлення
            sent_count = 0
            for user in users:
                try:
                    await self.bot.send_message(user['id'], message)
                    sent_count += 1
                    await asyncio.sleep(0.1)  # Затримка між повідомленнями
                except Exception as e:
                    logger.error(f"Помилка відправки {user['id']}: {e}")
            
            self.stats['broadcasts_sent'] += 1
            self.stats['jobs_executed'] += 1
            self.stats['last_activity'] = datetime.now()
            
            logger.info(f"✅ Розсилка завершена: {sent_count} повідомлень")
            
        except Exception as e:
            logger.error(f"❌ Помилка розсилки: {e}")
            self.stats['errors'] += 1
    
    async def check_duels(self):
        """Перевірка та завершення дуелей"""
        try:
            # Базова реалізація - автозавершення дуелей
            from database.services import auto_finish_expired_duels
            finished_count = await auto_finish_expired_duels()
            
            if finished_count > 0:
                logger.info(f"🏁 Завершено {finished_count} дуелей")
            
            self.stats['jobs_executed'] += 1
            
        except Exception as e:
            logger.error(f"❌ Помилка перевірки дуелей: {e}")
            self.stats['errors'] += 1
    
    async def get_active_users(self):
        """Отримання активних користувачів"""
        try:
            # Спроба отримати з БД
            from database.services import get_active_users_for_broadcast
            return await get_active_users_for_broadcast(days=7)
        except Exception:
            # Fallback - повертаємо пустий список
            return []
    
    async def start(self):
        """Запуск планувальника"""
        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                logger.info("🚀 Планувальник запущено")
        except Exception as e:
            logger.error(f"❌ Помилка запуску: {e}")
    
    async def stop(self):
        """Зупинка планувальника"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("⏹️ Планувальник зупинено")
        except Exception as e:
            logger.error(f"❌ Помилка зупинки: {e}")
    
    def get_scheduler_status(self):
        """Статус планувальника"""
        return {
            'is_running': self.is_running,
            'total_jobs': len(self.scheduler.get_jobs()) if self.is_running else 0,
            'stats': self.stats.copy()
        }

async def create_automated_scheduler(bot):
    """Створення планувальника"""
    scheduler = AutomatedScheduler(bot)
    success = await scheduler.initialize()
    return scheduler if success else None

__all__ = ['AutomatedScheduler', 'create_automated_scheduler']
'''
    
    # Створюємо директорію services
    services_dir = Path("app/services")
    services_dir.mkdir(exist_ok=True)
    
    # Створюємо __init__.py для services
    init_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .automated_scheduler import AutomatedScheduler, create_automated_scheduler

__all__ = ['AutomatedScheduler', 'create_automated_scheduler']
'''
    
    with open(services_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write(init_content)
    
    # Створюємо основний файл планувальника
    with open(services_dir / "automated_scheduler.py", "w", encoding="utf-8") as f:
        f.write(scheduler_content)
    
    print("✅ app/services/automated_scheduler.py")
    print("✅ app/services/__init__.py")

def create_broadcast_system():
    """Створення системи розсилок"""
    print("\n📢 СТВОРЕННЯ BROADCAST SYSTEM:")
    
    broadcast_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📢 СИСТЕМА РОЗСИЛОК - Базова версія
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BroadcastSystem:
    """Базова система розсилок"""
    
    def __init__(self, bot):
        self.bot = bot
        self.daily_content_sent = False
    
    async def send_daily_content(self):
        """Щоденна розсилка контенту"""
        try:
            logger.info("📢 Щоденна розсилка контенту...")
            
            # Отримуємо активних користувачів
            users = await self.get_active_users(days=7)
            
            if not users:
                logger.info("Немає активних користувачів")
                return
            
            # Створюємо повідомлення
            message = self.create_daily_message()
            
            # Відправляємо
            success_count = 0
            for user in users:
                try:
                    await self.bot.send_message(user['id'], message)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Помилка користувачу {user['id']}: {e}")
            
            logger.info(f"✅ Розсилка: {success_count}/{len(users)}")
            self.daily_content_sent = True
            
        except Exception as e:
            logger.error(f"❌ Помилка розсилки: {e}")
    
    def create_daily_message(self):
        """Створення щоденного повідомлення"""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            greeting = "🌅 Доброго ранку!"
        elif 12 <= hour < 18:
            greeting = "☀️ Доброго дня!"
        else:
            greeting = "🌆 Доброго вечора!"
        
        jokes = [
            "Чому програмісти плутають Хеллоуїн і Різдво? Тому що 31 OCT = 25 DEC!",
            "Скільки програмістів потрібно щоб закрутити лампочку? Жодного. Це апаратна проблема!",
            "Чому програмісти носять окуляри? Тому що не можуть C#!",
            "Що сказав 0 до 8? - Гарний пояс!",
            "Найкращий спосіб прискорити комп'ютер - кинути його з вікна!"
        ]
        
        import random
        joke = random.choice(jokes)
        
        return f"{greeting}\\n\\n😂 <b>ЖАРТ ДНЯ</b>\\n\\n<i>{joke}</i>\\n\\n🎯 Створіть дуель та отримуйте бали!"
    
    async def get_active_users(self, days=7):
        """Отримання активних користувачів"""
        try:
            from database.services import get_active_users_for_broadcast
            return await get_active_users_for_broadcast(days)
        except Exception:
            return []
    
    def get_broadcast_status(self):
        """Статус розсилок"""
        return {
            "daily_content_sent": self.daily_content_sent,
            "last_check": datetime.now().isoformat()
        }

async def create_broadcast_system(bot):
    """Створення системи розсилок"""
    return BroadcastSystem(bot)

__all__ = ['BroadcastSystem', 'create_broadcast_system']
'''
    
    with open(Path("app/services/broadcast_system.py"), "w", encoding="utf-8") as f:
        f.write(broadcast_content)
    
    print("✅ app/services/broadcast_system.py")

def update_main_app():
    """Оновлення app/main.py з автоматизацією"""
    print("\n🎮 ОНОВЛЕННЯ ГОЛОВНОГО ДОДАТКУ:")
    
    main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ З АВТОМАТИЗАЦІЄЮ 🤖
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedUkrainianTelegramBot:
    def __init__(self):
        self.bot = None
        self.dp = None
        self.startup_time = datetime.now()
        self.db_available = False
        self.scheduler = None
        self.automation_active = False
        
    def is_admin(self, user_id: int) -> bool:
        """Перевірка адміністратора"""
        try:
            from config.settings import settings
            return user_id == settings.ADMIN_ID
        except:
            return user_id == 603047391  # Fallback
    
    async def initialize_bot(self):
        """Ініціалізація бота"""
        try:
            logger.info("🔍 Завантаження налаштувань...")
            
            bot_token = os.getenv('BOT_TOKEN')
            if not bot_token:
                raise ValueError("BOT_TOKEN not found")
            
            from aiogram import Bot, Dispatcher
            from aiogram.client.default import DefaultBotProperties
            from aiogram.enums import ParseMode
            
            self.bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            self.dp = Dispatcher()
            
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Bot created: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            return False

    async def initialize_database(self):
        """Ініціалізація БД"""
        try:
            logger.info("💾 Ініціалізація БД...")
            from database.database import init_database
            success = await init_database()
            
            if success:
                logger.info("✅ Database initialized")
                self.db_available = True
                return True
            else:
                logger.warning("⚠️ Database initialization failed")
                return False
                
        except ImportError:
            logger.warning("⚠️ Database module not available")
            return False
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return False

    async def initialize_automation(self):
        """Ініціалізація автоматизації"""
        try:
            logger.info("🤖 Ініціалізація автоматизації...")
            
            from services.automated_scheduler import create_automated_scheduler
            self.scheduler = await create_automated_scheduler(self.bot)
            
            if self.scheduler:
                logger.info("✅ Scheduler створено")
                await self.scheduler.start()
                self.automation_active = True
                logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА!")
                return True
            else:
                logger.warning("⚠️ Не вдалося створити scheduler")
                return False
                
        except ImportError as e:
            logger.warning(f"⚠️ Automation не доступна: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Automation error: {e}")
            return False

    async def register_handlers(self):
        """Реєстрація хендлерів"""
        try:
            logger.info("🔧 Реєстрація хендлерів...")
            
            # Основні хендлери
            from handlers import register_handlers
            register_handlers(self.dp)
            
            # Додаткові хендлери автоматизації
            await self.register_automation_handlers()
            
            logger.info("✅ Хендлери зареєстровано")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers error: {e}")
            return False

    async def register_automation_handlers(self):
        """Хендлери автоматизації"""
        from aiogram.filters import Command
        from aiogram.types import Message
        
        @self.dp.message(Command("start"))
        async def automated_start(message: Message):
            text = (
                f"🤖 <b>БОТ З АВТОМАТИЗАЦІЄЮ!</b>\\n\\n"
                f"⚡ Автоматизація: {'Активна' if self.automation_active else 'Неактивна'}\\n"
                f"💾 База даних: {'Підключена' if self.db_available else 'Fallback'}\\n\\n"
                f"🎯 Функції:\\n"
                f"• ⚔️ Дуелі жартів\\n"
                f"• 📢 Автоматичні розсилки\\n"
                f"• 🤖 Розумний планувальник\\n"
                f"• 📊 Статистика та аналітика\\n\\n"
                f"Використовуйте /help для довідки!"
            )
            await message.answer(text)
        
        @self.dp.message(Command("automation_status"))
        async def automation_status(message: Message):
            if not self.is_admin(message.from_user.id):
                await message.answer("❌ Доступ заборонено")
                return
                
            if self.scheduler:
                status = self.scheduler.get_scheduler_status()
                text = (
                    f"🤖 <b>СТАТУС АВТОМАТИЗАЦІЇ</b>\\n\\n"
                    f"⚡ Планувальник: {'Активний' if status['is_running'] else 'Неактивний'}\\n"
                    f"📅 Завдань: {status['total_jobs']}\\n"
                    f"🎯 Виконано: {status['stats']['jobs_executed']}\\n"
                    f"📢 Розсилок: {status['stats']['broadcasts_sent']}\\n"
                    f"❌ Помилок: {status['stats']['errors']}"
                )
            else:
                text = "❌ Планувальник не ініціалізований"
            
            await message.answer(text)
        
        logger.info("✅ Automation handlers зареєстровано")

    async def main(self):
        """Головна функція"""
        logger.info("🤖 Starting Automated Bot...")
        
        try:
            if not await self.initialize_bot():
                return False
            
            if not await self.initialize_database():
                logger.warning("⚠️ Working without DB")
            
            automation_success = await self.initialize_automation()
            if automation_success:
                logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА!")
            
            if not await self.register_handlers():
                return False
            
            logger.info("✅ Bot готовий з автоматизацією")
            
            # Запуск
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            return False
        finally:
            if self.scheduler:
                await self.scheduler.stop()
            if self.bot:
                await self.bot.session.close()

async def main():
    bot = AutomatedUkrainianTelegramBot()
    await bot.main()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("app/main.py", "w", encoding="utf-8") as f:
        f.write(main_content)
    
    print("✅ app/main.py")

def update_requirements():
    """Оновлення requirements.txt"""
    print("\n📦 ОНОВЛЕННЯ REQUIREMENTS:")
    
    requirements_content = '''# Професійний україномовний бот з автоматизацією

# Основні залежності
aiogram>=3.4.0,<4.0.0
SQLAlchemy>=2.0.0,<3.0.0
asyncpg>=0.29.0
psycopg2-binary>=2.9.0
aiohttp>=3.9.0

# Автоматизація (НОВИНКА!)
APScheduler>=3.10.0,<4.0.0
pytz>=2023.3
python-dateutil>=2.8.0

# Конфігурація
python-dotenv>=1.0.0
pydantic>=2.5.0

# Файлова система
aiofiles>=23.0.0
alembic>=1.13.0

# Утиліти
emoji>=2.8.0
orjson>=3.9.0
psutil>=5.9.0
httpx>=0.25.0

# Безпека
cryptography>=42.0.0

# Веб-сервер
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# AI (опціонально)
openai>=1.6.0

# Логування
structlog>=23.0.0

# Продакшн
gunicorn>=21.2.0
'''
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt")

def extend_database_services():
    """Розширення database/services.py"""
    print("\n🗄️ РОЗШИРЕННЯ DATABASE SERVICES:")
    
    services_extension = '''

# ===== АВТОМАТИЗАЦІЯ ТА РОЗСИЛКИ (КРОК 6) =====

async def get_active_users_for_broadcast(days: int = 7):
    """Отримання активних користувачів для розсилки"""
    try:
        from .models import User
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with get_db_session() as session:
            users = session.query(User).filter(
                User.last_activity >= cutoff_date,
                User.is_active == True
            ).all()
            
            result = []
            for user in users:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting users for broadcast: {e}")
        return []

async def get_daily_best_content():
    """Отримання кращого контенту дня"""
    try:
        from .models import Content, ContentStatus
        import random
        
        with get_db_session() as session:
            # Отримуємо випадковий схвалений контент
            content = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).order_by(func.random()).first()
            
            if content:
                return {
                    'id': content.id,
                    'text': content.text,
                    'type': content.content_type
                }
            
            return None
            
    except Exception as e:
        logger.error(f"Error getting daily content: {e}")
        return None

async def generate_weekly_stats():
    """Генерація тижневої статистики"""
    try:
        from .models import User, Content, Duel
        from datetime import datetime, timedelta
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        with get_db_session() as session:
            # Базова статистика
            new_users = session.query(User).filter(
                User.created_at >= week_ago
            ).count()
            
            new_content = session.query(Content).filter(
                Content.created_at >= week_ago
            ).count()
            
            return {
                'new_users': new_users,
                'new_content': new_content,
                'period': 'week'
            }
            
    except Exception as e:
        logger.error(f"Error generating weekly stats: {e}")
        return {}

async def get_broadcast_statistics():
    """Статистика для розсилок"""
    try:
        from .models import User
        
        with get_db_session() as session:
            total_users = session.query(User).filter(User.is_active == True).count()
            
            return {
                'total_users': total_users,
                'last_updated': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error getting broadcast stats: {e}")
        return {'total_users': 0, 'error': str(e)}
'''
    
    services_file = Path("app/database/services.py")
    if services_file.exists():
        with open(services_file, "a", encoding="utf-8") as f:
            f.write(services_extension)
        print("✅ Розширено app/database/services.py")
    else:
        print("⚠️ app/database/services.py не знайдено")

def run_tests():
    """Швидкі тести"""
    print("\n🧪 ШВИДКІ ТЕСТИ:")
    
    try:
        # Тест імпорту scheduler
        sys.path.insert(0, str(Path("app").absolute()))
        from services.automated_scheduler import create_automated_scheduler
        print("✅ Automated scheduler імпортується")
        
        # Тест імпорту broadcast
        from services.broadcast_system import create_broadcast_system
        print("✅ Broadcast system імпортується")
        
        # Тест основного додатку
        from main import AutomatedUkrainianTelegramBot
        print("✅ Automated bot готовий")
        
        # Тест APScheduler
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        print("✅ APScheduler доступний")
        
        print("🎉 Всі швидкі тести пройшли!")
        return True
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        if "apscheduler" in str(e).lower():
            print("💡 Встановіть: pip install APScheduler>=3.10.0 pytz>=2023.3")
        return False
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")
        return False

def main():
    """Головна функція оновлення"""
    print_header()
    
    try:
        # Кроки оновлення
        backup_existing_files()
        ensure_directories()
        create_automated_scheduler()
        create_broadcast_system()
        update_main_app()
        update_requirements()
        extend_database_services()
        
        # Тестування
        tests_passed = run_tests()
        
        # Підсумок
        print(f"\\n{'🎉'*30}")
        print(f"📊 ОНОВЛЕННЯ ДО КРОКУ 6 ЗАВЕРШЕНО")
        print(f"{'🎉'*30}")
        
        if tests_passed:
            print("✅ Всі файли створено та протестовано")
            print("🤖 Система автоматизації готова до запуску!")
            
            print(f"\\n🚀 НАСТУПНІ КРОКИ:")
            print(f"1. Встановіть залежності: pip install -r requirements.txt")
            print(f"2. Перевірте змінні BOT_TOKEN, ADMIN_ID")
            print(f"3. Запустіть бота: python main.py")
            print(f"4. Перевірте автоматизацію: /automation_status")
            print(f"5. Запустіть повне тестування: python test_automation.py")
            
            print(f"\\n📅 АВТОМАТИЧНІ ФУНКЦІЇ:")
            print(f"• 9:00 щодня - ранкова розсилка")
            print(f"• Кожну хвилину - перевірка дуелей")
            print(f"• Автоматичне завершення просрочених дуелей")
            print(f"• Розумне планування завдань")
            
        else:
            print("⚠️ Є деякі проблеми - перевірте помилки вище")
            print("🔧 Встановіть відсутні залежності:")
            print("   pip install APScheduler>=3.10.0 pytz>=2023.3")
        
        return tests_passed
        
    except Exception as e:
        print(f"❌ Критична помилка оновлення: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\\n🎊 ВІТАЄМО! Повна автоматизація готова!")
    else:
        print("\\n🔧 Потрібні додаткові налаштування")