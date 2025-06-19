#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНІ ХЕНДЛЕРИ КОНТЕНТУ З ГЕЙМІФІКАЦІЄЮ 🧠😂🔥
"""

import logging
import random
from datetime import datetime
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
)

logger = logging.getLogger(__name__)

# Fallback налаштування
try:
    from config.settings import settings, EMOJI
    POINTS_FOR_VIEW = getattr(settings, 'POINTS_FOR_VIEW', 1)
    POINTS_FOR_REACTION = getattr(settings, 'POINTS_FOR_REACTION', 5)
    POINTS_FOR_SUBMISSION = getattr(settings, 'POINTS_FOR_SUBMISSION', 10)
except ImportError:
    import os
    POINTS_FOR_VIEW = int(os.getenv("POINTS_FOR_VIEW", "1"))
    POINTS_FOR_REACTION = int(os.getenv("POINTS_FOR_REACTION", "5"))
    POINTS_FOR_SUBMISSION = int(os.getenv("POINTS_FOR_SUBMISSION", "10"))
    
    EMOJI = {
        "brain": "🧠", "laugh": "😂", "fire": "🔥", "star": "⭐",
        "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
        "crown": "👑", "rocket": "🚀", "vs": "⚔️", "calendar": "📅",
        "thumbs_up": "👍", "thumbs_down": "👎", "heart": "❤️"
    }

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

def get_content_keyboard(content_id: int, content_type: str = "joke") -> InlineKeyboardMarkup:
    """Створити клавіатуру для контенту"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI.get('thumbs_up', '👍')} Подобається (+{POINTS_FOR_REACTION})",
                callback_data=f"like_{content_type}_{content_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI.get('thumbs_down', '👎')} Не подобається (+{POINTS_FOR_REACTION})",
                callback_data=f"dislike_{content_type}_{content_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI.get('rocket', '🚀')} Поділитися",
                callback_data=f"share_{content_type}_{content_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI.get('fire', '🔥')} Ще один!",
                callback_data=f"get_{content_type}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI.get('vs', '⚔️')} Дуель з цим жартом",
                callback_data=f"duel_with_{content_id}"
            )
        ]
    ])

def get_content_submission_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура для подачі контенту"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{EMOJI.get('laugh', '😂')} Надіслати жарт (+{POINTS_FOR_SUBMISSION})",
                callback_data="submit_joke"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI.get('fire', '🔥')} Надіслати мем (+{POINTS_FOR_SUBMISSION})",
                callback_data="submit_meme"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI.get('info', 'ℹ️')} Як це працює?",
                callback_data="submission_help"
            )
        ]
    ])

async def award_points(user_id: int, points: int, reason: str) -> bool:
    """Нарахувати бали користувачу"""
    try:
        from database import update_user_points
        
        result = await update_user_points(user_id, points, reason)
        if result:
            logger.info(f"💰 Користувач {user_id}: +{points} балів за {reason}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"❌ Помилка нарахування балів {user_id}: {e}")
        return False

async def record_content_interaction(user_id: int, content_id: int, action: str) -> bool:
    """Записати взаємодію з контентом"""
    try:
        from database import add_content_rating
        
        result = await add_content_rating(
            user_id=user_id,
            content_id=content_id,
            action_type=action,
            points_awarded=POINTS_FOR_REACTION if action in ['like', 'dislike'] else 0
        )
        
        return result is not None
        
    except Exception as e:
        logger.error(f"❌ Помилка запису взаємодії: {e}")
        return False

# ===== КОМАНДИ КОНТЕНТУ =====

async def cmd_meme(message: Message):
    """Команда /meme - отримати випадковий мем"""
    await send_random_content(message, "MEME")

async def cmd_anekdot(message: Message):
    """Команда /anekdot - отримати випадковий анекдот"""
    await send_random_content(message, "JOKE")

async def send_random_content(message: Message, content_type: str = "JOKE"):
    """Надіслати випадковий контент"""
    user_id = message.from_user.id
    
    try:
        from database import get_random_approved_content
        
        # Отримати контент
        content = await get_random_approved_content(content_type=content_type, user_id=user_id)
        
        if not content:
            await message.answer(
                f"{EMOJI.get('warning', '⚠️')} На жаль, поки немає {'мемів' if content_type == 'MEME' else 'анекдотів'}.\n\n"
                f"Будьте першим хто додасть контент! /submit"
            )
            return
        
        # Нарахувати бали за перегляд
        points_awarded = await award_points(user_id, POINTS_FOR_VIEW, "перегляд контенту")
        
        # Підготувати відповідь
        content_emoji = EMOJI.get('fire', '🔥') if content_type == 'MEME' else EMOJI.get('laugh', '😂')
        
        response_text = f"{content_emoji} <b>{'Мем' if content_type == 'MEME' else 'Анекдот'}:</b>\n\n"
        response_text += f"{content.text}\n\n"
        
        if points_awarded:
            response_text += f"💰 <i>+{POINTS_FOR_VIEW} бал за перегляд!</i>\n"
        
        response_text += f"👁‍🗨 Переглядів: {content.views}\n"
        response_text += f"👍 Лайків: {content.likes} | 👎 Дизлайків: {content.dislikes}"
        
        # Надіслати з клавіатурою
        keyboard = get_content_keyboard(content.id, content_type.lower())
        
        if content.file_id:
            # Якщо є файл (мем-картинка)
            await message.answer_photo(
                photo=content.file_id,
                caption=response_text,
                reply_markup=keyboard
            )
        else:
            # Текстовий контент
            await message.answer(
                text=response_text,
                reply_markup=keyboard
            )
        
        logger.info(f"📝 Користувач {user_id} переглянув {content_type.lower()} #{content.id}")
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання контенту: {e}")
        await message.answer(
            f"{EMOJI.get('warning', '⚠️')} Вибачте, сталася помилка при отриманні {'мема' if content_type == 'MEME' else 'анекдоту'}.\n"
            f"Спробуйте ще раз або зверніться до адміністратора."
        )

async def cmd_submit(message: Message):
    """Команда /submit - подати контент на модерацію"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Користувач"
    
    # Перевірити чи є текст після команди
    command_args = message.text.split(' ', 1)
    
    if len(command_args) > 1:
        # Є текст - додати як анекдот
        content_text = command_args[1].strip()
        await submit_content_text(message, content_text, "JOKE")
    else:
        # Показати меню вибору
        await message.answer(
            f"{EMOJI.get('star', '⭐')} <b>Привіт, {first_name}!</b>\n\n"
            f"Хочете поділитися своїм гумором? Виберіть тип контенту:\n\n"
            f"🎯 <b>За успішну подачу контенту:</b>\n"
            f"• +{POINTS_FOR_SUBMISSION} балів за подачу\n"
            f"• +20 балів якщо схвалять\n"
            f"• +50 балів якщо потрапить в ТОП\n\n"
            f"Що ви хочете надіслати?",
            reply_markup=get_content_submission_keyboard()
        )

async def submit_content_text(message: Message, content_text: str, content_type: str = "JOKE"):
    """Подати текстовий контент"""
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    
    try:
        from database import add_content_for_moderation
        
        # Валідація контенту
        if len(content_text) < 10:
            await message.answer(
                f"{EMOJI.get('warning', '⚠️')} {'Жарт' if content_type == 'JOKE' else 'Мем'} занадто короткий!\n"
                f"Мінімум 10 символів. Спробуйте ще раз."
            )
            return
        
        if len(content_text) > 1000:
            await message.answer(
                f"{EMOJI.get('warning', '⚠️')} {'Жарт' if content_type == 'JOKE' else 'Мем'} занадто довгий!\n"
                f"Максимум 1000 символів. Скоротіть текст."
            )
            return
        
        # Додати контент на модерацію
        content = await add_content_for_moderation(
            author_id=user_id,
            content_text=content_text,
            content_type=content_type
        )
        
        if content:
            # Нарахувати бали за подачу
            points_awarded = await award_points(user_id, POINTS_FOR_SUBMISSION, "подача контенту")
            
            response_text = (
                f"{EMOJI.get('check', '✅')} <b>{'Жарт' if content_type == 'JOKE' else 'Мем'} надіслано на модерацію!</b>\n\n"
                f"📝 <i>Ваш контент:</i>\n{content_text[:100]}{'...' if len(content_text) > 100 else ''}\n\n"
            )
            
            if points_awarded:
                response_text += f"💰 <b>+{POINTS_FOR_SUBMISSION} балів за подачу!</b>\n"
                response_text += f"💎 Додатково +20 балів якщо схвалять\n\n"
            
            response_text += (
                f"⏳ Зараз {'жарт' if content_type == 'JOKE' else 'мем'} розглядає модератор.\n"
                f"Ви отримаєте повідомлення про результат!\n\n"
                f"🚀 Надішліть ще контент щоб збирати більше балів!"
            )
            
            await message.answer(response_text)
            
            # Повідомити адміністратора
            try:
                from config.settings import settings
                admin_id = getattr(settings, 'ADMIN_ID', None)
                
                if admin_id:
                    admin_text = (
                        f"{EMOJI.get('crown', '👑')} <b>Новий контент на модерацію!</b>\n\n"
                        f"👤 Автор: {message.from_user.first_name} (@{username})\n"
                        f"🆔 ID: {user_id}\n"
                        f"📝 Тип: {'Жарт' if content_type == 'JOKE' else 'Мем'}\n\n"
                        f"<i>{content_text}</i>\n\n"
                        f"Використайте /pending для модерації"
                    )
                    
                    from aiogram import Bot
                    bot = message.bot
                    await bot.send_message(admin_id, admin_text)
                    
            except Exception:
                pass  # Не критично
            
            logger.info(f"📤 Користувач {user_id} надіслав {content_type.lower()} на модерацію")
            
        else:
            await message.answer(
                f"{EMOJI.get('cross', '❌')} Помилка при надсиланні {'жарту' if content_type == 'JOKE' else 'мему'}.\n"
                f"Спробуйте ще раз пізніше."
            )
            
    except Exception as e:
        logger.error(f"❌ Помилка подачі контенту: {e}")
        await message.answer(
            f"{EMOJI.get('cross', '❌')} Сталася помилка при надсиланні контенту.\n"
            f"Спробуйте ще раз або зверніться до адміністратора."
        )

# ===== CALLBACK ХЕНДЛЕРИ =====

async def callback_like_content(callback_query: CallbackQuery):
    """Лайк контенту"""
    await handle_content_reaction(callback_query, "like", "подобається")

async def callback_dislike_content(callback_query: CallbackQuery):
    """Дизлайк контенту"""
    await handle_content_reaction(callback_query, "dislike", "не подобається")

async def handle_content_reaction(callback_query: CallbackQuery, action: str, action_text: str):
    """Обробити реакцію на контент"""
    user_id = callback_query.from_user.id
    data_parts = callback_query.data.split('_')
    
    if len(data_parts) != 3:
        await callback_query.answer("❌ Помилка даних", show_alert=True)
        return
    
    content_id = int(data_parts[2])
    
    try:
        # Записати взаємодію
        interaction_recorded = await record_content_interaction(user_id, content_id, action)
        
        if interaction_recorded:
            # Нарахувати бали
            points_awarded = await award_points(user_id, POINTS_FOR_REACTION, f"реакція на контент")
            
            # Оновити статистику контенту
            from database import get_content_by_id
            content = await get_content_by_id(content_id)
            
            if content:
                # Оновити лічильники
                if action == "like":
                    content.likes += 1
                elif action == "dislike":
                    content.dislikes += 1
                
                # Зберегти зміни
                from database import get_db_session
                with get_db_session() as session:
                    session.merge(content)
                    session.commit()
            
            emoji = EMOJI.get('thumbs_up', '👍') if action == 'like' else EMOJI.get('thumbs_down', '👎')
            points_text = f" (+{POINTS_FOR_REACTION} балів)" if points_awarded else ""
            
            await callback_query.answer(
                f"{emoji} {action_text.capitalize()}{points_text}!",
                show_alert=False
            )
            
            logger.info(f"👍 Користувач {user_id} поставив {action} контенту #{content_id}")
        else:
            await callback_query.answer(
                f"⚠️ Ви вже оцінювали цей контент!",
                show_alert=True
            )
        
    except Exception as e:
        logger.error(f"❌ Помилка реакції на контент: {e}")
        await callback_query.answer(
            "❌ Помилка при оцінці контенту",
            show_alert=True
        )

async def callback_share_content(callback_query: CallbackQuery):
    """Поділитися контентом"""
    user_id = callback_query.from_user.id
    data_parts = callback_query.data.split('_')
    
    if len(data_parts) != 3:
        await callback_query.answer("❌ Помилка даних", show_alert=True)
        return
    
    content_id = int(data_parts[2])
    
    try:
        from database import get_content_by_id
        content = await get_content_by_id(content_id)
        
        if content:
            # Створити текст для поділення
            share_text = f"😂 Класний жарт з @BobikFun_bot:\n\n{content.text}"
            
            # Створити інлайн кнопку
            share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📢 Поділитися",
                    url=f"https://t.me/share/url?url={share_text.replace(' ', '%20')}"
                )]
            ])
            
            await callback_query.message.edit_reply_markup(reply_markup=share_keyboard)
            await callback_query.answer("🚀 Контент готовий до поділення!")
            
            # Нарахувати бали автору за поділення
            await award_points(content.author_id, 2, "поділення контенту")
            
        else:
            await callback_query.answer("❌ Контент не знайдено", show_alert=True)
            
    except Exception as e:
        logger.error(f"❌ Помилка поділення контенту: {e}")
        await callback_query.answer("❌ Помилка поділення контенту", show_alert=True)

async def callback_get_more_content(callback_query: CallbackQuery):
    """Отримати ще контент"""
    data_parts = callback_query.data.split('_')
    
    if len(data_parts) != 2:
        await callback_query.answer("❌ Помилка даних", show_alert=True)
        return
    
    content_type = data_parts[1].upper()
    
    # Імітувати повідомлення для отримання нового контенту
    await send_random_content(callback_query.message, content_type)
    await callback_query.answer("🔥 Ось новий контент!")

async def callback_submit_joke(callback_query: CallbackQuery):
    """Callback для подачі жарту"""
    await callback_query.message.answer(
        f"{EMOJI.get('laugh', '😂')} <b>Надішліть свій жарт!</b>\n\n"
        f"Просто напишіть текст жарту в наступному повідомленні.\n\n"
        f"💡 <b>Поради:</b>\n"
        f"• Мінімум 10 символів\n"
        f"• Максимум 1000 символів\n"
        f"• Без образливого контенту\n"
        f"• Оригінальний та смішний\n\n"
        f"💰 +{POINTS_FOR_SUBMISSION} балів за подачу!"
    )
    await callback_query.answer()

async def callback_submit_meme(callback_query: CallbackQuery):
    """Callback для подачі мему"""
    await callback_query.message.answer(
        f"{EMOJI.get('fire', '🔥')} <b>Надішліть свій мем!</b>\n\n"
        f"Ви можете надіслати:\n"
        f"• Картинку з підписом\n"
        f"• Текстовий мем\n"
        f"• GIF з описом\n\n"
        f"💡 <b>Поради:</b>\n"
        f"• Якісний та смішний контент\n"
        f"• Без авторських прав\n"
        f"• Українською мовою\n\n"
        f"💰 +{POINTS_FOR_SUBMISSION} балів за подачу!"
    )
    await callback_query.answer()

async def callback_submission_help(callback_query: CallbackQuery):
    """Допомога по подачі контенту"""
    help_text = (
        f"{EMOJI.get('info', 'ℹ️')} <b>Як працює подача контенту:</b>\n\n"
        f"1️⃣ <b>Надсилання</b>\n"
        f"   • Оберіть тип контенту\n"
        f"   • Надішліть жарт або мем\n"
        f"   • +{POINTS_FOR_SUBMISSION} балів відразу\n\n"
        f"2️⃣ <b>Модерація</b>\n"
        f"   • Адміністратор перевіряє контент\n"
        f"   • Схвалює або відхиляє\n"
        f"   • Ви отримуєте повідомлення\n\n"
        f"3️⃣ <b>Нагороди</b>\n"
        f"   • +20 балів за схвалення\n"
        f"   • +50 балів якщо потрапить в ТОП\n"
        f"   • Ваш контент бачать всі користувачі\n\n"
        f"📋 <b>Правила:</b>\n"
        f"• Тільки якісний та смішний контент\n"
        f"• Українською мовою\n"
        f"• Без образ та нецензурщини\n"
        f"• Оригінальний контент\n\n"
        f"🚀 Чим більше якісного контенту - тим більше балів!"
    )
    
    await callback_query.message.answer(help_text)
    await callback_query.answer()

# ===== ОБРОБКА МЕДІА =====

async def handle_photo_submission(message: Message):
    """Обробка надісланого фото (мем)"""
    if message.caption:
        # Фото з підписом
        content_text = message.caption.strip()
        
        # Валідація
        if len(content_text) < 5:
            await message.answer(
                f"{EMOJI.get('warning', '⚠️')} Додайте опис до мему!\n"
                f"Мінімум 5 символів."
            )
            return
        
        user_id = message.from_user.id
        
        try:
            from database import add_content_for_moderation
            
            # Додати мем з файлом
            content = await add_content_for_moderation(
                author_id=user_id,
                content_text=content_text,
                content_type="MEME",
                file_id=message.photo[-1].file_id  # Найбільший розмір
            )
            
            if content:
                await award_points(user_id, POINTS_FOR_SUBMISSION, "подача мему")
                
                await message.answer(
                    f"{EMOJI.get('check', '✅')} <b>Мем надіслано на модерацію!</b>\n\n"
                    f"💰 +{POINTS_FOR_SUBMISSION} балів за подачу!\n"
                    f"⏳ Чекайте на розгляд модератора."
                )
                
                logger.info(f"📷 Користувач {user_id} надіслав мем з фото")
            else:
                await message.answer(
                    f"{EMOJI.get('cross', '❌')} Помилка при надсиланні мему."
                )
        except Exception as e:
            logger.error(f"❌ Помилка обробки фото: {e}")
            await message.answer(
                f"{EMOJI.get('cross', '❌')} Сталася помилка при обробці мему."
            )
    else:
        await message.answer(
            f"{EMOJI.get('info', 'ℹ️')} Додайте опис до мему в підписі до фото!"
        )

async def handle_text_submission(message: Message):
    """Обробка текстового повідомлення як потенційного контенту"""
    # Перевірити чи це не команда
    if message.text.startswith('/'):
        return
    
    # Перевірити довжину
    if len(message.text) >= 10:
        # Запропонувати додати як жарт
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✅ Так, додати як жарт (+{POINTS_FOR_SUBMISSION})",
                    callback_data=f"confirm_submit_joke_{message.message_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Ні, це просто повідомлення",
                    callback_data="cancel_submit"
                )
            ]
        ])
        
        await message.answer(
            f"{EMOJI.get('star', '⭐')} Це схоже на жарт!\n\n"
            f"Хочете надіслати його на модерацію?\n"
            f"💰 +{POINTS_FOR_SUBMISSION} балів за подачу!",
            reply_markup=keyboard
        )

# ===== РЕЄСТРАЦІЯ ХЕНДЛЕРІВ =====

def register_content_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів контенту"""
    
    # Команди
    dp.message.register(cmd_meme, Command("meme"))
    dp.message.register(cmd_anekdot, Command("anekdot"))
    dp.message.register(cmd_submit, Command("submit"))
    
    # Callback запити
    dp.callback_query.register(callback_like_content, F.data.startswith("like_"))
    dp.callback_query.register(callback_dislike_content, F.data.startswith("dislike_"))
    dp.callback_query.register(callback_share_content, F.data.startswith("share_"))
    dp.callback_query.register(callback_get_more_content, F.data.startswith("get_"))
    
    dp.callback_query.register(callback_submit_joke, F.data == "submit_joke")
    dp.callback_query.register(callback_submit_meme, F.data == "submit_meme")
    dp.callback_query.register(callback_submission_help, F.data == "submission_help")
    
    # Обробка медіа
    dp.message.register(handle_photo_submission, F.photo)
    
    # Обробка тексту (має бути останнім)
    dp.message.register(handle_text_submission, F.text & ~F.text.startswith("/"))
    
    logger.info("✅ Хендлери контенту зареєстровано")