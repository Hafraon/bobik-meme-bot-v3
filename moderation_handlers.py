#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери модерації контенту 🧠😂🔥
"""

import logging
import re

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config.settings import EMOJI, TEXTS, settings
from database.database import (
    get_pending_content, moderate_content, update_user_points, get_db_session
)
from database.models import Content, ContentStatus, User

logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Перевірка чи є користувач адміністратором"""
    return user_id == settings.ADMIN_ID

async def cmd_pending(message: Message):
    """Команда /pending - показати контент на модерації"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    pending_content = await get_pending_content()
    
    if not pending_content:
        await message.answer(f"{EMOJI['check']} Немає контенту на модерації!")
        return
    
    await message.answer(
        f"{EMOJI['brain']} <b>КОНТЕНТ НА МОДЕРАЦІЇ</b>\n\n"
        f"{EMOJI['fire']} Знайдено: {len(pending_content)} елементів\n"
        f"Використовуй /moderate для перегляду"
    )

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

async def show_content_for_moderation(message: Message, content: Content):
    """Показ контенту для модерації"""
    # Отримання інформації про автора
    with get_db_session() as session:
        author = session.query(User).filter(User.id == content.author_id).first()
    
    author_info = f"{author.first_name or 'Невідомий'}"
    if author.username:
        author_info += f" (@{author.username})"
    
    # Статистика автора
    author_stats = f"Балів: {author.points} | Ранг: {author.rank}"
    approval_stats = f"Схвалено: {author.jokes_approved + author.memes_approved} з {author.jokes_submitted + author.memes_submitted}"
    
    content_type_emoji = EMOJI['brain'] if content.content_type.value == 'joke' else EMOJI['laugh']
    content_type_name = "Анекдот" if content.content_type.value == 'joke' else "Мем"
    
    moderation_text = (
        f"{EMOJI['new']} <b>МОДЕРАЦІЯ КОНТЕНТУ</b>\n\n"
        f"{content_type_emoji} <b>Тип:</b> {content_type_name}\n"
        f"{EMOJI['profile']} <b>Автор:</b> {author_info}\n"
        f"{EMOJI['star']} <b>Статистика:</b> {author_stats}\n"
        f"{EMOJI['check']} <b>Схвалення:</b> {approval_stats}\n"
        f"{EMOJI['calendar']} <b>Надіслано:</b> {content.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"{EMOJI['fire']} <b>КОНТЕНТ:</b>\n{content.text}"
    )
    
    # Клавіатура модерації
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['check']} Схвалити",
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
        ]
    ])
    
    if content.content_type.value == 'meme' and content.file_id:
        # Якщо це мем з файлом
        try:
            await message.answer_photo(
                photo=content.file_id,
                caption=moderation_text,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Помилка показу мему: {e}")
            await message.answer(moderation_text, reply_markup=keyboard)
    else:
        # Текстовий контент
        await message.answer(moderation_text, reply_markup=keyboard)

async def cmd_approve_content(message: Message):
    """Команда /approve_ID - схвалення контенту за ID"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    # Витягуємо ID з команди
    match = re.search(r'/approve_(\d+)', message.text)
    if not match:
        await message.answer(f"{EMOJI['warning']} Неправильний формат! Використовуй: /approve_ID")
        return
    
    content_id = int(match.group(1))
    await approve_content(message, content_id)

async def cmd_reject_content(message: Message):
    """Команда /reject_ID - відхилення контенту за ID"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    # Витягуємо ID з команди
    match = re.search(r'/reject_(\d+)', message.text)
    if not match:
        await message.answer(f"{EMOJI['warning']} Неправильний формат! Використовуй: /reject_ID")
        return
    
    content_id = int(match.group(1))
    await reject_content(message, content_id)

async def approve_content(message: Message, content_id: int, comment: str = ""):
    """Схвалення контенту"""
    try:
        # Модерація в БД
        await moderate_content(
            content_id=content_id,
            moderator_id=message.from_user.id,
            approve=True,
            comment=comment
        )
        
        # Отримання інформації про контент для повідомлення автору
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            
            if content:
                # Нарахування балів автору
                await update_user_points(
                    content.author_id,
                    settings.POINTS_FOR_APPROVAL,
                    "схвалення контенту"
                )
                
                # Повідомлення автору
                try:
                    await message.bot.send_message(
                        content.author_id,
                        TEXTS["submission_approved"]
                    )
                except Exception as e:
                    logger.error(f"Не вдалося повідомити автора: {e}")
        
        await message.answer(
            f"{EMOJI['check']} <b>Контент #{content_id} схвалено!</b>\n"
            f"{EMOJI['fire']} Автор отримав +{settings.POINTS_FOR_APPROVAL} балів"
        )
        
        logger.info(f"✅ Адміністратор {message.from_user.id} схвалив контент {content_id}")
        
    except Exception as e:
        await message.answer(f"{EMOJI['cross']} Помилка схвалення: {e}")
        logger.error(f"Помилка схвалення контенту {content_id}: {e}")

async def reject_content(message: Message, content_id: int, comment: str = ""):
    """Відхилення контенту"""
    try:
        # Модерація в БД
        await moderate_content(
            content_id=content_id,
            moderator_id=message.from_user.id,
            approve=False,
            comment=comment
        )
        
        # Отримання інформації про контент для повідомлення автору
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            
            if content:
                # Повідомлення автору
                try:
                    rejection_text = TEXTS["submission_rejected"]
                    if comment:
                        rejection_text += f"\n\n{EMOJI['info']} <b>Коментар модератора:</b> {comment}"
                    
                    await message.bot.send_message(content.author_id, rejection_text)
                except Exception as e:
                    logger.error(f"Не вдалося повідомити автора: {e}")
        
        await message.answer(
            f"{EMOJI['cross']} <b>Контент #{content_id} відхилено</b>\n"
            f"{EMOJI['thinking']} Автор отримав сповіщення"
        )
        
        logger.info(f"❌ Адміністратор {message.from_user.id} відхилив контент {content_id}")
        
    except Exception as e:
        await message.answer(f"{EMOJI['cross']} Помилка відхилення: {e}")
        logger.error(f"Помилка відхилення контенту {content_id}: {e}")

async def cmd_admin_stats(message: Message):
    """Команда /admin_stats - статистика для адміністратора"""
    if not is_admin(message.from_user.id):
        await message.answer(f"{EMOJI['cross']} Ця команда доступна тільки адміністраторам!")
        return
    
    with get_db_session() as session:
        # Загальна статистика
        total_users = session.query(User).count()
        active_users_today = session.query(User).filter(
            User.last_active >= session.query(User.last_active).filter(
                User.last_active >= '2024-01-01'  # Заглушка для today
            )
        ).count()
        
        # Статистика контенту
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
        top_users = session.query(User).order_by(User.points.desc()).limit(5).all()
    
    stats_text = (
        f"{EMOJI['crown']} <b>СТАТИСТИКА АДМІНІСТРАТОРА</b>\n\n"
        f"{EMOJI['profile']} <b>КОРИСТУВАЧІ:</b>\n"
        f"• Всього: {total_users}\n"
        f"• Активних сьогодні: {active_users_today}\n\n"
        
        f"{EMOJI['brain']} <b>КОНТЕНТ:</b>\n"
        f"• На модерації: {pending_count}\n"
        f"• Схвалено: {approved_count}\n"
        f"• Відхилено: {rejected_count}\n\n"
        
        f"{EMOJI['trophy']} <b>ТОП-5 КОРИСТУВАЧІВ:</b>\n"
    )
    
    for i, user in enumerate(top_users, 1):
        stats_text += f"{i}. {user.first_name or 'Невідомий'} - {user.points} балів\n"
    
    # Клавіатура адміністратора
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['brain']} Модерувати", callback_data="start_moderation"),
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
    await approve_content(callback_query.message, content_id)
    
    # Показуємо наступний контент
    await callback_next_moderation(callback_query)

async def callback_reject_content(callback_query):
    """Callback відхилення контенту"""
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Тільки для адміністраторів!")
        return
    
    content_id = int(callback_query.data.split(':')[1])
    await reject_content(callback_query.message, content_id)
    
    # Показуємо наступний контент
    await callback_next_moderation(callback_query)

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
            f"{EMOJI['fire']} Немає більше контенту на розгляді"
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

def register_moderation_handlers(dp: Dispatcher):
    """Реєстрація хендлерів модерації"""
    
    # Команди для адміністратора
    dp.message.register(cmd_pending, Command("pending"))
    dp.message.register(cmd_moderate, Command("moderate"))
    dp.message.register(cmd_admin_stats, Command("admin_stats"))
    
    # Команди схвалення/відхилення за ID
    dp.message.register(cmd_approve_content, F.text.regexp(r'/approve_\d+'))
    dp.message.register(cmd_reject_content, F.text.regexp(r'/reject_\d+'))
    
    # Callback запити
    dp.callback_query.register(callback_approve_content, F.data.startswith("approve:"))
    dp.callback_query.register(callback_reject_content, F.data.startswith("reject:"))
    dp.callback_query.register(callback_skip_content, F.data.startswith("skip:"))
    dp.callback_query.register(callback_next_moderation, F.data == "next_moderation")
    dp.callback_query.register(callback_start_moderation, F.data == "start_moderation")
    dp.callback_query.register(callback_refresh_admin_stats, F.data == "refresh_admin_stats")