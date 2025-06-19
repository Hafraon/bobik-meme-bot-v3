#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Персоналізовані хендлери для роботи з контентом 🧠😂🔥
"""

import logging
import random
from datetime import datetime
from typing import Dict, Set, Optional

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

# Глобальне сховище для відстеження показаних анекдотів/мемів (FALLBACK)
# В продакшені це буде в БД через нові функції
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

# ===== НОВІ ФУНКЦІЇ ДЛЯ ПЕРСОНАЛІЗАЦІЇ =====

async def get_personalized_content(user_id: int, content_type: str) -> Optional[dict]:
    """Отримати персоналізований контент (БД + fallback)"""
    try:
        # Спробуємо використати нові персоналізовані функції
        from database import get_recommended_content, record_content_view
        
        # Створюємо/оновлюємо користувача
        await ensure_user_exists(user_id)
        
        # Отримуємо рекомендований контент
        content_obj = await get_recommended_content(user_id, content_type)
        
        if content_obj:
            # Записуємо перегляд
            view_recorded = await record_content_view(user_id, content_obj.id, "command")
            
            return {
                "text": content_obj.text,
                "views": content_obj.views,
                "likes": content_obj.likes,
                "content_id": content_obj.id,
                "is_new": view_recorded,
                "topic": getattr(content_obj, 'topic', None),
                "quality": getattr(content_obj, 'quality_score', 0.8)
            }
    except Exception as e:
        logger.warning(f"Персоналізація недоступна: {e}")
    
    # FALLBACK - використовуємо стару логіку без повторів
    if content_type == "joke":
        joke_index, joke_text = get_random_joke_without_repeat(user_id)
        return {
            "text": joke_text,
            "views": random.randint(50, 500),
            "likes": random.randint(5, 50),
            "content_id": None,
            "is_new": True,
            "topic": "life"
        }
    else:
        meme_index, meme_data = get_random_meme_without_repeat(user_id)
        return {
            "text": meme_data["caption"],
            "views": random.randint(80, 600),
            "likes": random.randint(8, 60),
            "content_id": None,
            "is_new": True,
            "topic": "life"
        }

async def ensure_user_exists(user_id: int):
    """Переконатися що користувач існує в БД"""
    try:
        from database import get_or_create_user
        # Дані користувача будуть отримані з Message пізніше
        await get_or_create_user(user_id)
    except:
        pass  # Ігноруємо якщо БД недоступна

def get_random_joke_without_repeat(user_id: int) -> tuple:
    """Отримання випадкового анекдоту без повторів (FALLBACK)"""
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
    """Отримання випадкового мему без повторів (FALLBACK)"""
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

# ===== ОСНОВНІ КОМАНДИ =====

async def cmd_anekdot(message: Message):
    """Команда /anekdot"""
    await send_personalized_joke(message)

async def cmd_meme(message: Message):
    """Команда /meme"""
    await send_personalized_meme(message)

async def send_personalized_joke(message: Message, from_callback: bool = False):
    """Надсилання персоналізованого анекдоту"""
    user_id = message.from_user.id
    
    try:
        # Створюємо/оновлюємо користувача в БД
        try:
            from database import get_or_create_user
            await get_or_create_user(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
        except:
            pass  # БД може бути недоступна
        
        # Отримуємо персоналізований контент
        content_data = await get_personalized_content(user_id, "joke")
        
        if not content_data:
            await message.answer(f"{EMOJI['cross']} Упс! Анекдоти закінчилися. Спробуй пізніше!")
            return
        
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
        
        # Створюємо розширену клавіатуру
        keyboard_buttons = [
            [
                InlineKeyboardButton(text=f"{EMOJI['like']} Подобається", 
                                   callback_data=f"like_joke_{content_data.get('content_id', 0)}"),
                InlineKeyboardButton(text=f"{EMOJI['dislike']} Не подобається", 
                                   callback_data=f"dislike_joke_{content_data.get('content_id', 0)}")
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['brain']} Ще анекдот", callback_data="get_joke"),
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme")
            ]
        ]
        
        # Додаємо кнопки для персоналізованого контенту
        if content_data.get('content_id'):
            keyboard_buttons.append([
                InlineKeyboardButton(text=f"{EMOJI['fire']} Поділитися", 
                                   callback_data=f"share_joke_{content_data['content_id']}"),
                InlineKeyboardButton(text=f"📊 Топ анекдоти", callback_data="top_jokes")
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text=f"{EMOJI['star']} Надіслати свій", callback_data="submit_joke")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        # Формуємо інформацію про контент
        content_info = []
        
        # Додаємо тематичні емодзі
        if content_data.get('topic'):
            topic_emoji = {
                "programming": "💻", 
                "work": "🏢", 
                "life": "🌍", 
                "family": "👨‍👩‍👧‍👦",
                "education": "🎓"
            }.get(content_data['topic'], "📝")
            content_info.append(f"{topic_emoji}")
        
        content_info.append(f"👁️ {content_data['views']}")
        
        if content_data['likes'] > 0:
            content_info.append(f"❤️ {content_data['likes']}")
        
        # Персональні мітки
        personal_tag = ""
        if not content_data.get('is_new'):
            personal_tag = f" {EMOJI['thinking']} (переглянуто)"
        elif content_data.get('topic') in ['programming', 'work']:
            personal_tag = f" {EMOJI['brain']} (рекомендовано)"
        elif content_data.get('quality', 0) > 0.9:
            personal_tag = f" {EMOJI['star']} (топ якість)"
        
        info_line = " • ".join(content_info) + personal_tag if content_info else personal_tag
        
        response_text = f"{greeting}\n\n{content_data['text']}\n\n{info_line}\n{EMOJI['star']} Сподобався анекдот? Оціни!"
        
        await message.answer(
            response_text,
            reply_markup=keyboard
        )
        
        # Нарахування балів за перегляд
        try:
            from database import update_user_points
            if content_data.get('is_new'):
                await update_user_points(user_id, 1, "перегляд нового анекдоту")
        except:
            pass  # Ігноруємо помилки БД
        
        if not from_callback:
            logger.info(f"🧠 Користувач {user_id} отримав персоналізований анекдот")
            
    except Exception as e:
        logger.error(f"Помилка надсилання анекдоту: {e}")
        await message.answer(f"{EMOJI['cross']} Упс! Сталася помилка. Спробуй ще раз!")

async def send_personalized_meme(message: Message, from_callback: bool = False):
    """Надсилання персоналізованого мему"""
    user_id = message.from_user.id
    
    try:
        # Створюємо/оновлюємо користувача в БД
        try:
            from database import get_or_create_user
            await get_or_create_user(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
        except:
            pass  # БД може бути недоступна
        
        # Отримуємо персоналізований контент
        content_data = await get_personalized_content(user_id, "meme")
        
        if not content_data:
            await message.answer(f"{EMOJI['cross']} Упс! Меми закінчилися. Спробуй пізніше!")
            return
        
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
        
        # Створюємо розширену клавіатуру
        keyboard_buttons = [
            [
                InlineKeyboardButton(text=f"{EMOJI['like']} Подобається", 
                                   callback_data=f"like_meme_{content_data.get('content_id', 0)}"),
                InlineKeyboardButton(text=f"{EMOJI['dislike']} Не подобається", 
                                   callback_data=f"dislike_meme_{content_data.get('content_id', 0)}")
            ],
            [
                InlineKeyboardButton(text=f"{EMOJI['laugh']} Ще мем", callback_data="get_meme"),
                InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
            ]
        ]
        
        # Додаємо кнопки для персоналізованого контенту
        if content_data.get('content_id'):
            keyboard_buttons.append([
                InlineKeyboardButton(text=f"{EMOJI['fire']} Поділитися", 
                                   callback_data=f"share_meme_{content_data['content_id']}"),
                InlineKeyboardButton(text=f"📊 Топ меми", callback_data="top_memes")
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text=f"{EMOJI['star']} Надіслати свій", callback_data="submit_meme")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        # Формуємо інформацію про контент
        content_info = []
        
        # Додаємо тематичні емодзі
        if content_data.get('topic'):
            topic_emoji = {
                "programming": "💻", 
                "work": "🏢", 
                "life": "🌍", 
                "family": "👨‍👩‍👧‍👦"
            }.get(content_data['topic'], "📝")
            content_info.append(f"{topic_emoji}")
        
        content_info.append(f"👁️ {content_data['views']}")
        
        if content_data['likes'] > 0:
            content_info.append(f"❤️ {content_data['likes']}")
        
        # Персональні мітки
        personal_tag = ""
        if not content_data.get('is_new'):
            personal_tag = f" {EMOJI['thinking']} (переглянуто)"
        elif content_data.get('topic') in ['programming', 'work']:
            personal_tag = f" {EMOJI['brain']} (рекомендовано)"
        elif content_data.get('quality', 0) > 0.9:
            personal_tag = f" {EMOJI['star']} (топ якість)"
        
        info_line = " • ".join(content_info) + personal_tag if content_info else personal_tag
        
        response_text = f"{greeting}\n\n{content_data['text']}\n\n{info_line}\n{EMOJI['star']} Сподобався мем? Оціни!"
        
        await message.answer(
            response_text,
            reply_markup=keyboard
        )
        
        # Нарахування балів за перегляд
        try:
            from database import update_user_points
            if content_data.get('is_new'):
                await update_user_points(user_id, 1, "перегляд нового мему")
        except:
            pass  # Ігноруємо помилки БД
        
        if not from_callback:
            logger.info(f"🔥 Користувач {user_id} отримав персоналізований мем")
            
    except Exception as e:
        logger.error(f"Помилка надсилання мему: {e}")
        await message.answer(f"{EMOJI['cross']} Упс! Сталася помилка. Спробуй ще раз!")

# ===== СТАРІ ФУНКЦІЇ ДЛЯ СУМІСНОСТІ =====

async def send_joke(message: Message, from_callback: bool = False):
    """Стара функція для сумісності"""
    await send_personalized_joke(message, from_callback)

async def send_meme(message: Message, from_callback: bool = False):
    """Стара функція для сумісності"""
    await send_personalized_meme(message, from_callback)

# ===== ПОДАЧА КОНТЕНТУ (БЕЗ ЗМІН) =====

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
    await send_personalized_joke(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_get_meme(callback_query: CallbackQuery):
    """Callback для отримання мему"""
    await send_personalized_meme(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_like_content(callback_query: CallbackQuery):
    """Обробка лайка контенту з персоналізацією"""
    user_id = callback_query.from_user.id
    
    # Витягуємо ID контенту з callback_data
    callback_data = callback_query.data
    content_id = None
    
    if "_" in callback_data:
        parts = callback_data.split("_")
        if len(parts) >= 3:
            try:
                content_id = int(parts[2])
            except:
                content_id = None
    
    # Записуємо лайк в БД з нарахуванням балів автору
    try:
        from database import add_content_rating
        if content_id:
            success = await add_content_rating(user_id, content_id, "like", settings.POINTS_FOR_REACTION)
            if success:
                # Аналізуємо поведінку для персоналізації
                try:
                    from database import analyze_user_behavior
                    await analyze_user_behavior(user_id)
                except:
                    pass
                
                await callback_query.answer(f"{EMOJI['like']} Дякую за оцінку! +{settings.POINTS_FOR_REACTION} балів")
            else:
                await callback_query.answer(f"{EMOJI['like']} Ви вже оцінювали цей контент!")
        else:
            # Fallback для контенту без ID
            from database import update_user_points
            await update_user_points(user_id, settings.POINTS_FOR_REACTION, "лайк контенту")
            await callback_query.answer(f"{EMOJI['like']} Дякую за оцінку! +{settings.POINTS_FOR_REACTION} балів")
    except Exception as e:
        logger.error(f"Помилка обробки лайка: {e}")
        await callback_query.answer(f"{EMOJI['like']} Дякую за оцінку!")

async def callback_dislike_content(callback_query: CallbackQuery):
    """Обробка дизлайка контенту"""
    user_id = callback_query.from_user.id
    
    # Витягуємо ID контенту з callback_data
    callback_data = callback_query.data
    content_id = None
    
    if "_" in callback_data:
        parts = callback_data.split("_")
        if len(parts) >= 3:
            try:
                content_id = int(parts[2])
            except:
                content_id = None
    
    # Записуємо дизлайк в БД
    try:
        from database import add_content_rating
        if content_id:
            success = await add_content_rating(user_id, content_id, "dislike", 1)
            if success:
                await callback_query.answer(f"{EMOJI['dislike']} Дякую за відгук! +1 бал")
            else:
                await callback_query.answer(f"{EMOJI['dislike']} Ви вже оцінювали цей контент!")
        else:
            # Fallback
            from database import update_user_points
            await update_user_points(user_id, 1, "дизлайк контенту")
            await callback_query.answer(f"{EMOJI['dislike']} Дякую за відгук! +1 бал")
    except Exception as e:
        logger.error(f"Помилка обробки дизлайка: {e}")
        await callback_query.answer(f"{EMOJI['dislike']} Дякую за відгук!")

async def callback_share_content(callback_query: CallbackQuery):
    """НОВА ФУНКЦІЯ - Поділитися контентом"""
    user_id = callback_query.from_user.id
    
    # Витягуємо ID контенту
    callback_data = callback_query.data
    if "_" in callback_data:
        parts = callback_data.split("_")
        if len(parts) >= 3:
            try:
                content_id = int(parts[2])
                
                # Записуємо поділитися в БД
                from database import add_content_rating, update_user_points
                await add_content_rating(user_id, content_id, "share", 3)
                await update_user_points(user_id, 3, "поділитися контентом")
                
                await callback_query.answer(f"{EMOJI['fire']} Дякую за поширення! +3 бали")
                
                # Надсилаємо інструкції для поділитися
                await callback_query.message.answer(
                    f"{EMOJI['fire']} <b>Поділитися контентом:</b>\n\n"
                    f"Просто перешли це повідомлення друзям!\n"
                    f"Або використай кнопку 'Переслати' 📤"
                )
                
            except Exception as e:
                logger.error(f"Помилка поділитися: {e}")
                await callback_query.answer("Помилка поділитися")

async def callback_top_content(callback_query: CallbackQuery):
    """НОВА ФУНКЦІЯ - Показати топ контент"""
    try:
        content_type = "joke" if "jokes" in callback_query.data else "meme"
        emoji = EMOJI['brain'] if content_type == "joke" else EMOJI['laugh']
        name = "АНЕКДОТИ" if content_type == "joke" else "МЕМИ"
        
        # Спробуємо отримати топ з БД
        try:
            from database import get_trending_content, get_popular_content
            
            trending = await get_trending_content(content_type, 3)
            popular = await get_popular_content(content_type, 3)
            
            response = f"{emoji} <b>ТОП {name}</b>\n\n"
            
            if trending:
                response += f"🔥 <b>Трендові зараз:</b>\n"
                for i, item in enumerate(trending, 1):
                    response += f"{i}. 👁️{item.views} ❤️{item.likes} - {item.text[:50]}...\n"
                response += "\n"
            
            if popular:
                response += f"⭐ <b>Популярні за весь час:</b>\n"
                for i, item in enumerate(popular, 1):
                    response += f"{i}. 👁️{item.views} ❤️{item.likes} - {item.text[:50]}...\n"
            
        except:
            # Fallback якщо БД недоступна
            response = f"{emoji} <b>ТОП {name}</b>\n\n🔄 Статистика оновлюється..."
        
        await callback_query.message.edit_text(
            response,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Назад", 
                                   callback_data="get_joke" if content_type == "joke" else "get_meme")
            ]])
        )
        
    except Exception as e:
        logger.error(f"Помилка топ контенту: {e}")
        await callback_query.answer("Помилка завантаження топу")

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
    
    # Основні callback запити
    dp.callback_query.register(callback_get_joke, F.data == "get_joke")
    dp.callback_query.register(callback_get_meme, F.data == "get_meme")
    
    # Оцінки контенту (старі + нові з ID)
    dp.callback_query.register(callback_like_content, F.data.in_(["like_joke", "like_meme"]))
    dp.callback_query.register(callback_like_content, F.data.startswith("like_"))
    dp.callback_query.register(callback_dislike_content, F.data.in_(["dislike_joke", "dislike_meme"]))
    dp.callback_query.register(callback_dislike_content, F.data.startswith("dislike_"))
    
    # Нові функції
    dp.callback_query.register(callback_share_content, F.data.startswith("share_"))
    dp.callback_query.register(callback_top_content, F.data.in_(["top_jokes", "top_memes"]))
    
    # Інструкції
    dp.callback_query.register(callback_submit_instructions, F.data.in_(["how_submit_joke", "how_submit_meme"]))
    dp.callback_query.register(callback_submit_instructions, F.data.in_(["submit_joke", "submit_meme"]))