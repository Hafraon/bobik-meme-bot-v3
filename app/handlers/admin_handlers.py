#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from typing import Optional, List

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

# FSM для модерації
class ModerationStates(StatesGroup):
    waiting_for_rejection_reason = State()

def is_admin(user_id: int) -> bool:
    """Перевірка чи є користувач адміністратором"""
    try:
        from config.settings import settings
        return settings.is_admin(user_id)
    except ImportError:
        import os
        admin_id = int(os.getenv('ADMIN_ID', 0))
        return user_id == admin_id

async def admin_required(message: Message) -> bool:
    """Декоратор для перевірки прав адміна"""
    if not is_admin(message.from_user.id):
        await message.answer("🔒 <b>Недостатньо прав</b>\n\nЦя команда доступна тільки адміністраторам.")
        return False
    return True

async def cmd_admin_stats(message: Message):
    """Команда /admin_stats - статистика для адміна"""
    if not await admin_required(message):
        return
    
    try:
        from database.services import get_basic_stats
        
        stats = get_basic_stats()
        
        # Додаткова статистика для адміна
        stats_text = f"📊 <b>АДМІН СТАТИСТИКА</b>\n\n"
        
        stats_text += f"👥 <b>Користувачі:</b>\n"
        stats_text += f"   Всього: {stats['total_users']}\n"
        stats_text += f"   Активних сьогодні: calculating...\n\n"
        
        stats_text += f"📝 <b>Контент:</b>\n"
        stats_text += f"   Всього: {stats['total_content']}\n"
        stats_text += f"   ✅ Схвалено: {stats['approved_content']}\n"
        stats_text += f"   ⏳ На розгляді: {stats['pending_content']}\n"
        stats_text += f"   ❌ Відхилено: calculating...\n\n"
        
        stats_text += f"⚔️ <b>Дуелі:</b>\n"
        stats_text += f"   Всього: {stats['total_duels']}\n"
        stats_text += f"   Активних: calculating...\n\n"
        
        stats_text += f"🕐 <b>Час:</b> {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}"
        
        # Кнопки адмін дій
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Модерувати", callback_data="admin_moderate"),
                InlineKeyboardButton(text="📋 Контент на розгляді", callback_data="admin_pending")
            ],
            [
                InlineKeyboardButton(text="👥 Топ користувачів", callback_data="admin_top_users"),
                InlineKeyboardButton(text="🔄 Оновити статистику", callback_data="admin_refresh_stats")
            ]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard)
        
        logger.info(f"Admin {message.from_user.id} viewed stats")
        
    except Exception as e:
        logger.error(f"Error in admin stats: {e}")
        await message.answer("❌ Помилка отримання статистики.")

async def cmd_moderate(message: Message):
    """Команда /moderate - початок модерації"""
    if not await admin_required(message):
        return
    
    try:
        from database.services import get_db_session
        from database.models import Content, ContentStatus, User
        
        with get_db_session() as session:
            # Отримуємо контент на модерації
            pending_content = session.query(Content)\
                                   .filter(Content.status == ContentStatus.PENDING.value)\
                                   .order_by(Content.created_at.asc())\
                                   .limit(1)\
                                   .first()
            
            if not pending_content:
                await message.answer(
                    "✅ <b>Модерація завершена!</b>\n\n"
                    "Немає контенту на розгляді."
                )
                return
            
            # Отримуємо автора
            author = session.query(User).filter(User.id == pending_content.author_id).first()
            author_name = "Невідомий"
            if author:
                author_name = author.first_name or author.username or f"User{author.user_id}"
            
            # Формуємо повідомлення
            moderation_text = f"🛡️ <b>МОДЕРАЦІЯ КОНТЕНТУ</b>\n\n"
            moderation_text += f"📄 <b>ID:</b> {pending_content.id}\n"
            moderation_text += f"📂 <b>Тип:</b> {pending_content.content_type}\n"
            moderation_text += f"👤 <b>Автор:</b> {author_name} (ID: {pending_content.author_user_id})\n"
            moderation_text += f"📅 <b>Дата:</b> {pending_content.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            moderation_text += f"📝 <b>Контент:</b>\n{pending_content.text}"
            
            # Кнопки модерації
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Схвалити", callback_data=f"moderate_approve_{pending_content.id}"),
                    InlineKeyboardButton(text="❌ Відхилити", callback_data=f"moderate_reject_{pending_content.id}")
                ],
                [
                    InlineKeyboardButton(text="⏭️ Пропустити", callback_data="moderate_next"),
                    InlineKeyboardButton(text="🔄 Оновити", callback_data="moderate_refresh")
                ]
            ])
            
            await message.answer(moderation_text, reply_markup=keyboard)
            
            logger.info(f"Admin {message.from_user.id} started moderating content {pending_content.id}")
        
    except Exception as e:
        logger.error(f"Error in moderate command: {e}")
        await message.answer("❌ Помилка завантаження контенту для модерації.")

async def cmd_pending(message: Message):
    """Команда /pending - список контенту на розгляді"""
    if not await admin_required(message):
        return
    
    try:
        from database.services import get_db_session
        from database.models import Content, ContentStatus, User
        
        with get_db_session() as session:
            # Отримуємо весь контент на модерації
            pending_content = session.query(Content)\
                                   .filter(Content.status == ContentStatus.PENDING.value)\
                                   .order_by(Content.created_at.asc())\
                                   .limit(10)\
                                   .all()
            
            if not pending_content:
                await message.answer(
                    "✅ <b>Список порожній!</b>\n\n"
                    "Немає контенту на розгляді."
                )
                return
            
            # Формуємо список
            pending_text = f"📋 <b>КОНТЕНТ НА РОЗГЛЯДІ</b>\n\n"
            
            for content in pending_content:
                # Отримуємо автора
                author = session.query(User).filter(User.id == content.author_id).first()
                author_name = "Невідомий"
                if author:
                    author_name = author.first_name or author.username or f"User{author.user_id}"
                
                pending_text += f"🔹 <b>ID {content.id}</b> ({content.content_type})\n"
                pending_text += f"   👤 {author_name}\n"
                pending_text += f"   📅 {content.created_at.strftime('%d.%m %H:%M')}\n"
                pending_text += f"   📝 {content.text[:50]}{'...' if len(content.text) > 50 else ''}\n\n"
            
            if len(pending_content) == 10:
                pending_text += "📌 Показано перших 10 записів\n\n"
            
            # Кнопки швидких дій
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🛡️ Почати модерацію", callback_data="admin_moderate"),
                    InlineKeyboardButton(text="🔄 Оновити список", callback_data="admin_pending")
                ]
            ])
            
            await message.answer(pending_text, reply_markup=keyboard)
            
            logger.info(f"Admin {message.from_user.id} viewed pending list")
        
    except Exception as e:
        logger.error(f"Error in pending command: {e}")
        await message.answer("❌ Помилка завантаження списку.")

async def cmd_approve(message: Message):
    """Команда /approve_ID - швидке схвалення"""
    if not await admin_required(message):
        return
    
    try:
        # Парсимо ID з команди
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("❌ Використання: /approve_ID\nПриклад: /approve_5")
            return
        
        try:
            content_id = int(parts[1])
        except ValueError:
            await message.answer("❌ ID має бути числом.")
            return
        
        # Схвалюємо контент
        result = await approve_content(content_id, message.from_user.id)
        
        if result:
            await message.answer(f"✅ Контент ID {content_id} схвалено!")
        else:
            await message.answer(f"❌ Помилка схвалення контенту ID {content_id}")
            
    except Exception as e:
        logger.error(f"Error in approve command: {e}")
        await message.answer("❌ Помилка команди схвалення.")

async def cmd_reject(message: Message):
    """Команда /reject_ID - швидке відхилення"""
    if not await admin_required(message):
        return
    
    try:
        # Парсимо ID з команди
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Використання: /reject_ID [причина]\nПриклад: /reject_5 Неприйнятний контент")
            return
        
        try:
            content_id = int(parts[1])
        except ValueError:
            await message.answer("❌ ID має бути числом.")
            return
        
        # Причина відхилення (опціонально)
        reason = " ".join(parts[2:]) if len(parts) > 2 else "Не вказано"
        
        # Відхиляємо контент
        result = await reject_content(content_id, message.from_user.id, reason)
        
        if result:
            await message.answer(f"❌ Контент ID {content_id} відхилено!\nПричина: {reason}")
        else:
            await message.answer(f"❌ Помилка відхилення контенту ID {content_id}")
            
    except Exception as e:
        logger.error(f"Error in reject command: {e}")
        await message.answer("❌ Помилка команди відхилення.")

async def approve_content(content_id: int, admin_id: int) -> bool:
    """Схвалення контенту"""
    try:
        from database.services import get_db_session, update_user_points
        from database.models import Content, ContentStatus, AdminAction
        
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            
            if not content:
                return False
            
            if content.status != ContentStatus.PENDING.value:
                return False
            
            # Схвалюємо контент
            content.status = ContentStatus.APPROVED.value
            content.moderated_by = admin_id
            content.moderated_at = datetime.now()
            
            # Нараховуємо бали автору
            update_user_points(content.author_user_id, 20, f"схвалення контенту ID {content_id}")
            
            # Оновлюємо статистику автора
            from database.models import User
            author = session.query(User).filter(User.id == content.author_id).first()
            if author:
                author.total_approvals += 1
            
            # Записуємо дію адміна
            admin_action = AdminAction(
                admin_id=admin_id,
                action_type="approve_content",
                target_type="content",
                target_id=content_id,
                description=f"Схвалено контент типу {content.content_type}",
                created_at=datetime.now()
            )
            session.add(admin_action)
            
            session.commit()
            
            logger.info(f"Admin {admin_id} approved content {content_id}")
            return True
            
    except Exception as e:
        logger.error(f"Error approving content {content_id}: {e}")
        return False

async def reject_content(content_id: int, admin_id: int, reason: str = "") -> bool:
    """Відхилення контенту"""
    try:
        from database.services import get_db_session
        from database.models import Content, ContentStatus, AdminAction
        
        with get_db_session() as session:
            content = session.query(Content).filter(Content.id == content_id).first()
            
            if not content:
                return False
            
            if content.status != ContentStatus.PENDING.value:
                return False
            
            # Відхиляємо контент
            content.status = ContentStatus.REJECTED.value
            content.moderated_by = admin_id
            content.moderated_at = datetime.now()
            content.rejection_reason = reason
            
            # Записуємо дію адміна
            admin_action = AdminAction(
                admin_id=admin_id,
                action_type="reject_content",
                target_type="content",
                target_id=content_id,
                description=f"Відхилено контент типу {content.content_type}",
                reason=reason,
                created_at=datetime.now()
            )
            session.add(admin_action)
            
            session.commit()
            
            logger.info(f"Admin {admin_id} rejected content {content_id}: {reason}")
            return True
            
    except Exception as e:
        logger.error(f"Error rejecting content {content_id}: {e}")
        return False

async def handle_admin_callbacks(callback: CallbackQuery, state: FSMContext):
    """Обробка callback'ів адміна"""
    if not is_admin(callback.from_user.id):
        await callback.answer("🔒 Недостатньо прав")
        return
    
    try:
        data = callback.data
        
        if data == "admin_moderate":
            # Почати модерацію
            await cmd_moderate(callback.message)
            await callback.answer()
            
        elif data == "admin_pending":
            # Показати список на розгляді
            await cmd_pending(callback.message)
            await callback.answer()
            
        elif data == "admin_refresh_stats":
            # Оновити статистику
            await cmd_admin_stats(callback.message)
            await callback.answer("🔄 Статистику оновлено")
            
        elif data == "admin_top_users":
            # Показати топ користувачів
            try:
                from database.services import get_top_users
                top_users = get_top_users(10)
                
                if top_users:
                    top_text = "🏆 <b>ТОП КОРИСТУВАЧІВ</b>\n\n"
                    for i, user in enumerate(top_users, 1):
                        name = user['first_name'] or user['username'] or f"User{user['user_id']}"
                        top_text += f"{i}. {name} - {user['points']} балів ({user['rank']})\n"
                    
                    await callback.message.answer(top_text)
                else:
                    await callback.message.answer("👥 Немає користувачів в рейтингу")
                    
            except Exception as e:
                logger.error(f"Error getting top users: {e}")
                await callback.message.answer("❌ Помилка отримання рейтингу")
            
            await callback.answer()
            
        elif data.startswith("moderate_approve_"):
            # Схвалення контенту
            content_id = int(data.split("_")[-1])
            
            result = await approve_content(content_id, callback.from_user.id)
            
            if result:
                await callback.answer("✅ Контент схвалено!", show_alert=True)
                # Показати наступний контент
                await cmd_moderate(callback.message)
            else:
                await callback.answer("❌ Помилка схвалення", show_alert=True)
                
        elif data.startswith("moderate_reject_"):
            # Відхилення контенту
            content_id = int(data.split("_")[-1])
            
            # Запитуємо причину
            await state.update_data(reject_content_id=content_id)
            await state.set_state(ModerationStates.waiting_for_rejection_reason)
            
            await callback.message.answer(
                f"❌ <b>Відхилення контенту ID {content_id}</b>\n\n"
                "Введіть причину відхилення або надішліть /skip для відхилення без причини:"
            )
            await callback.answer()
            
        elif data == "moderate_next":
            # Пропустити поточний контент
            await cmd_moderate(callback.message)
            await callback.answer("⏭️ Наступний контент")
            
        elif data == "moderate_refresh":
            # Оновити поточний контент
            await cmd_moderate(callback.message)
            await callback.answer("🔄 Оновлено")
            
        else:
            await callback.answer("❓ Невідома дія")
            
    except Exception as e:
        logger.error(f"Error in admin callback: {e}")
        await callback.answer("❌ Помилка обробки!")

async def handle_rejection_reason(message: Message, state: FSMContext):
    """Обробка введення причини відхилення"""
    try:
        data = await state.get_data()
        content_id = data.get('reject_content_id')
        
        if not content_id:
            await message.answer("❌ Помилка: ID контенту не знайдено.")
            await state.clear()
            return
        
        reason = message.text.strip() if message.text else "Не вказано"
        
        # Відхиляємо контент
        result = await reject_content(content_id, message.from_user.id, reason)
        
        if result:
            await message.answer(f"❌ Контент ID {content_id} відхилено!\nПричина: {reason}")
            # Показати наступний контент
            await cmd_moderate(message)
        else:
            await message.answer(f"❌ Помилка відхилення контенту ID {content_id}")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error handling rejection reason: {e}")
        await message.answer("❌ Помилка обробки причини.")
        await state.clear()

async def cmd_skip_rejection(message: Message, state: FSMContext):
    """Команда /skip - відхилення без причини"""
    try:
        data = await state.get_data()
        content_id = data.get('reject_content_id')
        
        if content_id:
            result = await reject_content(content_id, message.from_user.id, "Причина не вказана")
            
            if result:
                await message.answer(f"❌ Контент ID {content_id} відхилено без вказання причини.")
                await cmd_moderate(message)
            else:
                await message.answer(f"❌ Помилка відхилення контенту ID {content_id}")
        else:
            await message.answer("❌ Немає активного процесу відхилення.")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in skip rejection: {e}")
        await message.answer("❌ Помилка команди.")
        await state.clear()

def register_admin_handlers(dp: Dispatcher):
    """Реєстрація адмін хендлерів"""
    
    # Команди адміна
    dp.message.register(cmd_admin_stats, Command("admin_stats"))
    dp.message.register(cmd_moderate, Command("moderate"))
    dp.message.register(cmd_pending, Command("pending"))
    dp.message.register(cmd_approve, Command("approve"))
    dp.message.register(cmd_reject, Command("reject"))
    dp.message.register(cmd_skip_rejection, Command("skip"))
    
    # Callback'и адміна
    dp.callback_query.register(
        handle_admin_callbacks,
        lambda c: c.data and c.data.startswith(("admin_", "moderate_"))
    )
    
    # FSM для введення причини відхилення
    dp.message.register(
        handle_rejection_reason,
        ModerationStates.waiting_for_rejection_reason
    )
    
    logger.info("✅ Admin handlers registered")

# Експорт для використання
__all__ = [
    'register_admin_handlers',
    'is_admin',
    'approve_content',
    'reject_content',
    'ModerationStates'
]