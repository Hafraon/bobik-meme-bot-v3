#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Основні команди бота з інтеграцією адмін-меню 🧠😂🔥
"""

import logging
from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from settings import settings, EMOJI, TEXTS

logger = logging.getLogger(__name__)

async def cmd_start(message: Message):
    """Команда /start з автоматичним адмін-меню"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "друже"
    
    # Створюємо/оновлюємо користувача в БД
    try:
        from database import get_or_create_user
        await get_or_create_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
    except Exception as e:
        logger.warning(f"Не вдалося створити користувача: {e}")
    
    # НОВЕ! Перевіряємо чи це адмін і показуємо адмін-меню
    try:
        from handlers.admin_panel_handlers import auto_show_admin_menu_on_start
        admin_menu_shown = await auto_show_admin_menu_on_start(message)
        
        if admin_menu_shown:
            # Для адміна показуємо скорочене привітання + основне меню
            keyboard = get_main_menu_keyboard()
            await message.answer(
                f"{EMOJI['fire']} Вітаю, {first_name}!\n\n"
                f"Ви в режимі адміністратора з розширеними можливостями.\n"
                f"Використовуйте кнопки меню нижче або основне меню:",
                reply_markup=keyboard
            )
            return
    except ImportError:
        pass  # Адмін-панель поки не доступна
    
    # Звичайне привітання для користувачів
    keyboard = get_main_menu_keyboard()
    
    welcome_text = (
        f"{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} <b>Вітаю, {first_name}!</b>\n\n"
        f"Ласкаво просимо до українського бота мемів та анекдотів!\n\n"
        f"{EMOJI['star']} <b>Що я вмію:</b>\n"
        f"{EMOJI['laugh']} Випадкові меми (+1 бал)\n"
        f"{EMOJI['brain']} Українські анекдоти (+1 бал)\n"
        f"{EMOJI['fire']} Прийом ваших жартів (+{settings.POINTS_FOR_SUBMISSION} балів)\n"
        f"{EMOJI['calendar']} Щоденна розсилка (+{settings.POINTS_FOR_DAILY_ACTIVITY} бали)\n"
        f"{EMOJI['vs']} Дуелі жартів (+{settings.POINTS_FOR_DUEL_WIN} за перемогу)\n\n"
        f"{EMOJI['party']} <b>Збирайте бали, підвищуйте ранг і ставайте легендою гумору!</b>\n\n"
        f"Почніть з кнопок нижче або команди /help"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)
    
    # Логування нового користувача
    logger.info(f"🎉 Користувач {user_id} ({first_name}) запустив бота")

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Головне меню бота"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['laugh']} Мем", callback_data="get_meme"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Анекдот", callback_data="get_joke")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['profile']} Профіль", callback_data="show_profile"),
            InlineKeyboardButton(text=f"{EMOJI['top']} Лідери", callback_data="show_leaderboard")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['calendar']} Щоденна розсилка", callback_data="toggle_daily"),
            InlineKeyboardButton(text=f"{EMOJI['fire']} Надіслати жарт", callback_data="submit_content")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI['vs']} Дуель", callback_data="start_duel"),
            InlineKeyboardButton(text=f"{EMOJI['help']} Допомога", callback_data="show_help")
        ]
    ])

async def cmd_help(message: Message):
    """Команда /help"""
    help_text = (
        f"{EMOJI['help']} <b>ДОВІДКА ПО БОТУ</b>\n\n"
        f"{EMOJI['brain']} <b>ОСНОВНІ КОМАНДИ:</b>\n"
        f"• /meme - отримати випадковий мем (+1 бал)\n"
        f"• /anekdot - отримати український анекдот (+1 бал)\n"
        f"• /submit - надіслати свій мем або анекдот (+{settings.POINTS_FOR_SUBMISSION} балів)\n"
        f"• /daily - підписатися на щоденну розсилку\n\n"
        f"{EMOJI['fire']} <b>ГЕЙМІФІКАЦІЯ:</b>\n"
        f"• /profile - переглянути свій профіль та бали\n"
        f"• /top - таблиця лідерів\n"
        f"• /duel - започаткувати дуель жартів\n\n"
        f"{EMOJI['star']} <b>СИСТЕМА БАЛІВ:</b>\n"
        f"• +1 бал - за перегляд контенту\n"
        f"• +{settings.POINTS_FOR_REACTION} балів - за лайк мему/анекдоту\n"
        f"• +{settings.POINTS_FOR_SUBMISSION} балів - за надісланий жарт\n"
        f"• +{settings.POINTS_FOR_APPROVAL} балів - якщо жарт схвалено\n"
        f"• +{settings.POINTS_FOR_DUEL_WIN} балів - за перемогу в дуелі\n"
        f"• +1 бал автору - за кожен лайк його контенту (макс 10/день)\n\n"
        f"{EMOJI['crown']} <b>РАНГИ:</b>\n"
        f"🤡 Новачок → 😄 Сміхун → 😂 Гуморист → 🎭 Комік\n"
        f"👑 Мастер Рофлу → 🏆 Король Гумору → 🌟 Легенда Мемів → 🚀 Геній\n\n"
        f"{EMOJI['rocket']} Дякуємо за використання бота!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EMOJI['fire']} Головне меню", callback_data="show_main_menu"),
            InlineKeyboardButton(text=f"{EMOJI['brain']} Почати", callback_data="get_joke")
        ]
    ])
    
    await message.answer(help_text, reply_markup=keyboard)

async def cmd_stats(message: Message):
    """Команда /stats - загальна статистика бота"""
    try:
        from database import get_db_session
        
        with get_db_session() as session:
            from database.models import User, Content, Rating
            
            # Загальна статистика
            total_users = session.query(User).count()
            total_content = session.query(Content).filter(Content.status == "approved").count()
            total_ratings = session.query(Rating).count()
            
            # Статистика сьогодні
            today = datetime.utcnow().date()
            today_ratings = session.query(Rating).filter(
                Rating.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
        
        stats_text = (
            f"{EMOJI['stats']} <b>СТАТИСТИКА БОТА</b>\n\n"
            f"👥 Користувачів: {total_users}\n"
            f"📝 Жартів схвалено: {total_content}\n"
            f"💖 Всього оцінок: {total_ratings}\n"
            f"🔥 Оцінок сьогодні: {today_ratings}\n\n"
            f"⏰ Оновлено: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        )
        
        await message.answer(stats_text)
        
    except Exception as e:
        logger.error(f"Помилка статистики: {e}")
        await message.answer(
            f"{EMOJI['stats']} <b>СТАТИСТИКА БОТА</b>\n\n"
            f"🔄 Завантажується...\n"
            f"Спробуйте пізніше"
        )

# ===== CALLBACK ОБРОБНИКИ =====

async def callback_get_meme(callback_query: CallbackQuery):
    """Callback для отримання мему"""
    from handlers.content_handlers import send_personalized_meme
    await send_personalized_meme(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_get_joke(callback_query: CallbackQuery):
    """Callback для отримання анекдоту"""
    from handlers.content_handlers import send_personalized_joke
    await send_personalized_joke(callback_query.message, from_callback=True)
    await callback_query.answer()

async def callback_show_profile(callback_query: CallbackQuery):
    """Callback для показу профілю"""
    try:
        from handlers.gamification_handlers import show_profile
        await show_profile(callback_query.message, callback_query.from_user.id)
    except ImportError:
        await callback_query.answer("Функція профілю тимчасово недоступна")
    await callback_query.answer()

async def callback_show_leaderboard(callback_query: CallbackQuery):
    """Callback для показу таблиці лідерів"""
    try:
        from handlers.gamification_handlers import show_leaderboard
        await show_leaderboard(callback_query.message)
    except ImportError:
        await callback_query.answer("Таблиця лідерів тимчасово недоступна")
    await callback_query.answer()

async def callback_toggle_daily(callback_query: CallbackQuery):
    """Callback для перемикання щоденної розсилки"""
    try:
        from handlers.gamification_handlers import toggle_daily_subscription
        await toggle_daily_subscription(callback_query.message, callback_query.from_user.id)
    except ImportError:
        await callback_query.answer("Щоденна розсилка тимчасово недоступна")
    await callback_query.answer()

async def callback_submit_content(callback_query: CallbackQuery):
    """Callback для початку подачі контенту"""
    await callback_query.message.answer(
        f"{EMOJI['fire']} <b>Як надіслати свій контент:</b>\n\n"
        f"{EMOJI['brain']} <b>Для анекдоту:</b>\n"
        f"Напиши /submit і одразу текст анекдоту\n\n"
        f"{EMOJI['laugh']} <b>Для мему:</b>\n"
        f"Надішли картинку з підписом\n\n"
        f"{EMOJI['star']} <b>Приклад:</b>\n"
        f"<code>/submit Чому програмісти п'ють каву? Бо без неї код не компілюється! {EMOJI['brain']}</code>\n\n"
        f"💰 <b>Нагороди:</b>\n"
        f"• +{settings.POINTS_FOR_SUBMISSION} балів за подачу\n"
        f"• +{settings.POINTS_FOR_APPROVAL} балів за схвалення\n"
        f"• +1 бал за кожен лайк від інших користувачів!"
    )
    await callback_query.answer()

async def callback_start_duel(callback_query: CallbackQuery):
    """Callback для початку дуелі"""
    try:
        from handlers.duel_handlers import start_duel
        await start_duel(callback_query.message, callback_query.from_user.id)
    except ImportError:
        await callback_query.answer("Дуелі тимчасово недоступні")
    await callback_query.answer()

async def callback_show_help(callback_query: CallbackQuery):
    """Callback для показу допомоги"""
    await cmd_help(callback_query.message)
    await callback_query.answer()

async def callback_show_main_menu(callback_query: CallbackQuery):
    """Callback для показу головного меню"""
    keyboard = get_main_menu_keyboard()
    
    await callback_query.message.edit_text(
        f"{EMOJI['fire']} <b>ГОЛОВНЕ МЕНЮ</b>\n\n"
        f"Оберіть дію:",
        reply_markup=keyboard
    )
    await callback_query.answer()

def register_basic_handlers(dp: Dispatcher):
    """Реєстрація основних хендлерів"""
    
    # Команди
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_stats, Command("stats"))
    
    # Callback запити
    dp.callback_query.register(callback_get_meme, F.data == "get_meme")
    dp.callback_query.register(callback_get_joke, F.data == "get_joke")
    dp.callback_query.register(callback_show_profile, F.data == "show_profile")
    dp.callback_query.register(callback_show_leaderboard, F.data == "show_leaderboard")
    dp.callback_query.register(callback_toggle_daily, F.data == "toggle_daily")
    dp.callback_query.register(callback_submit_content, F.data == "submit_content")
    dp.callback_query.register(callback_start_duel, F.data == "start_duel")
    dp.callback_query.register(callback_show_help, F.data == "show_help")
    dp.callback_query.register(callback_show_main_menu, F.data == "show_main_menu")
    
    logger.info("🔥 Основні хендлери зареєстровано!")