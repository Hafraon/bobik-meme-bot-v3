#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ГОЛОВНИЙ ФАЙЛ УКРАЇНОМОВНОГО БОТА - ОСТАТОЧНО ВИПРАВЛЕНИЙ 🚀
"""

import asyncio
import logging
import sys
from typing import Optional, List, Dict, Any, Union

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class AutomatedUkrainianTelegramBot:
    """🤖 УКРАЇНОМОВНИЙ ТЕЛЕГРАМ БОТ З АВТОМАТИЗАЦІЄЮ"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.scheduler = None
        self.db_available = False

    async def setup_bot(self) -> bool:
        """Налаштування бота"""
        try:
            from aiogram import Bot, Dispatcher
            from aiogram.client.default import DefaultBotProperties
            from aiogram.enums import ParseMode
            import os
            
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                try:
                    from config.settings import BOT_TOKEN
                    bot_token = BOT_TOKEN
                except ImportError:
                    logger.error("❌ BOT_TOKEN не знайдено!")
                    return False
            
            self.bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            self.dp = Dispatcher()
            
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Бот підключено: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка налаштування бота: {e}")
            return False

    async def setup_database(self) -> bool:
        """Налаштування БД"""
        try:
            from database import init_db
            self.db_available = await init_db()
            
            if self.db_available:
                logger.info("✅ Database initialized successfully")
            else:
                logger.warning("⚠️ Working without database")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Database warning: {e}")
            return True

    async def setup_automation(self) -> bool:
        """Налаштування автоматизації"""
        try:
            from services.automated_scheduler import create_automated_scheduler
            self.scheduler = await create_automated_scheduler(self.bot, self.db_available)
            
            if self.scheduler:
                logger.info("🤖 АВТОМАТИЗАЦІЯ АКТИВНА - бот працює самостійно!")
            else:
                logger.warning("⚠️ Working without automation")
            
            return True
        except Exception as e:
            logger.warning(f"⚠️ Automation warning: {e}")
            return True

    async def setup_handlers(self):
        """Налаштування хендлерів"""
        try:
            # Спроба імпорту основних handlers
            from handlers import register_all_handlers
            register_all_handlers(self.dp)
            logger.info("✅ All handlers registered successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Main handlers unavailable: {e}")
            await self._register_emergency_handlers()
        except Exception as e:
            logger.error(f"❌ Handlers error: {e}")
            await self._register_emergency_handlers()

    async def _register_emergency_handlers(self):
        """Аварійні handlers для всіх типів повідомлень"""
        from aiogram import F
        from aiogram.types import Message, CallbackQuery, InlineQuery
        from aiogram.filters import Command, CommandStart
        
        logger.info("🆘 Реєстрація аварійних handlers...")
        
        # Команда /start
        @self.dp.message(CommandStart())
        async def start_handler(message: Message):
            await message.answer(
                "🤖 <b>Привіт! Я український мем-бот з гейміфікацією!</b>\n\n"
                "📋 <b>Команди:</b>\n"
                "• /help - довідка\n"
                "• /meme - випадковий мем\n"
                "• /anekdot - український анекдот\n"
                "• /profile - мій профіль\n"
                "• /admin - панель адміна"
            )
        
        # Команда /help
        @self.dp.message(Command("help"))
        async def help_handler(message: Message):
            await message.answer(
                "❓ <b>ДОВІДКА ПО БОТУ</b>\n\n"
                "🎮 <b>Гейміфікація:</b>\n"
                "• Заробляйте бали за активність\n"
                "• Підвищуйте свій ранг\n\n"
                "📝 <b>Контент:</b>\n"
                "• /meme - випадковий мем\n"
                "• /anekdot - український анекдот\n\n"
                "👤 <b>Профіль:</b>\n"
                "• /profile - ваш профіль"
            )
        
        # Команда /meme
        @self.dp.message(Command("meme"))
        async def meme_handler(message: Message):
            memes = [
                "😂 <b>Програміст і кава</b>\n\nПрограміст заходить в кафе і замовляє каву.\nБариста: 'Java чи Python?'\nПрограміст: 'Звичайну!'",
                "🤣 <b>Різдво та Хеллоуїн</b>\n\nЧому програмісти плутають Різдво та Хеллоуїн?\nБо Oct 31 == Dec 25!",
                "😄 <b>Лампочка</b>\n\nСкільки програмістів треба щоб закрутити лампочку?\nЖодного - це апаратна проблема!"
            ]
            import random
            await message.answer(f"🎭 {random.choice(memes)}")
        
        # Команда /anekdot
        @self.dp.message(Command("anekdot"))
        async def anekdot_handler(message: Message):
            anekdots = [
                "🇺🇦 <b>Програмісти</b>\n\nУкраїнець написав код.\nБілорус оптимізував.\nРосіянин скопіював і сказав що сам придумав.",
                "😂 <b>У лікаря</b>\n\nПрограміст: 'Болить спина!'\nЛікар: 'Багато сидиш?'\nПрограміст: 'Тільки 18 годин!'\nЛікар: 'Нормально!'",
                "🤣 <b>Природа</b>\n\nЧому програмісти не люблять природу?\nБагато багів і немає документації!"
            ]
            import random
            await message.answer(f"🎭 {random.choice(anekdots)}")
        
        # Команда /profile
        @self.dp.message(Command("profile"))
        async def profile_handler(message: Message):
            user = message.from_user
            await message.answer(
                f"👤 <b>ПРОФІЛЬ</b>\n\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"👤 Ім'я: {user.first_name or 'Невідоме'}\n"
                f"📱 Username: @{user.username or 'Немає'}\n"
                f"📊 Бали: <b>0</b>\n"
                f"🏆 Ранг: 🤡 <b>Новачок</b>"
            )
        
        # Команда /admin
        @self.dp.message(Command("admin"))
        async def admin_handler(message: Message):
            try:
                import os
                admin_id = int(os.getenv("ADMIN_ID", 603047391))
                if message.from_user.id == admin_id:
                    await message.answer(
                        "👑 <b>ПАНЕЛЬ АДМІНІСТРАТОРА</b>\n\n"
                        "🛠️ <b>Статус:</b> Активний\n"
                        "📊 Функції в розробці..."
                    )
                else:
                    await message.answer("❌ Немає прав адміністратора")
            except:
                await message.answer("❌ Помилка перевірки прав")
        
        # Обробка всіх інших текстових повідомлень
        @self.dp.message(F.text)
        async def text_handler(message: Message):
            await message.answer(
                "🤖 Привіт! Використовуйте команди:\n\n"
                "/start - почати\n"
                "/help - довідка\n"
                "/meme - мем\n"
                "/anekdot - анекдот"
            )
        
        # Обробка callback queries
        @self.dp.callback_query()
        async def callback_handler(callback: CallbackQuery):
            await callback.answer("🔧 Функція в розробці!")
        
        # Обробка всіх інших повідомлень
        @self.dp.message()
        async def any_message_handler(message: Message):
            await message.answer("🤖 Надішліть текстове повідомлення або використовуйте /help")
        
        # Error handler
        @self.dp.error()
        async def error_handler(event, exception):
            logger.error(f"❌ Error: {exception}")
            try:
                if hasattr(event, 'message') and event.message:
                    await event.message.answer("😅 Технічна помилка! Спробуйте /help")
            except:
                pass
        
        logger.info("✅ Аварійні handlers зареєстровано")

    async def cleanup(self):
        """✅ ВИПРАВЛЕНО: Правильне очищення ресурсів"""
        try:
            if self.scheduler:
                await self.scheduler.stop()
            
            # ✅ ВИПРАВЛЕНО: Правильна перевірка aiohttp сесії
            if self.bot:
                try:
                    # Новий спосіб перевірки сесії в aiogram 3.x
                    if hasattr(self.bot, 'session') and self.bot.session:
                        if not self.bot.session.closed():  # ✅ Виклик методу closed()
                            await self.bot.session.close()
                            logger.info("✅ Bot session closed")
                except AttributeError:
                    # Fallback для старших версій
                    try:
                        await self.bot.close()
                        logger.info("✅ Bot closed (fallback)")
                    except:
                        logger.warning("⚠️ Bot cleanup skipped")
                except Exception as e:
                    logger.warning(f"⚠️ Session cleanup warning: {e}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")

    async def run(self) -> bool:
        """Запуск бота"""
        logger.info("🚀 УКРАЇНОМОВНИЙ TELEGRAM-БОT З ГЕЙМІФІКАЦІЄЮ 🚀")
        
        try:
            # Поетапна ініціалізація
            if not await self.setup_bot():
                return False
            
            await self.setup_database()
            await self.setup_automation()
            await self.setup_handlers()
            
            logger.info("🎯 Bot fully initialized with automation support")
            
            # Запуск polling
            try:
                await self.dp.start_polling(self.bot)
            except KeyboardInterrupt:
                logger.info("⏹️ Bot stopped by user")
            
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            return False
        finally:
            await self.cleanup()

async def main():
    """Точка входу"""
    bot = AutomatedUkrainianTelegramBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Program interrupted")
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {e}")
        sys.exit(1)
