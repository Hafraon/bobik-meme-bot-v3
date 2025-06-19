#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Middleware аутентифікації (ВИПРАВЛЕНО get_or_create_user) 🧠😂🔥
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable, Optional, Set

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логування всіх подій"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Логування повідомлень
        if isinstance(event, Message):
            user_info = f"{event.from_user.first_name} (@{event.from_user.username}) ID:{event.from_user.id}"
            if event.text:
                logger.info(f"📝 Повідомлення від {user_info}: {event.text}")
            elif event.photo:
                logger.info(f"📸 Фото від {user_info}")
            elif event.document:
                logger.info(f"📄 Документ від {user_info}")
            else:
                logger.info(f"💬 Повідомлення від {user_info}")
        
        # Логування callback запитів
        elif isinstance(event, CallbackQuery):
            user_info = f"{event.from_user.first_name} (@{event.from_user.username}) ID:{event.from_user.id}"
            logger.info(f"🔘 Callback від {user_info}: {event.data}")
        
        # Виклик наступного handler
        return await handler(event, data)

class AntiSpamMiddleware(BaseMiddleware):
    """Middleware для захисту від спаму"""
    
    def __init__(self, messages_per_second: int = 3):
        self.messages_per_second = messages_per_second
        self.user_last_message = {}
        self.user_message_count = {}
    
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
            current_second = int(time.time())
            
            # Перевірка кількості повідомлень за секунду
            if user_id in self.user_last_message:
                if self.user_last_message[user_id] == current_second:
                    self.user_message_count[user_id] += 1
                    
                    # Перевищення ліміту
                    if self.user_message_count[user_id] > self.messages_per_second:
                        logger.warning(f"🚫 Спам від користувача {user_id}")
                        
                        if isinstance(event, Message):
                            await event.answer(
                                "⚠️ Забагато запитів! Зачекай трохи...",
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
            else:
                # Перше повідомлення від користувача
                self.user_last_message[user_id] = current_second
                self.user_message_count[user_id] = 1
        
        # Виклик наступного handler
        return await handler(event, data)

class AuthMiddleware(BaseMiddleware):
    """Middleware для аутентифікації користувачів"""
    
    def __init__(self):
        self.banned_users: Set[int] = set()  # Заблоковані користувачі
        self.admin_users: Set[int] = set()   # Адміністратори
        
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
                await event.answer(
                    "🚫 Вас заблоковано в цьому боті!",
                    show_alert=True
                )
            
            return  # Не викликаємо handler
        
        # 🔥 ВИПРАВЛЕНО: Оновлення інформації про користувача
        try:
            from database import get_or_create_user
            # ✅ ПРАВИЛЬНИЙ ВИКЛИК - telegram_id як перший аргумент
            db_user = await get_or_create_user(
                telegram_id=user.id,  # ✅ ВИПРАВЛЕНО: був user.id як позиційний аргумент
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            if db_user:
                # Додання даних користувача до контексту
                data["user"] = db_user
                data["is_admin"] = user.id in self.admin_users
                data["user_permissions"] = self._get_user_permissions(db_user)
                
                logger.debug(f"✅ Користувач {user.id} успішно оновлено в middleware")
            else:
                logger.warning(f"⚠️ Не вдалося оновити користувача {user.id} в middleware")
                
        except Exception as e:
            logger.error(f"Помилка оновлення інформації користувача: {e}")
            # Не блокуємо виконання, якщо БД недоступна
        
        # Виклик наступного handler
        return await handler(event, data)
    
    def _get_user_permissions(self, user) -> Dict[str, bool]:
        """Отримання прав користувача"""
        permissions = {
            "can_submit_content": True,
            "can_vote_in_duels": True,
            "can_use_daily_subscription": True,
            "can_moderate": user.id in self.admin_users if hasattr(user, 'id') else False,
            "can_ban_users": user.id in self.admin_users if hasattr(user, 'id') else False,
        }
        
        return permissions
    
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
                    "last_seen": datetime.now(),
                    "message_count": 0,
                    "callback_count": 0,
                    "session_start": datetime.now()
                }
            
            # Оновлення статистики
            self.user_stats[user_id]["last_seen"] = datetime.now()
            
            if isinstance(event, Message):
                self.user_stats[user_id]["message_count"] += 1
            elif isinstance(event, CallbackQuery):
                self.user_stats[user_id]["callback_count"] += 1
            
            # Додання статистики до контексту
            data["user_stats"] = self.user_stats[user_id]
        
        # Виклик наступного handler
        return await handler(event, data)
    
    def get_active_users(self, hours: int = 24) -> list:
        """Отримання активних користувачів за останні X годин"""
        threshold = datetime.now() - timedelta(hours=hours)
        
        active_users = []
        for user_id, stats in self.user_stats.items():
            if stats["last_seen"] >= threshold:
                active_users.append({
                    "user_id": user_id,
                    "last_seen": stats["last_seen"],
                    "message_count": stats["message_count"],
                    "callback_count": stats["callback_count"]
                })
        
        return sorted(active_users, key=lambda x: x["last_seen"], reverse=True)

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