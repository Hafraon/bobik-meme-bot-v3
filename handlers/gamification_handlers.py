#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПОВНА ГЕЙМІФІКАЦІЯ - ПРОФІЛІ, РАНГИ, ЛІДЕРБОРД 🧠😂🔥
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, User as TelegramUser
)

logger = logging.getLogger(__name__)

# Fallback налаштування
try:
    from config.settings import settings, EMOJI
except ImportError:
    import os
    EMOJI = {
        "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐",
        "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
        "crown": "👑", "rocket": "🚀", "vs": "⚔️", "calendar": "📅",
        "profile": "👤", "trophy": "🏆", "medal": "🥇", "gem": "💎"
    }

# ===== КОНФІГУРАЦІЯ РАНГІВ =====

RANK_SYSTEM = [
    {"name": "🤡 Новачок", "min_points": 0, "emoji": "🤡", "description": "Тільки почали свій шлях в світі гумору"},
    {"name": "😄 Сміхун", "min_points": 50, "emoji": "😄", "description": "Розумієте що таке смішно"},
    {"name": "😂 Гуморист", "min_points": 150, "emoji": "😂", "description": "Вже можете розсмішити друзів"},
    {"name": "🎭 Комік", "min_points": 350, "emoji": "🎭", "description": "Справжній майстер жартів"},
    {"name": "👑 Мастер Рофлу", "min_points": 750, "emoji": "👑", "description": "Король місцевого стенд-апу"},
    {"name": "🏆 Король Гумору", "min_points": 1500, "emoji": "🏆", "description": "Легенда комедійного цеху"},
    {"name": "🌟 Легенда Мемів", "min_points": 3000, "emoji": "🌟", "description": "Ваші меми розходяться по всьому інтернету"},
    {"name": "🚀 Гумористичний Геній", "min_points": 5000, "emoji": "🚀", "description": "Абсолютний майстер комедії"}
]

def get_rank_by_points(points: int) -> Dict[str, Any]:
    """Отримати ранг за кількістю балів"""
    current_rank = RANK_SYSTEM[0]
    next_rank = None
    
    for i, rank in enumerate(RANK_SYSTEM):
        if points >= rank["min_points"]:
            current_rank = rank
            next_rank = RANK_SYSTEM[i + 1] if i + 1 < len(RANK_SYSTEM) else None
        else:
            break
    
    return {
        "current": current_rank,
        "next": next_rank,
        "progress": points - current_rank["min_points"],
        "next_threshold": next_rank["min_points"] - points if next_rank else 0
    }

def get_achievement_badge(user_stats: Dict[str, Any]) -> str:
    """Отримати значок досягнень"""
    badges = []
    
    # Значки за активність
    if user_stats.get("jokes_approved", 0) >= 10:
        badges.append("📝 Автор")
    if user_stats.get("reactions_given", 0) >= 100:
        badges.append("👍 Критик")
    if user_stats.get("duels_won", 0) >= 5:
        badges.append("⚔️ Боєць")
    if user_stats.get("points", 0) >= 1000:
        badges.append("💎 Багатій")
    
    # Значки за час
    if user_stats.get("days_active", 0) >= 30:
        badges.append("📅 Ветеран")
    if user_stats.get("daily_streak", 0) >= 7:
        badges.append("🔥 Постійний")
    
    return " ".join(badges) if badges else "🆕 Початківець"

# ===== ПРОФІЛЬ КОРИСТУВАЧА =====

async def cmd_profile(message: Message):
    """Команда /profile - показати профіль користувача"""
    await show_user_profile(message, message.from_user.id)

async def show_user_profile(message: Message, user_id: int):
    """Показати профіль користувача"""
    try:
        from database import get_user_by_id, get_user_stats
        
        # Отримати дані користувача
        user = await get_user_by_id(user_id)
        if not user:
            await message.answer(
                f"{EMOJI.get('warning', '⚠️')} Користувач не знайдений.\n"
                f"Спробуйте надіслати /start для створення профілю."
            )
            return
        
        # Отримати статистику
        stats = await get_user_stats(user_id)
        
        # Розрахувати ранг
        rank_info = get_rank_by_points(user.points)
        
        # Розрахувати активність
        days_since_registration = (datetime.utcnow() - user.created_at).days
        days_active = max(1, days_since_registration)
        
        # Створити статистику
        user_stats = {
            "points": user.points,
            "jokes_approved": user.jokes_approved,
            "memes_approved": user.memes_approved,
            "reactions_given": user.reactions_given,
            "duels_won": user.duels_won,
            "duels_lost": user.duels_lost,
            "days_active": days_active,
            "daily_streak": 0  # TODO: розрахувати streak
        }
        
        # Отримати значки досягнень
        achievements = get_achievement_badge(user_stats)
        
        # Створити текст профілю
        profile_text = f"{EMOJI.get('profile', '👤')} <b>Профіль користувача</b>\n\n"
        
        # Основна інформація
        profile_text += f"🎭 <b>{user.first_name or 'Невідомий'}</b>"
        if user.username:
            profile_text += f" (@{user.username})"
        profile_text += f"\n"
        
        # Ранг та бали
        profile_text += f"🏆 <b>Ранг:</b> {rank_info['current']['name']}\n"
        profile_text += f"💰 <b>Бали:</b> {user.points:,}\n"
        
        # Прогрес до наступного рангу
        if rank_info['next']:
            progress_percent = (rank_info['progress'] / (rank_info['progress'] + rank_info['next_threshold'])) * 100
            progress_bar = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))
            profile_text += f"📈 <b>Прогрес:</b> {progress_bar} {progress_percent:.1f}%\n"
            profile_text += f"🎯 <b>До {rank_info['next']['name']}:</b> {rank_info['next_threshold']:,} балів\n"
        else:
            profile_text += f"🌟 <b>Максимальний ранг досягнуто!</b>\n"
        
        profile_text += "\n"
        
        # Досягнення
        profile_text += f"🏅 <b>Досягнення:</b> {achievements}\n\n"
        
        # Статистика контенту
        profile_text += f"📊 <b>Статистика контенту:</b>\n"
        profile_text += f"• 📝 Жартів схвалено: {user.jokes_approved}\n"
        profile_text += f"• 🖼 Мемів схвалено: {user.memes_approved}\n"
        profile_text += f"• 📤 Всього надіслано: {user.jokes_submitted + user.memes_submitted}\n"
        
        # Статистика активності
        profile_text += f"\n🎮 <b>Активність:</b>\n"
        profile_text += f"• 👍 Реакцій дано: {user.reactions_given}\n"
        profile_text += f"• ⚔️ Дуелів виграно: {user.duels_won}\n"
        profile_text += f"• 🥊 Дуелів програно: {user.duels_lost}\n"
        
        # Загальна активність
        total_duels = user.duels_won + user.duels_lost
        win_rate = (user.duels_won / total_duels * 100) if total_duels > 0 else 0
        
        profile_text += f"\n📈 <b>Загальне:</b>\n"
        profile_text += f"• 🗓 Днів в боті: {days_active}\n"
        profile_text += f"• 🎯 Винрейт дуелів: {win_rate:.1f}%\n"
        profile_text += f"• 📅 Реєстрація: {user.created_at.strftime('%d.%m.%Y')}\n"
        
        # Клавіатура профілю
        keyboard = get_profile_keyboard(user_id)
        
        await message.answer(profile_text, reply_markup=keyboard)
        
        logger.info(f"👤 Показано профіль користувача {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Помилка показу профілю: {e}")
        await message.answer(
            f"{EMOJI.get('cross', '❌')} Помилка при завантаженні профілю.\n"
            f"Спробуйте ще раз пізніше."
        )

def get_profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавіатура профілю"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏆 Таблиця лідерів",
                callback_data="show_leaderboard"
            ),
            InlineKeyboardButton(
                text="📊 Детальна статистика",
                callback_data=f"detailed_stats_{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎯 Мої досягнення",
                callback_data=f"achievements_{user_id}"
            ),
            InlineKeyboardButton(
                text="📈 Історія балів",
                callback_data=f"points_history_{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Оновити профіль",
                callback_data=f"refresh_profile_{user_id}"
            )
        ]
    ])

# ===== ТАБЛИЦЯ ЛІДЕРІВ =====

async def cmd_top(message: Message):
    """Команда /top - показати таблицю лідерів"""
    await show_leaderboard(message)

async def show_leaderboard(message: Message, page: int = 1):
    """Показати таблицю лідерів"""
    try:
        from database import get_db_session
        from database.models import User
        from sqlalchemy import desc
        
        with get_db_session() as session:
            # Отримати топ користувачів
            users = session.query(User).order_by(desc(User.points)).limit(20).all()
            
            if not users:
                await message.answer(
                    f"{EMOJI.get('warning', '⚠️')} Поки немає користувачів в рейтингу.\n"
                    f"Будьте першим! Збирайте бали і підніматься в ТОП!"
                )
                return
            
            # Створити текст лідерборду
            leaderboard_text = f"{EMOJI.get('trophy', '🏆')} <b>ТАБЛИЦЯ ЛІДЕРІВ</b>\n\n"
            
            for i, user in enumerate(users, 1):
                # Визначити медаль
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}️⃣"
                
                # Отримати ранг
                rank_info = get_rank_by_points(user.points)
                rank_emoji = rank_info['current']['emoji']
                
                # Створити рядок
                username = user.first_name or "Невідомий"
                if len(username) > 15:
                    username = username[:12] + "..."
                
                leaderboard_text += f"{medal} {rank_emoji} <b>{username}</b>\n"
                leaderboard_text += f"    💰 {user.points:,} балів\n"
                
                # Додати статистику для топ-3
                if i <= 3:
                    total_approved = user.jokes_approved + user.memes_approved
                    leaderboard_text += f"    📝 Контенту: {total_approved} | ⚔️ Дуелів: {user.duels_won}\n"
                
                leaderboard_text += "\n"
            
            # Додати інформацію про поточного користувача
            current_user_id = message.from_user.id
            current_user_position = None
            
            # Знайти позицію поточного користувача
            all_users = session.query(User).order_by(desc(User.points)).all()
            for i, user in enumerate(all_users, 1):
                if user.id == current_user_id:
                    current_user_position = i
                    break
            
            if current_user_position:
                leaderboard_text += f"━━━━━━━━━━━━━━━━━━━━\n"
                leaderboard_text += f"📍 <b>Ваша позиція: #{current_user_position}</b>\n"
                
                current_user = session.query(User).filter(User.id == current_user_id).first()
                if current_user:
                    rank_info = get_rank_by_points(current_user.points)
                    leaderboard_text += f"💰 Ваші бали: {current_user.points:,}\n"
                    leaderboard_text += f"🏆 Ваш ранг: {rank_info['current']['name']}"
            
            # Клавіатура
            keyboard = get_leaderboard_keyboard(page)
            
            await message.answer(leaderboard_text, reply_markup=keyboard)
            
            logger.info(f"🏆 Показано таблицю лідерів")
            
    except Exception as e:
        logger.error(f"❌ Помилка показу лідерборду: {e}")
        await message.answer(
            f"{EMOJI.get('cross', '❌')} Помилка при завантаженні таблиці лідерів.\n"
            f"Спробуйте ще раз пізніше."
        )

def get_leaderboard_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    """Клавіатура лідерборду"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👤 Мій профіль",
                callback_data="show_my_profile"
            ),
            InlineKeyboardButton(
                text="🔄 Оновити ТОП",
                callback_data="refresh_leaderboard"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 ТОП по жартах",
                callback_data="top_jokes"
            ),
            InlineKeyboardButton(
                text="🖼 ТОП по мемах",
                callback_data="top_memes"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚔️ ТОП дуелянтів",
                callback_data="top_duels"
            ),
            InlineKeyboardButton(
                text="🎯 ТОП тиждень",
                callback_data="top_week"
            )
        ]
    ])

# ===== CALLBACK ХЕНДЛЕРИ =====

async def callback_show_profile(callback_query: CallbackQuery):
    """Показати профіль через callback"""
    user_id = callback_query.from_user.id
    await show_user_profile(callback_query.message, user_id)
    await callback_query.answer()

async def callback_show_leaderboard(callback_query: CallbackQuery):
    """Показати лідерборд через callback"""
    await show_leaderboard(callback_query.message)
    await callback_query.answer()

async def callback_refresh_profile(callback_query: CallbackQuery):
    """Оновити профіль"""
    data_parts = callback_query.data.split('_')
    if len(data_parts) >= 3:
        user_id = int(data_parts[2])
        await show_user_profile(callback_query.message, user_id)
        await callback_query.answer("✅ Профіль оновлено!")
    else:
        await callback_query.answer("❌ Помилка даних", show_alert=True)

async def callback_refresh_leaderboard(callback_query: CallbackQuery):
    """Оновити лідерборд"""
    await show_leaderboard(callback_query.message)
    await callback_query.answer("✅ Лідерборд оновлено!")

async def callback_detailed_stats(callback_query: CallbackQuery):
    """Детальна статистика користувача"""
    data_parts = callback_query.data.split('_')
    if len(data_parts) >= 3:
        user_id = int(data_parts[2])
        await show_detailed_stats(callback_query.message, user_id)
        await callback_query.answer()
    else:
        await callback_query.answer("❌ Помилка даних", show_alert=True)

async def show_detailed_stats(message: Message, user_id: int):
    """Показати детальну статистику"""
    try:
        from database import get_user_by_id, get_db_session
        from database.models import Content, Rating
        from sqlalchemy import func, and_
        
        user = await get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Користувач не знайдений")
            return
        
        with get_db_session() as session:
            # Статистика контенту
            total_content = session.query(Content).filter(Content.author_id == user_id).count()
            approved_content = session.query(Content).filter(
                and_(Content.author_id == user_id, Content.status == 'APPROVED')
            ).count()
            
            # Статистика переглядів
            total_views = session.query(func.sum(Content.views)).filter(
                and_(Content.author_id == user_id, Content.status == 'APPROVED')
            ).scalar() or 0
            
            # Статистика лайків
            total_likes = session.query(func.sum(Content.likes)).filter(
                and_(Content.author_id == user_id, Content.status == 'APPROVED')
            ).scalar() or 0
            
            # Статистика рейтингів
            ratings_given = session.query(Rating).filter(Rating.user_id == user_id).count()
            
            # Створити текст статистики
            stats_text = f"📊 <b>Детальна статистика</b>\n\n"
            stats_text += f"👤 <b>{user.first_name or 'Невідомий'}</b>\n\n"
            
            # Контент
            stats_text += f"📝 <b>Контент:</b>\n"
            stats_text += f"• Всього надіслано: {total_content}\n"
            stats_text += f"• Схвалено: {approved_content}\n"
            stats_text += f"• Відсоток схвалення: {(approved_content/total_content*100):.1f}%\n" if total_content > 0 else "• Відсоток схвалення: 0%\n"
            stats_text += f"• Всього переглядів: {total_views:,}\n"
            stats_text += f"• Всього лайків: {total_likes:,}\n\n"
            
            # Активність
            stats_text += f"🎮 <b>Активність:</b>\n"
            stats_text += f"• Реакцій дано: {ratings_given}\n"
            stats_text += f"• Дуелів виграно: {user.duels_won}\n"
            stats_text += f"• Дуелів програно: {user.duels_lost}\n"
            
            # Розрахунки
            total_duels = user.duels_won + user.duels_lost
            win_rate = (user.duels_won / total_duels * 100) if total_duels > 0 else 0
            avg_views = (total_views / approved_content) if approved_content > 0 else 0
            
            stats_text += f"• Винрейт дуелів: {win_rate:.1f}%\n"
            stats_text += f"• Середньо переглядів на контент: {avg_views:.1f}\n\n"
            
            # Бали
            stats_text += f"💰 <b>Бали:</b>\n"
            stats_text += f"• Поточний баланс: {user.points:,}\n"
            
            # Прогнозовані бали
            estimated_content_points = approved_content * 30  # 10 за подачу + 20 за схвалення
            estimated_reaction_points = ratings_given * 5
            estimated_duel_points = user.duels_won * 15
            
            stats_text += f"• Орієнтовно за контент: {estimated_content_points}\n"
            stats_text += f"• Орієнтовно за реакції: {estimated_reaction_points}\n"
            stats_text += f"• Орієнтовно за дуелі: {estimated_duel_points}\n"
            
            await message.answer(stats_text)
            
    except Exception as e:
        logger.error(f"❌ Помилка детальної статистики: {e}")
        await message.answer("❌ Помилка завантаження детальної статистики")

async def callback_achievements(callback_query: CallbackQuery):
    """Показати досягнення"""
    data_parts = callback_query.data.split('_')
    if len(data_parts) >= 2:
        user_id = int(data_parts[1])
        await show_achievements(callback_query.message, user_id)
        await callback_query.answer()
    else:
        await callback_query.answer("❌ Помилка даних", show_alert=True)

async def show_achievements(message: Message, user_id: int):
    """Показати досягнення користувача"""
    try:
        from database import get_user_by_id
        
        user = await get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Користувач не знайдений")
            return
        
        achievements_text = f"🏅 <b>Досягнення</b>\n\n"
        achievements_text += f"👤 <b>{user.first_name or 'Невідомий'}</b>\n\n"
        
        # Список досягнень
        achievements = []
        
        # Досягнення за контент
        if user.jokes_approved >= 1:
            achievements.append({"name": "📝 Перший жарт", "desc": "Схвалено перший жарт"})
        if user.jokes_approved >= 10:
            achievements.append({"name": "😂 Жартівник", "desc": "Схвалено 10+ жартів"})
        if user.jokes_approved >= 50:
            achievements.append({"name": "🎭 Комедіант", "desc": "Схвалено 50+ жартів"})
        
        # Досягнення за мемы
        if user.memes_approved >= 1:
            achievements.append({"name": "🖼 Перший мем", "desc": "Схвалено перший мем"})
        if user.memes_approved >= 10:
            achievements.append({"name": "🔥 Мемолорд", "desc": "Схвалено 10+ мемів"})
        
        # Досягнення за дуелі
        if user.duels_won >= 1:
            achievements.append({"name": "⚔️ Перша перемога", "desc": "Виграно перший дуель"})
        if user.duels_won >= 10:
            achievements.append({"name": "🏆 Дуелянт", "desc": "Виграно 10+ дуелів"})
        if user.duels_won >= 50:
            achievements.append({"name": "👑 Чемпіон", "desc": "Виграно 50+ дуелів"})
        
        # Досягнення за бали
        if user.points >= 100:
            achievements.append({"name": "💰 Перша сотня", "desc": "Зібрано 100+ балів"})
        if user.points >= 1000:
            achievements.append({"name": "💎 Тисячник", "desc": "Зібрано 1000+ балів"})
        if user.points >= 5000:
            achievements.append({"name": "🚀 Мільйонер", "desc": "Зібрано 5000+ балів"})
        
        # Досягнення за активність
        if user.reactions_given >= 50:
            achievements.append({"name": "👍 Активний критик", "desc": "Дано 50+ реакцій"})
        if user.reactions_given >= 200:
            achievements.append({"name": "🎯 Супер критик", "desc": "Дано 200+ реакцій"})
        
        # Показати досягнення
        if achievements:
            for achievement in achievements:
                achievements_text += f"{achievement['name']}\n"
                achievements_text += f"<i>{achievement['desc']}</i>\n\n"
        else:
            achievements_text += "Досягнень поки немає.\nПочніть збирати бали щоб отримати перші нагороди!"
        
        await message.answer(achievements_text)
        
    except Exception as e:
        logger.error(f"❌ Помилка показу досягнень: {e}")
        await message.answer("❌ Помилка завантаження досягнень")

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_gamification_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів гейміфікації"""
    
    # Команди
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_top, Command("top"))
    
    # Callback запити
    dp.callback_query.register(callback_show_profile, F.data == "show_profile")
    dp.callback_query.register(callback_show_profile, F.data == "show_my_profile")
    dp.callback_query.register(callback_show_leaderboard, F.data == "show_leaderboard")
    dp.callback_query.register(callback_refresh_profile, F.data.startswith("refresh_profile_"))
    dp.callback_query.register(callback_refresh_leaderboard, F.data == "refresh_leaderboard")
    dp.callback_query.register(callback_detailed_stats, F.data.startswith("detailed_stats_"))
    dp.callback_query.register(callback_achievements, F.data.startswith("achievements_"))
    
    logger.info("✅ Хендлери гейміфікації зареєстровано")