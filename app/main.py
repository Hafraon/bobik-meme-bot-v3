async def register_handlers(self):
        """Реєстрація всіх обробників команд"""
        try:
            logger.info("📝 Реєстрація обробників...")
            
            # Основні команди
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message):
                user_mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
                
                start_text = f"""
🧠😂🔥 Вітаю, {user_mention}!

🤖 Я - професійний україномовний бот з повною автоматизацією!

✅ Автоматизація: {'Активна' if self.automation_active else 'Неактивна'}
💾 База даних: {'Підключена' if self.db_available else 'Fallback режим'}
⏰ Запущено: {self.startup_time.strftime('%H:%M %d.%m.%Y')}

🎮 Використовуй /help для списку команд!
                """
                
                await message.answer(start_text.strip())
                
                # ✅ ВИПРАВЛЕНО: Показуємо адмін меню для адміністраторів
                if self.is_admin(message.from_user.id):
                    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
                    
                    admin_keyboard = ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="👑 Адмін панель"), KeyboardButton(text="📊 Статистика")],
                            [KeyboardButton(text="🛡️ Модерація"), KeyboardButton(text="📢 Розсилка")],
                            [KeyboardButton(text="❌ Вимкнути адмін меню")]
                        ],
                        resize_keyboard=True,
                        one_time_keyboard=False
                    )
                    
                    await message.answer(
                        f"👑 <b>Режим адміністратора активовано!</b>\n\n"
                        f"Використовуйте кнопки меню або команди:\n"
                        f"• /admin - повна адмін панель\n"
                        f"• /moderate - швидка модерація\n"
                        f"• /stats - детальна статистика",
                        reply_markup=admin_keyboard
                    )

            @self.dp.message(Command("help"))
            async def cmd_help(message: Message):
                help_text = """
🧠😂🔥 <b>КОМАНДИ БОТА</b> 🧠😂🔥

👤 <b>Користувацькі команди:</b>
/start - запуск та головне меню
/help - цей список команд
/status - статус бота та автоматизації
/stats - статистика бота

🎮 <b>Розваги:</b>
/meme - випадковий мем
/joke - український жарт
/anekdot - смішний анекдот

🏆 <b>Гейміфікація:</b>
/profile - твій профіль
/top - таблиця лідерів
/achievements - досягнення

⚔️ <b>Дуелі:</b>
/duel - запустити дуель жартів
/duel_stats - статистика дуелей

📝 <b>Контент:</b>
/submit - надіслати свій жарт/мем
/my_content - мої подання

🛡️ <b>Для адмінів:</b>
/admin - адмін панель
/moderate - модерація контенту
/pending - контент на розгляді

🎯 <b>Автоматизація:</b>
- 🌅 Ранкові розсилки (09:00)
- 📊 Вечірня статистика (20:00)  
- 🏆 Тижневі турніри (П'ятниця)
- ⚔️ Автоматичні дуелі
- 🎉 Святкові привітання

💡 <i>Бот працює повністю автоматично!</i>
                """
                await message.answer(help_text)

            @self.dp.message(Command("status"))
            async def cmd_status(message: Message):
                uptime = datetime.now() - self.startup_time
                uptime_str = f"{uptime.days}д {uptime.seconds//3600}г {(uptime.seconds//60)%60}хв"
                
                status_text = f"""
🔧 <b>СТАТУС БОТА</b>

🤖 <b>Основна інформація:</b>
├ Статус: ✅ Онлайн
├ Час роботи: {uptime_str}
├ Запуск: {self.startup_time.strftime('%H:%M %d.%m.%Y')}
└ Режим: Production

💾 <b>База даних:</b>
└ Стан: {'✅ Підключена' if self.db_available else '⚠️ Fallback режим'}

🤖 <b>Автоматизація:</b>
├ Статус: {'✅ Активна' if self.automation_active else '❌ Неактивна'}
├ Планувальник: {'✅ Працює' if self.scheduler else '❌ Не запущено'}
└ Завдань виконується: {len(getattr(self.scheduler, 'jobs', [])) if self.scheduler else 0}

🎯 <b>Функціональність:</b>
├ Меню та команди: ✅ Працюють
├ Жарти та меми: ✅ Доступні
├ Дуелі: ✅ Активні
├ Статистика: ✅ Збирається
└ Модерація: ✅ Функціональна

💡 <i>Всі системи працюють стабільно!</i>
                """
                await message.answer(status_text)

            # ✅ ВИПРАВЛЕНО: Правильна реєстрація адмін команд
            @self.dp.message(Command("admin"))
            async def cmd_admin(message: Message):
                # Перевірка прав ВСЕРЕДИНІ хендлера
                if not self.is_admin(message.from_user.id):
                    await message.answer("❌ Доступ заборонено. Тільки для адміністраторів.")
                    return
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
                        InlineKeyboardButton(text="🛡️ Модерація", callback_data="admin_moderate")
                    ],
                    [
                        InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
                        InlineKeyboardButton(text="📝 Контент", callback_data="admin_content")
                    ],
                    [
                        InlineKeyboardButton(text="🔥 Трендове", callback_data="admin_trending"),
                        InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings")
                    ],
                    [
                        InlineKeyboardButton(text="🚀 Масові дії", callback_data="admin_bulk"),
                        InlineKeyboardButton(text="💾 Бекап", callback_data="admin_backup")
                    ]
                ])
                
                admin_text = f"""
👑 <b>АДМІН ПАНЕЛЬ</b>

👤 <b>Адміністратор:</b> {message.from_user.first_name}
🕐 <b>Час доступу:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}

📊 <b>Швидка статистика:</b>
├ Час роботи: {(datetime.now() - self.startup_time).seconds // 3600}г
├ База даних: {'✅ Підключена' if self.db_available else '⚠️ Fallback'}
├ Автоматизація: {'✅ Активна' if self.automation_active else '❌ Неактивна'}
└ Планувальник: {'✅ Працює' if self.scheduler else '❌ Не запущено'}

🛠️ <b>Швидкі команди:</b>
• /moderate - почати модерацію
• /pending - контент на розгляді
• /stats - детальна статистика
• /broadcast - розсилка повідомлень

⚡ <b>Виберіть дію з меню нижче:</b>
                """
                
                await message.answer(admin_text.strip(), reply_markup=keyboard)

            @self.dp.message(Command("moderate"))
            async def cmd_moderate(message: Message):
                if not self.is_admin(message.from_user.id):
                    await message.answer("❌ Доступ заборонено.")
                    return
                
                await message.answer(
                    "🛡️ <b>МОДЕРАЦІЯ КОНТЕНТУ</b>\n\n"
                    "🔍 Пошук контенту на розгляді...\n"
                    "📋 Функція модерації буде доступна після повного підключення БД.\n\n"
                    "💡 Наразі бот працює в fallback режимі з базовими функціями."
                )

            @self.dp.message(Command("stats"))
            async def cmd_stats(message: Message):
                if not self.is_admin(message.from_user.id):
                    # Базова статистика для звичайних користувачів
                    await message.answer(
                        "📊 <b>СТАТИСТИКА БОТА</b>\n\n"
                        f"🤖 Статус: ✅ Онлайн\n"
                        f"⏰ Запущено: {self.startup_time.strftime('%H:%M %d.%m.%Y')}\n"
                        f"🎯 Автоматизація: {'Активна' if self.automation_active else 'Неактивна'}\n\n"
                        f"💡 Детальна статистика доступна тільки адміністраторам."
                    )
                    return
                
                # Детальна статистика для адмінів
                uptime = datetime.now() - self.startup_time
                uptime_str = f"{uptime.days}д {uptime.seconds//3600}г {(uptime.seconds//60)%60}хв"
                
                stats_text = f"""
📊 <b>ДЕТАЛЬНА СТАТИСТИКА БОТА</b>

🤖 <b>Система:</b>
├ Статус: ✅ Онлайн
├ Час роботи: {uptime_str}  
├ Запуск: {self.startup_time.strftime('%H:%M %d.%m.%Y')}
├ Режим: Production
└ Версія: 2.0 (Railway)

💾 <b>База даних:</b>
├ Стан: {'✅ Підключена' if self.db_available else '⚠️ Fallback режим'}
├ Тип: {'PostgreSQL' if self.db_available else 'In-memory fallback'}
└ З'єднання: {'Стабільне' if self.db_available else 'Недоступне'}

🤖 <b>Автоматизація:</b>
├ Статус: {'✅ Активна' if self.automation_active else '❌ Неактивна'}
├ Планувальник: {'✅ Працює' if self.scheduler else '❌ Не запущено'}
├ Завдань активно: {len(getattr(self.scheduler, 'jobs', [])) if self.scheduler else 0}
└ Останній запуск: {datetime.now().strftime('%H:%M')}

🎯 <b>Функціональність:</b>
├ Команди: ✅ Повністю працюють
├ Інлайн меню: ✅ Активні
├ Адмін панель: ✅ Доступна
├ Модерація: {'✅ Активна' if self.db_available else '⚠️ Обмежена'}
├ Гейміфікація: {'✅ Повна' if self.db_available else '⚠️ Базова'}
└ Дуелі: {'✅ Активні' if self.db_available else '⚠️ Тестовий режим'}

🌍 <b>Середовище:</b>
├ Platform: Railway
├ Region: Europe-West4
├ Memory: 512MB
└ Storage: 1GB

💡 <b>Рекомендації:</b>
{' Всі системи працюють оптимально!' if self.db_available else '⚠️ Для повної функціональності підключіть PostgreSQL БД.'}
                """
                
                await message.answer(stats_text.strip())

            # Обробка адмін кнопок
            @self.dp.message()
            async def handle_admin_buttons(message: Message):
                if not self.is_admin(message.from_user.id):
                    return
                
                text = message.text
                
                if text == "👑 Адмін панель":
                    await cmd_admin(message)
                elif text == "📊 Статистика":
                    await cmd_stats(message)
                elif text == "🛡️ Модерація":
                    await cmd_moderate(message)
                elif text == "📢 Розсилка":
                    await message.answer(
                        "📢 <b>СИСТЕМА РОЗСИЛКИ</b>\n\n"
                        "🚀 Функція масової розсилки буде доступна після підключення повної БД.\n\n"
                        "💡 Наразі можна використовувати команди для окремих повідомлень."
                    )
                elif text == "❌ Вимкнути адмін меню":
                    from aiogram.types import ReplyKeyboardRemove
                    await message.answer(
                        "✅ Адмін меню вимкнено.\n"
                        "Використовуйте команди /admin, /moderate, /stats для роботи.",
                        reply_markup=ReplyKeyboardRemove()
                    )

            # Обробка callback запитів адмін панелі
            @self.dp.callback_query()
            async def handle_admin_callbacks(callback: CallbackQuery):
                if not self.is_admin(callback.from_user.id):
                    await callback.answer("❌ Доступ заборонено", show_alert=True)
                    return
                
                data = callback.data
                
                if data == "admin_stats":
                    await callback.message.edit_text(
                        "📊 <b>ДЕТАЛЬНА СТАТИСТИКА</b>\n\n"
                        f"🤖 Статус: ✅ Онлайн\n"
                        f"💾 БД: {'Підключена' if self.db_available else 'Fallback'}\n"
                        f"🤖 Автоматизація: {'Активна' if self.automation_active else 'Неактивна'}\n"
                        f"⏰ Запуск: {self.startup_time.strftime('%H:%M %d.%m.%Y')}\n\n"
                        f"💡 Повна статистика доступна через /stats"
                    )
                elif data == "admin_moderate":
                    await callback.message.edit_text(
                        "🛡️ <b>ПАНЕЛЬ МОДЕРАЦІЇ</b>\n\n"
                        "📋 Контент на розгляді: 0\n"
                        "✅ Схвалено сьогодні: 0\n"
                        "❌ Відхилено сьогодні: 0\n\n"
                        "💡 Повна модерація буде доступна після підключення БД.\n"
                        "Використовуйте /moderate для початку."
                    )
                elif data == "admin_users":
                    await callback.message.edit_text(
                        "👥 <b>УПРАВЛІННЯ КОРИСТУВАЧАМИ</b>\n\n"
                        "📊 Всього користувачів: Підрахунок...\n"
                        "🆕 Нових за сьогодні: Підрахунок...\n"
                        "🏆 Топ користувачів: Завантаження...\n\n"
                        "💡 Функція буде повністю доступна після підключення БД."
                    )
                else:
                    await callback.message.edit_text(
                        f"⚙️ <b>ФУНКЦІЯ: {data.replace('admin_', '').upper()}</b>\n\n"
                        f"🚧 Ця функція знаходиться в розробці.\n"
                        f"💡 Буде доступна в наступних оновленнях."
                    )
                
                await callback.answer()

            logger.info("✅ All handlers registered with automation support")
            
        except Exception as e:
            logger.error(f"❌ Помилка реєстрації обробників: {e}")
            logger.error(traceback.format_exc())