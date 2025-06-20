#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM-БОТ З ПОВНОЮ АВТОМАТИЗАЦІЄЮ 🤖

КРОК 6: АВТОМАТИЗАЦІЯ ТА РОЗУМНІ РОЗСИЛКИ
⚡ Автоматичні щоденні розсилки контенту
🤖 Розумний планувальник завдань
📊 Автоматична статистика та звіти
🏆 Автоматичні турніри та події
🧹 Самоочищення та оптимізація
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

class AutomatedUkrainianTelegramBot:
    """Україномовний бот з повною автоматизацією"""
    
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
        """Ініціалізація бота"""
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
        """Ініціалізація бази даних"""
        try:
            logger.info("💾 Ініціалізація БД...")
            
            from database.database import init_database
            success = await init_database()
            
            if success:
                logger.info("✅ Database initialized successfully")
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

    async def initialize_automation(self):
        """Ініціалізація системи автоматизації"""
        try:
            logger.info("🤖 Ініціалізація системи автоматизації...")
            
            # Створення автоматизованого планувальника
            from services.automated_scheduler import create_automated_scheduler
            self.scheduler = await create_automated_scheduler(self.bot)
            
            if self.scheduler:
                logger.info("✅ Automated scheduler створено")
                
                # Запуск планувальника
                await self.scheduler.start()
                self.automation_active = True
                
                # Отримуємо broadcast system з планувальника
                self.broadcast_system = self.scheduler.broadcast_system
                
                logger.info("🤖 Повна автоматизація активна!")
                return True
            else:
                logger.warning("⚠️ Не вдалося створити планувальник")
                return False
                
        except ImportError as e:
            logger.warning(f"⚠️ Automation services not available: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Automation initialization error: {e}")
            return False

    async def register_handlers(self):
        """Реєстрація всіх хендлерів з автоматизацією"""
        try:
            logger.info("🔧 Реєстрація хендлерів з автоматизацією...")
            
            # Реєстрація через handlers/__init__.py
            from handlers import register_handlers
            self.handlers_status = register_handlers(self.dp)
            
            # Додаткові основні хендлери з автоматизацією
            await self.register_automation_handlers()
            
            # Callback хендлер з підтримкою автоматизації
            await self.register_enhanced_callbacks()
            
            logger.info("✅ All handlers registered with automation support")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers registration failed: {e}")
            return False

    async def register_automation_handlers(self):
        """Хендлери з підтримкою автоматизації"""
        from aiogram import F
        from aiogram.filters import Command
        from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
        
        @self.dp.message(Command("start"))
        async def automated_start(message: Message):
            """Розширена команда /start з автоматизацією"""
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
                
                # Текст привітання з автоматизацією
                text = "🤖 <b>ПРОФЕСІЙНИЙ БОТ З АВТОМАТИЗАЦІЄЮ!</b> 🤖\n\n"
                
                if is_admin:
                    text += "👑 <b>Адмін режим + Автоматизація</b>\n\n"
                
                text += (
                    "🎯 <b>НОВИНКА: ПОВНА АВТОМАТИЗАЦІЯ!</b> ⚡\n"
                    "Бот тепер працює самостійно 24/7!\n\n"
                    "🤖 <b>Автоматичні функції:</b>\n"
                    "• 📢 Щоденні розсилки контенту\n"
                    "• ⚔️ Автоматичні дуелі та турніри\n"
                    "• 📊 Розумна статистика\n"
                    "• 🏆 Автоматичні нагороди\n"
                    "• 🧹 Самоочищення системи\n\n"
                    "😂 <b>Основний функціонал:</b>\n"
                    "• Меми, жарти, анекдоти\n"
                    "• Дуелі з голосуванням\n"
                    "• Система рангів та балів"
                )
                
                # Створення клавіатури з автоматизацією
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
                
                # Адмін кнопки з автоматизацією
                if is_admin:
                    keyboard_rows.extend([
                        [
                            InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderate"),
                            InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")
                        ],
                        [
                            InlineKeyboardButton(text="🤖 Автоматизація", callback_data="automation_status"),
                            InlineKeyboardButton(text="📢 Розсилки", callback_data="broadcast_control")
                        ]
                    ])
                
                keyboard_rows.append([
                    InlineKeyboardButton(text="❓ Допомога", callback_data="help")
                ])
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
                
                await message.answer(text, reply_markup=keyboard)
                
                # Повідомлення адміну про запуск з автоматизацією
                if is_admin and self.automation_active:
                    try:
                        from config.settings import settings
                        uptime = datetime.now() - self.startup_time
                        
                        # Статус автоматизації
                        automation_status = self.scheduler.get_scheduler_status() if self.scheduler else {}
                        
                        admin_text = (
                            f"🤖 <b>БОТ ЗАПУЩЕНО З ПОВНОЮ АВТОМАТИЗАЦІЄЮ!</b>\n\n"
                            f"⚡ <b>Система автоматизації:</b> {'Активна' if self.automation_active else 'Неактивна'}\n"
                            f"💾 <b>База даних:</b> {'Підключена' if self.db_available else 'Fallback'}\n"
                            f"🔧 <b>Хендлери:</b> {self.handlers_status.get('total_registered', 0)}/4\n"
                            f"📅 <b>Завдань у черзі:</b> {automation_status.get('total_jobs', 0)}\n"
                            f"⏰ <b>Uptime:</b> {uptime.total_seconds():.1f}с\n\n"
                            f"🎯 <b>Автоматичні функції:</b>\n"
                            f"• Щоденні розсилки контенту (9:00)\n"
                            f"• Вечірня статистика (20:00)\n"
                            f"• Автоматичне завершення дуелей\n"
                            f"• Нагадування про активні дуелі\n"
                            f"• Тижневі турніри (п'ятниця)\n"
                            f"• Місячні підсумки\n"
                            f"• Автоматична очистка даних\n\n"
                            f"🚀 Бот працює повністю автономно!"
                        )
                        
                        await self.bot.send_message(settings.ADMIN_ID, admin_text)
                    except Exception as e:
                        logger.error(f"Error sending admin notification: {e}")
                
            except Exception as e:
                logger.error(f"Error in automated start handler: {e}")
                await message.answer("🤖 Бот запущено з автоматизацією! Використовуйте /help для довідки.")

        @self.dp.message(Command("help"))
        async def automated_help(message: Message):
            """Розширена довідка з автоматизацією"""
            try:
                text = (
                    "📖 <b>ДОВІДКА - БОТ З АВТОМАТИЗАЦІЄЮ</b>\n\n"
                    
                    "🤖 <b>АВТОМАТИЗАЦІЯ (НОВИНКА!):</b>\n"
                    "• Бот працює самостійно 24/7\n"
                    "• Щоденні розсилки контенту\n"
                    "• Автоматичні турніри та події\n"
                    "• Розумна статистика\n"
                    "• Самоочищення системи\n\n"
                    
                    "⚔️ <b>ДУЕЛІ ЖАРТІВ:</b>\n"
                    "• /duel - головне меню дуелів\n"
                    "• Автоматичне завершення дуелей\n"
                    "• Нагадування про активні змагання\n"
                    "• Автоматичні турніри\n\n"
                    
                    "😂 <b>КОНТЕНТ:</b>\n"
                    "• /meme - випадковий мем\n"
                    "• /joke - смішний жарт\n"
                    "• /anekdot - український анекдот\n"
                    "• Щоденний кращий контент\n\n"
                    
                    "👤 <b>ПРОФІЛЬ:</b>\n"
                    "• /profile - ваша статистика\n"
                    "• Автоматичні нагороди\n"
                    "• Повідомлення про досягнення\n"
                    "• Підвищення рангів\n\n"
                    
                    "🎮 <b>СИСТЕМА БАЛІВ:</b>\n"
                    "• +2 бали за голосування в дуелі\n"
                    "• +10 балів за участь у дуелі\n"
                    "• +25 балів за перемогу\n"
                    "• +50 балів за розгромну перемогу\n"
                    "• Бонуси за турніри та досягнення\n\n"
                    
                    "📅 <b>АВТОМАТИЧНИЙ РОЗКЛАД:</b>\n"
                    "• 9:00 - ранкова розсилка\n"
                    "• 20:00 - вечірня статистика\n"
                    "• П'ятниця 19:00 - тижневий турнір\n"
                    "• Неділя 18:00 - тижневий дайджест\n"
                    "• 1 число - місячні підсумки"
                )
                
                # Адмін команди
                if self.is_admin(message.from_user.id):
                    text += (
                        "\n\n🛡️ <b>АДМІН КОМАНДИ:</b>\n"
                        "• /admin_stats - детальна статистика\n"
                        "• /moderate - модерація контенту\n"
                        "• /automation_status - статус автоматизації\n"
                        "• /broadcast_now - ручна розсилка\n"
                        "• /scheduler_info - інформація планувальника"
                    )
                
                await message.answer(text)
                
            except Exception as e:
                logger.error(f"Error in automated help handler: {e}")
                await message.answer("📖 <b>Довідка</b>\n\nОсновні команди: /start, /duel, /profile, /help")

        # Спеціальні команди автоматизації для адміна
        @self.dp.message(Command("automation_status"))
        async def automation_status_command(message: Message):
            """Статус автоматизації (тільки для адміна)"""
            if not self.is_admin(message.from_user.id):
                await message.answer("❌ Доступ заборонено")
                return
                
            try:
                if self.scheduler:
                    status = self.scheduler.get_scheduler_status()
                    
                    text = (
                        f"🤖 <b>СТАТУС АВТОМАТИЗАЦІЇ</b>\n\n"
                        f"✅ Планувальник: {'Активний' if status['is_running'] else 'Неактивний'}\n"
                        f"📅 Завдань: {status['total_jobs']}\n"
                        f"⏰ Наступне: {status['next_job']}\n\n"
                        f"📊 <b>Статистика:</b>\n"
                        f"🎯 Виконано завдань: {status['stats']['jobs_executed']}\n"
                        f"📢 Розсилок: {status['stats']['broadcasts_sent']}\n"
                        f"🏁 Завершено дуелей: {status['stats']['duels_finished']}\n"
                        f"🧹 Очищено даних: {status['stats']['data_cleaned']}\n"
                        f"❌ Помилок: {status['stats']['errors']}\n\n"
                        f"⏱️ Остання активність: {status['stats'].get('last_activity', 'Невідомо')}"
                    )
                else:
                    text = "❌ Планувальник не ініціалізований"
                
                await message.answer(text)
                
            except Exception as e:
                logger.error(f"Error in automation status: {e}")
                await message.answer(f"❌ Помилка отримання статусу: {e}")

        @self.dp.message(Command("broadcast_now"))
        async def manual_broadcast(message: Message):
            """Ручна розсилка (тільки для адміна)"""
            if not self.is_admin(message.from_user.id):
                await message.answer("❌ Доступ заборонено")
                return
                
            try:
                if self.broadcast_system:
                    await message.answer("📢 Запуск ручної розсилки...")
                    await self.broadcast_system.send_daily_content()
                    await message.answer("✅ Розсилка завершена")
                else:
                    await message.answer("❌ Система розсилок недоступна")
                    
            except Exception as e:
                logger.error(f"Error in manual broadcast: {e}")
                await message.answer(f"❌ Помилка розсилки: {e}")

    async def register_enhanced_callbacks(self):
        """Розширені callback хендлери з автоматизацією"""
        
        @self.dp.callback_query()
        async def handle_automated_callbacks(callback):
            """Головний callback хендлер з автоматизацією"""
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
                
                # Нові callback'и автоматизації
                if data == "automation_status" and is_admin:
                    if self.scheduler:
                        status = self.scheduler.get_scheduler_status()
                        text = (
                            f"🤖 <b>СТАТУС АВТОМАТИЗАЦІЇ</b>\n\n"
                            f"⚡ Планувальник: {'Активний' if status['is_running'] else 'Неактивний'}\n"
                            f"📅 Завдань: {status['total_jobs']}\n"
                            f"⏰ Наступне: {status['next_job']}\n"
                            f"🎯 Виконано: {status['stats']['jobs_executed']}\n"
                            f"📢 Розсилок: {status['stats']['broadcasts_sent']}\n"
                            f"❌ Помилок: {status['stats']['errors']}"
                        )
                    else:
                        text = "❌ Планувальник не ініціалізований"
                    
                    await callback.message.edit_text(text)
                    await callback.answer()
                    
                elif data == "broadcast_control" and is_admin:
                    text = (
                        f"📢 <b>УПРАВЛІННЯ РОЗСИЛКАМИ</b>\n\n"
                        f"🤖 Автоматичні розсилки:\n"
                        f"• 9:00 - ранковий контент\n"
                        f"• 20:00 - вечірня статистика\n"
                        f"• Неділя 18:00 - тижневий дайджест\n\n"
                        f"⚡ Статус: {'Активні' if self.automation_active else 'Неактивні'}\n\n"
                        f"💡 Використовуйте /broadcast_now для ручної розсилки"
                    )
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="📊 Статистика розсилок", callback_data="broadcast_stats")],
                        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")]
                    ])
                    
                    await callback.message.edit_text(text, reply_markup=keyboard)
                    await callback.answer()
                
                # Основні callback'и (як раніше, але з автоматизацією)
                elif data == "get_meme":
                    try:
                        from handlers.content_handlers import handle_meme_command
                        await handle_meme_command(callback.message)
                        await callback.answer("😂 Мем завантажено!")
                    except ImportError:
                        await callback.message.answer("😂 <i>Коли твій код працює з першого разу...\nЗначить щось пішло не так! 🤔</i>")
                        await callback.answer()
                
                elif data == "duel_menu":
                    try:
                        from handlers.duel_handlers import cmd_duel
                        await cmd_duel(callback.message)
                        await callback.answer("⚔️ Дуелі жартів!")
                    except ImportError:
                        await callback.message.edit_text(
                            "⚔️ <b>ДУЕЛІ ЖАРТІВ</b>\n\n"
                            "🤖 Автоматичні дуелі та турніри!\n"
                            "Система тимчасово завантажується..."
                        )
                        await callback.answer("Завантаження...")
                
                elif data == "profile":
                    # Розширений профіль з автоматизацією
                    if self.db_available:
                        try:
                            from database.services import get_user_by_id, get_user_duel_stats
                            
                            user = await get_user_by_id(user_id)
                            duel_stats = await get_user_duel_stats(user_id)
                            
                            if user:
                                # Визначаємо ранг
                                points = user.get('total_points', 0)
                                rank = self.get_rank_by_points(points)
                                
                                text = f"👤 <b>ПРОФІЛЬ З АВТОМАТИЗАЦІЄЮ</b>\n\n"
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
                                else:
                                    text += "⚔️ <b>Ще не брали участь у дуелях</b>\n"
                                    text += "🤖 Автоматичні турніри щоп'ятниці!"
                                
                                # Інформація про автоматизацію
                                text += f"\n🤖 <b>АВТОМАТИЗАЦІЯ:</b>\n"
                                text += f"📢 Щоденні розсилки активні\n"
                                text += f"🏆 Автоматичні турніри\n"
                                text += f"⭐ Повідомлення про досягнення"
                                
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
                            "🤖 Автоматизація активна!\n"
                            "📢 Щоденні розсилки\n"
                            "🏆 Автоматичні турніри"
                        )
                    
                    await callback.answer()
                
                else:
                    await callback.answer("🔄 Функція завантажується...")
                    
            except Exception as e:
                logger.error(f"Error in automated callback handler: {e}")
                await callback.answer("❌ Помилка обробки")

    def get_rank_by_points(self, points: int) -> str:
        """Визначення рангу за балами"""
        if points >= 5000:
            return "🚀 Гумористичний Геній"
        elif points >= 3000:
            return "🌟 Легенда Мемів"
        elif points >= 1500:
            return "🏆 Король Гумору"
        elif points >= 750:
            return "👑 Мастер Рофлу"
        elif points >= 350:
            return "🎭 Комік"
        elif points >= 150:
            return "😂 Гуморист"
        elif points >= 50:
            return "😄 Сміхун"
        else:
            return "🤡 Новачок"

    async def main(self):
        """Головна функція запуску бота з автоматизацією"""
        logger.info("🤖 Starting Automated Ukrainian Telegram Bot...")
        
        try:
            # Ініціалізація компонентів
            if not await self.initialize_bot():
                return False
            
            if not await self.initialize_database():
                logger.warning("⚠️ Working without full database support")
            
            # Ініціалізація автоматизації (ключова новинка!)
            automation_success = await self.initialize_automation()
            if automation_success:
                logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА - бот працює самостійно!")
            else:
                logger.warning("⚠️ Working without automation")
            
            if not await self.register_handlers():
                return False
            
            # Налаштування graceful shutdown
            def signal_handler():
                logger.info("📶 Shutdown signal received")
                self.shutdown_event.set()
            
            signal.signal(signal.SIGINT, lambda s, f: signal_handler())
            signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
            
            logger.info("✅ Bot fully initialized with complete automation")
            
            # Запуск polling з graceful shutdown
            try:
                polling_task = asyncio.create_task(self.dp.start_polling(self.bot))
                shutdown_task = asyncio.create_task(self.shutdown_event.wait())
                
                logger.info("🎯 Bot started - Full automation active!")
                
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
                if self.scheduler:
                    await self.scheduler.stop()
                    logger.info("✅ Automated scheduler stopped")
                
                await self.bot.session.close()
                logger.info("✅ Bot session closed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Critical error in main: {e}")
            return False

# ===== ЗАПУСК =====

async def main():
    """Точка входу"""
    bot = AutomatedUkrainianTelegramBot()
    success = await bot.main()
    return success

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Automated bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)