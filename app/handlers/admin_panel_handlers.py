#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👑 ПОЛІПШЕНА АДМІН ПАНЕЛЬ З СТАТИЧНИМ МЕНЮ 👑

НОВІ ФУНКЦІЇ:
✅ Статичне меню з кнопками
✅ Розширена статистика
✅ Управління користувачами
✅ Модерація контенту
✅ Масові дії
✅ Бекап та налаштування
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from aiogram import F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Перевірка адміністратора"""
    try:
        from config.settings import ALL_ADMIN_IDS
        return user_id in ALL_ADMIN_IDS
    except ImportError:
        admin_id = int(os.getenv("ADMIN_ID", 603047391))
        return user_id == admin_id

def get_admin_static_menu() -> ReplyKeyboardMarkup:
    """Створення статичного адмін меню"""
    keyboard = [
        [
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="🛡️ Модерація")
        ],
        [
            KeyboardButton(text="👥 Користувачі"),
            KeyboardButton(text="📝 Контент")
        ],
        [
            KeyboardButton(text="🔥 Трендове"),
            KeyboardButton(text="⚙️ Налаштування")
        ],
        [
            KeyboardButton(text="🚀 Масові дії"),
            KeyboardButton(text="💾 Бекап")
        ],
        [
            KeyboardButton(text="❌ Вимкнути адмін меню")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True
    )

def get_admin_inline_menu() -> InlineKeyboardMarkup:
    """Inline меню для адмін панелі"""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Загальна статистика", callback_data="admin_stats_general"),
            InlineKeyboardButton(text="👥 Статистика користувачів", callback_data="admin_stats_users")
        ],
        [
            InlineKeyboardButton(text="📝 Модерація контенту", callback_data="admin_moderate_content"),
            InlineKeyboardButton(text="⚔️ Управління дуелями", callback_data="admin_manage_duels")
        ],
        [
            InlineKeyboardButton(text="🚀 Масові дії", callback_data="admin_mass_actions"),
            InlineKeyboardButton(text="⚙️ Налаштування бота", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="💾 Бекап БД", callback_data="admin_backup"),
            InlineKeyboardButton(text="🔄 Перезапуск", callback_data="admin_restart")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def get_bot_statistics() -> Dict[str, Any]:
    """Отримання статистики бота"""
    try:
        # Спроба отримання статистики з БД
        from database.database import get_database_stats, is_database_available
        
        if is_database_available():
            db_stats = await get_database_stats()
            return {
                "source": "database",
                "users_total": db_stats.get("users_total", 0),
                "users_active": db_stats.get("users_active", 0),
                "content_total": db_stats.get("content_total", 0),
                "content_approved": db_stats.get("content_approved", 0),
                "content_pending": db_stats.get("content_pending", 0),
                "duels_total": db_stats.get("duels_total", 0),
                "duels_active": db_stats.get("duels_active", 0),
                "database_status": "✅ Підключена"
            }
        else:
            return {
                "source": "fallback",
                "users_total": "Н/Д",
                "users_active": "Н/Д", 
                "content_total": "Н/Д",
                "content_approved": "Н/Д",
                "content_pending": "Н/Д",
                "duels_total": "Н/Д",
                "duels_active": "Н/Д",
                "database_status": "❌ Недоступна"
            }
    except Exception as e:
        logger.error(f"❌ Помилка отримання статистики: {e}")
        return {
            "source": "error",
            "error": str(e),
            "database_status": "❌ Помилка"
        }

async def get_system_info() -> Dict[str, Any]:
    """Системна інформація"""
    import psutil
    import sys
    
    try:
        # Інформація про систему
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "memory_total": f"{memory.total / (1024**3):.1f} GB",
            "memory_used": f"{memory.used / (1024**3):.1f} GB", 
            "memory_percent": f"{memory.percent:.1f}%",
            "disk_total": f"{disk.total / (1024**3):.1f} GB",
            "disk_used": f"{disk.used / (1024**3):.1f} GB",
            "disk_percent": f"{(disk.used/disk.total)*100:.1f}%",
            "uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
        }
    except Exception as e:
        logger.error(f"❌ Помилка системної інформації: {e}")
        return {"error": str(e)}

# ===== КОМАНДИ АДМІН ПАНЕЛІ =====

async def cmd_admin(message: Message):
    """Головна команда адмін панелі"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено. Тільки для адміністраторів.")
        return
    
    stats = await get_bot_statistics()
    system = await get_system_info()
    
    # Формуємо статистику
    text = f"👑 <b>АДМІН ПАНЕЛЬ</b>\n\n"
    
    text += f"📊 <b>СТАТИСТИКА БОТА:</b>\n"
    text += f"👥 Користувачі: {stats.get('users_total', 'Н/Д')} (активні: {stats.get('users_active', 'Н/Д')})\n"
    text += f"📝 Контент: {stats.get('content_total', 'Н/Д')} (схвалено: {stats.get('content_approved', 'Н/Д')})\n"
    text += f"⚔️ Дуелі: {stats.get('duels_total', 'Н/Д')} (активні: {stats.get('duels_active', 'Н/Д')})\n"
    text += f"💾 БД: {stats.get('database_status', 'Невідомо')}\n\n"
    
    if 'error' not in system:
        text += f"🖥️ <b>СИСТЕМА:</b>\n"
        text += f"🐍 Python: {system.get('python_version', 'Н/Д')}\n"
        text += f"💾 RAM: {system.get('memory_used', 'Н/Д')} / {system.get('memory_total', 'Н/Д')} ({system.get('memory_percent', 'Н/Д')})\n"
        text += f"💿 Диск: {system.get('disk_used', 'Н/Д')} / {system.get('disk_total', 'Н/Д')} ({system.get('disk_percent', 'Н/Д')})\n"
        text += f"⏱️ Uptime: {system.get('uptime', 'Н/Д')}\n\n"
    
    text += f"⚡ <b>ШВИДКІ ДІЇ:</b>\n"
    text += f"Використовуйте кнопки нижче або статичне меню для управління ботом.\n\n"
    text += f"🕐 Оновлено: {datetime.now().strftime('%H:%M:%S')}"
    
    await message.answer(
        text,
        reply_markup=get_admin_inline_menu(),
        parse_mode="HTML"
    )

async def cmd_admin_menu(message: Message):
    """Показати статичне адмін меню"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено.")
        return
    
    await message.answer(
        "👑 <b>АДМІН МЕНЮ АКТИВОВАНО</b>\n\n"
        "Тепер ви можете використовувати кнопки нижче для швидкого доступу до функцій адміністрування.\n\n"
        "📱 Кнопки залишаться доступними до вимкнення меню.",
        reply_markup=get_admin_static_menu(),
        parse_mode="HTML"
    )

# ===== ОБРОБКА СТАТИЧНИХ КНОПОК =====

async def handle_admin_static_buttons(message: Message):
    """Обробка натискань статичних кнопок адмін меню"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено.")
        return
    
    text = message.text
    
    if text == "📊 Статистика":
        await show_detailed_statistics(message)
    elif text == "🛡️ Модерація":
        await show_moderation_panel(message)
    elif text == "👥 Користувачі":
        await show_users_management(message)
    elif text == "📝 Контент":
        await show_content_management(message)
    elif text == "🔥 Трендове":
        await show_trending_content(message)
    elif text == "⚙️ Налаштування":
        await show_bot_settings(message)
    elif text == "🚀 Масові дії":
        await show_mass_actions(message)
    elif text == "💾 Бекап":
        await show_backup_options(message)
    elif text == "❌ Вимкнути адмін меню":
        await message.answer(
            "✅ Адмін меню вимкнено.\n\n"
            "Використовуйте /admin для повернення до панелі.",
            reply_markup=ReplyKeyboardRemove()
        )

# ===== ДЕТАЛЬНІ ФУНКЦІЇ ПАНЕЛЕЙ =====

async def show_detailed_statistics(message: Message):
    """Показати детальну статистику"""
    stats = await get_bot_statistics()
    
    text = "📊 <b>ДЕТАЛЬНА СТАТИСТИКА</b>\n\n"
    
    if stats.get("source") == "database":
        text += "💾 <b>База даних:</b> ✅ Підключена\n\n"
        text += f"👥 <b>Користувачі:</b>\n"
        text += f"• Всього: {stats['users_total']}\n"
        text += f"• Активні: {stats['users_active']}\n"
        text += f"• Неактивні: {stats['users_total'] - stats['users_active']}\n\n"
        
        text += f"📝 <b>Контент:</b>\n"
        text += f"• Всього: {stats['content_total']}\n"
        text += f"• Схвалено: {stats['content_approved']}\n"
        text += f"• На модерації: {stats['content_pending']}\n\n"
        
        text += f"⚔️ <b>Дуелі:</b>\n"
        text += f"• Всього: {stats['duels_total']}\n"
        text += f"• Активні: {stats['duels_active']}\n"
    else:
        text += "💾 <b>База даних:</b> ❌ Недоступна\n\n"
        text += "⚠️ Статистика недоступна без підключення до БД.\n"
        text += "Для отримання детальної статистики необхідно:\n"
        text += "• Перевірити DATABASE_URL\n"
        text += "• Переконатися що PostgreSQL працює\n"
        text += "• Перезапустити бота\n\n"
    
    text += f"🕐 Оновлено: {datetime.now().strftime('%H:%M:%S')}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_refresh_stats")],
        [InlineKeyboardButton(text="📈 Графіки", callback_data="admin_show_charts")],
        [InlineKeyboardButton(text="📋 Експорт", callback_data="admin_export_stats")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_moderation_panel(message: Message):
    """Панель модерації"""
    text = "🛡️ <b>ПАНЕЛЬ МОДЕРАЦІЇ</b>\n\n"
    
    try:
        from database.database import is_database_available
        if is_database_available():
            text += "✅ Модерація доступна\n\n"
            text += "📝 <b>Функції:</b>\n"
            text += "• Перегляд контенту на модерації\n"
            text += "• Схвалення/відхилення жартів\n"
            text += "• Управління користувачами\n"
            text += "• Видалення неприйнятного контенту\n\n"
            text += "Використовуйте кнопки нижче для початку модерації."
        else:
            text += "❌ Модерація недоступна без БД\n\n"
            text += "Для активації модерації потрібно:\n"
            text += "• Підключити PostgreSQL\n"
            text += "• Налаштувати таблиці БД\n"
            text += "• Перезапустити бота"
    except:
        text += "❌ Помилка підключення до системи модерації"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Контент на модерації", callback_data="moderate_pending")],
        [InlineKeyboardButton(text="🚫 Заблоковані користувачі", callback_data="moderate_blocked")],
        [InlineKeyboardButton(text="⚙️ Налаштування модерації", callback_data="moderate_settings")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_users_management(message: Message):
    """Управління користувачами"""
    text = "👥 <b>УПРАВЛІННЯ КОРИСТУВАЧАМИ</b>\n\n"
    
    try:
        from database.database import is_database_available
        if is_database_available():
            stats = await get_bot_statistics()
            text += f"📊 Всього користувачів: {stats.get('users_total', 0)}\n"
            text += f"✅ Активних: {stats.get('users_active', 0)}\n\n"
            text += "🔧 <b>Доступні дії:</b>\n"
            text += "• Пошук користувачів\n"
            text += "• Перегляд профілів\n"
            text += "• Зміна балів\n"
            text += "• Блокування/розблокування\n"
            text += "• Призначення ролей"
        else:
            text += "❌ Управління недоступне без БД"
    except:
        text += "❌ Помилка завантаження даних користувачів"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Пошук користувача", callback_data="users_search")],
        [InlineKeyboardButton(text="🏆 Топ користувачів", callback_data="users_top")],
        [InlineKeyboardButton(text="🚫 Заблоковані", callback_data="users_blocked")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_content_management(message: Message):
    """Управління контентом"""
    text = "📝 <b>УПРАВЛІННЯ КОНТЕНТОМ</b>\n\n"
    
    try:
        from database.database import is_database_available
        if is_database_available():
            stats = await get_bot_statistics()
            text += f"📊 Всього контенту: {stats.get('content_total', 0)}\n"
            text += f"✅ Схвалено: {stats.get('content_approved', 0)}\n"
            text += f"⏳ На модерації: {stats.get('content_pending', 0)}\n\n"
            text += "🔧 <b>Функції:</b>\n"
            text += "• Додавання нового контенту\n"
            text += "• Редагування існуючого\n"
            text += "• Видалення неактуального\n"
            text += "• Категоризація за типами\n"
            text += "• Статистика популярності"
        else:
            text += "❌ Управління недоступне без БД"
    except:
        text += "❌ Помилка завантаження контенту"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати контент", callback_data="content_add")],
        [InlineKeyboardButton(text="📝 Редагувати", callback_data="content_edit")],
        [InlineKeyboardButton(text="🗑️ Видалити", callback_data="content_delete")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_trending_content(message: Message):
    """Трендовий контент"""
    text = "🔥 <b>ТРЕНДОВИЙ КОНТЕНТ</b>\n\n"
    text += "📈 Аналіз популярності контенту за різні періоди\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 За сьогодні", callback_data="trending_today")],
        [InlineKeyboardButton(text="📅 За тиждень", callback_data="trending_week")],
        [InlineKeyboardButton(text="📅 За місяць", callback_data="trending_month")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_bot_settings(message: Message):
    """Налаштування бота"""
    text = "⚙️ <b>НАЛАШТУВАННЯ БОТА</b>\n\n"
    text += "🔧 Конфігурація основних параметрів роботи\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Налаштування бота", callback_data="settings_bot")],
        [InlineKeyboardButton(text="💾 Налаштування БД", callback_data="settings_database")],
        [InlineKeyboardButton(text="🎮 Гейміфікація", callback_data="settings_gamification")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_mass_actions(message: Message):
    """Масові дії"""
    text = "🚀 <b>МАСОВІ ДІЇ</b>\n\n"
    text += "⚠️ <b>УВАГА:</b> Ці дії впливають на всіх користувачів!\n\n"
    text += "📢 <b>Доступні дії:</b>\n"
    text += "• Розсилка повідомлень\n"
    text += "• Оновлення балів користувачів\n"
    text += "• Очищення старих даних\n"
    text += "• Резервне копіювання\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка", callback_data="mass_broadcast")],
        [InlineKeyboardButton(text="🧹 Очистка", callback_data="mass_cleanup")],
        [InlineKeyboardButton(text="💾 Бекап", callback_data="mass_backup")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_backup_options(message: Message):
    """Опції бекапу"""
    text = "💾 <b>БЕКАП ТА ВІДНОВЛЕННЯ</b>\n\n"
    text += "🔒 Резервне копіювання критичних даних\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 Створити бекап", callback_data="backup_create")],
        [InlineKeyboardButton(text="📥 Завантажити бекап", callback_data="backup_download")],
        [InlineKeyboardButton(text="🔄 Відновити дані", callback_data="backup_restore")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ===== CALLBACK ОБРОБНИКИ =====

async def handle_admin_callbacks(callback_query: CallbackQuery):
    """Обробка всіх адмін callback'ів"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    data = callback_query.data
    
    if data == "admin_refresh_stats":
        await callback_query.answer("🔄 Оновлення статистики...")
        await show_detailed_statistics(callback_query.message)
    
    elif data == "moderate_pending":
        await callback_query.answer("📝 Завантаження контенту...")
        await callback_query.message.answer("📝 Тут буде список контенту на модерації")
    
    elif data.startswith("admin_"):
        await callback_query.answer("⚙️ Функція в розробці")
        await callback_query.message.answer(f"🔧 Функція '{data}' буде додана в наступному оновленні")
    
    else:
        await callback_query.answer("❓ Невідома команда")

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_admin_handlers(dp: Dispatcher):
    """Реєстрація всіх адмін хендлерів"""
    
    # Команди
    dp.message.register(cmd_admin, Command("admin"))
    dp.message.register(cmd_admin_menu, Command("adminmenu"))
    
    # Статичні кнопки
    dp.message.register(
        handle_admin_static_buttons,
        F.text.in_([
            "📊 Статистика", "🛡️ Модерація", "👥 Користувачі", "📝 Контент",
            "🔥 Трендове", "⚙️ Налаштування", "🚀 Масові дії", "💾 Бекап",
            "❌ Вимкнути адмін меню"
        ])
    )
    
    # Callback запити
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("admin_"))
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("moderate_"))
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("users_"))
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("content_"))
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("settings_"))
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("mass_"))
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("backup_"))
    dp.callback_query.register(handle_admin_callbacks, F.data.startswith("trending_"))
    
    logger.info("✅ Адмін хендлери з статичним меню зареєстровано")

# ===== ЕКСПОРТ =====
__all__ = [
    'register_admin_handlers', 'is_admin', 'get_admin_static_menu',
    'cmd_admin', 'cmd_admin_menu'
]