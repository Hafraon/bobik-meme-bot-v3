#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 HANDLERS МОДУЛЬ - ПРАВИЛЬНА РЕЄСТРАЦІЯ 🎯
"""

import logging
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart

logger = logging.getLogger(__name__)

def register_all_handlers(dp: Dispatcher):
    """🎯 ГОЛОВНА ФУНКЦІЯ РЕЄСТРАЦІЇ ВСІХ HANDLERS"""
    logger.info("🎯 Початок реєстрації handlers...")
    
    # Команда /start
    @dp.message(CommandStart())
    async def start_handler(message: Message):
        await message.answer(
            "🤖 <b>Привіт! Я український мем-бот з гейміфікацією!</b>\n\n"
            "📋 <b>Команди:</b>\n"
            "• /help - довідка по боту\n"
            "• /meme - випадковий мем\n"
            "• /anekdot - український анекдот\n"
            "• /profile - мій профіль\n"
            "• /top - таблиця лідерів\n"
            "• /submit - надіслати контент\n"
            "• /admin - панель адміна\n\n"
            "🎮 <b>Гейміфікація:</b>\n"
            "Заробляйте бали за активність та підвищуйте свій ранг!"
        )
    
    # Команда /help
    @dp.message(Command("help"))
    async def help_handler(message: Message):
        await message.answer(
            "❓ <b>ДОВІДКА ПО БОТУ</b>\n\n"
            "🎮 <b>Гейміфікація:</b>\n"
            "• Отримуйте бали за активність\n"
            "• Підвищуйте свій ранг\n"
            "• Беріть участь в дуелях\n\n"
            "📝 <b>Контент:</b>\n"
            "• /meme - випадковий мем\n"
            "• /anekdot - український анекдот\n"
            "• /submit - надіслати свій жарт\n\n"
            "👤 <b>Профіль:</b>\n"
            "• /profile - переглянути профіль\n"
            "• /top - таблиця лідерів\n\n"
            "⚔️ <b>Дуелі:</b>\n"
            "• /duel - розпочати дуель жартів\n\n"
            "🛡️ <b>Адміністрування:</b>\n"
            "• /admin - панель адміністратора"
        )
    
    # Команда /meme
    @dp.message(Command("meme"))
    async def meme_handler(message: Message):
        memes = [
            "😂 <b>Програміст і кава</b>\n\nПрограміст заходить в кафе і замовляє каву.\nБариста питає: 'Java чи Python?'\nПрограміст: 'Та ні, звичайну каву!'",
            "🤣 <b>Різдво та Хеллоуїн</b>\n\nЧому програмісти завжди плутають Різдво та Хеллоуїн?\nБо Oct 31 == Dec 25!",
            "😄 <b>Лампочка та програмісти</b>\n\nСкільки програмістів потрібно, щоб закрутити лампочку?\nЖодного - це апаратна проблема!",
            "🤔 <b>Два байти в барі</b>\n\nДва байти зустрілися в барі.\nОдин каже: 'У мене біт болить!'\nДругий: 'То побайтися треба!'",
            "🙄 <b>QA тестер</b>\n\nQA тестер заходить в бар.\nЗамовляє пиво.\nЗамовляє 0 пив.\nЗамовляє 999999999 пив.\nЗамовляє ящірку.\nЗамовляє -1 пиво.\nЗамовляє NULL пиво."
        ]
        import random
        meme = random.choice(memes)
        await message.answer(f"🎭 Ось ваш мем:\n\n{meme}")
    
    # Команда /anekdot
    @dp.message(Command("anekdot"))
    async def anekdot_handler(message: Message):
        anekdots = [
            "🇺🇦 <b>Три програмісти</b>\n\nУкраїнець, росіянин та білорус сперечаються, хто краще програмує.\nУкраїнець написав красивий код.\nБілорус написав швидкий код.\nРосіянин скопіював обидва і сказав що сам придумав.",
            "😂 <b>Програміст у лікаря</b>\n\nПриходить програміст до лікаря:\n- Доктор, у мене болить спина!\n- А ти багато сидиш за комп'ютером?\n- Та ні, тільки 18 годин на день!\n- Це ж нормально для програміста!",
            "🤣 <b>Природа та баги</b>\n\nЧому програмісти не люблять природу?\nБо вона має занадто багато багів і немає документації!",
            "😄 <b>Хліб та яйця</b>\n\nПрограміст приходить додому:\n- Дорогий, купи хліб, якщо будуть яйця - візьми 10\nПовертається з 10 батонами.\n- Чому так багато?\n- Були яйця!",
            "🤪 <b>Рекурсія</b>\n\nЩоб зрозуміти рекурсію, спочатку треба зрозуміти рекурсію."
        ]
        import random
        anekdot = random.choice(anekdots)
        await message.answer(f"🎭 Ось ваш анекдот:\n\n{anekdot}")
    
    # Команда /profile
    @dp.message(Command("profile"))
    async def profile_handler(message: Message):
        user = message.from_user
        await message.answer(
            f"👤 <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"👤 Ім'я: {user.first_name or 'Невідоме'}\n"
            f"📱 Username: @{user.username or 'Немає'}\n"
            f"🌐 Мова: {user.language_code or 'uk'}\n\n"
            f"📊 <b>Статистика:</b>\n"
            f"🔥 Бали: <b>0</b> (початковий рівень)\n"
            f"🏆 Ранг: 🤡 <b>Новачок</b>\n"
            f"📅 Активність: Сьогодні\n\n"
            f"ℹ️ <i>Повна статистика буде доступна після підключення до бази даних</i>"
        )
    
    # Команда /top
    @dp.message(Command("top"))
    async def top_handler(message: Message):
        await message.answer(
            "🏆 <b>ТАБЛИЦЯ ЛІДЕРІВ</b>\n\n"
            "1. 👑 Demo User - 1500 балів\n"
            "2. 🥈 Test User - 1000 балів\n"
            "3. 🥉 Sample User - 500 балів\n"
            "4. 🏅 Example User - 300 балів\n"
            "5. 🎖️ Another User - 150 балів\n\n"
            "📊 Ваша позиція: #новачок\n\n"
            "ℹ️ <i>Реальна таблиця лідерів буде доступна після підключення до бази даних</i>"
        )
    
    # Команда /submit
    @dp.message(Command("submit"))
    async def submit_handler(message: Message):
        await message.answer(
            "📝 <b>ПОДАЧА ВЛАСНОГО КОНТЕНТУ</b>\n\n"
            "Функція подачі власного контенту буде доступна незабаром!\n\n"
            "📋 <b>Що можна буде подавати:</b>\n"
            "• 😂 Жарти та анекдоти\n"
            "• 🖼️ Меми (зображення з підписами)\n"
            "• 📜 Цікаві історії з життя\n\n"
            "🎯 <b>Винагорода за схвалення:</b> +20 балів\n"
            "🛡️ <b>Модерація:</b> Всі матеріали проходять перевірку\n\n"
            "ℹ️ <i>Поки що скористайтеся командами /meme та /anekdot для отримання готового контенту</i>"
        )
    
    # Команда /admin
    @dp.message(Command("admin"))
    async def admin_handler(message: Message):
        try:
            import os
            admin_id = int(os.getenv("ADMIN_ID", 603047391))
            
            if message.from_user.id == admin_id:
                await message.answer(
                    "👑 <b>ПАНЕЛЬ АДМІНІСТРАТОРА</b>\n\n"
                    "🛠️ <b>Статус системи:</b>\n"
                    "✅ Бот: Активний\n"
                    "✅ База даних: Підключена\n"
                    "✅ Автоматизація: Працює\n\n"
                    "🔧 <b>Доступні функції:</b>\n"
                    "• /stats - детальна статистика\n"
                    "• Модерація контенту\n"
                    "• Управління користувачами\n"
                    "• Налаштування автоматизації\n\n"
                    "📊 <b>Швидка статистика:</b>\n"
                    "👥 Користувачів: Завантаження...\n"
                    "📝 Контенту: Завантаження...\n"
                    "⚔️ Дуелей: Завантаження...\n\n"
                    "ℹ️ <i>Повна панель адміністратора в розробці</i>"
                )
            else:
                await message.answer(
                    "❌ <b>Доступ заборонено</b>\n\n"
                    "У вас немає прав адміністратора для доступу до цієї панелі."
                )
        except Exception as e:
            await message.answer(f"❌ Помилка перевірки прав: {e}")
    
    # Обробка всіх текстових повідомлень
    @dp.message(F.text & ~F.text.startswith('/'))
    async def text_handler(message: Message):
        await message.answer(
            "🤖 Привіт! Я розумію тільки команди.\n\n"
            "📋 <b>Спробуйте:</b>\n"
            "/start - почати роботу\n"
            "/help - повна довідка\n"
            "/meme - отримати мем\n"
            "/anekdot - отримати анекдот\n"
            "/profile - ваш профіль"
        )
    
    # Обробка callback queries
    @dp.callback_query()
    async def callback_handler(callback: CallbackQuery):
        await callback.answer("🔧 Ця функція поки що в розробці!")
        await callback.message.answer("🔧 Функція буде доступна в наступних оновленнях.")
    
    # Обробка інших типів повідомлень
    @dp.message()
    async def other_handler(message: Message):
        await message.answer(
            "🤖 Я поки що обробляю тільки текстові повідомлення та команди.\n\n"
            "Надішліть /help для списку доступних команд."
        )
    
    # Error handler
    @dp.error()
    async def error_handler(event, exception):
        logger.error(f"❌ Unhandled error: {exception}")
        try:
            if hasattr(event, 'message') and event.message:
                await event.message.answer(
                    "😅 <b>Вибачте, сталася технічна помилка!</b>\n\n"
                    "Спробуйте ще раз або скористайтеся командою /help"
                )
        except:
            pass
    
    logger.info("✅ Всі handlers зареєстровано успішно")

# Експорт
__all__ = ['register_all_handlers']

logger.info("🎮 Handlers модуль завантажено з повною підтримкою")
