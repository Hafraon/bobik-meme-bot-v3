#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 ВИПРАВЛЕНІ ХЕНДЛЕРИ ГЕЙМІФІКАЦІЇ БЕЗ КРАШІВ 🎮

ВИПРАВЛЕННЯ:
✅ Безпечна перевірка доступності БД
✅ Fallback функції для роботи без БД
✅ Правильна обробка помилок
✅ Ніколи не крашиться при недоступній БД
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)

# ===== РАНГИ ТА КОНСТАНТИ =====
RANKS = {
    0: "🥚 Новачок",
    50: "🐣 Початківець", 
    150: "🐤 Весельчак",
    300: "🐓 Жартівник",
    500: "🦅 Майстер Гумору",
    1000: "🦸 Легенда Жартів"
}

EMOJI = {
    'profile': '👤',
    'fire': '🔥',
    'crown': '👑',
    'top': '🏆',
    'vs': '⚔️',
    'brain': '🧠',
    'laugh': '😂',
    'rocket': '🚀',
    'stats': '📊',
    'calendar': '📅',
    'warning': '⚠️',
    'thinking': '🤔'
}

# ===== FALLBACK СХОВИЩЕ КОРИСТУВАЧІВ =====
USERS_STORAGE: Dict[int, Dict[str, Any]] = {}

# ===== ПЕРЕВІРКА ДОСТУПНОСТІ БД =====
def is_database_available() -> bool:
    """Перевірка чи доступна база даних"""
    try:
        from database.database import is_database_available
        return is_database_available()
    except ImportError:
        return False
    except Exception:
        return False

# ===== ФУНКЦІЇ РОБОТИ З КОРИСТУВАЧАМИ =====
async def get_or_create_user(user_id: int, username: str = None, 
                           first_name: str = None, last_name: str = None) -> Dict[str, Any]:
    """Отримати або створити користувача з безпечною fallback логікою"""
    
    # Спроба використання БД
    if is_database_available():
        try:
            from database.database import get_or_create_user as db_get_user
            db_user = await db_get_user(user_id, username, first_name, last_name)
            if db_user:
                return {
                    'id': db_user.id,
                    'username': db_user.username,
                    'first_name': db_user.first_name,
                    'last_name': db_user.last_name,
                    'points': db_user.points,
                    'rank': db_user.rank,
                    'total_content_submitted': getattr(db_user, 'total_content_submitted', 0),
                    'total_content_approved': getattr(db_user, 'total_content_approved', 0),
                    'total_duels_won': getattr(db_user, 'total_duels_won', 0),
                    'total_duels_participated': getattr(db_user, 'total_duels_participated', 0),
                    'daily_subscription': getattr(db_user, 'daily_subscription', False),
                    'is_admin': getattr(db_user, 'is_admin', False),
                    'created_at': getattr(db_user, 'created_at', datetime.utcnow()),
                    'source': 'database'
                }
        except Exception as e:
            logger.warning(f"⚠️ БД недоступна для get_or_create_user: {e}")
    
    # Fallback - використання пам'яті
    if user_id not in USERS_STORAGE:
        USERS_STORAGE[user_id] = {
            'id': user_id,
            'username': username,
            'first_name': first_name or "Користувач",
            'last_name': last_name,
            'points': 0,
            'rank': get_rank_by_points(0),
            'total_content_submitted': 0,
            'total_content_approved': 0,
            'total_duels_won': 0,
            'total_duels_participated': 0,
            'daily_subscription': False,
            'is_admin': is_admin(user_id),
            'created_at': datetime.utcnow(),
            'source': 'memory'
        }
        logger.info(f"👤 Створено fallback користувача: {user_id}")
    else:
        # Оновлення даних
        user = USERS_STORAGE[user_id]
        if username and user['username'] != username:
            user['username'] = username
        if first_name and user['first_name'] != first_name:
            user['first_name'] = first_name
        if last_name and user['last_name'] != last_name:
            user['last_name'] = last_name
    
    return USERS_STORAGE[user_id]

async def get_top_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Отримання топ користувачів БЕЗ КРАШІВ"""
    
    # Спроба використання БД
    if is_database_available():
        try:
            from database.database import get_top_users as db_get_top
            db_users = await db_get_top(limit)
            if db_users:
                logger.info(f"📊 Отримано топ користувачів з БД: {len(db_users)}")
                result = []
                for user in db_users:
                    result.append({
                        'id': user.id,
                        'first_name': user.first_name,
                        'username': user.username,
                        'points': user.points,
                        'rank': user.rank,
                        'source': 'database'
                    })
                return result
        except Exception as e:
            logger.warning(f"⚠️ БД недоступна для get_top_users: {e}")
    
    # Fallback - сортування з пам'яті
    if USERS_STORAGE:
        sorted_users = sorted(USERS_STORAGE.values(), key=lambda u: u['points'], reverse=True)
        result = sorted_users[:limit]
        logger.info(f"📊 Отримано топ користувачів з пам'яті: {len(result)}")
        return result
    
    # Якщо немає даних взагалі
    logger.info("📊 Немає даних користувачів")
    return []

async def update_user_points(user_id: int, points: int, reason: str = "") -> bool:
    """Оновлення балів користувача з безпечною логікою"""
    
    # Спроба використання БД
    if is_database_available():
        try:
            from database.database import update_user_points as db_update_points
            success = await db_update_points(user_id, points)
            if success:
                logger.info(f"📈 БД: Користувач {user_id} отримав {points} балів за {reason}")
                return True
        except Exception as e:
            logger.warning(f"⚠️ БД недоступна для update_user_points: {e}")
    
    # Fallback - оновлення в пам'яті
    user = await get_or_create_user(user_id)
    old_points = user['points']
    user['points'] += points
    
    # Оновлення рангу
    old_rank = user['rank']
    new_rank = get_rank_by_points(user['points'])
    user['rank'] = new_rank
    
    logger.info(f"📈 Пам'ять: Користувач {user_id} отримав {points} балів за {reason} (було {old_points}, стало {user['points']})")
    
    if old_rank != new_rank:
        logger.info(f"🎖️ Користувач {user_id} підвищив ранг: {old_rank} → {new_rank}")
    
    return True

def get_rank_by_points(points: int) -> str:
    """Визначення рангу за балами"""
    for min_points in sorted(RANKS.keys(), reverse=True):
        if points >= min_points:
            return RANKS[min_points]
    return RANKS[0]

def get_next_rank_info(current_points: int) -> Dict[str, Any]:
    """Інформація про наступний ранг"""
    current_rank = get_rank_by_points(current_points)
    
    for min_points in sorted(RANKS.keys()):
        if min_points > current_points:
            return {
                "next_rank": RANKS[min_points],
                "points_needed": min_points - current_points,
                "current_points": current_points
            }
    
    return {
        "next_rank": None,
        "points_needed": 0,
        "current_points": current_points
    }

def is_admin(user_id: int) -> bool:
    """Перевірка адміністратора"""
    try:
        from config.settings import ALL_ADMIN_IDS
        return user_id in ALL_ADMIN_IDS
    except ImportError:
        admin_id = int(os.getenv("ADMIN_ID", 603047391))
        return user_id == admin_id

# ===== КОМАНДИ ГЕЙМІФІКАЦІЇ =====

async def cmd_profile(message: Message):
    """Команда /profile - показ профілю користувача"""
    user_id = message.from_user.id
    
    try:
        # Отримуємо або створюємо користувача
        user = await get_or_create_user(
            user_id, 
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        
        # Формуємо текст профілю
        next_rank_info = get_next_rank_info(user['points'])
        
        if next_rank_info["points_needed"] > 0:
            progress_text = (
                f"{EMOJI['rocket']} <b>До наступного рангу:</b>\n"
                f"🎯 {next_rank_info['next_rank']}\n"
                f"🔥 Потрібно ще: {next_rank_info['points_needed']} балів"
            )
        else:
            progress_text = f"{EMOJI['crown']} <b>Максимальний ранг досягнуто!</b>"
        
        # Статистика активності
        stats_text = (
            f"\n{EMOJI['stats']} <b>Статистика:</b>\n"
            f"📝 Контент подано: {user['total_content_submitted']}\n"
            f"✅ Контент схвалено: {user['total_content_approved']}\n"
            f"⚔️ Дуелей виграно: {user['total_duels_won']}\n"
            f"🎮 Дуелей зіграно: {user['total_duels_participated']}"
        )
        
        data_source = "💾 БД" if user.get('source') == 'database' else "💻 Пам'ять"
        
        profile_text = (
            f"{EMOJI['profile']} <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n\n"
            f"👤 <b>Ім'я:</b> {user['first_name']}\n"
            f"🆔 <b>ID:</b> {user['id']}\n"
            f"{EMOJI['fire']} <b>Балів:</b> {user['points']}\n"
            f"{EMOJI['crown']} <b>Ранг:</b> {user['rank']}\n\n"
            f"{progress_text}"
            f"{stats_text}\n\n"
            f"{EMOJI['calendar']} Щоденна розсилка: {'✅ Увімкнена' if user['daily_subscription'] else '❌ Вимкнена'}\n"
            f"📊 Джерело даних: {data_source}"
        )
        
        # Клавіатура профілю
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['top']} Рейтинг", callback_data="show_leaderboard"),
                InlineKeyboardButton(text=f"{EMOJI['vs']} Дуель", callback_data="start_duel")
            ],
            [
                InlineKeyboardButton(
                    text=f"{'❌ Відписатись' if user['daily_subscription'] else '✅ Підписатись'} на розсилку",
                    callback_data="toggle_daily"
                )
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke"),
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
            ]
        ])
        
        await message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"❌ Помилка cmd_profile: {e}")
        await message.answer(
            f"❌ Помилка завантаження профілю.\n\n"
            f"🔧 Спробуйте пізніше або зверніться до адміністратора.\n"
            f"💡 Деякі функції можуть бути недоступні через проблеми з БД."
        )

async def cmd_top(message: Message):
    """Команда /top - таблиця лідерів БЕЗ КРАШІВ"""
    try:
        await show_leaderboard(message)
    except Exception as e:
        logger.error(f"❌ Помилка cmd_top: {e}")
        await message.answer(
            f"❌ Помилка завантаження рейтингу.\n\n"
            f"🔧 Можливі причини:\n"
            f"• База даних тимчасово недоступна\n"
            f"• Проблеми з підключенням\n\n"
            f"💡 Спробуйте знову через хвилину."
        )

async def show_leaderboard(message: Message):
    """Показ таблиці лідерів БЕЗ КРАШІВ"""
    try:
        # Безпечне отримання топ користувачів
        top_users = await get_top_users(10)
        
        if not top_users:
            await message.answer(
                f"{EMOJI['warning']} <b>Рейтинг порожній</b>\n\n"
                f"😔 Поки що немає користувачів в рейтингу.\n"
                f"🚀 Будьте першим! Збирайте бали:\n\n"
                f"• 📝 Подавайте контент (/submit)\n"
                f"• ⚔️ Беріть участь в дуелях (/duel)\n"
                f"• 👍 Ставте лайки іншим\n"
                f"• 🎯 Будьте активними!\n\n"
                f"💡 <i>Система збереже ваш прогрес коли БД буде доступна</i>",
                parse_mode="HTML"
            )
            return
        
        # Формуємо текст рейтингу
        leaderboard_text = f"{EMOJI['top']} <b>РЕЙТИНГ КОРИСТУВАЧІВ</b>\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        for i, user in enumerate(top_users):
            position = i + 1
            medal = medals[i] if i < 3 else f"{position}."
            
            username_display = f"@{user['username']}" if user.get('username') else user['first_name']
            
            leaderboard_text += (
                f"{medal} <b>{username_display}</b>\n"
                f"   🔥 {user['points']} балів | {user['rank']}\n\n"
            )
        
        # Додаємо інформацію про джерело даних
        data_source = "БД" if top_users[0].get('source') == 'database' else "пам'ять"
        leaderboard_text += f"📊 <i>Дані з: {data_source}</i>\n"
        leaderboard_text += f"🕐 Оновлено: {datetime.now().strftime('%H:%M:%S')}"
        
        # Клавіатура
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="refresh_leaderboard"),
                InlineKeyboardButton(text="👤 Мій профіль", callback_data="show_profile")
            ],
            [
                InlineKeyboardButton(text="🎯 Як заробити бали?", callback_data="earn_points_info")
            ]
        ])
        
        await message.answer(leaderboard_text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"❌ Помилка show_leaderboard: {e}")
        await message.answer(
            f"❌ <b>Помилка завантаження рейтингу</b>\n\n"
            f"🔧 Технічні деталі:\n"
            f"• Тип помилки: {type(e).__name__}\n"
            f"• Повідомлення: {str(e)}\n\n"
            f"💡 Спробуйте команду /profile для перевірки ваших даних.",
            parse_mode="HTML"
        )

async def cmd_daily(message: Message):
    """Команда /daily - щоденна активність"""
    user_id = message.from_user.id
    
    try:
        user = await get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
        
        # Логіка щоденної винагороди (спрощена версія)
        daily_points = 5
        await update_user_points(user_id, daily_points, "щоденна активність")
        
        await message.answer(
            f"🎁 <b>Щоденна винагорода!</b>\n\n"
            f"🔥 Ви отримали {daily_points} балів за активність!\n"
            f"📊 Ваш загальний рахунок: {user['points'] + daily_points} балів\n\n"
            f"💡 Повертайтесь завтра за новою винагородою!",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка cmd_daily: {e}")
        await message.answer("❌ Помилка отримання щоденної винагороди. Спробуйте пізніше.")

# ===== CALLBACK ХЕНДЛЕРИ =====

async def callback_show_profile(callback_query: CallbackQuery):
    """Показати профіль через callback"""
    try:
        # Створюємо "фейкове" повідомлення для використання існуючої логіки
        fake_message = callback_query.message
        fake_message.from_user = callback_query.from_user
        
        await cmd_profile(fake_message)
        await callback_query.answer("✅ Профіль оновлено!")
    except Exception as e:
        logger.error(f"❌ Помилка callback_show_profile: {e}")
        await callback_query.answer("❌ Помилка завантаження профілю", show_alert=True)

async def callback_show_leaderboard(callback_query: CallbackQuery):
    """Показати рейтинг через callback"""
    try:
        await show_leaderboard(callback_query.message)
        await callback_query.answer("✅ Рейтинг оновлено!")
    except Exception as e:
        logger.error(f"❌ Помилка callback_show_leaderboard: {e}")
        await callback_query.answer("❌ Помилка завантаження рейтингу", show_alert=True)

async def callback_refresh_leaderboard(callback_query: CallbackQuery):
    """Оновити рейтинг"""
    try:
        await show_leaderboard(callback_query.message)
        await callback_query.answer("🔄 Рейтинг оновлено!")
    except Exception as e:
        logger.error(f"❌ Помилка callback_refresh_leaderboard: {e}")
        await callback_query.answer("❌ Помилка оновлення", show_alert=True)

async def callback_toggle_daily(callback_query: CallbackQuery):
    """Перемикання щоденної підписки"""
    user_id = callback_query.from_user.id
    
    try:
        user = await get_or_create_user(user_id)
        user['daily_subscription'] = not user['daily_subscription']
        
        status = "✅ увімкнена" if user['daily_subscription'] else "❌ вимкнена"
        await callback_query.answer(f"Щоденна розсилка {status}!")
        
        # Оновлюємо повідомлення
        fake_message = callback_query.message
        fake_message.from_user = callback_query.from_user
        await cmd_profile(fake_message)
        
    except Exception as e:
        logger.error(f"❌ Помилка callback_toggle_daily: {e}")
        await callback_query.answer("❌ Помилка зміни налаштувань", show_alert=True)

async def callback_earn_points_info(callback_query: CallbackQuery):
    """Інформація про заробляння балів"""
    info_text = (
        f"🎯 <b>ЯК ЗАРОБИТИ БАЛИ?</b>\n\n"
        f"📝 <b>Створюйте контент:</b>\n"
        f"• Подайте анекдот: +5 балів\n"
        f"• Схвалення контенту: +15 балів\n\n"
        f"⚔️ <b>Беріть участь в дуелях:</b>\n"
        f"• Участь: +3 бали\n"
        f"• Перемога: +15 балів\n\n"
        f"👍 <b>Будьте активними:</b>\n"
        f"• Лайк іншому: +1 бал\n"
        f"• Щоденна активність: +5 балів\n\n"
        f"🏆 <b>Досягнення:</b>\n"
        f"• Спеціальні винагороди за віхи\n\n"
        f"💡 <i>Чим активніше, тим більше балів!</i>"
    )
    
    await callback_query.message.answer(info_text, parse_mode="HTML")
    await callback_query.answer()

async def callback_start_duel(callback_query: CallbackQuery):
    """Почати дуель"""
    await callback_query.answer("⚔️ Функція дуелей буде додана в наступному оновленні!", show_alert=True)

async def callback_get_content(callback_query: CallbackQuery):
    """Отримати контент (анекдот/мем)"""
    content_type = "анекдот" if callback_query.data == "get_joke" else "мем"
    await callback_query.answer(f"😂 {content_type.capitalize()} буде відправлено!")
    
    # Тут можна додати логіку отримання контенту
    await callback_query.message.answer(f"😂 Ось ваш {content_type}! (функція в розробці)")

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_gamification_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів гейміфікації"""
    
    # Команди
    dp.message.register(cmd_profile, Command("profile"))
    dp.message.register(cmd_top, Command("top"))
    dp.message.register(cmd_daily, Command("daily"))
    
    # Callback запити
    dp.callback_query.register(callback_show_profile, F.data == "show_profile")
    dp.callback_query.register(callback_show_leaderboard, F.data == "show_leaderboard")
    dp.callback_query.register(callback_refresh_leaderboard, F.data == "refresh_leaderboard")
    dp.callback_query.register(callback_toggle_daily, F.data == "toggle_daily")
    dp.callback_query.register(callback_earn_points_info, F.data == "earn_points_info")
    dp.callback_query.register(callback_start_duel, F.data == "start_duel")
    dp.callback_query.register(callback_get_content, F.data.in_(["get_joke", "get_meme"]))
    
    logger.info("✅ Gamification handlers зареєстровані БЕЗ РИЗИКУ КРАШІВ")

# ===== ЕКСПОРТ =====
__all__ = [
    'register_gamification_handlers',
    'get_or_create_user', 
    'update_user_points',
    'get_top_users',
    'get_rank_by_points'
]

logger.info("🎮 Gamification handlers модуль завантажено з безпечною логікою")