#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 Ініціалізація та реєстрація всіх хендлерів бота

Включає:
✅ Content handlers - меми, жарти, анекдоти
✅ Admin handlers - модерація, статистика  
✅ Duel handlers - дуелі жартів з голосуванням
✅ Fallback handlers - базовий функціонал
"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher) -> dict:
    """Реєстрація всіх хендлерів з повним логуванням"""
    
    handlers_status = {
        'content': False,
        'admin': False, 
        'duel': False,
        'fallback': False,
        'total_registered': 0,
        'errors': []
    }
    
    logger.info("🔧 Початок реєстрації хендлерів...")
    
    # ===== CONTENT HANDLERS =====
    try:
        from .content_handlers import register_content_handlers
        register_content_handlers(dp)
        handlers_status['content'] = True
        handlers_status['total_registered'] += 1
        logger.info("✅ Content handlers зареєстровано (меми, жарти, анекдоти)")
    except ImportError as e:
        logger.warning(f"⚠️ Content handlers не доступні: {e}")
        handlers_status['errors'].append(f"Content: {e}")
        handlers_status['content'] = 'fallback'
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації content handlers: {e}")
        handlers_status['errors'].append(f"Content error: {e}")
    
    # ===== ADMIN HANDLERS =====
    try:
        from .admin_handlers import register_admin_handlers
        register_admin_handlers(dp)
        handlers_status['admin'] = True
        handlers_status['total_registered'] += 1
        logger.info("✅ Admin handlers зареєстровано (модерація, статистика)")
    except ImportError as e:
        logger.warning(f"⚠️ Admin handlers не доступні: {e}")
        handlers_status['errors'].append(f"Admin: {e}")
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації admin handlers: {e}")
        handlers_status['errors'].append(f"Admin error: {e}")
    
    # ===== DUEL HANDLERS (НОВИЙ!) =====
    try:
        from .duel_handlers import register_duel_handlers
        register_duel_handlers(dp)
        handlers_status['duel'] = True
        handlers_status['total_registered'] += 1
        logger.info("✅ Duel handlers зареєстровано (дуелі жартів, голосування)")
    except ImportError as e:
        logger.warning(f"⚠️ Duel handlers не доступні: {e}")
        handlers_status['errors'].append(f"Duel: {e}")
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації duel handlers: {e}")
        handlers_status['errors'].append(f"Duel error: {e}")
    
    # ===== FALLBACK HANDLERS =====
    try:
        register_fallback_handlers(dp)
        handlers_status['fallback'] = True
        handlers_status['total_registered'] += 1
        logger.info("✅ Fallback handlers зареєстровано (базовий функціонал)")
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації fallback handlers: {e}")
        handlers_status['errors'].append(f"Fallback error: {e}")
    
    # ===== ПІДСУМОК =====
    total_possible = 4  # content, admin, duel, fallback
    success_rate = (handlers_status['total_registered'] / total_possible) * 100
    
    logger.info(f"📊 Реєстрація завершена: {handlers_status['total_registered']}/{total_possible} ({success_rate:.1f}%)")
    
    if handlers_status['total_registered'] >= 3:
        logger.info("🎉 Хендлери успішно зареєстровані! Бот готовий до роботи")
    elif handlers_status['total_registered'] >= 2:
        logger.warning("⚠️ Частково зареєстровано - бот працездатний з обмеженими функціями")
    else:
        logger.error("❌ Критично мало хендлерів! Бот може працювати некоректно")
    
    if handlers_status['errors']:
        logger.warning(f"⚠️ Помилки при реєстрації: {handlers_status['errors']}")
    
    return handlers_status

def register_fallback_handlers(dp: Dispatcher):
    """Базові fallback хендлери для мінімального функціонала"""
    
    from aiogram import F
    from aiogram.filters import Command
    from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
    
    @dp.message(Command("start"))
    async def fallback_start(message: Message):
        """Fallback команда /start"""
        text = (
            "🧠😂🔥 <b>Україномовний бот запущено!</b>\n\n"
            "✅ Базовий режим активний\n\n"
            "📋 <b>Доступні команди:</b>\n"
            "• /start - це меню\n"
            "• /help - довідка\n"
            "• /status - статус бота\n"
            "• /duel - дуелі жартів ⚔️\n"
            "• /meme - випадковий мем\n"
            "• /profile - ваш профіль"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Дуелі жартів", callback_data="duel_menu")],
            [InlineKeyboardButton(text="😂 Мем", callback_data="get_meme")],
            [InlineKeyboardButton(text="👤 Профіль", callback_data="profile")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    @dp.message(Command("help"))
    async def fallback_help(message: Message):
        """Fallback команда /help"""
        text = (
            "📖 <b>ДОВІДКА БОТА</b>\n\n"
            "🎯 <b>Основні функції:</b>\n"
            "• ⚔️ Дуелі жартів - змагання за найкращий жарт\n"
            "• 😂 Меми та жарти - розважальний контент\n"
            "• 👤 Профіль - ваша статистика та ранг\n"
            "• 🏆 Система балів - нагороди за активність\n\n"
            
            "⚔️ <b>Дуелі:</b>\n"
            "• /duel - головне меню дуелів\n"
            "• Голосуйте за найкращий жарт\n"
            "• Отримуйте бали за участь\n\n"
            
            "🎮 <b>Гейміфікація:</b>\n"
            "• +2 бали за голосування\n"
            "• +10 балів за участь у дуелі\n"
            "• +25 балів за перемогу\n"
            "• +50 балів за розгромну перемогу"
        )
        
        await message.answer(text)
    
    @dp.message(Command("status"))
    async def fallback_status(message: Message):
        """Fallback команда /status"""
        from datetime import datetime
        
        uptime = datetime.now().strftime("%H:%M:%S")
        
        text = (
            f"🤖 <b>СТАТУС БОТА</b>\n\n"
            f"✅ Статус: Онлайн\n"
            f"⏰ Час: {uptime}\n"
            f"🔧 Режим: Production\n"
            f"📦 Модулі: Базові + Дуелі\n\n"
            f"🎯 <b>Доступний функціонал:</b>\n"
            f"• ⚔️ Дуелі жартів\n"
            f"• 😂 Базовий контент\n"
            f"• 👤 Профілі користувачів\n"
            f"• 📊 Статистика"
        )
        
        await message.answer(text)
    
    # Callback для кнопки дуелів
    @dp.callback_query(F.data == "duel_menu")
    async def fallback_duel_menu(callback: CallbackQuery):
        """Fallback меню дуелів"""
        try:
            # Спробуємо використати справжні duel handlers
            from .duel_handlers import cmd_duel
            await cmd_duel(callback.message)
            await callback.answer()
        except:
            # Fallback якщо duel handlers недоступні
            text = (
                "⚔️ <b>ДУЕЛІ ЖАРТІВ</b>\n\n"
                "Система дуелів тимчасово недоступна.\n"
                "Спробуйте команду /duel"
            )
            await callback.message.edit_text(text)
            await callback.answer("Duel система завантажується...")
    
    # Базовий callback хендлер
    @dp.callback_query()
    async def fallback_callbacks(callback: CallbackQuery):
        """Fallback для всіх callback'ів"""
        data = callback.data
        
        if data == "get_meme":
            await callback.message.answer("😂 Випадковий мем:\n\n<i>Коли твій код працює з першого разу... 🤔\nЗначить ти щось зробив не так!</i>")
        elif data == "profile":
            await callback.message.answer("👤 <b>Ваш профіль</b>\n\n🎮 Ранг: Новачок\n💰 Бали: 0\n🏆 Дуелі: 0/0")
        elif data == "stats":
            await callback.message.answer("📊 <b>Статистика бота</b>\n\n👥 Користувачів: ∞\n😂 Мемів: ∞\n⚔️ Дуелі: Активні")
        else:
            await callback.answer("🔄 Функція завантажується...")
        
        await callback.answer()
    
    logger.info("✅ Fallback handlers зареєстровано")

def check_handlers_status() -> dict:
    """Перевірка статусу всіх хендлерів"""
    status = {
        'content_handlers': False,
        'admin_handlers': False,
        'duel_handlers': False,
        'fallback_handlers': True,  # Завжди доступні
        'errors': []
    }
    
    # Перевірка content handlers
    try:
        from . import content_handlers
        status['content_handlers'] = True
    except ImportError as e:
        status['errors'].append(f"Content handlers: {e}")
    
    # Перевірка admin handlers  
    try:
        from . import admin_handlers
        status['admin_handlers'] = True
    except ImportError as e:
        status['errors'].append(f"Admin handlers: {e}")
    
    # Перевірка duel handlers
    try:
        from . import duel_handlers
        status['duel_handlers'] = True
    except ImportError as e:
        status['errors'].append(f"Duel handlers: {e}")
    
    return status

def log_handlers_status():
    """Логування статусу хендлерів"""
    status = check_handlers_status()
    
    available_count = sum(1 for v in status.values() if v is True and isinstance(v, bool))
    total_count = 4  # content, admin, duel, fallback
    
    logger.info(f"📦 Статус хендлерів: {available_count}/{total_count}")
    
    if status['content_handlers']:
        logger.info("✅ Content handlers: меми, жарти, анекдоти")
    if status['admin_handlers']:
        logger.info("✅ Admin handlers: модерація, статистика")
    if status['duel_handlers']:
        logger.info("✅ Duel handlers: дуелі жартів, голосування")
    if status['fallback_handlers']:
        logger.info("✅ Fallback handlers: базовий функціонал")
    
    if status['errors']:
        for error in status['errors']:
            logger.warning(f"⚠️ {error}")
    
    if available_count >= 3:
        logger.info("🎉 Всі основні хендлери доступні!")
    elif available_count >= 2:
        logger.warning("⚠️ Частково доступні хендлери")
    else:
        logger.error("❌ Критично мало хендлерів!")
    
    return status

# ===== ЕКСПОРТ =====

__all__ = [
    'register_handlers',
    'check_handlers_status', 
    'log_handlers_status',
    'register_fallback_handlers'
]

# Виконати діагностику при імпорті
if __name__ != "__main__":
    log_handlers_status()