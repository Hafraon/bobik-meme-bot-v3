#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚔️ СИСТЕМА ДУЕЛІВ ЖАРТІВ - Хендлери ⚔️

Повноцінна система дуелів з голосуванням користувачів:
- Створення нових дуелів
- Голосування за кращий жарт
- Автоматичне визначення переможця
- Нарахування балів та досягнень
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Імпорти проекту
from config.settings import settings
from database.services import (
    get_or_create_user, update_user_points, get_user_by_id,
    create_duel, get_active_duels, get_duel_by_id, vote_in_duel,
    finish_duel, get_user_duel_stats, get_random_approved_content
)
from database.models import DuelStatus, ContentType

logger = logging.getLogger(__name__)

# ===== FSM СТАНИ ДЛЯ ДУЕЛІВ =====

class DuelStates(StatesGroup):
    waiting_for_opponent = State()
    waiting_for_content_choice = State()
    waiting_for_custom_content = State()

# ===== КОНСТАНТИ =====

DUEL_EMOJI = {
    'sword': '⚔️',
    'vs': '🆚', 
    'crown': '👑',
    'fire': '🔥',
    'trophy': '🏆',
    'timer': '⏱️',
    'vote_up': '👍',
    'vote_down': '👎',
    'laugh': '😂',
    'clap': '👏',
    'lightning': '⚡',
    'star': '⭐',
    'boom': '💥',
    'target': '🎯'
}

DUEL_TEXTS = {
    'welcome': f"{DUEL_EMOJI['sword']} <b>АРЕНА ДУЕЛІВ ЖАРТІВ!</b> {DUEL_EMOJI['sword']}\n\nТут найкращі жартуни змагаються за звання короля гумору!",
    'no_content': f"{DUEL_EMOJI['timer']} Недостатньо схваленого контенту для дуелі. Спробуйте пізніше!",
    'duel_created': f"{DUEL_EMOJI['fire']} <b>ДУЕЛЬ РОЗПОЧАТО!</b>\n\nГолосуйте за найсмішніший жарт!",
    'vote_registered': f"{DUEL_EMOJI['clap']} Ваш голос зараховано!",
    'already_voted': f"{DUEL_EMOJI['timer']} Ви вже голосували в цій дуелі!",
    'duel_finished': f"{DUEL_EMOJI['crown']} <b>ДУЕЛЬ ЗАВЕРШЕНО!</b>",
    'no_active_duels': f"{DUEL_EMOJI['target']} Наразі немає активних дуелів. Створіть новий!",
    'voting_time_up': f"{DUEL_EMOJI['timer']} Час голосування вичерпано!",
    'minimum_votes': "Для завершення потрібно мінімум 3 голоси",
}

RANK_REWARDS = {
    'duel_win': 25,      # За перемогу в дуелі
    'duel_participate': 10,  # За участь
    'vote_in_duel': 2,   # За голосування
    'epic_victory': 50,  # За розгромну перемогу (70%+ голосів)
    'streak_bonus': 15   # Бонус за серію перемог
}

# ===== ОСНОВНІ КОМАНДИ ДУЕЛІВ =====

async def cmd_duel(message: Message):
    """Головна команда /duel - показ меню дуелів"""
    try:
        user_id = message.from_user.id
        await get_or_create_user(user_id, message.from_user.username, message.from_user.full_name)
        
        # Отримуємо статистику користувача
        stats = await get_user_duel_stats(user_id)
        
        # Перевіряємо активні дуелі
        active_duels = await get_active_duels(limit=3)
        
        text = f"{DUEL_TEXTS['welcome']}\n\n"
        
        # Персональна статистика
        if stats:
            wins = stats.get('wins', 0)
            total = stats.get('total_duels', 0)
            win_rate = (wins / total * 100) if total > 0 else 0
            
            text += f"📊 <b>Ваша статистика:</b>\n"
            text += f"🏆 Перемоги: {wins}/{total} ({win_rate:.1f}%)\n"
            text += f"⭐ Рейтинг: {stats.get('rating', 1000)}\n\n"
        
        # Активні дуелі
        if active_duels:
            text += f"🔥 <b>Активні дуелі ({len(active_duels)}):</b>\n"
            for duel in active_duels[:2]:  # Показуємо топ 2
                votes_total = duel.get('challenger_votes', 0) + duel.get('opponent_votes', 0)
                text += f"• Дуель #{duel['id']} ({votes_total} голосів)\n"
            text += "\n"
        else:
            text += f"{DUEL_TEXTS['no_active_duels']}\n\n"
        
        # Меню кнопок
        keyboard = create_duel_main_keyboard(bool(active_duels))
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in duel command: {e}")
        await message.answer(f"❌ Помилка завантаження дуелів. Спробуйте пізніше.")

async def cmd_create_duel(message: Message):
    """Команда створення нової дуелі"""
    try:
        user_id = message.from_user.id
        
        # Перевіряємо чи користувач не має активних дуелів
        user_active_duels = await get_user_active_duels(user_id)
        if user_active_duels:
            await message.answer(
                f"⚠️ У вас вже є активна дуель #{user_active_duels[0]['id']}!\n"
                f"Дочекайтеся її завершення або використайте /duels для перегляду."
            )
            return
        
        # Створюємо нову дуель
        duel = await create_random_duel()
        
        if not duel:
            await message.answer(DUEL_TEXTS['no_content'])
            return
        
        # Показуємо створену дуель
        await show_duel(message, duel['id'])
        
    except Exception as e:
        logger.error(f"Error creating duel: {e}")
        await message.answer("❌ Помилка створення дуелі.")

async def cmd_active_duels(message: Message):
    """Команда перегляду активних дуелів"""
    try:
        active_duels = await get_active_duels(limit=10)
        
        if not active_duels:
            await message.answer(DUEL_TEXTS['no_active_duels'])
            return
        
        text = f"{DUEL_EMOJI['fire']} <b>АКТИВНІ ДУЕЛІ</b>\n\n"
        
        for i, duel in enumerate(active_duels, 1):
            votes_total = duel.get('challenger_votes', 0) + duel.get('opponent_votes', 0)
            time_left = calculate_time_left(duel.get('ends_at'))
            
            text += f"{i}. Дуель #{duel['id']}\n"
            text += f"   👥 Голосів: {votes_total}\n"
            text += f"   ⏰ Залишилось: {time_left}\n\n"
        
        # Кнопки для швидкого переходу
        keyboard = create_duels_list_keyboard(active_duels[:5])
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error getting active duels: {e}")
        await message.answer("❌ Помилка завантаження дуелів.")

# ===== CALLBACK ОБРОБНИКИ =====

async def handle_duel_callbacks(callback: CallbackQuery):
    """Обробка всіх callback'ів пов'язаних з дуелями"""
    try:
        data = callback.data
        user_id = callback.from_user.id
        
        # Гарантуємо що користувач існує
        await get_or_create_user(user_id, callback.from_user.username, callback.from_user.full_name)
        
        if data == "create_duel":
            await handle_create_duel_callback(callback)
            
        elif data == "view_duels":
            await handle_view_duels_callback(callback)
            
        elif data == "duel_stats":
            await handle_duel_stats_callback(callback)
            
        elif data == "duel_rules":
            await handle_duel_rules_callback(callback)
            
        elif data.startswith("view_duel_"):
            duel_id = int(data.split("_")[2])
            await handle_view_specific_duel(callback, duel_id)
            
        elif data.startswith("vote_"):
            await handle_vote_callback(callback)
            
        elif data.startswith("duel_refresh_"):
            duel_id = int(data.split("_")[2])
            await handle_refresh_duel(callback, duel_id)
            
        else:
            await callback.answer("❓ Невідома дія")
            
    except Exception as e:
        logger.error(f"Error in duel callback: {e}")
        await callback.answer("❌ Помилка обробки дії")

async def handle_create_duel_callback(callback: CallbackQuery):
    """Обробка створення дуелі через callback"""
    try:
        # Створюємо нову дуель
        duel = await create_random_duel()
        
        if not duel:
            await callback.answer(DUEL_TEXTS['no_content'], show_alert=True)
            return
        
        # Оновлюємо повідомлення з новою дуеллю
        await show_duel_in_message(callback.message, duel['id'], edit=True)
        await callback.answer(f"{DUEL_EMOJI['fire']} Дуель створено!")
        
    except Exception as e:
        logger.error(f"Error in create duel callback: {e}")
        await callback.answer("❌ Помилка створення дуелі")

async def handle_vote_callback(callback: CallbackQuery):
    """Обробка голосування в дуелі"""
    try:
        # Парсимо дані: vote_duelID_side (challenger/opponent)
        parts = callback.data.split("_")
        duel_id = int(parts[1])
        side = parts[2]  # 'challenger' або 'opponent'
        
        user_id = callback.from_user.id
        
        # Голосуємо
        result = await vote_in_duel(duel_id, user_id, side)
        
        if result['success']:
            # Оновлюємо дуель та показуємо результат
            await show_duel_in_message(callback.message, duel_id, edit=True)
            
            # Нараховуємо бали за голосування
            await update_user_points(user_id, RANK_REWARDS['vote_in_duel'], "Голосування в дуелі")
            
            await callback.answer(DUEL_TEXTS['vote_registered'])
            
            # Перевіряємо чи дуель готова до завершення
            await check_and_finish_duel(duel_id)
            
        elif result['error'] == 'already_voted':
            await callback.answer(DUEL_TEXTS['already_voted'], show_alert=True)
            
        elif result['error'] == 'duel_finished':
            await callback.answer("Дуель вже завершена!", show_alert=True)
            await show_duel_in_message(callback.message, duel_id, edit=True)
            
        else:
            await callback.answer(f"❌ {result.get('error', 'Помилка голосування')}")
            
    except Exception as e:
        logger.error(f"Error in vote callback: {e}")
        await callback.answer("❌ Помилка голосування")

async def handle_view_duels_callback(callback: CallbackQuery):
    """Показ списку активних дуелів"""
    try:
        active_duels = await get_active_duels(limit=10)
        
        if not active_duels:
            await callback.answer(DUEL_TEXTS['no_active_duels'], show_alert=True)
            return
        
        text = f"{DUEL_EMOJI['fire']} <b>АКТИВНІ ДУЕЛІ</b>\n\n"
        
        for i, duel in enumerate(active_duels, 1):
            votes_total = duel.get('challenger_votes', 0) + duel.get('opponent_votes', 0)
            time_left = calculate_time_left(duel.get('ends_at'))
            
            text += f"{i}. Дуель #{duel['id']} ({votes_total} голосів)\n"
            text += f"   ⏰ {time_left}\n\n"
        
        keyboard = create_duels_list_keyboard(active_duels[:5])
        
        # Оновлюємо повідомлення
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in view duels callback: {e}")
        await callback.answer("❌ Помилка завантаження дуелів")

async def handle_duel_stats_callback(callback: CallbackQuery):
    """Показ статистики дуелів користувача"""
    try:
        user_id = callback.from_user.id
        stats = await get_user_duel_stats(user_id)
        
        if not stats:
            await callback.answer("У вас ще немає статистики дуелів", show_alert=True)
            return
        
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        rating = stats.get('rating', 1000)
        
        # Визначаємо ранг
        rank = get_duel_rank(rating)
        
        text = f"{DUEL_EMOJI['trophy']} <b>СТАТИСТИКА ДУЕЛІВ</b>\n\n"
        text += f"🏆 Перемоги: {wins}\n"
        text += f"💔 Поразки: {losses}\n"
        text += f"📊 Відсоток перемог: {win_rate:.1f}%\n"
        text += f"⭐ Рейтинг: {rating}\n"
        text += f"👑 Ранг: {rank}\n\n"
        
        # Додаткова статистика
        if stats.get('best_win_streak', 0) > 0:
            text += f"🔥 Найкраща серія: {stats['best_win_streak']} перемог\n"
        
        if stats.get('total_votes_received', 0) > 0:
            text += f"👥 Отримано голосів: {stats['total_votes_received']}\n"
        
        # Кнопка повернення до головного меню дуелів
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад до дуелів", callback_data="back_to_duels")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in duel stats callback: {e}")
        await callback.answer("❌ Помилка завантаження статистики")

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def create_random_duel() -> Optional[Dict[str, Any]]:
    """Створення випадкової дуелі між двома жартами"""
    try:
        # Отримуємо два випадкові схвалені жарти
        content1 = await get_random_approved_content(ContentType.JOKE)
        content2 = await get_random_approved_content(ContentType.JOKE)
        
        if not content1 or not content2 or content1['id'] == content2['id']:
            # Пробуємо меми якщо жартів не вистачає
            if not content1:
                content1 = await get_random_approved_content(ContentType.MEME)
            if not content2:
                content2 = await get_random_approved_content(ContentType.MEME)
        
        if not content1 or not content2:
            return None
        
        # Тривалість дуелі (5 хвилин)
        duration_minutes = 5
        ends_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        # Створюємо дуель
        duel = await create_duel(
            content1_id=content1['id'],
            content2_id=content2['id'],
            ends_at=ends_at,
            min_votes=3
        )
        
        return duel
        
    except Exception as e:
        logger.error(f"Error creating random duel: {e}")
        return None

async def show_duel(message: Message, duel_id: int):
    """Показ дуелі в новому повідомленні"""
    try:
        duel = await get_duel_by_id(duel_id)
        
        if not duel:
            await message.answer("❌ Дуель не знайдена")
            return
        
        text = format_duel_text(duel)
        keyboard = create_duel_keyboard(duel)
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing duel: {e}")
        await message.answer("❌ Помилка завантаження дуелі")

async def show_duel_in_message(message: Message, duel_id: int, edit: bool = False):
    """Показ дуелі в існуючому повідомленні"""
    try:
        duel = await get_duel_by_id(duel_id)
        
        if not duel:
            text = "❌ Дуель не знайдена"
            keyboard = None
        else:
            text = format_duel_text(duel)
            keyboard = create_duel_keyboard(duel)
        
        if edit:
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error showing duel in message: {e}")

def format_duel_text(duel: Dict[str, Any]) -> str:
    """Форматування тексту дуелі"""
    try:
        # Базова інформація
        duel_id = duel['id']
        status = duel['status']
        
        # Контент
        content1 = duel.get('content1', {})
        content2 = duel.get('content2', {})
        
        # Голоси
        votes1 = duel.get('content1_votes', 0)
        votes2 = duel.get('content2_votes', 0)
        total_votes = votes1 + votes2
        
        # Заголовок
        text = f"{DUEL_EMOJI['sword']} <b>ДУЕЛЬ #{duel_id}</b> {DUEL_EMOJI['sword']}\n\n"
        
        if status == DuelStatus.FINISHED:
            # Завершена дуель
            winner_text = "🤝 Нічия!"
            if votes1 > votes2:
                winner_text = f"{DUEL_EMOJI['crown']} Переможець: Жарт A!"
            elif votes2 > votes1:
                winner_text = f"{DUEL_EMOJI['crown']} Переможець: Жарт B!"
            
            text += f"{winner_text}\n\n"
        else:
            # Активна дуель
            time_left = calculate_time_left(duel.get('ends_at'))
            text += f"{DUEL_EMOJI['timer']} Залишилось часу: {time_left}\n\n"
        
        # Контент дуелі
        text += f"🅰️ <b>Жарт A</b> ({votes1} {get_votes_word(votes1)}):\n"
        text += f"<i>{content1.get('text', 'Завантаження...')}</i>\n\n"
        
        text += f"🅱️ <b>Жарт B</b> ({votes2} {get_votes_word(votes2)}):\n"
        text += f"<i>{content2.get('text', 'Завантаження...')}</i>\n\n"
        
        # Підсумок голосування
        if total_votes > 0:
            percentage1 = (votes1 / total_votes * 100) if total_votes > 0 else 0
            percentage2 = (votes2 / total_votes * 100) if total_votes > 0 else 0
            
            text += f"📊 <b>Результати:</b>\n"
            text += f"🅰️ {percentage1:.1f}% ({'█' * int(percentage1/10)}{' ' * (10 - int(percentage1/10))})\n"
            text += f"🅱️ {percentage2:.1f}% ({'█' * int(percentage2/10)}{' ' * (10 - int(percentage2/10))})\n\n"
        
        # Додаткова інформація для активних дуелів
        if status == DuelStatus.ACTIVE:
            min_votes = duel.get('min_votes', 3)
            if total_votes < min_votes:
                text += f"💡 Для завершення потрібно ще {min_votes - total_votes} {get_votes_word(min_votes - total_votes)}\n"
        
        return text
        
    except Exception as e:
        logger.error(f"Error formatting duel text: {e}")
        return f"❌ Помилка завантаження дуелі #{duel.get('id', '?')}"

def create_duel_keyboard(duel: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Створення клавіатури для дуелі"""
    try:
        duel_id = duel['id']
        status = duel['status']
        
        buttons = []
        
        if status == DuelStatus.ACTIVE:
            # Кнопки голосування для активної дуелі
            buttons.append([
                InlineKeyboardButton(
                    text=f"🅰️ Голосую за A", 
                    callback_data=f"vote_{duel_id}_content1"
                ),
                InlineKeyboardButton(
                    text=f"🅱️ Голосую за B", 
                    callback_data=f"vote_{duel_id}_content2"
                )
            ])
            
            # Кнопка оновлення
            buttons.append([
                InlineKeyboardButton(
                    text="🔄 Оновити", 
                    callback_data=f"duel_refresh_{duel_id}"
                )
            ])
        
        # Кнопка повернення
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Назад до дуелів", 
                callback_data="back_to_duels"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
        
    except Exception as e:
        logger.error(f"Error creating duel keyboard: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[])

def create_duel_main_keyboard(has_active_duels: bool = False) -> InlineKeyboardMarkup:
    """Створення головної клавіатури дуелів"""
    buttons = [
        [InlineKeyboardButton(text=f"{DUEL_EMOJI['fire']} Створити дуель", callback_data="create_duel")],
    ]
    
    if has_active_duels:
        buttons.append([
            InlineKeyboardButton(text=f"{DUEL_EMOJI['target']} Активні дуелі", callback_data="view_duels")
        ])
    
    buttons.extend([
        [InlineKeyboardButton(text=f"{DUEL_EMOJI['trophy']} Моя статистика", callback_data="duel_stats")],
        [InlineKeyboardButton(text="❓ Правила дуелів", callback_data="duel_rules")],
        [InlineKeyboardButton(text="🔙 Головне меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_duels_list_keyboard(duels: List[Dict]) -> InlineKeyboardMarkup:
    """Створення клавіатури зі списком дуелів"""
    buttons = []
    
    for duel in duels[:5]:  # Максимум 5 дуелів
        votes_total = duel.get('content1_votes', 0) + duel.get('content2_votes', 0)
        button_text = f"Дуель #{duel['id']} ({votes_total} голосів)"
        buttons.append([
            InlineKeyboardButton(
                text=button_text, 
                callback_data=f"view_duel_{duel['id']}"
            )
        ])
    
    # Кнопка створення нової дуелі
    buttons.append([
        InlineKeyboardButton(text=f"{DUEL_EMOJI['fire']} Створити нову", callback_data="create_duel")
    ])
    
    # Кнопка повернення
    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_duels")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def calculate_time_left(ends_at) -> str:
    """Розрахунок часу що залишився"""
    try:
        if not ends_at:
            return "Невідомо"
        
        if isinstance(ends_at, str):
            ends_at = datetime.fromisoformat(ends_at.replace('Z', '+00:00'))
        
        now = datetime.utcnow()
        if ends_at.tzinfo:
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        
        diff = ends_at - now
        
        if diff.total_seconds() <= 0:
            return "Завершено"
        
        minutes = int(diff.total_seconds() // 60)
        seconds = int(diff.total_seconds() % 60)
        
        if minutes > 0:
            return f"{minutes}хв {seconds}с"
        else:
            return f"{seconds}с"
            
    except Exception:
        return "Невідомо"

def get_votes_word(count: int) -> str:
    """Правильна форма слова 'голос'"""
    if count % 10 == 1 and count % 100 != 11:
        return "голос"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "голоси"
    else:
        return "голосів"

def get_duel_rank(rating: int) -> str:
    """Визначення рангу дуеліста за рейтингом"""
    if rating >= 2000:
        return f"{DUEL_EMOJI['crown']} Гранд-майстер"
    elif rating >= 1800:
        return f"{DUEL_EMOJI['trophy']} Майстер"
    elif rating >= 1600:
        return f"{DUEL_EMOJI['star']} Експерт"
    elif rating >= 1400:
        return f"{DUEL_EMOJI['lightning']} Професіонал"
    elif rating >= 1200:
        return f"{DUEL_EMOJI['fire']} Досвідчений"
    elif rating >= 1000:
        return f"{DUEL_EMOJI['target']} Новачок"
    else:
        return "🥉 Стажер"

async def check_and_finish_duel(duel_id: int):
    """Перевірка та автоматичне завершення дуелі"""
    try:
        duel = await get_duel_by_id(duel_id)
        
        if not duel or duel['status'] != DuelStatus.ACTIVE:
            return
        
        total_votes = duel.get('content1_votes', 0) + duel.get('content2_votes', 0)
        min_votes = duel.get('min_votes', 3)
        ends_at = duel.get('ends_at')
        
        # Перевіряємо умови завершення
        should_finish = False
        
        # Час вичерпано
        if ends_at:
            if isinstance(ends_at, str):
                ends_at = datetime.fromisoformat(ends_at.replace('Z', '+00:00'))
            
            now = datetime.utcnow()
            if ends_at.tzinfo:
                from datetime import timezone
                now = now.replace(tzinfo=timezone.utc)
            
            if now >= ends_at and total_votes >= min_votes:
                should_finish = True
        
        # Достатньо голосів і явний лідер
        if total_votes >= min_votes * 2:  # В два рази більше мінімуму
            votes1 = duel.get('content1_votes', 0)
            votes2 = duel.get('content2_votes', 0)
            
            # Якщо різниця більше 50% від загальних голосів
            if abs(votes1 - votes2) > total_votes * 0.5:
                should_finish = True
        
        if should_finish:
            await finish_duel(duel_id)
            logger.info(f"Duel {duel_id} finished automatically")
        
    except Exception as e:
        logger.error(f"Error checking duel finish: {e}")

# ===== ДОДАТКОВІ ХЕНДЛЕРИ =====

async def handle_duel_rules_callback(callback: CallbackQuery):
    """Показ правил дуелів"""
    text = f"{DUEL_EMOJI['sword']} <b>ПРАВИЛА ДУЕЛІВ ЖАРТІВ</b>\n\n"
    text += "🎯 <b>Як працють дуелі:</b>\n"
    text += "• Два жарти змагаються за голоси\n"
    text += "• Кожен користувач може проголосувати один раз\n"
    text += "• Дуель триває 5 хвилин\n"
    text += "• Мінімум 3 голоси для завершення\n\n"
    
    text += "🏆 <b>Нагороди:</b>\n"
    text += f"• За голосування: +{RANK_REWARDS['vote_in_duel']} балів\n"
    text += f"• За участь: +{RANK_REWARDS['duel_participate']} балів\n"
    text += f"• За перемогу: +{RANK_REWARDS['duel_win']} балів\n"
    text += f"• За розгромну перемогу: +{RANK_REWARDS['epic_victory']} балів\n\n"
    
    text += "📊 <b>Рейтингова система:</b>\n"
    text += "• Початковий рейтинг: 1000\n"
    text += "• За перемогу: +20-40 рейтингу\n"
    text += "• За поразку: -10-20 рейтингу\n"
    text += "• Ранги від Стажера до Гранд-майстра\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад до дуелів", callback_data="back_to_duels")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_duel_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів дуелів"""
    
    # Команди
    dp.message.register(cmd_duel, Command("duel"))
    dp.message.register(cmd_create_duel, Command("create_duel"))
    dp.message.register(cmd_active_duels, Command("duels"))
    
    # Callback'и
    dp.callback_query.register(
        handle_duel_callbacks,
        lambda c: c.data and (
            c.data.startswith("duel_") or
            c.data.startswith("vote_") or
            c.data in ["create_duel", "view_duels", "duel_stats", "duel_rules", "back_to_duels"]
        )
    )
    
    logger.info("✅ Duel handlers registered")

# ===== ЕКСПОРТ =====

__all__ = [
    'register_duel_handlers',
    'cmd_duel',
    'create_random_duel',
    'check_and_finish_duel',
    'DuelStates',
    'RANK_REWARDS'
]