#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Налаштування проекту Бобік 2.0
"""

import os
from typing import Optional

class Settings:
    """Клас налаштувань бота"""
    
    def __init__(self):
        # Основні налаштування
        self.BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@BobikFun")
        
        # AI налаштування
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Часові налаштування
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")
        self.POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "11"))
        
        # Логування
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Валідація
        self._validate()
    
    def _validate(self):
        """Валідація обов'язкових налаштувань"""
        if not self.BOT_TOKEN:
            raise ValueError("⚠️ TELEGRAM_BOT_TOKEN потрібен для роботи бота")
        
        if not self.CHANNEL_ID:
            raise ValueError("⚠️ TELEGRAM_CHANNEL_ID потрібен для публікацій")
        
        print(f"✅ Налаштування завантажено для каналу: {self.CHANNEL_ID}")
