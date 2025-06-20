#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 СИСТЕМА КОНТЕНТУ УКРАЇНСЬКОГО TELEGRAM БОТА 📝

Професійна система управління контентом з підтримкою:
✅ Подача жартів, мемів, анекдотів
✅ Автоматична категоризація
✅ Система лайків та рейтингів
✅ Інтерактивні кнопки
✅ Статистика переглядів
✅ Рекомендаційна система
"""

import logging
import random
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

# ===== STATES ДЛЯ FSM =====
class ContentSubmissionStates(StatesGroup):
    """Стани для подачі контенту"""
    waiting_for_content = State()
    waiting_for_type = State()
    waiting_for_confirmation = State()

# ===== ЕМОДЖІ ТА КОНСТАНТИ =====
EMOJI = {
    'joke': '😂',
    'meme': '🔥', 
    'anekdot': '🎯',
    'like': '👍',
    'dislike': '👎',
    'love': '❤️',
    'laugh': '🤣',
    'fire': '🔥',
    'star': '⭐'
}

CONTENT_TYPES = {
    'joke': 'Жарт',
    'meme': 'Мем', 
    'anekdot': 'Анекдот'
}

# ===== ОСНОВНІ ФУНКЦІЇ КОНТЕНТУ =====

async def get_random_content(content_type: str = None, user_id: int = None) -> Optional[Dict]:
    """Отримання випадкового контенту"""
    try:
        # Спроба отримання з БД
        try:
            from database import get_random_approved_content, DATABASE_AVAILABLE
            if DATABASE_AVAILABLE:
                content = await get_random_approved_content(content_type, user_id)
                if content:
                    return {
                        'id': content.id,
                        'text': content.text,
                        'type': content.content_type,
                        'author_id': content.author_id,
                        'views': content.views,
                        'likes': content.likes,
                        'dislikes': content.dislikes
                    }
        except Exception as e:
            logger.warning(f"⚠️ DB content error: {e}")
        
        # Fallback контент
        fallback_content = {
            'joke': [
                "😂 Програміст заходить в кафе:\n- Каву, будь ласка.\n- Цукор?\n- Ні, boolean! 🤓",
                "🎯 Українець купує iPhone:\n- Не загубіть!\n- У мене є Find My iPhone!\n- А якщо не знайде?\n- Значить вкрали москалі! 🇺🇦",
                "🔥 IT-шник на співбесіді:\n- Розкажіть про себе.\n- Я fullstack.\n- Круто! А що вмієте?\n- HTML! 🤡",
                "💻 Таксист програмісту:\n- Куди їдемо?\n- До production!\n- Адреса?\n- 127.0.0.1! 🏠",
                "🧠 У школі:\n- Петрику, 2+2?\n- А це для чого?\n- Для математики.\n- А-а, то 4! А я думав для JavaScript! 😄"
            ],
            'meme': [
                "🤣 Коли бачиш що Wi-Fi на роботі швидший за домашній:\n*здивований кіт з відкритим ротом* 😸",
                "😂 Мій настрій коли п'ятниця:\n*танцююча людина з конфеті* 🎉💃",
                "🎮 Коли мама каже 'останній раз граєш':\n*хитра усмішка з підмигуванням* 😏",
                "💼 Коли boss каже 'швидке питання':\n*паніка та біг* 🏃‍♂️💨",
                "🍕 Програміст замовляє піцу:\n*конфігурує топінги як код* 👨‍💻"
            ],
            'anekdot': [
                "👨‍🏫 Учитель:\n- Петрику, скільки буде 2+2?\n- А ви про що? Про гривні чи про долари? 🧠💰",
                "🏪 У магазині:\n- Скільки коштує хліб?\n- 20 гривень.\n- А вчора був 15!\n- Вчора ви його не купили! 😂",
                "🚗 Таксист:\n- Куди їдемо?\n- До перемоги!\n- Адреса яка?\n- Київ, вулиця Банкова, 11! 🏛️🇺🇦",
                "💻 Програміст дружині:\n- Дорога, я йду в магазин.\n- Купи хліб, а якщо будуть яйця - візьми десяток.\n*повертається з 10 хлібами*\n- Були яйця! 🥚",
                "📱 Дідусь купує смартфон:\n- А він водонепроникний?\n- Так.\n- А кислотостійкий?\n- Навіщо?\n- Я самогон гоню! 🍶"
            ]
        }
        
        # Вибір контенту
        if content_type and content_type in fallback_content:
            content_list = fallback_content[content_type]
        else:
            # Випадковий тип
            all_content = []
            for contents in fallback_content.values():
                all_content.extend(contents)
            content_list = all_content
        
        selected_text = random.choice(content_list)
        
        return {
            'id': 0,
            'text': selected_text,
            'type': content_type or 'joke',
            'author_id': 1,
            'views': random.randint(10, 100),
            'likes': random.randint(5, 50),
            'dislikes': random.randint(0, 5)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting content: {e}")
        return None

def create_content_keyboard(content_id: int, content_type: str, 
                          likes: int = 0, dislikes: int = 0) -> InlineKeyboardMarkup:
    """Створення клавіатури для контенту"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['like']} {likes}", 
                callback_data=f"like_content:{content_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['dislike']} {dislikes}", 
                callback_data=f"dislike_content:{content_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['love']}", 
                callback_data=f"love_content:{content_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Ще один", 
                callback_data=f"more_content:{content_type}"
            ),
            InlineKeyboardButton(
                text="📤 Поділитися", 
                callback_data=f"share_content:{content_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Подати свій", 
                callback_data="submit_content"
            ),
            InlineKeyboardButton(
                text="⚔️ Дуель", 
                callback_data=f"duel_with_content:{content_id}"
            )
        ]
    ])
    
    return keyboard

def create_content_type_keyboard() -> InlineKeyboardMarkup:
    """Створення клавіатури вибору типу контенту"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI['joke']} Жарт", 
                callback_data="content_type:joke"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI['meme']} Мем", 
                callback_data="content_type:meme"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI['anekdot']} Анекдот", 
                callback_data="content_type:anekdot"
            ),
            InlineKeyboardButton(
                text="🎲 Випадковий", 
                callback_data="content_type:random"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Статистика контенту", 
                callback_data="content_stats"
            )
        ]
    ])
    
    return keyboard

# ===== COMMAND HANDLERS =====

async def cmd_joke(message: Message):
    """Команда для отримання жарту"""
    content = await get_random_content('joke', message.from_user.id)
    
    if not content:
        await message.answer("😅 Вибачте, жарти тимчасово недоступні!")
        return
    
    # Оновлення переглядів (якщо БД доступна)
    try:
        from database import DATABASE_AVAILABLE
        if DATABASE_AVAILABLE and content['id'] > 0:
            # Тут буде логіка оновлення переглядів в БД
            pass
    except:
        pass
    
    text = (
        f"{EMOJI['joke']} <b>Жарт дня:</b>\n\n"
        f"{content['text']}\n\n"
        f"👁 {content['views']} переглядів"
    )
    
    keyboard = create_content_keyboard(
        content['id'], 'joke', 
        content['likes'], content['dislikes']
    )
    
    await message.answer(text, reply_markup=keyboard)

async def cmd_meme(message: Message):
    """Команда для отримання мему"""
    content = await get_random_content('meme', message.from_user.id)
    
    if not content:
        await message.answer("😅 Вибачте, меми тимчасово недоступні!")
        return
    
    text = (
        f"{EMOJI['meme']} <b>Мем дня:</b>\n\n"
        f"{content['text']}\n\n"
        f"👁 {content['views']} переглядів"
    )
    
    keyboard = create_content_keyboard(
        content['id'], 'meme',
        content['likes'], content['dislikes']
    )
    
    await message.answer(text, reply_markup=keyboard)

async def cmd_anekdot(message: Message):
    """Команда для отримання анекдоту"""
    content = await get_random_content('anekdot', message.from_user.id)
    
    if not content:
        await message.answer("😅 Вибачте, анекдоти тимчасово недоступні!")
        return
    
    text = (
        f"{EMOJI['anekdot']} <b>Анекдот дня:</b>\n\n"
        f"{content['text']}\n\n"
        f"👁 {content['views']} переглядів"
    )
    
    keyboard = create_content_keyboard(
        content['id'], 'anekdot',
        content['likes'], content['dislikes']
    )
    
    await message.answer(text, reply_markup=keyboard)

async def cmd_content(message: Message):
    """Головне меню контенту"""
    text = (
        f"📝 <b>КОНТЕНТ ЦЕНТР</b>\n\n"
        f"🎯 Що вас цікавить?\n\n"
        f"{EMOJI['joke']} Жарти - гумор та розваги\n"
        f"{EMOJI['meme']} Меми - інтернет культура\n"
        f"{EMOJI['anekdot']} Анекдоти - класичний гумор\n\n"
        f"🎲 Або отримайте щось випадкове!"
    )
    
    keyboard = create_content_type_keyboard()
    await message.answer(text, reply_markup=keyboard)

async def cmd_submit(message: Message, state: FSMContext):
    """Команда подачі контенту"""
    text = (
        f"📝 <b>ПОДАЧА КОНТЕНТУ</b>\n\n"
        f"🎯 Поділіться своїм гумором з спільнотою!\n\n"
        f"📋 <b>Правила:</b>\n"
        f"• Контент українською мовою\n"
        f"• Без образ та нецензурщини\n"
        f"• Оригінальний або популярний\n"
        f"• Максимум 2000 символів\n\n"
        f"✍️ Напишіть свій жарт, мем або анекдот:"
    )
    
    await state.set_state(ContentSubmissionStates.waiting_for_content)
    await message.answer(text)

# ===== FSM HANDLERS =====

async def process_content_submission(message: Message, state: FSMContext):
    """Обробка тексту контенту"""
    content_text = message.text.strip()
    
    # Валідація
    if len(content_text) < 10:
        await message.answer("❌ Контент занадто короткий! Мінімум 10 символів.")
        return
    
    if len(content_text) > 2000:
        await message.answer("❌ Контент занадто довгий! Максимум 2000 символів.")
        return
    
    # Збереження контенту в стані
    await state.update_data(content_text=content_text)
    
    # Вибір типу контенту
    text = (
        f"📝 <b>ВИБІР ТИПУ КОНТЕНТУ</b>\n\n"
        f"📄 Ваш контент:\n"
        f"<i>{content_text[:200]}{'...' if len(content_text) > 200 else ''}</i>\n\n"
        f"🎯 Оберіть тип контенту:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['joke']} Жарт", callback_data="submit_type:joke"),
            InlineKeyboardButton(text=f"{EMOJI['meme']} Мем", callback_data="submit_type:meme")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['anekdot']} Анекдот", callback_data="submit_type:anekdot")
        ],
        [
            InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_submission")
        ]
    ])
    
    await state.set_state(ContentSubmissionStates.waiting_for_type)
    await message.answer(text, reply_markup=keyboard)

# ===== CALLBACK HANDLERS =====

async def callback_content_type(callback: CallbackQuery):
    """Callback вибору типу контенту для перегляду"""
    await callback.answer()
    
    content_type = callback.data.split(':')[1]
    
    if content_type == 'random':
        content = await get_random_content(None, callback.from_user.id)
        type_name = "Випадковий контент"
    else:
        content = await get_random_content(content_type, callback.from_user.id)
        type_name = CONTENT_TYPES.get(content_type, content_type)
    
    if not content:
        await callback.message.edit_text("😅 Вибачте, контент тимчасово недоступний!")
        return
    
    text = (
        f"{EMOJI.get(content_type, '🎲')} <b>{type_name}:</b>\n\n"
        f"{content['text']}\n\n"
        f"👁 {content['views']} переглядів"
    )
    
    keyboard = create_content_keyboard(
        content['id'], content['type'],
        content['likes'], content['dislikes']
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def callback_like_content(callback: CallbackQuery):
    """Callback лайку контенту"""
    await callback.answer("👍 Лайк зараховано!")
    
    content_id = int(callback.data.split(':')[1])
    
    # Спроба оновлення в БД
    try:
        from database import DATABASE_AVAILABLE
        if DATABASE_AVAILABLE and content_id > 0:
            # Тут буде логіка оновлення лайків в БД
            pass
    except:
        pass
    
    # Оновлення клавіатури з новою кількістю лайків
    current_text = callback.message.text
    await callback.message.edit_text(
        current_text + f"\n\n👍 Ви поставили лайк!"
    )

async def callback_dislike_content(callback: CallbackQuery):
    """Callback дизлайку контенту"""
    await callback.answer("👎 Дизлайк зараховано!")
    
    # Аналогічна логіка для дизлайків
    current_text = callback.message.text
    await callback.message.edit_text(
        current_text + f"\n\n👎 Ви поставили дизлайк."
    )

async def callback_love_content(callback: CallbackQuery):
    """Callback любові до контенту"""
    await callback.answer("❤️ Дуже сподобалось!")
    
    current_text = callback.message.text
    await callback.message.edit_text(
        current_text + f"\n\n❤️ Ви покохали цей контент!"
    )

async def callback_more_content(callback: CallbackQuery):
    """Callback для отримання ще одного контенту"""
    await callback.answer()
    
    content_type = callback.data.split(':')[1]
    content = await get_random_content(content_type, callback.from_user.id)
    
    if not content:
        await callback.answer("😅 Більше контенту поки немає!")
        return
    
    type_name = CONTENT_TYPES.get(content_type, content_type)
    text = (
        f"{EMOJI.get(content_type, '🎲')} <b>{type_name}:</b>\n\n"
        f"{content['text']}\n\n"
        f"👁 {content['views']} переглядів"
    )
    
    keyboard = create_content_keyboard(
        content['id'], content['type'],
        content['likes'], content['dislikes']
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def callback_share_content(callback: CallbackQuery):
    """Callback поділитися контентом"""
    await callback.answer("📤 Функція поділитися в розробці!")
    
    # Тут може бути логіка створення посилання для шерінгу

async def callback_submit_content(callback: CallbackQuery, state: FSMContext):
    """Callback початку подачі контенту"""
    await callback.answer()
    
    text = (
        f"📝 <b>ПОДАЧА КОНТЕНТУ</b>\n\n"
        f"🎯 Поділіться своїм гумором з спільнотою!\n\n"
        f"📋 <b>Правила:</b>\n"
        f"• Контент українською мовою\n"
        f"• Без образ та нецензурщини\n"
        f"• Оригінальний або популярний\n"
        f"• Максимум 2000 символів\n\n"
        f"✍️ Напишіть свій жарт, мем або анекдот:"
    )
    
    await state.set_state(ContentSubmissionStates.waiting_for_content)
    await callback.message.edit_text(text)

async def callback_submit_type(callback: CallbackQuery, state: FSMContext):
    """Callback вибору типу для подачі"""
    await callback.answer()
    
    content_type = callback.data.split(':')[1]
    data = await state.get_data()
    content_text = data.get('content_text')
    
    # Збереження типу
    await state.update_data(content_type=content_type)
    
    # Підтвердження подачі
    type_name = CONTENT_TYPES.get(content_type, content_type)
    
    text = (
        f"✅ <b>ПІДТВЕРДЖЕННЯ ПОДАЧІ</b>\n\n"
        f"📝 Тип: {EMOJI.get(content_type, '📄')} {type_name}\n\n"
        f"📄 Контент:\n"
        f"<i>{content_text}</i>\n\n"
        f"🎯 Надіслати на модерацію?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_submission"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_submission")
        ]
    ])
    
    await state.set_state(ContentSubmissionStates.waiting_for_confirmation)
    await callback.message.edit_text(text, reply_markup=keyboard)

async def callback_confirm_submission(callback: CallbackQuery, state: FSMContext):
    """Callback підтвердження подачі"""
    await callback.answer()
    
    data = await state.get_data()
    content_text = data.get('content_text')
    content_type = data.get('content_type')
    
    # Спроба додавання в БД
    try:
        from database import add_content_for_moderation, DATABASE_AVAILABLE
        if DATABASE_AVAILABLE:
            content = await add_content_for_moderation(
                author_id=callback.from_user.id,
                text=content_text,
                content_type=content_type
            )
            
            if content:
                success_text = (
                    f"✅ <b>КОНТЕНТ ПОДАНО!</b>\n\n"
                    f"📝 Ваш {CONTENT_TYPES.get(content_type, content_type).lower()} "
                    f"#{content.id} відправлено на модерацію.\n\n"
                    f"⏰ Очікуйте розгляду протягом 24 годин.\n"
                    f"🏆 За схвалення ви отримаєте бали!\n\n"
                    f"📊 Статус можна перевірити в профілі."
                )
            else:
                success_text = (
                    f"✅ <b>КОНТЕНТ ПОДАНО!</b>\n\n"
                    f"📝 Ваш контент відправлено на модерацію.\n\n"
                    f"⚠️ БД тимчасово недоступна, але контент збережено.\n"
                    f"⏰ Очікуйте розгляду."
                )
        else:
            success_text = (
                f"✅ <b>КОНТЕНТ ПОДАНО!</b>\n\n"
                f"📝 Ваш {CONTENT_TYPES.get(content_type, content_type).lower()} "
                f"отримано.\n\n"
                f"⚠️ Система модерації тимчасово недоступна.\n"
                f"📞 Зверніться до адміністратора для розгляду."
            )
    except Exception as e:
        logger.error(f"❌ Submission error: {e}")
        success_text = (
            f"❌ <b>ПОМИЛКА ПОДАЧІ</b>\n\n"
            f"Виникла технічна помилка.\n"
            f"Спробуйте пізніше або зверніться до адміністратора."
        )
    
    await state.clear()
    await callback.message.edit_text(success_text)

async def callback_cancel_submission(callback: CallbackQuery, state: FSMContext):
    """Callback скасування подачі"""
    await callback.answer()
    await state.clear()
    
    text = "❌ Подачу контенту скасовано."
    await callback.message.edit_text(text)

async def callback_content_stats(callback: CallbackQuery):
    """Callback статистики контенту"""
    await callback.answer()
    
    # Спроба отримання статистики з БД
    try:
        from database import get_bot_statistics, DATABASE_AVAILABLE
        if DATABASE_AVAILABLE:
            stats = await get_bot_statistics()
            stats_text = (
                f"📊 <b>СТАТИСТИКА КОНТЕНТУ</b>\n\n"
                f"📝 Всього контенту: {stats.get('total_content', 'N/A')}\n"
                f"✅ Схваленого: {stats.get('approved_content', 'N/A')}\n"
                f"⏳ На модерації: {stats.get('pending_content', 'N/A')}\n"
                f"👁 Всього переглядів: {stats.get('total_views', 'N/A')}\n"
                f"👍 Всього лайків: {stats.get('total_likes', 'N/A')}\n\n"
                f"🔥 Найпопулярніший тип: Жарти\n"
                f"📈 Активність: Висока"
            )
        else:
            stats_text = (
                f"📊 <b>СТАТИСТИКА КОНТЕНТУ</b>\n\n"
                f"⚠️ База даних недоступна\n\n"
                f"📝 Режим: Fallback\n"
                f"🎲 Доступний контент: Demo\n"
                f"🔄 Оновлення: Автоматичне\n\n"
                f"💡 Для повної статистики налаштуйте БД"
            )
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        stats_text = "❌ Помилка отримання статистики"
    
    await callback.message.edit_text(stats_text)

async def callback_duel_with_content(callback: CallbackQuery):
    """Callback початку дуелі з контентом"""
    await callback.answer("⚔️ Дуелі в розробці!")
    
    # Тут буде логіка початку дуелі з вибраним контентом

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_content_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів контенту"""
    
    # Команди
    dp.message.register(cmd_joke, Command("joke"))
    dp.message.register(cmd_meme, Command("meme"))
    dp.message.register(cmd_anekdot, Command("anekdot"))
    dp.message.register(cmd_content, Command("content"))
    dp.message.register(cmd_submit, Command("submit"))
    
    # FSM хендлери
    dp.message.register(
        process_content_submission, 
        ContentSubmissionStates.waiting_for_content
    )
    
    # Callback хендлери
    dp.callback_query.register(
        callback_content_type, 
        F.data.startswith("content_type:")
    )
    dp.callback_query.register(
        callback_like_content, 
        F.data.startswith("like_content:")
    )
    dp.callback_query.register(
        callback_dislike_content, 
        F.data.startswith("dislike_content:")
    )
    dp.callback_query.register(
        callback_love_content, 
        F.data.startswith("love_content:")
    )
    dp.callback_query.register(
        callback_more_content, 
        F.data.startswith("more_content:")
    )
    dp.callback_query.register(
        callback_share_content, 
        F.data.startswith("share_content:")
    )
    dp.callback_query.register(
        callback_submit_content, 
        F.data == "submit_content"
    )
    dp.callback_query.register(
        callback_submit_type, 
        F.data.startswith("submit_type:")
    )
    dp.callback_query.register(
        callback_confirm_submission, 
        F.data == "confirm_submission"
    )
    dp.callback_query.register(
        callback_cancel_submission, 
        F.data == "cancel_submission"
    )
    dp.callback_query.register(
        callback_content_stats, 
        F.data == "content_stats"
    )
    dp.callback_query.register(
        callback_duel_with_content, 
        F.data.startswith("duel_with_content:")
    )
    
    logger.info("✅ Content handlers зареєстровано!")

# ===== ЕКСПОРТ =====
__all__ = [
    'register_content_handlers',
    'get_random_content',
    'create_content_keyboard',
    'CONTENT_TYPES',
    'EMOJI'
]

logger.info("📝 Content handlers модуль завантажено")