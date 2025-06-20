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
from typing import Optional, List, Dict, Any, Union, Callable  # ✅ ВИПРАВЛЕНО: всі typing імпорти
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher) -> bool:
    """
    Реєстрація всіх хендлерів бота в правильному порядку
    
    ВИПРАВЛЕННЯ:
    ✅ Додано typing імпорти
    ✅ Graceful fallback при помилках імпорту
    ✅ Детальне логування статусу
    
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
    
    # ===== 7. CALLBACK ХЕНДЛЕРИ =====
    try:
        _register_universal_callback_handlers(dp)
        handlers_status['callbacks'] = True
        registered_handlers += 1
        logger.info("✅ Universal callback handlers зареєстровано")
    except Exception as e:
        handlers_status['callbacks'] = False
        logger.error(f"❌ Помилка callback handlers: {e}")
    
    total_handlers += 1
    
    # ===== ПІДСУМОК РЕЄСТРАЦІЇ =====
    success_rate = (registered_handlers / total_handlers) * 100 if total_handlers > 0 else 0
    
    logger.info("🎮" + "="*50)
    logger.info(f"🎮 ПІДСУМОК РЕЄСТРАЦІЇ ХЕНДЛЕРІВ")
    logger.info("🎮" + "="*50)
    logger.info(f"📊 Зареєстровано: {registered_handlers}/{total_handlers} ({success_rate:.1f}%)")
    
    for handler_name, status in handlers_status.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"   {status_icon} {handler_name}")
    
    if success_rate >= 80:
        logger.info("🎉 Хендлери успішно зареєстровані!")
        result = True
    elif success_rate >= 50:
        logger.warning("⚠️ Частково зареєстровані хендлери - бот працездатний")
        result = True
    else:
        logger.error("❌ Критично мало хендлерів - може бути неробочий")
        result = False
    
    logger.info("🎮" + "="*50)
    
    return result

# ===== FALLBACK ХЕНДЛЕРИ =====

def _register_fallback_basic_handlers(dp: Dispatcher) -> None:
    """Fallback основні хендлери"""
    
    @dp.message(Command("start"))
    async def fallback_start(message: Message):
        """Fallback команда /start"""
        try:
            # Спроба отримання конфігурації
            try:
                from config.settings import BOT_USERNAME, ALL_ADMIN_IDS
                bot_name = BOT_USERNAME
                is_admin = message.from_user.id in ALL_ADMIN_IDS
            except ImportError:
                bot_name = "UkrainianBot"
                is_admin = message.from_user.id == 603047391
            
            user_name = message.from_user.first_name or "Друже"
            
            welcome_text = (
                f"🧠😂🔥 <b>Вітаю, {user_name}!</b>\n\n"
                f"🤖 <b>Україномовний бот @{bot_name}</b>\n\n"
                f"📋 <b>Доступні команди:</b>\n"
                f"• /help - Довідка\n"
                f"• /joke - Випадковий жарт\n"
                f"• /meme - Випадковий мем\n"
                f"• /stats - Статистика\n"
            )
            
            if is_admin:
                welcome_text += (
                    f"\n🛡️ <b>Адмін команди:</b>\n"
                    f"• /admin - Адмін панель\n"
                    f"• /moderate - Модерація контенту\n"
                    f"• /broadcast - Розсилка\n"
                )
            
            welcome_text += (
                f"\n🎮 <b>Функціональність:</b>\n"
                f"• 😂 Жарти та меми\n"
                f"• ⚔️ Дуелі жартів\n"
                f"• 🏆 Система рангів\n"
                f"• 🤖 Автоматизація\n\n"
                f"🚀 <i>Fallback режим активний</i>"
            )
            
            await message.answer(welcome_text)
            
        except Exception as e:
            logger.error(f"❌ Fallback start error: {e}")
            await message.answer("🤖 Бот активний! Використовуйте /help для довідки.")
    
    @dp.message(Command("help"))
    async def fallback_help(message: Message):
        """Fallback команда /help"""
        help_text = (
            "📚 <b>ДОВІДКА ПО БОТУ</b>\n\n"
            "🎮 <b>Основні команди:</b>\n"
            "• /start - Головне меню\n"
            "• /help - Ця довідка\n"
            "• /joke - Випадковий жарт\n"
            "• /meme - Випадковий мем\n"
            "• /stats - Статистика\n"
            "• /profile - Мій профіль\n\n"
            "⚔️ <b>Дуелі:</b>\n"
            "• /duel - Почати дуель\n"
            "• /duel_stats - Статистика дуелей\n\n"
            "🛡️ <b>Для адмінів:</b>\n"
            "• /admin - Адмін панель\n"
            "• /moderate - Модерація\n\n"
            "💡 <b>Підказка:</b> Більшість функцій доступні через кнопки меню!"
        )
        await message.answer(help_text)
    
    @dp.message(Command("joke"))
    async def fallback_joke(message: Message):
        """Fallback команда /joke"""
        import random
        
        jokes: List[str] = [
            "😂 Програміст заходить в кафе:\n- Каву, будь ласка.\n- Цукор?\n- Ні, boolean! 🤓",
            "🎯 Українець купує iPhone:\n- Не загубіть!\n- У мене є Find My iPhone!\n- А якщо не знайде?\n- Значить вкрали москалі! 🇺🇦",
            "🔥 IT-шник на співбесіді:\n- Розкажіть про себе.\n- Я fullstack.\n- Круто! А що вмієте?\n- HTML! 🤡"
        ]
        
        selected_joke = random.choice(jokes)
        await message.answer(f"😄 <b>Жарт дня:</b>\n\n{selected_joke}")
    
    logger.info("✅ Fallback basic handlers зареєстровано")

def _register_fallback_admin_handlers(dp: Dispatcher) -> None:
    """Fallback адмін хендлери"""
    
    @dp.message(Command("admin"))
    async def fallback_admin(message: Message):
        """Fallback адмін панель"""
        try:
            from config.settings import ALL_ADMIN_IDS
            admin_ids = ALL_ADMIN_IDS
        except ImportError:
            admin_ids = [603047391]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ Доступ заборонено. Тільки для адміністраторів.")
            return
        
        admin_text = (
            "🛡️ <b>АДМІН ПАНЕЛЬ</b>\n\n"
            "📊 <b>Статус системи:</b>\n"
            "• Бот: ✅ Активний\n"
            "• БД: ⚠️ Fallback режим\n"
            "• Автоматизація: ⚠️ Обмежена\n\n"
            "📋 <b>Доступні команди:</b>\n"
            "• /moderate - Модерація контенту\n"
            "• /stats - Детальна статистика\n"
            "• /broadcast - Розсилка повідомлень\n"
            "• /users - Список користувачів\n\n"
            "⚠️ <i>Fallback режим - деякі функції обмежені</i>"
        )
        
        await message.answer(admin_text)
    
    @dp.message(Command("broadcast"))
    async def fallback_broadcast(message: Message):
        """Fallback розсилка"""
        try:
            from config.settings import ALL_ADMIN_IDS
            admin_ids = ALL_ADMIN_IDS
        except ImportError:
            admin_ids = [603047391]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ Доступ заборонено.")
            return
        
        await message.answer(
            "📢 <b>СИСТЕМА РОЗСИЛОК</b>\n\n"
            "⚠️ Fallback режим - розсилки обмежені\n\n"
            "Для повноцінних розсилок потрібна БД та автоматизація.\n"
            "Зверніться до розробника для налаштування."
        )
    
    logger.info("✅ Fallback admin handlers зареєстровано")

def _register_fallback_content_handlers(dp: Dispatcher) -> None:
    """Fallback контент хендлери"""
    
    @dp.message(Command("meme"))
    async def fallback_meme(message: Message):
        """Fallback команда /meme"""
        import random
        
        memes: List[str] = [
            "🤣 Коли бачиш що Wi-Fi на роботі швидший за домашній:\n*здивований кіт* 😸",
            "😂 Мій настрій коли п'ятниця:\n*танцююча людина* 💃",
            "🎮 Коли мама каже 'останній раз граєш':\n*хитра усмішка* 😏"
        ]
        
        selected_meme = random.choice(memes)
        await message.answer(f"🔥 <b>Мем дня:</b>\n\n{selected_meme}")
    
    @dp.message(Command("submit"))
    async def fallback_submit(message: Message):
        """Fallback подача контенту"""
        await message.answer(
            "📝 <b>ПОДАЧА КОНТЕНТУ</b>\n\n"
            "⚠️ Fallback режим - БД недоступна\n\n"
            "Для подачі контенту потрібна робоча база даних.\n"
            "Зверніться до адміністратора."
        )
    
    logger.info("✅ Fallback content handlers зареєстровано")

def _register_fallback_duel_handlers(dp: Dispatcher) -> None:
    """Fallback дуель хендлери"""
    
    @dp.message(Command("duel"))
    async def fallback_duel(message: Message):
        """Fallback команда дуелі"""
        await message.answer(
            "⚔️ <b>ДУЕЛІ ЖАРТІВ</b>\n\n"
            "⚠️ Fallback режим - дуелі недоступні\n\n"
            "Для дуелей потрібна:\n"
            "• База даних\n"
            "• Система користувачів\n"
            "• Контент для змагання\n\n"
            "Налаштуйте БД для активації дуелей."
        )
    
    @dp.message(Command("duel_stats"))
    async def fallback_duel_stats(message: Message):
        """Fallback статистика дуелей"""
        await message.answer(
            "📊 <b>СТАТИСТИКА ДУЕЛЕЙ</b>\n\n"
            "⚠️ Недоступно в fallback режимі\n\n"
            "Для статистики потрібна база даних."
        )
    
    logger.info("✅ Fallback duel handlers зареєстровано")

def _register_fallback_moderation_handlers(dp: Dispatcher) -> None:
    """Fallback модерація хендлери"""
    
    @dp.message(Command("moderate"))
    async def fallback_moderate(message: Message):
        """Fallback модерація"""
        try:
            from config.settings import ALL_ADMIN_IDS
            admin_ids = ALL_ADMIN_IDS
        except ImportError:
            admin_ids = [603047391]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ Доступ заборонено.")
            return
        
        await message.answer(
            "🛡️ <b>МОДЕРАЦІЯ КОНТЕНТУ</b>\n\n"
            "⚠️ Fallback режим - модерація недоступна\n\n"
            "Для модерації потрібна:\n"
            "• База даних\n"
            "• Система контенту\n"
            "• Черга модерації\n\n"
            "Налаштуйте БД для активації модерації."
        )
    
    logger.info("✅ Fallback moderation handlers зареєстровано")

def _register_fallback_gamification_handlers(dp: Dispatcher) -> None:
    """Fallback гейміфікація хендлери"""
    
    @dp.message(Command("profile"))
    async def fallback_profile(message: Message):
        """Fallback профіль користувача"""
        user_name = message.from_user.first_name or "Невідомий"
        username = f"@{message.from_user.username}" if message.from_user.username else "Без username"
        
        profile_text = (
            f"👤 <b>ПРОФІЛЬ</b>\n\n"
            f"👨‍💼 Ім'я: {user_name}\n"
            f"📱 Username: {username}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"⚠️ <b>Fallback режим</b>\n"
            f"🎯 Бали: недоступно\n"
            f"🏆 Ранг: недоступно\n"
            f"📊 Статистика: недоступно\n\n"
            f"💡 Для повного профілю потрібна БД"
        )
        
        await message.answer(profile_text)
    
    @dp.message(Command("stats"))
    async def fallback_stats(message: Message):
        """Fallback статистика"""
        await message.answer(
            "📊 <b>СТАТИСТИКА БОТА</b>\n\n"
            "⚠️ Fallback режим\n\n"
            "🤖 Бот: Активний\n"
            "💾 БД: Недоступна\n"
            "🎮 Хендлери: Fallback\n"
            "🤖 Автоматизація: Обмежена\n\n"
            "📝 Для повної статистики потрібна база даних."
        )
    
    logger.info("✅ Fallback gamification handlers зареєстровано")

def _register_universal_callback_handlers(dp: Dispatcher) -> None:
    """Універсальні callback хендлери"""
    
    @dp.callback_query(F.data == "back_to_main")
    async def callback_back_to_main(callback: CallbackQuery):
        """Повернення до головного меню"""
        await callback.answer()
        
        welcome_text = (
            "🧠😂🔥 <b>ГОЛОВНЕ МЕНЮ</b>\n\n"
            "Оберіть дію з меню:"
        )
        
        # Простий inline keyboard
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="😂 Жарт", callback_data="get_joke")],
            [InlineKeyboardButton(text="🔥 Мем", callback_data="get_meme")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats")],
            [InlineKeyboardButton(text="👤 Профіль", callback_data="show_profile")]
        ])
        
        await callback.message.edit_text(welcome_text, reply_markup=keyboard)
    
    @dp.callback_query(F.data == "get_joke")
    async def callback_get_joke(callback: CallbackQuery):
        """Callback отримання жарту"""
        await callback.answer()
        
        import random
        jokes: List[str] = [
            "😂 Програміст у кафе:\n- Каву?\n- Так.\n- Цукор?\n- Ні, boolean!",
            "🎯 Купую iPhone:\n- Не загубіть!\n- Find My iPhone є!\n- А якщо не знайде?\n- Москалі вкрали!",
            "💻 Співбесіда:\n- Розкажіть про себе.\n- Fullstack.\n- Що вмієте?\n- HTML!"
        ]
        
        joke = random.choice(jokes)
        await callback.message.edit_text(f"😄 <b>Жарт:</b>\n\n{joke}")
    
    @dp.callback_query(F.data == "get_meme")
    async def callback_get_meme(callback: CallbackQuery):
        """Callback отримання мему"""
        await callback.answer()
        
        import random
        memes: List[str] = [
            "🤣 Wi-Fi на роботі швидший за домашній:\n*здивований кіт*",
            "😂 Настрій коли п'ятниця:\n*танцююча людина*",
            "🎮 'Останній раз граєш':\n*хитра усмішка*"
        ]
        
        meme = random.choice(memes)
        await callback.message.edit_text(f"🔥 <b>Мем:</b>\n\n{meme}")
    
    @dp.callback_query(F.data == "show_stats")
    async def callback_show_stats(callback: CallbackQuery):
        """Callback показу статистики"""
        await callback.answer()
        
        stats_text = (
            "📊 <b>СТАТИСТИКА</b>\n\n"
            "⚠️ Fallback режим\n\n"
            "🤖 Бот: Активний\n"
            "💾 БД: Недоступна\n"
            "🎮 Режим: Fallback\n\n"
            "💡 Для повної статистики потрібна БД"
        )
        
        await callback.message.edit_text(stats_text)
    
    @dp.callback_query(F.data == "show_profile")
    async def callback_show_profile(callback: CallbackQuery):
        """Callback показу профілю"""
        await callback.answer()
        
        user = callback.from_user
        profile_text = (
            f"👤 <b>ПРОФІЛЬ</b>\n\n"
            f"👨‍💼 Ім'я: {user.first_name or 'Невідомий'}\n"
            f"📱 Username: @{user.username or 'відсутній'}\n"
            f"🆔 ID: {user.id}\n\n"
            f"⚠️ Fallback режим\n"
            f"🎯 Бали: недоступно\n"
            f"🏆 Ранг: недоступно"
        )
        
        await callback.message.edit_text(profile_text)
    
    # Універсальний обробник невідомих callback'ів
    @dp.callback_query()
    async def universal_callback_handler(callback: CallbackQuery):
        """Обробник всіх інших callback'ів"""
        await callback.answer()
        
        unknown_text = (
            f"🤖 <b>Невідома дія</b>\n\n"
            f"Callback: <code>{callback.data}</code>\n\n"
            f"⚠️ Функція може бути недоступна в fallback режимі.\n"
            f"Спробуйте використати команди або зверніться до адміністратора."
        )
        
        await callback.message.answer(unknown_text)
    
    logger.info("✅ Universal callback handlers зареєстровано")

# ===== ДІАГНОСТИЧНІ ФУНКЦІЇ =====

def check_handlers_status() -> Dict[str, Any]:
    """Перевірка статусу всіх хендлерів"""
    status: Dict[str, Any] = {
        "basic_commands": False,
        "admin_panel": False,
        "content": False,
        "duels": False,
        "moderation": False,
        "gamification": False,
        "errors": []
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
            status[module_name.replace("_handlers", "")] = True
        except ImportError as e:
            status["errors"].append(f"{module_name}: {e}")
    
    return status

def get_handlers_summary() -> Dict[str, Any]:
    """Отримання резюме стану хендлерів"""
    status = check_handlers_status()
    
    total_modules = 6
    available_modules = sum(1 for v in status.values() if isinstance(v, bool) and v)
    
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