#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Реєстрація всіх хендлерів бота 🧠😂🔥
"""

from aiogram import Dispatcher

from .basic_commands import register_basic_handlers
from .content_handlers import register_content_handlers
from .gamification_handlers import register_gamification_handlers
from .moderation_handlers import register_moderation_handlers
from .duel_handlers import register_duel_handlers

def register_handlers(dp: Dispatcher):
    """Реєстрація всіх хендлерів"""
    
    # Основні команди (start, help)
    register_basic_handlers(dp)
    
    # Контент (meme, anekdot, submit)
    register_content_handlers(dp)
    
    # Гейміфікація (profile, top, daily)
    register_gamification_handlers(dp)
    
    # Модерація (approve, reject)
    register_moderation_handlers(dp)
    
    # Дуелі (duel)
    register_duel_handlers(dp)