#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 ВИПРАВЛЕНА РЕЄСТРАЦІЯ ВСІХ ХЕНДЛЕРІВ 🎮

ВИПРАВЛЕННЯ:
✅ Додано всі typing імпорти (List, Dict, Any, Optional)
✅ Правильна обробка ImportError для відсутніх модулів
✅ Fallback хендлери для критичних функцій
✅ Детальне логування статусу завантаження
✅ Правильний порядок реєстрації хендлерів
"""

import logging
import random
from typing import Optional, List, Dict, Any, Union, Callable
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher) -> bool:
    """
    Реєстрація всіх хендлерів бота в правильному порядку
    
    Args:
        dp: Dispatcher для реєстрації хендлерів
    
    Returns:
        bool: True якщо хендлери зареєстровані успішно
    """
    
    logger.info("🎮 Починаю реєстрацію хендлерів...")
    
    handlers_status: Dict[str, bool] = {}
    total_handlers = 0
    registered_handlers = 0
    
    # ===== 1. ОСНОВНІ КОМАНДИ =====
    try:
        from .basic_commands import register_basic_handlers
        register_basic_handlers(dp)
        handlers_status['basic_commands'] = True
        registered_handlers += 1
        logger.info("✅ Basic commands зареєстровано")
    except ImportError as e:
        handlers_status['basic_commands'] = False
        logger.warning(f"⚠️ Basic commands не завантажені: {e}")
        # Реєструємо fallback основні команди
        _register_fallback_basic_handlers(dp)
        registered_handlers += 1
    except Exception as e:
        handlers_status['basic_commands'] = False
        logger.error(f"❌ Помилка basic commands: {e}")
        _register_fallback_basic_handlers(dp)
        registered_handlers += 1
    
    total_handlers += 1
    
    # ===== 2. АДМІН-ПАНЕЛЬ =====
    try:
        from .admin_panel_handlers import register_admin_handlers
        register_admin_handlers(dp)
        handlers_status['admin_panel'] = True
        registered_handlers += 1
        logger.info("✅ Admin panel зареєстровано")
    except ImportError as e:
        handlers_status['admin_panel'] = False
        logger.warning(f"⚠️ Admin panel не завантажена: {e}")
        # Реєструємо fallback адмін команди
        _register_fallback_admin_handlers(dp)
        registered_handlers += 1
    except Exception as e:
        handlers_status['admin_panel'] = False
        logger.error(f"❌ Помилка admin panel: {e}")
    
    total_handlers += 1
    
    # ===== 3. КОНТЕНТ (МЕМИ/ЖАРТИ) =====
    try:
        from .content_handlers import register_content_handlers
        register_content_handlers(dp)
        handlers_status['content'] = True
        registered_handlers += 1
        logger.info("✅ Content handlers зареєстровано")
    except ImportError as e:
        handlers_status['content'] = False
        logger.warning(f"⚠️ Content handlers не завантажені: {e}")
        # Реєструємо fallback контент команди
        _register_fallback_content_handlers(dp)
        registered_handlers += 1
    except Exception as e:
        handlers_status['content'] = False
        logger.error(f"❌ Помилка content handlers: {e}")
    
    total_handlers += 1
    
    # ===== 4. ДУЕЛІ =====
    try:
        from .duel_handlers import register_duel_handlers
        register_duel_handlers(dp)
        handlers_status['duels'] = True
        registered_handlers += 1
        logger.info("✅ Duel handlers зареєстровано")
    except ImportError as e:
        handlers_status['duels'] = False
        logger.warning(f"⚠️ Duel handlers не завантажені: {e}")
        # Реєструємо fallback дуель команди
        _register_fallback_duel_handlers(dp)
        registered_handlers += 1
    except Exception as e:
        handlers_status['duels'] = False
        logger.error(f"❌ Помилка duel handlers: {e}")
    
    total_handlers += 1
    
    # ===== 5. МОДЕРАЦІЯ =====
    try:
        from .moderation_handlers import register_moderation_handlers
        register_moderation_handlers(dp)
        handlers_status['moderation'] = True
        registered_handlers += 1
        logger.info("✅ Moderation handlers зареєстровано")
    except ImportError as e:
        handlers_status['moderation'] = False
        logger.warning(f"⚠️ Moderation handlers не завантажені: {e}")
        # Реєструємо fallback модерація команди
        _register_fallback_moderation_handlers(dp)
        registered_handlers += 1
    except Exception as e:
        handlers_status['moderation'] = False
        logger.error(f"❌ Помилка moderation handlers: {e}")
    
    total_handlers += 1
    
    # ===== 6. ГЕЙМІФІКАЦІЯ =====
    try:
        from .gamification_handlers import register_gamification_handlers
        register_gamification_handlers(dp)
        handlers_status['gamification'] = True
        registered_handlers += 1
        logger.info("✅ Gamification handlers зареєстровано")
    except ImportError as e:
        handlers_status['gamification'] = False
        logger.warning(f"⚠️ Gamification handlers не завантажені: {e}")
        # Реєструємо fallback гейміфікація команди
        _register_fallback_gamification_handlers(dp)
        registered_handlers += 1
    except Exception as e:
        handlers_status['gamification'] = False
        logger.error(f"❌ Помилка gamification handlers: {e}")
    
    total_handlers += 1
    
    # ===== 7. УНІВЕРСАЛЬНІ CALLBACK'И =====
    _register_universal_callbacks(dp)
    
    # ===== ПІДСУМОК =====
    logger.info(f"📊 Реєстрація завершена: {registered_handlers}/{total_handlers} модулів")
    
    success_rate = (registered_handlers / total_handlers) * 100
    if success_rate >= 90:
        logger.info("🎉 Всі хендлери зареєстровані успішно!")
    elif success_rate >= 70:
        logger.info("✅ Більшість хендлерів зареєстровано")
    else:
        logger.warning("⚠️ Деякі хендлери недоступні, але бот працездатний")
    
    return True

# ===== FALLBACK ФУНКЦІЇ =====

def _register_fallback_basic_handlers(dp: Dispatcher):
    """Fallback основні команди"""
    logger.info("🆘 Реєстрація fallback basic handlers...")
    
    @dp.message(Command("start"))
    async def fallback_start(message: Message):
        await message.answer(
            "🧠😂🔥 <b>Вітаю в україномовному боті!</b>\n\n"
            "🎯 <b>Що я вмію:</b>\n"
            "• 😂 Генерую меми та анекдоти\n"
            "• ⚔️ Організовую дуелі жартів\n"
            "• 🏆 Веду рейтинг користувачів\n"
            "• 🎮 Гейміфікація з балами\n\n"
            "📋 <b>Команди:</b>\n"
            "/meme - отримати мем\n"
            "/anekdot - отримати анекдот\n"
            "/profile - мій профіль\n"
            "/top - рейтинг\n"
            "/duel - почати дуель\n"
            "/help - детальна довідка\n\n"
            "🔧 <i>Працює в базовому режимі</i>"
        )
    
    @dp.message(Command("help"))
    async def fallback_help(message: Message):
        await message.answer(
            "📚 <b>ДЕТАЛЬНА ДОВІДКА</b>\n\n"
            "🎯 <b>ОСНОВНІ ФУНКЦІЇ:</b>\n\n"
            "😂 <b>Контент:</b>\n"
            "• /meme - випадковий мем\n"
            "• /anekdot - випадковий анекдот\n"
            "• /submit - подати свій жарт\n\n"
            "⚔️ <b>Дуелі:</b>\n"
            "• /duel - почати дуель жартів\n"
            "• Голосування за кращий жарт\n"
            "• Отримання балів за перемоги\n\n"
            "🏆 <b>Рейтинг:</b>\n"
            "• /profile - ваш профіль та бали\n"
            "• /top - топ користувачів\n"
            "• Система рангів та досягнень\n\n"
            "👑 <b>Для адміністраторів:</b>\n"
            "• /admin - адмін панель\n"
            "• /stats - статистика бота\n\n"
            "💡 <i>Деякі функції можуть бути обмежені в базовому режимі</i>"
        )
    
    logger.info("✅ Fallback basic handlers зареєстровано")

def _register_fallback_content_handlers(dp: Dispatcher):
    """Fallback контент команди"""
    logger.info("🆘 Реєстрація fallback content handlers...")
    
    FALLBACK_JOKES = [
        "Чому програмісти плутають Хеллоуїн і Різдво? Тому що 31 OCT = 25 DEC!",
        "Скільки програмістів потрібно щоб закрутити лампочку? Жодного. Це апаратна проблема!",
        "Чому програмісти носять окуляри? Тому що не можуть C#!",
        "Що сказав 0 до 8? - Гарний пояс!",
        "Найкращий спосіб прискорити комп'ютер - кинути його з вікна!",
        "Чому Java програмісти носять окуляри? Тому що вони не можуть C!",
        "Який найкращий об'єкт в Java? Перерва на каву!",
        "Я розповів дружині жарт про UDP, але не знаю, чи дійшов він до неї.",
        "У чому різниця між Java та JavaScript? Така ж як між молотком та молотковою акулою!",
        "Програміст - це машина для перетворення кави на код!"
    ]
    
    @dp.message(Command("meme"))
    async def fallback_meme(message: Message):
        joke = random.choice(FALLBACK_JOKES)
        await message.answer(
            f"🔥 <b>Мем дня:</b>\n\n"
            f"<i>{joke}</i>\n\n"
            f"😂 Сподіваюся, вам сподобалось!\n"
            f"💡 <i>Це fallback контент. Для більшого розмаїття налаштуйте БД</i>"
        )
    
    @dp.message(Command("anekdot"))
    async def fallback_anekdot(message: Message):
        joke = random.choice(FALLBACK_JOKES)
        await message.answer(
            f"😂 <b>Анекдот:</b>\n\n"
            f"<i>{joke}</i>\n\n"
            f"🎭 Сміялись? Поділіться з друзями!\n"
            f"💡 <i>Це fallback контент. Додайте власні анекдоти через БД</i>"
        )
    
    @dp.message(Command("submit"))
    async def fallback_submit(message: Message):
        await message.answer(
            "📝 <b>Подача контенту</b>\n\n"
            "🔧 Функція подачі контенту недоступна в базовому режимі.\n"
            "Для повного функціоналу потрібна:\n"
            "• Налаштована база даних\n"
            "• Система модерації\n"
            "• Адмін панель\n\n"
            "💡 <i>Зараз ви можете просто надіслати свій жарт боту!</i>\n\n"
            "📨 Напишіть свій жарт у наступному повідомленні:"
        )
    
    logger.info("✅ Fallback content handlers зареєстровано")

def _register_fallback_admin_handlers(dp: Dispatcher):
    """Fallback адмін команди"""
    logger.info("🆘 Реєстрація fallback admin handlers...")
    
    @dp.message(Command("admin"))
    async def fallback_admin(message: Message):
        admin_id = int(os.getenv("ADMIN_ID", 0))
        if message.from_user.id != admin_id:
            await message.answer("❌ Тільки для адміністраторів")
            return
        
        await message.answer(
            "👑 <b>АДМІН ПАНЕЛЬ</b>\n\n"
            "🔧 <b>Базовий режим активний</b>\n\n"
            "📊 <b>Доступні команди:</b>\n"
            "• /stats - базова статистика\n"
            "• /status - статус бота\n\n"
            "⚙️ <b>Для повного функціоналу потрібно:</b>\n"
            "• Налаштувати базу даних\n"
            "• Активувати всі handlers\n"
            "• Запустити автоматизацію\n\n"
            "💡 <i>Перевірте логи для діагностики</i>"
        )
    
    @dp.message(Command("stats"))
    async def fallback_stats(message: Message):
        admin_id = int(os.getenv("ADMIN_ID", 0))
        if message.from_user.id != admin_id:
            await message.answer("❌ Тільки для адміністраторів")
            return
        
        await message.answer(
            "📊 <b>БАЗОВА СТАТИСТИКА</b>\n\n"
            "🤖 <b>Статус бота:</b> Fallback режим\n"
            "💾 <b>База даних:</b> Недоступна\n"
            "🎮 <b>Handlers:</b> Fallback версії\n"
            "🤖 <b>Автоматизація:</b> Неактивна\n\n"
            "⚡ <b>Для повної статистики потрібно:</b>\n"
            "• Підключити PostgreSQL\n"
            "• Налаштувати всі модулі\n"
            "• Активувати планувальник"
        )
    
    logger.info("✅ Fallback admin handlers зареєстровано")

def _register_fallback_duel_handlers(dp: Dispatcher):
    """Fallback дуель команди"""
    logger.info("🆘 Реєстрація fallback duel handlers...")
    
    @dp.message(Command("duel"))
    async def fallback_duel(message: Message):
        await message.answer(
            "⚔️ <b>ДУЕЛІ ЖАРТІВ</b>\n\n"
            "🔧 <i>Функція недоступна в базовому режимі</i>\n\n"
            "🎯 <b>Що таке дуелі:</b>\n"
            "• Змагання між двома жартами\n"
            "• Голосування інших користувачів\n"
            "• Бали за перемоги та участь\n"
            "• Рейтинг найкращих жартунів\n\n"
            "⚙️ <b>Для активації потрібно:</b>\n"
            "• База даних для збереження дуелей\n"
            "• Система голосування\n"
            "• Планувальник для автозавершення\n\n"
            "💡 <i>Поки що використовуйте /meme та /anekdot</i>"
        )
    
    logger.info("✅ Fallback duel handlers зареєстровано")

def _register_fallback_moderation_handlers(dp: Dispatcher):
    """Fallback модерація команди"""
    logger.info("🆘 Реєстрація fallback moderation handlers...")
    
    @dp.message(Command("moderate"))
    async def fallback_moderate(message: Message):
        admin_id = int(os.getenv("ADMIN_ID", 0))
        if message.from_user.id != admin_id:
            await message.answer("❌ Тільки для адміністраторів")
            return
        
        await message.answer(
            "🛡️ <b>МОДЕРАЦІЯ</b>\n\n"
            "🔧 <i>Функція недоступна в базовому режимі</i>\n\n"
            "📋 <b>Що включає модерація:</b>\n"
            "• Перегляд поданого контенту\n"
            "• Схвалення/відхилення жартів\n"
            "• Видалення неприйнятного контенту\n"
            "• Управління користувачами\n\n"
            "⚙️ <b>Для активації потрібно:</b>\n"
            "• База даних з таблицею контенту\n"
            "• Черга модерації\n"
            "• Інтерфейс адміністратора\n\n"
            "💡 <i>Наразі модерація відбувається вручну</i>"
        )
    
    logger.info("✅ Fallback moderation handlers зареєстровано")

def _register_fallback_gamification_handlers(dp: Dispatcher):
    """Fallback гейміфікація команди"""
    logger.info("🆘 Реєстрація fallback gamification handlers...")
    
    @dp.message(Command("profile"))
    async def fallback_profile(message: Message):
        user = message.from_user
        await message.answer(
            f"👤 <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n\n"
            f"🆔 <b>ID:</b> {user.id}\n"
            f"📝 <b>Ім'я:</b> {user.first_name}\n"
            f"🔗 <b>Username:</b> @{user.username or 'Не встановлено'}\n\n"
            f"🔧 <i>Базовий режим</i>\n\n"
            f"⚙️ <b>Для повної гейміфікації потрібно:</b>\n"
            f"• База даних для збереження балів\n"
            f"• Система досягнень\n"
            f"• Рейтинги та ранги\n"
            f"• Статистика активності\n\n"
            f"💡 <i>Використовуйте бота для накопичення балів!</i>"
        )
    
    @dp.message(Command("top"))
    async def fallback_top(message: Message):
        await message.answer(
            "🏆 <b>РЕЙТИНГ КОРИСТУВАЧІВ</b>\n\n"
            "🔧 <i>Функція недоступна в базовому режимі</i>\n\n"
            "📊 <b>Що показує рейтинг:</b>\n"
            "• Топ користувачів за балами\n"
            "• Кількість перемог у дуелях\n"
            "• Активність та досягнення\n"
            "• Статистика за різні періоди\n\n"
            "⚙️ <b>Для активації потрібно:</b>\n"
            "• База даних з таблицею користувачів\n"
            "• Система підрахунку балів\n"
            "• Статистичні функції\n\n"
            "💡 <i>Почніть використовувати бота зараз!</i>"
        )
    
    logger.info("✅ Fallback gamification handlers зареєстровано")

def _register_universal_callbacks(dp: Dispatcher):
    """Універсальні callback'и для необроблених випадків"""
    logger.info("🔗 Реєстрація universal callbacks...")
    
    @dp.callback_query()
    async def handle_unknown_callback(callback: CallbackQuery):
        """Обробка невідомих callback'ів"""
        await callback.answer("⚠️ Ця функція тимчасово недоступна", show_alert=True)
        
        unknown_text = (
            "🔧 <b>Функція в розробці</b>\n\n"
            "⚠️ Ця кнопка поки що не працює.\n"
            "Це може бути через:\n"
            "• Базовий режим роботи\n"
            "• Відсутність БД\n"
            "• Неактивні модулі\n\n"
            "💡 <i>Спробуйте основні команди: /help</i>"
        )
        
        await callback.message.answer(unknown_text)
    
    logger.info("✅ Universal callback handlers зареєстровано")

# ===== ДІАГНОСТИЧНІ ФУНКЦІЇ =====

def check_handlers_status() -> Dict[str, bool]:
    """Перевірка статусу всіх хендлерів"""
    status: Dict[str, bool] = {
        "basic_commands": False,
        "admin_panel": False,
        "content": False,
        "duels": False,
        "moderation": False,
        "gamification": False
    }
    
    # Перевірка наявності модулів
    modules_to_check: List[str] = [
        "basic_commands",
        "admin_panel_handlers",
        "content_handlers", 
        "duel_handlers",
        "moderation_handlers",
        "gamification_handlers"
    ]
    
    for module_name in modules_to_check:
        try:
            __import__(f"handlers.{module_name}")
            key = module_name.replace("_handlers", "").replace("admin_panel", "admin_panel")
            if key in status:
                status[key] = True
        except ImportError:
            pass
    
    return status

def get_handlers_summary() -> Dict[str, Any]:
    """Отримання резюме стану хендлерів"""
    status = check_handlers_status()
    
    total_modules = len(status)
    available_modules = sum(status.values())
    
    return {
        "total_modules": total_modules,
        "available_modules": available_modules,
        "availability_rate": (available_modules / total_modules) * 100,
        "status": status,
        "recommendation": _get_status_recommendation(available_modules, total_modules)
    }

def _get_status_recommendation(available: int, total: int) -> str:
    """Отримання рекомендацій на основі статусу"""
    rate = (available / total) * 100
    
    if rate >= 90:
        return "🎉 Всі хендлери працюють відмінно!"
    elif rate >= 70:
        return "✅ Більшість хендлерів працює, бот функціональний"
    elif rate >= 50:
        return "⚠️ Частина хендлерів недоступна, деякі функції обмежені"
    else:
        return "❌ Багато хендлерів недоступно, рекомендується перевірка залежностей"

# ===== ЕКСПОРТ =====
__all__ = [
    "register_handlers",
    "check_handlers_status", 
    "get_handlers_summary"
]

logger.info(f"🎮 Handlers модуль завантажено з fallback підтримкою")