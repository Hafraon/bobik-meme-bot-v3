#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📢 СИСТЕМА РОЗУМНИХ РОЗСИЛОК

Автоматичні розсилки контенту, статистики та нагадувань
для підтримки активності користувачів
"""

import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest

logger = logging.getLogger(__name__)

class BroadcastSystem:
    """Система розумних розсилок"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_broadcasts = {}
        self.daily_content_sent = False
        self.weekly_stats_sent = False
        
    # ===== ЩОДЕННІ РОЗСИЛКИ =====
    
    async def send_daily_content(self):
        """Щоденна розсилка кращого контенту"""
        try:
            logger.info("📢 Початок щоденної розсилки контенту...")
            
            # Отримуємо активних користувачів
            active_users = await self.get_active_users(days=7)
            
            if not active_users:
                logger.info("Немає активних користувачів для розсилки")
                return
            
            # Отримуємо кращий контент за день
            daily_content = await self.get_daily_best_content()
            
            if not daily_content:
                logger.info("Немає контенту для щоденної розсилки")
                return
            
            # Створюємо повідомлення
            message_text, keyboard = self.create_daily_content_message(daily_content)
            
            # Відправляємо з обмеженням швидкості
            success_count = await self.send_broadcast(
                active_users, 
                message_text, 
                keyboard,
                delay=0.1  # 100мс між повідомленнями
            )
            
            logger.info(f"✅ Щоденна розсилка завершена: {success_count}/{len(active_users)}")
            self.daily_content_sent = True
            
        except Exception as e:
            logger.error(f"❌ Помилка щоденної розсилки: {e}")
    
    async def send_duel_reminders(self):
        """Нагадування про активні дуелі"""
        try:
            from database.services import get_active_duels, get_users_who_can_vote
            
            # Отримуємо активні дуелі що скоро завершуються
            active_duels = await get_active_duels(limit=5)
            expiring_duels = []
            
            for duel in active_duels:
                if duel.get('ends_at'):
                    time_left = duel['ends_at'] - datetime.utcnow()
                    if time_left.total_seconds() < 1800:  # менше 30 хвилин
                        expiring_duels.append(duel)
            
            if not expiring_duels:
                return
            
            # Отримуємо користувачів які ще не голосували
            for duel in expiring_duels:
                users_to_notify = await get_users_who_can_vote(duel['id'])
                
                if users_to_notify:
                    message_text, keyboard = self.create_duel_reminder_message(duel)
                    
                    await self.send_broadcast(
                        users_to_notify,
                        message_text,
                        keyboard,
                        delay=0.05
                    )
            
            logger.info(f"📢 Надіслано нагадувань про {len(expiring_duels)} дуелі")
            
        except Exception as e:
            logger.error(f"❌ Помилка нагадувань про дуелі: {e}")
    
    async def send_weekly_digest(self):
        """Тижневий дайджест статистики"""
        try:
            logger.info("📊 Початок тижневого дайджесту...")
            
            # Отримуємо всіх користувачів
            all_users = await self.get_all_users()
            
            # Генеруємо тижневу статистику
            weekly_stats = await self.generate_weekly_stats()
            
            # Створюємо повідомлення дайджесту
            message_text, keyboard = self.create_weekly_digest_message(weekly_stats)
            
            # Відправляємо
            success_count = await self.send_broadcast(
                all_users,
                message_text,
                keyboard,
                delay=0.2
            )
            
            logger.info(f"✅ Тижневий дайджест надіслано: {success_count}/{len(all_users)}")
            self.weekly_stats_sent = True
            
        except Exception as e:
            logger.error(f"❌ Помилка тижневого дайджесту: {e}")
    
    # ===== СПЕЦІАЛЬНІ РОЗСИЛКИ =====
    
    async def send_tournament_announcement(self, tournament_data: Dict):
        """Анонс турніру дуелів"""
        try:
            # Отримуємо активних дуелістів
            duel_participants = await self.get_duel_participants()
            
            message_text = (
                f"🏆 <b>АНОНС ТУРНІРУ ДУЕЛІВ!</b> 🏆\n\n"
                f"🎯 <b>{tournament_data.get('name', 'Великий турнір')}</b>\n\n"
                f"📅 Початок: {tournament_data.get('start_date', 'Завтра')}\n"
                f"⏰ Тривалість: {tournament_data.get('duration', '7 днів')}\n"
                f"🏆 Приз: {tournament_data.get('prize', '+500 балів переможцю')}\n\n"
                f"💡 Участь беруть автоматично всі дуелісти!\n"
                f"Створюйте жарти та перемагайте у дуелях!"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚔️ Дуелі жартів", callback_data="duel_menu")],
                [InlineKeyboardButton(text="📊 Мій рейтинг", callback_data="duel_stats")]
            ])
            
            await self.send_broadcast(duel_participants, message_text, keyboard)
            
        except Exception as e:
            logger.error(f"❌ Помилка анонсу турніру: {e}")
    
    async def send_maintenance_notification(self, maintenance_info: Dict):
        """Повідомлення про технічні роботи"""
        try:
            all_users = await self.get_all_users()
            
            message_text = (
                f"🔧 <b>ТЕХНІЧНІ РОБОТИ</b>\n\n"
                f"⏰ Час: {maintenance_info.get('time', 'незабаром')}\n"
                f"⌛ Тривалість: {maintenance_info.get('duration', '~30 хвилин')}\n\n"
                f"🎯 <b>Що покращимо:</b>\n"
                f"• {maintenance_info.get('improvements', 'Оптимізація роботи дуелів')}\n\n"
                f"💡 Бот може бути недоступний протягом робіт.\n"
                f"Дякуємо за розуміння!"
            )
            
            await self.send_broadcast(all_users, message_text, None, delay=0.3)
            
        except Exception as e:
            logger.error(f"❌ Помилка повідомлення про ТО: {e}")
    
    # ===== ПЕРСОНАЛЬНІ ПОВІДОМЛЕННЯ =====
    
    async def send_achievement_notifications(self):
        """Повідомлення про досягнення користувачів"""
        try:
            from database.services import get_recent_achievements
            
            # Отримуємо нові досягнення за останню добу
            achievements = await get_recent_achievements(hours=24)
            
            for achievement in achievements:
                try:
                    message_text = (
                        f"🏆 <b>НОВЕ ДОСЯГНЕННЯ!</b>\n\n"
                        f"🎯 {achievement['title']}\n"
                        f"📝 {achievement['description']}\n"
                        f"💰 Нагорода: +{achievement['points']} балів\n\n"
                        f"🎉 Вітаємо з досягненням!"
                    )
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="👤 Мій профіль", callback_data="profile")],
                        [InlineKeyboardButton(text="🏆 Всі досягнення", callback_data="achievements")]
                    ])
                    
                    await self.bot.send_message(
                        achievement['user_id'],
                        message_text,
                        reply_markup=keyboard
                    )
                    
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Помилка надсилання досягнення {achievement['id']}: {e}")
            
            if achievements:
                logger.info(f"📢 Надіслано {len(achievements)} повідомлень про досягнення")
                
        except Exception as e:
            logger.error(f"❌ Помилка повідомлень про досягнення: {e}")
    
    async def send_rank_up_notifications(self):
        """Повідомлення про підвищення рангу"""
        try:
            from database.services import get_recent_rank_ups
            
            rank_ups = await get_recent_rank_ups(hours=24)
            
            for rank_up in rank_ups:
                try:
                    message_text = (
                        f"⬆️ <b>ПІДВИЩЕННЯ РАНГУ!</b> ⬆️\n\n"
                        f"🎉 Вітаємо! Ви досягли нового рангу:\n"
                        f"👑 <b>{rank_up['new_rank']}</b>\n\n"
                        f"💰 Поточні бали: {rank_up['total_points']}\n"
                        f"🎯 До наступного рангу: {rank_up['points_to_next']}\n\n"
                        f"💡 Продовжуйте участь у дуелях та отримуйте бали!"
                    )
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⚔️ Дуелі", callback_data="duel_menu")],
                        [InlineKeyboardButton(text="👤 Профіль", callback_data="profile")]
                    ])
                    
                    await self.bot.send_message(
                        rank_up['user_id'],
                        message_text,
                        reply_markup=keyboard
                    )
                    
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Помилка надсилання rank up {rank_up['user_id']}: {e}")
            
            if rank_ups:
                logger.info(f"📢 Надіслано {len(rank_ups)} повідомлень про ранги")
                
        except Exception as e:
            logger.error(f"❌ Помилка повідомлень про ранги: {e}")
    
    # ===== ДОПОМІЖНІ МЕТОДИ =====
    
    async def send_broadcast(
        self, 
        users: List[Dict], 
        message: str, 
        keyboard: Optional[InlineKeyboardMarkup] = None,
        delay: float = 0.1
    ) -> int:
        """Надсилання розсилки з обмеженням швидкості"""
        success_count = 0
        failed_count = 0
        
        for user in users:
            try:
                await self.bot.send_message(
                    user['id'],
                    message,
                    reply_markup=keyboard
                )
                success_count += 1
                
                # Затримка між повідомленнями
                if delay > 0:
                    await asyncio.sleep(delay)
                    
            except TelegramRetryAfter as e:
                # Rate limit - чекаємо
                logger.warning(f"Rate limit: чекаємо {e.retry_after} секунд")
                await asyncio.sleep(e.retry_after)
                # Повторюємо спробу
                try:
                    await self.bot.send_message(user['id'], message, reply_markup=keyboard)
                    success_count += 1
                except:
                    failed_count += 1
                    
            except TelegramBadRequest as e:
                # Користувач заблокував бота або інша помилка
                if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
                    logger.debug(f"Користувач {user['id']} заблокував бота")
                    await self.mark_user_inactive(user['id'])
                failed_count += 1
                
            except Exception as e:
                logger.error(f"Помилка надсилання користувачу {user['id']}: {e}")
                failed_count += 1
        
        logger.info(f"📊 Розсилка завершена: ✅{success_count} ❌{failed_count}")
        return success_count
    
    def create_daily_content_message(self, content: Dict) -> tuple:
        """Створення повідомлення щоденного контенту"""
        
        # Контекстне привітання
        hour = datetime.now().hour
        if 6 <= hour < 12:
            greeting = "🌅 Доброго ранку!"
        elif 12 <= hour < 18:
            greeting = "☀️ Доброго дня!"
        elif 18 <= hour < 23:
            greeting = "🌆 Доброго вечора!"
        else:
            greeting = "🌙 Доброї ночі!"
        
        message_text = f"{greeting}\n\n"
        message_text += f"😂 <b>ЖАРТ ДНЯ</b> 😂\n\n"
        message_text += f"<i>{content.get('text', 'Завантаження...')}</i>\n\n"
        
        # Статистика
        if content.get('likes', 0) > 0:
            message_text += f"👍 {content['likes']} вподобань\n"
        
        message_text += f"\n🎯 Створіть свій жарт та беріть участь у дуелях!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Дуелі жартів", callback_data="duel_menu")],
            [
                InlineKeyboardButton(text="😂 Ще жарт", callback_data="get_joke"),
                InlineKeyboardButton(text="👤 Профіль", callback_data="profile")
            ],
            [InlineKeyboardButton(text="📝 Подати жарт", callback_data="submit_joke")]
        ])
        
        return message_text, keyboard
    
    def create_duel_reminder_message(self, duel: Dict) -> tuple:
        """Створення повідомлення нагадування про дуель"""
        
        time_left = duel['ends_at'] - datetime.utcnow()
        minutes_left = int(time_left.total_seconds() // 60)
        
        message_text = (
            f"⏰ <b>ДУЕЛЬ СКОРО ЗАВЕРШУЄТЬСЯ!</b>\n\n"
            f"⚔️ Дуель #{duel['id']}\n"
            f"⏱️ Залишилось: {minutes_left} хвилин\n"
            f"🗳️ Голосів: {duel.get('total_votes', 0)}\n\n"
            f"💡 Встигніть проголосувати за найкращий жарт!"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Голосувати", callback_data=f"view_duel_{duel['id']}")],
            [InlineKeyboardButton(text="🎯 Всі дуелі", callback_data="view_duels")]
        ])
        
        return message_text, keyboard
    
    def create_weekly_digest_message(self, stats: Dict) -> tuple:
        """Створення тижневого дайджесту"""
        
        message_text = (
            f"📊 <b>ТИЖНЕВИЙ ДАЙДЖЕСТ</b>\n\n"
            f"🎯 <b>Статистика тижня:</b>\n"
            f"⚔️ Дуелей проведено: {stats.get('duels_completed', 0)}\n"
            f"🗳️ Голосів подано: {stats.get('total_votes', 0)}\n"
            f"😂 Нових жартів: {stats.get('new_content', 0)}\n"
            f"👥 Активних користувачів: {stats.get('active_users', 0)}\n\n"
            
            f"🏆 <b>Топ дуеліст тижня:</b>\n"
            f"👑 {stats.get('top_duelist', 'Невідомо')}\n"
            f"🎯 Перемог: {stats.get('top_wins', 0)}\n\n"
            
            f"😂 <b>Найпопулярніший жарт:</b>\n"
            f"<i>{stats.get('top_content', 'Завантаження...')[:100]}...</i>\n\n"
            
            f"🎊 Дякуємо за активність! Продовжуйте брати участь у дуелях!"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Дуелі", callback_data="duel_menu")],
            [
                InlineKeyboardButton(text="🏆 Топ", callback_data="leaderboard"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
            ]
        ])
        
        return message_text, keyboard
    
    # ===== МЕТОДИ ОТРИМАННЯ ДАНИХ =====
    
    async def get_active_users(self, days: int = 7) -> List[Dict]:
        """Отримання активних користувачів"""
        try:
            from database.services import get_active_users_for_broadcast
            return await get_active_users_for_broadcast(days)
        except Exception as e:
            logger.error(f"Помилка отримання активних користувачів: {e}")
            return []
    
    async def get_all_users(self) -> List[Dict]:
        """Отримання всіх користувачів"""
        try:
            from database.services import get_all_users_for_broadcast
            return await get_all_users_for_broadcast()
        except Exception as e:
            logger.error(f"Помилка отримання всіх користувачів: {e}")
            return []
    
    async def get_duel_participants(self) -> List[Dict]:
        """Отримання користувачів що брали участь у дуелях"""
        try:
            from database.services import get_duel_participants_for_broadcast
            return await get_duel_participants_for_broadcast()
        except Exception as e:
            logger.error(f"Помилка отримання дуелістів: {e}")
            return []
    
    async def get_daily_best_content(self) -> Optional[Dict]:
        """Отримання кращого контенту за день"""
        try:
            from database.services import get_daily_best_content
            return await get_daily_best_content()
        except Exception as e:
            logger.error(f"Помилка отримання контенту дня: {e}")
            return None
    
    async def generate_weekly_stats(self) -> Dict:
        """Генерація тижневої статистики"""
        try:
            from database.services import generate_weekly_stats
            return await generate_weekly_stats()
        except Exception as e:
            logger.error(f"Помилка генерації статистики: {e}")
            return {}
    
    async def mark_user_inactive(self, user_id: int):
        """Позначити користувача як неактивного"""
        try:
            from database.services import mark_user_inactive
            await mark_user_inactive(user_id)
        except Exception as e:
            logger.error(f"Помилка позначення користувача неактивним: {e}")
    
    # ===== СТАН СИСТЕМИ =====
    
    def reset_daily_flags(self):
        """Скидання щоденних прапорців"""
        self.daily_content_sent = False
    
    def reset_weekly_flags(self):
        """Скидання тижневих прапорців"""
        self.weekly_stats_sent = False
    
    def get_broadcast_status(self) -> Dict:
        """Отримання статусу розсилок"""
        return {
            "daily_content_sent": self.daily_content_sent,
            "weekly_stats_sent": self.weekly_stats_sent,
            "active_broadcasts": len(self.active_broadcasts),
            "last_check": datetime.now().isoformat()
        }

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def create_broadcast_system(bot: Bot) -> BroadcastSystem:
    """Створення системи розсилок"""
    return BroadcastSystem(bot)

async def test_broadcast_system(broadcast_system: BroadcastSystem):
    """Тестування системи розсилок"""
    try:
        logger.info("🧪 Тестування системи розсилок...")
        
        # Тест отримання користувачів
        active_users = await broadcast_system.get_active_users(days=30)
        logger.info(f"✅ Активних користувачів: {len(active_users)}")
        
        # Тест статусу
        status = broadcast_system.get_broadcast_status()
        logger.info(f"✅ Статус системи: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка тестування: {e}")
        return False

# ===== ЕКСПОРТ =====

__all__ = [
    'BroadcastSystem',
    'create_broadcast_system',
    'test_broadcast_system'
]