#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Хендлери для роботи з контентом 🧠😂🔥
"""

import logging
import random
from datetime import datetime
from typing import Dict, Set

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Імпорти з нашого проекту
from settings import settings, EMOJI, TEXTS, TIME_GREETINGS

logger = logging.getLogger(__name__)

# FSM для подачі контенту
class SubmissionStates(StatesGroup):
    waiting_for_content = State()

# Глобальне сховище для відстеження показаних анекдотів/мемів
# В продакшені це буде в БД або Redis
USER_SHOWN_JOKES: Dict[int, Set[int]] = {}
USER_SHOWN_MEMES: Dict[int, Set[int]] = {}

# Тимчасові дані поки БД не налаштована
SAMPLE_JOKES = [
    "🧠 Приходить програміст до лікаря:\n- Доктор, в мене болить рука!\n- А де саме?\n- В лівому кліку! 😂",
    "🔥 Зустрічаються два українці:\n- Як справи?\n- Та нормально, працюю в IT.\n- А що робиш?\n- Борщ доставляю через додаток! 😂",
    "😂 Учитель запитує:\n- Петрику, скільки буде 2+2?\n- А ви про що? Про гривні чи про долари? 🧠",
    "🔥 Покупець у магазині:\n- Скільки коштує хліб?\n- 20 гривень.\n- А вчора був 15!\n- Вчора ви його і не купили! 😂",
    "🧠 Дружина чоловікові:\n- Любий, я схудла на 5 кг!\n- А де вони?\n- В холодильнику! 😂🔥",
    "😂 Син питає батька:\n- Тату, а що таке політика?\n- Це коли багато людей говорять, а нічого не роблять.\n- А що таке демократія?\n- Це коли всі мають право говорити, але слухає тільки мама! 🧠",
    "🔥 Лікар пацієнтові:\n- Ви кури?\n- Ні.\n- П'єте?\n- Ні.\n- Тоді живіть як хочете - все одно довго протягнете! 😂",
    "🧠 Заходить чоловік до аптеки:\n- Дайте щось від голови!\n- А що саме болить?\n- Дружина! 😂🔥",
    "😂 Розмова в офісі:\n- Ти чому такий веселий?\n- Зарплату підняли!\n- На скільки?\n- На другий поверх! 🧠",
    "🔥 Студент здає екзамен:\n- Розкажіть про Наполеона.\n- Не можу, ми не знайомі особисто.\n- Тоді про Пушкіна.\n- Теж не знайомі.\n- Незадовільно!\n- А з ким ви знайомі?\n- З вами... і то погано! 😂"
]

SAMPLE_MEMES = [
    {
        "caption": "🧠 Коли нарешті зрозумів як працює async/await 😂",
        "description": "Мем про програмування"
    },
    {
        "caption": "🔥 Настрій понеділка vs настрій п'ятниці 😂",
        "description": "Мем про робочий тиждень"
    },
    {
        "caption": "🧠 Коли код працює з першого разу 😂🔥",
        "description": "Мем про чудеса програмування"
    },
    {
        "caption": "😂 Коли побачив зарплату після податків 🤔",
        "description": "Мем про зарплату"
    },
    {
        "caption": "🔥 Українець під час блекауту: 'А у нас світло є!' 😎",
        "description": "Мем про українську стійкість"
    }
]

def get_random_joke_without_repeat(user_id: int) -> tuple:
    """Отримання випадкового анекдоту без повторів"""
    global USER_SHOWN_JOKES
    
    # Ініціалізуємо користувача якщо потрібно
    if user_id not in USER_SHOWN_JOKES:
        USER_SHOWN_JOKES[user_id] = set()
    
    shown_jokes = USER_SHOWN_JOKES[user_id]
    available_jokes = []
    
    # Знаходимо доступні анекдоти (не показані)
    for i, joke in enumerate(SAMPLE_JOKES):
        if i not in shown_jokes:
            available_jokes.append((i, joke))
    
    # Якщо всі анекдоти показано - скидаємо історію
    if not available_jokes:
        USER_SHOWN_JOKES[user_id] = set()
        available_jokes = [(i, joke) for i, joke in enumerate(SAMPLE_JOKES)]
        logger.info(f"🔄 Скинуто історію анекдотів для користувача {user_id}")
    
    # Вибираємо випадковий доступний анекдот
    joke_index, joke_text = random.choice(available_jokes)
    
    # Додаємо до показаних
    USER_SHOWN_JOKES[user_id].add(joke_index)
    
    return joke_index, joke_text

def get_random_meme_without_repeat(user_id: int) -> tuple:
    """Отримання випадкового мему без повторів"""
    global USER_SHOWN_MEMES
    
    # Ініціалізуємо користувача якщо потрібно
    if user_id not in USER_SHOWN_MEMES:
        USER_SHOWN_MEMES[user_id] = set()
    
    shown_memes = USER_SHOWN_MEMES[user_id]
    available_memes = []
    
    # Знаходимо доступні меми (не показані)
    for i, meme in enumerate(SAMPLE_MEMES):
        if i not in shown_memes:
            available_memes.append((i, meme))
    
    # Якщо всі меми показано - скидаємо історію
    if not available_memes:
        USER_SHOWN_MEMES[user_id] = set()
        available_memes = [(i, meme) for i, meme in enumerate(SAMPLE_MEMES)]
        logger.info(f"🔄 Скинуто історію мемів для користувача {user_id}")
    
    # Вибираємо випадковий доступний мем
    meme_index, meme_data = random.choice(available_memes)
    
    # Додаємо до показаних
    USER_SHOWN_MEMES[user_id].add(meme_index)
    
    return meme_index, meme_data

async def cmd_anekdot(message: Message):
    """Команда /anekdot"""
    await send_joke(message)

async def cmd_meme(message: Message):
    """Команда /meme"""
    await send_meme(message)

async def send_joke(message: Message, from_callback: bool = False):
    """Надсилання випадкового анекдоту БЕЗ ПОВТОРІВ"""
    user_id = message.from_user.id
    
    try:
        # Спробуємо отримати з БД
        try:
            from database import get_random_joke
            joke_obj = await get_random_joke()
            if joke_obj:
                joke_text = joke_obj.text
                joke_views = getattr(joke_obj, 'views', 0)
            else:
                # Якщо БД порожня, використовуємо зразки БЕЗ ПОВТОРІВ
                joke_index, joke_text = get_random_joke_without_repeat(user_id)
                joke_views = random.randint(50, 500)  # Фейкові перегляди для демо
        except:
            # Якщо БД не працює, використовуємо зразки БЕЗ ПОВТОРІВ
            joke_index, joke_text = get_random_joke_without_repeat(user_id)
            joke_views = random.randint(50, 500)  # Фейкові перегляди для демо
        
        # Контекстне привітання залежно від часу
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            greeting = random.choice(TIME_GREETINGS["morning"])
        elif 12 <= current_hour < 18:
            greeting = random.choice(TIME_GREETINGS["day"])
        elif 18 <= current_hour < 23:
            greeting = random.choice(TIME_GREETINGS["evening"])
        else:
            greeting = random.choice(TIME_GREETINGS["night"])
        
        # Клавіатура для взаємодії
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['like']} Подобається", callback_data="like_joke"),
                InlineKeyboardButton(text=f"{EMOJI['dislike']} Не подобається", callback_data="dislike_joke")
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Ще анекдот", callback_data="get_joke"),
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати свій", callback_data="submit_joke")
            ]
        ])
        
        # Додаємо лічильник переглядів
        views_text = f"👁️ {joke_views}"
        response_text = f"{greeting}\n\n{joke_text}\n\n{views_text} • {EMOJI['star']} Сподобався анекдот? Оціни!"
        
        await message.answer(
            response_text,
            reply_markup=keyboard
        )
        
        # Нарахування балів (якщо БД працює)
        try:
            from database import update_user_points
            await update_user_points(user_id, 1, "перегляд анекдоту")
        except:
            pass  # Ігноруємо помилки БД
        
        if not from_callback:
            logger.info(f"🧠 Користувач {user_id} отримав анекдот без повтору")
            
    except Exception as e:
        logger.error(f"Помилка надсилання анекдоту: {e}")
        await message.answer(f"{EMOJI['cross']} Упс! Сталася помилка. Спробуй ще раз!")

async def send_meme(message: Message, from_callback: bool = False):
    """Надсилання випадкового мему БЕЗ ПОВТОРІВ"""
    user_id = message.from_user.id
    
    try:
        # Спробуємо отримати з БД
        try:
            from database import get_random_meme
            meme_obj = await get_random_meme()
            if meme_obj:
                meme_data = {"caption": meme_obj.text, "description": "Мем з бази"}
                meme_views = getattr(meme_obj, 'views', 0)
            else:
                # Якщо БД порожня, використовуємо зразки БЕЗ ПОВТОРІВ
                meme_index, meme_data = get_random_meme_without_repeat(user_id)
                meme_views = random.randint(80, 600)  # Фейкові перегляди для демо
        except:
            # Якщо БД не працює, використовуємо зразки БЕЗ ПОВТОРІВ
            meme_index, meme_data = get_random_meme_without_repeat(user_id)
            meme_views = random.randint(80, 600)  # Фейкові перегляди для демо
        
        # Контекстне привітання
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            greeting = random.choice(TIME_GREETINGS["morning"])
        elif 12 <= current_hour < 18:
            greeting = random.choice(TIME_GREETINGS["day"])
        elif 18 <= current_hour < 23:
            greeting = random.choice(TIME_GREETINGS["evening"])
        else:
            greeting = random.choice(TIME_GREETINGS["night"])
        
        # Клавіатура для взаємодії
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['like']} Подобається", callback_data="like_meme"),
                InlineKeyboardButton(text=f"{EMOJI['dislike']} Не подобається", callback_data="dislike_meme")
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Ще мем", callback_data="get_meme"),
                InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати свій", callback_data="submit_meme")
            ]
        ])
        
        # Додаємо лічильник переглядів
        views_text = f"👁️ {meme_views}"
        response_text = f"{greeting}\n\n{meme_data['caption']}\n\n{views_text} • {EMOJI['star']} Сподобався мем? Оціни!"
        
        await message.answer(
            response_text,
            reply_markup=keyboard
        )
        
        # Нарахування балів (якщо БД працює)
        try:
            from database import update_user_points
            await update_user_points(user_id, 1, "перегляд мему")
        except:
            pass  # Ігноруємо помилки БД
        
        if not from_callback:
            logger.info(f"🔥 Користувач {user_id} отримав мем без повтору")
            
    except Exception as e:
        logger.error(f"Помилка надсилання мему: {e}")
        await message.answer(f"{EMOJI['cross']} Упс! Сталася помилка. Спробуй ще раз!")

async def cmd_submit(message: Message, state: FSMContext):
    """Команда /submit - подача контенту на модерацію"""
    user_id = message.from_user.id
    
    # Отримуємо текст після команди
    text_parts = message.text.split(maxsplit=1)
    
    if len(text_parts) > 1:
        # Якщо є текст після команди - це анекдот
        joke_text = text_parts[1].strip()
        
        if len(joke_text) < 10:
            await message.answer(
                f"{EMOJI['cross']} Анекдот занадто короткий! Мінімум 10 символів."
            )
            return
        
        if len(joke_text) > settings.MAX_JOKE_LENGTH:
            await message.answer(
                f"{EMOJI['cross']} Анекдот занадто довгий! Максимум {settings.MAX_JOKE_LENGTH} символів."
            )
            return
        
        # Зберігаємо анекдот на модерацію
        try:
            from database import add_content_for_moderation
            await add_content_for_moderation(
                user_id=user_id,
                content_type="joke",
                text=joke_text
            )
            
            # Нарахування балів за подачу
            from database import update_user_points
            await update_user_points(user_id, settings.POINTS_FOR_SUBMISSION, "подача анекдоту")
            
            await message.answer(
                f"{EMOJI['star']} Дякую! Твій анекдот надіслано на модерацію.\n"
                f"Отримано +{settings.POINTS_FOR_SUBMISSION} балів!\n\n"
                f"Після схвалення отримаєш ще +{settings.POINTS_FOR_APPROVAL} балів! {EMOJI['fire']}"
            )
            
        except Exception as e:
            logger.error(f"Помилка збереження анекдоту: {e}")
            await message.answer(
                f"{EMOJI['cross']} Сталася помилка. Спробуй ще раз!"
            )
    else:
        # Інструкції по використанню
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Як надіслати анекдот?", callback_data="how_submit_joke"),
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Як надіслати мем?", callback_data="how_submit_meme")
            ]
        ])
        
        await message.answer(
            f"{EMOJI['fire']} <b>Як надіслати свій контент:</b>\n\n"
            f"{EMOJI['brain']} <b>Анекдот:</b>\n"
            f"<code>/submit Твій смішний анекдот тут</code>\n\n"
            f"{EMOJI['laugh']} <b>Мем:</b>\n"
            f"Надішли картинку з підписом\n\n"
            f"{EMOJI['star']} За кожну подачу: <b>+{settings.POINTS_FOR_SUBMISSION} балів</b>\n"
            f"За схвалення: <b>+{settings.POINTS_FOR_APPROVAL} балів</b>",
            reply_markup=keyboard
        )
    
    logger.info(f"🔥 Користувач {user_id} надіслав контент на модерацію")

async def handle_photo_submission(message: Message):
    """Обробка фото для подачі мему"""
    user_id = message.from_user.id
    
    if not message.caption:
        await message.answer(
            f"{EMOJI['cross']} Для мему потрібен підпис! Додай підпис до картинки."
        )
        return
    
    caption = message.caption.strip()
    
    if len(caption) < 5:
        await message.answer(
            f"{EMOJI['cross']} Підпис занадто короткий! Мінімум 5 символів."
        )
        return
    
    if len(caption) > settings.MAX_MEME_CAPTION_LENGTH:
        await message.answer(
            f"{EMOJI['cross']} Підпис занадто довгий! Максимум {settings.MAX_MEME_CAPTION_LENGTH} символів."
        )
        return
    
    # Зберігаємо мем на модерацію
    try:
        from database import add_content_for_moderation
        
        # Отримуємо найбільше фото
        photo = message.photo[-1]
        
        await add_content_for_moderation(
            user_id=user_id,
            content_type="meme",
            text=caption,
            file_id=photo.file_id
        )
        
        # Нарахування балів за подачу
        from database import update_user_points
        await update_user_points(user_id, settings.POINTS_FOR_SUBMISSION, "подача мему")
        
        await message.answer(
            f"{EMOJI['star']} Дякую! Твій мем надіслано на модерацію.\n"
            f"Отримано +{settings.POINTS_FOR_SUBMISSION} балів!\n\n"
            f"Після схвалення отримаєш ще +{settings.POINTS_FOR_APPROVAL} балів! {EMOJI['fire']}"
        )
        
    except Exception as e:
        logger.error(f"Помилка збереження мему: {e}")
        await message.answer(
            f"{EMOJI['cross']} Сталася помилка. Спробуй ще раз!"
        )
    
    logger.info(f"🔥 Користувач {user_id} надіслав мем")

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_get_joke(callback_query: CallbackQuery):
    """Callback для отримання анекдоту"""
    await send_joke(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_get_meme(callback_query: CallbackQuery):
    """Callback для отримання мему"""
    await send_meme(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_like_content(callback_query: CallbackQuery):
    """Обробка лайка контенту"""
    user_id = callback_query.from_user.id
    
    # Нарахування балів
    try:
        from database import update_user_points
        await update_user_points(user_id, settings.POINTS_FOR_REACTION, "лайк контенту")
    except:
        pass  # Ігноруємо помилки БД
    
    await callback_query.answer(f"{EMOJI['like']} Дякую за оцінку! +{settings.POINTS_FOR_REACTION} балів")

async def callback_dislike_content(callback_query: CallbackQuery):
    """Обробка дизлайка контенту"""
    user_id = callback_query.from_user.id
    
    # Нарахування балів
    try:
        from database import update_user_points
        await update_user_points(user_id, 1, "дизлайк контенту")
    except:
        pass  # Ігноруємо помилки БД
    
    await callback_query.answer(f"{EMOJI['dislike']} Дякую за відгук! +1 бал")

async def callback_submit_instructions(callback_query: CallbackQuery):
    """Інструкції по поданні контенту"""
    content_type = "анекдот" if "joke" in callback_query.data else "мем"
    
    if "joke" in callback_query.data:
        instructions = (
            f"{EMOJI['brain']} <b>Як надіслати анекдот:</b>\n\n"
            f"1. Напиши <code>/submit</code> і одразу текст анекдоту\n"
            f"2. Максимум {settings.MAX_JOKE_LENGTH} символів\n"
            f"3. Анекдот має бути українською мовою\n"
            f"4. Без мату та образ\n\n"
            f"{EMOJI['star']} <b>Приклад:</b>\n"
            f"<code>/submit Чому програмісти люблять природу? Бо в ній немає багів! {EMOJI['laugh']}</code>"
        )
    else:
        instructions = (
            f"{EMOJI['laugh']} <b>Як надіслати мем:</b>\n\n"
            f"1. Прикріпи картинку до повідомлення\n"
            f"2. Додай підпис до картинки\n"
            f"3. Максимум {settings.MAX_MEME_CAPTION_LENGTH} символів у підписі\n"
            f"4. Мем має бути смішним та відповідати правилам\n\n"
            f"{EMOJI['star']} <b>Підпис - обов'язковий!</b>"
        )
    
    await callback_query.message.edit_text(instructions)
    await callback_query.answer()

def register_content_handlers(dp: Dispatcher):
    """Реєстрація хендлерів контенту"""
    
    # Команди
    dp.message.register(cmd_anekdot, Command("anekdot"))
    dp.message.register(cmd_meme, Command("meme"))
    dp.message.register(cmd_submit, Command("submit"))
    
    # Обробка фото
    dp.message.register(handle_photo_submission, F.photo)
    
    # Callback запити
    dp.callback_query.register(callback_get_joke, F.data == "get_joke")
    dp.callback_query.register(callback_get_meme, F.data == "get_meme")
    dp.callback_query.register(callback_like_content, F.data.in_(["like_joke", "like_meme"]))
    dp.callback_query.register(callback_dislike_content, F.data.in_(["dislike_joke", "dislike_meme"]))
    dp.callback_query.register(callback_submit_instructions, F.data.in_(["how_submit_joke", "how_submit_meme"]))
    dp.callback_query.register(callback_submit_instructions, F.data.in_(["submit_joke", "submit_meme"]))