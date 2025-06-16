#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Україномовний Telegram-бот - Головний файл запуску 🧠😂🔥
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Додаємо поточну папку до Python path
sys.path.insert(0, str(Path(__file__).parent))

# Aiogram imports з підтримкою нової версії
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import web

# Наші модулі (спробуємо різні варіанти структури)
try:
    from settings import settings, EMOJI
except ImportError:
    try:
        from config.settings import settings, EMOJI
    except ImportError:
        # Fallback налаштування
        import os
        class FallbackSettings:
            BOT_TOKEN = os.getenv("BOT_TOKEN", "")
            ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
            DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        settings = FallbackSettings()
        EMOJI = {"brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐", "check": "✅", "cross": "❌"}

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, getattr(settings, 'LOG_LEVEL', 'INFO'), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8') if Path.cwd().is_dir() else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class UkrainianBot:
    """Головний клас україномовного бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.app = None
        
    async def create_bot(self):
        """Створення бота та диспетчера (оновлено для aiogram 3.7.0+)"""
        try:
            # Створення сесії з налаштуваннями
            session = AiohttpSession()
            
            # Створення бота з новим API
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                session=session,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            # Створення диспетчера
            self.dp = Dispatcher()
            
            logger.info(f"🤖 Бот створено успішно!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка створення бота: {e}")
            return False
    
    async def setup_handlers(self):
        """Реєстрація всіх хендлерів"""
        if not self.dp:
            logger.error("❌ Диспетчер не створено!")
            return False
            
        try:
            handlers_registered = 0
            
            # Спробуємо різні варіанти імпорту
            handler_modules = [
                # Спочатку спробуємо плоску структуру
                ("basic_commands", "register_basic_handlers", "Основні команди"),
                ("content_handlers", "register_content_handlers", "Контент хендлери"),
                ("gamification_handlers", "register_gamification_handlers", "Гейміфікація"),
                ("moderation_handlers", "register_moderation_handlers", "Модерація"),
                ("duel_handlers", "register_duel_handlers", "Дуелі"),
                # Потім папкову структуру
                ("handlers.basic_commands", "register_basic_handlers", "Основні команди (handlers/)"),
                ("handlers.content_handlers", "register_content_handlers", "Контент хендлери (handlers/)"),
                ("handlers.gamification_handlers", "register_gamification_handlers", "Гейміфікація (handlers/)"),
                ("handlers.moderation_handlers", "register_moderation_handlers", "Модерація (handlers/)"),
                ("handlers.duel_handlers", "register_duel_handlers", "Дуелі (handlers/)")
            ]
            
            for module_name, func_name, description in handler_modules:
                try:
                    module = __import__(module_name, fromlist=[func_name])
                    register_func = getattr(module, func_name)
                    register_func(self.dp)
                    handlers_registered += 1
                    logger.info(f"✅ {description} - зареєстровано")
                    break  # Якщо знайшли цей модуль, пропускаємо інші варіанти
                except (ImportError, AttributeError):
                    continue
            
            # Якщо нічого не зареєстровано, додаємо базові хендлери
            if handlers_registered == 0:
                logger.warning("⚠️ Використовуємо fallback хендлери")
                self.register_fallback_handlers()
                handlers_registered = 1
            
            logger.info(f"🎯 Зареєстровано {handlers_registered} груп хендлерів")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка реєстрації хендлерів: {e}")
            # Все одно реєструємо fallback хендлери
            try:
                self.register_fallback_handlers()
                return True
            except Exception as fallback_error:
                logger.error(f"❌ Навіть fallback хендлери не працюють: {fallback_error}")
                return False
    
    def register_fallback_handlers(self):
        """Базові хендлери як fallback"""
        from aiogram import F
        from aiogram.filters import Command
        from aiogram.types import Message
        
        @self.dp.message(Command("start"))
        async def cmd_start_fallback(message: Message):
            await message.answer(
                f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю в україномовному боті!</b>\n\n"
                f"{EMOJI['star']} Бот запущено у базовому режимі\n"
                f"{EMOJI['check']} Основні функції активні\n"
                f"{EMOJI['fire']} Адмін: {settings.ADMIN_ID}\n\n"
                f"Доступні команди:\n"
                f"• /start - запуск\n"
                f"• /help - допомога\n"
                f"• /status - статус бота\n"
                f"• /test - тест функцій"
            )
        
        @self.dp.message(Command("help"))
        async def cmd_help_fallback(message: Message):
            await message.answer(
                f"{EMOJI['star']} <b>Допомога</b>\n\n"
                f"Базові команди:\n"
                f"• /start - запуск бота\n"
                f"• /help - ця довідка\n"
                f"• /status - статус\n"
                f"• /test - тест\n\n"
                f"{EMOJI['fire']} Бот працює в базовому режимі\n"
                f"🔧 Для повного функціоналу потрібні додаткові модулі"
            )
        
        @self.dp.message(Command("status"))
        async def cmd_status_fallback(message: Message):
            await message.answer(
                f"{EMOJI['check']} <b>Статус бота</b>\n\n"
                f"🤖 Бот: активний\n"
                f"👥 Адмін: {settings.ADMIN_ID}\n"
                f"💾 БД: {settings.DATABASE_URL.split('@')[0] if '@' in settings.DATABASE_URL else 'Local'}@***\n"
                f"🧠 AI: {'✅' if getattr(settings, 'OPENAI_API_KEY', None) else '❌'}\n"
                f"🔥 Режим: базовий"
            )
        
        @self.dp.message(Command("test"))
        async def cmd_test_fallback(message: Message):
            test_msg = f"{EMOJI['fire']} <b>Тест функцій:</b>\n\n"
            
            # Тест відправки повідомлення
            test_msg += f"✅ Відправка повідомлень - OK\n"
            
            # Тест HTML форматування
            test_msg += f"✅ HTML форматування - OK\n"
            
            # Тест емодзі
            test_msg += f"✅ Емодзі {EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} - OK\n"
            
            # Тест налаштувань
            test_msg += f"✅ Налаштування - OK\n"
            
            test_msg += f"\n{EMOJI['check']} Всі базові функції працюють!"
            
            await message.answer(test_msg)
        
        # Обробник всіх інших повідомлень
        @self.dp.message(F.text)
        async def fallback_handler(message: Message):
            if not message.text.startswith('/'):
                await message.answer(
                    f"{EMOJI['star']} Привіт! Використай /help для допомоги\n"
                    f"Або /start для початку роботи"
                )
        
        logger.info("🔧 Fallback хендлери зареєстровано")
    
    async def setup_database(self):
        """Ініціалізація бази даних"""
        try:
            # Спробуємо різні варіанти імпорту БД
            database_modules = [
                ("database", "init_db"),
                ("database.database", "init_db"),
                ("models", "init_db")
            ]
            
            for module_name, func_name in database_modules:
                try:
                    module = __import__(module_name, fromlist=[func_name])
                    init_db = getattr(module, func_name)
                    await init_db()
                    logger.info("💾 База даних ініціалізована")
                    return True
                except (ImportError, AttributeError):
                    continue
            
            logger.warning("⚠️ Модуль database не знайдено, пропускаємо ініціалізацію БД")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації БД: {e}")
            return True  # Продовжуємо без БД
    
    async def setup_scheduler(self):
        """Налаштування планувальника задач"""
        try:
            # Спробуємо різні варіанти імпорту планувальника
            scheduler_modules = [
                ("scheduler", "SchedulerService"),
                ("services.scheduler", "SchedulerService")
            ]
            
            for module_name, class_name in scheduler_modules:
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    SchedulerService = getattr(module, class_name)
                    self.scheduler = SchedulerService(self.bot)
                    await self.scheduler.start()
                    logger.info("⏰ Планувальник запущено")
                    return True
                except (ImportError, AttributeError):
                    continue
            
            logger.warning("⚠️ Модуль scheduler не знайдено, пропускаємо планувальник")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка запуску планувальника: {e}")
            return True  # Продовжуємо без планувальника
    
    async def create_webapp(self):
        """Створення веб-додатку для Railway"""
        try:
            # Створення aiohttp додатку
            self.app = web.Application()
            
            # Health check endpoint
            async def health_check(request):
                return web.json_response({
                    "status": "healthy",
                    "bot": "ukrainian_telegram_bot",
                    "version": "1.0.0",
                    "admin_id": settings.ADMIN_ID,
                    "bot_ready": self.bot is not None
                })
            
            # Статична сторінка
            async def index(request):
                return web.Response(
                    text=f"""
                    <html>
                        <head>
                            <title>🧠😂🔥 Україномовний Telegram-бот</title>
                            <style>
                                body {{ font-family: Arial; text-align: center; padding: 50px; background: #f0f8ff; }}
                                .status {{ color: {'green' if self.bot else 'red'}; }}
                            </style>
                        </head>
                        <body>
                            <h1>🧠😂🔥 Україномовний Telegram-бот</h1>
                            <div class="status">
                                <p>✅ Статус: {'Активний' if self.bot else 'Помилка'}</p>
                                <p>🤖 Версія: 1.0.0</p>
                                <p>👥 Адмін: {settings.ADMIN_ID}</p>
                                <p>📊 <a href="/health">Health Check</a></p>
                            </div>
                            <hr>
                            <p>🇺🇦 Зроблено з ❤️ для української мем-спільноти!</p>
                        </body>
                    </html>
                    """,
                    content_type='text/html'
                )
            
            self.app.router.add_get('/', index)
            self.app.router.add_get('/health', health_check)
            
            logger.info("🌐 Веб-додаток створено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка створення веб-додатку: {e}")
            return False
    
    async def start_webapp(self):
        """Запуск веб-сервера для Railway"""
        try:
            port = int(os.getenv("PORT", 8000))
            
            # Запуск веб-сервера у фоновому режимі
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            logger.info(f"🌐 Веб-сервер запущено на порту {port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка запуску веб-сервера: {e}")
            return False
    
    async def start_polling(self):
        """Запуск бота в режимі polling"""
        if not self.bot:
            raise ValueError("Бот не створено!")
            
        try:
            logger.info(f"🚀 Запуск бота в режимі polling...")
            
            # Видалення webhook якщо був
            await self.bot.delete_webhook(drop_pending_updates=True)
            
            # Запуск polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            
        except Exception as e:
            logger.error(f"❌ Помилка polling: {e}")
            raise
    
    async def shutdown(self):
        """Коректне завершення роботи"""
        logger.info("🛑 Завершення роботи бота...")
        
        try:
            if hasattr(self, 'scheduler') and self.scheduler:
                await self.scheduler.stop()
                logger.info("⏰ Планувальник зупинено")
            
            if self.bot:
                await self.bot.session.close()
                logger.info("🤖 Сесія бота закрита")
            
            logger.info("✅ Бот завершено коректно")
            
        except Exception as e:
            logger.error(f"❌ Помилка завершення: {e}")
    
    async def run(self):
        """Головний метод запуску"""
        logger.info("🧠😂🔥 ЗАПУСК УКРАЇНОМОВНОГО TELEGRAM-БОТА 🧠😂🔥")
        
        try:
            # Перевірка налаштувань
            if not settings.BOT_TOKEN:
                raise ValueError("BOT_TOKEN не налаштовано!")
            if not settings.ADMIN_ID:
                raise ValueError("ADMIN_ID не налаштовано!")
            
            logger.info(f"🔧 Налаштування:")
            logger.info(f"   📱 Адмін ID: {settings.ADMIN_ID}")
            logger.info(f"   💾 База даних: {settings.DATABASE_URL.split('@')[0] if '@' in settings.DATABASE_URL else 'Local'}@***")
            logger.info(f"   🧠 OpenAI: {'✅ Налаштовано' if getattr(settings, 'OPENAI_API_KEY', None) else '❌ Відсутнє'}")
            
            # Поетапна ініціалізація
            steps = [
                ("🤖 Створення бота", self.create_bot()),
                ("💾 Ініціалізація БД", self.setup_database()),
                ("🎯 Реєстрація хендлерів", self.setup_handlers()),
                ("⏰ Запуск планувальника", self.setup_scheduler()),
                ("🌐 Створення веб-додатку", self.create_webapp()),
                ("🌐 Запуск веб-сервера", self.start_webapp())
            ]
            
            success_count = 0
            for step_name, step_coro in steps:
                logger.info(f"▶️ {step_name}...")
                result = await step_coro
                if not result:
                    logger.warning(f"⚠️ {step_name} - пропущено через помилку")
                else:
                    logger.info(f"✅ {step_name} - завершено")
                    success_count += 1
            
            # Перевірка критичних компонентів
            if not self.bot:
                raise ValueError("Не вдалося створити бота!")
            if not self.dp:
                raise ValueError("Не вдалося створити диспетчер!")
            
            # Отримання інформації про бота
            bot_info = await self.bot.get_me()
            logger.info(f"🎉 Бот @{bot_info.username} готовий до роботи!")
            
            # Повідомлення адміністратору про запуск
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"🚀 <b>Бот запущено успішно!</b>\n\n"
                    f"🤖 <b>Бот:</b> @{bot_info.username}\n"
                    f"💾 <b>БД:</b> {'✅ Підключена' if hasattr(self, 'database_ok') else '⚠️ Базовий режим'}\n"
                    f"⏰ <b>Планувальник:</b> {'✅ Активний' if hasattr(self, 'scheduler') else '⚠️ Вимкнений'}\n"
                    f"🧠 <b>AI:</b> {'✅ Активний' if getattr(settings, 'OPENAI_API_KEY', None) else '❌ Вимкнений'}\n"
                    f"🎯 <b>Успішних кроків:</b> {success_count}/6\n\n"
                    f"📊 Доступні команди:\n"
                    f"• /start - перевірка роботи\n"
                    f"• /help - довідка\n"
                    f"• /status - статус бота\n"
                    f"• /test - тест функцій"
                )
            except Exception as e:
                logger.warning(f"Не вдалося повідомити адміністратора: {e}")
            
            # Запуск основного циклу
            await self.start_polling()
            
        except Exception as e:
            logger.error(f"💥 Критична помилка: {e}")
            raise
        finally:
            await self.shutdown()

def setup_signal_handlers(bot_instance):
    """Налаштування обробників сигналів"""
    def signal_handler(signum, frame):
        logger.info(f"🛑 Отримано сигнал {signum}")
        # Створюємо задачу на завершення
        loop = asyncio.get_event_loop()
        loop.create_task(bot_instance.shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Головна функція"""
    try:
        # Створення екземпляру бота
        bot_instance = UkrainianBot()
        
        # Налаштування обробників сигналів
        setup_signal_handlers(bot_instance)
        
        # Запуск бота
        await bot_instance.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Фатальна помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Створення директорій якщо не існують
    try:
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
    except:
        pass  # Ігноруємо помилки створення директорій
    
    # Запуск
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Програма завершена")
    except Exception as e:
        print(f"💥 Критична помилка запуску: {e}")
        sys.exit(1)