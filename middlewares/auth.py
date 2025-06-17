#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Middleware для аутентифікації та контролю доступу 🧠😂🔥
"""

import logging
import time
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логування всіх повідомлень"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Логування повідомлень
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"📝 Повідомлення від {user.first_name} (@{user.username or 'no_username'}) "
                f"ID:{user.id}: {event.text[:50] if event.text else 'медіа'}"
            )
        
        # Логування callback запитів
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"🔘 Callback від {user.first_name} ID:{user.id}: {event.data}"
            )
        
        # Виклик наступного handler
        return await handler(event, data)

class AntiSpamMiddleware(BaseMiddleware):
    """Middleware для захисту від спаму"""
    
    def __init__(self, rate_limit: int = 3):
        """
        rate_limit: максимум повідомлень на секунду
        """
        self.rate_limit = rate_limit
        self.user_last_message = {}  # user_id -> timestamp
        self.user_message_count = {}  # user_id -> count in current second
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Отримання user_id
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            return await handler(event, data)
        
        # Поточний час
        current_time = time.time()
        current_second = int(current_time)
        
        # Ініціалізація для нового користувача
        if user_id not in self.user_last_message:
            self.user_last_message[user_id] = current_second
            self.user_message_count[user_id] = 1
            return await handler(event, data)
        
        # Перевірка rate limit
        last_second = self.user_last_message[user_id]
        
        if current_second == last_second:
            # Та ж секунда - збільшуємо лічильник
            self.user_message_count[user_id] += 1
            
            if self.user_message_count[user_id] > self.rate_limit:
                # Перевищено ліміт
                logger.warning(f"🚫 Спам від користувача {user_id}")
                
                if isinstance(event, Message):
                    await event.answer(
                        "⚠️ Забагато повідомлень! Зачекай трохи...",
                        show_alert=True
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "⚠️ Забагато запитів! Зачекай трохи...", 
                        show_alert=True
                    )
                
                return  # Не викликаємо handler
        else:
            # Нова секунда - скидаємо лічильник
            self.user_last_message[user_id] = current_second
            self.user_message_count[user_id] = 1
        
        # Виклик наступного handler
        return await handler(event, data)

class AuthMiddleware(BaseMiddleware):
    """Middleware для аутентифікації користувачів"""
    
    def __init__(self):
        self.banned_users = set()  # Заблоковані користувачі
        self.admin_users = set()   # Адміністратори
        
        # Завантаження списку адмінів
        try:
            from config.settings import Settings
            settings = Settings()
            if hasattr(settings, 'ADMIN_ID') and settings.ADMIN_ID:
                self.admin_users.add(settings.ADMIN_ID)
        except ImportError:
            import os
            admin_id = os.getenv("ADMIN_ID")
            if admin_id:
                self.admin_users.add(int(admin_id))
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Отримання інформації про користувача
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Перевірка бану
        if user.id in self.banned_users:
            logger.warning(f"🚫 Заблокований користувач {user.id} спробував використати бота")
            
            if isinstance(event, Message):
                await event.answer(
                    "🚫 Вас заблоковано в цьому боті.\n"
                    "Для отримання додаткової інформації зверніться до адміністратора."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Доступ заборонено", show_alert=True)
            
            return  # Не викликаємо handler
        
        # Додавання інформації про права до контексту
        data["is_admin"] = user.id in self.admin_users
        data["user_permissions"] = {
            "is_admin": user.id in self.admin_users,
            "can_moderate": user.id in self.admin_users,
            "is_banned": user.id in self.banned_users
        }
        
        # Оновлення інформації про користувача в БД
        try:
            await self.update_user_info(user)
        except Exception as e:
            logger.error(f"Помилка оновлення інформації користувача: {e}")
        
        # Виклик наступного handler
        return await handler(event, data)
    
    async def update_user_info(self, user):
        """Оновлення інформації про користувача в БД"""
        try:
            # Спроба оновлення через БД
            from handlers.gamification_handlers import get_or_create_user
            await get_or_create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
        except ImportError:
            # Fallback - просто логування
            logger.info(f"👤 Користувач {user.first_name} (ID:{user.id}) використовує бота")
    
    def ban_user(self, user_id: int):
        """Заборона користувача"""
        self.banned_users.add(user_id)
        logger.info(f"🚫 Користувача {user_id} заблоковано")
    
    def unban_user(self, user_id: int):
        """Розблокування користувача"""
        self.banned_users.discard(user_id)
        logger.info(f"✅ Користувача {user_id} розблоковано")
    
    def add_admin(self, user_id: int):
        """Додавання адміністратора"""
        self.admin_users.add(user_id)
        logger.info(f"👑 Користувача {user_id} призначено адміністратором")
    
    def remove_admin(self, user_id: int):
        """Видалення адміністратора"""
        self.admin_users.discard(user_id)
        logger.info(f"👤 У користувача {user_id} забрано права адміністратора")

class UserTrackingMiddleware(BaseMiddleware):
    """Middleware для відстеження активності користувачів"""
    
    def __init__(self):
        self.user_stats = {}  # Статистика користувачів
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Отримання user_id
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            # Ініціалізація статистики для нового користувача
            if user_id not in self.user_stats:
                self.user_stats[user_id] = {
                    "first_seen": datetime.now(),
                    "last_active": datetime.now(),
                    "message_count": 0,
                    "callback_count": 0
                }
            
            # Оновлення статистики
            stats = self.user_stats[user_id]
            stats["last_active"] = datetime.now()
            
            if isinstance(event, Message):
                stats["message_count"] += 1
            elif isinstance(event, CallbackQuery):
                stats["callback_count"] += 1
            
            # Додавання статистики до контексту
            data["user_stats"] = stats
        
        # Виклик наступного handler
        return await handler(event, data)
    
    def get_user_stats(self, user_id: int) -> dict:
        """Отримання статистики користувача"""
        return self.user_stats.get(user_id, {})
    
    def get_active_users(self, hours: int = 24) -> list:
        """Отримання списку активних користувачів за останні години"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        active_users = []
        for user_id, stats in self.user_stats.items():
            if stats["last_active"] > cutoff_time:
                active_users.append({
                    "user_id": user_id,
                    "last_active": stats["last_active"],
                    "total_messages": stats["message_count"] + stats["callback_count"]
                })
        
        return sorted(active_users, key=lambda x: x["last_active"], reverse=True)

# Допоміжні функції для роботи з middleware

def is_admin(data: Dict[str, Any]) -> bool:
    """Перевірка чи є користувач адміністратором"""
    return data.get("is_admin", False)

def get_user_permissions(data: Dict[str, Any]) -> dict:
    """Отримання прав користувача"""
    return data.get("user_permissions", {})

def get_user_stats_from_context(data: Dict[str, Any]) -> dict:
    """Отримання статистики користувача з контексту"""
    return data.get("user_stats", {})

# Глобальні екземпляри middleware для експорту
auth_middleware = AuthMiddleware()
tracking_middleware = UserTrackingMiddleware()

# Функції для управління з інших модулів
def ban_user(user_id: int):
    """Заборона користувача"""
    return auth_middleware.ban_user(user_id)

def unban_user(user_id: int):
    """Розблокування користувача"""
    return auth_middleware.unban_user(user_id)

def add_admin(user_id: int):
    """Додавання адміністратора"""
    return auth_middleware.add_admin(user_id)

def remove_admin(user_id: int):
    """Видалення адміністратора"""
    return auth_middleware.remove_admin(user_id)

def get_active_users(hours: int = 24) -> list:
    """Отримання активних користувачів"""
    return tracking_middleware.get_active_users(hours)

# Експорт основних класів
__all__ = [
    "LoggingMiddleware",
    "AntiSpamMiddleware", 
    "AuthMiddleware",
    "UserTrackingMiddleware",
    "is_admin",
    "get_user_permissions",
    "ban_user",
    "unban_user",
    "add_admin",
    "remove_admin",
    "get_active_users"
]