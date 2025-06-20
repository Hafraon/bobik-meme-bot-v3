#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ПОВНІСТЮ ВИПРАВЛЕНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ 🚀

ВИПРАВЛЕННЯ:
✅ Додано всі typing імпорти (List, Dict, Any)
✅ Виправлено AutomatedScheduler аргументи
✅ Правильне закриття aiohttp сесій
✅ Покращена обробка помилок БД
✅ Розширена система автоматизації
"""

import asyncio
import logging
import sys
import os
import signal
from datetime import datetime
from typing import Optional, List, Dict, Any, Union  # ✅ ВИПРАВЛЕНО: всі typing імпорти
import traceback

# Додаємо app до Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Telegram Bot API
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

class AutomatedUkrainianTelegramBot:
    """Повністю автоматизований україномовний Telegram бот"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.startup_time = datetime.now()
        self.db_available = False
        self.handlers_status = {}
        self.shutdown_event = asyncio.Event()
        
        # Системи автоматизації
        self.scheduler = None
        self.broadcast_system = None
        self.automation_active = False
        
        # Налаштування з environment variables
        self.bot_token = os.getenv("BOT_TOKEN")
        self.admin_id = int(os.getenv("ADMIN_ID", "603047391"))
        
        if not self.bot_token:
            logger.error("❌ BOT_TOKEN не знайдено в environment variables!")
            sys.exit(1)
        
        logger.info("🧠😂🔥 Ініціалізація україномовного бота...")

    def is_admin(self, user_id: int) -> bool:
        """Перевірка чи користувач є адміністратором"""
        return user_id == self.admin_id

    async def initialize_bot(self) -> bool:
        """Ініціалізація бота та диспетчера"""
        try:
            logger.info("🤖 Ініціалізація Telegram бота...")
            
            # Створення бота з правильними налаштуваннями
            self.bot = Bot(
                token=self.bot_token,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            )
            
            # Створення диспетчера
            self.dp = Dispatcher()
            
            # Перевірка підключення
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Бот підключено: @{bot_info.username} ({bot_info.full_name})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації бота: {e}")
            return False

    async def initialize_database(self) -> bool:
        """Ініціалізація бази даних"""
        try:
            logger.info("💾 Ініціалізація бази даних...")
            
            # Спроба імпорту та ініціалізації БД
            try:
                from database import init_db
                self.db_available = await init_db()
                
                if self.db_available:
                    logger.info("✅ База даних ініціалізована успішно")
                else:
                    logger.warning("⚠️ База даних недоступна - працюємо в fallback режимі")
                    
            except ImportError as e:
                logger.warning(f"⚠️ Database модуль недоступний: {e}")
                self.db_available = False
            except Exception as e:
                logger.error(f"❌ Помилка ініціалізації БД: {e}")
                self.db_available = False
            
            return True  # Завжди повертаємо True - бот може працювати без БД
            
        except Exception as e:
            logger.error(f"❌ Критична помилка БД: {e}")
            return False

    async def initialize_automation(self) -> bool:
        """Ініціалізація системи автоматизації"""
        logger.info("🤖 Ініціалізація системи автоматизації...")
        
        try:
            # Імпорт модулів автоматизації
            from services.automated_scheduler import create_automated_scheduler
            
            # ✅ ВИПРАВЛЕНО: Передаємо правильні аргументи
            self.scheduler = await create_automated_scheduler(self.bot, self.db_available)
            
            if self.scheduler:
                logger.info("✅ Automated scheduler створено")
                
                # Запуск планувальника
                if await self.scheduler.start():
                    self.automation_active = True
                    logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА - бот працює самостійно!")
                    
                    # Логування статусу
                    status = self.scheduler.get_scheduler_status()
                    logger.info(f"📅 Запущено {status['jobs_count']} автоматичних завдань")
                    
                    return True
                else:
                    logger.warning("⚠️ Не вдалося запустити планувальник")
                    return False
            else:
                logger.warning("⚠️ Не вдалося створити планувальник")
                return False
                
        except ImportError as e:
            logger.warning(f"⚠️ Automation services недоступні: {e}")
            logger.info("📄 Працюємо без автоматизації")
            return False
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації автоматизації: {e}")
            logger.error(traceback.format_exc())
            return False

    async def register_handlers(self) -> bool:
        """Реєстрація всіх хендлерів"""
        try:
            logger.info("🔧 Реєстрація хендлерів з автоматизацією...")
            
            # Основні хендлери з handlers/__init__.py
            try:
                from handlers import register_handlers
                register_handlers(self.dp)
                logger.info("✅ Основні хендлери зареєстровано")
            except Exception as e:
                logger.error(f"❌ Помилка реєстрації основних хендлерів: {e}")
                # Реєструємо fallback хендлери
                await self._register_fallback_handlers()
            
            # Додаткові хендлери автоматизації
            await self._register_automation_handlers()
            
            logger.info("✅ All handlers registered with automation support")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers registration failed: {e}")
            logger.error(traceback.format_exc())
            return False

    async def _register_fallback_handlers(self):
        """Реєстрація fallback хендлерів на випадок проблем з основними"""
        
        @self.dp.message(Command("start"))
        async def fallback_start(message: Message):
            """Fallback команда /start"""
            await message.answer(
                "🤖 <b>Україномовний бот активний!</b>\n\n"
                "⚡ Базовий функціонал доступний\n"
                "🔧 Використовуйте /help для довідки"
            )
        
        @self.dp.message(Command("help"))
        async def fallback_help(message: Message):
            """Fallback команда /help"""
            await message.answer(
                "📚 <b>Довідка по боту:</b>\n\n"
                "🤖 /start - Головне меню\n"
                "📊 /status - Статус автоматизації\n"
                "🛡️ /admin - Адмін панель (тільки для адміністраторів)"
            )
        
        logger.info("✅ Fallback хендлери зареєстровано")

    async def _register_automation_handlers(self):
        """Хендлери з підтримкою автоматизації"""
        
        @self.dp.message(Command("start"))
        async def automated_start(message: Message):
            """Розширена команда /start з автоматизацією"""
            user_id = message.from_user.id
            first_name = message.from_user.first_name or "Друже"
            
            # Реєстрація користувача в БД (якщо доступна)
            if self.db_available:
                try:
                    from database import get_or_create_user
                    await get_or_create_user(
                        telegram_id=user_id,
                        username=message.from_user.username,
                        first_name=first_name,
                        last_name=message.from_user.last_name
                    )
                except Exception as e:
                    logger.error(f"❌ Помилка реєстрації користувача: {e}")
            
            # Створення меню
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
                    InlineKeyboardButton(text="🛡️ Модерація", callback_data="moderation")
                ],
                [
                    InlineKeyboardButton(text="👥 Користувачі", callback_data="users"),
                    InlineKeyboardButton(text="📝 Контент", callback_data="content")
                ],
                [
                    InlineKeyboardButton(text="🔥 Трендове", callback_data="trending"),
                    InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings")
                ],
                [
                    InlineKeyboardButton(text="🚀 Масові дії", callback_data="bulk_actions"),
                    InlineKeyboardButton(text="💾 Бекап", callback_data="backup")
                ],
                [
                    InlineKeyboardButton(text="🤖 Автоматизація", callback_data="automation"),
                    InlineKeyboardButton(text="📢 Розсилки", callback_data="broadcasts")
                ],
                [
                    InlineKeyboardButton(text="❌ Вимкнути адмін меню", callback_data="disable_admin_menu")
                ]
            ])
            
            automation_status = "Активна" if self.automation_active else "Неактивна"
            db_status = "Підключена" if self.db_available else "Fallback режим"
            
            welcome_text = (
                f"🧠😂🔥 <b>Вітаю, {first_name}!</b>\n\n"
                f"🤖 <b>Україномовний бот з автоматизацією</b>\n\n"
                f"📊 <b>Статус системи:</b>\n"
                f"⚡ Автоматизація: {automation_status}\n"
                f"💾 База даних: {db_status}\n"
                f"🕐 Запущено: {self.startup_time.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"🎯 <b>Основні функції:</b>\n"
                f"• 😂 Меми та жарти\n"
                f"• ⚔️ Дуелі жартів\n"
                f"• 🤖 Автоматичні розсилки\n"
                f"• 📊 Детальна статистика\n"
                f"• 🛡️ Система модерації\n\n"
                f"Оберіть дію з меню нижче:"
            )
            
            await message.answer(welcome_text, reply_markup=keyboard)

        @self.dp.message(Command("status"))
        async def automation_status(message: Message):
            """Статус автоматизації"""
            if self.scheduler:
                status = self.scheduler.get_scheduler_status()
                jobs = self.scheduler.get_jobs_info()
                
                status_text = (
                    f"🤖 <b>СТАТУС АВТОМАТИЗАЦІЇ</b>\n\n"
                    f"⚡ Планувальник: {'Активний' if status['is_running'] else 'Неактивний'}\n"
                    f"💾 База даних: {'Доступна' if status['db_available'] else 'Недоступна'}\n"
                    f"📅 Завдань: {status['jobs_count']}\n"
                    f"⏱️ Час роботи: {status['uptime_hours']:.1f} год\n\n"
                    f"📊 <b>Статистика:</b>\n"
                    f"• Виконано завдань: {status['stats']['jobs_executed']}\n"
                    f"• Помилок: {status['stats']['jobs_failed']}\n"
                    f"• Розсилок: {status['stats']['broadcasts_sent']}\n\n"
                )
                
                if jobs:
                    status_text += f"📋 <b>Наступні завдання:</b>\n"
                    for job in jobs[:5]:  # Показуємо перші 5
                        status_text += f"• {job['name']}\n"
                    
                    if len(jobs) > 5:
                        status_text += f"... та ще {len(jobs) - 5} завдань"
                        
            else:
                status_text = "❌ Планувальник не ініціалізований"
            
            await message.answer(status_text)

        # Callback обробник
        @self.dp.callback_query(F.data.startswith((
            "stats", "moderation", "users", "content", "trending", 
            "settings", "bulk_actions", "backup", "automation", 
            "broadcasts", "disable_admin_menu"
        )))
        async def enhanced_callback_handler(callback: CallbackQuery):
            """Розширений callback обробник з автоматизацією"""
            await callback.answer()
            
            data = callback.data
            user_id = callback.from_user.id
            
            if data == "automation" and self.is_admin(user_id):
                if self.scheduler:
                    status = self.scheduler.get_scheduler_status()
                    jobs = self.scheduler.get_jobs_info()
                    
                    text = (
                        f"🤖 <b>АВТОМАТИЗАЦІЯ</b>\n\n"
                        f"⚡ Статус: {'Активна' if self.automation_active else 'Неактивна'}\n"
                        f"📅 Завдань: {len(jobs)}\n"
                        f"🚀 Запущено: {self.startup_time.strftime('%d.%m.%Y %H:%M')}\n\n"
                        f"📋 <b>Поточні завдання:</b>\n"
                    )
                    
                    for job in jobs:
                        if job['next_run']:
                            next_run = datetime.fromisoformat(job['next_run']).strftime('%H:%M')
                            text += f"• {job['name']}: {next_run}\n"
                        else:
                            text += f"• {job['name']}: інтервальне\n"
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔄 Перезапустити", callback_data="restart_automation")],
                        [InlineKeyboardButton(text="⏹️ Зупинити", callback_data="stop_automation")],
                        [InlineKeyboardButton(text="📊 Детальна статистика", callback_data="detailed_stats")],
                        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
                    ])
                    
                    await callback.message.edit_text(text, reply_markup=keyboard)
                else:
                    await callback.message.edit_text("❌ Автоматизація недоступна")
            
            elif data == "broadcasts" and self.is_admin(user_id):
                text = (
                    f"📢 <b>СИСТЕМА РОЗСИЛОК</b>\n\n"
                    f"📊 Статистика розсилок:\n"
                    f"• Відправлено сьогодні: {self.stats.get('broadcasts_sent', 0) if hasattr(self, 'stats') else 'N/A'}\n"
                    f"• Активних підписників: N/A\n"
                    f"• Остання розсилка: N/A\n\n"
                    f"🕐 Автоматичні розсилки:\n"
                    f"• 9:00 - Ранковий контент\n"
                    f"• 20:00 - Вечірня статистика\n"
                    f"• П'ятниця 19:00 - Тижневий турнір\n"
                    f"• Неділя 18:00 - Тижневий дайджест"
                )
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📤 Тестова розсилка", callback_data="test_broadcast")],
                    [InlineKeyboardButton(text="📋 Список підписників", callback_data="subscribers_list")],
                    [InlineKeyboardButton(text="⚙️ Налаштування розсилок", callback_data="broadcast_settings")],
                    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
                ])
                
                await callback.message.edit_text(text, reply_markup=keyboard)
            
            else:
                # Стандартна обробка інших callback'ів
                await callback.message.edit_text(f"🔧 Функція '{data}' в розробці")

        logger.info("✅ Automation handlers зареєстровано")

    async def cleanup(self):
        """Очистка ресурсів перед завершенням"""
        logger.info("🧹 Cleanup resources...")
        
        try:
            # Зупинка автоматизації
            if self.scheduler:
                await self.scheduler.stop()
                logger.info("⏹️ Планувальник зупинено")
            
            # ✅ ВИПРАВЛЕНО: Правильне закриття aiohttp сесії
            if self.bot and hasattr(self.bot, 'session') and self.bot.session:
                if not self.bot.session.closed:
                    await self.bot.session.close()
                    logger.info("✅ Bot session closed")
            
        except Exception as e:
            logger.error(f"❌ Помилка cleanup: {e}")

    async def run(self):
        """Основний цикл роботи бота"""
        try:
            logger.info("🚀 Запуск україномовного бота з повною автоматизацією...")
            
            # Ініціалізація всіх компонентів
            if not await self.initialize_bot():
                logger.error("❌ Не вдалося ініціалізувати бота")
                return
            
            if not await self.initialize_database():
                logger.error("❌ Не вдалося ініціалізувати БД")
                return
            
            automation_success = await self.initialize_automation()
            if automation_success:
                logger.info("🤖 Автоматизація активна!")
            else:
                logger.warning("⚠️ Working without automation")
            
            if not await self.register_handlers():
                logger.error("❌ Не вдалося зареєструвати хендлери")
                return
            
            # Налаштування обробки сигналів для graceful shutdown
            def signal_handler():
                logger.info("🛑 Отримано сигнал зупинки")
                self.shutdown_event.set()
            
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, lambda s, f: signal_handler())
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
            
            # Запуск polling
            logger.info("🎯 Bot fully initialized with automation support")
            logger.info("🚀 Starting polling...")
            
            # Створення task для polling
            polling_task = asyncio.create_task(
                self.dp.start_polling(self.bot, allowed_updates=["message", "callback_query"])
            )
            
            # Створення task для очікування shutdown
            shutdown_task = asyncio.create_task(self.shutdown_event.wait())
            
            # Очікування завершення одного з task'ів
            done, pending = await asyncio.wait(
                [polling_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Скасування незавершених task'ів
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            logger.info("🛑 Бот завершує роботу...")
            
        except Exception as e:
            logger.error(f"❌ Критична помилка запуску: {e}")
            logger.error(traceback.format_exc())
        finally:
            await self.cleanup()

# ===== ГОЛОВНА ФУНКЦІЯ =====
async def main():
    """Головна функція запуску бота"""
    try:
        bot = AutomatedUkrainianTelegramBot()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # ✅ ВИПРАВЛЕНО: Правильний запуск async функції
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Програма завершена")
    except Exception as e:
        logger.error(f"💥 Фатальна помилка: {e}")
        sys.exit(1)