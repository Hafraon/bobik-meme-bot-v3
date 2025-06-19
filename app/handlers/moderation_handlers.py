#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери модерації контенту для адміністратора 🧠😂🔥
"""

import logging
import re
from datetime import datetime, timedelta

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

# Fallback імпорти
try:
    from config.settings import Settings
    settings = Settings()
    
    if not hasattr(settings, 'ADMIN_ID'):
        settings.ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    if not hasattr(settings, 'POINTS_FOR_APPROVAL'):
        settings.POINTS_FOR_APPROVAL = 20
        
except ImportError:
    import os
    class FallbackSettings:
        ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
        POINTS_FOR_APPROVAL = int(os.getenv("POINTS_FOR_APPROVAL", "20"))
    settings = FallbackSettings()

# EMOJI константи
EMOJI = {
    "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐", 
    "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
    "new": "🆕", "profile": "👤", "stats": "📊", "time": "⏰",
    "crown": "👑", "thinking": "🤔", "party": "🎉"
}

def is_admin(user_id: int) -> bool:
    """Перевірка чи є користувач адміністратором"""
    return user_id == settings.ADMIN_ID

# Fallback для модерації без БД
PENDING_CONTENT = []  # Тимчасове сховище
CONTENT_COUNTER = 1

class ContentItem:
    def __init__(self, id, author_id, text, content_type="joke", author_name="Невідомий"):
        self.id = id
        self.author_id = author_id
        self.text = text
        self.content_type = content_type
        self.author_name = author_name
        self.created_at = datetime.now()

async def get_pending_content():
    """Отримання контенту на модерації"""
    try:
        # Спроба отримання з БД
        from database.database import get_pending_content as db_get_pending
        return await db_get_pending()
    except ImportError:
        # Fallback - використовуємо пам'ять
        return PENDING_CONTENT

async def update_user_points(user_id: int, points: int, reason: str):
    """Нарахування балів користувачу"""
    try:
        from database.database import update_user_points as db_update_points
        await db_update_points(user_id, points, reason)
    except ImportError:
        logger.info(f"👤 Користувач {user_id}: +{points} балів за {reason}")

async def cmd_pending(message: Message):
    """Команда /pending - показати контент на модерації"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    pending_content = await get_pending_content()
    
    if not pending_content:
        await message.answer(f"{EMOJI['check']} Немає контенту на модерації!")
        return
    
    # Групування за типом
    jokes = [c for c in pending_content if getattr(c, 'content_type', 'joke') == 'joke']
    memes = [c for c in pending_content if getattr(c, 'content_type', 'joke') == 'meme']
    
    pending_text = (
        f"{EMOJI['brain']} <b>КОНТЕНТ НА МОДЕРАЦІЇ</b>\n\n"
        f"{EMOJI['fire']} <b>Всього:</b> {len(pending_content)} елементів\n"
        f"{EMOJI['brain']} Анекдотів: {len(jokes)}\n"
        f"{EMOJI['laugh']} Мемів: {len(memes)}\n\n"
        f"{EMOJI['info']} Використовуй /moderate для перегляду по черзі\n"
        f"або /approve_ID і /reject_ID для швидкої модерації"
    )
    
    # Клавіатура швидких дій
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['brain']} Почати модерацію", callback_data="start_moderation"),
            InlineKeyboardButton(text=f"{EMOJI['stats']} Статистика", callback_data="refresh_admin_stats")
        ]
    ])
    
    await message.answer(pending_text, reply_markup=keyboard)

async def cmd_moderate(message: Message):
    """Команда /moderate - модерація контенту по черзі"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    pending_content = await get_pending_content()
    
    if not pending_content:
        await message.answer(f"{EMOJI['check']} Немає контенту на модерації!")
        return
    
    # Показуємо перший елемент
    content = pending_content[0]
    await show_content_for_moderation(message, content)

async def show_content_for_moderation(message: Message, content):
    """Показ контенту для модерації з детальною інформацією"""
    
    # Інформація про автора
    author_info = getattr(content, 'author_name', 'Невідомий')
    author_id = getattr(content, 'author_id', 0)
    
    content_type_emoji = EMOJI['brain'] if getattr(content, 'content_type', 'joke') == 'joke' else EMOJI['laugh']
    content_type_name = "Анекдот" if getattr(content, 'content_type', 'joke') == 'joke' else "Мем"
    
    # Час очікування
    created_at = getattr(content, 'created_at', datetime.now())
    waiting_time = datetime.now() - created_at
    waiting_hours = int(waiting_time.total_seconds() // 3600)
    
    moderation_text = (
        f"{EMOJI['new']} <b>МОДЕРАЦІЯ КОНТЕНТУ #{content.id}</b>\n\n"
        f"{content_type_emoji} <b>Тип:</b> {content_type_name}\n"
        f"{EMOJI['profile']} <b>Автор:</b> {author_info} (ID: {author_id})\n"
        f"{EMOJI['time']} <b>Очікує:</b> {waiting_hours} годин\n\n"
        f"{EMOJI['fire']} <b>КОНТЕНТ:</b>\n{content.text}"
    )
    
    # Клавіатура модерації з додатковими опціями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['check']} Схвалити (+{settings.POINTS_FOR_APPROVAL})",
                callback_data=f"approve:{content.id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['cross']} Відхилити",
                callback_data=f"reject:{content.id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI['thinking']} Пропустити",
                callback_data=f"skip:{content.id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['stats']} Наступний",
                callback_data="next_moderation"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI['brain']} Завершити модерацію",
                callback_data="finish_moderation"
            )
        ]
    ])
    
    await message.answer(moderation_text, reply_markup=keyboard)

async def cmd_approve_content(message: Message):
    """Команда /approve_ID - швидке схвалення контенту за ID"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    # Витягуємо ID з команди
    match = re.search(r'/approve_(\d+)', message.text)
    if not match:
        await message.answer(f"{EMOJI['warning']} Неправильний формат! Використовуй: /approve_ID")
        return
    
    content_id = int(match.group(1))
    await approve_content(message, content_id, "Швидке схвалення через команду")

async def cmd_reject_content(message: Message):
    """Команда /reject_ID - швидке відхилення контенту за ID"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    # Витягуємо ID з команди
    match = re.search(r'/reject_(\d+)', message.text)
    if not match:
        await message.answer(f"{EMOJI['warning']} Неправильний формат! Використовуй: /reject_ID")
        return
    
    content_id = int(match.group(1))
    await reject_content(message, content_id, "Швидке відхилення через команду")

async def approve_content(message: Message, content_id: int, comment: str = ""):
    """Схвалення контенту з повним циклом нарахування балів"""
    try:
        # Пошук контенту в тимчасовому сховищі
        global PENDING_CONTENT
        content = None
        for item in PENDING_CONTENT:
            if item.id == content_id:
                content = item
                break
        
        if not content:
            await message.answer(f"{EMOJI['cross']} Контент #{content_id} не знайдений!")
            return
        
        # Видалення з черги модерації
        PENDING_CONTENT.remove(content)
        
        # Нарахування балів автору
        await update_user_points(
            content.author_id,
            settings.POINTS_FOR_APPROVAL,
            "схвалення контенту"
        )
        
        # Повідомлення автору
        try:
            content_type_name = "анекдот" if getattr(content, 'content_type', 'joke') == 'joke' else "мем"
            notification_text = (
                f"{EMOJI['party']} <b>УРА! Твій {content_type_name} схвалено!</b>\n\n"
                f"{EMOJI['star']} Він додано до загальної бази\n"
                f"{EMOJI['fire']} Ти отримав +{settings.POINTS_FOR_APPROVAL} балів!\n\n"
                f"{EMOJI['info']} При схваленні отримаєш ще більше балів!\n\n"
                f"{EMOJI['star']} Переглянь свій профіль: /profile"
            )
            
            await message.bot.send_message(content.author_id, notification_text)
        except Exception as e:
            logger.error(f"Не вдалося повідомити автора: {e}")
        
        # Відповідь адміністратору
        success_text = (
            f"{EMOJI['check']} <b>Контент #{content_id} схвалено!</b>\n\n"
            f"{EMOJI['profile']} Автор: {content.author_name}\n"
            f"{EMOJI['fire']} Автор отримав +{settings.POINTS_FOR_APPROVAL} балів"
        )
        
        # Клавіатура для продовження модерації
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Наступний контент", callback_data="next_moderation"),
                InlineKeyboardButton(text=f"{EMOJI['stats']} Статистика", callback_data="refresh_admin_stats")
            ]
        ])
        
        await message.answer(success_text, reply_markup=keyboard)
        
        logger.info(f"✅ Адміністратор {message.from_user.id} схвалив контент {content_id}")
        
    except Exception as e:
        await message.answer(f"{EMOJI['cross']} Помилка схвалення: {e}")
        logger.error(f"Помилка схвалення контенту {content_id}: {e}")

async def reject_content(message: Message, content_id: int, comment: str = ""):
    """Відхилення контенту з поясненням"""
    try:
        # Пошук контенту в тимчасовому сховищі
        global PENDING_CONTENT
        content = None
        for item in PENDING_CONTENT:
            if item.id == content_id:
                content = item
                break
        
        if not content:
            await message.answer(f"{EMOJI['cross']} Контент #{content_id} не знайдений!")
            return
        
        # Видалення з черги модерації
        PENDING_CONTENT.remove(content)
        
        # Повідомлення автору
        try:
            content_type_name = "анекдот" if getattr(content, 'content_type', 'joke') == 'joke' else "мем"
            rejection_text = (
                f"{EMOJI['cross']} <b>Твій {content_type_name} не пройшов модерацію</b>\n\n"
                f"{EMOJI['thinking']} Можливі причини:\n"
                f"• Не відповідає правилам спільноти\n"
                f"• Вже є в базі\n"
                f"• Низька якість контенту\n\n"
                f"{EMOJI['fire']} Спробуй надіслати інший!\n"
                f"{EMOJI['info']} Бали за подачу залишаються у тебе"
            )
            
            if comment:
                rejection_text += f"\n\n{EMOJI['info']} <b>Коментар модератора:</b> {comment}"
            
            await message.bot.send_message(content.author_id, rejection_text)
        except Exception as e:
            logger.error(f"Не вдалося повідомити автора: {e}")
        
        # Відповідь адміністратору
        rejection_response = (
            f"{EMOJI['cross']} <b>Контент #{content_id} відхилено</b>\n\n"
            f"{EMOJI['profile']} Автор: {content.author_name}\n"
            f"{EMOJI['thinking']} Автор отримав сповіщення"
        )
        
        if comment:
            rejection_response += f"\n{EMOJI['info']} Коментар: {comment}"
        
        # Клавіатура для продовження
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Наступний контент", callback_data="next_moderation"),
                InlineKeyboardButton(text=f"{EMOJI['stats']} Статистика", callback_data="refresh_admin_stats")
            ]
        ])
        
        await message.answer(rejection_response, reply_markup=keyboard)
        
        logger.info(f"❌ Адміністратор {message.from_user.id} відхилив контент {content_id}")
        
    except Exception as e:
        await message.answer(f"{EMOJI['cross']} Помилка відхилення: {e}")
        logger.error(f"Помилка відхилення контенту {content_id}: {e}")

async def cmd_admin_stats(message: Message):
    """Команда /admin_stats - детальна статистика для адміністратора"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    try:
        # Спроба отримання з БД
        from database.database import get_db_session
        from database.models import User, Content, Duel
        
        with get_db_session() as session:
            total_users = session.query(User).count()
            
            # Активність користувачів
            today = datetime.utcnow().date()
            active_users_today = session.query(User).filter(
                User.last_active >= today
            ).count()
            
            users_with_points = session.query(User).filter(User.points > 0).count()
            
            # Статистика контенту
            from database.models import ContentStatus
            pending_count = session.query(Content).filter(
                Content.status == ContentStatus.PENDING
            ).count()
            
            approved_count = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).count()
            
            rejected_count = session.query(Content).filter(
                Content.status == ContentStatus.REJECTED
            ).count()
            
            # Топ користувачі
            top_users = session.query(User).order_by(User.points.desc()).limit(3).all()
            
            stats_text = (
                f"{EMOJI['crown']} <b>ПАНЕЛЬ АДМІНІСТРАТОРА</b>\n\n"
                f"{EMOJI['profile']} <b>КОРИСТУВАЧІ:</b>\n"
                f"• Всього: {total_users}\n"
                f"• Активних сьогодні: {active_users_today}\n"
                f"• З балами: {users_with_points}\n\n"
                
                f"{EMOJI['brain']} <b>КОНТЕНТ:</b>\n"
                f"• На модерації: {pending_count}\n"
                f"• Схвалено: {approved_count}\n"
                f"• Відхилено: {rejected_count}\n\n"
                
                f"{EMOJI['fire']} <b>ТОП-3 КОРИСТУВАЧІВ:</b>\n"
            )
            
            medals = ["🥇", "🥈", "🥉"]
            for i, user in enumerate(top_users):
                medal = medals[i] if i < len(medals) else "🏅"
                stats_text += f"{medal} {user.first_name or 'Невідомий'} - {user.points} балів\n"
            
    except ImportError:
        # Fallback статистика
        pending_count = len(PENDING_CONTENT)
        
        stats_text = (
            f"{EMOJI['crown']} <b>ПАНЕЛЬ АДМІНІСТРАТОРА</b>\n\n"
            f"{EMOJI['warning']} <b>Режим:</b> Fallback (без БД)\n\n"
            f"{EMOJI['brain']} <b>КОНТЕНТ:</b>\n"
            f"• На модерації: {pending_count}\n\n"
            f"{EMOJI['info']} Для повної статистики додай БД"
        )
    
    # Клавіатура адміністратора
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['brain']} Модерувати", 
                callback_data="start_moderation"
            ),
            InlineKeyboardButton(text=f"{EMOJI['stats']} Оновити", callback_data="refresh_admin_stats")
        ]
    ])
    
    await message.answer(stats_text, reply_markup=keyboard)

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_approve_content(callback_query):
    """Callback схвалення контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    content_id = int(callback_query.data.split(':')[1])
    await approve_content(callback_query.message, content_id, "Схвалено через інтерфейс модерації")
    await callback_query.answer(f"{EMOJI['check']} Контент схвалено!")

async def callback_reject_content(callback_query):
    """Callback відхилення контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    content_id = int(callback_query.data.split(':')[1])
    await reject_content(callback_query.message, content_id, "Відхилено через інтерфейс модерації")
    await callback_query.answer(f"{EMOJI['cross']} Контент відхилено!")

async def callback_skip_content(callback_query):
    """Callback пропуску контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    await callback_query.answer("⏭️ Пропущено")
    await callback_next_moderation(callback_query)

async def callback_next_moderation(callback_query):
    """Callback показу наступного контенту на модерації"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    pending_content = await get_pending_content()
    
    if not pending_content:
        await callback_query.message.edit_text(
            f"{EMOJI['check']} <b>Модерацію завершено!</b>\n\n"
            f"{EMOJI['fire']} Немає більше контенту на розгляді\n\n"
            f"{EMOJI['stats']} Переглянь статистику: /admin_stats"
        )
        return
    
    # Показуємо перший елемент зі списку
    content = pending_content[0]
    await show_content_for_moderation(callback_query.message, content)
    await callback_query.answer()

async def callback_start_moderation(callback_query):
    """Callback початку модерації"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    await callback_next_moderation(callback_query)

async def callback_refresh_admin_stats(callback_query):
    """Callback оновлення статистики адміністратора"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    await cmd_admin_stats(callback_query.message)
    await callback_query.answer("🔄 Статистику оновлено!")

async def callback_finish_moderation(callback_query):
    """Callback завершення модерації"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    pending_count = len(await get_pending_content())
    
    finish_text = (
        f"{EMOJI['check']} <b>Сесію модерації завершено</b>\n\n"
        f"{EMOJI['brain']} Залишилось на модерації: {pending_count}\n\n"
        f"{EMOJI['info']} Для продовження використовуй /moderate"
    )
    
    await callback_query.message.edit_text(finish_text)
    await callback_query.answer("✅ Модерацію завершено")

# Функція для додавання контенту в чергу модерації (для fallback)
def add_content_to_moderation(author_id: int, text: str, content_type: str = "joke", author_name: str = "Невідомий"):
    """Додавання контенту в чергу модерації (fallback функція)"""
    global CONTENT_COUNTER, PENDING_CONTENT
    
    content = ContentItem(
        id=CONTENT_COUNTER,
        author_id=author_id,
        text=text,
        content_type=content_type,
        author_name=author_name
    )
    
    PENDING_CONTENT.append(content)
    CONTENT_COUNTER += 1
    
    logger.info(f"📝 Додано контент #{content.id} на модерацію від {author_name}")
    return content

def register_moderation_handlers(dp: Dispatcher):
    """Реєстрація хендлерів модерації"""
    
    # Команди для адміністратора
    dp.message.register(cmd_pending, Command("pending"))
    dp.message.register(cmd_moderate, Command("moderate"))
    dp.message.register(cmd_admin_stats, Command("admin_stats"))
    
    # Команди швидкого схвалення/відхилення
    dp.message.register(cmd_approve_content, F.text.regexp(r'/approve_\d+'))
    dp.message.register(cmd_reject_content, F.text.regexp(r'/reject_\d+'))
    
    # Callback запити
    dp.callback_query.register(callback_approve_content, F.data.startswith("approve:"))
    dp.callback_query.register(callback_reject_content, F.data.startswith("reject:"))
    dp.callback_query.register(callback_skip_content, F.data.startswith("skip:"))
    dp.callback_query.register(callback_next_moderation, F.data == "next_moderation")
    dp.callback_query.register(callback_start_moderation, F.data == "start_moderation")
    dp.callback_query.register(callback_refresh_admin_stats, F.data == "refresh_admin_stats")
    dp.callback_query.register(callback_finish_moderation, F.data == "finish_moderation")
    
    logger.info("✅ Moderation handlers зареєстровані")