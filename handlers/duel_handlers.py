#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПОВНИЙ ФУНКЦІОНАЛ ДУЕЛІВ ЖАРТІВ 🧠😂🔥
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton
)

logger = logging.getLogger(__name__)

# Fallback налаштування
try:
    from config.settings import settings
    DUEL_VOTING_TIME = getattr(settings, 'DUEL_VOTING_TIME', 300)  # 5 хвилин
    MIN_VOTES_FOR_DUEL = getattr(settings, 'MIN_VOTES_FOR_DUEL', 3)
    POINTS_FOR_DUEL_WIN = getattr(settings, 'POINTS_FOR_DUEL_WIN', 15)
    POINTS_FOR_DUEL_PARTICIPATION = getattr(settings, 'POINTS_FOR_DUEL_PARTICIPATION', 5)
except ImportError:
    import os
    DUEL_VOTING_TIME = int(os.getenv("DUEL_VOTING_TIME", "300"))
    MIN_VOTES_FOR_DUEL = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
    POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
    POINTS_FOR_DUEL_PARTICIPATION = int(os.getenv("POINTS_FOR_DUEL_PARTICIPATION", "5"))

EMOJI = {
    "vs": "⚔️", "fire": "🔥", "crown": "👑", "trophy": "🏆",
    "star": "⭐", "gem": "💎", "rocket": "🚀", "timer": "⏰",
    "vote": "🗳️", "winner": "🎉", "thumbs_up": "👍", "thumbs_down": "👎"
}

# ===== ОСНОВНІ КОМАНДИ ДУЕЛІВ =====

async def cmd_duel(message: Message):
    """Команда /duel - створити або приєднатися до дуелі"""
    user_id = message.from_user.id
    
    # Перевірити чи є текст після команди
    command_args = message.text.split(' ', 1)
    
    if len(command_args) > 1:
        # Є текст - створити дуель з цим жартом
        joke_text = command_args[1].strip()
        await create_duel_with_text(message, joke_text)
    else:
        # Показати меню дуелів
        await show_duel_menu(message)

async def show_duel_menu(message: Message):
    """Показати меню дуелів"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Боєць"
    
    try:
        from database import get_active_duels, get_user_by_id
        
        # Отримати статистику користувача
        user = await get_user_by_id(user_id)
        active_duels = await get_active_duels()
        
        duel_text = f"{EMOJI['vs']} <b>АРЕНА ДУЕЛІВ ЖАРТІВ</b>\n\n"
        duel_text += f"🎭 Вітаю, {first_name}!\n\n"
        
        if user:
            win_rate = (user.duels_won / (user.duels_won + user.duels_lost) * 100) if (user.duels_won + user.duels_lost) > 0 else 0
            duel_text += f"📊 <b>Ваша статистика:</b>\n"
            duel_text += f"🏆 Перемог: {user.duels_won}\n"
            duel_text += f"💔 Поразок: {user.duels_lost}\n"
            duel_text += f"📈 Винрейт: {win_rate:.1f}%\n\n"
        
        duel_text += f"⚔️ <b>Що таке дуель жартів?</b>\n"
        duel_text += f"Два учасники змагаються жартами, а інші користувачі голосують за найсмішніший!\n\n"
        
        duel_text += f"🎯 <b>Нагороди:</b>\n"
        duel_text += f"• Переможець: +{POINTS_FOR_DUEL_WIN} балів\n"
        duel_text += f"• Учасник: +{POINTS_FOR_DUEL_PARTICIPATION} балів\n"
        duel_text += f"• Голосуючий: +2 бали\n\n"
        
        if active_duels:
            duel_text += f"🔥 <b>Активних дуелів: {len(active_duels)}</b>\n"
            duel_text += f"Приєднайтесь до голосування!\n\n"
        
        duel_text += f"Що бажаєте зробити?"
        
        keyboard = get_duel_menu_keyboard(len(active_duels) > 0)
        await message.answer(duel_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ Помилка меню дуелів: {e}")
        await message.answer(f"❌ Помилка завантаження меню дуелів: {e}")

def get_duel_menu_keyboard(has_active_duels: bool = False) -> InlineKeyboardMarkup:
    """Клавіатура меню дуелів"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{EMOJI['fire']} Створити дуель",
                callback_data="create_duel"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['rocket']} Випадковий дуель",
                callback_data="random_duel"
            )
        ]
    ]
    
    if has_active_duels:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{EMOJI['vote']} Голосувати в дуелях",
                callback_data="show_active_duels"
            )
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton(
                text=f"{EMOJI['trophy']} ТОП дуелянтів",
                callback_data="duel_leaderboard"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['star']} Історія дуелів",
                callback_data="duel_history"
            )
        ],
        [
            InlineKeyboardButton(
                text="❓ Як грати",
                callback_data="duel_help"
            )
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ===== СТВОРЕННЯ ДУЕЛІВ =====

async def create_duel_with_text(message: Message, joke_text: str):
    """Створити дуель з конкретним жартом"""
    user_id = message.from_user.id
    
    # Валідація жарту
    if len(joke_text) < 10:
        await message.answer(
            f"❌ Жарт занадто короткий для дуелі!\n"
            f"Мінімум 10 символів. Спробуйте ще раз."
        )
        return
    
    if len(joke_text) > 500:
        await message.answer(
            f"❌ Жарт занадто довгий для дуелі!\n"
            f"Максимум 500 символів. Скоротіть текст."
        )
        return
    
    # Створити дуель
    await create_new_duel(message, user_id, joke_text)

async def create_new_duel(message: Message, challenger_id: int, joke_text: str):
    """Створити новий дуель"""
    try:
        from database import create_duel, add_content_for_moderation
        
        # Додати жарт як контент (він буде автоматично схвалений для дуелі)
        content = await add_content_for_moderation(
            author_id=challenger_id,
            content_text=joke_text,
            content_type="JOKE"
        )
        
        if not content:
            await message.answer("❌ Помилка створення контенту для дуелі")
            return
        
        # Автоматично схвалити контент для дуелі
        from database import moderate_content
        await moderate_content(
            content_id=content.id,
            action="APPROVE",
            moderator_id=challenger_id,
            comment="Автоматично схвалено для дуелі"
        )
        
        # Створити дуель
        duel = await create_duel(
            challenger_id=challenger_id,
            challenger_content_id=content.id
        )
        
        if duel:
            duel_text = (
                f"{EMOJI['vs']} <b>ДУЕЛЬ СТВОРЕНО!</b>\n\n"
                f"🎭 Ваш жарт готовий до бою!\n\n"
                f"📝 <i>Ваш жарт:</i>\n{joke_text}\n\n"
                f"⏳ Чекаємо на суперника...\n"
                f"🔥 Дуель почнеться коли хтось прийме виклик!\n\n"
                f"🎯 Нагороди:\n"
                f"• Переможець: +{POINTS_FOR_DUEL_WIN} балів\n"
                f"• Учасник: +{POINTS_FOR_DUEL_PARTICIPATION} балів"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Поділитися дуеллю",
                        callback_data=f"share_duel_{duel.id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Скасувати дуель",
                        callback_data=f"cancel_duel_{duel.id}"
                    )
                ]
            ])
            
            await message.answer(duel_text, reply_markup=keyboard)
            
            # Повідомити в загальний чат про новий дуель
            await announce_new_duel(message.bot, duel, joke_text)
            
            logger.info(f"⚔️ Користувач {challenger_id} створив дуель #{duel.id}")
            
        else:
            await message.answer("❌ Помилка створення дуелі")
            
    except Exception as e:
        logger.error(f"❌ Помилка створення дуелі: {e}")
        await message.answer(f"❌ Помилка створення дуелі: {e}")

async def announce_new_duel(bot, duel, joke_text: str):
    """Анонсувати новий дуель"""
    try:
        # Тут можна було б надіслати в канал або групу
        # Поки що просто логуємо
        logger.info(f"📢 Новий дуель #{duel.id} створено: {joke_text[:50]}...")
        
    except Exception as e:
        logger.error(f"❌ Помилка анонсування дуелі: {e}")

# ===== ПРИЄДНАННЯ ДО ДУЕЛІ =====

async def join_random_duel(callback_query: CallbackQuery):
    """Приєднатися до випадкової дуелі"""
    user_id = callback_query.from_user.id
    
    try:
        from database import get_active_duels
        
        # Знайти дуелі без суперника
        active_duels = await get_active_duels()
        available_duels = [d for d in active_duels if not d.opponent_id and d.challenger_id != user_id]
        
        if not available_duels:
            await callback_query.answer(
                "😔 Немає доступних дуелів!\nСтворіть свій дуель.",
                show_alert=True
            )
            return
        
        # Вибрати випадковий дуель
        import random
        selected_duel = random.choice(available_duels)
        
        # Показати дуель для приєднання
        await show_duel_for_joining(callback_query.message, selected_duel)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"❌ Помилка приєднання до дуелі: {e}")
        await callback_query.answer("❌ Помилка пошуку дуелі", show_alert=True)

async def show_duel_for_joining(message: Message, duel):
    """Показати дуель для приєднання"""
    try:
        from database import get_content_by_id, get_user_by_id
        
        # Отримати контент challenger'а
        challenger_content = await get_content_by_id(duel.challenger_content_id)
        challenger = await get_user_by_id(duel.challenger_id)
        
        if not challenger_content or not challenger:
            await message.answer("❌ Помилка завантаження дуелі")
            return
        
        duel_text = (
            f"{EMOJI['vs']} <b>ДУЕЛЬ ОЧІКУЄ СУПЕРНИКА!</b>\n\n"
            f"🎭 Challenger: {challenger.first_name or 'Невідомий'}\n"
            f"💰 Бали: {challenger.points:,}\n\n"
            f"📝 <b>Їх жарт:</b>\n<i>{challenger_content.text}</i>\n\n"
            f"⚔️ Готові прийняти виклик?\n"
            f"Надішліть свій жарт для участі в дуелі!\n\n"
            f"🎯 Нагороди:\n"
            f"• Переможець: +{POINTS_FOR_DUEL_WIN} балів\n"
            f"• Учасник: +{POINTS_FOR_DUEL_PARTICIPATION} балів"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['fire']} Прийняти виклик!",
                    callback_data=f"accept_duel_{duel.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Інші дуелі",
                    callback_data="show_active_duels"
                ),
                InlineKeyboardButton(
                    text="🏠 Головне меню",
                    callback_data="duel_main_menu"
                )
            ]
        ])
        
        await message.answer(duel_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ Помилка показу дуелі: {e}")
        await message.answer("❌ Помилка завантаження дуелі")

# ===== ГОЛОСУВАННЯ В ДУЕЛЯХ =====

async def show_active_duels_for_voting(message: Message):
    """Показати активні дуелі для голосування"""
    try:
        from database import get_active_duels
        
        active_duels = await get_active_duels()
        voting_duels = [d for d in active_duels if d.opponent_id is not None]
        
        if not voting_duels:
            await message.answer(
                f"😴 Зараз немає активних дуелів для голосування.\n\n"
                f"🔥 Створіть свій дуель або почекайте поки інші створять!"
            )
            return
        
        duels_text = f"{EMOJI['vote']} <b>АКТИВНІ ДУЕЛІ</b>\n\n"
        duels_text += f"Голосуйте за найсмішніший жарт! (+2 бали за голос)\n\n"
        
        for i, duel in enumerate(voting_duels[:5], 1):  # Показуємо перші 5
            time_left = duel.ends_at - datetime.utcnow() if duel.ends_at else timedelta(minutes=5)
            time_left_str = f"{int(time_left.total_seconds() // 60)}хв" if time_left.total_seconds() > 0 else "завершується"
            
            duels_text += f"#{duel.id} - {EMOJI['timer']} {time_left_str}\n"
            duels_text += f"👍 {duel.challenger_votes} vs {duel.opponent_votes} 👎\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🗳️ Голосувати в дуелі #{voting_duels[0].id}",
                    callback_data=f"vote_duel_{voting_duels[0].id}"
                )
            ] if voting_duels else [],
            [
                InlineKeyboardButton(
                    text="🔄 Оновити список",
                    callback_data="refresh_active_duels"
                ),
                InlineKeyboardButton(
                    text="🏠 Головне меню",
                    callback_data="duel_main_menu"
                )
            ]
        ])
        
        await message.answer(duels_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ Помилка показу активних дуелів: {e}")
        await message.answer("❌ Помилка завантаження дуелів")

async def show_duel_for_voting(message: Message, duel_id: int):
    """Показати конкретний дуель для голосування"""
    try:
        from database import get_db_session
        from database.models import Duel, Content, User
        
        with get_db_session() as session:
            duel = session.query(Duel).filter(Duel.id == duel_id).first()
            
            if not duel or not duel.opponent_id:
                await message.answer("❌ Дуель не знайдено або не активний")
                return
            
            # Отримати контент та учасників
            challenger_content = session.query(Content).filter(Content.id == duel.challenger_content_id).first()
            opponent_content = session.query(Content).filter(Content.id == duel.opponent_content_id).first()
            challenger = session.query(User).filter(User.id == duel.challenger_id).first()
            opponent = session.query(User).filter(User.id == duel.opponent_id).first()
            
            if not all([challenger_content, opponent_content, challenger, opponent]):
                await message.answer("❌ Помилка завантаження даних дуелі")
                return
            
            # Розрахувати час що залишився
            time_left = duel.ends_at - datetime.utcnow() if duel.ends_at else timedelta(minutes=5)
            time_left_str = f"{int(time_left.total_seconds() // 60)}хв {int(time_left.total_seconds() % 60)}с" if time_left.total_seconds() > 0 else "завершується"
            
            duel_text = (
                f"{EMOJI['vs']} <b>ДУЕЛЬ #{duel.id}</b>\n\n"
                f"{EMOJI['timer']} Залишилося: {time_left_str}\n\n"
                f"🔵 <b>{challenger.first_name or 'Невідомий'}</b> ({duel.challenger_votes} голосів)\n"
                f"<i>{challenger_content.text}</i>\n\n"
                f"🔴 <b>{opponent.first_name or 'Невідомий'}</b> ({duel.opponent_votes} голосів)\n"
                f"<i>{opponent_content.text}</i>\n\n"
                f"🗳️ Який жарт смішніший? Голосуйте!\n"
                f"💰 +2 бали за голос"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"🔵 За {challenger.first_name or 'Першого'} ({duel.challenger_votes})",
                        callback_data=f"vote_challenger_{duel.id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"🔴 За {opponent.first_name or 'Другого'} ({duel.opponent_votes})",
                        callback_data=f"vote_opponent_{duel.id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Результати",
                        callback_data=f"duel_results_{duel.id}"
                    ),
                    InlineKeyboardButton(
                        text="🔄 Оновити",
                        callback_data=f"refresh_duel_{duel.id}"
                    )
                ]
            ])
            
            await message.answer(duel_text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"❌ Помилка показу дуелі для голосування: {e}")
        await message.answer("❌ Помилка завантаження дуелі")

# ===== ОБРОБКА ГОЛОСІВ =====

async def process_vote(callback_query: CallbackQuery, vote_for: str, duel_id: int):
    """Обробити голос в дуелі"""
    user_id = callback_query.from_user.id
    
    try:
        from database import vote_in_duel, update_user_points
        
        # Записати голос
        success = await vote_in_duel(duel_id, user_id, vote_for)
        
        if success:
            # Нарахувати бали за голосування
            await update_user_points(user_id, 2, "голосування в дуелі")
            
            vote_text = "🔵 challenger" if vote_for == "challenger" else "🔴 opponent"
            await callback_query.answer(f"✅ Голос за {vote_text} зарахований! (+2 бали)")
            
            # Оновити дуель
            await show_duel_for_voting(callback_query.message, duel_id)
            
            # Перевірити чи дуель закінчився
            await check_duel_completion(callback_query.bot, duel_id)
            
        else:
            await callback_query.answer("⚠️ Ви вже голосували в цій дуелі!", show_alert=True)
            
    except Exception as e:
        logger.error(f"❌ Помилка голосування: {e}")
        await callback_query.answer("❌ Помилка голосування", show_alert=True)

async def check_duel_completion(bot, duel_id: int):
    """Перевірити чи дуель завершилася"""
    try:
        from database import get_db_session
        from database.models import Duel
        
        with get_db_session() as session:
            duel = session.query(Duel).filter(Duel.id == duel_id).first()
            
            if not duel or duel.status != 'ACTIVE':
                return
            
            # Перевірити умови завершення
            total_votes = duel.challenger_votes + duel.opponent_votes
            time_expired = duel.ends_at and datetime.utcnow() >= duel.ends_at
            
            if total_votes >= MIN_VOTES_FOR_DUEL * 2 or time_expired:
                await complete_duel(bot, duel)
                
    except Exception as e:
        logger.error(f"❌ Помилка перевірки завершення дуелі: {e}")

async def complete_duel(bot, duel):
    """Завершити дуель та визначити переможця"""
    try:
        from database import get_db_session, update_user_points, get_user_by_id
        from database.models import User
        
        with get_db_session() as session:
            # Визначити переможця
            if duel.challenger_votes > duel.opponent_votes:
                winner_id = duel.challenger_id
                loser_id = duel.opponent_id
            elif duel.opponent_votes > duel.challenger_votes:
                winner_id = duel.opponent_id
                loser_id = duel.challenger_id
            else:
                # Нічия
                winner_id = None
                loser_id = None
            
            # Оновити статус дуелі
            duel.status = 'COMPLETED'
            duel.completed_at = datetime.utcnow()
            duel.winner_id = winner_id
            
            session.commit()
            
            # Нарахувати бали та оновити статистику
            if winner_id:
                await update_user_points(winner_id, POINTS_FOR_DUEL_WIN, "перемога в дуелі")
                await update_user_points(loser_id, POINTS_FOR_DUEL_PARTICIPATION, "участь в дуелі")
                
                # Оновити статистику дуелів
                winner = session.query(User).filter(User.id == winner_id).first()
                loser = session.query(User).filter(User.id == loser_id).first()
                
                if winner:
                    winner.duels_won += 1
                if loser:
                    loser.duels_lost += 1
                
                session.commit()
                
                # Повідомити учасників
                await notify_duel_participants(bot, duel, winner_id, loser_id)
                
            else:
                # Нічия
                await update_user_points(duel.challenger_id, POINTS_FOR_DUEL_PARTICIPATION, "нічия в дуелі")
                await update_user_points(duel.opponent_id, POINTS_FOR_DUEL_PARTICIPATION, "нічия в дуелі")
                
                await notify_duel_draw(bot, duel)
            
            logger.info(f"🏁 Дуель #{duel.id} завершено. Переможець: {winner_id or 'нічия'}")
            
    except Exception as e:
        logger.error(f"❌ Помилка завершення дуелі: {e}")

async def notify_duel_participants(bot, duel, winner_id: int, loser_id: int):
    """Повідомити учасників про результат дуелі"""
    try:
        from database import get_user_by_id
        
        winner = await get_user_by_id(winner_id)
        loser = await get_user_by_id(loser_id)
        
        if winner:
            winner_text = (
                f"{EMOJI['winner']} <b>ПЕРЕМОГА В ДУЕЛІ!</b>\n\n"
                f"🎉 Вітаємо! Ви виграли дуель #{duel.id}!\n"
                f"🗳️ Голосів: {duel.challenger_votes if winner_id == duel.challenger_id else duel.opponent_votes}\n"
                f"💰 +{POINTS_FOR_DUEL_WIN} балів за перемогу!\n\n"
                f"🔥 Продовжуйте в тому ж дусі!"
            )
            
            await bot.send_message(winner_id, winner_text)
        
        if loser:
            loser_text = (
                f"😔 <b>Поразка в дуелі</b>\n\n"
                f"На жаль, ви програли дуель #{duel.id}.\n"
                f"🗳️ Голосів: {duel.challenger_votes if loser_id == duel.challenger_id else duel.opponent_votes}\n"
                f"💰 +{POINTS_FOR_DUEL_PARTICIPATION} балів за участь!\n\n"
                f"💪 Не засмучуйтесь! Створіть новий дуель!"
            )
            
            await bot.send_message(loser_id, loser_text)
        
    except Exception as e:
        logger.error(f"❌ Помилка повідомлення учасників: {e}")

# ===== CALLBACK ХЕНДЛЕРИ =====

async def callback_create_duel(callback_query: CallbackQuery):
    """Створити дуель"""
    await callback_query.message.answer(
        f"{EMOJI['fire']} <b>Створення дуелі</b>\n\n"
        f"Надішліть свій найкращий жарт для дуелі!\n\n"
        f"📋 Вимоги:\n"
        f"• Мінімум 10 символів\n"
        f"• Максимум 500 символів\n"
        f"• Смішно та оригінально\n\n"
        f"💡 Просто напишіть жарт в наступному повідомленні"
    )
    await callback_query.answer()

async def callback_random_duel(callback_query: CallbackQuery):
    """Випадковий дуель"""
    await join_random_duel(callback_query)

async def callback_show_active_duels(callback_query: CallbackQuery):
    """Показати активні дуелі"""
    await show_active_duels_for_voting(callback_query.message)
    await callback_query.answer()

async def callback_vote_challenger(callback_query: CallbackQuery):
    """Голос за challenger"""
    data_parts = callback_query.data.split('_')
    if len(data_parts) >= 3:
        duel_id = int(data_parts[2])
        await process_vote(callback_query, "challenger", duel_id)

async def callback_vote_opponent(callback_query: CallbackQuery):
    """Голос за opponent"""
    data_parts = callback_query.data.split('_')
    if len(data_parts) >= 3:
        duel_id = int(data_parts[2])
        await process_vote(callback_query, "opponent", duel_id)

async def callback_duel_main_menu(callback_query: CallbackQuery):
    """Повернутися до головного меню дуелів"""
    await show_duel_menu(callback_query.message)
    await callback_query.answer()

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_duel_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів дуелів"""
    
    # Команди
    dp.message.register(cmd_duel, Command("duel"))
    
    # Callback запити
    dp.callback_query.register(callback_create_duel, F.data == "create_duel")
    dp.callback_query.register(callback_random_duel, F.data == "random_duel")
    dp.callback_query.register(callback_show_active_duels, F.data == "show_active_duels")
    dp.callback_query.register(callback_duel_main_menu, F.data == "duel_main_menu")
    
    dp.callback_query.register(callback_vote_challenger, F.data.startswith("vote_challenger_"))
    dp.callback_query.register(callback_vote_opponent, F.data.startswith("vote_opponent_"))
    
    # Додати обробку голосування в дуелі через callback з content_handlers
    dp.callback_query.register(
        lambda cq: show_duel_for_voting(cq.message, int(cq.data.split('_')[2])),
        F.data.startswith("duel_with_")
    )
    
    logger.info("✅ Хендлери дуелів зареєстровано")