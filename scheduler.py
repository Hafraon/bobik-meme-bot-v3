#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Планувальник задач для бота 🧠😂🔥
"""

import asyncio
import logging
from datetime import datetime, time
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import EMOJI, settings, TIME_GREETINGS
from database.database import get_db_session, get_random_joke, get_random_meme, update_user_points
from database.models import User

logger = logging.getLogger(__name__)

class SchedulerService:
    """Сервіс планувальника для автоматичних задач"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone='Europe/Kiev')  # Українська часова зона
        
    async def start(self):
        """Запуск планувальника"""
        try:
            # Щоденна розсилка
            self.scheduler.add_job(
                self.daily_broadcast,
                CronTrigger(
                    hour=settings.DAILY_BROADCAST_HOUR,
                    minute=settings.DAILY_BROADCAST_MINUTE
                ),
                id='daily_broadcast',
                name='Щоденна розсилка контенту'
            )
            
            # Завершення дуелей (кожні 5 хвилин)
            self.scheduler.add_job(
                self.finish_expired_duels,
                CronTrigger(minute='*/5'),
                id='finish_duels',
                name='Завершення просрочених дуелей'
            )
            
            # Очищення статистики (щотижня)
            self.scheduler.add_job(
                self.weekly_cleanup,
                CronTrigger(day_of_week=0, hour=2, minute=0),  # Неділя 02:00
                id='weekly_cleanup',
                name='Тижневе очищення'
            )
            
            # Нагадування про активність (щодня о 20:00)
            self.scheduler.add_job(
                self.activity_reminder,
                CronTrigger(hour=20, minute=0),
                id='activity_reminder',
                name='Нагадування про активність'
            )
            
            self.scheduler.start()
            logger.info("🔥 Планувальник запущено!")
            
        except Exception as e:
            logger.error(f"Помилка запуску планувальника: {e}")
    
    async def stop(self):
        """Зупинка планувальника"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️ Планувальник зупинено")
    
    async def daily_broadcast(self):
        """Щоденна розсилка контенту підписникам"""
        logger.info("📅 Початок щоденної розсилки...")
        
        try:
            # Отримання підписників
            subscribers = await self.get_daily_subscribers()
            
            if not subscribers:
                logger.info("📭 Немає підписників для щоденної розсилки")
                return
            
            # Отримання контенту дня
            daily_joke = await get_random_joke()
            daily_meme = await get_random_meme()
            
            if not daily_joke and not daily_meme:
                logger.warning("📭 Немає контенту для щоденної розсилки")
                return
            
            # Підготовка повідомлення
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                greeting = f"{EMOJI['fire']} Доброго ранку!"
                mood_text = "Заряджайся позитивом на весь день!"
            elif 12 <= current_hour < 18:
                greeting = f"{EMOJI['laugh']} Гарного дня!"
                mood_text = "Час для гумористичної паузи!"
            else:
                greeting = f"{EMOJI['brain']} Доброго вечора!"
                mood_text = "Розслабся з хорошим гумором!"
            
            # Статистика для мотивації
            stats_text = await self.get_daily_stats()
            
            # Надсилання підписникам
            success_count = 0
            for subscriber in subscribers:
                try:
                    # Персоналізований контент
                    personal_greeting = f"{greeting}\n\n{EMOJI['star']} {subscriber.first_name or 'Друже'}, {mood_text}\n\n"
                    
                    # Анекдот дня
                    if daily_joke:
                        joke_message = (
                            f"{personal_greeting}"
                            f"{EMOJI['brain']} <b>АНЕКДОТ ДНЯ:</b>\n\n"
                            f"{daily_joke.text}\n\n"
                            f"{stats_text}"
                        )
                        
                        await self.bot.send_message(
                            subscriber.id,
                            joke_message
                        )
                        
                        # Коротка пауза між повідомленнями
                        await asyncio.sleep(0.5)
                    
                    # Мем дня (якщо є)
                    if daily_meme:
                        meme_caption = f"{EMOJI['laugh']} <b>МЕМ ДНЯ:</b>\n\n{daily_meme.text}"
                        
                        if daily_meme.file_id:
                            await self.bot.send_photo(
                                subscriber.id,
                                photo=daily_meme.file_id,
                                caption=meme_caption
                            )
                        elif daily_meme.file_url:
                            await self.bot.send_photo(
                                subscriber.id,
                                photo=daily_meme.file_url,
                                caption=meme_caption
                            )
                        else:
                            await self.bot.send_message(
                                subscriber.id,
                                meme_caption
                            )
                        
                        await asyncio.sleep(0.5)
                    
                    # Нарахування балів за щоденну активність
                    await update_user_points(subscriber.id, 2, "щоденна розсилка")
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Помилка надсилання користувачу {subscriber.id}: {e}")
                    continue
            
            logger.info(f"📤 Щоденну розсилку надіслано {success_count}/{len(subscribers)} користувачів")
            
        except Exception as e:
            logger.error(f"Помилка щоденної розсилки: {e}")
    
    async def get_daily_subscribers(self) -> List[User]:
        """Отримання списку підписників щоденної розсилки"""
        with get_db_session() as session:
            return session.query(User).filter(User.daily_subscription == True).all()
    
    async def get_daily_stats(self) -> str:
        """Отримання щоденної статистики для мотивації"""
        with get_db_session() as session:
            total_users = session.query(User).count()
            total_points = session.query(User.points).filter(User.points > 0).count()
            
            # Випадкова мотиваційна фраза
            motivational_phrases = [
                f"{EMOJI['rocket']} Сьогодні {total_users} людей сміються разом з нами!",
                f"{EMOJI['fire']} Вже {total_points} користувачів заробили бали!",
                f"{EMOJI['star']} Приєднуйся до спільноти гумористів!",
                f"{EMOJI['trophy']} Кожен день - нова можливість посміятися!",
                f"{EMOJI['heart']} Гумор об'єднує нас всіх!"
            ]
            
            import random
            return random.choice(motivational_phrases)
    
    async def finish_expired_duels(self):
        """Завершення просрочених дуелей"""
        try:
            from database.models import Duel, DuelStatus
            from handlers.duel_handlers import finish_duel
            
            with get_db_session() as session:
                expired_duels = session.query(Duel).filter(
                    Duel.status == DuelStatus.ACTIVE,
                    Duel.voting_ends_at <= datetime.utcnow()
                ).all()
                
                for duel in expired_duels:
                    try:
                        result = await finish_duel(duel.id)
                        
                        if result:
                            # Повідомлення учасникам про результат
                            result_text = (
                                f"{EMOJI['vs']} <b>ДУЕЛЬ ЗАВЕРШЕНА!</b>\n\n"
                                f"{EMOJI['fire']} Жарт А: {result['initiator_votes']} голосів\n"
                                f"{EMOJI['brain']} Жарт Б: {result['opponent_votes']} голосів\n\n"
                            )
                            
                            if result['winner_id']:
                                result_text += f"{EMOJI['trophy']} <b>Переможець отримав +15 балів!</b>"
                            else:
                                result_text += f"{EMOJI['thinking']} <b>Нічия! Обидва учасники молодці!</b>"
                            
                            # Повідомлення ініціатору
                            try:
                                await self.bot.send_message(duel.initiator_id, result_text)
                            except:
                                pass
                            
                            # Повідомлення опоненту
                            if duel.opponent_id:
                                try:
                                    await self.bot.send_message(duel.opponent_id, result_text)
                                except:
                                    pass
                        
                    except Exception as e:
                        logger.error(f"Помилка завершення дуелі {duel.id}: {e}")
                
                if expired_duels:
                    logger.info(f"🏁 Завершено {len(expired_duels)} просрочених дуелей")
                
        except Exception as e:
            logger.error(f"Помилка завершення дуелей: {e}")
    
    async def weekly_cleanup(self):
        """Тижневе очищення та підбиття підсумків"""
        logger.info("🧹 Початок тижневого очищення...")
        
        try:
            from database.models import Rating, BotStatistics
            
            with get_db_session() as session:
                # Очищення старих рейтингів (старші 30 днів)
                month_ago = datetime.utcnow() - timedelta(days=30)
                old_ratings = session.query(Rating).filter(
                    Rating.created_at < month_ago
                ).delete()
                
                # Створення статистики тижня
                weekly_stats = BotStatistics(
                    total_users=session.query(User).count(),
                    active_users_today=session.query(User).filter(
                        User.last_active >= datetime.utcnow() - timedelta(days=7)
                    ).count(),
                    # Додати інші метрики
                )
                session.add(weekly_stats)
                session.commit()
                
                logger.info(f"🗑️ Видалено {old_ratings} старих рейтингів")
                
        except Exception as e:
            logger.error(f"Помилка тижневого очищення: {e}")
    
    async def activity_reminder(self):
        """Нагадування неактивним користувачам"""
        try:
            from datetime import timedelta
            
            # Користувачі, які не були активні 3 дні
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            
            with get_db_session() as session:
                inactive_users = session.query(User).filter(
                    User.last_active < three_days_ago,
                    User.daily_subscription == False  # Не підписані на розсилку
                ).limit(50).all()  # Обмежуємо кількість
                
                reminder_text = (
                    f"{EMOJI['thinking']} <b>Сумуємо за тобою!</b>\n\n"
                    f"{EMOJI['brain']} Поки ти був відсутній, з'явилося багато нових жартів\n"
                    f"{EMOJI['fire']} Твоя позиція в рейтингу може змінитися\n"
                    f"{EMOJI['star']} Повертайся швидше!\n\n"
                    f"{EMOJI['laugh']} /meme - отримати новий мем\n"
                    f"{EMOJI['calendar']} /daily - підписатися на щоденну розсилку"
                )
                
                sent_count = 0
                for user in inactive_users:
                    try:
                        await self.bot.send_message(user.id, reminder_text)
                        sent_count += 1
                        await asyncio.sleep(1)  # Пауза між повідомленнями
                    except:
                        continue
                
                if sent_count > 0:
                    logger.info(f"📬 Надіслано нагадувань {sent_count} неактивним користувачам")
                
        except Exception as e:
            logger.error(f"Помилка нагадування: {e}")

# Допоміжні функції для ручного керування

async def send_broadcast_message(bot, message_text: str, target_users: List[int] = None):
    """Розсилка повідомлення всім або вибраним користувачам"""
    try:
        if target_users is None:
            # Розсилка всім користувачам
            with get_db_session() as session:
                all_users = session.query(User).all()
                target_users = [user.id for user in all_users]
        
        success_count = 0
        for user_id in target_users:
            try:
                await bot.send_message(user_id, message_text)
                success_count += 1
                await asyncio.sleep(0.1)  # Анти-спам пауза
            except:
                continue
        
        logger.info(f"📢 Розсилку надіслано {success_count}/{len(target_users)} користувачів")
        return success_count
        
    except Exception as e:
        logger.error(f"Помилка розсилки: {e}")
        return 0