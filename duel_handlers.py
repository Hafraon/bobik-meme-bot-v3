#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери дуелей жартів 🧠😂🔥
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.settings import EMOJI, settings
from database.database import get_db_session, update_user_points, get_random_joke
from database.models import (
    User, Duel, DuelVote, Content, DuelStatus, ContentType, ContentStatus
)

logger = logging.getLogger(__name__)

# FSM для дуелей
class DuelStates(StatesGroup):
    waiting_for_joke = State()

async def cmd_duel(message: Message, state: FSMContext):
    """Команда /duel - почати дуель жартів"""
    user_id = message.from_user.id
    
    # Перевірка чи не має користувач активної дуелі
    with get_db_session() as session:
        active_duel = session.query(Duel).filter(
            (Duel.initiator_id == user_id) | (Duel.opponent_id == user_id),
            Duel.status == DuelStatus.ACTIVE
        ).first()
        
        if active_duel:
            # Показати поточну дуель
            await show_active_duel(message, active_duel)
            return
    
    # Клавіатура вибору типу дуелі
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['brain']} Дуель з моїм жартом",
                callback_data="duel_with_my_joke"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI['fire']} Дуель з випадковим жартом",
                callback_data="duel_with_random_joke"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI['thinking']} Як працює дуель?",
                callback_data="duel_info"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['stats']} Історія дуелей",
                callback_data="duel_history"
            )
        ]
    ])
    
    await message.answer(
        f"{EMOJI['vs']} <b>ДУЕЛЬ ЖАРТІВ!</b>\n\n"
        f"{EMOJI['fire']} Обери варіант дуелі:\n\n"
        f"{EMOJI['brain']} <b>З моїм жартом</b> - надішли свій анекдот\n"
        f"{EMOJI['laugh']} <b>З випадковим</b> - використай жарт з бази\n\n"
        f"{EMOJI['trophy']} <b>Переможець отримує +{settings.POINTS_FOR_DUEL_WIN} балів!</b>\n"
        f"{EMOJI['vs']} <b>Голосування триває {settings.DUEL_VOTING_TIME // 60} хвилин</b>",
        reply_markup=keyboard
    )

async def show_active_duel(message: Message, duel: Duel):
    """Показ активної дуелі користувача"""
    with get_db_session() as session:
        initiator_content = session.query(Content).filter(Content.id == duel.initiator_content_id).first()
        opponent_content = session.query(Content).filter(Content.id == duel.opponent_content_id).first()
        
        initiator = session.query(User).filter(User.id == duel.initiator_id).first()
        opponent = session.query(User).filter(User.id == duel.opponent_id).first() if duel.opponent_id else None
        
        time_left = (duel.voting_ends_at - datetime.utcnow()).total_seconds()
        time_left_minutes = max(0, int(time_left // 60))
        
        duel_text = (
            f"{EMOJI['vs']} <b>ТВОЯ АКТИВНА ДУЕЛЬ #{duel.id}</b>\n\n"
            f"{EMOJI['fire']} <b>Жарт А</b> від {initiator.first_name if initiator else 'Невідомий'}:\n"
            f"{initiator_content.text if initiator_content else 'Контент не знайдено'}\n\n"
            f"{EMOJI['brain']} <b>Жарт Б</b> від {opponent.first_name if opponent else 'Бот'}:\n"
            f"{opponent_content.text if opponent_content else 'Контент не знайдено'}\n\n"
            f"{EMOJI['fire']} Голосів за А: {duel.initiator_votes}\n"
            f"{EMOJI['brain']} Голосів за Б: {duel.opponent_votes}\n"
            f"{EMOJI['time']} Залишилось: {time_left_minutes} хвилин"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['fire']} Жарт А ({duel.initiator_votes})",
                    callback_data=f"vote_duel:{duel.id}:initiator"
                ),
                InlineKeyboardButton(
                    text=f"{EMOJI['brain']} Жарт Б ({duel.opponent_votes})",
                    callback_data=f"vote_duel:{duel.id}:opponent"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['stats']} Оновити результати",
                    callback_data=f"duel_results:{duel.id}"
                )
            ]
        ])
        
        await message.answer(duel_text, reply_markup=keyboard)

async def create_duel_with_content(user_id: int, content: Content, bot) -> Duel:
    """Створення дуелі з контентом"""
    with get_db_session() as session:
        # Знаходження контенту опонента (випадковий анекдот)
        opponent_content = await get_random_joke()
        
        if not opponent_content:
            raise Exception("Не знайдено контенту для дуелі")
        
        # Створення дуелі
        duel = Duel(
            initiator_id=user_id,
            initiator_content_id=content.id,
            opponent_content_id=opponent_content.id,
            opponent_id=opponent_content.author_id,
            voting_ends_at=datetime.utcnow() + timedelta(seconds=settings.DUEL_VOTING_TIME),
            status=DuelStatus.ACTIVE
        )
        session.add(duel)
        session.commit()
        
        logger.info(f"🔥 Створено дуель {duel.id} від користувача {user_id}")
        return duel

async def start_duel_voting(duel: Duel, bot, initiator_message: Message):
    """Початок голосування в дуелі з розсилкою іншим користувачам"""
    with get_db_session() as session:
        # Отримання контенту
        initiator_content = session.query(Content).filter(Content.id == duel.initiator_content_id).first()
        opponent_content = session.query(Content).filter(Content.id == duel.opponent_content_id).first()
        
        # Отримання користувачів
        initiator = session.query(User).filter(User.id == duel.initiator_id).first()
        opponent = session.query(User).filter(User.id == duel.opponent_id).first()
        
        if not (initiator_content and opponent_content):
            logger.error(f"Не знайдено контент для дуелі {duel.id}")
            return
        
        # Клавіатура голосування
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['fire']} Жарт А ({duel.initiator_votes})",
                    callback_data=f"vote_duel:{duel.id}:initiator"
                ),
                InlineKeyboardButton(
                    text=f"{EMOJI['brain']} Жарт Б ({duel.opponent_votes})",
                    callback_data=f"vote_duel:{duel.id}:opponent"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['stats']} Результати",
                    callback_data=f"duel_results:{duel.id}"
                )
            ]
        ])
        
        duel_text = (
            f"{EMOJI['vs']} <b>ДУЕЛЬ ЖАРТІВ #{duel.id}</b>\n\n"
            f"{EMOJI['fire']} <b>Жарт А</b> від {initiator.first_name or 'Невідомий'}:\n"
            f"{initiator_content.text}\n\n"
            f"{EMOJI['brain']} <b>Жарт Б</b> від {opponent.first_name or 'Бот'}:\n"
            f"{opponent_content.text}\n\n"
            f"{EMOJI['time']} <b>Голосування закінчується через {settings.DUEL_VOTING_TIME // 60} хвилин</b>\n"
            f"{EMOJI['trophy']} Переможець отримає +{settings.POINTS_FOR_DUEL_WIN} балів!\n"
            f"{EMOJI['like']} Кожен голос: +2 бали учаснику"
        )
        
        # Надсилання повідомлення ініціатору
        try:
            await initiator_message.answer(
                f"{EMOJI['vs']} <b>Твоя дуель почалася!</b>\n\n{duel_text}",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Не вдалося повідомити ініціатора: {e}")
        
        # Розсилка активним користувачам (останні 24 години)
        active_users = session.query(User).filter(
            User.last_active >= datetime.utcnow() - timedelta(days=1),
            User.id != duel.initiator_id,
            User.id != duel.opponent_id
        ).limit(20).all()  # Обмежуємо кількість для уникнення спаму
        
        notification_count = 0
        for user in active_users:
            try:
                await bot.send_message(
                    user.id,
                    f"{EMOJI['vs']} <b>Нова дуель жартів!</b>\n\n{duel_text}",
                    reply_markup=keyboard
                )
                notification_count += 1
                await asyncio.sleep(0.1)  # Пауза для уникнення rate limit
            except Exception as e:
                logger.debug(f"Не вдалося повідомити користувача {user.id}: {e}")
                continue
        
        logger.info(f"📢 Дуель {duel.id} розіслано {notification_count} користувачам")

async def vote_in_duel(duel_id: int, voter_id: int, vote_for: str) -> dict:
    """Голосування в дуелі з нарахуванням балів"""
    with get_db_session() as session:
        # Перевірка чи існує дуель
        duel = session.query(Duel).filter(
            Duel.id == duel_id,
            Duel.status == DuelStatus.ACTIVE
        ).first()
        
        if not duel:
            return {"success": False, "message": "Дуель не знайдена або завершена"}
        
        # Перевірка часу голосування
        if datetime.utcnow() > duel.voting_ends_at:
            # Автоматично завершити дуель
            await finish_duel(duel_id)
            return {"success": False, "message": "Час голосування вичерпано"}
        
        # Перевірка чи не голосував вже
        existing_vote = session.query(DuelVote).filter(
            DuelVote.duel_id == duel_id,
            DuelVote.voter_id == voter_id
        ).first()
        
        if existing_vote:
            return {"success": False, "message": "Ти вже голосував у цій дуелі"}
        
        # Перевірка чи не учасник дуелі
        if voter_id in [duel.initiator_id, duel.opponent_id]:
            return {"success": False, "message": "Учасники дуелі не можуть голосувати"}
        
        # Додавання голосу
        vote = DuelVote(
            duel_id=duel_id,
            voter_id=voter_id,
            vote_for=vote_for
        )
        session.add(vote)
        
        # Оновлення лічильників
        if vote_for == "initiator":
            duel.initiator_votes += 1
        else:
            duel.opponent_votes += 1
        
        duel.total_votes += 1
        session.commit()
        
        # Нарахування балів за голосування
        await update_user_points(voter_id, 2, "голосування в дуелі")
        
        return {
            "success": True,
            "message": f"Голос зараховано! +2 бали",
            "initiator_votes": duel.initiator_votes,
            "opponent_votes": duel.opponent_votes
        }

async def finish_duel(duel_id: int):
    """Завершення дуелі та підбиття підсумків"""
    with get_db_session() as session:
        duel = session.query(Duel).filter(Duel.id == duel_id).first()
        
        if not duel or duel.status != DuelStatus.ACTIVE:
            return None
        
        # Визначення переможця
        if duel.initiator_votes > duel.opponent_votes:
            winner_id = duel.initiator_id
            winner_name = "Ініціатор"
        elif duel.opponent_votes > duel.initiator_votes:
            winner_id = duel.opponent_id if duel.opponent_id else None
            winner_name = "Опонент"
        else:
            winner_id = None
            winner_name = "Нічия"
        
        # Оновлення дуелі
        duel.status = DuelStatus.COMPLETED
        duel.winner_id = winner_id
        duel.completed_at = datetime.utcnow()
        
        # Оновлення статистики учасників
        initiator = session.query(User).filter(User.id == duel.initiator_id).first()
        if initiator:
            if winner_id == duel.initiator_id:
                initiator.duels_won += 1
                await update_user_points(duel.initiator_id, settings.POINTS_FOR_DUEL_WIN, "перемога в дуелі")
            else:
                initiator.duels_lost += 1
        
        if duel.opponent_id:
            opponent = session.query(User).filter(User.id == duel.opponent_id).first()
            if opponent:
                if winner_id == duel.opponent_id:
                    opponent.duels_won += 1
                    await update_user_points(duel.opponent_id, settings.POINTS_FOR_DUEL_WIN, "перемога в дуелі")
                else:
                    opponent.duels_lost += 1
        
        session.commit()
        
        logger.info(f"🏆 Дуель {duel_id} завершена. Переможець: {winner_name}")
        
        return {
            "winner_id": winner_id,
            "winner_name": winner_name,
            "initiator_votes": duel.initiator_votes,
            "opponent_votes": duel.opponent_votes,
            "total_votes": duel.total_votes
        }

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_duel_info(callback_query: CallbackQuery):
    """Інформація про дуелі"""
    info_text = (
        f"{EMOJI['vs']} <b>ЯК ПРАЦЮЮТЬ ДУЕЛІ:</b>\n\n"
        f"{EMOJI['fire']} <b>1. Створення дуелі</b>\n"
        f"• Обери свій жарт або випадковий\n"
        f"• Система знайде опонента з бази\n\n"
        f"{EMOJI['brain']} <b>2. Голосування</b>\n"
        f"• Тривалість: {settings.DUEL_VOTING_TIME // 60} хвилин\n"
        f"• Голосують інші користувачі\n"
        f"• Учасники дуелі не голосують\n\n"
        f"{EMOJI['trophy']} <b>3. Нагороди</b>\n"
        f"• Переможець: +{settings.POINTS_FOR_DUEL_WIN} балів\n"
        f"• Кожен голос: +2 бали\n"
        f"• Мінімум {settings.MIN_VOTES_FOR_DUEL} голосів для дійсності\n\n"
        f"{EMOJI['star']} <b>Готовий до батлу?</b>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['fire']} Почати дуель!",
                callback_data="start_new_duel"
            )
        ]
    ])
    
    await callback_query.message.edit_text(info_text, reply_markup=keyboard)
    await callback_query.answer()

async def callback_duel_with_my_joke(callback_query: CallbackQuery, state: FSMContext):
    """Дуель з власним жартом"""
    await callback_query.message.edit_text(
        f"{EMOJI['brain']} <b>Надішли свій анекдот для дуелі!</b>\n\n"
        f"{EMOJI['fire']} Напиши найсмішніший жарт\n"
        f"{EMOJI['star']} Максимум {settings.MAX_JOKE_LENGTH} символів\n"
        f"{EMOJI['time']} Час на відповідь: 2 хвилини\n\n"
        f"{EMOJI['thinking']} <b>Приклад:</b>\n"
        f"Чому програмісти п'ють каву? Бо без неї код не компілюється!"
    )
    
    await state.set_state(DuelStates.waiting_for_joke)
    await callback_query.answer()

async def callback_duel_with_random_joke(callback_query: CallbackQuery):
    """Дуель з випадковим жартом"""
    user_id = callback_query.from_user.id
    
    # Отримання випадкового анекдоту
    random_joke = await get_random_joke()
    
    if not random_joke:
        await callback_query.message.edit_text(
            f"{EMOJI['cross']} <b>Не знайдено жартів для дуелі!</b>\n\n"
            f"{EMOJI['thinking']} База контенту порожня. Спробуй пізніше!"
        )
        await callback_query.answer()
        return
    
    try:
        # Створення дуелі
        duel = await create_duel_with_content(user_id, random_joke, callback_query.bot)
        
        # Початок голосування
        await start_duel_voting(duel, callback_query.bot, callback_query.message)
        
        await callback_query.answer(f"{EMOJI['check']} Дуель створена!")
        
    except Exception as e:
        logger.error(f"Помилка створення дуелі: {e}")
        await callback_query.message.edit_text(
            f"{EMOJI['cross']} <b>Помилка створення дуелі!</b>\n\n"
            f"{EMOJI['thinking']} Спробуй пізніше"
        )
        await callback_query.answer()

async def handle_duel_joke_submission(message: Message, state: FSMContext):
    """Обробка жарту для дуелі"""
    user_id = message.from_user.id
    joke_text = message.text.strip()
    
    if len(joke_text) > settings.MAX_JOKE_LENGTH:
        await message.answer(
            f"{EMOJI['warning']} Жарт занадто довгий!\n"
            f"Максимум {settings.MAX_JOKE_LENGTH} символів."
        )
        return
    
    # Створення тимчасового контенту для дуелі
    with get_db_session() as session:
        temp_content = Content(
            content_type=ContentType.JOKE,
            text=joke_text,
            author_id=user_id,
            status=ContentStatus.APPROVED  # Для дуелі одразу схвалюємо
        )
        session.add(temp_content)
        session.commit()
        
        content_id = temp_content.id
    
    try:
        # Створення дуелі
        duel = await create_duel_with_content(user_id, temp_content, message.bot)
        
        # Початок голосування
        await start_duel_voting(duel, message.bot, message)
        
        await message.answer(
            f"{EMOJI['check']} <b>Дуель створена!</b>\n\n"
            f"{EMOJI['fire']} Твій жарт:\n{joke_text}\n\n"
            f"{EMOJI['vs']} Початок батлу!\n"
            f"{EMOJI['time']} Голосування триває {settings.DUEL_VOTING_TIME // 60} хвилин"
        )
        
    except Exception as e:
        logger.error(f"Помилка створення дуелі: {e}")
        await message.answer(
            f"{EMOJI['cross']} <b>Не вдалося створити дуель!</b>\n\n"
            f"{EMOJI['thinking']} Спробуй пізніше"
        )
    
    await state.clear()

async def callback_vote_duel(callback_query: CallbackQuery):
    """Голосування в дуелі"""
    data_parts = callback_query.data.split(':')
    duel_id = int(data_parts[1])
    vote_for = data_parts[2]
    
    result = await vote_in_duel(duel_id, callback_query.from_user.id, vote_for)
    
    if result["success"]:
        # Оновлення клавіатури з новими результатами
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['fire']} Жарт А ({result['initiator_votes']})",
                    callback_data=f"vote_duel:{duel_id}:initiator"
                ),
                InlineKeyboardButton(
                    text=f"{EMOJI['brain']} Жарт Б ({result['opponent_votes']})",
                    callback_data=f"vote_duel:{duel_id}:opponent"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['stats']} Результати",
                    callback_data=f"duel_results:{duel_id}"
                )
            ]
        ])
        
        try:
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        except:
            pass  # Ігноруємо помилки оновлення клавіатури
    
    await callback_query.answer(result["message"])

async def callback_duel_results(callback_query: CallbackQuery):
    """Показ результатів дуелі"""
    duel_id = int(callback_query.data.split(':')[1])
    
    with get_db_session() as session:
        duel = session.query(Duel).filter(Duel.id == duel_id).first()
        
        if not duel:
            await callback_query.answer("❌ Дуель не знайдена")
            return
        
        results_text = (
            f"{EMOJI['stats']} <b>РЕЗУЛЬТАТИ ДУЕЛІ #{duel_id}</b>\n\n"
            f"{EMOJI['fire']} <b>Жарт А:</b> {duel.initiator_votes} голосів\n"
            f"{EMOJI['brain']} <b>Жарт Б:</b> {duel.opponent_votes} голосів\n"
            f"{EMOJI['vs']} <b>Всього голосів:</b> {duel.total_votes}\n\n"
        )
        
        if duel.status == DuelStatus.COMPLETED:
            if duel.winner_id == duel.initiator_id:
                results_text += f"{EMOJI['trophy']} <b>Переможець:</b> Жарт А!"
            elif duel.winner_id == duel.opponent_id:
                results_text += f"{EMOJI['trophy']} <b>Переможець:</b> Жарт Б!"
            else:
                results_text += f"{EMOJI['thinking']} <b>Результат:</b> Нічия!"
        else:
            time_left = (duel.voting_ends_at - datetime.utcnow()).total_seconds()
            if time_left > 0:
                results_text += f"{EMOJI['time']} <b>Залишилось:</b> {int(time_left // 60)} хв {int(time_left % 60)} сек"
            else:
                results_text += f"{EMOJI['time']} <b>Голосування завершене</b>"
    
    await callback_query.answer(results_text, show_alert=True)

async def callback_start_new_duel(callback_query: CallbackQuery):
    """Callback для початку нової дуелі"""
    await callback_query.message.answer(
        f"{EMOJI['vs']} <b>Створюємо нову дуель!</b>\n\n"
        f"Використай команду /duel для початку"
    )
    await callback_query.answer()

def register_duel_handlers(dp: Dispatcher):
    """Реєстрація хендлерів дуелей"""
    
    # Команди
    dp.message.register(cmd_duel, Command("duel"))
    
    # FSM хендлери
    dp.message.register(handle_duel_joke_submission, DuelStates.waiting_for_joke)
    
    # Callback запити
    dp.callback_query.register(callback_duel_info, F.data == "duel_info")
    dp.callback_query.register(callback_duel_with_my_joke, F.data == "duel_with_my_joke")
    dp.callback_query.register(callback_duel_with_random_joke, F.data == "duel_with_random_joke")
    dp.callback_query.register(callback_vote_duel, F.data.startswith("vote_duel:"))
    dp.callback_query.register(callback_duel_results, F.data.startswith("duel_results:"))
    dp.callback_query.register(callback_start_new_duel, F.data == "start_new_duel")