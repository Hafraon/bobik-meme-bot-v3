#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Optional

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class UkrainianTelegramBot:
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.startup_time = datetime.now()
        self.settings = None
        self.db_available = False
    
    def load_settings(self):
        """Завантаження налаштувань з config.settings або env"""
        try:
            from config.settings import settings
            self.settings = settings
            logger.info("✅ Settings loaded from config.settings")
            return {
                'bot_token': settings.BOT_TOKEN,
                'admin_id': settings.ADMIN_ID,
                'database_url': settings.DATABASE_URL,
                'debug': settings.DEBUG
            }
        except ImportError:
            logger.warning("⚠️ config.settings not available, using env variables")
            return {
                'bot_token': os.getenv('BOT_TOKEN'),
                'admin_id': int(os.getenv('ADMIN_ID', 0)),
                'database_url': os.getenv('DATABASE_URL', 'sqlite:///bot.db'),
                'debug': os.getenv('DEBUG', 'False').lower() == 'true'
            }
    
    def validate_settings(self, settings):
        if not settings.get('bot_token'):
            logger.error("❌ BOT_TOKEN not found!")
            return False
        if not settings.get('admin_id'):
            logger.error("❌ ADMIN_ID not found!")
            return False
        return True
    
    async def init_database(self, database_url: str):
        """Ініціалізація бази даних з новими сервісами"""
        try:
            from database.services import init_database, test_database_connection
            
            # Ініціалізація БД
            if init_database(database_url):
                # Тестування з'єднання
                if test_database_connection():
                    self.db_available = True
                    logger.info("✅ Database fully operational")
                    return True
                else:
                    logger.warning("⚠️ Database initialized but connection test failed")
                    return False
            else:
                logger.error("❌ Database initialization failed")
                return False
            
        except ImportError:
            logger.warning("⚠️ Database services not available, working without DB")
            return True
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return False
    
    async def create_bot(self, settings):
        try:
            from aiogram import Bot, Dispatcher
            from aiogram.enums import ParseMode
            from aiogram.client.default import DefaultBotProperties
            
            self.bot = Bot(
                token=settings['bot_token'],
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            self.dp = Dispatcher()
            
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Bot created: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot creation error: {e}")
            return False
    
    async def setup_handlers(self):
        """Налаштування всіх хендлерів включно з контентом"""
        try:
            from aiogram.filters import Command
            from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
            
            # Реєстрація всіх хендлерів з handlers/
            try:
                from handlers import register_all_handlers
                register_all_handlers(self.dp)
                logger.info("✅ All handlers from handlers/ registered")
            except ImportError:
                logger.warning("⚠️ handlers/ package not available")
            except Exception as e:
                logger.error(f"❌ Error registering handlers: {e}")
            
            # Основні команди (залишаються тут для стабільності)
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message):
                try:
                    # Реєстрація користувача в БД (якщо доступна)
                    if self.db_available:
                        from database.services import get_or_create_user
                        user_data = get_or_create_user(
                            user_id=message.from_user.id,
                            username=message.from_user.username,
                            first_name=message.from_user.first_name,
                            last_name=message.from_user.last_name
                        )
                        
                        if user_data:
                            logger.info(f"User registered/updated: {message.from_user.id}")
                    
                    # Підготовка тексту з інформацією про новий контент
                    if self.settings:
                        from config.settings import TEXTS
                        text = TEXTS['start_message']
                    else:
                        text = (
                            f"🧠😂🔥 <b>Привіт! Я професійний україномовний бот!</b>\n\n"
                            f"🎭 <b>Новий контент доступний:</b>\n"
                            f"😂 /meme - випадкові меми\n"
                            f"🤣 /joke - смішні жарти\n"
                            f"🧠 /anekdot - українські анекдоти\n\n"
                            f"📝 <b>Можете подавати свій контент через кнопки!</b>\n\n"
                            f"{'💾 База даних: підключена' if self.db_available else '⚠️ База даних: недоступна'}\n\n"
                            f"⚡ <b>Всі команди:</b>\n"
                            f"/start - запуск\n/status - статус\n/profile - профіль\n"
                            f"/meme - мем\n/joke - жарт\n/anekdot - анекдот"
                        )
                    
                    # Створення розширеної клавіатури з контентом
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="😂 Мем", callback_data="get_meme"),
                            InlineKeyboardButton(text="🤣 Жарт", callback_data="get_joke"),
                            InlineKeyboardButton(text="🧠 Анекдот", callback_data="get_anekdot")
                        ],
                        [
                            InlineKeyboardButton(text="👤 Мій профіль", callback_data="profile"),
                            InlineKeyboardButton(text="🏆 Топ користувачів", callback_data="top")
                        ],
                        [
                            InlineKeyboardButton(text="📝 Подати мем", callback_data="submit_demo_meme"),
                            InlineKeyboardButton(text="📝 Подати жарт", callback_data="submit_demo_joke")
                        ],
                        [
                            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
                            InlineKeyboardButton(text="❓ Допомога", callback_data="help")
                        ]
                    ])
                    
                    await message.answer(text, reply_markup=keyboard)
                    
                except Exception as e:
                    logger.error(f"Error in start handler: {e}")
                    await message.answer("🧠😂🔥 <b>Бот працює!</b>\n\nВикористовуйте /status для перевірки стану.")
            
            @self.dp.message(Command("status"))
            async def cmd_status(message: Message):
                uptime = datetime.now() - self.startup_time
                
                status_text = f"✅ <b>Статус бота</b>\n\n"
                status_text += f"⏱ Час роботи: {uptime}\n"
                status_text += f"🗓 Запущено: {self.startup_time.strftime('%H:%M:%S %d.%m.%Y')}\n"
                
                if self.settings:
                    status_text += f"⚙️ Конфігурація: повна\n"
                    status_text += f"💾 База даних: {'✅ активна' if self.db_available else '❌ недоступна'}\n"
                    status_text += f"🎭 Контент: меми, жарти, анекдоти\n"
                    status_text += f"🔧 Режим: професійний з контентом\n"
                else:
                    status_text += f"⚙️ Конфігурація: базова\n"
                    status_text += f"🔧 Режим: мінімальний\n"
                
                await message.answer(status_text)
            
            # Інші основні команди (profile, stats, help) залишаються без змін...
            @self.dp.message(Command("profile"))
            async def cmd_profile(message: Message):
                if not self.db_available:
                    await message.answer("❌ База даних недоступна")
                    return
                
                try:
                    from database.services import get_user_stats
                    
                    user_stats = get_user_stats(message.from_user.id)
                    if user_stats:
                        profile_text = f"👤 <b>Ваш профіль</b>\n\n"
                        profile_text += f"🆔 ID: {user_stats['user_id']}\n"
                        profile_text += f"⭐ Бали: {user_stats['points']}\n"
                        profile_text += f"👑 Ранг: {user_stats['rank']}\n"
                        profile_text += f"📅 Реєстрація: {user_stats['created_at'].strftime('%d.%m.%Y')}\n"
                        profile_text += f"🕐 Остання активність: {user_stats['last_activity'].strftime('%d.%m.%Y %H:%M')}\n\n"
                        profile_text += f"📊 <b>Статистика:</b>\n"
                        profile_text += f"👀 Переглядів: {user_stats['total_views']}\n"
                        profile_text += f"👍 Лайків: {user_stats['total_likes']}\n"
                        profile_text += f"📝 Подань: {user_stats['total_submissions']}\n"
                        profile_text += f"✅ Схвалень: {user_stats['total_approvals']}\n"
                        profile_text += f"⚔️ Дуелей: {user_stats['total_duels']}"
                        
                        await message.answer(profile_text)
                    else:
                        await message.answer("❌ Профіль не знайдено")
                        
                except Exception as e:
                    logger.error(f"Profile error: {e}")
                    await message.answer("❌ Помилка отримання профілю")
            
            @self.dp.message(Command("stats"))
            async def cmd_stats(message: Message):
                if not self.db_available:
                    await message.answer("❌ База даних недоступна")
                    return
                
                try:
                    from database.services import get_basic_stats
                    
                    stats = get_basic_stats()
                    stats_text = f"📊 <b>Статистика бота</b>\n\n"
                    stats_text += f"👥 Користувачів: {stats['total_users']}\n"
                    stats_text += f"📝 Контенту: {stats['total_content']}\n"
                    stats_text += f"✅ Схвалено: {stats['approved_content']}\n"
                    stats_text += f"⏳ На розгляді: {stats['pending_content']}\n"
                    stats_text += f"⚔️ Дуелей: {stats['total_duels']}"
                    
                    await message.answer(stats_text)
                    
                except Exception as e:
                    logger.error(f"Stats error: {e}")
                    await message.answer("❌ Помилка отримання статистики")
            
            @self.dp.message(Command("help"))
            async def cmd_help(message: Message):
                try:
                    help_text = (
                        "📖 <b>Довідка по командах</b>\n\n"
                        "🎭 <b>Контент:</b>\n"
                        "/meme - випадковий мем\n"
                        "/joke - смішний жарт\n"
                        "/anekdot - український анекдот\n\n"
                        "👤 <b>Профіль:</b>\n"
                        "/profile - ваш профіль\n"
                        "/stats - статистика бота\n\n"
                        "⚙️ <b>Система:</b>\n"
                        "/start - перезапуск\n"
                        "/status - статус бота\n"
                        "/help - ця довідка\n\n"
                        "📝 <b>Подача контенту через кнопки в меню!</b>"
                    )
                    
                    await message.answer(help_text)
                except Exception as e:
                    logger.error(f"Error in help handler: {e}")
                    await message.answer("📖 <b>Довідка</b>\n\nБазові команди: /start, /status, /profile, /stats, /help")
            
            # Callback handlers з інтеграцією контенту
            @self.dp.callback_query()
            async def handle_main_callbacks(callback):
                """Основні callback'и (не контентні, які обробляються в content_handlers)"""
                try:
                    data = callback.data
                    
                    # Перевіряємо чи це не контентний callback (вони обробляються в content_handlers)
                    if any(data.startswith(prefix) for prefix in ["like_", "dislike_", "more_", "submit_"]):
                        return  # Нехай обробляє content_handlers
                    
                    if data == "get_meme":
                        # Викликаємо обробник мемів
                        from handlers.content_handlers import handle_meme_command
                        await handle_meme_command(callback.message)
                        await callback.answer()
                        
                    elif data == "get_joke":
                        # Викликаємо обробник жартів
                        from handlers.content_handlers import handle_joke_command
                        await handle_joke_command(callback.message)
                        await callback.answer()
                        
                    elif data == "get_anekdot":
                        # Викликаємо обробник анекдотів
                        from handlers.content_handlers import handle_anekdot_command
                        await handle_anekdot_command(callback.message)
                        await callback.answer()
                    
                    elif data == "profile":
                        if self.db_available:
                            from database.services import get_user_stats
                            user_stats = get_user_stats(callback.from_user.id)
                            if user_stats:
                                await callback.message.answer(f"👤 <b>Ваш профіль:</b>\n⭐ Бали: {user_stats['points']}\n👑 Ранг: {user_stats['rank']}")
                            else:
                                await callback.message.answer("❌ Профіль не знайдено")
                        else:
                            await callback.message.answer("❌ База даних недоступна")
                        await callback.answer()
                        
                    elif data == "stats":
                        if self.db_available:
                            from database.services import get_basic_stats
                            stats = get_basic_stats()
                            await callback.message.answer(f"📊 <b>Статистика:</b>\n👥 Користувачів: {stats['total_users']}\n📝 Контенту: {stats['total_content']}")
                        else:
                            await callback.message.answer("❌ База даних недоступна")
                        await callback.answer()
                        
                    elif data == "top":
                        if self.db_available:
                            from database.services import get_top_users
                            top_users = get_top_users(5)
                            if top_users:
                                top_text = "🏆 <b>Топ користувачів:</b>\n\n"
                                for i, user in enumerate(top_users, 1):
                                    name = user['first_name'] or user['username'] or f"User{user['user_id']}"
                                    top_text += f"{i}. {name} - {user['points']} балів\n"
                                await callback.message.answer(top_text)
                            else:
                                await callback.message.answer("👥 Поки що немає користувачів в рейтингу")
                        else:
                            await callback.message.answer("❌ База даних недоступна")
                        await callback.answer()
                        
                    elif data == "help":
                        await callback.message.answer(
                            "📖 <b>Допомога</b>\n\n"
                            "🎭 Використовуйте кнопки для отримання контенту!\n"
                            "📝 Подавайте свій контент через відповідні кнопки\n"
                            "⭐ Заробляйте бали за активність\n"
                            "🏆 Змагайтеся в рейтингу!\n\n"
                            "Всі функції працюють та постійно розширюються!"
                        )
                        await callback.answer()
                    else:
                        await callback.answer("🚧 Функція в розробці!")
                        
                except Exception as e:
                    logger.error(f"Main callback error: {e}")
                    await callback.answer("❌ Помилка обробки!")
            
            logger.info("✅ Enhanced handlers with content system registered")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers setup error: {e}")
            return False
    
    async def main(self):
        logger.info("🚀 Starting Enhanced Ukrainian Telegram Bot with Content System...")
        
        try:
            # Load settings
            settings = self.load_settings()
            
            if not self.validate_settings(settings):
                return False
            
            # Initialize database
            await self.init_database(settings['database_url'])
            
            # Create bot
            if not await self.create_bot(settings):
                return False
            
            # Setup handlers
            if not await self.setup_handlers():
                return False
            
            # Notify admin
            if settings.get('admin_id') and self.bot:
                try:
                    mode = "професійному з контентом" if self.settings else "базовому"
                    db_status = "підключена" if self.db_available else "недоступна"
                    
                    await self.bot.send_message(
                        settings['admin_id'],
                        f"✅ <b>Бот запущено в {mode} режимі!</b>\n\n"
                        f"🕐 Час: {datetime.now().strftime('%H:%M:%S')}\n"
                        f"⚙️ Налаштування: {'повні' if self.settings else 'базові'}\n"
                        f"💾 База даних: {db_status}\n\n"
                        f"🎭 <b>Новий контент:</b>\n"
                        f"😂 Меми (/meme)\n"
                        f"🤣 Жарти (/joke)\n"
                        f"🧠 Анекдоти (/anekdot)\n"
                        f"📝 Подача контенту через кнопки\n"
                        f"⭐ Система балів за активність"
                    )
                except Exception as e:
                    logger.warning(f"Could not notify admin: {e}")
            
            logger.info("🎯 Starting polling with content system...")
            await self.dp.start_polling(self.bot, skip_updates=True)
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Critical error: {e}")
            return False
        finally:
            if self.bot:
                await self.bot.session.close()

async def main():
    bot = UkrainianTelegramBot()
    try:
        result = await bot.main()
        return result
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user")
        return True
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)