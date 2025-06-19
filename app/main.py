#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
?????? ОСНОВНИЙ МОДУЛЬ УКРАЇНОМОВНОГО TELEGRAM-БОТА ??????

РОЗТАШУВАННЯ: ukrainian-telegram-bot/app/main.py
ЗАПУСК ЧЕРЕЗ: ukrainian-telegram-bot/main.py

АРХІТЕКТУРА:
? Модульна структура з app/
? Правильні імпорти з відносними шляхами
? Безпечна ініціалізація всіх компонентів
? Професійна обробка помилок
? Graceful shutdown
? Railway-сумісність
"""

import asyncio
import logging
import sys
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional
import traceback

# Налаштування логування для app/ модуля
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # Логи тільки в development (не на Railway)
        *([] if os.getenv('RAILWAY_ENVIRONMENT') else [
            logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'bot.log', encoding='utf-8')
        ])
    ]
)

logger = logging.getLogger(__name__)

# Aiogram imports з обробкою помилок
try:
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.exceptions import TelegramNetworkError, TelegramBadRequest
    AIOGRAM_AVAILABLE = True
except ImportError as e:
    logger.error(f"? Помилка імпорту aiogram: {e}")
    logger.error("?? Встановіть: pip install aiogram>=3.4.0")
    AIOGRAM_AVAILABLE = False

class UkrainianTelegramBot:
    """?? ВИПРАВЛЕНИЙ клас україномовного Telegram-бота"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.scheduler_service = None
        self.is_running = False
        self.startup_time = datetime.now()
        self.health_server = None
        
        # Обробка сигналів для коректного завершення
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обробка сигналів завершення"""
        logger.info(f"?? Отримано сигнал {signum}")
        self.is_running = False
    
    def print_banner(self):
        """Красивий банер запуску"""
        print("\n" + "??????" * 20)
        print("?? ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ v2.0 ??")
        print("???? ВИПРАВЛЕНА ВЕРСІЯ З PROPER ASYNC/AWAIT ????")
        print("??????" * 20 + "\n")
    
    def load_settings(self) -> dict:
        """Завантаження налаштувань з обробкою помилок для app/ структури"""
        try:
            # Спроба імпорту з відносним шляхом
            from config.settings import settings
            return {
                'bot_token': settings.BOT_TOKEN,
                'admin_id': settings.ADMIN_ID,
                'database_url': getattr(settings, 'DATABASE_URL', 'sqlite:///bot.db'),
                'debug': getattr(settings, 'DEBUG', False),
                'timezone': getattr(settings, 'TIMEZONE', 'Europe/Kiev')
            }
        except ImportError:
            logger.warning("?? Не вдалося імпортувати config.settings з app/, використовую env")
            return {
                'bot_token': os.getenv('BOT_TOKEN'),
                'admin_id': int(os.getenv('ADMIN_ID', 0)),
                'database_url': os.getenv('DATABASE_URL', 'sqlite:///ukrainian_bot.db'),
                'debug': os.getenv('DEBUG', 'False').lower() == 'true',
                'timezone': os.getenv('TIMEZONE', 'Europe/Kiev')
            }
    
    def validate_settings(self, settings: dict) -> bool:
        """Валідація налаштувань"""
        if not settings.get('bot_token'):
            logger.error("? BOT_TOKEN не встановлено!")
            return False
        
        if not settings.get('admin_id'):
            logger.error("? ADMIN_ID не встановлено!")
            return False
        
        logger.info("? Налаштування валідні")
        return True
    
    async def init_database(self) -> bool:
        """Безпечна ініціалізація БД з урахуванням app/ структури"""
        try:
            # Спроба імпорту з app/database
            from database import init_db
            await init_db()
            logger.info("? База даних ініціалізована")
            return True
        except ImportError:
            logger.warning("?? Модуль database недоступний з app/, працюю без БД")
            return True
        except Exception as e:
            logger.error(f"? Помилка ініціалізації БД: {e}")
            return False
    
    async def create_bot(self, settings: dict) -> bool:
        """Створення бота"""
        try:
            if not AIOGRAM_AVAILABLE:
                logger.error("? aiogram недоступний")
                return False
            
            self.bot = Bot(
                token=settings['bot_token'],
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML
                )
            )
            
            self.dp = Dispatcher()
            
            # Тест з'єднання
            bot_info = await self.bot.get_me()
            logger.info(f"? Бот створено: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"? Помилка створення бота: {e}")
            return False
    
    async def setup_dispatcher(self) -> bool:
        """Налаштування диспетчера"""
        try:
            # Реєстрація базових команд
            from aiogram.filters import Command
            from aiogram.types import Message
            
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message):
                await message.answer("?????? Бот працює в тестовому режимі!")
            
            @self.dp.message(Command("status"))
            async def cmd_status(message: Message):
                uptime = datetime.now() - self.startup_time
                await message.answer(f"? Статус: Працює\n? Час роботи: {uptime}")
            
            # Спроба реєстрації всіх хендлерів з app/handlers
            try:
                from handlers import register_all_handlers
                register_all_handlers(self.dp)
                logger.info("? Всі хендлери зареєстровано з app/handlers")
            except ImportError:
                logger.warning("?? app/handlers недоступні, працюю з базовими командами")
            except Exception as e:
                logger.warning(f"?? Помилка реєстрації хендлерів: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"? Помилка налаштування диспетчера: {e}")
            return False
    
    async def setup_scheduler(self, settings: dict):
        """Налаштування планувальника з app/services"""
        try:
            from services.scheduler import SchedulerService
            self.scheduler_service = SchedulerService(self.bot)
            await self.scheduler_service.start()
            logger.info("? Планувальник запущено з app/services")
        except ImportError:
            logger.warning("?? app/services/scheduler недоступний")
        except Exception as e:
            logger.error(f"? Помилка планувальника: {e}")
    
    async def startup_checks(self, settings: dict):
        """Перевірки при запуску"""
        try:
            # Повідомлення адміністратору про запуск
            if settings.get('admin_id') and self.bot:
                await self.bot.send_message(
                    settings['admin_id'],
                    "? <b>БОТ УСПІШНО ЗАПУЩЕНО</b>\n\n"
                    f"?? Час запуску: {self.startup_time.strftime('%H:%M:%S')}\n"
                    f"?? Версія: 2.0 (Виправлена)\n"
                    f"?? Середовище: {'Production' if os.getenv('RAILWAY_ENVIRONMENT') else 'Development'}"
                )
        except Exception as e:
            logger.warning(f"?? Не вдалося надіслати повідомлення адміну: {e}")
    
    async def run_bot(self):
        """Запуск основного циклу бота"""
        try:
            self.is_running = True
            logger.info("?? Початок polling...")
            
            await self.dp.start_polling(
                self.bot,
                skip_updates=True,
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            
        except Exception as e:
            logger.error(f"? Помилка polling: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Коректне завершення роботи"""
        try:
            logger.info("?? Початок процедури завершення...")
            
            # Повідомлення адміністратору
            if self.bot:
                try:
                    from config.settings import settings
                    uptime = datetime.now() - self.startup_time
                    shutdown_message = (
                        "?? <b>БОТ ЗУПИНЕНО</b>\n\n"
                        f"? Час роботи: {uptime}\n"
                        f"?? Статус: Коректне завершення"
                    )
                    await self.bot.send_message(settings.ADMIN_ID, shutdown_message)
                except ImportError:
                    logger.warning("?? Не вдалося імпортувати налаштування для повідомлення адміну")
                except Exception:
                    pass
            
            # Зупинка планувальника
            if self.scheduler_service:
                await self.scheduler_service.stop()
                logger.info("? Планувальник зупинено")
            
            # Закриття сесії бота
            if self.bot:
                await self.bot.session.close()
                logger.info("?? Сесія бота закрита")
            
            uptime = datetime.now() - self.startup_time
            logger.info(f"?? Час роботи: {uptime}")
            logger.info("?? Бот зупинено коректно")
            
        except Exception as e:
            logger.error(f"? Помилка при завершенні: {e}")
    
    async def main(self):
        """?? ВИПРАВЛЕНА головна функція запуску"""
        self.print_banner()
        
        try:
            # Крок 1: Завантаження налаштувань
            logger.info("?? ?? Завантаження налаштувань...")
            settings = self.load_settings()
            
            if not self.validate_settings(settings):
                logger.error("? Помилка валідації налаштувань")
                return False
            
            # Крок 2: Ініціалізація БД
            logger.info("?? ?? Ініціалізація БД...")
            if not await self.init_database():
                logger.error("? Критична помилка БД")
                return False
            
            # Крок 3: Створення бота
            logger.info("?? ?? Створення бота...")
            if not await self.create_bot(settings):
                logger.error("? Не вдалося створити бота")
                return False
            
            # Крок 4: Налаштування диспетчера
            logger.info("?? ?? Налаштування диспетчера...")
            if not await self.setup_dispatcher():
                logger.error("? Помилка налаштування диспетчера")
                return False
            
            # Крок 5: Планувальник
            logger.info("?? ?? Налаштування планувальника...")
            await self.setup_scheduler(settings)
            
            # Крок 6: Перевірки при запуску
            logger.info("?? ?? Перевірки при запуску...")
            await self.startup_checks(settings)
            
            # Крок 7: Запуск
            logger.info("?? ?? Запуск бота...")
            await self.run_bot()
            
            return True
            
        except Exception as e:
            logger.error(f"?? КРИТИЧНА ПОМИЛКА: {e}")
            logger.error(traceback.format_exc())
            return False

async def main():
    """?? ВИПРАВЛЕНА точка входу в програму"""
    bot = UkrainianTelegramBot()
    
    try:
        result = await bot.main()
        return result
    except KeyboardInterrupt:
        logger.info("?? Зупинка через Ctrl+C")
        return True
    except Exception as e:
        logger.error(f"?? Неочікувана помилка: {e}")
        logger.error(traceback.format_exc())
        return False

# Точка входу для синхронного виклику
def sync_main():
    """Синхронна обгортка для main()"""
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("?? Зупинка через Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.error(f"?? Неочікувана помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_main()