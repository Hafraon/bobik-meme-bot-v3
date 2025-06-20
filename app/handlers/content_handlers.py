#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import random
from datetime import datetime
from typing import Optional

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

# FSM для подачі контенту
class ContentSubmissionStates(StatesGroup):
    waiting_for_meme = State()
    waiting_for_joke = State()
    waiting_for_anekdot = State()

# Готовий контент для демонстрації
DEMO_MEMES = [
    "Коли бачиш ціни в магазині після зарплати: 'Я багатий!' \n\n*через 3 дні* \n\n'Хлібом підойду...' 😅",
    "Українець заходить в кафе:\n- Що у вас є?\n- Все є!\n- А борщ?\n- Нема.\n- А вареники?\n- Нема.\n- То що є?\n- Все нема! 😂",
    "Коли мама каже 'Приберися в кімнаті':\n\nЯ: *переклав все з підлоги на ліжко*\n\nТехнічно, підлога чиста! 🧠",
    "Понеділок - це як математика:\nНіхто не любить, але всі змушені терпіти 😤",
    "Коли друзі запитують чому я не виходжу:\n\nГроші: відсутні ✗\nЕнергія: відсутня ✗ \nБажання: відсутнє ✗\n\nДиван: присутній ✓"
]

DEMO_JOKES = [
    "Чому програмісти не люблять природу?\n\nБо там забагато багів! 🐛💻",
    "Учитель:\n- Петрику, назви мені 5 речей, які містять молоко.\n- Сир, масло, морозиво та... дві корови! 🐄",
    "Дружина чоловікові:\n- Дорогий, ти мене любиш?\n- Авжеж!\n- А наскільки?\n- На всі мої гроші! 💰",
    "Чому ведмеді не носять кросівки?\n\nБо в них лапи! 🐻👟",
    "Заходить чоловік до аптеки:\n- Дайте щось від головного болю.\n- Візьміть аспірин.\n- А що дешевше?\n- Розлучення! 💊💔"
]

DEMO_ANEKDOTS = [
    "Іде Василь по лісу, бачить - ведмідь.\nВедмідь:\n- Ти мене боїшся?\n- Ні.\n- А чому тоді тремтиш?\n- Та я от думаю, ти мене боїшся чи ні... 🐻😅",
    "Приходить син додому:\n- Мам, я одружуюся!\n- З ким?\n- З Машею з сусіднього двору.\n- Синку, вона ж тобі не пара!\n- Чому?\n- Так вона ж розумна! 🤦‍♂️",
    "Дзвонить Іван додому:\n- Алло, це дім Петренків?\n- Ні, це дім Сидоренків.\n- Вибачте, я помилився номером.\n- Нічого, ми теж не завжди дома! 📞😂",
    "Зустрічаються два друзі:\n- Як справи?\n- Та все добре, тільки з грошима погано.\n- А що з ними?\n- Вони в мене є! 💸",
    "Учитель:\n- Дітки, хто знає, що таке 'ніколи'?\nПетрик:\n- Це коли мама каже 'зараз'! ⏰"
]

def get_content_keyboard(content_id: int, content_type: str = "demo") -> InlineKeyboardMarkup:
    """Створення клавіатури для контенту"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Подобається", callback_data=f"like_{content_type}_{content_id}"),
            InlineKeyboardButton(text="👎 Не подобається", callback_data=f"dislike_{content_type}_{content_id}")
        ],
        [
            InlineKeyboardButton(text="🔄 Ще один", callback_data=f"more_{content_type}"),
            InlineKeyboardButton(text="📝 Подати свій", callback_data=f"submit_{content_type}")
        ]
    ])
    return keyboard

async def handle_meme_command(message: Message):
    """Обробка команди /meme"""
    try:
        # Спочатку спробуємо взяти з БД
        try:
            from database.services import get_random_approved_content, update_user_points
            
            content = get_random_approved_content("meme")
            if content:
                # Контент з БД
                keyboard = get_content_keyboard(content['id'], "db_meme")
                
                # Нараховуємо бали за перегляд
                update_user_points(message.from_user.id, 1, "перегляд мему")
                
                await message.answer(
                    f"😂 <b>Мем від користувача:</b>\n\n{content['text']}\n\n"
                    f"👀 Переглядів: {content['views']} | 👍 Лайків: {content['likes']}",
                    reply_markup=keyboard
                )
                return
        except ImportError:
            pass
        
        # Fallback до демо контенту
        meme = random.choice(DEMO_MEMES)
        meme_id = DEMO_MEMES.index(meme)
        
        keyboard = get_content_keyboard(meme_id, "demo_meme")
        
        await message.answer(
            f"😂 <b>Демо мем:</b>\n\n{meme}",
            reply_markup=keyboard
        )
        
        logger.info(f"User {message.from_user.id} viewed demo meme {meme_id}")
        
    except Exception as e:
        logger.error(f"Error in meme handler: {e}")
        await message.answer("❌ Помилка завантаження мему. Спробуйте пізніше.")

async def handle_joke_command(message: Message):
    """Обробка команди /joke"""
    try:
        # Спочатку спробуємо взяти з БД
        try:
            from database.services import get_random_approved_content, update_user_points
            
            content = get_random_approved_content("joke")
            if content:
                keyboard = get_content_keyboard(content['id'], "db_joke")
                
                # Нараховуємо бали за перегляд
                update_user_points(message.from_user.id, 1, "перегляд жарту")
                
                await message.answer(
                    f"🤣 <b>Жарт від користувача:</b>\n\n{content['text']}\n\n"
                    f"👀 Переглядів: {content['views']} | 👍 Лайків: {content['likes']}",
                    reply_markup=keyboard
                )
                return
        except ImportError:
            pass
        
        # Fallback до демо контенту
        joke = random.choice(DEMO_JOKES)
        joke_id = DEMO_JOKES.index(joke)
        
        keyboard = get_content_keyboard(joke_id, "demo_joke")
        
        await message.answer(
            f"🤣 <b>Демо жарт:</b>\n\n{joke}",
            reply_markup=keyboard
        )
        
        logger.info(f"User {message.from_user.id} viewed demo joke {joke_id}")
        
    except Exception as e:
        logger.error(f"Error in joke handler: {e}")
        await message.answer("❌ Помилка завантаження жарту. Спробуйте пізніше.")

async def handle_anekdot_command(message: Message):
    """Обробка команди /anekdot"""
    try:
        # Спочатку спробуємо взяти з БД
        try:
            from database.services import get_random_approved_content, update_user_points
            
            content = get_random_approved_content("anekdot")
            if content:
                keyboard = get_content_keyboard(content['id'], "db_anekdot")
                
                # Нараховуємо бали за перегляд
                update_user_points(message.from_user.id, 1, "перегляд анекдоту")
                
                await message.answer(
                    f"🧠 <b>Анекдот від користувача:</b>\n\n{content['text']}\n\n"
                    f"👀 Переглядів: {content['views']} | 👍 Лайків: {content['likes']}",
                    reply_markup=keyboard
                )
                return
        except ImportError:
            pass
        
        # Fallback до демо контенту
        anekdot = random.choice(DEMO_ANEKDOTS)
        anekdot_id = DEMO_ANEKDOTS.index(anekdot)
        
        keyboard = get_content_keyboard(anekdot_id, "demo_anekdot")
        
        await message.answer(
            f"🧠 <b>Демо анекдот:</b>\n\n{anekdot}",
            reply_markup=keyboard
        )
        
        logger.info(f"User {message.from_user.id} viewed demo anekdot {anekdot_id}")
        
    except Exception as e:
        logger.error(f"Error in anekdot handler: {e}")
        await message.answer("❌ Помилка завантаження анекдоту. Спробуйте пізніше.")

async def handle_content_callbacks(callback: CallbackQuery, state: FSMContext):
    """Обробка callback'ів для контенту"""
    try:
        data = callback.data
        user_id = callback.from_user.id
        
        if data.startswith("like_"):
            # Обробка лайків
            parts = data.split("_")
            content_type = "_".join(parts[1:-1])
            content_id = parts[-1]
            
            try:
                from database.services import update_user_points
                # Нараховуємо бали за реакцію
                update_user_points(user_id, 2, f"лайк {content_type}")
                await callback.answer("👍 Дякуємо за оцінку! +2 бали")
            except ImportError:
                await callback.answer("👍 Дякуємо за оцінку!")
            
            logger.info(f"User {user_id} liked {content_type} {content_id}")
            
        elif data.startswith("dislike_"):
            await callback.answer("👎 Дякуємо за оцінку!")
            
        elif data.startswith("more_"):
            # Запит ще одного контенту
            content_type = data.replace("more_", "")
            
            if "meme" in content_type:
                await handle_meme_command(callback.message)
            elif "joke" in content_type:
                await handle_joke_command(callback.message)
            elif "anekdot" in content_type:
                await handle_anekdot_command(callback.message)
            
            await callback.answer()
            
        elif data.startswith("submit_"):
            # Початок процесу подачі контенту
            content_type = data.replace("submit_", "")
            
            if "meme" in content_type:
                await state.set_state(ContentSubmissionStates.waiting_for_meme)
                await callback.message.answer(
                    "📝 <b>Подача мему</b>\n\n"
                    "Надішліть свій мем текстом. Він буде розглянутий модератором.\n"
                    "За схвалення ви отримаєте +20 балів!\n\n"
                    "Натисніть /cancel для скасування."
                )
            elif "joke" in content_type:
                await state.set_state(ContentSubmissionStates.waiting_for_joke)
                await callback.message.answer(
                    "📝 <b>Подача жарту</b>\n\n"
                    "Надішліть свій жарт текстом. Він буде розглянутий модератором.\n"
                    "За схвалення ви отримаєте +20 балів!\n\n"
                    "Натисніть /cancel для скасування."
                )
            elif "anekdot" in content_type:
                await state.set_state(ContentSubmissionStates.waiting_for_anekdot)
                await callback.message.answer(
                    "📝 <b>Подача анекдоту</b>\n\n"
                    "Надішліть свій анекдот текстом. Він буде розглянутий модератором.\n"
                    "За схвалення ви отримаєте +20 балів!\n\n"
                    "Натисніть /cancel для скасування."
                )
            
            await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in content callback: {e}")
        await callback.answer("❌ Помилка обробки!")

async def handle_content_submission(message: Message, state: FSMContext):
    """Обробка подачі контенту"""
    try:
        current_state = await state.get_state()
        
        if not current_state:
            return
        
        content_text = message.text
        if not content_text or len(content_text.strip()) < 10:
            await message.answer("❌ Контент занадто короткий. Мінімум 10 символів.")
            return
        
        if len(content_text) > 1000:
            await message.answer("❌ Контент занадто довгий. Максимум 1000 символів.")
            return
        
        # Визначаємо тип контенту
        content_type = None
        if current_state == ContentSubmissionStates.waiting_for_meme:
            content_type = "meme"
        elif current_state == ContentSubmissionStates.waiting_for_joke:
            content_type = "joke"
        elif current_state == ContentSubmissionStates.waiting_for_anekdot:
            content_type = "anekdot"
        
        if not content_type:
            await message.answer("❌ Невідомий тип контенту.")
            await state.clear()
            return
        
        # Спроба збереження в БД
        try:
            from database.services import add_content, update_user_points
            
            content_id = add_content(
                author_user_id=message.from_user.id,
                content_type=content_type,
                text=content_text
            )
            
            if content_id:
                # Нараховуємо бали за подачу
                update_user_points(message.from_user.id, 10, f"подача {content_type}")
                
                await message.answer(
                    f"✅ <b>Контент відправлено на модерацію!</b>\n\n"
                    f"Тип: {content_type}\n"
                    f"ID: {content_id}\n\n"
                    f"За подачу ви отримали +10 балів!\n"
                    f"За схвалення отримаєте ще +20 балів!"
                )
                
                logger.info(f"User {message.from_user.id} submitted {content_type} content (ID: {content_id})")
            else:
                await message.answer("❌ Помилка збереження контенту. Спробуйте пізніше.")
                
        except ImportError:
            # Fallback без БД
            await message.answer(
                f"✅ <b>Дякуємо за контент!</b>\n\n"
                f"Ваш {content_type} буде розглянутий в наступних версіях бота.\n"
                f"База даних наразі недоступна."
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in content submission: {e}")
        await message.answer("❌ Помилка обробки контенту.")
        await state.clear()

async def handle_cancel_command(message: Message, state: FSMContext):
    """Скасування поточної дії"""
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("❌ Дію скасовано.")
    else:
        await message.answer("Немає активних дій для скасування.")

def register_content_handlers(dp: Dispatcher):
    """Реєстрація хендлерів контенту"""
    
    # Команди контенту
    dp.message.register(handle_meme_command, Command("meme"))
    dp.message.register(handle_joke_command, Command("joke"))
    dp.message.register(handle_anekdot_command, Command("anekdot"))
    dp.message.register(handle_cancel_command, Command("cancel"))
    
    # Callback'и контенту (реєструємо окремо від основних)
    dp.callback_query.register(
        handle_content_callbacks,
        lambda c: c.data and (
            c.data.startswith("like_") or 
            c.data.startswith("dislike_") or 
            c.data.startswith("more_") or 
            c.data.startswith("submit_")
        )
    )
    
    # Обробка подачі контенту в FSM станах
    dp.message.register(
        handle_content_submission,
        ContentSubmissionStates.waiting_for_meme
    )
    dp.message.register(
        handle_content_submission,
        ContentSubmissionStates.waiting_for_joke
    )
    dp.message.register(
        handle_content_submission,
        ContentSubmissionStates.waiting_for_anekdot
    )
    
    logger.info("✅ Content handlers registered")

# Експорт для використання в інших модулях
__all__ = [
    'register_content_handlers',
    'handle_meme_command',
    'handle_joke_command', 
    'handle_anekdot_command',
    'ContentSubmissionStates'
]