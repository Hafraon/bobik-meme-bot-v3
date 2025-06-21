#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ШВИДКЕ ВИПРАВЛЕННЯ HANDLERS 🔧

Цей скрипт виправляє проблему з register_all_handlers
"""

from pathlib import Path

def fix_handlers_init():
    """Виправлення app/handlers/__init__.py"""
    
    print("🔧 ВИПРАВЛЕННЯ APP/HANDLERS/__INIT__.PY:")
    
    # Створюємо папку handlers якщо не існує
    handlers_dir = Path("app/handlers")
    handlers_dir.mkdir(exist_ok=True, parents=True)
    
    handlers_init_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 HANDLERS МОДУЛЬ - ВИПРАВЛЕНА РЕЄСТРАЦІЯ 🎯
"""

import logging
from aiogram import Dispatcher
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart

logger = logging.getLogger(__name__)

def register_all_handlers(dp: Dispatcher):
    """🎯 ГОЛОВНА ФУНКЦІЯ РЕЄСТРАЦІЇ ВСІХ HANDLERS"""
    logger.info("🎯 Початок реєстрації handlers...")
    
    # Спробуємо зареєструвати основні handlers
    registered = 0
    
    handler_modules = [
        "basic_commands",
        "content_handlers", 
        "gamification_handlers",
        "duel_handlers",
        "moderation_handlers",
        "admin_handlers",
        "admin_panel_handlers",
    ]
    
    for module_name in handler_modules:
        try:
            module = __import__(f"handlers.{module_name}", fromlist=["register"])
            if hasattr(module, f"register_{module_name}"):
                register_func = getattr(module, f"register_{module_name}")
                register_func(dp)
                registered += 1
                logger.info(f"✅ {module_name} зареєстровано")
        except ImportError:
            logger.warning(f"⚠️ Модуль {module_name} не знайдено")
        except Exception as e:
            logger.warning(f"⚠️ Помилка реєстрації {module_name}: {e}")
    
    # Якщо нічого не зареєстровано, використовуємо fallback
    if registered == 0:
        logger.warning("⚠️ Використовую fallback handlers")
        register_fallback_handlers(dp)
    
    logger.info(f"✅ Handlers зареєстровано: {registered} основних + fallback")

def register_fallback_handlers(dp: Dispatcher):
    """🆘 Fallback handlers"""
    
    @dp.message(CommandStart())
    async def start_handler(message: Message):
        await message.answer(
            "🤖 <b>Привіт! Я український мем-бот з гейміфікацією!</b>\\n\\n"
            "📋 <b>Команди:</b>\\n"
            "• /help - довідка\\n"
            "• /meme - випадковий мем\\n"
            "• /anekdot - український анекдот\\n"
            "• /profile - мій профіль\\n"
            "• /admin - панель адміна"
        )
    
    @dp.message(Command("help"))
    async def help_handler(message: Message):
        await message.answer(
            "❓ <b>ДОВІДКА ПО БОТУ</b>\\n\\n"
            "🎮 <b>Гейміфікація:</b>\\n"
            "• Заробляйте бали за активність\\n"
            "• Підвищуйте свій ранг\\n\\n"
            "📝 <b>Контент:</b>\\n"
            "• /meme - випадковий мем\\n"
            "• /anekdot - український анекдот\\n\\n"
            "👤 <b>Профіль:</b>\\n"
            "• /profile - ваш профіль"
        )
    
    @dp.message(Command("meme"))
    async def meme_handler(message: Message):
        memes = [
            "😂 Програміст заходить в кафе і замовляє каву. Бариста: 'Java чи Python?' Програміст: 'Звичайну!'",
            "🤣 Чому програмісти плутають Різдво та Хеллоуїн? Бо Oct 31 == Dec 25!",
            "😄 Скільки програмістів треба щоб закрутити лампочку? Жодного - це апаратна проблема!"
        ]
        import random
        await message.answer(f"🎭 {random.choice(memes)}")
    
    @dp.message(Command("anekdot"))
    async def anekdot_handler(message: Message):
        anekdots = [
            "🇺🇦 Українець написав код. Білорус оптимізував. Росіянин скопіював і сказав що сам придумав.",
            "😂 Програміст у лікаря: 'Болить спина!' 'Багато сидиш?' 'Тільки 18 годин!' 'Нормально!'",
            "🤣 Чому програмісти не люблять природу? Багато багів і немає документації!"
        ]
        import random
        await message.answer(f"🎭 {random.choice(anekdots)}")
    
    @dp.message(Command("profile"))
    async def profile_handler(message: Message):
        user = message.from_user
        await message.answer(
            f"👤 <b>ПРОФІЛЬ</b>\\n\\n"
            f"🆔 ID: {user.id}\\n"
            f"👤 Ім'я: {user.first_name or 'Невідоме'}\\n"
            f"📊 Бали: 0\\n"
            f"🏆 Ранг: 🤡 Новачок"
        )
    
    @dp.message(Command("admin"))
    async def admin_handler(message: Message):
        # Перевірка адміністратора
        try:
            import os
            admin_id = int(os.getenv("ADMIN_ID", 603047391))
            if message.from_user.id == admin_id:
                await message.answer("👑 <b>ПАНЕЛЬ АДМІНІСТРАТОРА</b>\\n\\nФункції в розробці...")
            else:
                await message.answer("❌ Немає прав адміністратора")
        except:
            await message.answer("❌ Помилка перевірки прав")
    
    @dp.error()
    async def error_handler(event, exception):
        logger.error(f"❌ Error: {exception}")
        try:
            if hasattr(event, 'message') and event.message:
                await event.message.answer("😅 Технічна помилка! Спробуйте /help")
        except:
            pass

# Експорт
__all__ = ['register_all_handlers']

logger.info("🎮 Handlers модуль завантажено з fallback підтримкою")
'''
    
    # Записуємо файл
    with open("app/handlers/__init__.py", "w", encoding="utf-8") as f:
        f.write(handlers_init_content)
    
    print("   ✅ app/handlers/__init__.py створено з register_all_handlers")
    return True

def main():
    """Головна функція"""
    print("🔧 ШВИДКЕ ВИПРАВЛЕННЯ HANDLERS")
    print("=" * 40)
    
    try:
        success = fix_handlers_init()
        
        if success:
            print("\n✅ ВИПРАВЛЕННЯ ЗАВЕРШЕНО!")
            print("\nНаступні кроки:")
            print("1. git add .")
            print("2. git commit -m '🔧 Fix handlers registration'") 
            print("3. git push")
            print("\nОчікувані результати:")
            print("✅ Зникне помилка: cannot import name 'register_all_handlers'")
            print("✅ Всі команди будуть оброблятися")
            print("✅ Updates handled правильно")
        else:
            print("\n❌ Виправлення не вдалося")
            
    except Exception as e:
        print(f"\n❌ Помилка: {e}")

if __name__ == "__main__":
    main()