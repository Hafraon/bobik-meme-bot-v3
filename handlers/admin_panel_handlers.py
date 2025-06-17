#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Статичне адмін-меню + розширена панель 🧠😂🔥
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

from config.settings import settings, EMOJI

logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Перевірка чи є користувач адміністратором"""
    return user_id == settings.ADMIN_ID

def get_admin_static_menu() -> ReplyKeyboardMarkup:
    """Статичне меню адміна (завжди видиме)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="🛡️ Модерація"),
                KeyboardButton(text="👥 Користувачі")
            ],
            [
                KeyboardButton(text="📝 Контент"),
                KeyboardButton(text="🔥 Трендове"),
                KeyboardButton(text="⚙️ Налаштування")
            ],
            [
                KeyboardButton(text="🚀 Масові дії"),
                KeyboardButton(text="💾 Бекап"),
                KeyboardButton(text="❌ Вимкнути адмін меню")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Оберіть дію або введіть команду..."
    )

def get_admin_inline_menu() -> InlineKeyboardMarkup:
    """Інлайн меню адміна (за командою /admin)"""
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
            InlineKeyboardButton(text="⭐ Популярне", callback_data="admin_popular")
        ],
        [
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings"),
            InlineKeyboardButton(text="📈 Аналітика", callback_data="admin_analytics")
        ],
        [
            InlineKeyboardButton(text="🚀 Масові дії", callback_data="admin_bulk"),
            InlineKeyboardButton(text="💾 Резервне копіювання", callback_data="admin_backup")
        ],
        [
            InlineKeyboardButton(text="❌ Закрити", callback_data="admin_close")
        ]
    ])

# ===== КОМАНДИ АДМІНА =====

async def cmd_admin(message: Message):
    """Команда /admin - повна адмін-панель"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
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
    
    # Показуємо швидку статистику
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
    """Швидка статистика для /m"""
    try:
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import User, Content, Rating
            
            # Швидкі метрики
            total_users = session.query(User).count()
            total_content = session.query(Content).count()
            pending_content = session.query(Content).filter(Content.status == "pending").count()
            
            # Сьогоднішня активність
            today = datetime.utcnow().date()
            today_ratings = session.query(Rating).filter(
                Rating.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
        
        stats_text = (
            f"{EMOJI['fire']} <b>ШВИДКА СТАТИСТИКА</b>\n\n"
            f"👥 Користувачів: {total_users}\n"
            f"📝 Контенту: {total_content}\n"
            f"⏳ На модерації: {pending_content}\n"
            f"💖 Оцінок сьогодні: {today_ratings}\n\n"
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
        logger.error(f"Помилка швидкої статистики: {e}")
        await message.answer(f"❌ Помилка отримання статистики: {e}")

async def show_detailed_stats(message: Message):
    """Детальна статистика"""
    try:
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import User, Content, Rating
            
            # Загальна статистика
            total_users = session.query(User).count()
            total_content = session.query(Content).count()
            pending_content = session.query(Content).filter(Content.status == "pending").count()
            approved_content = session.query(Content).filter(Content.status == "approved").count()
            
            # Статистика за сьогодні
            today = datetime.utcnow().date()
            today_ratings = session.query(Rating).filter(
                Rating.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
            
            # Активні користувачі за тиждень
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_users = session.query(User).filter(User.last_active >= week_ago).count()
            
            # Топ користувачі
            top_users = session.query(User).order_by(User.points.desc()).limit(5).all()
        
        stats_text = (
            f"{EMOJI['fire']} <b>ДЕТАЛЬНА СТАТИСТИКА БОТА</b>\n\n"
            f"👥 <b>Користувачі:</b>\n"
            f"• Всього: {total_users}\n"
            f"• Активні (7 днів): {active_users}\n\n"
            f"📝 <b>Контент:</b>\n"
            f"• Всього: {total_content}\n"
            f"• Схвалено: {approved_content}\n"
            f"• На модерації: {pending_content}\n\n"
            f"📊 <b>Сьогодні:</b>\n"
            f"• Оцінок: {today_ratings}\n\n"
            f"🏆 <b>Топ користувачі:</b>\n"
        )
        
        for i, user in enumerate(top_users, 1):
            name = user.first_name or user.username or f"ID{user.id}"
            stats_text += f"{i}. {name}: {user.points} балів\n"
        
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
        logger.error(f"Помилка детальної статистики: {e}")
        await message.answer(f"❌ Помилка статистики: {e}")

# ===== ФУНКЦІЇ МОДЕРАЦІЇ =====

async def show_moderation_interface(message: Message):
    """Інтерфейс модерації"""
    try:
        # Спробуємо отримати контент на модерації
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import Content, User
            
            pending_content = session.query(Content).filter(Content.status == "pending").all()
            
            if not pending_content:
                await message.answer(
                    f"{EMOJI['check']} <b>Немає контенту на модерації!</b>\n\n"
                    f"🎉 Всі подання перевірено",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_moderate")
                    ]])
                )
                return
            
            content = pending_content[0]  # Перший в черзі
            
            # Отримуємо інформацію про автора
            author = session.query(User).filter(User.id == content.author_id).first()
            
            author_name = "Невідомий"
            author_stats = "Статистика недоступна"
            
            if author:
                author_name = author.first_name or author.username or f"ID{author.id}"
                author_stats = f"Балів: {author.points}"
            
            content_type = "Анекдот" if content.content_type == "joke" else "Мем"
            
            moderation_text = (
                f"{EMOJI['brain']} <b>МОДЕРАЦІЯ КОНТЕНТУ</b>\n\n"
                f"📝 <b>Тип:</b> {content_type}\n"
                f"👤 <b>Автор:</b> {author_name}\n"
                f"📊 <b>Статистика:</b> {author_stats}\n"
                f"🕐 <b>Надіслано:</b> {content.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"📄 <b>Контент:</b>\n{content.text}\n\n"
                f"⏳ <b>В черзі:</b> {len(pending_content)} елементів"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Схвалити", callback_data=f"approve_{content.id}"),
                    InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{content.id}")
                ],
                [
                    InlineKeyboardButton(text="⏭️ Наступний", callback_data="admin_moderate"),
                    InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_moderate")
                ]
            ])
            
            await message.answer(moderation_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Помилка модерації: {e}")
        await message.answer(f"❌ Помилка модерації: {e}")

# ===== STUB ФУНКЦІЇ (поки не реалізовані) =====

async def show_users_management(message: Message):
    """Управління користувачами - поки заглушка"""
    await message.answer(f"{EMOJI['construction']} Функція в розробці...")

async def show_content_analytics(message: Message):
    """Аналітика контенту - поки заглушка"""
    await message.answer(f"{EMOJI['construction']} Функція в розробці...")

async def show_trending_content(message: Message):
    """Трендовий контент - поки заглушка"""
    await message.answer(f"{EMOJI['construction']} Функція в розробці...")

async def show_bot_settings(message: Message):
    """Налаштування бота - поки заглушка"""
    await message.answer(f"{EMOJI['construction']} Функція в розробці...")

async def show_bulk_actions(message: Message):
    """Масові дії - поки заглушка"""
    await message.answer(f"{EMOJI['construction']} Функція в розробці...")

async def show_backup_options(message: Message):
    """Бекап - поки заглушка"""
    await message.answer(f"{EMOJI['construction']} Функція в розробці...")

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
        content_id = int(callback_query.data.split("_")[1])
        
        # Схвалюємо контент в БД
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import Content
            
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                content.status = "approved"
                session.commit()
                
                await callback_query.answer(f"{EMOJI['check']} Контент схвалено!")
                
                # Показуємо наступний контент
                await show_moderation_interface(callback_query.message)
            else:
                await callback_query.answer("Контент не знайдено")
        
    except Exception as e:
        logger.error(f"Помилка схвалення: {e}")
        await callback_query.answer("Помилка схвалення")

async def callback_reject_content(callback_query: CallbackQuery):
    """Відхилення контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    try:
        content_id = int(callback_query.data.split("_")[1])
        
        # Відхиляємо контент в БД
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import Content
            
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                content.status = "rejected"
                session.commit()
                
                await callback_query.answer(f"{EMOJI['cross']} Контент відхилено!")
                
                # Показуємо наступний контент
                await show_moderation_interface(callback_query.message)
            else:
                await callback_query.answer("Контент не знайдено")
        
    except Exception as e:
        logger.error(f"Помилка відхилення: {e}")
        await callback_query.answer("Помилка відхилення")

async def callback_quick_stats_refresh(callback_query: CallbackQuery):
    """Оновлення швидкої статистики"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_quick_stats(callback_query.message)
    await callback_query.answer("🔄 Статистику оновлено!")

# ===== ФУНКЦІЯ АВТОМАТИЧНОГО ПОКАЗУ МЕНЮ ПРИ /start ДЛЯ АДМІНА =====

async def auto_show_admin_menu_on_start(message: Message):
    """Автоматично показати адмін-меню при /start для адміна"""
    if is_admin(message.from_user.id):
        # Показуємо статичне меню
        await message.answer(
            f"{EMOJI['crown']} <b>Режим адміністратора активовано!</b>\n\n"
            f"Використовуйте кнопки меню нижче або команди:\n"
            f"• /admin - повна панель\n"
            f"• /m - швидка статистика",
            reply_markup=get_admin_static_menu()
        )
        return True
    return False

def register_admin_handlers(dp: Dispatcher):
    """Реєстрація хендлерів адмін-панелі"""
    
    # Команди
    dp.message.register(cmd_admin, Command("admin"))
    dp.message.register(cmd_m, Command("m"))
    
    # Статичні кнопки адміна
    dp.message.register(
        handle_admin_static_buttons,
        F.text.in_([
            "📊 Статистика", "🛡️ Модерація", "👥 Користувачі",
            "📝 Контент", "🔥 Трендове", "⚙️ Налаштування",
            "🚀 Масові дії", "💾 Бекап", "❌ Вимкнути адмін меню"
        ])
    )
    
    # Callback запити
    dp.callback_query.register(callback_admin_stats, F.data == "admin_stats")
    dp.callback_query.register(callback_admin_moderate, F.data == "admin_moderate")
    dp.callback_query.register(callback_approve_content, F.data.startswith("approve_"))
    dp.callback_query.register(callback_reject_content, F.data.startswith("reject_"))
    dp.callback_query.register(callback_quick_stats_refresh, F.data == "quick_stats_refresh")
    
    logger.info("🔥 Хендлери адмін-панелі зареєстровано!")

# Експортуємо функцію для використання в basic_commands.py
__all__ = ['auto_show_admin_menu_on_start', 'register_admin_handlers']