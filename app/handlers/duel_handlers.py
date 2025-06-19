#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери дуелей жартів 🧠😂🔥
"""

import logging
import asyncio
import random
from datetime import datetime, timedelta

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

# Fallback імпорти
try:
    from config.settings import Settings
    settings = Settings()
    
    if not hasattr(settings, 'DUEL_VOTING_TIME'):
        settings.DUEL_VOTING_TIME = 300  # 5 хвилин
    if not hasattr(settings, 'POINTS_FOR_DUEL_WIN'):
        settings.POINTS_FOR_DUEL_WIN = 15
    if not hasattr(settings, 'MIN_VOTES_FOR_DUEL'):
        settings.MIN_VOTES_FOR_DUEL = 3
    if not hasattr(settings, 'MAX_JOKE_LENGTH'):
        settings.MAX_JOKE_LENGTH = 1000
        
except ImportError:
    import os
    class FallbackSettings:
        DUEL_VOTING_TIME = int(os.getenv("DUEL_VOTING_TIME", "300"))
        POINTS_FOR_DUEL_WIN = int(os.getenv("POINTS_FOR_DUEL_WIN", "15"))
        MIN_VOTES_FOR_DUEL = int(os.getenv("MIN_VOTES_FOR_DUEL", "3"))
        MAX_JOKE_LENGTH = int(os.getenv("MAX_JOKE_LENGTH", "1000"))
    settings = FallbackSettings()

# EMOJI константи
EMOJI = {
    "vs": "⚔️", "fire": "🔥", "brain": "🧠", "laugh": "😂",
    "trophy": "🏆", "star": "⭐", "thinking": "🤔", 
    "time": "⏰", "check": "✅", "cross": "❌",
    "stats": "📊", "profile": "👤", "party": "🎉"
}

# FSM для дуелей
class DuelStates(StatesGroup):
    waiting_for_joke = State()

# Прості моделі для дуелей (fallback)
class Duel:
    def __init__(self, id, initiator_id, opponent_id=None):
        self.id = id
        self.initiator_id = initiator_id
        self.opponent_id = opponent_id
        self.initiator_joke = ""
        self.opponent_joke = ""
        self.initiator_votes = 0
        self.opponent_votes = 0
        self.total_votes = 0
        self.voting_ends_at = datetime.now() + timedelta(seconds=settings.DUEL_VOTING_TIME)
        self.voters = set()  # ID користувачів, які проголосували
        self.status = "active"
        self.winner_id = None

# Тимчасове сховище дуелей
ACTIVE_DUELS = {}
DUEL_COUNTER = 1

# Зразки жартів для опонентів
OPPONENT_JOKES = [
    "Чому програмісти не можуть знайти кохання? Бо вони завжди шукають ідеальний матч!",
    "Що робить програміст коли холодно? Відкриває Java!",
    "Чому програмісти люблять темну тему? Бо світло приваблює баги!",
    "Як програміст рахує вівці? 1 овця, 2 овці, 3 овці... stack overflow!",
    "Чому у програмістів немає дітей? Бо вони не можуть зробити коміт без конфліктів!"
]

async def get_random_joke_for_duel():
    """Отримання випадкового жарту для дуелі"""
    try:
        # Спроба отримання з БД
        from handlers.content_handlers import get_random_joke
        joke = await get_random_joke()
        if joke:
            return joke.text
    except ImportError:
        pass
    
    # Fallback
    return random.choice(OPPONENT_JOKES)

async def update_user_points(user_id: int, points: int, reason: str):
    """Нарахування балів користувачу"""
    try:
        from database.database import update_user_points as db_update_points
        await db_update_points(user_id, points, reason)
    except ImportError:
        logger.info(f"👤 Користувач {user_id}: +{points} балів за {reason}")

# ===== КОМАНДИ ДУЕЛЕЙ =====

async def cmd_duel(message: Message, state: FSMContext):
    """Команда /duel - почати дуель жартів"""
    user_id = message.from_user.id
    
    # Перевірка чи не має користувач активної дуелі
    for duel in ACTIVE_DUELS.values():
        if duel.initiator_id == user_id and duel.status == "active":
            await show_active_duel(message, duel)
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
                text=f"{EMOJI['stats']} Моя статистика", 
                callback_data="show_profile"
            )
        ]
    ])
    
    await message.answer(
        f"{EMOJI['vs']} <b>ДУЕЛЬ ЖАРТІВ!</b>\n\n"
        f"{EMOJI['fire']} Обери варіант дуелі:\n\n"
        f"{EMOJI['brain']} <b>З моїм жартом</b> - надішли свій анекдот\n"
        f"{EMOJI['laugh']} <b>З випадковим</b> - використай жарт з бази\n\n"
        f"{EMOJI['trophy']} <b>Переможець отримує +{settings.POINTS_FOR_DUEL_WIN} балів!</b>\n"
        f"{EMOJI['time']} <b>Голосування триває {settings.DUEL_VOTING_TIME // 60} хвилин</b>",
        reply_markup=keyboard
    )

async def show_active_duel(message: Message, duel: Duel):
    """Показ активної дуелі користувача"""
    time_left = (duel.voting_ends_at - datetime.now()).total_seconds()
    time_left_minutes = max(0, int(time_left // 60))
    
    duel_text = (
        f"{EMOJI['vs']} <b>ТВОЯ АКТИВНА ДУЕЛЬ #{duel.id}</b>\n\n"
        f"{EMOJI['fire']} <b>Жарт А</b> (твій):\n"
        f"{duel.initiator_joke}\n\n"
        f"{EMOJI['brain']} <b>Жарт Б</b> (опонент):\n"
        f"{duel.opponent_joke}\n\n"
        f"{EMOJI['fire']} Голосів за А: {duel.initiator_votes}\n"
        f"{EMOJI['brain']} Голосів за Б: {duel.opponent_votes}\n"
        f"{EMOJI['time']} Залишилось: {time_left_minutes} хвилин"
    )
    
    if time_left <= 0:
        # Дуель завершена
        winner = determine_winner(duel)
        duel_text += f"\n\n{EMOJI['trophy']} <b>Результат:</b> {winner}"
    else:
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
        
        await message.answer(duel_text, reply_markup=keyboard)
        return
    
    await message.answer(duel_text)

async def create_duel_with_joke(user_id: int, user_joke: str, bot) -> Duel:
    """Створення дуелі з жартом користувача"""
    global DUEL_COUNTER
    
    # Отримання жарту опонента
    opponent_joke = await get_random_joke_for_duel()
    
    # Створення дуелі
    duel = Duel(DUEL_COUNTER, user_id)
    duel.initiator_joke = user_joke
    duel.opponent_joke = opponent_joke
    
    ACTIVE_DUELS[DUEL_COUNTER] = duel
    DUEL_COUNTER += 1
    
    logger.info(f"🔥 Створено дуель {duel.id} від користувача {user_id}")
    return duel

async def start_duel_voting(duel: Duel, bot, initiator_message: Message):
    """Початок голосування в дуелі"""
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
        f"{EMOJI['fire']} <b>Жарт А:</b>\n"
        f"{duel.initiator_joke}\n\n"
        f"{EMOJI['brain']} <b>Жарт Б:</b>\n"
        f"{duel.opponent_joke}\n\n"
        f"{EMOJI['time']} <b>Голосування закінчується через {settings.DUEL_VOTING_TIME // 60} хвилин</b>\n"
        f"{EMOJI['trophy']} Переможець отримає +{settings.POINTS_FOR_DUEL_WIN} балів!\n"
        f"{EMOJI['star']} Кожен голос: +2 бали учаснику"
    )
    
    # Надсилання повідомлення ініціатору
    await initiator_message.answer(
        f"{EMOJI['vs']} <b>Твоя дуель почалася!</b>\n\n{duel_text}",
        reply_markup=keyboard
    )
    
    # Планування автоматичного завершення
    asyncio.create_task(auto_finish_duel(duel.id, bot))

async def auto_finish_duel(duel_id: int, bot):
    """Автоматичне завершення дуелі по таймауту"""
    await asyncio.sleep(settings.DUEL_VOTING_TIME)
    
    if duel_id in ACTIVE_DUELS:
        duel = ACTIVE_DUELS[duel_id]
        if duel.status == "active":
            await finish_duel(duel_id, bot)

async def vote_in_duel(duel_id: int, voter_id: int, vote_for: str) -> dict:
    """Голосування в дуелі"""
    if duel_id not in ACTIVE_DUELS:
        return {"success": False, "message": "Дуель не знайдена"}
    
    duel = ACTIVE_DUELS[duel_id]
    
    # Перевірка часу голосування
    if datetime.now() > duel.voting_ends_at:
        return {"success": False, "message": "Час голосування вичерпано"}
    
    # Перевірка чи не голосував вже
    if voter_id in duel.voters:
        return {"success": False, "message": "Ти вже голосував у цій дуелі"}
    
    # Перевірка чи не учасник дуелі
    if voter_id == duel.initiator_id:
        return {"success": False, "message": "Ініціатор дуелі не може голосувати"}
    
    # Додавання голосу
    duel.voters.add(voter_id)
    
    if vote_for == "initiator":
        duel.initiator_votes += 1
    else:
        duel.opponent_votes += 1
    
    duel.total_votes += 1
    
    # Нарахування балів за голосування
    await update_user_points(voter_id, 2, "голосування в дуелі")
    
    return {
        "success": True,
        "message": f"Голос зараховано! +2 бали",
        "initiator_votes": duel.initiator_votes,
        "opponent_votes": duel.opponent_votes
    }

def determine_winner(duel: Duel) -> str:
    """Визначення переможця дуелі"""
    if duel.initiator_votes > duel.opponent_votes:
        return "Жарт А переміг!"
    elif duel.opponent_votes > duel.initiator_votes:
        return "Жарт Б переміг!"
    else:
        return "Нічия!"

async def finish_duel(duel_id: int, bot):
    """Завершення дуелі та підбиття підсумків"""
    if duel_id not in ACTIVE_DUELS:
        return
    
    duel = ACTIVE_DUELS[duel_id]
    duel.status = "completed"
    
    # Визначення переможця
    winner_text = determine_winner(duel)
    
    # Нарахування балів переможцю
    if duel.initiator_votes > duel.opponent_votes:
        duel.winner_id = duel.initiator_id
        await update_user_points(duel.initiator_id, settings.POINTS_FOR_DUEL_WIN, "перемога в дуелі")
        
        # Повідомлення переможцю
        try:
            await bot.send_message(
                duel.initiator_id,
                f"{EMOJI['trophy']} <b>ПЕРЕМОГА В ДУЕЛІ #{duel.id}!</b>\n\n"
                f"{EMOJI['fire']} Твій жарт переміг!\n"
                f"{EMOJI['stats']} Результат: {duel.initiator_votes} vs {duel.opponent_votes}\n"
                f"{EMOJI['star']} +{settings.POINTS_FOR_DUEL_WIN} балів до твоєї скарбнички!"
            )
        except:
            pass
    
    logger.info(f"🏆 Дуель {duel_id} завершена. {winner_text}")

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
    random_joke = await get_random_joke_for_duel()
    
    try:
        # Створення дуелі
        duel = await create_duel_with_joke(user_id, random_joke, callback_query.bot)
        
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
            f"{EMOJI['cross']} Жарт занадто довгий!\n"
            f"Максимум {settings.MAX_JOKE_LENGTH} символів."
        )
        return
    
    try:
        # Створення дуелі
        duel = await create_duel_with_joke(user_id, joke_text, message.bot)
        
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
            pass
    
    await callback_query.answer(result["message"])

async def callback_duel_results(callback_query: CallbackQuery):
    """Показ результатів дуелі"""
    duel_id = int(callback_query.data.split(':')[1])
    
    if duel_id not in ACTIVE_DUELS:
        await callback_query.answer("❌ Дуель не знайдена")
        return
    
    duel = ACTIVE_DUELS[duel_id]
    
    results_text = (
        f"{EMOJI['stats']} <b>РЕЗУЛЬТАТИ ДУЕЛІ #{duel_id}</b>\n\n"
        f"{EMOJI['fire']} <b>Жарт А:</b> {duel.initiator_votes} голосів\n"
        f"{EMOJI['brain']} <b>Жарт Б:</b> {duel.opponent_votes} голосів\n"
        f"{EMOJI['vs']} <b>Всього голосів:</b> {duel.total_votes}\n\n"
    )
    
    if duel.status == "completed":
        results_text += f"{EMOJI['trophy']} <b>Результат:</b> {determine_winner(duel)}"
    else:
        time_left = (duel.voting_ends_at - datetime.now()).total_seconds()
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
    
    logger.info("✅ Duel handlers зареєстровані")