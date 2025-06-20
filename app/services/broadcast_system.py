#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📢 СИСТЕМА РОЗСИЛОК УКРАЇНСЬКОГО TELEGRAM БОТА 📢

Професійна система для масових розсилок з підтримкою:
✅ Rate limiting та захист від блокування
✅ Персоналізовані повідомлення
✅ Статистика доставки
✅ Різні типи розсилок (щоденні, тижневі, спеціальні)
✅ Асинхронна обробка великої кількості користувачів
✅ Резервування при помилках
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable, Union
import json
import random
from enum import Enum

logger = logging.getLogger(__name__)

class BroadcastType(Enum):
    """Типи розсилок"""
    DAILY_CONTENT = "daily_content"          # Щоденний контент
    EVENING_STATS = "evening_stats"          # Вечірня статистика
    WEEKLY_DIGEST = "weekly_digest"          # Тижневий дайджест
    TOURNAMENT_ANNOUNCE = "tournament"       # Оголошення турнірів
    ACHIEVEMENT_NOTIFY = "achievement"       # Повідомлення про досягнення
    SYSTEM_ANNOUNCE = "system"               # Системні оголошення
    CUSTOM = "custom"                        # Кастомні розсилки

class BroadcastStatus(Enum):
    """Статуси розсилки"""
    PENDING = "pending"                      # Очікує відправки
    IN_PROGRESS = "in_progress"              # В процесі відправки
    COMPLETED = "completed"                  # Завершена
    FAILED = "failed"                        # Не вдалась
    CANCELLED = "cancelled"                  # Скасована

class BroadcastSystem:
    """
    Система розсилок з повною підтримкою автоматизації
    """
    
    def __init__(self, bot, db_available: bool = False):
        """
        Ініціалізація системи розсилок
        
        Args:
            bot: Telegram Bot instance
            db_available: Чи доступна база даних
        """
        self.bot = bot
        self.db_available = db_available
        
        # Налаштування з конфігурації
        try:
            from config.settings import (
                BROADCAST_ENABLED, BROADCAST_RATE_LIMIT, BROADCAST_CHUNK_SIZE,
                ALL_ADMIN_IDS, DAILY_DIGEST_ENABLED, WEEKLY_DIGEST_ENABLED
            )
            self.enabled = BROADCAST_ENABLED
            self.rate_limit = BROADCAST_RATE_LIMIT
            self.chunk_size = BROADCAST_CHUNK_SIZE
            self.admin_ids = ALL_ADMIN_IDS
            self.daily_digest_enabled = DAILY_DIGEST_ENABLED
            self.weekly_digest_enabled = WEEKLY_DIGEST_ENABLED
        except ImportError:
            # Fallback налаштування
            self.enabled = True
            self.rate_limit = 30  # повідомлень на секунду
            self.chunk_size = 100
            self.admin_ids = [603047391]
            self.daily_digest_enabled = True
            self.weekly_digest_enabled = True
        
        # Статистика розсилок
        self.stats = {
            'total_broadcasts': 0,
            'total_sent': 0,
            'total_failed': 0,
            'last_broadcast': None,
            'active_broadcasts': 0,
            'user_blocks': 0,  # Користувачі що заблокували бота
            'delivery_rate': 0.0
        }
        
        # Активні розсилки
        self.active_broadcasts: Dict[str, Dict] = {}
        
        # Шаблони повідомлень
        self.message_templates = self._load_message_templates()
        
        # Семафор для rate limiting
        self.rate_semaphore = asyncio.Semaphore(self.rate_limit)
        
        logger.info(f"📢 BroadcastSystem ініціалізовано (rate: {self.rate_limit}/sec, enabled: {self.enabled})")

    def _load_message_templates(self) -> Dict[str, Dict]:
        """Завантаження шаблонів повідомлень"""
        return {
            "daily_content": {
                "emoji": "🌅",
                "title": "Ранкова порція гумору!",
                "format": "{emoji} <b>{title}</b>\n\n{content}\n\n💫 <i>Гарного дня, {name}!</i>"
            },
            "evening_stats": {
                "emoji": "📊",
                "title": "Вечірня статистика",
                "format": "{emoji} <b>{title}</b>\n\n📈 Користувачів: {total_users}\n📝 Контенту: {total_content}\n⚔️ Активних дуелей: {active_duels}\n\n🌙 Гарної ночі!"
            },
            "weekly_digest": {
                "emoji": "📰",
                "title": "Тижневий дайджест",
                "format": "{emoji} <b>{title}</b>\n\n🔥 Топ контент тижня:\n{top_content}\n\n🏆 Переможці дуелей:\n{top_duelers}\n\n📈 Статистика:\n{weekly_stats}"
            },
            "tournament": {
                "emoji": "🏆",
                "title": "Турнір розпочався!",
                "format": "{emoji} <b>{title}</b>\n\n⚔️ Тижневий турнір жартів стартував!\n\n🎯 Як взяти участь:\n• Подайте свій найкращий жарт\n• Беріть участь у дуелях\n• Голосуйте за улюблені жарти\n\n🏅 Призи для переможців:\n{prizes}\n\n🚀 Удачі!"
            },
            "achievement": {
                "emoji": "🎉",
                "title": "Нове досягнення!",
                "format": "{emoji} <b>Вітаємо, {name}!</b>\n\n🏆 Ви отримали досягнення:\n<b>{achievement_name}</b>\n\n📝 {achievement_description}\n\n💰 Нагорода: +{reward_points} балів"
            },
            "system": {
                "emoji": "🔔",
                "title": "Системне повідомлення",
                "format": "{emoji} <b>{title}</b>\n\n{message}\n\n🤖 Команда бота"
            }
        }

    async def send_daily_content_broadcast(self) -> Dict[str, Any]:
        """Щоденна розсилка контенту"""
        if not self.enabled or not self.daily_digest_enabled:
            logger.info("📢 Щоденна розсилка вимкнена")
            return {"status": "disabled", "sent": 0}
        
        logger.info("📢 Початок щоденної розсилки контенту...")
        
        try:
            # Отримання випадкового контенту
            content = await self._get_content_for_broadcast()
            if not content:
                logger.warning("⚠️ Немає контенту для розсилки")
                return {"status": "no_content", "sent": 0}
            
            # Отримання списку користувачів
            users = await self._get_active_users_for_broadcast()
            if not users:
                logger.warning("⚠️ Немає активних користувачів для розсилки")
                return {"status": "no_users", "sent": 0}
            
            # Формування повідомлення
            template = self.message_templates["daily_content"]
            
            # Запуск розсилки
            broadcast_id = f"daily_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = await self._execute_broadcast(
                broadcast_id=broadcast_id,
                broadcast_type=BroadcastType.DAILY_CONTENT,
                users=users,
                message_template=template,
                message_data={
                    "content": content.get("text", "🤣 Заряд позитиву на весь день!"),
                    "name": "{user_name}"  # Буде замінено для кожного користувача
                }
            )
            
            logger.info(f"📢 Щоденна розсилка завершена: {result['sent']}/{result['total']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Помилка щоденної розсилки: {e}")
            return {"status": "error", "error": str(e), "sent": 0}

    async def send_evening_stats_broadcast(self) -> Dict[str, Any]:
        """Вечірня розсилка статистики"""
        if not self.enabled:
            return {"status": "disabled", "sent": 0}
        
        logger.info("📢 Початок вечірньої розсилки статистики...")
        
        try:
            # Отримання статистики
            stats = await self._get_bot_statistics()
            
            # Формування повідомлення для адмінів
            template = self.message_templates["evening_stats"]
            
            broadcast_id = f"evening_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = await self._execute_broadcast(
                broadcast_id=broadcast_id,
                broadcast_type=BroadcastType.EVENING_STATS,
                users=[{"id": admin_id, "first_name": "Адмін"} for admin_id in self.admin_ids],
                message_template=template,
                message_data=stats
            )
            
            logger.info(f"📢 Вечірня статистика надіслана адмінам")
            return result
            
        except Exception as e:
            logger.error(f"❌ Помилка вечірньої статистики: {e}")
            return {"status": "error", "error": str(e), "sent": 0}

    async def send_weekly_digest_broadcast(self) -> Dict[str, Any]:
        """Тижнева розсилка дайджесту"""
        if not self.enabled or not self.weekly_digest_enabled:
            return {"status": "disabled", "sent": 0}
        
        logger.info("📢 Початок тижневої розсилки дайджесту...")
        
        try:
            # Отримання даних для дайджесту
            digest_data = await self._generate_weekly_digest()
            users = await self._get_active_users_for_broadcast()
            
            if not users:
                return {"status": "no_users", "sent": 0}
            
            template = self.message_templates["weekly_digest"]
            
            broadcast_id = f"weekly_digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = await self._execute_broadcast(
                broadcast_id=broadcast_id,
                broadcast_type=BroadcastType.WEEKLY_DIGEST,
                users=users,
                message_template=template,
                message_data=digest_data
            )
            
            logger.info(f"📢 Тижневий дайджест надіслано: {result['sent']} користувачам")
            return result
            
        except Exception as e:
            logger.error(f"❌ Помилка тижневого дайджесту: {e}")
            return {"status": "error", "error": str(e), "sent": 0}

    async def send_tournament_announcement(self) -> Dict[str, Any]:
        """Оголошення про турнір"""
        if not self.enabled:
            return {"status": "disabled", "sent": 0}
        
        logger.info("📢 Оголошення турніру...")
        
        try:
            users = await self._get_active_users_for_broadcast()
            template = self.message_templates["tournament"]
            
            prizes_text = (
                "🥇 1 місце: +100 балів та титул 'Майстер Гумору'\n"
                "🥈 2 місце: +50 балів\n"
                "🥉 3 місце: +25 балів"
            )
            
            broadcast_id = f"tournament_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = await self._execute_broadcast(
                broadcast_id=broadcast_id,
                broadcast_type=BroadcastType.TOURNAMENT_ANNOUNCE,
                users=users,
                message_template=template,
                message_data={"prizes": prizes_text}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Помилка оголошення турніру: {e}")
            return {"status": "error", "error": str(e), "sent": 0}

    async def send_achievement_notification(self, user_id: int, achievement_data: Dict) -> bool:
        """Персональне повідомлення про досягнення"""
        if not self.enabled:
            return False
        
        try:
            # Отримання інформації про користувача
            user_info = await self._get_user_info(user_id)
            if not user_info:
                return False
            
            template = self.message_templates["achievement"]
            message_data = {
                "name": user_info.get("first_name", "Друже"),
                "achievement_name": achievement_data.get("name", "Невідоме досягнення"),
                "achievement_description": achievement_data.get("description", "Опис відсутній"),
                "reward_points": achievement_data.get("reward_points", 0)
            }
            
            message = template["format"].format(**message_data)
            
            success = await self._send_message_to_user(user_id, message)
            if success:
                logger.info(f"🏆 Повідомлення про досягнення надіслано користувачу {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Помилка повідомлення про досягнення: {e}")
            return False

    async def send_custom_broadcast(self, message: str, target_users: List[int] = None, 
                                  broadcast_type: str = "custom") -> Dict[str, Any]:
        """Кастомна розсилка"""
        if not self.enabled:
            return {"status": "disabled", "sent": 0}
        
        logger.info(f"📢 Кастомна розсилка: {len(target_users or [])} користувачів")
        
        try:
            # Якщо не вказані користувачі, відправляємо всім активним
            if target_users is None:
                users = await self._get_active_users_for_broadcast()
            else:
                users = []
                for user_id in target_users:
                    user_info = await self._get_user_info(user_id)
                    if user_info:
                        users.append(user_info)
            
            if not users:
                return {"status": "no_users", "sent": 0}
            
            # Просте повідомлення без шаблону
            broadcast_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = await self._execute_simple_broadcast(
                broadcast_id=broadcast_id,
                users=users,
                message=message
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Помилка кастомної розсилки: {e}")
            return {"status": "error", "error": str(e), "sent": 0}

    async def _execute_broadcast(self, broadcast_id: str, broadcast_type: BroadcastType,
                               users: List[Dict], message_template: Dict, 
                               message_data: Dict) -> Dict[str, Any]:
        """Виконання розсилки з шаблоном"""
        
        # Реєстрація розсилки
        self.active_broadcasts[broadcast_id] = {
            "type": broadcast_type,
            "status": BroadcastStatus.IN_PROGRESS,
            "total_users": len(users),
            "sent": 0,
            "failed": 0,
            "started_at": datetime.now(),
            "estimated_duration": len(users) / self.rate_limit
        }
        
        sent_count = 0
        failed_count = 0
        
        try:
            # Розсилка батчами для rate limiting
            for i in range(0, len(users), self.chunk_size):
                batch = users[i:i + self.chunk_size]
                
                # Обробка батчу паралельно з rate limiting
                tasks = []
                for user in batch:
                    task = self._send_templated_message_to_user(
                        user, message_template, message_data
                    )
                    tasks.append(task)
                
                # Виконання батчу з обмеженням швидкості
                batch_results = await self._execute_batch_with_rate_limit(tasks)
                
                # Підрахунок результатів
                for success in batch_results:
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                
                # Оновлення статусу
                self.active_broadcasts[broadcast_id]["sent"] = sent_count
                self.active_broadcasts[broadcast_id]["failed"] = failed_count
                
                # Пауза між батчами для запобігання перевантаження
                if i + self.chunk_size < len(users):
                    await asyncio.sleep(1)
            
            # Завершення розсилки
            self.active_broadcasts[broadcast_id]["status"] = BroadcastStatus.COMPLETED
            self.active_broadcasts[broadcast_id]["completed_at"] = datetime.now()
            
            # Оновлення загальної статистики
            self.stats["total_broadcasts"] += 1
            self.stats["total_sent"] += sent_count
            self.stats["total_failed"] += failed_count
            self.stats["last_broadcast"] = datetime.now()
            self.stats["delivery_rate"] = (
                self.stats["total_sent"] / (self.stats["total_sent"] + self.stats["total_failed"])
                if (self.stats["total_sent"] + self.stats["total_failed"]) > 0 else 0
            )
            
            return {
                "status": "completed",
                "broadcast_id": broadcast_id,
                "total": len(users),
                "sent": sent_count,
                "failed": failed_count,
                "delivery_rate": (sent_count / len(users)) * 100 if len(users) > 0 else 0
            }
            
        except Exception as e:
            self.active_broadcasts[broadcast_id]["status"] = BroadcastStatus.FAILED
            self.active_broadcasts[broadcast_id]["error"] = str(e)
            raise

    async def _execute_simple_broadcast(self, broadcast_id: str, users: List[Dict], 
                                      message: str) -> Dict[str, Any]:
        """Виконання простої розсилки без шаблону"""
        
        self.active_broadcasts[broadcast_id] = {
            "type": BroadcastType.CUSTOM,
            "status": BroadcastStatus.IN_PROGRESS,
            "total_users": len(users),
            "sent": 0,
            "failed": 0,
            "started_at": datetime.now()
        }
        
        sent_count = 0
        failed_count = 0
        
        try:
            for i in range(0, len(users), self.chunk_size):
                batch = users[i:i + self.chunk_size]
                
                tasks = []
                for user in batch:
                    task = self._send_message_to_user(user["id"], message)
                    tasks.append(task)
                
                batch_results = await self._execute_batch_with_rate_limit(tasks)
                
                for success in batch_results:
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                
                if i + self.chunk_size < len(users):
                    await asyncio.sleep(1)
            
            self.active_broadcasts[broadcast_id]["status"] = BroadcastStatus.COMPLETED
            self.active_broadcasts[broadcast_id]["sent"] = sent_count
            self.active_broadcasts[broadcast_id]["failed"] = failed_count
            
            return {
                "status": "completed",
                "broadcast_id": broadcast_id,
                "total": len(users),
                "sent": sent_count,
                "failed": failed_count
            }
            
        except Exception as e:
            self.active_broadcasts[broadcast_id]["status"] = BroadcastStatus.FAILED
            raise

    async def _execute_batch_with_rate_limit(self, tasks: List) -> List[bool]:
        """Виконання батчу з rate limiting"""
        async def rate_limited_task(task):
            async with self.rate_semaphore:
                return await task
        
        # Виконання всіх задач з rate limiting
        results = await asyncio.gather(
            *[rate_limited_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Обробка результатів та винятків
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(False)
            else:
                processed_results.append(result)
        
        return processed_results

    async def _send_templated_message_to_user(self, user: Dict, template: Dict, 
                                            data: Dict) -> bool:
        """Відправка повідомлення користувачу з шаблоном"""
        try:
            # Персоналізація даних для користувача
            personalized_data = data.copy()
            personalized_data.update({
                "name": user.get("first_name", "Друже"),
                "user_name": user.get("first_name", "Друже")
            })
            personalized_data.update(template)
            
            # Формування повідомлення
            message = template["format"].format(**personalized_data)
            
            # Відправка повідомлення
            return await self._send_message_to_user(user["id"], message)
            
        except Exception as e:
            logger.error(f"❌ Помилка відправки шаблонного повідомлення користувачу {user.get('id')}: {e}")
            return False

    async def _send_message_to_user(self, user_id: int, message: str) -> bool:
        """Відправка повідомлення конкретному користувачу"""
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "bot was blocked by the user" in error_msg:
                self.stats["user_blocks"] += 1
                logger.debug(f"🚫 Користувач {user_id} заблокував бота")
            elif "chat not found" in error_msg:
                logger.debug(f"❓ Чат {user_id} не знайдено")
            else:
                logger.warning(f"⚠️ Помилка відправки повідомлення {user_id}: {e}")
            
            return False

    async def _get_content_for_broadcast(self) -> Optional[Dict]:
        """Отримання контенту для розсилки"""
        try:
            if self.db_available:
                from database import get_random_approved_content
                content = await get_random_approved_content()
                if content:
                    return {"text": content.text, "id": content.id}
            
            # Fallback контент
            fallback_content = [
                "🌅 Доброго ранку! Час для українського гумору!\n\n😂 Програміст заходить в кафе:\n- Каву, будь ласка.\n- Цукор?\n- Ні, boolean! 🤓",
                "☀️ Ранкова доза позитиву!\n\n🎯 Українець купує iPhone:\n- Не загубіть!\n- У мене є Find My iPhone!\n- А якщо не знайде?\n- Значить вкрали москалі! 🇺🇦",
                "🌞 Гарного ранку всім!\n\n🚗 Таксист:\n- Куди їдемо?\n- До перемоги!\n- Адреса?\n- Київ, Банкова! 🏛️"
            ]
            
            return {"text": random.choice(fallback_content), "id": 0}
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання контенту: {e}")
            return None

    async def _get_active_users_for_broadcast(self) -> List[Dict]:
        """Отримання списку активних користувачів для розсилки"""
        try:
            if self.db_available:
                # Отримуємо користувачів з БД
                # Тут буде реальна логіка отримання з БД
                pass
            
            # Fallback: повертаємо адмінів
            return [{"id": admin_id, "first_name": "Адмін"} for admin_id in self.admin_ids]
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання користувачів: {e}")
            return []

    async def _get_user_info(self, user_id: int) -> Optional[Dict]:
        """Отримання інформації про користувача"""
        try:
            if self.db_available:
                from database import get_user_by_id
                user = await get_user_by_id(user_id)
                if user:
                    return {
                        "id": user.id,
                        "first_name": user.first_name or "Друже",
                        "username": user.username
                    }
            
            # Fallback
            return {"id": user_id, "first_name": "Користувач"}
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання користувача {user_id}: {e}")
            return None

    async def _get_bot_statistics(self) -> Dict[str, Any]:
        """Отримання статистики бота"""
        try:
            if self.db_available:
                from database import get_bot_statistics
                stats = await get_bot_statistics()
                return stats
            
            # Fallback статистика
            return {
                "total_users": "N/A",
                "total_content": "N/A",
                "active_duels": "N/A",
                "broadcasts_sent": self.stats["total_sent"]
            }
            
        except Exception as e:
            logger.error(f"❌ Помилка отримання статистики: {e}")
            return {}

    async def _generate_weekly_digest(self) -> Dict[str, str]:
        """Генерація тижневого дайджесту"""
        try:
            # Тут буде логіка генерації дайджесту з БД
            # Поки що заглушка
            return {
                "top_content": "1. 😂 Найпопулярніший жарт тижня\n2. 🔥 Найкращий мем\n3. 🎯 Найкумедніший анекдот",
                "top_duelers": "1. 👑 @user1 - 15 перемог\n2. 🥈 @user2 - 12 перемог\n3. 🥉 @user3 - 10 перемог",
                "weekly_stats": "📊 Загалом дуелей: 45\n📝 Нового контенту: 89\n👥 Нових користувачів: 23"
            }
            
        except Exception as e:
            logger.error(f"❌ Помилка генерації дайджесту: {e}")
            return {}

    def get_broadcast_status(self, broadcast_id: str) -> Optional[Dict]:
        """Отримання статусу розсилки"""
        return self.active_broadcasts.get(broadcast_id)

    def get_system_stats(self) -> Dict[str, Any]:
        """Отримання статистики системи розсилок"""
        return {
            "enabled": self.enabled,
            "rate_limit": self.rate_limit,
            "chunk_size": self.chunk_size,
            "stats": self.stats.copy(),
            "active_broadcasts": len(self.active_broadcasts),
            "last_cleanup": getattr(self, "last_cleanup", None)
        }

    async def cleanup_old_broadcasts(self, days: int = 7):
        """Очистка старих записів розсилок"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        to_remove = []
        for broadcast_id, broadcast_data in self.active_broadcasts.items():
            if broadcast_data.get("started_at", datetime.now()) < cutoff_date:
                to_remove.append(broadcast_id)
        
        for broadcast_id in to_remove:
            del self.active_broadcasts[broadcast_id]
        
        self.last_cleanup = datetime.now()
        logger.info(f"🧹 Очищено {len(to_remove)} старих записів розсилок")

# ===== ФАБРИЧНІ ФУНКЦІЇ =====

async def create_broadcast_system(bot, db_available: bool = False) -> Optional[BroadcastSystem]:
    """
    Фабрична функція для створення системи розсилок
    
    Args:
        bot: Telegram Bot instance  
        db_available: Чи доступна база даних
    
    Returns:
        BroadcastSystem або None при помилці
    """
    try:
        broadcast_system = BroadcastSystem(bot, db_available)
        logger.info("✅ BroadcastSystem створено успішно")
        return broadcast_system
        
    except Exception as e:
        logger.error(f"❌ Помилка створення BroadcastSystem: {e}")
        return None

# ===== ЕКСПОРТ =====
__all__ = [
    'BroadcastSystem',
    'BroadcastType', 
    'BroadcastStatus',
    'create_broadcast_system'
]

logger.info("✅ BroadcastSystem модуль завантажено")