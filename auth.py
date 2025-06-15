#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Middleware для аутентифікації та оновлення активності 🧠😂🔥
"""

import logging
from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User, Message, CallbackQuery

from database.database import get_or_create_user, get_db_session
from database.models import User as DBUser

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    """Middleware для аутентифікації та оновлення активності користувачів"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обробка події"""
        
        # Отримання користувача з події
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user and not user.is_bot:
            try:
                # Створення або оновлення користувача в БД
                db_user = await get_or_create_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                
                # Оновлення часу останньої активності
                await self.update_last_activity(user.id)
                
                # Додавання користувача до даних для хендлера
                data["db_user"] = db_user
                
            except Exception as e:
                logger.error(f"Помилка в AuthMiddleware: {e}")
                # Продовжуємо виконання навіть при помилці
        
        # Виклик наступного хендлера
        return await handler(event, data)
    
    async def update_last_activity(self, user_id: int):
        """Оновлення часу останньої активності користувача"""
        try:
            with get_db_session() as session:
                user = session.query(DBUser).filter(DBUser.id == user_id).first()
                if user:
                    user.last_active = datetime.utcnow()
                    session.commit()
        except Exception as e:
            logger.error(f"Помилка оновлення активності користувача {user_id}: {e}")

class AntiSpamMiddleware(BaseMiddleware):
    """Middleware для захисту від спаму"""
    
    def __init__(self, rate_limit: int = 3):
        """
        rate_limit: максимальна кількість повідомлень за секунду
        """
        self.rate_limit = rate_limit
        self.user_requests = {}  # {user_id: [timestamp1, timestamp2, ...]}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обробка події з перевіркою на спам"""
        
        # Отримання користувача
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user and not user.is_bot:
            current_time = datetime.now().timestamp()
            user_id = user.id
            
            # Ініціалізація списку запитів користувача
            if user_id not in self.user_requests:
                self.user_requests[user_id] = []
            
            # Очищення старих запитів (старше 1 секунди)
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id]
                if current_time - req_time < 1.0
            ]
            
            # Перевірка кількості запитів
            if len(self.user_requests[user_id]) >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                
                # Якщо це повідомлення, відправляємо попередження
                if isinstance(event, Message):
                    try:
                        await event.answer(
                            "⚠️ Забагато запитів! Зачекай трохи перед наступною командою."
                        )
                    except:
                        pass
                elif isinstance(event, CallbackQuery):
                    try:
                        await event.answer(
                            "⚠️ Забагато дій! Зачекай трохи.",
                            show_alert=True
                        )
                    except:
                        pass
                
                return  # Блокуємо виконання хендлера
            
            # Додавання поточного запиту
            self.user_requests[user_id].append(current_time)
        
        # Виклик наступного хендлера
        return await handler(event, data)

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логування активності користувачів"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Логування події"""
        
        # Логування повідомлень
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"📨 Message from {user.id} (@{user.username}): "
                f"{event.text[:50] if event.text else '[Media]'}..."
            )
        
        # Логування callback запитів
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"🔘 Callback from {user.id} (@{user.username}): {event.data}"
            )
        
        # Виклик наступного хендлера
        result = await handler(event, data)
        
        return result

class MaintenanceMiddleware(BaseMiddleware):
    """Middleware для режиму технічного обслуговування"""
    
    def __init__(self, maintenance_mode: bool = False, admin_id: int = None):
        self.maintenance_mode = maintenance_mode
        self.admin_id = admin_id
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Перевірка режиму обслуговування"""
        
        if not self.maintenance_mode:
            return await handler(event, data)
        
        # Отримання користувача
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        # Пропускаємо адміністратора
        if user and user.id == self.admin_id:
            return await handler(event, data)
        
        # Блокуємо всіх інших
        maintenance_text = (
            "🔧 <b>Технічне обслуговування</b>\n\n"
            "⏰ Бот тимчасово недоступний\n"
            "🔄 Очікується відновлення роботи незабаром\n"
            "💬 Дякуємо за розуміння!"
        )
        
        if isinstance(event, Message):
            try:
                await event.answer(maintenance_text)
            except:
                pass
        elif isinstance(event, CallbackQuery):
            try:
                await event.answer(
                    "🔧 Бот на технічному обслуговуванні",
                    show_alert=True
                )
            except:
                pass
        
        return  # Блокуємо виконання хендлера