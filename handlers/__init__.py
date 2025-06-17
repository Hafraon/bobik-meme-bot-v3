#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Реєстрація всіх хендлерів бота 🧠😂🔥
"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів у правильному порядку"""
    
    try:
        # 1. Основні команди (start, help, stats)
        from handlers.basic_commands import register_basic_handlers
        register_basic_handlers(dp)
        logger.info("✅ Зареєстровано основні команди")
        
        # 2. АДМІН-ПАНЕЛЬ (admin, m) - одразу після основних команд!
        try:
            from handlers.admin_panel_handlers import register_admin_handlers
            register_admin_handlers(dp)
            logger.info("✅ Зареєстровано адмін-панель")
        except ImportError as e:
            logger.warning(f"⚠️ Адмін-панель не завантажена: {e}")
        
        # 3. Гейміфікація (profile, top, daily) - до контенту!
        from handlers.gamification_handlers import register_gamification_handlers
        register_gamification_handlers(dp)
        logger.info("✅ Зареєстровано гейміфікацію")
        
        # 4. Контент (meme, anekdot, submit) - після гейміфікації
        from handlers.content_handlers import register_content_handlers
        register_content_handlers(dp)
        logger.info("✅ Зареєстровано контент-хендлери")
        
        # 5. Модерація (approve, reject) - тільки для адміна
        from handlers.moderation_handlers import register_moderation_handlers
        register_moderation_handlers(dp)
        logger.info("✅ Зареєстровано модерацію")
        
        # 6. Дуелі (duel) - в кінці
        from handlers.duel_handlers import register_duel_handlers
        register_duel_handlers(dp)
        logger.info("✅ Зареєстровано дуелі")
        
        logger.info("🎯 Всі хендлери успішно зареєстровані!")
        
    except ImportError as e:
        logger.error(f"❌ Помилка імпорту хендлерів: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації хендлерів: {e}")
        raise