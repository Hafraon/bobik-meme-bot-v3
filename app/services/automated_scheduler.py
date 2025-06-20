#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 АВТОМАТИЗОВАНИЙ ПЛАНУВАЛЬНИК

Повна автоматизація бота: розсилки, дуелі, модерація, статистика
Розумний планувальник що керує всіма автоматичними процесами
"""

import logging
import asyncio
from datetime import datetime, timedelta, time
from typing import Optional, Dict, Any, List
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from aiogram import Bot

logger = logging.getLogger(__name__)

class AutomatedScheduler:
    """Розумний автоматизований планувальник"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.broadcast_system = None
        self.is_running = False
        self.jobs_registry = {}
        
        # Статистика роботи
        self.stats = {
            'jobs_executed': 0,
            'broadcasts_sent': 0,
            'duels_finished': 0,
            'data_cleaned': 0,
            'errors': 0,
            'last_activity': None
        }
    
    async def initialize(self):
        """Ініціалізація планувальника"""
        try:
            logger.info("🤖 Ініціалізація автоматизованого планувальника...")
            
            # Ініціалізація broadcast system
            from .broadcast_system import create_broadcast_system
            self.broadcast_system = await create_broadcast_system(self.bot)
            
            # Налаштування всіх завдань
            await self.setup_all_jobs()
            
            logger.info("✅ Автоматизований планувальник готовий")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації планувальника: {e}")
            return False
    
    async def setup_all_jobs(self):
        """Налаштування всіх автоматичних завдань"""
        
        # ===== ЩОДЕННІ ЗАВДАННЯ =====
        
        # Ранкова розсилка (9:00)
        self.add_job(
            func=self.morning_content_broadcast,
            trigger=CronTrigger(hour=9, minute=0),
            id='morning_broadcast',
            name='Ранкова розсилка контенту',
            replace_existing=True
        )
        
        # Вечірня розсилка статистики (20:00)
        self.add_job(
            func=self.evening_stats_broadcast,
            trigger=CronTrigger(hour=20, minute=0),
            id='evening_stats',
            name='Вечірня статистика',
            replace_existing=True
        )
        
        # Очистка даних о 3:00
        self.add_job(
            func=self.daily_cleanup,
            trigger=CronTrigger(hour=3, minute=0),
            id='daily_cleanup',
            name='Щоденна очистка даних',
            replace_existing=True
        )
        
        # ===== РЕГУЛЯРНІ ЗАВДАННЯ =====
        
        # Перевірка дуелів кожну хвилину
        self.add_job(
            func=self.check_duels,
            trigger=IntervalTrigger(minutes=1),
            id='duel_checker',
            name='Перевірка дуелей',
            replace_existing=True
        )
        
        # Нагадування про дуелі кожні 15 хвилин
        self.add_job(
            func=self.duel_reminders,
            trigger=IntervalTrigger(minutes=15),
            id='duel_reminders',
            name='Нагадування про дуелі',
            replace_existing=True
        )
        
        # Перевірка досягнень кожні 5 хвилин
        self.add_job(
            func=self.check_achievements,
            trigger=IntervalTrigger(minutes=5),
            id='achievement_checker',
            name='Перевірка досягнень',
            replace_existing=True
        )
        
        # ===== ТИЖНЕВІ ЗАВДАННЯ =====
        
        # Тижневий дайджест (неділя, 18:00)
        self.add_job(
            func=self.weekly_digest,
            trigger=CronTrigger(day_of_week=6, hour=18, minute=0),  # Sunday
            id='weekly_digest',
            name='Тижневий дайджест',
            replace_existing=True
        )
        
        # Турнір дуелів (п'ятниця, 19:00)
        self.add_job(
            func=self.weekly_tournament,
            trigger=CronTrigger(day_of_week=4, hour=19, minute=0),  # Friday
            id='weekly_tournament',
            name='Тижневий турнір',
            replace_existing=True
        )
        
        # ===== МІСЯЧНІ ЗАВДАННЯ =====
        
        # Підбиття підсумків місяця (1 число, 12:00)
        self.add_job(
            func=self.monthly_summary,
            trigger=CronTrigger(day=1, hour=12, minute=0),
            id='monthly_summary',
            name='Місячне підбиття підсумків',
            replace_existing=True
        )
        
        logger.info("📅 Налаштовано всі автоматичні завдання")
    
    def add_job(self, func, trigger, id: str, name: str, **kwargs):
        """Додавання завдання з реєстрацією"""
        try:
            job = self.scheduler.add_job(func, trigger, id=id, name=name, **kwargs)
            self.jobs_registry[id] = {
                'name': name,
                'function': func.__name__,
                'trigger': str(trigger),
                'added_at': datetime.now(),
                'last_run': None,
                'run_count': 0,
                'error_count': 0
            }
            logger.info(f"📝 Додано завдання: {name} ({id})")
            return job
        except Exception as e:
            logger.error(f"❌ Помилка додавання завдання {name}: {e}")
    
    # ===== ЩОДЕННІ ЗАВДАННЯ =====
    
    async def morning_content_broadcast(self):
        """Ранкова розсилка контенту"""
        try:
            logger.info("🌅 Виконання ранкової розсилки...")
            
            if not self.broadcast_system:
                logger.warning("Broadcast system не ініціалізована")
                return
            
            await self.broadcast_system.send_daily_content()
            
            # Оновлюємо статистику
            self.stats['broadcasts_sent'] += 1
            self.stats['jobs_executed'] += 1
            self.stats['last_activity'] = datetime.now()
            
            # Додаткові дії
            await self.check_for_special_events()
            
            logger.info("✅ Ранкова розсилка завершена")
            
        except Exception as e:
            logger.error(f"❌ Помилка ранкової розсилки: {e}")
            self.stats['errors'] += 1
    
    async def evening_stats_broadcast(self):
        """Вечірня розсилка статистики"""
        try:
            logger.info("🌆 Виконання вечірньої статистики...")
            
            # Генеруємо денну статистику
            daily_stats = await self.generate_daily_stats()
            
            # Відправляємо адміністратору
            await self.send_admin_daily_report(daily_stats)
            
            # Можливо відправляємо активним користувачам
            if daily_stats.get('interesting_events'):
                await self.send_daily_highlights(daily_stats)
            
            self.stats['jobs_executed'] += 1
            self.stats['last_activity'] = datetime.now()
            
            logger.info("✅ Вечірня статистика завершена")
            
        except Exception as e:
            logger.error(f"❌ Помилка вечірньої статистики: {e}")
            self.stats['errors'] += 1
    
    async def daily_cleanup(self):
        """Щоденна очистка даних"""
        try:
            logger.info("🧹 Виконання щоденної очистки...")
            
            cleanup_stats = {
                'old_duels': 0,
                'old_ratings': 0,
                'inactive_users': 0,
                'temp_files': 0
            }
            
            # Очистка старих дуелей
            from database.services import cleanup_old_duels
            cleanup_stats['old_duels'] = await cleanup_old_duels()
            
            # Очистка старих рейтингів (старше 30 днів)
            cleanup_stats['old_ratings'] = await self.cleanup_old_ratings(days=30)
            
            # Позначення неактивних користувачів
            cleanup_stats['inactive_users'] = await self.mark_inactive_users(days=60)
            
            # Очистка тимчасових файлів
            cleanup_stats['temp_files'] = await self.cleanup_temp_files()
            
            # Оновлення статистики бота
            await self.update_bot_statistics()
            
            self.stats['data_cleaned'] += sum(cleanup_stats.values())
            self.stats['jobs_executed'] += 1
            self.stats['last_activity'] = datetime.now()
            
            # Відправляємо звіт адміну
            await self.send_cleanup_report(cleanup_stats)
            
            logger.info(f"✅ Щоденна очистка завершена: {cleanup_stats}")
            
        except Exception as e:
            logger.error(f"❌ Помилка щоденної очистки: {e}")
            self.stats['errors'] += 1
    
    # ===== РЕГУЛЯРНІ ЗАВДАННЯ =====
    
    async def check_duels(self):
        """Перевірка та завершення дуелів"""
        try:
            from database.services import auto_finish_expired_duels
            
            finished_count = await auto_finish_expired_duels()
            
            if finished_count > 0:
                logger.info(f"🏁 Автоматично завершено {finished_count} дуелей")
                self.stats['duels_finished'] += finished_count
            
            self.stats['jobs_executed'] += 1
            self.stats['last_activity'] = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Помилка перевірки дуелей: {e}")
            self.stats['errors'] += 1
    
    async def duel_reminders(self):
        """Нагадування про активні дуелі"""
        try:
            if self.broadcast_system:
                await self.broadcast_system.send_duel_reminders()
            
            self.stats['jobs_executed'] += 1
            
        except Exception as e:
            logger.error(f"❌ Помилка нагадувань про дуелі: {e}")
            self.stats['errors'] += 1
    
    async def check_achievements(self):
        """Перевірка та повідомлення про досягнення"""
        try:
            if self.broadcast_system:
                await self.broadcast_system.send_achievement_notifications()
                await self.broadcast_system.send_rank_up_notifications()
            
            self.stats['jobs_executed'] += 1
            
        except Exception as e:
            logger.error(f"❌ Помилка перевірки досягнень: {e}")
            self.stats['errors'] += 1
    
    # ===== ТИЖНЕВІ ЗАВДАННЯ =====
    
    async def weekly_digest(self):
        """Тижневий дайджест"""
        try:
            logger.info("📊 Виконання тижневого дайджесту...")
            
            if self.broadcast_system:
                await self.broadcast_system.send_weekly_digest()
            
            # Генеруємо детальний звіт для адміна
            weekly_report = await self.generate_weekly_admin_report()
            await self.send_admin_weekly_report(weekly_report)
            
            self.stats['broadcasts_sent'] += 1
            self.stats['jobs_executed'] += 1
            self.stats['last_activity'] = datetime.now()
            
            logger.info("✅ Тижневий дайджест завершено")
            
        except Exception as e:
            logger.error(f"❌ Помилка тижневого дайджесту: {e}")
            self.stats['errors'] += 1
    
    async def weekly_tournament(self):
        """Запуск тижневого турніру"""
        try:
            logger.info("🏆 Запуск тижневого турніру...")
            
            tournament_data = {
                'name': 'Тижневий турнір дуелів',
                'start_date': 'Зараз',
                'duration': '48 годин',
                'prize': '+500 балів переможцю + спеціальний титул'
            }
            
            if self.broadcast_system:
                await self.broadcast_system.send_tournament_announcement(tournament_data)
            
            # Створюємо спеціальні дуелі для турніру
            await self.create_tournament_duels()
            
            self.stats['jobs_executed'] += 1
            
            logger.info("✅ Тижневий турнір запущено")
            
        except Exception as e:
            logger.error(f"❌ Помилка запуску турніру: {e}")
            self.stats['errors'] += 1
    
    # ===== МІСЯЧНІ ЗАВДАННЯ =====
    
    async def monthly_summary(self):
        """Місячне підбиття підсумків"""
        try:
            logger.info("📈 Виконання місячного підбиття підсумків...")
            
            # Генеруємо місячну статистику
            monthly_stats = await self.generate_monthly_stats()
            
            # Визначаємо найкращих користувачів місяця
            top_users = await self.get_monthly_top_users()
            
            # Відправляємо нагороди
            await self.distribute_monthly_rewards(top_users)
            
            # Відправляємо підсумки всім користувачам
            await self.send_monthly_summary_broadcast(monthly_stats, top_users)
            
            self.stats['broadcasts_sent'] += 1
            self.stats['jobs_executed'] += 1
            
            logger.info("✅ Місячне підбиття підсумків завершено")
            
        except Exception as e:
            logger.error(f"❌ Помилка місячного підсумку: {e}")
            self.stats['errors'] += 1
    
    # ===== ДОПОМІЖНІ МЕТОДИ =====
    
    async def generate_daily_stats(self) -> Dict[str, Any]:
        """Генерація денної статистики"""
        try:
            from database.services import get_broadcast_statistics
            
            stats = await get_broadcast_statistics()
            
            # Додаткова обробка
            stats['interesting_events'] = await self.find_interesting_daily_events()
            stats['system_health'] = await self.check_system_health()
            
            return stats
            
        except Exception as e:
            logger.error(f"Помилка генерації денної статистики: {e}")
            return {'error': str(e)}
    
    async def find_interesting_daily_events(self) -> List[str]:
        """Пошук цікавих подій дня"""
        events = []
        
        try:
            from database.services import get_active_duels, get_daily_best_content
            
            # Перевіряємо активність дуелей
            active_duels = await get_active_duels()
            if len(active_duels) > 5:
                events.append(f"🔥 Рекордна кількість дуелей: {len(active_duels)}")
            
            # Перевіряємо популярний контент
            best_content = await get_daily_best_content()
            if best_content and best_content.get('likes', 0) > 10:
                events.append(f"⭐ Вірусний жарт дня: {best_content['likes']} лайків")
            
            return events
            
        except Exception as e:
            logger.error(f"Помилка пошуку подій: {e}")
            return []
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Перевірка здоров'я системи"""
        health = {
            'status': 'healthy',
            'issues': [],
            'performance': 'good'
        }
        
        try:
            # Перевірка БД
            from database.services import get_basic_stats
            stats = get_basic_stats()
            
            if stats.get('error'):
                health['status'] = 'warning'
                health['issues'].append('Database connectivity issues')
            
            # Перевірка помилок планувальника
            if self.stats['errors'] > 10:
                health['status'] = 'warning'
                health['issues'].append(f"High error count: {self.stats['errors']}")
            
            return health
            
        except Exception as e:
            return {
                'status': 'error',
                'issues': [str(e)],
                'performance': 'degraded'
            }
    
    async def send_admin_daily_report(self, stats: Dict[str, Any]):
        """Відправка щоденного звіту адміну"""
        try:
            from config.settings import settings
            
            message = (
                f"📊 <b>ЩОДЕННИЙ ЗВІТ СИСТЕМИ</b>\n\n"
                f"📅 Дата: {datetime.now().strftime('%d.%m.%Y')}\n\n"
                f"👥 Активних користувачів: {stats.get('active_today', 0)}\n"
                f"⚔️ Активних дуелей: {stats.get('active_duels', 0)}\n"
                f"📈 Залученість: {stats.get('engagement_rate', 0):.1f}%\n\n"
                f"🔧 Статус системи: {stats.get('system_health', {}).get('status', 'unknown')}\n"
                f"🤖 Виконано завдань: {self.stats['jobs_executed']}\n"
                f"❌ Помилок: {self.stats['errors']}\n\n"
            )
            
            if stats.get('interesting_events'):
                message += "🎯 <b>Події дня:</b>\n"
                for event in stats['interesting_events']:
                    message += f"• {event}\n"
            
            await self.bot.send_message(settings.ADMIN_ID, message)
            
        except Exception as e:
            logger.error(f"Помилка відправки звіту адміну: {e}")
    
    # ===== УПРАВЛІННЯ ПЛАНУВАЛЬНИКОМ =====
    
    async def start(self):
        """Запуск планувальника"""
        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                logger.info("🚀 Автоматизований планувальник запущено")
                
                # Відправляємо повідомлення про запуск
                await self.send_startup_notification()
            
        except Exception as e:
            logger.error(f"❌ Помилка запуску планувальника: {e}")
    
    async def stop(self):
        """Зупинка планувальника"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("⏹️ Автоматизований планувальник зупинено")
                
                # Відправляємо звіт про роботу
                await self.send_shutdown_report()
            
        except Exception as e:
            logger.error(f"❌ Помилка зупинки планувальника: {e}")
    
    async def send_startup_notification(self):
        """Повідомлення про запуск"""
        try:
            from config.settings import settings
            
            message = (
                f"🤖 <b>АВТОМАТИЗАЦІЯ АКТИВНА</b>\n\n"
                f"✅ Планувальник запущено\n"
                f"📅 Завдань у черзі: {len(self.jobs_registry)}\n"
                f"⏰ Наступне завдання: {self.get_next_job_info()}\n\n"
                f"🎯 Автоматичні функції:\n"
                f"• Щоденні розсилки контенту\n"
                f"• Автоматичне завершення дуелей\n"
                f"• Нагадування та сповіщення\n"
                f"• Очистка та оптимізація\n"
                f"• Тижневі та місячні звіти"
            )
            
            await self.bot.send_message(settings.ADMIN_ID, message)
            
        except Exception as e:
            logger.error(f"Помилка відправки повідомлення про запуск: {e}")
    
    def get_next_job_info(self) -> str:
        """Інформація про наступне завдання"""
        try:
            jobs = self.scheduler.get_jobs()
            if jobs:
                next_job = min(jobs, key=lambda j: j.next_run_time)
                return f"{next_job.name} о {next_job.next_run_time.strftime('%H:%M')}"
            return "Немає запланованих завдань"
        except:
            return "Невідомо"
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Статус планувальника"""
        return {
            'is_running': self.is_running,
            'total_jobs': len(self.jobs_registry),
            'stats': self.stats.copy(),
            'next_job': self.get_next_job_info(),
            'uptime': datetime.now() - self.stats.get('last_activity', datetime.now())
        }

# ===== ДОПОМІЖНІ ФУНКЦІЇ =====

async def create_automated_scheduler(bot: Bot) -> AutomatedScheduler:
    """Створення автоматизованого планувальника"""
    scheduler = AutomatedScheduler(bot)
    success = await scheduler.initialize()
    
    if success:
        return scheduler
    else:
        logger.error("❌ Не вдалося створити планувальник")
        return None

async def test_automated_scheduler(scheduler: AutomatedScheduler):
    """Тестування планувальника"""
    try:
        logger.info("🧪 Тестування автоматизованого планувальника...")
        
        # Тест статусу
        status = scheduler.get_scheduler_status()
        logger.info(f"📊 Статус планувальника: {status}")
        
        # Тест ініціалізації
        if scheduler.broadcast_system:
            logger.info("✅ Broadcast system ініціалізована")
        else:
            logger.warning("⚠️ Broadcast system не ініціалізована")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка тестування: {e}")
        return False

# ===== ЕКСПОРТ =====

__all__ = [
    'AutomatedScheduler',
    'create_automated_scheduler',
    'test_automated_scheduler'
]