# ===== ДОДАТИ ЦІ ФУНКЦІЇ В database/database.py =====
# (в секцію async def init_db(), замінити існуючу функцію)

async def init_db():
    """Професійна ініціалізація бази даних з міграцією"""
    try:
        logger.info("💾 Початок ініціалізації бази даних...")
        
        # КРОК 1: Перевірка чи потрібна міграція
        needs_migration = await check_if_migration_needed()
        
        if needs_migration:
            logger.info("🔄 Потрібна міграція БД, видаляю старі таблиці...")
            await drop_old_tables()
        
        # КРОК 2: Створення всіх таблиць
        Base.metadata.create_all(bind=engine)
        logger.info("🔥 Таблиці бази даних створено!")
        
        # КРОК 3: Додавання початкових даних
        await add_initial_data()
        
        # КРОК 4: Перевірка цілісності
        await verify_database_integrity()
        
        logger.info("✅ База даних повністю ініціалізована!")
        
    except Exception as e:
        logger.error(f"❌ Критична помилка ініціалізації БД: {e}")
        raise

async def check_if_migration_needed() -> bool:
    """Перевірити чи потрібна міграція БД"""
    try:
        with get_db_session() as session:
            # Спробуємо виконати запит до нової структури
            session.execute(text("SELECT telegram_id FROM users LIMIT 1"))
            logger.info("✅ Структура БД актуальна")
            return False
    except Exception as e:
        logger.info(f"🔄 Потрібна міграція БД: {e}")
        return True

async def drop_old_tables():
    """Видалити старі таблиці для міграції"""
    try:
        with engine.begin() as conn:
            # Видаляємо таблиці в правильному порядку (з урахуванням зв'язків)
            tables_to_drop = [
                'duel_votes',
                'admin_actions', 
                'bot_statistics',
                'ratings',
                'duels',
                'content',
                'users'
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    logger.info(f"🗑️ Видалено таблицю: {table}")
                except Exception as e:
                    logger.warning(f"⚠️ Не вдалося видалити {table}: {e}")
            
            logger.info("✅ Старі таблиці видалено")
            
    except Exception as e:
        logger.error(f"❌ Помилка видалення старих таблиць: {e}")
        # Продовжуємо виконання - можливо таблиць не було