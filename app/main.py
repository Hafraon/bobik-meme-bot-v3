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
    
    def is_admin(self, user_id: int) -> bool:
        """Перевірка чи є користувач адміністратором"""
        try:
            if self.settings:
                return self.settings.is_admin(user_id)
            else:
                admin_id = int(os.getenv('ADMIN_ID', 0))
                return user_id == admin_id
        except:
            return False
    
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
        """Налаштування всіх хендлерів включно з контентом та адміном"""
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
            
            # Основні команди з адмін підтримкою
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message):
                try:
                    user_id = message.from_user.id
                    is_admin = self.is_admin(user_id)
                    
                    # Реєстрація користувача в БД (якщо доступна)
                    if self.db_available:
                        from database.services import get_or_create_user
                        user_data = get_or_create_user(
                            user_id=user_id,
                            username=message.from_user.username,
                            first_name=message.from_user.first_name,
                            last_name=message.from_user.last_name
                        )
                        
                        if user_data:
                            logger.info(f"User registered/updated: {user_id} (Admin: {is_admin})")
                    
                    # Підготовка тексту з адмін інформацією
                    if self.settings:
                        from config.settings import TEXTS
                        text = TEXTS['start_message']
                        if is_admin:
                            text += f"\n\n🛡️ <b>АДМІН РЕЖИМ АКТИВНИЙ</b>\n📊 Доступні адмін команди"
                    else:
                        text = (
                            f"🧠😂🔥 <b>Привіт! Я професійний україномовний бот!</b>\n\n"
                            f"🎭 <b>Контент доступний:</b>\n"
                            f"😂 /meme - випадкові меми\n"
                            f"🤣 /joke - смішні жарти\n"
                            f"🧠 /anekdot - українські анекдоти\n\n"
                            f"📝 <b>Подавайте свій контент через кнопки!</b>\n\n"
                            f"{'💾 База даних: підключена' if self.db_available else '⚠️ База даних: недоступна'}\n"
                        )
                        
                        if is_admin:
                            text += (
                                f"\n🛡️ <b>АДМІН ФУНКЦІЇ:</b>\n"
                                f"/admin_stats - статистика\n"
                                f"/moderate - модерація\n"
                                f"/pending - контент на розгляді\n"
                                f"/approve_ID - швидке схвалення\n"
                                f"/reject_ID - швидке відхилення"
                            )
                    
                    # Створення клавіатури (різна для адміна та користувачів)
                    if is_admin:
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
                                InlineKeyboardButton(text="📊 Адмін статистика", callback_data="admin_stats"),
                                InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderate")
                            ],
                            [
                                InlineKeyboardButton(text="📋 На розгляді", callback_data="admin_pending"),
                                InlineKeyboardButton(text="👥 Адмін топ", callback_data="admin_top_users")
                            ],
                            [
                                InlineKeyboardButton(text="📝 Подати мем", callback_data="submit_demo_meme"),
                                InlineKeyboardButton(text="❓ Допомога", callback_data="help")
                            ]
                        ])
                    else:
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
                is_admin = self.is_admin(message.from_user.id)
                
                status_text = f"✅ <b>Статус бота</b>\n\n"
                status_text += f"⏱ Час роботи: {uptime}\n"
                status_text += f"🗓 Запущено: {self.startup_time.strftime('%H:%M:%S %d.%m.%Y')}\n"
                
                if self.settings:
                    status_text += f"⚙️ Конфігурація: повна\n"
                    status_text += f"💾 База даних: {'✅ активна' if self.db_available else '❌ недоступна'}\n"
                    status_text += f"🎭 Контент: меми, жарти, анекдоти\n"
                    status_text += f"🛡️ Модерація: активна\n"
                    status_text += f"🔧 Режим: професійний з модерацією\n"
                else:
                    status_text += f"⚙️ Конфігурація: базова\n"
                    status_text += f"🔧 Режим: мінімальний\n"
                
                if is_admin:
                    status_text += f"\n👑 <b>Адмін статус: активний</b>"
                
                await message.answer(status_text)
            
            # Інші основні команди залишаються без змін...
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
                        
                        if self.is_admin(message.from_user.id):
                            profile_text += f"\n\n👑 <b>Статус: Адміністратор</b>"
                        
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
                    
                    # Додаткова інформація для адміна
                    if self.is_admin(message.from_user.id):
                        stats_text += f"\n\n🛡️ <b>Адмін команди:</b>\n/admin_stats - детальна статистика\n/moderate - почати модерацію"
                    
                    await message.answer(stats_text)
                    
                except Exception as e:
                    logger.error(f"Stats error: {e}")
                    await message.answer("❌ Помилка отримання статистики")
            
            @self.dp.message(Command("help"))
            async def cmd_help(message: Message):
                try:
                    is_admin = self.is_admin(message.from_user.id)
                    
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
                    
                    if is_admin:
                        help_text += (
                            f"\n\n🛡️ <b>АДМІН КОМАНДИ:</b>\n"
                            f"/admin_stats - детальна статистика\n"
                            f"/moderate - почати модерацію\n"
                            f"/pending - контент на розгляді\n"
                            f"/approve_ID - швидке схвалення\n"
                            f"/reject_ID [причина] - відхилення\n\n"
                            f"💡 <b>Приклади:</b>\n"
                            f"/approve_5 - схвалити контент ID 5\n"
                            f"/reject_3 Неприйнятний контент"
                        )
                    
                    await message.answer(help_text)
                except Exception as e:
                    logger.error(f"Error in help handler: {e}")
                    await message.answer("📖 <b>Довідка</b>\n\nБазові команди: /start, /status, /profile, /stats, /help")
            
            # Розширені callback handlers з адмін підтримкою
            @self.dp.callback_query()
            async def handle_main_callbacks(callback):
                """Основні callback'и з адмін підтримкою"""
                try:
                    data = callback.data
                    user_id = callback.from_user.id
                    is_admin = self.is_admin(user_id)
                    
                    # Перевіряємо чи це не спеціалізований callback
                    if any(data.startswith(prefix) for prefix in ["like_", "dislike_", "more_", "submit_", "admin_", "moderate_"]):
                        return  # Нехай обробляють спеціалізовані хендлери
                    
                    if data == "get_meme":
                        from handlers.content_handlers import handle_meme_command
                        await handle_meme_command(callback.message)
                        await callback.answer()
                        
                    elif data == "get_joke":
                        from handlers.content_handlers import handle_joke_command
                        await handle_joke_command(callback.message)
                        await callback.answer()
                        
                    elif data == "get_anekdot":
                        from handlers.content_handlers import handle_anekdot_command
                        await handle_anekdot_command(callback.message)
                        await callback.answer()
                    
                    elif data == "profile":
                        if self.db_available:
                            from database.services import get_user_stats
                            user_stats = get_user_stats(user_id)
                            if user_stats:
                                profile_msg = f"👤 <b>Ваш профіль:</b>\n⭐ Бали: {user_stats['points']}\n👑 Ранг: {user_stats['rank']}"
                                if is_admin:
                                    profile_msg += f"\n👑 Статус: Адміністратор"
                                await callback.message.answer(profile_msg)
                            else:
                                await callback.message.answer("❌ Профіль не знайдено")
                        else:
                            await callback.message.answer("❌ База даних недоступна")
                        await callback.answer()
                        
                    elif data == "stats":
                        if self.db_available:
                            from database.services import get_basic_stats
                            stats = get_basic_stats()
                            stats_msg = f"📊 <b>Статистика:</b>\n👥 Користувачів: {stats['total_users']}\n📝 Контенту: {stats['total_content']}"
                            if is_admin:
                                stats_msg += f"\n⏳ На модерації: {stats['pending_content']}"
                            await callback.message.answer(stats_msg)
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
                        help_msg = (
                            "📖 <b>Допомога</b>\n\n"
                            "🎭 Використовуйте кнопки для отримання контенту!\n"
                            "📝 Подавайте свій контент через відповідні кнопки\n"
                            "⭐ Заробляйте бали за активність\n"
                            "🏆 Змагайтеся в рейтингу!"
                        )
                        if is_admin:
                            help_msg += f"\n\n🛡️ Ви маєте адмін права!\nВикористовуйте адмін кнопки для модерації."
                        await callback.message.answer(help_msg)
                        await callback.answer()
                    else:
                        await callback.answer("🚧 Функція в розробці!")
                        
                except Exception as e:
                    logger.error(f"Main callback error: {e}")
                    await callback.answer("❌ Помилка обробки!")
            
            logger.info("✅ Enhanced handlers with admin integration registered")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers setup error: {e}")
            return False
    
    async def main(self):
        logger.info("🚀 Starting Enhanced Ukrainian Telegram Bot with Admin System...")
        
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
                    mode = "професійному з модерацією" if self.settings else "базовому"
                    db_status = "підключена" if self.db_available else "недоступна"
                    
                    await self.bot.send_message(
                        settings['admin_id'],
                        f"✅ <b>Бот запущено в {mode} режимі!</b>\n\n"
                        f"🕐 Час: {datetime.now().strftime('%H:%M:%S')}\n"
                        f"⚙️ Налаштування: {'повні' if self.settings else 'базові'}\n"
                        f"💾 База даних: {db_status}\n\n"
                        f"🎭 <b>Контент система:</b>\n"
                        f"😂 Меми (/meme)\n"
                        f"🤣 Жарти (/joke)\n"
                        f"🧠 Анекдоти (/anekdot)\n"
                        f"📝 Подача контенту через кнопки\n\n"
                        f"🛡️ <b>Адмін функції:</b>\n"
                        f"/admin_stats - детальна статистика\n"
                        f"/moderate - модерація контенту\n"
                        f"/pending - контент на розгляді\n"
                        f"/approve_ID - швидке схвалення\n"
                        f"/reject_ID - швидке відхилення\n\n"
                        f"⭐ Система балів та модерація активні!"
                    )
                except Exception as e:
                    logger.warning(f"Could not notify admin: {e}")
            
            logger.info("🎯 Starting polling with admin system...")
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