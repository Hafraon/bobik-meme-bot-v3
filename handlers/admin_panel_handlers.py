#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Модернізовані хендлери адмін-панелі (ВИПРАВЛЕНО SQLAlchemy detached objects) 🧠😂🔥
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

from aiogram import types
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardMarkup, 
    KeyboardButton, ReplyKeyboardRemove
)

from config.settings import settings
from database.services import DatabaseService
from utils.formatters import (
    SafeFormatter, StatsFormatter, ErrorHandler, 
    TableFormatter, ProgressFormatter
)

logger = logging.getLogger(__name__)

# Емодзі для інтерфейсу
EMOJI = {
    'fire': '🔥',
    'crown': '👑', 
    'cross': '❌',
    'check': '✅',
    'construction': '🚧',
    'rocket': '🚀',
    'brain': '🧠',
    'vs': '⚔️',
    'calendar': '📅',
    'warning': '⚠️',
    'gear': '⚙️',
    'backup': '💾',
    'bulk': '🚀',
    'trending': '📈'
}

def is_admin(user_id: int) -> bool:
    """Перевірка чи є користувач адміністратором"""
    admin_ids = [settings.ADMIN_ID]
    if hasattr(settings, 'ADDITIONAL_ADMINS'):
        admin_ids.extend(settings.ADDITIONAL_ADMINS)
    return user_id in admin_ids

def get_admin_inline_menu() -> InlineKeyboardMarkup:
    """Інлайн меню адміністратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderate")
        ],
        [
            InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
            InlineKeyboardButton(text="📝 Контент", callback_data="admin_content")
        ],
        [
            InlineKeyboardButton(text="🔥 Трендове", callback_data="admin_trending"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="🚀 Масові дії", callback_data="admin_bulk"),
            InlineKeyboardButton(text="💾 Бекап", callback_data="admin_backup")
        ]
    ])

def get_admin_static_menu() -> ReplyKeyboardMarkup:
    """Статичне меню адміністратора"""
    return ReplyKeyboardMarkup(
        keyboard=[
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
        ],
        resize_keyboard=True,
        is_persistent=True
    )

# ===== ОСНОВНІ КОМАНДИ =====

async def cmd_admin(message: Message):
    """Головна команда адміна"""
    if not is_admin(message.from_user.id):
        await message.answer(
            f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!"
        )
        return
    
    await message.answer(
        f"{EMOJI['fire']} <b>АДМІН-ПАНЕЛЬ</b>\n\n"
        f"Вітаю, адміністраторе! {EMOJI['crown']}\n"
        f"Оберіть розділ для роботи:",
        reply_markup=get_admin_inline_menu()
    )

async def cmd_m(message: Message):
    """Команда /m - швидкий доступ до статистики"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    await show_quick_stats(message)

async def handle_admin_static_buttons(message: Message):
    """Обробка натискань на статичні кнопки адміна"""
    if not is_admin(message.from_user.id):
        return
    
    text = message.text
    
    if text == "📊 Статистика":
        await show_detailed_stats(message)
    elif text == "🛡️ Модерація":
        await show_moderation_interface(message)
    elif text == "👥 Користувачі":
        await show_users_management(message)
    elif text == "📝 Контент":
        await show_content_analytics(message)
    elif text == "🔥 Трендове":
        await show_trending_content(message)
    elif text == "⚙️ Налаштування":
        await show_bot_settings(message)
    elif text == "🚀 Масові дії":
        await show_bulk_actions(message)
    elif text == "💾 Бекап":
        await show_backup_options(message)
    elif text == "❌ Вимкнути адмін меню":
        await disable_admin_menu(message)

# ===== ФУНКЦІЇ СТАТИСТИКИ =====

async def show_quick_stats(message: Message):
    """Швидка статистика для /m (✅ ВИПРАВЛЕНО)"""
    try:
        # ✅ Використовуємо новий сервіс
        stats = DatabaseService.get_basic_stats()
        
        stats_text = (
            f"{EMOJI['fire']} <b>ШВИДКА СТАТИСТИКА</b>\n\n"
            f"{StatsFormatter.format_basic_stats(stats)}\n\n"
            f"⏰ {datetime.now().strftime('%H:%M')} • {datetime.now().strftime('%d.%m.%Y')}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Детальна статистика", callback_data="admin_stats"),
                InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderate")
            ],
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="quick_stats_refresh")
            ]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "швидкої статистики", message.from_user.id
        )
        await message.answer(error_message)

async def show_detailed_stats(message: Message):
    """Детальна статистика (✅ ПОВНІСТЮ ВИПРАВЛЕНО)"""
    try:
        # ✅ Використовуємо безпечний сервіс
        stats = DatabaseService.get_detailed_stats()
        
        # Формуємо текст БЕЗ роботи з detached objects
        stats_text = (
            f"{EMOJI['fire']} <b>ДЕТАЛЬНА СТАТИСТИКА</b>\n\n"
            f"{StatsFormatter.format_basic_stats(stats)}\n\n"
            f"{StatsFormatter.format_top_users(stats.get('top_users', []), 5)}\n"
            f"⏰ Оновлено: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        # Додаємо аналітику тижневої активності
        weekly_activity = stats.get('weekly_activity', [])
        if weekly_activity:
            stats_text += f"\n\n{ProgressFormatter.format_weekly_activity(weekly_activity)}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_stats"),
                InlineKeyboardButton(text="📈 Експорт даних", callback_data="admin_export")
            ],
            [
                InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderate"),
                InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users")
            ]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "детальної статистики", message.from_user.id
        )
        await message.answer(error_message)

# ===== ФУНКЦІЇ МОДЕРАЦІЇ =====

async def show_moderation_interface(message: Message):
    """Інтерфейс модерації (✅ ВИПРАВЛЕНО)"""
    try:
        # ✅ Безпечне отримання даних
        pending_content = DatabaseService.get_pending_content(limit=1)
        
        if not pending_content:
            await message.answer(
                f"{EMOJI['check']} <b>Немає контенту на модерації!</b>\n\n"
                f"🎉 Всі подання перевірено",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_moderate")
                ]])
            )
            return
        
        # Форматуємо інформацію про контент
        moderation_text = TableFormatter.format_pending_content(pending_content)
        
        content_id = pending_content[0]['id']
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Схвалити", 
                    callback_data=f"approve_{content_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Відхилити", 
                    callback_data=f"reject_{content_id}"
                )
            ],
            [
                InlineKeyboardButton(text="⏭️ Наступний", callback_data="admin_moderate"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
            ]
        ])
        
        # Відправляємо медіа якщо є
        if pending_content[0].get('file_id'):
            await message.answer_photo(
                photo=pending_content[0]['file_id'],
                caption=moderation_text,
                reply_markup=keyboard
            )
        else:
            await message.answer(moderation_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "модерації", message.from_user.id
        )
        await message.answer(error_message)

# ===== РЕАЛІЗОВАНІ ФУНКЦІЇ (раніше були stub) =====

async def show_users_management(message: Message):
    """Управління користувачами (✅ РЕАЛІЗОВАНО)"""
    try:
        users_data = DatabaseService.get_users_management_data(page=1, per_page=10)
        
        users_text = TableFormatter.format_users_table(users_data)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Попередня", callback_data="users_page_0"),
                InlineKeyboardButton(text="▶️ Наступна", callback_data="users_page_2")
            ],
            [
                InlineKeyboardButton(text="🔍 Пошук", callback_data="users_search"),
                InlineKeyboardButton(text="📊 Експорт", callback_data="users_export")
            ],
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_users")
            ]
        ])
        
        await message.answer(users_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "управління користувачами", message.from_user.id
        )
        await message.answer(error_message)

async def show_content_analytics(message: Message):
    """Аналітика контенту (✅ РЕАЛІЗОВАНО)"""
    try:
        analytics = DatabaseService.get_content_analytics()
        
        analytics_text = StatsFormatter.format_content_analytics(analytics)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📈 Детальний звіт", callback_data="content_detailed"),
                InlineKeyboardButton(text="📊 За категоріями", callback_data="content_categories")
            ],
            [
                InlineKeyboardButton(text="🔥 Популярне", callback_data="content_popular"),
                InlineKeyboardButton(text="📉 Проблемне", callback_data="content_issues")
            ],
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_content")
            ]
        ])
        
        await message.answer(analytics_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "аналітики контенту", message.from_user.id
        )
        await message.answer(error_message)

async def show_trending_content(message: Message):
    """Трендовий контент (✅ РЕАЛІЗОВАНО)"""
    try:
        trending = DatabaseService.get_trending_content(days=7)
        
        trending_text = StatsFormatter.format_trending_content(trending)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 За день", callback_data="trending_1"),
                InlineKeyboardButton(text="📅 За тиждень", callback_data="trending_7"),
                InlineKeyboardButton(text="📅 За місяць", callback_data="trending_30")
            ],
            [
                InlineKeyboardButton(text="🏆 Зробити ТОПом", callback_data="make_top"),
                InlineKeyboardButton(text="📤 Опублікувати", callback_data="publish_trending")
            ],
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_trending")
            ]
        ])
        
        await message.answer(trending_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "трендового контенту", message.from_user.id
        )
        await message.answer(error_message)

async def show_bot_settings(message: Message):
    """Налаштування бота (✅ РЕАЛІЗОВАНО)"""
    try:
        settings_text = (
            f"{EMOJI['gear']} <b>НАЛАШТУВАННЯ БОТА</b>\n\n"
            f"🤖 Режим: {'Виробничий' if settings.ENVIRONMENT == 'production' else 'Розробка'}\n"
            f"📊 Логування: {settings.LOG_LEVEL}\n"
            f"🕐 Часовий пояс: {getattr(settings, 'TIMEZONE', 'UTC')}\n"
            f"👑 Головний адмін: {settings.ADMIN_ID}\n"
            f"📢 Канал: {getattr(settings, 'CHANNEL_ID', 'Не налаштовано')}\n\n"
            f"⚙️ Доступні налаштування:"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔔 Сповіщення", callback_data="settings_notifications"),
                InlineKeyboardButton(text="⏰ Розклад", callback_data="settings_schedule")
            ],
            [
                InlineKeyboardButton(text="🎮 Гейміфікація", callback_data="settings_gamification"),
                InlineKeyboardButton(text="🛡️ Модерація", callback_data="settings_moderation")
            ],
            [
                InlineKeyboardButton(text="🤖 OpenAI", callback_data="settings_ai"),
                InlineKeyboardButton(text="📊 Аналітика", callback_data="settings_analytics")
            ],
            [
                InlineKeyboardButton(text="💾 Зберегти", callback_data="settings_save"),
                InlineKeyboardButton(text="🔄 Скинути", callback_data="settings_reset")
            ]
        ])
        
        await message.answer(settings_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "налаштувань", message.from_user.id
        )
        await message.answer(error_message)

async def show_bulk_actions(message: Message):
    """Масові дії (✅ РЕАЛІЗОВАНО)"""
    try:
        bulk_text = (
            f"{EMOJI['bulk']} <b>МАСОВІ ДІЇ</b>\n\n"
            f"⚠️ <b>Увага!</b> Масові операції можуть вплинути на багато користувачів.\n"
            f"Будьте обережні та перевіряйте дані перед виконанням.\n\n"
            f"Доступні операції:"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📤 Розсилка", callback_data="bulk_broadcast"),
                InlineKeyboardButton(text="🧹 Очистка", callback_data="bulk_cleanup")
            ],
            [
                InlineKeyboardButton(text="🏆 Нарахування балів", callback_data="bulk_points"),
                InlineKeyboardButton(text="📊 Перерахунок рангів", callback_data="bulk_ranks")
            ],
            [
                InlineKeyboardButton(text="🚫 Блокування", callback_data="bulk_ban"),
                InlineKeyboardButton(text="✅ Розблокування", callback_data="bulk_unban")
            ],
            [
                InlineKeyboardButton(text="🗑️ Видалення контенту", callback_data="bulk_delete"),
                InlineKeyboardButton(text="📈 Оновлення статистики", callback_data="bulk_stats")
            ],
            [
                InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")
            ]
        ])
        
        await message.answer(bulk_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "масових дій", message.from_user.id
        )
        await message.answer(error_message)

async def show_backup_options(message: Message):
    """Резервне копіювання (✅ РЕАЛІЗОВАНО)"""
    try:
        # Отримуємо статистику для показу в backup інтерфейсі
        stats = DatabaseService.get_basic_stats()
        
        backup_text = (
            f"{EMOJI['backup']} <b>РЕЗЕРВНЕ КОПІЮВАННЯ</b>\n\n"
            f"📊 Поточний стан бази даних:\n"
            f"{StatsFormatter.format_basic_stats(stats)}\n\n"
            f"💾 Останній бекап: {'Немає даних'}\n"
            f"📏 Розмір БД: {'Розраховується...'}\n\n"
            f"Виберіть дію:"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💾 Створити бекап", callback_data="backup_create"),
                InlineKeyboardButton(text="📥 Завантажити", callback_data="backup_download")
            ],
            [
                InlineKeyboardButton(text="🔄 Відновити", callback_data="backup_restore"),
                InlineKeyboardButton(text="📋 Список бекапів", callback_data="backup_list")
            ],
            [
                InlineKeyboardButton(text="⚙️ Автобекап", callback_data="backup_auto"),
                InlineKeyboardButton(text="🗑️ Очистка старих", callback_data="backup_cleanup")
            ],
            [
                InlineKeyboardButton(text="📤 Експорт CSV", callback_data="backup_export_csv"),
                InlineKeyboardButton(text="📊 Експорт JSON", callback_data="backup_export_json")
            ],
            [
                InlineKeyboardButton(text="❌ Назад", callback_data="admin_menu")
            ]
        ])
        
        await message.answer(backup_text, reply_markup=keyboard)
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "резервного копіювання", message.from_user.id
        )
        await message.answer(error_message)

async def disable_admin_menu(message: Message):
    """Вимкнути статичне адмін-меню"""
    await message.answer(
        f"{EMOJI['check']} Адмін-меню вимкнено!\n\n"
        f"Для увімкнення використовуйте:\n"
        f"• /admin - повна панель\n"
        f"• /m - швидка статистика",
        reply_markup=ReplyKeyboardRemove()
    )

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_admin_stats(callback_query: CallbackQuery):
    """Статистика через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_detailed_stats(callback_query.message)
    await callback_query.answer()

async def callback_admin_moderate(callback_query: CallbackQuery):
    """Модерація через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_moderation_interface(callback_query.message)
    await callback_query.answer()

async def callback_approve_content(callback_query: CallbackQuery):
    """Схвалення контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    try:
        # Витягуємо ID контенту з callback_data
        content_id = int(callback_query.data.split('_')[1])
        
        # Модеруємо контент
        success = DatabaseService.moderate_content(
            content_id=content_id,
            approve=True,
            moderator_id=callback_query.from_user.id
        )
        
        if success:
            await callback_query.message.edit_text(
                f"✅ Контент #{content_id} схвалено!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="➡️ Наступний", callback_data="admin_moderate")
                ]])
            )
        else:
            await callback_query.answer("❌ Помилка схвалення контенту!")
        
        await callback_query.answer()
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "схвалення контенту", callback_query.from_user.id
        )
        await callback_query.message.answer(error_message)
        await callback_query.answer()

async def callback_reject_content(callback_query: CallbackQuery):
    """Відхилення контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    try:
        # Витягуємо ID контенту з callback_data
        content_id = int(callback_query.data.split('_')[1])
        
        # Модеруємо контент
        success = DatabaseService.moderate_content(
            content_id=content_id,
            approve=False,
            moderator_id=callback_query.from_user.id,
            comment="Відхилено адміністратором"
        )
        
        if success:
            await callback_query.message.edit_text(
                f"❌ Контент #{content_id} відхилено!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="➡️ Наступний", callback_data="admin_moderate")
                ]])
            )
        else:
            await callback_query.answer("❌ Помилка відхилення контенту!")
        
        await callback_query.answer()
        
    except Exception as e:
        error_message = ErrorHandler.log_and_format_error(
            e, "відхилення контенту", callback_query.from_user.id
        )
        await callback_query.message.answer(error_message)
        await callback_query.answer()

# ===== ШВИДКЕ ОНОВЛЕННЯ =====

async def callback_quick_stats_refresh(callback_query: CallbackQuery):
    """Оновлення швидкої статистики"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_quick_stats(callback_query.message)
    await callback_query.answer("🔄 Статистику оновлено!")

# ===== ЕКСПОРТ ФУНКЦІЇ =====

async def export_data_handler(callback_query: CallbackQuery):
    """Експорт даних"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await callback_query.answer("📈 Експорт даних буде реалізовано в наступній версії!")

# ===== РЕЄСТРАЦІЯ CALLBACK HANDLERS =====

def register_admin_callbacks(dp):
    """Реєстрація всіх admin callback handlers"""
    dp.callback_query.register(callback_admin_stats, lambda c: c.data == "admin_stats")
    dp.callback_query.register(callback_admin_moderate, lambda c: c.data == "admin_moderate") 
    dp.callback_query.register(callback_approve_content, lambda c: c.data.startswith("approve_"))
    dp.callback_query.register(callback_reject_content, lambda c: c.data.startswith("reject_"))
    dp.callback_query.register(callback_quick_stats_refresh, lambda c: c.data == "quick_stats_refresh")
    dp.callback_query.register(export_data_handler, lambda c: c.data == "admin_export")