#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Функції для роботи з БД будуть додані поступово
try:
    from .models import Base, User, Content, Rating, Duel, DuelVote, AdminAction, BotStatistics
    from .models import ContentType, ContentStatus, DuelStatus
    
    MODELS_LOADED = True
    logger.info("Database models loaded successfully")
    
except ImportError as e:
    logger.warning(f"Could not load database models: {e}")
    MODELS_LOADED = False

# Експорт основних класів
__all__ = [
    'Base', 'User', 'Content', 'Rating', 'Duel', 'DuelVote', 
    'AdminAction', 'BotStatistics',
    'ContentType', 'ContentStatus', 'DuelStatus',
    'MODELS_LOADED'
]