#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ З ДУЕЛЯМИ 🧠😂🔥

НОВИНКИ В КРОЦІ 5:
⚔️ Повна система дуелів жартів
🗳️ Голосування за найкращий контент  
🏆 Рейтингова система дуелістів
🎯 Автоматичне завершення дуелів
📊 Розширена статистика та ранги
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Optional
import signal

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

class UkrainianTelegramBotWithDuels:
    """Україномовний бот з повною системою дуелів"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.startup_time = datetime.now()
        self.db_available = False
        self.handlers_status = {}
        self.shutdown_event = asyncio.Event()
        
    def is_admin(self, user_id: int) -> bool:
        """Перевірка чи користувач є адміністратором"""
        try:
            from config.settings import settings
            admin_ids = [settings.ADMIN_ID]
            if hasattr(settings, 'ADDITIONAL_ADMINS'):
                admin_ids.extend(settings.ADDITIONAL_ADMINS)
            return user_id in admin_ids
        except:
            return user_id == 603047391  # Fallback admin ID

    async def initialize_bot(self):
        """Ініціалізація бота з повною підтримкою дуелів"""
        try:
            logger.info("🔍 Завантаження налаштувань...")
            
            # Завантаження конфігурації
            try:
                from config.settings import settings
                bot_token = settings.BOT_TOKEN
                logger.info("✅ Settings loaded from config.settings")
            except ImportError:
                bot_token = os.getenv('BOT_TOKEN')
                logger.warning("⚠️ Using environment BOT_TOKEN")
            
            if not bot_token:
                raise ValueError("BOT_TOKEN not found")
            
            # Ініціалізація aiogram
            from aiogram import Bot, Dispatcher
            from aiogram.client.default import DefaultBotProperties
            from aiogram.enums import ParseMode
            
            self.bot = Bot(
                token=bot_token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            self.dp = Dispatcher()
            
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Bot created: @{bot_info.username}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            return False

    async def initialize_database(self):
        """Ініціалізація бази даних з підтримкою дуелів"""
        try:
            logger.info("💾 Ініціалізація БД з підтримкою дуелів...")
            
            from database.database import init_database
            success = await init_database()
            
            if success:
                logger.info("✅ Database initialized successfully")
                
                # Перевірка моделей дуелів
                try:
                    from database.models import Duel, DuelVote
                    logger.info("✅ Duel models loaded successfully")
                except ImportError as e:
                    logger.warning(f"⚠️ Duel models not available: {e}")
                
                self.db_available = True
                return True
            else:
                logger.warning("⚠️ Database initialization failed")
                return False
                
        except ImportError:
            logger.warning("⚠️ Database module not available - working without DB")
            return False
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            return False

    async def register_handlers(self):
        """Реєстрація всіх хендлерів включно з дуелями"""
        try:
            logger.info("🔧 Реєстрація хендлерів з підтримкою дуелів...")
            
            # Реєстрація через handlers/__init__.py
            from handlers import register_handlers
            self.handlers_status = register_handlers(self.dp)
            
            # Додаткові основні хендлери
            await self.register_core_handlers()
            
            # Callback хендлер з підтримкою дуелів
            await self.register_enhanced_callbacks()
            
            logger.info("✅ All handlers registered with duel support")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers registration failed: {e}")
            return False

    async def register_core_handlers(self):
        """Основні хендлери з меню дуелів"""
        from aiogram import F
        from aiogram.filters import Command
        from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
        
        @self.dp.message(Command("start"))
        async def enhanced_start(message: Message):
            """Розширена команда /start з меню дуелів"""
            try:
                user_id = message.from_user.id
                is_admin = self.is_admin(user_id)
                
                # Реєстрація користувача
                if self.db_available:
                    try:
                        from database.services import get_or_create_user
                        await get_or_create_user(
                            user_id, 
                            message.from_user.username, 
                            message.from_user.full_name
                        )
                    except Exception as e:
                        logger.error(f"Error creating user: {e}")
                
                # Текст привітання
                text = "🧠😂🔥 <b>УКРАЇНОМОВНИЙ БОТ З ДУЕЛЯМИ!</b> 🧠😂🔥\n\n"
                
                if is_admin:
                    text += "👑 <b>Адмін режим активний</b>\n\n"
                
                text += (
                    "🎯 <b>Новинка: ДУЕЛІ ЖАРТІВ!</b> ⚔️\n"
                    "Змагайтеся за звання найкращого коміка!\n\n"
                    "📋 <b>Головні функції:</b>\n"
                    "• ⚔️ Дуелі жартів з голосуванням\n"
                    "• 😂 Меми та анекдоти\n"
                    "• 🏆 Рейтингова система\n"
                    "• 👤 Персональний профіль\n"
                    "• 📊 Детальна статистика"
                )
                
                # Створення клавіатури з дуелями
                keyboard_rows = [
                    [InlineKeyboardButton(text="⚔️ Дуелі жартів", callback_data="duel_menu")],
                    [
                        InlineKeyboardButton(text="😂 Мем", callback_data="get_meme"),
                        InlineKeyboardButton(text="🤣 Жарт", callback_data="get_joke")
                    ],
                    [
                        InlineKeyboardButton(text="👤 Профіль", callback_data="profile"),
                        InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
                    ]
                ]
                
                # Адмін кнопки
                if is_admin:
                    keyboard_rows.append([
                        InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderate"),
                        InlineKeyboardButton(text="📈 Адмін стат", callback_data="admin_stats")
                    ])
                
                keyboard_rows.append([
                    InlineKeyboardButton(text="❓ Допомога", callback_data="help")
                ])
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
                
                await message.answer(text, reply_markup=keyboard)
                
                # Повідомлення адміну про запуск з дуелями
                if is_admin:
                    try:
                        from config.settings import settings
                        uptime = datetime.now() - self.startup_time
                        admin_text = (
                            f"✅ <b>Бот запущено в професійному режимі з дуелями!</b>\n\n"
                            f"⚔️ <b>Система дуелів:</b> Активна\n"
                            f"💾 <b>База даних:</b> {'Підключена' if self.db_available else 'Fallback'}\n"
                            f"🔧 <b>Хендлери:</b> {self.handlers_status.get('total_registered', 0)}/4\n"
                            f"⏰ <b>Uptime:</b> {uptime.total_seconds():.1f}с\n\n"
                            f"🎯 <b>Нові функції:</b>\n"
                            f"• /duel - система дуелів\n"
                            f"• Голосування за жарти\n"
                            f"• Рейтинги дуелістів\n"
                            f"• Автоматичне завершення дуелів"
                        )
                        
                        await self.bot.send_message(settings.ADMIN_ID, admin_text)
                    except Exception as e:
                        logger.error(f"Error sending admin notification: {e}")
                
            except Exception as e:
                logger.error(f"Error in start handler: {e}")
                await message.answer("🤖 Бот запущено! Використовуйте /help для довідки.")

        @self.dp.message(Command("help"))
        async def enhanced_help(message: Message):
            """Розширена довідка з дуелями"""
            try:
                text = (
                    "📖 <b>ДОВІДКА - ПРОФЕСІЙНИЙ БОТ З ДУЕЛЯМИ</b>\n\n"
                    
                    "⚔️ <b>ДУЕЛІ ЖАРТІВ (НОВИНКА!):</b>\n"
                    "• /duel - головне меню дуелів\n"
                    "• Голосуйте за найкращий жарт\n"
                    "• Здобувайте рейтинг та ранги\n"
                    "• Отримуйте бали за перемоги\n\n"
                    
                    "😂 <b>КОНТЕНТ:</b>\n"
                    "• /meme - випадковий мем\n"
                    "• /joke - смішний жарт\n"
                    "• /anekdot - український анекдот\n"
                    "• Лайкайте та діліться\n\n"
                    
                    "👤 <b>ПРОФІЛЬ:</b>\n"
                    "• /profile - ваша статистика\n"
                    "• Система балів та рангів\n"
                    "• Історія дуелей\n"
                    "• Досягнення\n\n"
                    
                    "🎮 <b>СИСТЕМА БАЛІВ:</b>\n"
                    "• +2 бали за голосування в дуелі\n"
                    "• +10 балів за участь у дуелі\n"
                    "• +25 балів за перемогу\n"
                    "• +50 балів за розгромну перемогу\n\n"
                    
                    "🏆 <b>РАНГИ ДУЕЛІСТІВ:</b>\n"
                    "• 🥉 Стажер (0-999)\n"
                    "• 🎯 Новачок (1000-1199)\n"
                    "• 🔥 Досвідчений (1200-1399)\n"
                    "• ⚡ Професіонал (1400-1599)\n"
                    "• ⭐ Експерт (1600-1799)\n"
                    "• 🏆 Майстер (1800-1999)\n"
                    "• 👑 Гранд-майстер (2000+)"
                )
                
                # Адмін команди
                if self.is_admin(message.from_user.id):
                    text += (
                        "\n\n🛡️ <b>АДМІН КОМАНДИ:</b>\n"
                        "• /admin_stats - детальна статистика\n"
                        "• /moderate - модерація контенту\n"
                        "• /pending - контент на розгляді\n"
                        "• /approve_ID - схвалити\n"
                        "• /reject_ID причина - відхилити"
                    )
                
                await message.answer(text)
                
            except Exception as e:
                logger.error(f"Error in help handler: {e}")
                await message.answer("📖 <b>Довідка</b>\n\nБазові команди: /start, /duel, /profile, /help")

    async def register_enhanced_callbacks(self):
        """Розширені callback хендлери з підтримкою дуелів"""
        
        @self.dp.callback_query()
        async def handle_enhanced_callbacks(callback):
            """Головний callback хендлер з підтримкою дуелів"""
            try:
                data = callback.data
                user_id = callback.from_user.id
                is_admin = self.is_admin(user_id)
                
                # Перевіряємо спеціалізовані callback'и
                if any(data.startswith(prefix) for prefix in [
                    "like_", "dislike_", "more_", "submit_",  # content
                    "admin_", "moderate_",                    # admin
                    "vote_", "duel_", "create_duel", "view_duels"  # duels
                ]):
                    return  # Нехай спеціалізовані хендлери обробляють
                
                # Основні callback'и
                if data == "duel_menu":
                    # Переходимо до меню дуелів
                    try:
                        from handlers.duel_handlers import cmd_duel
                        await cmd_duel(callback.message)
                        await callback.answer("⚔️ Дуелі жартів!")
                    except ImportError:
                        await callback.message.edit_text(
                            "⚔️ <b>ДУЕЛІ ЖАРТІВ</b>\n\n"
                            "Система дуелів тимчасово недоступна.\n"
                            "Спробуйте пізніше або використайте /duel"
                        )
                        await callback.answer("Завантаження...")
                        
                elif data == "get_meme":
                    try:
                        from handlers.content_handlers import handle_meme_command
                        await handle_meme_command(callback.message)
                        await callback.answer("😂 Мем завантажено!")
                    except ImportError:
                        await callback.message.answer("😂 <i>Коли твій код працює з першого разу...\nЗначить щось пішло не так! 🤔</i>")
                        await callback.answer()
                        
                elif data == "get_joke":
                    try:
                        from handlers.content_handlers import handle_joke_command
                        await handle_joke_command(callback.message)
                        await callback.answer("🤣 Жарт завантажено!")
                    except ImportError:
                        await callback.message.answer("🤣 <i>Програміст заходить у бар...\nБармен каже: 'Як завжди?' Програміст: 'Ні, цього разу я просто випити прийшов!'</i>")
                        await callback.answer()
                
                elif data == "profile":
                    if self.db_available:
                        try:
                            from database.services import get_user_by_id, get_user_duel_stats
                            
                            user = await get_user_by_id(user_id)
                            duel_stats = await get_user_duel_stats(user_id)
                            
                            if user:
                                # Визначаємо ранг
                                points = user.get('total_points', 0)
                                if points >= 5000:
                                    rank = "🚀 Гумористичний Геній"
                                elif points >= 3000:
                                    rank = "🌟 Легенда Мемів"
                                elif points >= 1500:
                                    rank = "🏆 Король Гумору"
                                elif points >= 750:
                                    rank = "👑 Мастер Рофлу"
                                elif points >= 350:
                                    rank = "🎭 Комік"
                                elif points >= 150:
                                    rank = "😂 Гуморист"
                                elif points >= 50:
                                    rank = "😄 Сміхун"
                                else:
                                    rank = "🤡 Новачок"
                                
                                text = f"👤 <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n\n"
                                text += f"🏷️ Ім'я: {user.get('full_name', 'Невідомо')}\n"
                                text += f"👑 Ранг: {rank}\n"
                                text += f"💰 Бали: {points}\n"
                                text += f"📅 Реєстрація: {user.get('created_at', 'Невідомо')}\n\n"
                                
                                # Статистика дуелів
                                if duel_stats:
                                    wins = duel_stats.get('wins', 0)
                                    total = duel_stats.get('total_duels', 0)
                                    win_rate = (wins / total * 100) if total > 0 else 0
                                    duel_rating = duel_stats.get('rating', 1000)
                                    
                                    text += f"⚔️ <b>СТАТИСТИКА ДУЕЛІВ:</b>\n"
                                    text += f"🏆 Перемоги: {wins}/{total} ({win_rate:.1f}%)\n"
                                    text += f"⭐ Рейтинг: {duel_rating}\n"
                                    
                                    # Ранг дуеліста
                                    if duel_rating >= 2000:
                                        duel_rank = "👑 Гранд-майстер"
                                    elif duel_rating >= 1800:
                                        duel_rank = "🏆 Майстер"
                                    elif duel_rating >= 1600:
                                        duel_rank = "⭐ Експерт"
                                    elif duel_rating >= 1400:
                                        duel_rank = "⚡ Професіонал"
                                    elif duel_rating >= 1200:
                                        duel_rank = "🔥 Досвідчений"
                                    elif duel_rating >= 1000:
                                        duel_rank = "🎯 Новачок"
                                    else:
                                        duel_rank = "🥉 Стажер"
                                    
                                    text += f"🎯 Ранг дуеліста: {duel_rank}\n"
                                    
                                    if duel_stats.get('best_win_streak', 0) > 0:
                                        text += f"🔥 Найкраща серія: {duel_stats['best_win_streak']}\n"
                                else:
                                    text += "⚔️ <b>Ще не брали участь у дуелях</b>\n"
                                    text += "Використайте /duel щоб почати!"
                                
                                await callback.message.edit_text(text)
                            else:
                                await callback.message.edit_text("❌ Профіль не знайдено")
                        except Exception as e:
                            logger.error(f"Error in profile callback: {e}")
                            await callback.message.edit_text("❌ Помилка завантаження профілю")
                    else:
                        await callback.message.edit_text(
                            "👤 <b>Ваш профіль</b>\n\n"
                            "🎮 Ранг: Новачок\n"
                            "💰 Бали: 0\n"
                            "⚔️ Дуелі: 0/0\n\n"
                            "📊 База даних недоступна"
                        )
                    
                    await callback.answer()
                    
                elif data == "stats":
                    try:
                        if self.db_available:
                            from database.services import get_basic_stats
                            stats = get_basic_stats()
                            
                            text = f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
                            text += f"👥 Користувачів: {stats.get('total_users', '?')}\n"
                            text += f"😂 Контенту: {stats.get('total_content', '?')}\n"
                            text += f"✅ Схвалено: {stats.get('approved_content', '?')}\n"
                            text += f"⚔️ Дуелей: {stats.get('total_duels', '?')}\n"
                            text += f"🗳️ Голосів: {stats.get('total_votes', '?')}\n"
                            text += f"🏆 Активних дуелей: {stats.get('active_duels', '?')}\n\n"
                            text += f"📈 <b>Система дуелей працює!</b>"
                        else:
                            text = (
                                "📊 <b>СТАТИСТИКА БОТА</b>\n\n"
                                "🤖 Статус: Онлайн\n"
                                "⚔️ Дуелі: Активні\n"
                                "💾 БД: Fallback режим\n"
                                "🔧 Версія: Professional з дуелями"
                            )
                        
                        await callback.message.edit_text(text)
                    except Exception as e:
                        logger.error(f"Error in stats callback: {e}")
                        await callback.message.edit_text("📊 Статистика тимчасово недоступна")
                    
                    await callback.answer()
                    
                elif data == "help":
                    await self.enhanced_help(callback.message)
                    await callback.answer()
                    
                # Адмін callback'и
                elif data == "admin_moderate" and is_admin:
                    try:
                        from handlers.admin_handlers import cmd_moderate
                        await cmd_moderate(callback.message)
                        await callback.answer("🛡️ Модерація")
                    except ImportError:
                        await callback.message.edit_text("🛡️ Модерація тимчасово недоступна")
                        await callback.answer()
                        
                elif data == "admin_stats" and is_admin:
                    try:
                        from handlers.admin_handlers import cmd_admin_stats
                        await cmd_admin_stats(callback.message)
                        await callback.answer("📈 Адмін статистика")
                    except ImportError:
                        await callback.message.edit_text("📈 Адмін статистика недоступна")
                        await callback.answer()
                
                else:
                    await callback.answer("🔄 Функція завантажується...")
                    
            except Exception as e:
                logger.error(f"Error in callback handler: {e}")
                await callback.answer("❌ Помилка обробки")

    async def setup_scheduler(self):
        """Налаштування планувальника для автоматичного завершення дуелів"""
        try:
            logger.info("⏰ Налаштування планувальника дуелів...")
            
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.interval import IntervalTrigger
            
            scheduler = AsyncIOScheduler()
            
            # Автоматичне завершення прострочених дуелів кожну хвилину
            if self.db_available:
                try:
                    from database.services import auto_finish_expired_duels, cleanup_old_duels
                    
                    scheduler.add_job(
                        auto_finish_expired_duels,
                        IntervalTrigger(minutes=1),
                        id='auto_finish_duels',
                        name='Auto finish expired duels'
                    )
                    
                    # Очистка старих дуелей щодня о 03:00
                    scheduler.add_job(
                        cleanup_old_duels,
                        'cron',
                        hour=3,
                        minute=0,
                        id='cleanup_old_duels',
                        name='Cleanup old duels'
                    )
                    
                    logger.info("✅ Duel scheduler configured")
                except ImportError:
                    logger.warning("⚠️ Duel services not available for scheduler")
            
            scheduler.start()
            logger.info("✅ Scheduler started successfully")
            return scheduler
            
        except ImportError:
            logger.warning("⚠️ APScheduler not available")
            return None
        except Exception as e:
            logger.error(f"❌ Scheduler setup failed: {e}")
            return None

    async def main(self):
        """Головна функція запуску бота з дуелями"""
        logger.info("🚀 Starting Enhanced Ukrainian Telegram Bot with Duels...")
        
        try:
            # Ініціалізація компонентів
            if not await self.initialize_bot():
                return False
            
            if not await self.initialize_database():
                logger.warning("⚠️ Working without full database support")
            
            if not await self.register_handlers():
                return False
            
            # Планувальник
            scheduler = await self.setup_scheduler()
            
            # Налаштування graceful shutdown
            def signal_handler():
                logger.info("📶 Shutdown signal received")
                self.shutdown_event.set()
            
            signal.signal(signal.SIGINT, lambda s, f: signal_handler())
            signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
            
            logger.info("✅ Bot fully initialized with duel system")
            
            # Запуск polling з graceful shutdown
            try:
                polling_task = asyncio.create_task(self.dp.start_polling(self.bot))
                shutdown_task = asyncio.create_task(self.shutdown_event.wait())
                
                logger.info("🎯 Bot started - Duels are active!")
                
                # Чекаємо або polling або shutdown
                done, pending = await asyncio.wait(
                    [polling_task, shutdown_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Скасовуємо pending завдання
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                
            finally:
                # Graceful shutdown
                if scheduler:
                    scheduler.shutdown()
                    logger.info("✅ Scheduler stopped")
                
                await self.bot.session.close()
                logger.info("✅ Bot session closed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Critical error in main: {e}")
            return False

# ===== ЗАПУСК =====

async def main():
    """Точка входу"""
    bot = UkrainianTelegramBotWithDuels()
    success = await bot.main()
    return success

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)