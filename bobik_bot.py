#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Професійний україномовний Telegram-бот з мемами та анекдотами 🧠😂🔥
Версія: 2.0 Production
Автор: AI Assistant
Ліцензія: MIT
"""

import asyncio
import logging
import sys
import os
import signal
import traceback
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramNetworkError, TelegramBadRequest

# Додаємо поточну папку до Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Імпорти конфігурації
from config.settings import settings, EMOJI, TEXTS

# Імпорти компонентів
from database.database import init_db
from handlers import register_handlers
from middlewares.auth import AuthMiddleware, AntiSpamMiddleware, LoggingMiddleware
from services.scheduler import SchedulerService
from services.content_generator import auto_generate_content_if_needed

# Професійне налаштування логування
def setup_logging():
    """Налаштування професійного логування"""
    
    # Створення директорії логів
    os.makedirs('logs', exist_ok=True)
    
    # Форматування логів
    log_format = '%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Налаштування root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Файл для всіх логів
            logging.FileHandler('logs/bot.log', encoding='utf-8'),
            # Файл тільки для помилок
            logging.FileHandler('logs/errors.log', encoding='utf-8', mode='a'),
            # Консоль
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Налаштування логгера помилок
    error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Отключення сторонніх библиотек в debug режимі
    if not settings.DEBUG:
        logging.getLogger('aiogram').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)

# Ініціалізація логування
setup_logging()
logger = logging.getLogger(__name__)

class UkrainianTelegramBot:
    """Професійний клас україномовного Telegram-бота"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.scheduler_service: Optional[SchedulerService] = None
        self.is_running = False
        self.startup_time = datetime.now()
        
        # Обробка сигналів для корректного завершення
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обробка сигналів завершення"""
        logger.info(f"🛑 Отримано сигнал {signum}, завершуємо роботу...")
        self.is_running = False
    
    async def create_bot(self) -> Bot:
        """Створення та налаштування екземпляру бота"""
        try:
            logger.info("🤖 Ініціалізація Telegram бота...")
            
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            )
            
            # Перевірка з'єднання та отримання інформації про бота
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Бот успішно підключено: @{bot_info.username}")
            logger.info(f"   📋 Ім'я: {bot_info.first_name}")
            logger.info(f"   🆔 ID: {bot_info.id}")
            logger.info(f"   🔗 Посилання: https://t.me/{bot_info.username}")
            
            return self.bot
            
        except TelegramNetworkError as e:
            logger.error(f"❌ Помилка мережі Telegram: {e}")
            raise
        except TelegramBadRequest as e:
            logger.error(f"❌ Неправильний токен бота: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Критична помилка ініціалізації бота: {e}")
            raise
    
    async def setup_dispatcher(self):
        """Професійне налаштування диспетчера"""
        logger.info("📝 Налаштування диспетчера...")
        
        self.dp = Dispatcher()
        
        # Підключення middleware в правильному порядку
        middlewares = [
            AuthMiddleware(),
            AntiSpamMiddleware(rate_limit=settings.RATE_LIMIT_MESSAGES),
            LoggingMiddleware()
        ]
        
        for middleware in middlewares:
            self.dp.message.middleware(middleware)
            self.dp.callback_query.middleware(middleware)
        
        # Реєстрація всіх хендлерів
        register_handlers(self.dp)
        
        # Налаштування обробки помилок
        self.dp.error.register(self._global_error_handler)
        
        logger.info("✅ Диспетчер налаштовано з middleware та хендлерами")
    
    async def _global_error_handler(self, update, exception):
        """Глобальний обробник помилок"""
        logger.error(f"🚨 Необроблена помилка: {exception}")
        logger.error(f"📄 Update: {update}")
        logger.error(f"📊 Traceback: {traceback.format_exc()}")
        
        # Спроба повідомити адміністратора про критичну помилку
        try:
            if self.bot and hasattr(update, 'message') and update.message:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"🚨 <b>КРИТИЧНА ПОМИЛКА В БОТІ</b>\n\n"
                    f"<b>Помилка:</b> <code>{str(exception)[:500]}</code>\n"
                    f"<b>Час:</b> {datetime.now().strftime('%H:%M:%S')}\n"
                    f"<b>Користувач:</b> {update.message.from_user.id}"
                )
        except:
            pass  # Ігноруємо помилки повідомлення адміністратору
        
        return True  # Продовжуємо обробку
    
    async def setup_database(self):
        """Професійна ініціалізація бази даних"""
        try:
            logger.info("💾 Ініціалізація бази даних...")
            await init_db()
            
            # Перевірка з'єднання
            from database.database import get_db_session
            with get_db_session() as session:
                # Простий тест з'єднання
                result = session.execute("SELECT 1").scalar()
                if result == 1:
                    logger.info("✅ З'єднання з базою даних працює")
                else:
                    raise Exception("Тест з'єднання провалився")
                    
        except Exception as e:
            logger.error(f"❌ Критична помилка бази даних: {e}")
            raise
    
    async def setup_scheduler(self):
        """Налаштування розумного планувальника"""
        try:
            logger.info("⏰ Ініціалізація планувальника задач...")
            self.scheduler_service = SchedulerService(self.bot)
            await self.scheduler_service.start()
            
            logger.info("✅ Планувальник активний:")
            logger.info(f"   📅 Щоденна розсилка: {settings.DAILY_BROADCAST_HOUR}:00")
            logger.info(f"   ⚔️ Перевірка дуелей: кожні 5 хвилин")
            logger.info(f"   🧹 Очищення: щотижня")
            
        except Exception as e:
            logger.warning(f"⚠️ Планувальник недоступний: {e}")
            # Не критична помилка, продовжуємо без планувальника
    
    async def setup_ai_content(self):
        """Розумне налаштування AI генерації"""
        try:
            if settings.OPENAI_API_KEY:
                logger.info("🧠 Ініціалізація AI генератора контенту...")
                await auto_generate_content_if_needed()
                logger.info(f"✅ AI активний (модель: {settings.OPENAI_MODEL})")
            else:
                logger.info("⚠️ AI вимкнений: немає OpenAI API ключа")
                logger.info("   💡 Для увімкнення додайте OPENAI_API_KEY")
        except Exception as e:
            logger.warning(f"⚠️ AI недоступний: {e}")
    
    async def notify_admin_startup(self):
        """Повідомлення адміністратору про запуск"""
        try:
            startup_message = (
                f"{EMOJI['rocket']} <b>БОТ УСПІШНО ЗАПУЩЕНО!</b>\n\n"
                f"{EMOJI['time']} <b>Час запуску:</b> {self.startup_time.strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"{EMOJI['brain']} <b>AI:</b> {'✅ Активний' if settings.OPENAI_API_KEY else '❌ Вимкнений'}\n"
                f"{EMOJI['calendar']} <b>Планувальник:</b> {'✅ Активний' if self.scheduler_service else '❌ Вимкнений'}\n"
                f"{EMOJI['shield']} <b>База даних:</b> {'PostgreSQL' if 'postgresql' in settings.DATABASE_URL else 'SQLite'}\n"
                f"{EMOJI['target']} <b>Канал:</b> {settings.CHANNEL_ID}\n\n"
                f"{EMOJI['check']} <b>Всі системи готові до роботи!</b>\n"
                f"{EMOJI['fire']} <b>Слава Україні!</b> 🇺🇦"
            )
            
            await self.bot.send_message(settings.ADMIN_ID, startup_message)
            logger.info("📱 Повідомлення про запуск надіслано адміністратору")
            
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося повідомити адміністратора: {e}")
    
    async def start_polling(self):
        """Професійний запуск polling з обробкою помилок"""
        try:
            self.is_running = True
            
            # Статистика запуску
            logger.info("🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОТ ЗАПУЩЕНО")
            logger.info("=" * 50)
            logger.info(f"🌍 Середовище: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Локальне'}")
            logger.info(f"🇺🇦 Мова інтерфейсу: Українська")
            logger.info(f"👤 Адміністратор: {settings.ADMIN_ID}")
            logger.info(f"📺 Канал: {settings.CHANNEL_ID}")
            logger.info(f"🔧 Debug режим: {'Увімкнений' if settings.DEBUG else 'Вимкнений'}")
            logger.info("=" * 50)
            
            # Повідомлення адміністратору
            await self.notify_admin_startup()
            
            # Запуск polling з обробкою помилок
            while self.is_running:
                try:
                    logger.info("🔄 Запуск polling...")
                    await self.dp.start_polling(
                        self.bot,
                        allowed_updates=['message', 'callback_query', 'inline_query']
                    )
                except TelegramNetworkError as e:
                    logger.error(f"🌐 Помилка мережі: {e}")
                    logger.info("⏳ Повторне підключення через 10 секунд...")
                    await asyncio.sleep(10)
                except Exception as e:
                    logger.error(f"💥 Критична помилка polling: {e}")
                    if self.is_running:
                        logger.info("⏳ Перезапуск через 30 секунд...")
                        await asyncio.sleep(30)
                    else:
                        break
                        
        except KeyboardInterrupt:
            logger.info("⌨️ Отримано Ctrl+C")
        except Exception as e:
            logger.error(f"🚨 Критична помилка: {e}")
            raise
        finally:
            self.is_running = False
    
    async def shutdown(self):
        """Корректне завершення роботи з повідомленням адміністратору"""
        logger.info("🛑 Початок завершення роботи бота...")
        
        try:
            # Повідомлення адміністратору про зупинку
            if self.bot:
                try:
                    uptime = datetime.now() - self.startup_time
                    shutdown_message = (
                        f"{EMOJI['warning']} <b>БОТ ЗУПИНЕНО</b>\n\n"
                        f"{EMOJI['time']} <b>Час роботи:</b> {uptime}\n"
                        f"{EMOJI['calendar']} <b>Зупинено:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                        f"{EMOJI['info']} Для перезапуску зверніться до адміністратора"
                    )
                    await self.bot.send_message(settings.ADMIN_ID, shutdown_message)
                except:
                    pass
            
            # Зупинка планувальника
            if self.scheduler_service:
                await self.scheduler_service.stop()
                logger.info("⏰ Планувальник зупинено")
            
            # Закриття сесії бота
            if self.bot:
                await self.bot.session.close()
                logger.info("🤖 Сесія бота закрита")
            
            logger.info("✅ Бот коректно завершив роботу")
            
        except Exception as e:
            logger.error(f"❌ Помилка при завершенні: {e}")

async def main():
    """Головна функція запуску з професійною обробкою помилок"""
    
    # Красивий заголовок
    print("\n" + "🧠😂🔥" * 20)
    print("🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОТ v2.0 🚀")
    print("🇺🇦 ПРОФЕСІЙНА ВЕРСІЯ З ПОВНОЮ ФУНКЦІОНАЛЬНІСТЮ 🇺🇦")
    print("🧠😂🔥" * 20 + "\n")
    
    # Створення екземпляру бота
    ukrainian_bot = UkrainianTelegramBot()
    
    try:
        # Поетапна ініціалізація всіх компонентів
        logger.info("🔄 Початок ініціалізації компонентів...")
        
        await ukrainian_bot.create_bot()
        await ukrainian_bot.setup_database()
        await ukrainian_bot.setup_dispatcher()
        await ukrainian_bot.setup_scheduler()
        await ukrainian_bot.setup_ai_content()
        
        logger.info("✅ Всі компоненти ініціалізовано успішно")
        
        # Запуск основного циклу
        await ukrainian_bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("👋 Отримано сигнал завершення від користувача")
    except Exception as e:
        logger.error(f"💥 Критична помилка запуску: {e}")
        logger.error(f"📊 Детальний traceback:\n{traceback.format_exc()}")
        
        # Спроба повідомити адміністратора про помилку запуску
        if ukrainian_bot.bot:
            try:
                await ukrainian_bot.bot.send_message(
                    settings.ADMIN_ID,
                    f"🚨 <b>КРИТИЧНА ПОМИЛКА ЗАПУСКУ</b>\n\n"
                    f"<code>{str(e)[:500]}</code>\n\n"
                    f"Перевірте логи сервера для деталей"
                )
            except:
                pass
        
        sys.exit(1)
    finally:
        await ukrainian_bot.shutdown()

if __name__ == "__main__":
    try:
        # Запуск з обробкою помилок asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До побачення! Дякуємо за використання бота!")
    except Exception as e:
        print(f"\n💥 Фатальна помилка: {e}")
        print("📝 Перевірте логи в папці logs/ для деталей")
        sys.exit(1)