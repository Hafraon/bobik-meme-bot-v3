#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 ПРОФЕСІЙНИЙ ПЛАНУВАЛЬНИК ЗАДАЧ 🧠😂🔥
Щоденна розсилка, очищення даних, статистика та інше
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
import pytz

logger = logging.getLogger(__name__)

# Fallback налаштування
try:
    from config.settings import settings
    DAILY_BROADCAST_HOUR = getattr(settings, 'DAILY_BROADCAST_HOUR', 9)
    DAILY_BROADCAST_MINUTE = getattr(settings, 'DAILY_BROADCAST_MINUTE', 0)
    TIMEZONE = getattr(settings, 'TIMEZONE', 'Europe/Kiev')
    POINTS_FOR_DAILY_ACTIVITY = getattr(settings, 'POINTS_FOR_DAILY_ACTIVITY', 2)
except ImportError:
    import os
    DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
    DAILY_BROADCAST_MINUTE = int(os.getenv("DAILY_BROADCAST_MINUTE", "0"))
    TIMEZONE = os.getenv("TIMEZONE", "Europe/Kiev")
    POINTS_FOR_DAILY_ACTIVITY = int(os.getenv("POINTS_FOR_DAILY_ACTIVITY", "2"))

EMOJI = {
    "calendar": "📅", "fire": "🔥", "star": "⭐", "gem": "💎",
    "crown": "👑", "rocket": "🚀", "heart": "❤️", "wave": "👋"
}

class SchedulerService:
    """Сервіс планувальника задач"""
    
    def __init__(self, bot):
        self.bot = bot
        self.is_running = False
        self.tasks = []
        self.timezone = pytz.timezone(TIMEZONE)
        self.last_daily_broadcast = None
        
    async def start(self):
        """Запустити планувальник"""
        if self.is_running:
            logger.warning("⚠️ Планувальник вже запущений")
            return
        
        self.is_running = True
        logger.info("📅 Запуск планувальника задач...")
        
        # Створити задачі
        self.tasks = [
            asyncio.create_task(self._daily_broadcast_loop()),
            asyncio.create_task(self._hourly_maintenance_loop()),
            asyncio.create_task(self._duel_completion_check_loop()),
            asyncio.create_task(self._statistics_update_loop())
        ]
        
        logger.info("✅ Планувальник задач запущено")
    
    async def stop(self):
        """Зупинити планувальник"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("🛑 Зупинка планувальника задач...")
        
        # Скасувати всі задачі
        for task in self.tasks:
            task.cancel()
        
        # Дочекатися завершення
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("✅ Планувальник задач зупинено")
    
    # ===== ЩОДЕННА РОЗСИЛКА =====
    
    async def _daily_broadcast_loop(self):
        """Цикл щоденної розсилки"""
        logger.info(f"📅 Розсилка налаштована на {DAILY_BROADCAST_HOUR:02d}:{DAILY_BROADCAST_MINUTE:02d}")
        
        while self.is_running:
            try:
                await self._check_daily_broadcast()
                await asyncio.sleep(60)  # Перевіряємо кожну хвилину
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Помилка циклу розсилки: {e}")
                await asyncio.sleep(300)  # 5 хвилин при помилці
    
    async def _check_daily_broadcast(self):
        """Перевірити чи час для щоденної розсилки"""
        now = datetime.now(self.timezone)
        
        # Перевірити чи правильний час
        if now.hour != DAILY_BROADCAST_HOUR or now.minute != DAILY_BROADCAST_MINUTE:
            return
        
        # Перевірити чи вже була розсилка сьогодні
        today = now.date()
        if self.last_daily_broadcast == today:
            return
        
        logger.info("📢 Починаю щоденну розсилку...")
        await self._perform_daily_broadcast()
        self.last_daily_broadcast = today
    
    async def _perform_daily_broadcast(self):
        """Виконати щоденну розсилку"""
        try:
            from database import get_db_session, get_random_approved_content, update_user_points
            from database.models import User
            
            # Отримати випадковий контент
            daily_joke = await get_random_approved_content("JOKE")
            daily_meme = await get_random_approved_content("MEME")
            
            if not daily_joke and not daily_meme:
                logger.warning("⚠️ Немає контенту для щоденної розсилки")
                return
            
            # Отримати підписаних користувачів
            with get_db_session() as session:
                subscribed_users = session.query(User).filter(
                    User.daily_subscription == True
                ).all()
            
            if not subscribed_users:
                logger.info("📭 Немає підписаних користувачів")
                return
            
            logger.info(f"📬 Розсилка для {len(subscribed_users)} користувачів")
            
            # Підготувати повідомлення
            broadcast_text = self._prepare_daily_message(daily_joke, daily_meme)
            
            # Відправити всім підписаним
            success_count = 0
            for user in subscribed_users:
                try:
                    await self.bot.send_message(user.id, broadcast_text)
                    
                    # Нарахувати бали за щоденну активність
                    await update_user_points(user.id, POINTS_FOR_DAILY_ACTIVITY, "щоденна розсилка")
                    
                    success_count += 1
                    await asyncio.sleep(0.1)  # Невелика затримка між повідомленнями
                    
                except Exception as e:
                    logger.warning(f"⚠️ Не вдалося надіслати користувачу {user.id}: {e}")
            
            logger.info(f"✅ Щоденна розсилка завершена: {success_count}/{len(subscribed_users)}")
            
            # Записати статистику
            await self._record_broadcast_stats(len(subscribed_users), success_count)
            
        except Exception as e:
            logger.error(f"❌ Помилка щоденної розсилки: {e}")
    
    def _prepare_daily_message(self, joke=None, meme=None):
        """Підготувати повідомлення для щоденної розсилки"""
        now = datetime.now(self.timezone)
        
        # Контекстне привітання
        if now.hour < 12:
            greeting = "Доброго ранку"
            greeting_emoji = "🌅"
        elif now.hour < 18:
            greeting = "Гарного дня"
            greeting_emoji = "☀️"
        else:
            greeting = "Доброго вечора"
            greeting_emoji = "🌆"
        
        message = f"{greeting_emoji} <b>{greeting}!</b>\n\n"
        message += f"{EMOJI['calendar']} <b>Щоденна порція гумору</b>\n"
        message += f"📅 {now.strftime('%d.%m.%Y')}\n\n"
        
        # Додати жарт
        if joke:
            message += f"{EMOJI['fire']} <b>Жарт дня:</b>\n"
            message += f"<i>{joke.text}</i>\n\n"
        
        # Додати мем
        if meme:
            message += f"{EMOJI['rocket']} <b>Мем дня:</b>\n"
            message += f"<i>{meme.text}</i>\n\n"
        
        message += f"{EMOJI['gem']} <b>+{POINTS_FOR_DAILY_ACTIVITY} балів за щоденну активність!</b>\n\n"
        
        # Заклик до дії
        message += f"🎮 Не забудьте:\n"
        message += f"• Переглянути нові меми /meme\n"
        message += f"• Почитати анекдоти /anekdot\n"
        message += f"• Взяти участь в дуелях /duel\n"
        message += f"• Подивитися свій прогрес /profile\n\n"
        
        message += f"{EMOJI['heart']} Гарного дня та багато сміху!"
        
        return message
    
    async def _record_broadcast_stats(self, total_users: int, successful_sends: int):
        """Записати статистику розсилки"""
        try:
            from database import get_db_session
            
            # Тут можна було б записати в окрему таблицю статистики розсилок
            logger.info(f"📊 Статистика розсилки: {successful_sends}/{total_users} ({successful_sends/total_users*100:.1f}%)")
            
        except Exception as e:
            logger.error(f"❌ Помилка запису статистики розсилки: {e}")
    
    # ===== ЩОГОДИННЕ ОБСЛУГОВУВАННЯ =====
    
    async def _hourly_maintenance_loop(self):
        """Цикл щогодинного обслуговування"""
        while self.is_running:
            try:
                await self._perform_hourly_maintenance()
                await asyncio.sleep(3600)  # Кожну годину
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Помилка щогодинного обслуговування: {e}")
                await asyncio.sleep(1800)  # 30 хвилин при помилці
    
    async def _perform_hourly_maintenance(self):
        """Виконати щогодинне обслуговування"""
        try:
            logger.debug("🔧 Щогодинне обслуговування...")
            
            # Очистити старі дані
            await self._cleanup_old_data()
            
            # Оновити статистику
            await self._update_statistics()
            
            # Перевірити завершені дуелі
            await self._cleanup_completed_duels()
            
            logger.debug("✅ Щогодинне обслуговування завершено")
            
        except Exception as e:
            logger.error(f"❌ Помилка щогодинного обслуговування: {e}")
    
    async def _cleanup_old_data(self):
        """Очистити старі дані"""
        try:
            from database import get_db_session
            from database.models import Duel, Rating
            
            # Видалити старі завершені дуелі (старші 7 днів)
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            with get_db_session() as session:
                old_duels = session.query(Duel).filter(
                    Duel.status == 'COMPLETED',
                    Duel.completed_at < week_ago
                ).delete()
                
                if old_duels > 0:
                    session.commit()
                    logger.info(f"🗑️ Видалено {old_duels} старих дуелів")
            
        except Exception as e:
            logger.error(f"❌ Помилка очищення даних: {e}")
    
    async def _update_statistics(self):
        """Оновити статистику"""
        try:
            from database import update_bot_statistics
            await update_bot_statistics()
            logger.debug("📊 Статистика оновлена")
            
        except Exception as e:
            logger.error(f"❌ Помилка оновлення статистики: {e}")
    
    async def _cleanup_completed_duels(self):
        """Очистити завершені дуелі"""
        try:
            from database import get_db_session
            from database.models import Duel
            
            with get_db_session() as session:
                # Знайти "заморожені" дуелі (активні більше 24 годин)
                day_ago = datetime.utcnow() - timedelta(hours=24)
                
                frozen_duels = session.query(Duel).filter(
                    Duel.status == 'ACTIVE',
                    Duel.created_at < day_ago
                ).all()
                
                for duel in frozen_duels:
                    duel.status = 'CANCELLED'
                    logger.info(f"❄️ Скасовано заморожений дуель #{duel.id}")
                
                if frozen_duels:
                    session.commit()
            
        except Exception as e:
            logger.error(f"❌ Помилка очищення дуелів: {e}")
    
    # ===== ПЕРЕВІРКА ЗАВЕРШЕННЯ ДУЕЛІВ =====
    
    async def _duel_completion_check_loop(self):
        """Цикл перевірки завершення дуелів"""
        while self.is_running:
            try:
                await self._check_duel_completions()
                await asyncio.sleep(30)  # Кожні 30 секунд
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Помилка перевірки дуелів: {e}")
                await asyncio.sleep(60)
    
    async def _check_duel_completions(self):
        """Перевірити дуелі що потребують завершення"""
        try:
            from database import get_db_session
            from database.models import Duel
            
            with get_db_session() as session:
                # Знайти дуелі що мають завершитися
                now = datetime.utcnow()
                
                duels_to_complete = session.query(Duel).filter(
                    Duel.status == 'ACTIVE',
                    Duel.ends_at <= now
                ).all()
                
                for duel in duels_to_complete:
                    from handlers.duel_handlers import complete_duel
                    await complete_duel(self.bot, duel)
            
        except Exception as e:
            logger.error(f"❌ Помилка перевірки завершення дуелів: {e}")
    
    # ===== ОНОВЛЕННЯ СТАТИСТИКИ =====
    
    async def _statistics_update_loop(self):
        """Цикл оновлення детальної статистики"""
        while self.is_running:
            try:
                await self._update_detailed_statistics()
                await asyncio.sleep(1800)  # Кожні 30 хвилин
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Помилка оновлення статистики: {e}")
                await asyncio.sleep(900)  # 15 хвилин при помилці
    
    async def _update_detailed_statistics(self):
        """Оновити детальну статистику"""
        try:
            from database import get_db_session
            from database.models import User, Content, Duel, Rating
            from sqlalchemy import func
            
            with get_db_session() as session:
                # Загальна статистика
                stats = {
                    'total_users': session.query(User).count(),
                    'total_content': session.query(Content).count(),
                    'approved_content': session.query(Content).filter(Content.status == 'APPROVED').count(),
                    'total_duels': session.query(Duel).count(),
                    'total_ratings': session.query(Rating).count()
                }
                
                logger.debug(f"📊 Статистика: {stats}")
                
                # Тут можна було б зберегти в спеціальну таблицю статистики
                
        except Exception as e:
            logger.error(f"❌ Помилка детальної статистики: {e}")
    
    # ===== ПУБЛІЧНІ МЕТОДИ =====
    
    async def send_broadcast_message(self, message: str, target_group: str = "all"):
        """Надіслати розсилку вручну"""
        try:
            from database import get_db_session
            from database.models import User
            
            with get_db_session() as session:
                # Вибрати цільову групу
                if target_group == "all":
                    users = session.query(User).all()
                elif target_group == "active":
                    week_ago = datetime.utcnow() - timedelta(days=7)
                    users = session.query(User).filter(User.last_active >= week_ago).all()
                elif target_group == "subscribed":
                    users = session.query(User).filter(User.daily_subscription == True).all()
                else:
                    users = []
                
                if not users:
                    return {"success": False, "error": "Немає користувачів для розсилки"}
                
                # Відправити повідомлення
                success_count = 0
                for user in users:
                    try:
                        await self.bot.send_message(user.id, message)
                        success_count += 1
                        await asyncio.sleep(0.1)
                    except Exception:
                        pass
                
                return {
                    "success": True,
                    "total_users": len(users),
                    "successful_sends": success_count
                }
        
        except Exception as e:
            logger.error(f"❌ Помилка ручної розсилки: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_scheduler_status(self):
        """Отримати статус планувальника"""
        return {
            "is_running": self.is_running,
            "tasks_count": len(self.tasks),
            "last_daily_broadcast": self.last_daily_broadcast.isoformat() if self.last_daily_broadcast else None,
            "timezone": TIMEZONE,
            "broadcast_time": f"{DAILY_BROADCAST_HOUR:02d}:{DAILY_BROADCAST_MINUTE:02d}"
        }

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def schedule_task_at_time(target_time: time, task_func, *args, **kwargs):
    """Запланувати виконання задачі на конкретний час"""
    while True:
        now = datetime.now()
        
        # Розрахувати час до виконання
        target_datetime = datetime.combine(now.date(), target_time)
        
        # Якщо час вже минув сьогодні, запланувати на завтра
        if target_datetime <= now:
            target_datetime += timedelta(days=1)
        
        # Чекати до потрібного часу
        sleep_seconds = (target_datetime - now).total_seconds()
        await asyncio.sleep(sleep_seconds)
        
        # Виконати задачу
        try:
            await task_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Помилка запланованої задачі: {e}")

def create_scheduler_service(bot):
    """Створити сервіс планувальника"""
    return SchedulerService(bot)