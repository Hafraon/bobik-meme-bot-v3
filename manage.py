#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Скрипт управління україномовним Telegram-ботом 🧠😂🔥

Використання:
    python scripts/manage.py <command> [options]

Команди:
    init        - Ініціалізація проекту
    health      - Перевірка здоров'я бота
    stats       - Статистика бота
    users       - Управління користувачами
    content     - Управління контентом
    backup      - Створення backup
    restore     - Відновлення з backup
    cleanup     - Очищення старих даних
    migrate     - Міграція БД
    test        - Запуск тестів
"""

import asyncio
import sys
import os
import argparse
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import json

# Додавання поточної директорії до PATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings, EMOJI
from database.database import get_db_session, init_db
from database.models import User, Content, Duel, Rating, ContentType, ContentStatus

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotManager:
    """Клас для управління ботом"""
    
    def __init__(self):
        self.bot = None
        
    async def init_bot(self):
        """Ініціалізація бота"""
        from aiogram import Bot
        from aiogram.enums import ParseMode
        
        self.bot = Bot(
            token=settings.BOT_TOKEN,
            parse_mode=ParseMode.HTML
        )
        return self.bot
    
    async def check_health(self) -> dict:
        """Перевірка здоров'я бота"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "bot_status": "unknown",
            "database_status": "unknown",
            "api_status": "unknown",
            "errors": []
        }
        
        try:
            # Перевірка підключення до Telegram API
            bot = await self.init_bot()
            bot_info = await bot.get_me()
            health_status["bot_status"] = "healthy"
            health_status["bot_info"] = {
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "id": bot_info.id
            }
            await bot.session.close()
            
        except Exception as e:
            health_status["bot_status"] = "error"
            health_status["errors"].append(f"Bot API error: {str(e)}")
        
        try:
            # Перевірка підключення до БД
            with get_db_session() as session:
                user_count = session.query(User).count()
                health_status["database_status"] = "healthy"
                health_status["database_info"] = {
                    "total_users": user_count,
                    "database_url": settings.DATABASE_URL.split('@')[0] + "@***"
                }
                
        except Exception as e:
            health_status["database_status"] = "error"
            health_status["errors"].append(f"Database error: {str(e)}")
        
        # Перевірка OpenAI API (якщо налаштовано)
        if settings.OPENAI_API_KEY:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
                    async with session.get(
                        "https://api.openai.com/v1/models", 
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            health_status["api_status"] = "healthy"
                        else:
                            health_status["api_status"] = "error"
                            health_status["errors"].append(f"OpenAI API status: {response.status}")
            except Exception as e:
                health_status["api_status"] = "error"
                health_status["errors"].append(f"OpenAI API error: {str(e)}")
        
        # Загальний статус
        if health_status["bot_status"] == "healthy" and health_status["database_status"] == "healthy":
            health_status["overall_status"] = "healthy"
        else:
            health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def get_stats(self) -> dict:
        """Отримання статистики бота"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "users": {},
            "content": {},
            "duels": {},
            "activity": {}
        }
        
        try:
            with get_db_session() as session:
                # Статистика користувачів
                total_users = session.query(User).count()
                active_users_today = session.query(User).filter(
                    User.last_active >= datetime.utcnow() - timedelta(days=1)
                ).count()
                active_users_week = session.query(User).filter(
                    User.last_active >= datetime.utcnow() - timedelta(days=7)
                ).count()
                
                stats["users"] = {
                    "total": total_users,
                    "active_today": active_users_today,
                    "active_week": active_users_week,
                    "daily_subscribers": session.query(User).filter(
                        User.daily_subscription == True
                    ).count()
                }
                
                # Статистика контенту
                total_content = session.query(Content).count()
                approved_content = session.query(Content).filter(
                    Content.status == ContentStatus.APPROVED
                ).count()
                pending_content = session.query(Content).filter(
                    Content.status == ContentStatus.PENDING
                ).count()
                
                stats["content"] = {
                    "total": total_content,
                    "approved": approved_content,
                    "pending": pending_content,
                    "jokes": session.query(Content).filter(
                        Content.content_type == ContentType.JOKE
                    ).count(),
                    "memes": session.query(Content).filter(
                        Content.content_type == ContentType.MEME
                    ).count()
                }
                
                # Статистика дуелей
                from database.models import DuelStatus
                stats["duels"] = {
                    "total": session.query(Duel).count(),
                    "active": session.query(Duel).filter(
                        Duel.status == DuelStatus.ACTIVE
                    ).count(),
                    "completed_today": session.query(Duel).filter(
                        Duel.completed_at >= datetime.utcnow() - timedelta(days=1)
                    ).count()
                }
                
                # Топ користувачі
                top_users = session.query(User).order_by(User.points.desc()).limit(5).all()
                stats["top_users"] = [
                    {
                        "name": user.first_name or "Невідомий",
                        "username": user.username,
                        "points": user.points,
                        "rank": user.rank
                    }
                    for user in top_users
                ]
                
        except Exception as e:
            stats["error"] = str(e)
            logger.error(f"Помилка отримання статистики: {e}")
        
        return stats
    
    async def manage_users(self, action: str, user_id: Optional[int] = None, **kwargs):
        """Управління користувачами"""
        try:
            with get_db_session() as session:
                if action == "list":
                    users = session.query(User).order_by(User.points.desc()).limit(20).all()
                    for user in users:
                        print(f"ID: {user.id}, Name: {user.first_name}, Points: {user.points}, Rank: {user.rank}")
                
                elif action == "info" and user_id:
                    user = session.query(User).filter(User.id == user_id).first()
                    if user:
                        print(f"Користувач {user.id}:")
                        print(f"  Ім'я: {user.first_name}")
                        print(f"  Username: @{user.username}")
                        print(f"  Бали: {user.points}")
                        print(f"  Ранг: {user.rank}")
                        print(f"  Щоденна розсилка: {user.daily_subscription}")
                        print(f"  Анекдотів подано: {user.jokes_submitted}")
                        print(f"  Анекдотів схвалено: {user.jokes_approved}")
                    else:
                        print(f"Користувач {user_id} не знайдений")
                
                elif action == "add_points" and user_id:
                    points = kwargs.get("points", 0)
                    from database.database import update_user_points
                    await update_user_points(user_id, points, "адмін додав бали")
                    print(f"Додано {points} балів користувачу {user_id}")
                
                elif action == "reset_points" and user_id:
                    user = session.query(User).filter(User.id == user_id).first()
                    if user:
                        user.points = 0
                        user.rank = "🤡 Новачок"
                        session.commit()
                        print(f"Бали користувача {user_id} скинуто")
                
        except Exception as e:
            logger.error(f"Помилка управління користувачами: {e}")
    
    async def manage_content(self, action: str, content_id: Optional[int] = None, **kwargs):
        """Управління контентом"""
        try:
            with get_db_session() as session:
                if action == "pending":
                    pending = session.query(Content).filter(
                        Content.status == ContentStatus.PENDING
                    ).order_by(Content.created_at).all()
                    
                    print(f"Контент на модерації ({len(pending)}):")
                    for content in pending:
                        author = session.query(User).filter(User.id == content.author_id).first()
                        print(f"ID: {content.id}")
                        print(f"  Автор: {author.first_name if author else 'Невідомий'}")
                        print(f"  Тип: {content.content_type.value}")
                        print(f"  Текст: {content.text[:100]}...")
                        print(f"  Дата: {content.created_at}")
                        print()
                
                elif action == "approve" and content_id:
                    from database.database import moderate_content
                    await moderate_content(content_id, settings.ADMIN_ID, True, "Схвалено через manage.py")
                    print(f"Контент {content_id} схвалено")
                
                elif action == "reject" and content_id:
                    from database.database import moderate_content
                    await moderate_content(content_id, settings.ADMIN_ID, False, "Відхилено через manage.py")
                    print(f"Контент {content_id} відхилено")
                
                elif action == "stats":
                    total = session.query(Content).count()
                    approved = session.query(Content).filter(Content.status == ContentStatus.APPROVED).count()
                    pending = session.query(Content).filter(Content.status == ContentStatus.PENDING).count()
                    rejected = session.query(Content).filter(Content.status == ContentStatus.REJECTED).count()
                    
                    print(f"Статистика контенту:")
                    print(f"  Всього: {total}")
                    print(f"  Схвалено: {approved}")
                    print(f"  На модерації: {pending}")
                    print(f"  Відхилено: {rejected}")
                
        except Exception as e:
            logger.error(f"Помилка управління контентом: {e}")
    
    async def cleanup_old_data(self, days: int = 30):
        """Очищення старих даних"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with get_db_session() as session:
                # Видалення старих рейтингів
                old_ratings = session.query(Rating).filter(
                    Rating.created_at < cutoff_date
                ).delete()
                
                # Видалення завершених дуелей старіше ніж 7 днів
                from database.models import DuelStatus
                old_duels = session.query(Duel).filter(
                    Duel.status == DuelStatus.COMPLETED,
                    Duel.completed_at < datetime.utcnow() - timedelta(days=7)
                ).delete()
                
                session.commit()
                
                print(f"Очищення завершено:")
                print(f"  Видалено старих рейтингів: {old_ratings}")
                print(f"  Видалено старих дуелей: {old_duels}")
                
        except Exception as e:
            logger.error(f"Помилка очищення: {e}")
    
    async def test_apis(self):
        """Тестування всіх API"""
        print("🧠 Тестування API...")
        
        # Тест Telegram API
        try:
            bot = await self.init_bot()
            me = await bot.get_me()
            print(f"✅ Telegram API: @{me.username}")
            await bot.session.close()
        except Exception as e:
            print(f"❌ Telegram API: {e}")
        
        # Тест OpenAI API
        if settings.OPENAI_API_KEY:
            try:
                from services.content_generator import content_generator
                joke = await content_generator.generate_jokes(1, "тест")
                if joke:
                    print(f"✅ OpenAI API: згенеровано жарт")
                else:
                    print(f"⚠️ OpenAI API: порожня відповідь")
            except Exception as e:
                print(f"❌ OpenAI API: {e}")
        else:
            print("⚠️ OpenAI API: не налаштовано")
        
        # Тест БД
        try:
            with get_db_session() as session:
                count = session.query(User).count()
                print(f"✅ Database: {count} користувачів")
        except Exception as e:
            print(f"❌ Database: {e}")

async def main():
    """Головна функція"""
    parser = argparse.ArgumentParser(description="Управління україномовним Telegram-ботом")
    
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")
    
    # Команда init
    init_parser = subparsers.add_parser("init", help="Ініціалізація проекту")
    
    # Команда health
    health_parser = subparsers.add_parser("health", help="Перевірка здоров'я")
    health_parser.add_argument("--json", action="store_true", help="Вивід у JSON форматі")
    
    # Команда stats
    stats_parser = subparsers.add_parser("stats", help="Статистика бота")
    stats_parser.add_argument("--json", action="store_true", help="Вивід у JSON форматі")
    
    # Команда users
    users_parser = subparsers.add_parser("users", help="Управління користувачами")
    users_parser.add_argument("action", choices=["list", "info", "add_points", "reset_points"])
    users_parser.add_argument("--user_id", type=int, help="ID користувача")
    users_parser.add_argument("--points", type=int, default=0, help="Кількість балів")
    
    # Команда content
    content_parser = subparsers.add_parser("content", help="Управління контентом")
    content_parser.add_argument("action", choices=["pending", "approve", "reject", "stats"])
    content_parser.add_argument("--content_id", type=int, help="ID контенту")
    
    # Команда cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Очищення старих даних")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Кількість днів для збереження")
    
    # Команда test
    test_parser = subparsers.add_parser("test", help="Тестування API")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = BotManager()
    
    try:
        if args.command == "init":
            print("🚀 Ініціалізація проекту...")
            await init_db()
            print("✅ База даних ініціалізована")
            
        elif args.command == "health":
            health = await manager.check_health()
            if args.json:
                print(json.dumps(health, indent=2, ensure_ascii=False))
            else:
                print(f"🏥 Здоров'я бота: {health['overall_status']}")
                if health.get('bot_info'):
                    print(f"🤖 Бот: @{health['bot_info']['username']}")
                if health.get('database_info'):
                    print(f"💾 БД: {health['database_info']['total_users']} користувачів")
                if health.get('errors'):
                    print("❌ Помилки:")
                    for error in health['errors']:
                        print(f"  - {error}")
                        
        elif args.command == "stats":
            stats = await manager.get_stats()
            if args.json:
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print(f"📊 Статистика бота:")
                print(f"  👥 Користувачів: {stats['users']['total']} (активних сьогодні: {stats['users']['active_today']})")
                print(f"  📝 Контенту: {stats['content']['total']} (схвалено: {stats['content']['approved']})")
                print(f"  ⚔️ Дуелей: {stats['duels']['total']} (активних: {stats['duels']['active']})")
                
        elif args.command == "users":
            await manager.manage_users(
                args.action,
                args.user_id,
                points=args.points
            )
            
        elif args.command == "content":
            await manager.manage_content(
                args.action,
                args.content_id
            )
            
        elif args.command == "cleanup":
            await manager.cleanup_old_data(args.days)
            
        elif args.command == "test":
            await manager.test_apis()
            
    except Exception as e:
        logger.error(f"Помилка виконання команди: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())