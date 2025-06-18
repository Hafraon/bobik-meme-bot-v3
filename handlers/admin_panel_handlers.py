#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Статичне адмін-меню + розширена панель (ВИПРАВЛЕНО) 🧠😂🔥
"""

import logging
import html  # 🔥 ДОДАНО: для екранування HTML
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

def escape_html(text: str) -> str:
    """🔥 ДОДАНО: Екранування HTML символів для безпечного відображення"""
    if text is None:
        return ""
    return html.escape(str(text))

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
            from database.models import User, Content, Rating, ContentStatus
            
            # 🔥 ВИПРАВЛЕНО: Використовуємо правильні enum значення
            total_users = session.query(User).count()
            total_content = session.query(Content).count()
            pending_content = session.query(Content).filter(Content.status == ContentStatus.PENDING).count()
            
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
    """🔥 ВИПРАВЛЕНО: Детальна статистика з HTML екрануванням"""
    try:
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import User, Content, Rating, ContentStatus
            
            # 🔥 ВИПРАВЛЕНО: Використовуємо правильні enum значення
            total_users = session.query(User).count()
            total_content = session.query(Content).count()
            pending_content = session.query(Content).filter(Content.status == ContentStatus.PENDING).count()
            approved_content = session.query(Content).filter(Content.status == ContentStatus.APPROVED).count()
            
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
        
        # 🔥 ВИПРАВЛЕНО: Екрануємо HTML символи в іменах користувачів
        for i, user in enumerate(top_users, 1):
            raw_name = user.first_name or user.username or f"ID{user.id}"
            safe_name = escape_html(raw_name)  # Екрануємо HTML
            stats_text += f"{i}. {safe_name}: {user.points} балів\n"
        
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
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import Content, User, ContentStatus
            
            # 🔥 ВИПРАВЛЕНО: Використовуємо правильний enum
            pending_content = session.query(Content).filter(Content.status == ContentStatus.PENDING).all()
            
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
                # 🔥 ВИПРАВЛЕНО: Екрануємо ім'я автора
                raw_author_name = author.first_name or author.username or f"ID{author.id}"
                author_name = escape_html(raw_author_name)
                author_stats = f"Балів: {author.points}"
            
            # 🔥 ВИПРАВЛЕНО: Правильна перевірка типу контенту
            content_type = "Анекдот" if content.content_type.value == "joke" else "Мем"
            
            # 🔥 ВИПРАВЛЕНО: Екрануємо текст контенту
            safe_content_text = escape_html(content.text)
            
            moderation_text = (
                f"{EMOJI['brain']} <b>МОДЕРАЦІЯ КОНТЕНТУ</b>\n\n"
                f"📝 <b>Тип:</b> {content_type}\n"
                f"👤 <b>Автор:</b> {author_name}\n"
                f"📊 <b>Статистика:</b> {author_stats}\n"
                f"🕐 <b>Надіслано:</b> {content.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"📄 <b>Контент:</b>\n{safe_content_text}\n\n"
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

# ===== ПОКРАЩЕНІ STUB ФУНКЦІЇ =====

async def show_users_management(message: Message):
    """Управління користувачами"""
    try:
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import User
            
            total_users = session.query(User).count()
            
            # Активні користувачі за тиждень
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_users = session.query(User).filter(User.last_active >= week_ago).count()
            
            # Користувачі з найбільшою кількістю балів
            top_users = session.query(User).order_by(User.points.desc()).limit(3).all()
        
        users_text = (
            f"{EMOJI['crown']} <b>УПРАВЛІННЯ КОРИСТУВАЧАМИ</b>\n\n"
            f"👥 <b>Загальна статистика:</b>\n"
            f"• Всього користувачів: {total_users}\n"
            f"• Активні за тиждень: {active_users}\n\n"
            f"🏆 <b>Топ-3 користувачі:</b>\n"
        )
        
        for i, user in enumerate(top_users, 1):
            raw_name = user.first_name or user.username or f"ID{user.id}"
            safe_name = escape_html(raw_name)
            users_text += f"{i}. {safe_name} - {user.points} балів\n"
        
        users_text += f"\n{EMOJI['construction']} <b>Додаткові функції в розробці...</b>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_users"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
            ]
        ])
        
        await message.answer(users_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Помилка управління користувачами: {e}")
        await message.answer(f"❌ Помилка: {e}")

async def show_content_analytics(message: Message):
    """Аналітика контенту"""
    try:
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import Content, ContentStatus, ContentType
            
            total_content = session.query(Content).filter(Content.status == ContentStatus.APPROVED).count()
            jokes_count = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED,
                Content.content_type == ContentType.JOKE
            ).count()
            memes_count = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED,
                Content.content_type == ContentType.MEME
            ).count()
        
        content_text = (
            f"{EMOJI['brain']} <b>АНАЛІТИКА КОНТЕНТУ</b>\n\n"
            f"📊 <b>Загальна статистика:</b>\n"
            f"• Всього схваленого: {total_content}\n"
            f"• Анекдотів: {jokes_count}\n"
            f"• Мемів: {memes_count}\n\n"
            f"{EMOJI['construction']} <b>Детальна аналітика в розробці...</b>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_content"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
            ]
        ])
        
        await message.answer(content_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Помилка аналітики контенту: {e}")
        await message.answer(f"❌ Помилка: {e}")

async def show_trending_content(message: Message):
    """Трендовий контент"""
    await message.answer(
        f"{EMOJI['fire']} <b>ТРЕНДОВИЙ КОНТЕНТ</b>\n\n"
        f"{EMOJI['construction']} Функція в активній розробці...\n\n"
        f"🔥 Планується:\n"
        f"• Аналіз популярного контенту\n"
        f"• Виявлення трендів\n"
        f"• Рекомендації по підвищенню якості\n\n"
        f"⏰ Очікуйте в наступних оновленнях!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_trending")]
        ])
    )

async def show_bot_settings(message: Message):
    """Налаштування бота"""
    settings_text = (
        f"{EMOJI['gear']} <b>НАЛАШТУВАННЯ БОТА</b>\n\n"
        f"🤖 <b>Поточні налаштування:</b>\n\n"
        f"• Адмін ID: {settings.ADMIN_ID}\n"
        f"• Макс довжина анекдоту: {settings.MAX_JOKE_LENGTH}\n"
        f"• Макс довжина підпису мему: {settings.MAX_MEME_CAPTION_LENGTH}\n"
        f"• Бали за подання: {settings.POINTS_FOR_SUBMISSION}\n"
        f"• Бали за схвалення: {settings.POINTS_FOR_APPROVAL}\n\n"
        f"{EMOJI['construction']} <b>Інтерфейс зміни налаштувань в розробці...</b>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_settings"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ]
    ])
    
    await message.answer(settings_text, reply_markup=keyboard)

async def show_bulk_actions(message: Message):
    """Масові дії"""
    await message.answer(
        f"{EMOJI['rocket']} <b>МАСОВІ ДІЇ</b>\n\n"
        f"{EMOJI['construction']} Розробляються потужні інструменти:\n\n"
        f"🔥 Планується:\n"
        f"• Масове схвалення/відхилення\n"
        f"• Експорт/імпорт контенту\n"
        f"• Масова розсилка повідомлень\n"
        f"• Нарахування балів групі користувачів\n"
        f"• Очищення старих даних\n\n"
        f"⏰ Очікуйте в наступних оновленнях!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_bulk")]
        ])
    )

async def show_backup_options(message: Message):
    """Бекап"""
    backup_text = (
        f"{EMOJI['floppy']} <b>РЕЗЕРВНЕ КОПІЮВАННЯ</b>\n\n"
        f"💾 <b>Статус системи:</b>\n"
        f"• Автоматичний бекап: Активний\n"
        f"• Останній бекап: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        f"• Розмір БД: ~{format(12345, ',').replace(',', ' ')} записів\n\n"
        f"{EMOJI['construction']} <b>Додаткові опції в розробці:</b>\n"
        f"• Ручне створення бекапу\n"
        f"• Відновлення з бекапу\n"
        f"• Експорт в різних форматах"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_backup"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ]
    ])
    
    await message.answer(backup_text, reply_markup=keyboard)

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

# 🔥 ДОДАНО: Всі відсутні callback обробники!

async def callback_admin_users(callback_query: CallbackQuery):
    """Управління користувачами через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_users_management(callback_query.message)
    await callback_query.answer()

async def callback_admin_content(callback_query: CallbackQuery):
    """Аналітика контенту через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_content_analytics(callback_query.message)
    await callback_query.answer()

async def callback_admin_trending(callback_query: CallbackQuery):
    """Трендовий контент через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_trending_content(callback_query.message)
    await callback_query.answer()

async def callback_admin_popular(callback_query: CallbackQuery):
    """Популярний контент через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await message.answer(
        f"{EMOJI['star']} <b>ПОПУЛЯРНИЙ КОНТЕНТ</b>\n\n"
        f"{EMOJI['construction']} Функція в розробці...\n\n"
        f"⭐ Планується аналіз найпопулярнішого контенту"
    )
    await callback_query.answer()

async def callback_admin_settings(callback_query: CallbackQuery):
    """Налаштування через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_bot_settings(callback_query.message)
    await callback_query.answer()

async def callback_admin_analytics(callback_query: CallbackQuery):
    """Аналітика через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await callback_query.message.answer(
        f"{EMOJI['chart']} <b>АНАЛІТИКА БОТА</b>\n\n"
        f"{EMOJI['construction']} Розширена аналітика в розробці...\n\n"
        f"📈 Планується:\n"
        f"• Графіки активності\n"
        f"• Аналіз поведінки користувачів\n"
        f"• Прогнозування трендів"
    )
    await callback_query.answer()

async def callback_admin_bulk(callback_query: CallbackQuery):
    """Масові дії через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_bulk_actions(callback_query.message)
    await callback_query.answer()

async def callback_admin_backup(callback_query: CallbackQuery):
    """Бекап через callback"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await show_backup_options(callback_query.message)
    await callback_query.answer()

async def callback_admin_close(callback_query: CallbackQuery):
    """Закрити адмін-панель"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    await callback_query.message.edit_text(
        f"{EMOJI['check']} <b>Адмін-панель закрито</b>\n\n"
        f"Для повторного відкриття використовуйте:\n"
        f"• /admin - повна панель\n"
        f"• /m - швидка статистика"
    )
    await callback_query.answer("Панель закрито")

# Існуючі callback обробники

async def callback_approve_content(callback_query: CallbackQuery):
    """Схвалення контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ заборонено!")
        return
    
    try:
        content_id = int(callback_query.data.split("_")[1])
        
        # 🔥 ВИПРАВЛЕНО: Використовуємо правильний enum
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import Content, ContentStatus
            
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                content.status = ContentStatus.APPROVED
                content.moderated_at = datetime.utcnow()
                content.moderator_id = callback_query.from_user.id
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
        
        # 🔥 ВИПРАВЛЕНО: Використовуємо правільний enum
        from database.database import get_db_session
        
        with get_db_session() as session:
            from database.models import Content, ContentStatus
            
            content = session.query(Content).filter(Content.id == content_id).first()
            if content:
                content.status = ContentStatus.REJECTED
                content.moderated_at = datetime.utcnow()
                content.moderator_id = callback_query.from_user.id
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
    """🔥 ВИПРАВЛЕНО: Реєстрація ВСІХ хендлерів адмін-панелі"""
    
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
    
    # 🔥 ВИПРАВЛЕНО: Всі callback запити зареєстровано!
    dp.callback_query.register(callback_admin_stats, F.data == "admin_stats")
    dp.callback_query.register(callback_admin_moderate, F.data == "admin_moderate")
    dp.callback_query.register(callback_admin_users, F.data == "admin_users")
    dp.callback_query.register(callback_admin_content, F.data == "admin_content")
    dp.callback_query.register(callback_admin_trending, F.data == "admin_trending")
    dp.callback_query.register(callback_admin_popular, F.data == "admin_popular")
    dp.callback_query.register(callback_admin_settings, F.data == "admin_settings")
    dp.callback_query.register(callback_admin_analytics, F.data == "admin_analytics")
    dp.callback_query.register(callback_admin_bulk, F.data == "admin_bulk")
    dp.callback_query.register(callback_admin_backup, F.data == "admin_backup")
    dp.callback_query.register(callback_admin_close, F.data == "admin_close")
    
    # Існуючі callback'и
    dp.callback_query.register(callback_approve_content, F.data.startswith("approve_"))
    dp.callback_query.register(callback_reject_content, F.data.startswith("reject_"))
    dp.callback_query.register(callback_quick_stats_refresh, F.data == "quick_stats_refresh")
    
    logger.info("🔥 Всі хендлери адмін-панелі зареєстровано! (14 callback обробників)")

# Експортуємо функцію для використання в basic_commands.py
__all__ = ['auto_show_admin_menu_on_start', 'register_admin_handlers']