#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНА АДМІН-ПАНЕЛЬ З МОДЕРАЦІЄЮ 🧠😂🔥
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
)

logger = logging.getLogger(__name__)

# Fallback налаштування
try:
    from config.settings import settings
    ADMIN_ID = settings.ADMIN_ID
except ImportError:
    import os
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

EMOJI = {
    "crown": "👑", "fire": "🔥", "check": "✅", "cross": "❌",
    "warning": "⚠️", "info": "ℹ️", "stats": "📊", "gear": "⚙️",
    "hammer": "🔨", "shield": "🛡️", "rocket": "🚀", "gem": "💎"
}

def is_admin(user_id: int) -> bool:
    """Перевірка чи є користувач адміністратором"""
    return user_id == ADMIN_ID

# ===== АДМІН МЕНЮ =====

def get_admin_main_menu() -> InlineKeyboardMarkup:
    """Головне адмін меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderation")
        ],
        [
            InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
            InlineKeyboardButton(text="📝 Контент", callback_data="admin_content")
        ],
        [
            InlineKeyboardButton(text="⚔️ Дуелі", callback_data="admin_duels"),
            InlineKeyboardButton(text="📢 Розсилка", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔄 Оновити", callback_data="admin_refresh")
        ]
    ])

def get_admin_static_menu() -> ReplyKeyboardMarkup:
    """Статичне адмін меню"""
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="👑 Адмін панель"),
            KeyboardButton(text="📊 Швидка статистика")
        ],
        [
            KeyboardButton(text="🛡️ Модерація"),
            KeyboardButton(text="📢 Розсилка")
        ],
        [
            KeyboardButton(text="❌ Вимкнути адмін меню")
        ]
    ], resize_keyboard=True)

# ===== ОСНОВНІ КОМАНДИ АДМІНА =====

async def cmd_admin(message: Message):
    """Команда /admin - головна адмін панель"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Доступ заборонено!")
        return
    
    admin_text = (
        f"{EMOJI['crown']} <b>АДМІНІСТРАТИВНА ПАНЕЛЬ</b>\n\n"
        f"Вітаю, адміністратор! Виберіть розділ для роботи:\n\n"
        f"📊 <b>Статистика</b> - загальна інформація про бота\n"
        f"🛡️ <b>Модерація</b> - перевірка контенту\n"
        f"👥 <b>Користувачі</b> - управління користувачами\n"
        f"📝 <b>Контент</b> - управління контентом\n"
        f"⚔️ <b>Дуелі</b> - управління дуелями\n"
        f"📢 <b>Розсилка</b> - масові повідомлення\n\n"
        f"💡 Використовуйте кнопки нижче для швидкого доступу"
    )
    
    await message.answer(
        admin_text,
        reply_markup=get_admin_main_menu()
    )
    
    # Показати статичне меню
    await message.answer(
        f"{EMOJI['info']} Використовуйте меню для швидкого доступу:",
        reply_markup=get_admin_static_menu()
    )

async def cmd_stats(message: Message):
    """Команда швидкої статистики"""
    if not is_admin(message.from_user.id):
        return
    
    await show_bot_statistics(message)

# ===== СТАТИСТИКА =====

async def show_bot_statistics(message: Message, detailed: bool = False):
    """Показати статистику бота"""
    try:
        from database import get_db_session
        from database.models import User, Content, Duel, Rating
        from sqlalchemy import func, and_
        
        with get_db_session() as session:
            # Основна статистика
            total_users = session.query(User).count()
            total_content = session.query(Content).count()
            approved_content = session.query(Content).filter(Content.status == 'APPROVED').count()
            pending_content = session.query(Content).filter(Content.status == 'PENDING').count()
            
            # Статистика за сьогодні
            today = datetime.utcnow().date()
            users_today = session.query(User).filter(func.date(User.created_at) == today).count()
            content_today = session.query(Content).filter(func.date(Content.created_at) == today).count()
            
            # Статистика за тиждень
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_users_week = session.query(User).filter(User.last_active >= week_ago).count()
            
            # Статистика дуелів
            total_duels = session.query(Duel).count()
            active_duels = session.query(Duel).filter(Duel.status == 'ACTIVE').count()
            
            # Статистика контенту
            total_jokes = session.query(Content).filter(Content.content_type == 'JOKE').count()
            total_memes = session.query(Content).filter(Content.content_type == 'MEME').count()
            
            # Створити текст статистики
            stats_text = f"{EMOJI['stats']} <b>СТАТИСТИКА БОТА</b>\n\n"
            
            # Загальна статистика
            stats_text += f"👥 <b>Користувачі:</b>\n"
            stats_text += f"• Всього: {total_users:,}\n"
            stats_text += f"• Сьогодні: +{users_today}\n"
            stats_text += f"• Активних за тиждень: {active_users_week:,}\n\n"
            
            stats_text += f"📝 <b>Контент:</b>\n"
            stats_text += f"• Всього: {total_content:,}\n"
            stats_text += f"• Схвалено: {approved_content:,}\n"
            stats_text += f"• На модерації: {pending_content:,}\n"
            stats_text += f"• Сьогодні: +{content_today}\n\n"
            
            stats_text += f"🎭 <b>Типи контенту:</b>\n"
            stats_text += f"• Жарти: {total_jokes:,}\n"
            stats_text += f"• Меми: {total_memes:,}\n\n"
            
            stats_text += f"⚔️ <b>Дуелі:</b>\n"
            stats_text += f"• Всього: {total_duels:,}\n"
            stats_text += f"• Активних: {active_duels:,}\n\n"
            
            # Додаткова статистика для детального режиму
            if detailed:
                # Топ активних користувачів
                top_users = session.query(User).order_by(User.points.desc()).limit(5).all()
                stats_text += f"🏆 <b>ТОП користувачів:</b>\n"
                for i, user in enumerate(top_users, 1):
                    stats_text += f"{i}. {user.first_name or 'Невідомий'}: {user.points:,} балів\n"
                
                stats_text += "\n"
                
                # Статистика модерації
                rejected_content = session.query(Content).filter(Content.status == 'REJECTED').count()
                approval_rate = (approved_content / total_content * 100) if total_content > 0 else 0
                
                stats_text += f"🛡️ <b>Модерація:</b>\n"
                stats_text += f"• Схвалено: {approved_content:,}\n"
                stats_text += f"• Відхилено: {rejected_content:,}\n"
                stats_text += f"• Відсоток схвалення: {approval_rate:.1f}%\n"
            
            # Час оновлення
            stats_text += f"\n🕐 Оновлено: {datetime.now().strftime('%H:%M:%S')}"
            
            # Клавіатура
            keyboard = get_stats_keyboard()
            
            await message.answer(stats_text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"❌ Помилка статистики: {e}")
        await message.answer(f"{EMOJI['cross']} Помилка завантаження статистики: {e}")

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура статистики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Детальна статистика", callback_data="detailed_stats"),
            InlineKeyboardButton(text="🔄 Оновити", callback_data="refresh_stats")
        ],
        [
            InlineKeyboardButton(text="📈 Графіки", callback_data="stats_charts"),
            InlineKeyboardButton(text="📋 Експорт", callback_data="export_stats")
        ],
        [
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="admin_main")
        ]
    ])

# ===== МОДЕРАЦІЯ =====

async def show_moderation_panel(message: Message):
    """Показати панель модерації"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        from database import get_pending_content
        
        pending_content = await get_pending_content()
        
        moderation_text = f"{EMOJI['shield']} <b>ПАНЕЛЬ МОДЕРАЦІЇ</b>\n\n"
        
        if not pending_content:
            moderation_text += f"{EMOJI['check']} Немає контенту на модерації!\n\n"
            moderation_text += "Всі подання перевірені. Гарна робота! 👏"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Оновити", callback_data="refresh_moderation")],
                [InlineKeyboardButton(text="🏠 Головне меню", callback_data="admin_main")]
            ])
        else:
            moderation_text += f"📋 <b>Контенту на розгляді: {len(pending_content)}</b>\n\n"
            
            for i, content in enumerate(pending_content[:5], 1):  # Показуємо тільки перші 5
                content_type = "Жарт" if content.content_type.value == "JOKE" else "Мем"
                
                moderation_text += f"#{content.id} - {content_type}\n"
                moderation_text += f"👤 Автор ID: {content.author_id}\n"
                moderation_text += f"📅 {content.created_at.strftime('%d.%m %H:%M')}\n"
                moderation_text += f"📝 {content.text[:100]}{'...' if len(content.text) > 100 else ''}\n\n"
            
            if len(pending_content) > 5:
                moderation_text += f"... та ще {len(pending_content) - 5} елементів\n\n"
            
            moderation_text += "Виберіть дію:"
            
            keyboard = get_moderation_keyboard(pending_content[0].id if pending_content else None)
        
        await message.answer(moderation_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ Помилка модерації: {e}")
        await message.answer(f"{EMOJI['cross']} Помилка завантаження модерації: {e}")

def get_moderation_keyboard(content_id: Optional[int]) -> InlineKeyboardMarkup:
    """Клавіатура модерації"""
    if content_id:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Схвалити", callback_data=f"approve_{content_id}"),
                InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{content_id}")
            ],
            [
                InlineKeyboardButton(text="👁 Переглянути", callback_data=f"view_content_{content_id}"),
                InlineKeyboardButton(text="⏭ Наступний", callback_data="next_content")
            ],
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="refresh_moderation"),
                InlineKeyboardButton(text="🏠 Головне меню", callback_data="admin_main")
            ]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Оновити", callback_data="refresh_moderation")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="admin_main")]
        ])

async def moderate_content_item(callback_query: CallbackQuery, action: str, content_id: int):
    """Модерувати конкретний контент"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ заборонено!", show_alert=True)
        return
    
    try:
        from database import moderate_content, get_content_by_id
        
        # Отримати контент
        content = await get_content_by_id(content_id)
        if not content:
            await callback_query.answer("❌ Контент не знайдено!", show_alert=True)
            return
        
        # Модерувати
        success = await moderate_content(
            content_id=content_id,
            action=action.upper(),
            moderator_id=callback_query.from_user.id,
            comment=f"Модеровано через адмін-панель"
        )
        
        if success:
            action_text = "схвалено" if action == "approve" else "відхилено"
            
            # Повідомити автора
            try:
                bot = callback_query.bot
                author_message = (
                    f"{EMOJI['info']} <b>Результат модерації</b>\n\n"
                    f"Ваш {'жарт' if content.content_type.value == 'JOKE' else 'мем'} "
                    f"<b>{action_text}</b> модератором!\n\n"
                )
                
                if action == "approve":
                    author_message += f"🎉 Вітаємо! Ваш контент тепер бачать всі користувачі!\n"
                    author_message += f"💰 +20 балів за схвалення!\n\n"
                else:
                    author_message += f"😔 На жаль, контент не відповідає стандартам.\n"
                    author_message += f"Спробуйте надіслати щось інше!\n\n"
                
                author_message += f"📝 <i>Ваш контент:</i>\n{content.text[:200]}..."
                
                await bot.send_message(content.author_id, author_message)
                
            except Exception:
                pass  # Не критично якщо не вдалося повідомити автора
            
            await callback_query.answer(f"✅ Контент {action_text}!")
            
            # Оновити панель модерації
            await show_moderation_panel(callback_query.message)
            
            logger.info(f"🛡️ Адмін {callback_query.from_user.id} {action_text} контент #{content_id}")
            
        else:
            await callback_query.answer("❌ Помилка модерації!", show_alert=True)
            
    except Exception as e:
        logger.error(f"❌ Помилка модерації контенту: {e}")
        await callback_query.answer("❌ Помилка модерації!", show_alert=True)

# ===== УПРАВЛІННЯ КОРИСТУВАЧАМИ =====

async def show_user_management(message: Message):
    """Показати панель управління користувачами"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        from database import get_db_session
        from database.models import User
        from sqlalchemy import desc
        
        with get_db_session() as session:
            # Статистика користувачів
            total_users = session.query(User).count()
            active_today = session.query(User).filter(
                func.date(User.last_active) == datetime.utcnow().date()
            ).count()
            
            # Топ користувачів
            top_users = session.query(User).order_by(desc(User.points)).limit(10).all()
            
            users_text = f"{EMOJI['crown']} <b>УПРАВЛІННЯ КОРИСТУВАЧАМИ</b>\n\n"
            users_text += f"👥 Всього користувачів: {total_users:,}\n"
            users_text += f"🟢 Активних сьогодні: {active_today:,}\n\n"
            
            users_text += f"🏆 <b>ТОП-10 користувачів:</b>\n"
            for i, user in enumerate(top_users, 1):
                status = "🟢" if user.last_active.date() == datetime.utcnow().date() else "🔴"
                users_text += f"{i}. {status} {user.first_name or 'Невідомий'} ({user.points:,} балів)\n"
            
            keyboard = get_user_management_keyboard()
            await message.answer(users_text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"❌ Помилка управління користувачами: {e}")
        await message.answer(f"{EMOJI['cross']} Помилка завантаження користувачів: {e}")

def get_user_management_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура управління користувачами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Пошук користувача", callback_data="search_user"),
            InlineKeyboardButton(text="📊 Детальна статистика", callback_data="user_detailed_stats")
        ],
        [
            InlineKeyboardButton(text="💰 Нарахувати бали", callback_data="award_points"),
            InlineKeyboardButton(text="🚫 Заблокувати", callback_data="ban_user")
        ],
        [
            InlineKeyboardButton(text="📈 Активність", callback_data="user_activity"),
            InlineKeyboardButton(text="🔄 Оновити", callback_data="refresh_users")
        ],
        [
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="admin_main")
        ]
    ])

# ===== РОЗСИЛКА =====

async def show_broadcast_panel(message: Message):
    """Показати панель розсилки"""
    if not is_admin(message.from_user.id):
        return
    
    broadcast_text = (
        f"{EMOJI['rocket']} <b>ПАНЕЛЬ РОЗСИЛКИ</b>\n\n"
        f"📢 Тут ви можете надіслати повідомлення всім користувачам.\n\n"
        f"⚠️ <b>Увага!</b> Використовуйте розсилку обережно:\n"
        f"• Тільки важливі оголошення\n"
        f"• Не спам\n"
        f"• Якісний контент\n\n"
        f"📋 Виберіть тип розсилки:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 Всім користувачам", callback_data="broadcast_all"),
            InlineKeyboardButton(text="🟢 Тільки активним", callback_data="broadcast_active")
        ],
        [
            InlineKeyboardButton(text="🏆 ТОП користувачам", callback_data="broadcast_top"),
            InlineKeyboardButton(text="🆕 Новим користувачам", callback_data="broadcast_new")
        ],
        [
            InlineKeyboardButton(text="📋 Статистика розсилок", callback_data="broadcast_stats"),
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="admin_main")
        ]
    ])
    
    await message.answer(broadcast_text, reply_markup=keyboard)

# ===== CALLBACK ХЕНДЛЕРИ =====

async def callback_admin_stats(callback_query: CallbackQuery):
    """Callback статистики"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ заборонено!", show_alert=True)
        return
    
    await show_bot_statistics(callback_query.message)
    await callback_query.answer()

async def callback_admin_moderation(callback_query: CallbackQuery):
    """Callback модерації"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ заборонено!", show_alert=True)
        return
    
    await show_moderation_panel(callback_query.message)
    await callback_query.answer()

async def callback_admin_users(callback_query: CallbackQuery):
    """Callback користувачів"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ заборонено!", show_alert=True)
        return
    
    await show_user_management(callback_query.message)
    await callback_query.answer()

async def callback_admin_broadcast(callback_query: CallbackQuery):
    """Callback розсилки"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Доступ заборонено!", show_alert=True)
        return
    
    await show_broadcast_panel(callback_query.message)
    await callback_query.answer()

async def callback_approve_content(callback_query: CallbackQuery):
    """Схвалити контент"""
    data_parts = callback_query.data.split('_')
    if len(data_parts) >= 2:
        content_id = int(data_parts[1])
        await moderate_content_item(callback_query, "approve", content_id)

async def callback_reject_content(callback_query: CallbackQuery):
    """Відхилити контент"""
    data_parts = callback_query.data.split('_')
    if len(data_parts) >= 2:
        content_id = int(data_parts[1])
        await moderate_content_item(callback_query, "reject", content_id)

async def auto_show_admin_menu_on_start(message: Message) -> bool:
    """Автоматично показати адмін-меню при /start для адміна"""
    if is_admin(message.from_user.id):
        await message.answer(
            f"{EMOJI['crown']} <b>Режим адміністратора активовано!</b>\n\n"
            f"Використовуйте кнопки меню нижче або команди:\n"
            f"• /admin - повна панель\n"
            f"• /stats - швидка статистика\n\n"
            f"🛡️ Ви маєте повний доступ до управління ботом.",
            reply_markup=get_admin_static_menu()
        )
        return True
    return False

# ===== ОБРОБКА СТАТИЧНИХ КНОПОК =====

async def handle_admin_static_buttons(message: Message):
    """Обробка статичних адмін кнопок"""
    if not is_admin(message.from_user.id):
        return
    
    text = message.text
    
    if text == "👑 Адмін панель":
        await cmd_admin(message)
    elif text == "📊 Швидка статистика":
        await show_bot_statistics(message)
    elif text == "🛡️ Модерація":
        await show_moderation_panel(message)
    elif text == "📢 Розсилка":
        await show_broadcast_panel(message)
    elif text == "❌ Вимкнути адмін меню":
        from aiogram.types import ReplyKeyboardRemove
        await message.answer(
            "✅ Адмін меню вимкнено.\nВикористовуйте команди для роботи з ботом.",
            reply_markup=ReplyKeyboardRemove()
        )

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_admin_handlers(dp: Dispatcher):
    """Реєстрація всіх адмін хендлерів"""
    
    # Команди
    dp.message.register(cmd_admin, Command("admin"))
    dp.message.register(cmd_stats, Command("stats"))
    
    # Статичні кнопки
    dp.message.register(
        handle_admin_static_buttons,
        F.text.in_([
            "👑 Адмін панель", "📊 Швидка статистика", "🛡️ Модерація",
            "📢 Розсилка", "❌ Вимкнути адмін меню"
        ])
    )
    
    # Callback запити
    dp.callback_query.register(callback_admin_stats, F.data == "admin_stats")
    dp.callback_query.register(callback_admin_moderation, F.data == "admin_moderation")
    dp.callback_query.register(callback_admin_users, F.data == "admin_users")
    dp.callback_query.register(callback_admin_broadcast, F.data == "admin_broadcast")
    
    dp.callback_query.register(callback_approve_content, F.data.startswith("approve_"))
    dp.callback_query.register(callback_reject_content, F.data.startswith("reject_"))
    
    logger.info("✅ Адмін хендлери зареєстровано")

# Експорт для використання в basic_commands.py
__all__ = ['auto_show_admin_menu_on_start', 'register_admin_handlers', 'is_admin']