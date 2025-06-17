#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Планувальник задач для автоматичної розсилки 🧠😂🔥
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import EMOJI, settings, TIME_GREETINGS
from database.database import get_db_session, get_random_joke, get_random_meme, update_user_points
from database.models import User, Content, ContentStatus, Duel, DuelStatus

logger = logging.getLogger(__name__)

class SchedulerService:
    """Сервіс планувальника для автоматичних задач"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
        
    async def start(self):
        """Запуск планувальника з усіма задачами"""
        try:
            # Щоденна розсилка підписникам
            self.scheduler.add_job(
                self.daily_broadcast,
                CronTrigger(
                    hour=settings.DAILY_BROADCAST_HOUR,
                    minute=settings.DAILY_BROADCAST_MINUTE
                ),
                id='daily_broadcast',
                name='Щоденна розсилка контенту',
                max_instances=1
            )
            
            # Завершення просрочених дуелей (кожні 5 хвилин)
            self.scheduler.add_job(
                self.finish_expired_duels,
                CronTrigger(minute='*/5'),
                id='finish_duels',
                name='Завершення просрочених дуелей',
                max_instances=1
            )
            
            # Щоденне нагадування неактивним користувачам (о 19:00)
            self.scheduler.add_job(
                self.inactive_users_reminder,
                CronTrigger(hour=19, minute=0),
                id='inactive_reminder',
                name='Нагадування неактивним користувачам',
                max_instances=1
            )
            
            # Тижневі нагороди топ-користувачам (неділя о 20:00)
            self.scheduler.add_job(
                self.weekly_top_rewards,
                CronTrigger(day_of_week=6, hour=20, minute=0),  # Неділя
                id='weekly_rewards',
                name='Тижневі нагороди',
                max_instances=1
            )
            
            self.scheduler.start()
            logger.info("🔥 Планувальник запущено з усіма задачами!")
            
        except Exception as e:
            logger.error(f"Помилка запуску планувальника: {e}")
            raise
    
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
            
            # Визначення привітання за часом
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
            stats_text = await self.get_motivation_stats()
            
            success_count = 0
            for subscriber in subscribers:
                try:
                    # Персоналізоване привітання
                    user_name = subscriber.first_name or "Друже"
                    personal_greeting = f"{greeting}\n\n{EMOJI['star']} {user_name}, {mood_text}\n\n"
                    
                    # Основне повідомлення з анекдотом
                    if daily_joke:
                        joke_message = (
                            f"{personal_greeting}"
                            f"{EMOJI['brain']} <b>АНЕКДОТ ДНЯ:</b>\n\n"
                            f"{daily_joke.text}\n\n"
                            f"{stats_text}\n\n"
                            f"{EMOJI['like']} Оціни та отримай +{settings.POINTS_FOR_REACTION} балів!"
                        )
                        
                        # Клавіатура для швидких дій
                        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text=f"{EMOJI['like']} Подобається", 
                                    callback_data=f"like_content:{daily_joke.id}"
                                ),
                                InlineKeyboardButton(
                                    text=f"{EMOJI['laugh']} Ще мем", 
                                    callback_data="get_meme"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    text=f"{EMOJI['fire']} Мій профіль", 
                                    callback_data="show_profile"
                                ),
                                InlineKeyboardButton(
                                    text=f"{EMOJI['vs']} Дуель", 
                                    callback_data="start_duel"
                                )
                            ]
                        ])
                        
                        await self.bot.send_message(
                            subscriber.id,
                            joke_message,
                            reply_markup=keyboard
                        )
                        
                        await asyncio.sleep(0.5)  # Пауза між повідомленнями
                    
                    # Додаткове повідомлення з мемом (якщо є)
                    if daily_meme and daily_meme.file_id:
                        meme_caption = (
                            f"{EMOJI['laugh']} <b>МЕМ ДНЯ:</b>\n\n"
                            f"{daily_meme.text}\n\n"
                            f"{EMOJI['fire']} Переглядів: {daily_meme.views}"
                        )
                        
                        try:
                            await self.bot.send_photo(
                                subscriber.id,
                                photo=daily_meme.file_id,
                                caption=meme_caption
                            )
                        except:
                            # Якщо не вдалося відправити фото, відправляємо текст
                            await self.bot.send_message(subscriber.id, meme_caption)
                        
                        await asyncio.sleep(0.5)
                    
                    # Нарахування балів за щоденну активність
                    await update_user_points(
                        subscriber.id, 
                        settings.POINTS_FOR_DAILY_ACTIVITY, 
                        "щоденна розсилка"
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Помилка надсилання користувачу {subscriber.id}: {e}")
                    continue
            
            logger.info(f"📤 Щоденну розсилку надіслано {success_count}/{len(subscribers)} користувачів")
            
            # Повідомлення адміністратору про результат
            try:
                await self.bot.send_message(
                    settings.ADMIN_ID,
                    f"{EMOJI['check']} <b>Щоденна розсилка завершена!</b>\n\n"
                    f"{EMOJI['profile']} Підписників: {len(subscribers)}\n"
                    f"{EMOJI['fire']} Успішно надіслано: {success_count}\n"
                    f"{EMOJI['cross']} Помилок: {len(subscribers) - success_count}"
                )
            except:
                pass
            
        except Exception as e:
            logger.error(f"Помилка щоденної розсилки: {e}")
    
    async def get_daily_subscribers(self) -> List[User]:
        """Отримання списку підписників щоденної розсилки"""
        with get_db_session() as session:
            return session.query(User).filter(
                User.daily_subscription == True
            ).all()
    
    async def get_motivation_stats(self) -> str:
        """Отримання мотиваційної статистики"""
        with get_db_session() as session:
            total_users = session.query(User).count()
            users_with_points = session.query(User).filter(User.points > 0).count()
            active_duels = session.query(Duel).filter(Duel.status == DuelStatus.ACTIVE).count()
            
            motivational_phrases = [
                f"{EMOJI['rocket']} Сьогодні {total_users} людей сміються разом з нами!",
                f"{EMOJI['fire']} Вже {users_with_points} користувачів заробили бали!",
                f"{EMOJI['vs']} Зараз йде {active_duels} дуелей жартів!",
                f"{EMOJI['star']} Приєднуйся до спільноти гумористів!",
                f"{EMOJI['trophy']} Кожен день - нова можливість посміятися!",
                f"{EMOJI['heart']} Гумор об'єднує нас всіх!"
            ]
            
            import random
            return random.choice(motivational_phrases)
    
    async def finish_expired_duels(self):
        """Завершення просрочених дуелей"""
        try:
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
                                f"{EMOJI['vs']} <b>ДУЕЛЬ #{duel.id} ЗАВЕРШЕНА!</b>\n\n"
                                f"{EMOJI['fire']} Жарт А: {result['initiator_votes']} голосів\n"
                                f"{EMOJI['brain']} Жарт Б: {result['opponent_votes']} голосів\n\n"
                            )
                            
                            if result['winner_id']:
                                result_text += f"{EMOJI['trophy']} <b>Переможець отримав +{settings.POINTS_FOR_DUEL_WIN} балів!</b>"
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
    
    async def inactive_users_reminder(self):
        """Нагадування неактивним користувачам"""
        try:
            # Користувачі, які не були активні 3 дні
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            
            with get_db_session() as session:
                inactive_users = session.query(User).filter(
                    User.last_active < three_days_ago,
                    User.daily_subscription == False,  # Не підписані на розсилку
                    User.points > 0  # Але мають бали (колись були активними)
                ).limit(50).all()  # Обмежуємо кількість
                
                reminder_text = (
                    f"{EMOJI['thinking']} <b>Сумуємо за тобою!</b>\n\n"
                    f"{EMOJI['brain']} Поки ти був відсутній, з'явилося багато нових жартів\n"
                    f"{EMOJI['fire']} Твоя позиція в рейтингу може змінитися\n"
                    f"{EMOJI['vs']} З'явилися нові дуелі жартів\n"
                    f"{EMOJI['star']} Повертайся швидше!\n\n"
                    f"{EMOJI['laugh']} /meme - отримати новий мем\n"
                    f"{EMOJI['calendar']} /daily - підписатися на щоденну розсилку\n"
                    f"{EMOJI['profile']} /profile - переглянути свій профіль"
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
    
    async def weekly_top_rewards(self):
        """Тижневі нагороди топ-користувачам"""
        try:
            with get_db_session() as session:
                # Топ-3 користувачі за балами
                top_users = session.query(User).order_by(User.points.desc()).limit(3).all()
                
                if not top_users:
                    return
                
                rewards = [
                    (50, "🥇", "ЧЕМПІОН ТИЖНЯ"),
                    (30, "🥈", "СРІБНИЙ ПРИЗЕР"),
                    (20, "🥉", "БРОНЗОВИЙ ПРИЗЕР")
                ]
                
                for i, user in enumerate(top_users):
                    if i < len(rewards):
                        bonus_points, medal, title = rewards[i]
                        
                        # Нарахування бонусних балів
                        await update_user_points(
                            user.id, 
                            bonus_points, 
                            f"тижнева нагорода - {title.lower()}"
                        )
                        
                        # Повідомлення переможцю
                        try:
                            reward_text = (
                                f"{medal} <b>{title}!</b>\n\n"
                                f"{EMOJI['trophy']} Вітаємо, {user.first_name or 'Гумористе'}!\n"
                                f"{EMOJI['fire']} Ти в топ-{i+1} за цей тиждень!\n"
                                f"{EMOJI['star']} Бонус: +{bonus_points} балів\n\n"
                                f"{EMOJI['rocket']} Продовжуй в тому ж дусі!"
                            )
                            
                            await self.bot.send_message(user.id, reward_text)
                        except:
                            pass
                
                # Повідомлення в загальний чат про топ
                top_announcement = (
                    f"{EMOJI['trophy']} <b>ПІДСУМКИ ТИЖНЯ!</b>\n\n"
                    f"🥇 {top_users[0].first_name or 'Невідомий'} - {top_users[0].points} балів\n"
                )
                
                if len(top_users) > 1:
                    top_announcement += f"🥈 {top_users[1].first_name or 'Невідомий'} - {top_users[1].points} балів\n"
                
                if len(top_users) > 2:
                    top_announcement += f"🥉 {top_users[2].first_name or 'Невідомий'} - {top_users[2].points} балів\n"
                
                top_announcement += f"\n{EMOJI['fire']} Вітаємо переможців!"
                
                # Розсилка топ-5 активним користувачам
                active_users = session.query(User).filter(
                    User.last_active >= datetime.utcnow() - timedelta(days=7)
                ).limit(20).all()
                
                for user in active_users[:10]:  # Тільки топ-10 активним
                    try:
                        await self.bot.send_message(user.id, top_announcement)
                        await asyncio.sleep(0.5)
                    except:
                        continue
                
                logger.info(f"🏆 Тижневі нагороди надано {len(top_users)} користувачам")
                
        except Exception as e:
            logger.error(f"Помилка тижневих нагород: {e}")

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