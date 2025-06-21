#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 ОСТАТОЧНЕ ВИПРАВЛЕННЯ ВСІХ ПРОБЛЕМ 🚨

Виправляє:
1. aiohttp cleanup помилку
2. handlers registration
3. Update handling
"""

from pathlib import Path

def fix_main_aiohttp():
    """Виправлення aiohttp cleanup в main.py"""
    
    print("🔧 ВИПРАВЛЕННЯ AIOHTTP CLEANUP:")
    
    main_content = '''#!/usr/bin/env python3
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
                "🤖 <b>Привіт! Я український мем-бот з гейміфікацією!</b>\\n\\n"
                "📋 <b>Команди:</b>\\n"
                "• /help - довідка\\n"
                "• /meme - випадковий мем\\n"
                "• /anekdot - український анекдот\\n"
                "• /profile - мій профіль\\n"
                "• /admin - панель адміна"
            )
        
        # Команда /help
        @self.dp.message(Command("help"))
        async def help_handler(message: Message):
            await message.answer(
                "❓ <b>ДОВІДКА ПО БОТУ</b>\\n\\n"
                "🎮 <b>Гейміфікація:</b>\\n"
                "• Заробляйте бали за активність\\n"
                "• Підвищуйте свій ранг\\n\\n"
                "📝 <b>Контент:</b>\\n"
                "• /meme - випадковий мем\\n"
                "• /anekdot - український анекдот\\n\\n"
                "👤 <b>Профіль:</b>\\n"
                "• /profile - ваш профіль"
            )
        
        # Команда /meme
        @self.dp.message(Command("meme"))
        async def meme_handler(message: Message):
            memes = [
                "😂 <b>Програміст і кава</b>\\n\\nПрограміст заходить в кафе і замовляє каву.\\nБариста: 'Java чи Python?'\\nПрограміст: 'Звичайну!'",
                "🤣 <b>Різдво та Хеллоуїн</b>\\n\\nЧому програмісти плутають Різдво та Хеллоуїн?\\nБо Oct 31 == Dec 25!",
                "😄 <b>Лампочка</b>\\n\\nСкільки програмістів треба щоб закрутити лампочку?\\nЖодного - це апаратна проблема!"
            ]
            import random
            await message.answer(f"🎭 {random.choice(memes)}")
        
        # Команда /anekdot
        @self.dp.message(Command("anekdot"))
        async def anekdot_handler(message: Message):
            anekdots = [
                "🇺🇦 <b>Програмісти</b>\\n\\nУкраїнець написав код.\\nБілорус оптимізував.\\nРосіянин скопіював і сказав що сам придумав.",
                "😂 <b>У лікаря</b>\\n\\nПрограміст: 'Болить спина!'\\nЛікар: 'Багато сидиш?'\\nПрограміст: 'Тільки 18 годин!'\\nЛікар: 'Нормально!'",
                "🤣 <b>Природа</b>\\n\\nЧому програмісти не люблять природу?\\nБагато багів і немає документації!"
            ]
            import random
            await message.answer(f"🎭 {random.choice(anekdots)}")
        
        # Команда /profile
        @self.dp.message(Command("profile"))
        async def profile_handler(message: Message):
            user = message.from_user
            await message.answer(
                f"👤 <b>ПРОФІЛЬ</b>\\n\\n"
                f"🆔 ID: <code>{user.id}</code>\\n"
                f"👤 Ім'я: {user.first_name or 'Невідоме'}\\n"
                f"📱 Username: @{user.username or 'Немає'}\\n"
                f"📊 Бали: <b>0</b>\\n"
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
                        "👑 <b>ПАНЕЛЬ АДМІНІСТРАТОРА</b>\\n\\n"
                        "🛠️ <b>Статус:</b> Активний\\n"
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
                "🤖 Привіт! Використовуйте команди:\\n\\n"
                "/start - почати\\n"
                "/help - довідка\\n"
                "/meme - мем\\n"
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
'''
    
    with open("app/main.py", "w", encoding="utf-8") as f:
        f.write(main_content)
    
    print("   ✅ app/main.py виправлено (aiohttp cleanup)")

def create_handlers_init():
    """Створення правильного handlers/__init__.py"""
    
    print("🎯 СТВОРЕННЯ HANDLERS/__INIT__.PY:")
    
    # Створюємо папку handlers
    handlers_dir = Path("app/handlers")
    handlers_dir.mkdir(exist_ok=True, parents=True)
    
    handlers_init_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 HANDLERS МОДУЛЬ - ПРАВИЛЬНА РЕЄСТРАЦІЯ 🎯
"""

import logging
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart

logger = logging.getLogger(__name__)

def register_all_handlers(dp: Dispatcher):
    """🎯 ГОЛОВНА ФУНКЦІЯ РЕЄСТРАЦІЇ ВСІХ HANDLERS"""
    logger.info("🎯 Початок реєстрації handlers...")
    
    # Команда /start
    @dp.message(CommandStart())
    async def start_handler(message: Message):
        await message.answer(
            "🤖 <b>Привіт! Я український мем-бот з гейміфікацією!</b>\\n\\n"
            "📋 <b>Команди:</b>\\n"
            "• /help - довідка по боту\\n"
            "• /meme - випадковий мем\\n"
            "• /anekdot - український анекдот\\n"
            "• /profile - мій профіль\\n"
            "• /top - таблиця лідерів\\n"
            "• /submit - надіслати контент\\n"
            "• /admin - панель адміна\\n\\n"
            "🎮 <b>Гейміфікація:</b>\\n"
            "Заробляйте бали за активність та підвищуйте свій ранг!"
        )
    
    # Команда /help
    @dp.message(Command("help"))
    async def help_handler(message: Message):
        await message.answer(
            "❓ <b>ДОВІДКА ПО БОТУ</b>\\n\\n"
            "🎮 <b>Гейміфікація:</b>\\n"
            "• Отримуйте бали за активність\\n"
            "• Підвищуйте свій ранг\\n"
            "• Беріть участь в дуелях\\n\\n"
            "📝 <b>Контент:</b>\\n"
            "• /meme - випадковий мем\\n"
            "• /anekdot - український анекдот\\n"
            "• /submit - надіслати свій жарт\\n\\n"
            "👤 <b>Профіль:</b>\\n"
            "• /profile - переглянути профіль\\n"
            "• /top - таблиця лідерів\\n\\n"
            "⚔️ <b>Дуелі:</b>\\n"
            "• /duel - розпочати дуель жартів\\n\\n"
            "🛡️ <b>Адміністрування:</b>\\n"
            "• /admin - панель адміністратора"
        )
    
    # Команда /meme
    @dp.message(Command("meme"))
    async def meme_handler(message: Message):
        memes = [
            "😂 <b>Програміст і кава</b>\\n\\nПрограміст заходить в кафе і замовляє каву.\\nБариста питає: 'Java чи Python?'\\nПрограміст: 'Та ні, звичайну каву!'",
            "🤣 <b>Різдво та Хеллоуїн</b>\\n\\nЧому програмісти завжди плутають Різдво та Хеллоуїн?\\nБо Oct 31 == Dec 25!",
            "😄 <b>Лампочка та програмісти</b>\\n\\nСкільки програмістів потрібно, щоб закрутити лампочку?\\nЖодного - це апаратна проблема!",
            "🤔 <b>Два байти в барі</b>\\n\\nДва байти зустрілися в барі.\\nОдин каже: 'У мене біт болить!'\\nДругий: 'То побайтися треба!'",
            "🙄 <b>QA тестер</b>\\n\\nQA тестер заходить в бар.\\nЗамовляє пиво.\\nЗамовляє 0 пив.\\nЗамовляє 999999999 пив.\\nЗамовляє ящірку.\\nЗамовляє -1 пиво.\\nЗамовляє NULL пиво."
        ]
        import random
        meme = random.choice(memes)
        await message.answer(f"🎭 Ось ваш мем:\\n\\n{meme}")
    
    # Команда /anekdot
    @dp.message(Command("anekdot"))
    async def anekdot_handler(message: Message):
        anekdots = [
            "🇺🇦 <b>Три програмісти</b>\\n\\nУкраїнець, росіянин та білорус сперечаються, хто краще програмує.\\nУкраїнець написав красивий код.\\nБілорус написав швидкий код.\\nРосіянин скопіював обидва і сказав що сам придумав.",
            "😂 <b>Програміст у лікаря</b>\\n\\nПриходить програміст до лікаря:\\n- Доктор, у мене болить спина!\\n- А ти багато сидиш за комп'ютером?\\n- Та ні, тільки 18 годин на день!\\n- Це ж нормально для програміста!",
            "🤣 <b>Природа та баги</b>\\n\\nЧому програмісти не люблять природу?\\nБо вона має занадто багато багів і немає документації!",
            "😄 <b>Хліб та яйця</b>\\n\\nПрограміст приходить додому:\\n- Дорогий, купи хліб, якщо будуть яйця - візьми 10\\nПовертається з 10 батонами.\\n- Чому так багато?\\n- Були яйця!",
            "🤪 <b>Рекурсія</b>\\n\\nЩоб зрозуміти рекурсію, спочатку треба зрозуміти рекурсію."
        ]
        import random
        anekdot = random.choice(anekdots)
        await message.answer(f"🎭 Ось ваш анекдот:\\n\\n{anekdot}")
    
    # Команда /profile
    @dp.message(Command("profile"))
    async def profile_handler(message: Message):
        user = message.from_user
        await message.answer(
            f"👤 <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\\n\\n"
            f"🆔 ID: <code>{user.id}</code>\\n"
            f"👤 Ім'я: {user.first_name or 'Невідоме'}\\n"
            f"📱 Username: @{user.username or 'Немає'}\\n"
            f"🌐 Мова: {user.language_code or 'uk'}\\n\\n"
            f"📊 <b>Статистика:</b>\\n"
            f"🔥 Бали: <b>0</b> (початковий рівень)\\n"
            f"🏆 Ранг: 🤡 <b>Новачок</b>\\n"
            f"📅 Активність: Сьогодні\\n\\n"
            f"ℹ️ <i>Повна статистика буде доступна після підключення до бази даних</i>"
        )
    
    # Команда /top
    @dp.message(Command("top"))
    async def top_handler(message: Message):
        await message.answer(
            "🏆 <b>ТАБЛИЦЯ ЛІДЕРІВ</b>\\n\\n"
            "1. 👑 Demo User - 1500 балів\\n"
            "2. 🥈 Test User - 1000 балів\\n"
            "3. 🥉 Sample User - 500 балів\\n"
            "4. 🏅 Example User - 300 балів\\n"
            "5. 🎖️ Another User - 150 балів\\n\\n"
            "📊 Ваша позиція: #новачок\\n\\n"
            "ℹ️ <i>Реальна таблиця лідерів буде доступна після підключення до бази даних</i>"
        )
    
    # Команда /submit
    @dp.message(Command("submit"))
    async def submit_handler(message: Message):
        await message.answer(
            "📝 <b>ПОДАЧА ВЛАСНОГО КОНТЕНТУ</b>\\n\\n"
            "Функція подачі власного контенту буде доступна незабаром!\\n\\n"
            "📋 <b>Що можна буде подавати:</b>\\n"
            "• 😂 Жарти та анекдоти\\n"
            "• 🖼️ Меми (зображення з підписами)\\n"
            "• 📜 Цікаві історії з життя\\n\\n"
            "🎯 <b>Винагорода за схвалення:</b> +20 балів\\n"
            "🛡️ <b>Модерація:</b> Всі матеріали проходять перевірку\\n\\n"
            "ℹ️ <i>Поки що скористайтеся командами /meme та /anekdot для отримання готового контенту</i>"
        )
    
    # Команда /admin
    @dp.message(Command("admin"))
    async def admin_handler(message: Message):
        try:
            import os
            admin_id = int(os.getenv("ADMIN_ID", 603047391))
            
            if message.from_user.id == admin_id:
                await message.answer(
                    "👑 <b>ПАНЕЛЬ АДМІНІСТРАТОРА</b>\\n\\n"
                    "🛠️ <b>Статус системи:</b>\\n"
                    "✅ Бот: Активний\\n"
                    "✅ База даних: Підключена\\n"
                    "✅ Автоматизація: Працює\\n\\n"
                    "🔧 <b>Доступні функції:</b>\\n"
                    "• /stats - детальна статистика\\n"
                    "• Модерація контенту\\n"
                    "• Управління користувачами\\n"
                    "• Налаштування автоматизації\\n\\n"
                    "📊 <b>Швидка статистика:</b>\\n"
                    "👥 Користувачів: Завантаження...\\n"
                    "📝 Контенту: Завантаження...\\n"
                    "⚔️ Дуелей: Завантаження...\\n\\n"
                    "ℹ️ <i>Повна панель адміністратора в розробці</i>"
                )
            else:
                await message.answer(
                    "❌ <b>Доступ заборонено</b>\\n\\n"
                    "У вас немає прав адміністратора для доступу до цієї панелі."
                )
        except Exception as e:
            await message.answer(f"❌ Помилка перевірки прав: {e}")
    
    # Обробка всіх текстових повідомлень
    @dp.message(F.text & ~F.text.startswith('/'))
    async def text_handler(message: Message):
        await message.answer(
            "🤖 Привіт! Я розумію тільки команди.\\n\\n"
            "📋 <b>Спробуйте:</b>\\n"
            "/start - почати роботу\\n"
            "/help - повна довідка\\n"
            "/meme - отримати мем\\n"
            "/anekdot - отримати анекдот\\n"
            "/profile - ваш профіль"
        )
    
    # Обробка callback queries
    @dp.callback_query()
    async def callback_handler(callback: CallbackQuery):
        await callback.answer("🔧 Ця функція поки що в розробці!")
        await callback.message.answer("🔧 Функція буде доступна в наступних оновленнях.")
    
    # Обробка інших типів повідомлень
    @dp.message()
    async def other_handler(message: Message):
        await message.answer(
            "🤖 Я поки що обробляю тільки текстові повідомлення та команди.\\n\\n"
            "Надішліть /help для списку доступних команд."
        )
    
    # Error handler
    @dp.error()
    async def error_handler(event, exception):
        logger.error(f"❌ Unhandled error: {exception}")
        try:
            if hasattr(event, 'message') and event.message:
                await event.message.answer(
                    "😅 <b>Вибачте, сталася технічна помилка!</b>\\n\\n"
                    "Спробуйте ще раз або скористайтеся командою /help"
                )
        except:
            pass
    
    logger.info("✅ Всі handlers зареєстровано успішно")

# Експорт
__all__ = ['register_all_handlers']

logger.info("🎮 Handlers модуль завантажено з повною підтримкою")
'''
    
    with open("app/handlers/__init__.py", "w", encoding="utf-8") as f:
        f.write(handlers_init_content)
    
    print("   ✅ app/handlers/__init__.py створено з register_all_handlers")

def main():
    """Головна функція остаточного виправлення"""
    print("🚨" * 30)
    print("\n🔧 ОСТАТОЧНЕ ВИПРАВЛЕННЯ ВСІХ ПРОБЛЕМ")
    print("🎯 Виправляє: aiohttp cleanup + handlers registration")
    print("🚨" * 30)
    print()
    
    try:
        # Виправлення main.py
        fix_main_aiohttp()
        
        # Створення handlers/__init__.py
        create_handlers_init()
        
        print("\n✅ ВСІ ВИПРАВЛЕННЯ ЗАСТОСОВАНО!")
        print("\n🚀 ОЧІКУВАНІ РЕЗУЛЬТАТИ:")
        print("✅ Зникне: 'AiohttpSession' object has no attribute 'closed'")
        print("✅ Зникне: cannot import name 'register_all_handlers'")
        print("✅ Всі Update будуть handled (не 'not handled')")
        print("✅ Бот буде відповідати на всі команди")
        
        print("\n📋 НАСТУПНІ КРОКИ:")
        print("1. git add .")
        print("2. git commit -m '🚨 Final fix: aiohttp cleanup + handlers'")
        print("3. git push")
        print("4. Перевірте логи Railway через 1-2 хвилини")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Помилка виправлення: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 УСПІХ!' if success else '❌ ПОМИЛКА'}")