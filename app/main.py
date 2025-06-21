async def launch_app_main():
    """Адаптивний запуск основного коду з app/main.py"""
    
    logger.info("🔄 Адаптивний імпорт та запуск app/main.py...")
    print("🔄 Adaptive import and launch app/main.py...", flush=True)
    
    try:
        # Імпорт модуля app/main.py
        import main as app_module
        
        logger.info("✅ app/main.py успішно імпортовано")
        print("✅ app/main.py imported successfully", flush=True)
        
        # ===== АДАПТИВНИЙ ЗАПУСК - СПРОБУЄМО ВСІ ВАРІАНТИ =====
        
        # Варіант 1: Функція main()
        if hasattr(app_module, 'main') and callable(getattr(app_module, 'main')):
            logger.info("🎯 Знайдено функцію main(), запускаємо...")
            print("🎯 Found main() function, launching...", flush=True)
            
            await app_module.main()
            return
        
        # Варіант 2: Клас AutomatedUkrainianTelegramBot
        elif hasattr(app_module, 'AutomatedUkrainianTelegramBot'):
            logger.info("🎯 Знайдено клас AutomatedUkrainianTelegramBot, створюємо інстанс...")
            print("🎯 Found AutomatedUkrainianTelegramBot class, creating instance...", flush=True)
            
            bot_instance = app_module.AutomatedUkrainianTelegramBot()
            
            # Перевіряємо методи запуску
            if hasattr(bot_instance, 'run') and callable(getattr(bot_instance, 'run')):
                logger.info("✅ Запускаємо через bot.run()...")
                print("✅ Launching via bot.run()...", flush=True)
                await bot_instance.run()
            elif hasattr(bot_instance, 'main') and callable(getattr(bot_instance, 'main')):
                logger.info("✅ Запускаємо через bot.main()...")  
                print("✅ Launching via bot.main()...", flush=True)
                await bot_instance.main()
            else:
                logger.error("❌ Клас не має методу run() або main()")
                raise Exception("Bot class has no run() or main() method")
            return
        
        # Варіант 3: Інший клас бота
        elif hasattr(app_module, 'UkrainianTelegramBot'):
            logger.info("🎯 Знайдено клас UkrainianTelegramBot, створюємо інстанс...")
            print("🎯 Found UkrainianTelegramBot class, creating instance...", flush=True)
            
            bot_instance = app_module.UkrainianTelegramBot()
            
            if hasattr(bot_instance, 'run'):
                await bot_instance.run()
            elif hasattr(bot_instance, 'main'):
                await bot_instance.main()
            else:
                logger.error("❌ Клас не має методу run() або main()")
                raise Exception("Bot class has no run() or main() method")
            return
        
        # Варіант 4: Глобальна змінна bot або dispatcher
        elif hasattr(app_module, 'bot') and hasattr(app_module, 'dp'):
            logger.info("🎯 Знайдено bot та dp змінні, запускаємо polling...")
            print("🎯 Found bot and dp variables, starting polling...", flush=True)
            
            bot = getattr(app_module, 'bot')
            dp = getattr(app_module, 'dp')
            
            # Запускаємо polling
            await dp.start_polling(bot, skip_updates=True)
            return
        
        # Варіант 5: Функція run_bot() або start_bot()
        elif hasattr(app_module, 'run_bot') and callable(getattr(app_module, 'run_bot')):
            logger.info("🎯 Знайдено функцію run_bot(), запускаємо...")
            print("🎯 Found run_bot() function, launching...", flush=True)
            
            await app_module.run_bot()
            return
        
        elif hasattr(app_module, 'start_bot') and callable(getattr(app_module, 'start_bot')):
            logger.info("🎯 Знайдено функцію start_bot(), запускаємо...")
            print("🎯 Found start_bot() function, launching...", flush=True)
            
            await app_module.start_bot()
            return
        
        # Якщо нічого не знайшли - запускаємо fallback бот
        else:
            logger.warning("⚠️ Жоден entry point не знайдено в app/main.py")
            print("⚠️ No entry point found in app/main.py", flush=True)
            
            # Показуємо доступні атрибути для діагностики
            available_attrs = [attr for attr in dir(app_module) if not attr.startswith('_')]
            logger.info(f"📋 Доступні атрибути в app/main.py: {available_attrs}")
            print(f"📋 Available attributes in app/main.py: {available_attrs}", flush=True)
            
            logger.info("🆘 Запускаємо fallback бот...")
            print("🆘 Starting fallback bot...", flush=True)
            await run_fallback_bot()
        
    except ImportError as e:
        logger.error(f"❌ Помилка імпорту app/main.py: {e}")
        print(f"❌ Import error app/main.py: {e}", flush=True)
        logger.error(traceback.format_exc())
        
        logger.info("🆘 Запускаємо fallback бот через import error...")
        print("🆘 Starting fallback bot due to import error...", flush=True)
        await run_fallback_bot()
        
    except Exception as e:
        logger.error(f"❌ Помилка виконання app/main.py: {e}")
        print(f"❌ Execution error app/main.py: {e}", flush=True)
        logger.error(traceback.format_exc())
        
        logger.info("🆘 Запускаємо fallback бот через execution error...")
        print("🆘 Starting fallback bot due to execution error...", flush=True)
        await run_fallback_bot()

async def run_fallback_bot():
    """Fallback бот який точно працює"""
    
    logger.info("🆘 Запуск fallback бота...")
    print("🆘 Starting fallback bot...", flush=True)
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from aiogram.filters import Command
        from aiogram.types import Message
        
        bot_token = os.getenv("BOT_TOKEN")
        admin_id = int(os.getenv("ADMIN_ID", "603047391"))
        
        if not bot_token:
            logger.error("❌ BOT_TOKEN не знайдено для fallback бота!")
            print("❌ BOT_TOKEN not found for fallback bot!", flush=True)
            return
        
        # Створюємо fallback бота
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        
        # Основні команди fallback бота
        @dp.message(Command("start"))
        async def fallback_start(message: Message):
            user_name = message.from_user.first_name or "друже"
            await message.answer(
                f"🆘 <b>Fallback режим активний</b>\n\n"
                f"Привіт, {user_name}! Я працюю в спрощеному режимі.\n\n"
                f"📋 <b>Доступні команди:</b>\n"
                f"• /start - це повідомлення\n"
                f"• /status - статус бота\n"
                f"• /help - довідка\n"
                f"• /joke - випадковий жарт\n\n"
                f"⚠️ <b>Адміну:</b> Перевірте логи Railway для виправлення проблем."
            )
        
        @dp.message(Command("status"))
        async def fallback_status(message: Message):
            await message.answer(
                f"🆘 <b>СТАТУС FALLBACK БОТА</b>\n\n"
                f"🤖 Режим: Аварійний\n"
                f"✅ Статус: Онлайн\n"
                f"⏰ Час: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n"
                f"📡 Railway: Активний\n\n"
                f"⚠️ Основний функціонал недоступний.\n"
                f"Адміністратор має перевірити логи Railway."
            )
        
        @dp.message(Command("help"))
        async def fallback_help(message: Message):
            await message.answer(
                f"🆘 <b>FALLBACK БОТ - ДОВІДКА</b>\n\n"
                f"Я працюю в аварійному режимі через проблеми з основним кодом.\n\n"
                f"📋 <b>Доступні команди:</b>\n"
                f"• /start - головне меню\n"
                f"• /status - поточний статус\n"
                f"• /help - ця довідка\n"
                f"• /joke - випадковий жарт\n\n"
                f"🔧 <b>Для адміністратора:</b>\n"
                f"Перевірте Railway логи для діагностики.\n"
                f"Проблема: entry point не знайдено в app/main.py"
            )
        
        @dp.message(Command("joke"))
        async def fallback_joke(message: Message):
            import random
            
            jokes = [
                "😂 Програміст заходить в кафе:\n- Каву, будь ласка.\n- Цукор?\n- Ні, boolean!",
                "🤖 Чому боти не п'ють каву?\nБо вони працюють на енергетиках!",
                "🔧 Fallback жарт:\nМій код не працює.\n- А чому?\n- Бо я в fallback режимі!",
                "🚀 Railway розробник:\n- Чому бот крашиться?\n- Import error.\n- А fallback?\n- Працює!",
                "🧠 AI жарт:\nЯ б розповів жарт про машинне навчання,\nале воно досі тренується!"
            ]
            
            selected_joke = random.choice(jokes)
            await message.answer(f"😄 <b>Fallback жарт:</b>\n\n{selected_joke}")
        
        # Адмін команди
        @dp.message(Command("admin"))
        async def fallback_admin(message: Message):
            if message.from_user.id != admin_id:
                await message.answer("❌ Доступ заборонено.")
                return
            
            await message.answer(
                f"👑 <b>FALLBACK АДМІН ПАНЕЛЬ</b>\n\n"
                f"🆘 Бот працює в аварійному режимі.\n\n"
                f"🔍 <b>Діагностика:</b>\n"
                f"• Entry point не знайдено в app/main.py\n"
                f"• Перевірте структуру файлу\n"
                f"• Перевірте наявність функції main() або класу\n\n"
                f"📋 <b>Railway логи:</b>\n"
                f"Dashboard → Deployments → Logs\n\n"
                f"🔧 <b>Виправлення:</b>\n"
                f"1. Перевірте app/main.py\n"
                f"2. Додайте функцію main() або клас\n"
                f"3. Redeploy проект"
            )
        
        # Перевірка підключення бота
        bot_info = await bot.get_me()
        logger.info(f"✅ Fallback бот підключено: @{bot_info.username}")
        print(f"✅ Fallback bot connected: @{bot_info.username}", flush=True)
        
        # Запуск polling
        logger.info("🚀 Запуск fallback polling...")
        print("🚀 Starting fallback polling...", flush=True)
        
        await dp.start_polling(
            bot, 
            skip_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
    except Exception as e:
        logger.error(f"💥 Критична помилка fallback бота: {e}")
        print(f"💥 Critical fallback bot error: {e}", flush=True)
        logger.error(traceback.format_exc())
        raise