import requests
import asyncio
import random
import logging
import json
import time
import hashlib
import os
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from typing import Dict, List, Optional
import threading

# HTTP сервер для Railway
from aiohttp import web, ClientSession
from aiohttp.web import Response, json_response

# Для ChatGPT інтеграції
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI не встановлено. Працюємо без AI локалізації.")

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Railway налаштування
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

class AdvancedBobikBot:
    def __init__(self):
        # Змінні середовища з Railway
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "7882259321:AAGGqql6LD6bzLHTODlHdKUYs2IJBZqsd6F")
        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "1002889574159")  # Твій канал ID
        self.admin_id = int(os.getenv("ADMIN_ID", "603047391"))
        
        # Логування налаштувань
        logger.info(f"🚀 Запуск в режимі: {ENVIRONMENT}")
        logger.info(f"📱 Канал ID: {self.channel_id}")
        logger.info(f"👤 Адмін ID: {self.admin_id}")
        logger.info(f"🌐 HTTP порт: {PORT}")
        
        # OpenAI клієнт (опціонально)
        self.openai_client = None
        if OPENAI_AVAILABLE:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key and openai_key.startswith('sk-'):
                try:
                    self.openai_client = OpenAI(api_key=openai_key)
                    logger.info("🤖 ChatGPT інтеграція активована")
                except Exception as e:
                    logger.error(f"Помилка ініціалізації OpenAI: {e}")
            else:
                logger.info("🔑 OPENAI_API_KEY не налаштовано. Працюємо без AI.")
        
        # Покращена статистика з українізацією
        self.stats = {
            'posts_today': 0,
            'total_posts': 0,
            'last_post_time': None,
            'successful_posts': 0,
            'failed_posts': 0,
            'best_engagement_time': None,
            'daily_stats': {},
            'posted_memes': set(),
            'posted_hashes': set(),  # Хеші для дедуплікації
            'hourly_posts': {},
            'last_api_check': None,
            'localized_posts': 0,  # Кількість локалізованих постів
            'api_failures': {},     # Статистика відмов API
            'content_sources': {},   # Статистика джерел контенту
            'server_start_time': datetime.now()
        }
        
        # Оптимальний розклад для української аудиторії (UTC+2 = Київський час)
        self.posting_schedule = [
            "03:00",  # 05:00 Київ - Рання пташка
            "05:00",  # 07:00 Київ - Ранкова кава ☕
            "07:00",  # 09:00 Київ - Початок робочого дня 💼
            "09:30",  # 11:30 Київ - Перед обідом
            "11:00",  # 13:00 Київ - Обідня перерва 🍽️
            "13:00",  # 15:00 Київ - Після обіду ⚡
            "15:00",  # 17:00 Київ - Кінець робочого дня
            "17:00",  # 19:00 Київ - Вечерня активність 🏠
            "19:00",  # 21:00 Київ - Прайм-тайм 📺
            "21:00",  # 23:00 Київ - Релакс 🌙
            "23:00"   # 01:00 Київ - Нічні сови 🦉
        ]
        
        # Розумні API з fallback системою
        self.api_sources = [
            {
                'name': 'Reddit Dank Memes',
                'url': 'https://meme-api.herokuapp.com/gimme/dankmemes',
                'weight': 3,
                'ukrainian_friendly': True
            },
            {
                'name': 'Reddit Programming Humor',
                'url': 'https://meme-api.herokuapp.com/gimme/ProgrammerHumor',
                'weight': 4,
                'ukrainian_friendly': True  # IT аудиторія
            },
            {
                'name': 'Reddit Wholesome Memes',
                'url': 'https://meme-api.herokuapp.com/gimme/wholesomememes',
                'weight': 2,
                'ukrainian_friendly': True
            },
            {
                'name': 'General Memes',
                'url': 'https://meme-api.herokuapp.com/gimme',
                'weight': 2,
                'ukrainian_friendly': False  # Потребує перевірки
            },
            {
                'name': 'Reddit Memes',
                'url': 'https://meme-api.herokuapp.com/gimme/memes',
                'weight': 3,
                'ukrainian_friendly': True
            }
        ]
        
        # Контекстні українські підписи для різних типів мемів
        self.ukrainian_contexts = {
            'morning': [
                "Доброго ранку, програмісти! ☕",
                "Ранкова доза мотивації для IT команди! 💪",
                "Кава готова, мем теж! Час працювати! ⚡"
            ],
            'work': [
                "Коли код нарешті запрацював... 🎉",
                "Життя программіста у двох словах 😄",
                "Релейтбл контент для наших айтішників! 🤓"
            ],
            'evening': [
                "Завершуємо день з хорошим настроєм! 😊",
                "Релакс після важкого дня коду 💆‍♂️",
                "Вечірній мем для душі 🌅"
            ],
            'general': [
                "Трохи гумору для вашого дня! 😂",
                "Коли мем просто мем, але він точний! 💯",
                "IT гумор, який зрозуміє кожен 🎯"
            ]
        }
        
        self.bot = None
        self.telegram_app = None
        logger.info("🐕 Бобік 2.0 ініціалізовано успішно!")

    # HTTP endpoints для Railway
    async def health_endpoint(self, request):
        """HTTP Health check endpoint для Railway"""
        try:
            uptime = datetime.now() - self.stats['server_start_time']
            uptime_seconds = int(uptime.total_seconds())
            
            health_data = {
                "status": "healthy",
                "environment": ENVIRONMENT,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime_seconds,
                "total_posts": self.stats['total_posts'],
                "posts_today": self.stats['posts_today'],
                "ai_enabled": self.openai_client is not None,
                "last_post": self.stats['last_post_time'].isoformat() if self.stats['last_post_time'] else None,
                "bot_status": "running" if self.bot else "initializing"
            }
            
            logger.info(f"✅ Health check OK: uptime {uptime_seconds}s, posts today: {self.stats['posts_today']}")
            return json_response(health_data, status=200)
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return json_response({
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=503)

    async def stats_endpoint(self, request):
        """HTTP Stats endpoint"""
        try:
            # Розрахунок успішності
            total_attempts = self.stats['successful_posts'] + self.stats['failed_posts']
            success_rate = (self.stats['successful_posts'] / total_attempts * 100) if total_attempts > 0 else 0
            
            # Топ джерела
            top_sources = sorted(self.stats['content_sources'].items(), key=lambda x: x[1], reverse=True)[:3]
            
            stats_data = {
                "status": "ok",
                "environment": ENVIRONMENT,
                "timestamp": datetime.now().isoformat(),
                "posts": {
                    "today": self.stats['posts_today'],
                    "total": self.stats['total_posts'],
                    "successful": self.stats['successful_posts'],
                    "failed": self.stats['failed_posts'],
                    "success_rate": round(success_rate, 1)
                },
                "ai": {
                    "enabled": self.openai_client is not None,
                    "localized_posts": self.stats['localized_posts']
                },
                "sources": dict(top_sources),
                "schedule": {
                    "posts_per_day": len(self.posting_schedule),
                    "next_post_time": self.get_next_post_time()
                },
                "uptime": int((datetime.now() - self.stats['server_start_time']).total_seconds())
            }
            
            return json_response(stats_data, status=200)
            
        except Exception as e:
            logger.error(f"❌ Stats endpoint failed: {e}")
            return json_response({"error": str(e)}, status=500)

    async def manual_post_endpoint(self, request):
        """HTTP endpoint для ручного постингу"""
        try:
            logger.info("📤 Manual post requested via HTTP")
            
            # Отримуємо мем
            meme = await self.get_smart_meme()
            if meme:
                # Локалізуємо за допомогою AI
                meme = await self.localize_with_ai(meme)
                
                # Публікуємо
                success = await self.post_meme_to_channel(meme)
                if success:
                    return json_response({
                        "status": "success",
                        "message": "Мем опублікований",
                        "meme_title": meme.get('title', 'N/A'),
                        "source": meme.get('source', 'N/A'),
                        "localized": meme.get('localized', False)
                    }, status=200)
                else:
                    return json_response({
                        "status": "error",
                        "message": "Помилка публікації"
                    }, status=500)
            else:
                return json_response({
                    "status": "error",
                    "message": "Не вдалося отримати мем"
                }, status=404)
                
        except Exception as e:
            logger.error(f"❌ Manual post failed: {e}")
            return json_response({"error": str(e)}, status=500)

    def get_next_post_time(self) -> str:
        """Визначає час наступного поста"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            current_minutes = datetime.now().hour * 60 + datetime.now().minute
            
            # Конвертуємо розклад у хвилини
            schedule_minutes = []
            for time_str in self.posting_schedule:
                hour, minute = map(int, time_str.split(':'))
                schedule_minutes.append(hour * 60 + minute)
            
            # Знаходимо наступний час
            for schedule_time in sorted(schedule_minutes):
                if schedule_time > current_minutes:
                    hour = schedule_time // 60
                    minute = schedule_time % 60
                    return f"{hour:02d}:{minute:02d}"
            
            # Якщо сьогодні часу немає, повертаємо перший час завтра
            first_time = min(schedule_minutes)
            hour = first_time // 60
            minute = first_time % 60
            return f"{hour:02d}:{minute:02d} (завтра)"
            
        except Exception:
            return "N/A"

    def get_meme_hash(self, url: str) -> str:
        """Генерує хеш для мему для запобігання дублікатів"""
        return hashlib.md5(url.encode()).hexdigest()

    async def get_meme_from_api(self, source: dict) -> Optional[dict]:
        """Отримує мем з конкретного API джерела з обробкою помилок"""
        try:
            logger.info(f"🔍 Запит до {source['name']}")
            
            async with ClientSession() as session:
                async with session.get(source['url'], timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Перевіряємо чи це масив чи окремий об'єкт
                        if isinstance(data, list) and len(data) > 0:
                            meme_data = data[0]
                        elif isinstance(data, dict):
                            meme_data = data
                        else:
                            logger.warning(f"⚠️ Незрозумілий формат відповіді від {source['name']}")
                            return None
                        
                        # Валідація даних мему
                        if not all(key in meme_data for key in ['url', 'title']):
                            logger.warning(f"⚠️ Неповні дані мему від {source['name']}")
                            return None
                        
                        # Перевірка на дублікати
                        meme_hash = self.get_meme_hash(meme_data['url'])
                        if meme_hash in self.stats['posted_hashes']:
                            logger.info(f"🔄 Мем вже був опублікований, пропускаємо")
                            return None
                        
                        # Додаємо метадані
                        meme_data['source'] = source['name']
                        meme_data['hash'] = meme_hash
                        meme_data['ukrainian_friendly'] = source['ukrainian_friendly']
                        
                        # Оновлюємо статистику джерел
                        if source['name'] not in self.stats['content_sources']:
                            self.stats['content_sources'][source['name']] = 0
                        self.stats['content_sources'][source['name']] += 1
                        
                        logger.info(f"✅ Отримано мем від {source['name']}: {meme_data['title'][:50]}...")
                        return meme_data
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Таймаут для {source['name']}")
            self.stats['api_failures'][source['name']] = self.stats['api_failures'].get(source['name'], 0) + 1
        except Exception as e:
            logger.error(f"❌ Помилка для {source['name']}: {e}")
            self.stats['api_failures'][source['name']] = self.stats['api_failures'].get(source['name'], 0) + 1
        
        return None

    async def get_smart_meme(self) -> Optional[dict]:
        """Розумне отримання мему з fallback між API"""
        
        # Сортуємо джерела за вагою та успішністю
        sorted_sources = sorted(
            self.api_sources, 
            key=lambda x: (
                x['weight'], 
                -self.stats['api_failures'].get(x['name'], 0)
            ), 
            reverse=True
        )
        
        # Спробуємо кілька джерел
        for source in sorted_sources:
            meme = await self.get_meme_from_api(source)
            if meme:
                return meme
            
            # Невелика затримка між спробами
            await asyncio.sleep(1)
        
        logger.error("❌ Не вдалося отримати мем з жодного джерела")
        return None

    def get_time_context(self) -> str:
        """Визначає контекст часу для українських підписів"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 11:
            return 'morning'
        elif 11 <= current_hour < 17:
            return 'work'
        elif 17 <= current_hour < 23:
            return 'evening'
        else:
            return 'general'

    async def localize_with_ai(self, meme_data: dict) -> dict:
        """Локалізація мему за допомогою ChatGPT"""
        if not self.openai_client:
            return meme_data
        
        try:
            time_context = self.get_time_context()
            
            prompt = f"""
            Ти - експерт з локалізації мемів для української IT аудиторії. 

            Оригінальний заголовок мему: "{meme_data['title']}"
            Контекст часу: {time_context}

            Завдання:
            1. Переклади/адаптуй заголовок українською мовою
            2. Зроби його релевантним для українських програмістів/IT спеціалістів
            3. Зберігай гумор та стиль
            4. Додай відповідний емоджі
            5. Максимум 100 символів

            Приклад стилю: "Коли код нарешті запрацював 🎉", "Життя програміста у двох словах 😄"

            Відповідь лише українською, без пояснень:
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            localized_title = response.choices[0].message.content.strip()
            
            # Якщо відповідь занадто довга або порожня, використовуємо fallback
            if len(localized_title) > 100 or len(localized_title) < 5:
                localized_title = f"{meme_data['title']} 😄"
            
            meme_data['localized_title'] = localized_title
            meme_data['localized'] = True
            self.stats['localized_posts'] += 1
            
            logger.info(f"🤖 AI локалізація: '{meme_data['title']}' → '{localized_title}'")
            
        except Exception as e:
            logger.error(f"🤖 Помилка AI локалізації: {e}")
            meme_data['localized'] = False
        
        return meme_data

    def get_ukrainian_caption(self, meme_data: dict) -> str:
        """Генерує українську підпись для мему"""
        time_context = self.get_time_context()
        
        # Використовуємо AI локалізацію якщо доступна
        if meme_data.get('localized_title'):
            return meme_data['localized_title']
        
        # Fallback до контекстних підписів
        captions = self.ukrainian_contexts.get(time_context, self.ukrainian_contexts['general'])
        
        # Додаємо оригінальний заголовок якщо він короткий
        original_title = meme_data['title']
        if len(original_title) < 50:
            return f"{random.choice(captions)}\n\n{original_title} 😄"
        else:
            return random.choice(captions)

    async def post_meme_to_channel(self, meme_data: dict) -> bool:
        """Публікує мем у канал Telegram"""
        try:
            caption = self.get_ukrainian_caption(meme_data)
            
            # Додаємо інформацію про джерело та статистику
            footer = f"\n\n🔗 Джерело: {meme_data['source']}"
            if meme_data.get('localized'):
                footer += " | 🤖 AI локалізовано"
            
            full_caption = caption + footer
            
            logger.info(f"📤 Публікуємо мем: {caption[:50]}...")
            
            # Відправляємо мем
            message = await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=meme_data['url'],
                caption=full_caption,
                parse_mode='HTML'
            )
            
            # Оновлюємо статистику
            self.stats['successful_posts'] += 1
            self.stats['total_posts'] += 1
            self.stats['posts_today'] += 1
            self.stats['last_post_time'] = datetime.now()
            self.stats['posted_hashes'].add(meme_data['hash'])
            
            # Зберігаємо годинну статистику
            current_hour = datetime.now().hour
            if current_hour not in self.stats['hourly_posts']:
                self.stats['hourly_posts'][current_hour] = 0
            self.stats['hourly_posts'][current_hour] += 1
            
            logger.info(f"✅ Мем опубліковано успішно! ID: {message.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка публікації мему: {e}")
            self.stats['failed_posts'] += 1
            return False

    async def scheduled_posting(self):
        """Автоматичне публікування за розкладом"""
        logger.info("⏰ Розпочато автоматичне публікування за розкладом")
        
        while True:
            try:
                current_time = datetime.now().strftime("%H:%M")
                
                if current_time in self.posting_schedule:
                    logger.info(f"🎯 Час публікації: {current_time}")
                    
                    # Отримуємо мем
                    meme = await self.get_smart_meme()
                    if meme:
                        # Локалізуємо за допомогою AI
                        meme = await self.localize_with_ai(meme)
                        
                        # Публікуємо
                        success = await self.post_meme_to_channel(meme)
                        if success:
                            logger.info(f"🎉 Автопост успішний о {current_time}")
                        else:
                            logger.error(f"❌ Автопост невдалий о {current_time}")
                    
                    # Чекаємо хвилину щоб не дублювати
                    await asyncio.sleep(70)
                
                # Перевіряємо кожні 30 секунд
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Помилка в автопубликуванні: {e}")
                await asyncio.sleep(60)

    async def health_check_handler(self, update, context):
        """Health check handler для Telegram команд"""
        try:
            bot_info = await context.bot.get_me()
            health_data = {
                "status": "healthy",
                "bot_username": bot_info.username,
                "environment": ENVIRONMENT,
                "timestamp": datetime.now().isoformat(),
                "total_posts": self.stats['total_posts'],
                "posts_today": self.stats['posts_today'],
                "ai_enabled": self.openai_client is not None
            }
            
            # Відправляємо health статус у вигляді повідомлення
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"🟢 Бот здоровий!\n\n"
                         f"🤖 Username: @{bot_info.username}\n"
                         f"🌍 Середовище: {ENVIRONMENT}\n"
                         f"📊 Постів сьогодні: {self.stats['posts_today']}\n"
                         f"📈 Всього постів: {self.stats['total_posts']}\n"
                         f"🧠 AI: {'✅ Активний' if self.openai_client else '❌ Неактивний'}\n"
                         f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
            
            logger.info(f"✅ Health check OK: {health_data}")
            return health_data
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"🔴 Помилка health check: {str(e)}"
                )
            return {"status": "unhealthy", "error": str(e)}

    async def stats_command(self, update, context):
        """Команда для перегляду статистики"""
        if update.effective_user.id != self.admin_id:
            await update.message.reply_text("❌ Немає доступу")
            return
        
        # Розрахунок успішності
        total_attempts = self.stats['successful_posts'] + self.stats['failed_posts']
        success_rate = (self.stats['successful_posts'] / total_attempts * 100) if total_attempts > 0 else 0
        
        # Топ джерела
        top_sources = sorted(self.stats['content_sources'].items(), key=lambda x: x[1], reverse=True)[:3]
        sources_text = "\n".join([f"• {name}: {count}" for name, count in top_sources]) if top_sources else "Немає даних"
        
        # Найактивніші години
        top_hours = sorted(self.stats['hourly_posts'].items(), key=lambda x: x[1], reverse=True)[:3]
        hours_text = "\n".join([f"• {hour:02d}:00: {count} постів" for hour, count in top_hours]) if top_hours else "Немає даних"
        
        stats_text = f"""
📊 **Статистика Бобік 2.0**

📈 **Загальна інформація:**
• Постів сьогодні: {self.stats['posts_today']}
• Всього постів: {self.stats['total_posts']}
• Успішних: {self.stats['successful_posts']}
• Помилок: {self.stats['failed_posts']}
• Успішність: {success_rate:.1f}%

🤖 **AI статистика:**
• Локалізовано постів: {self.stats['localized_posts']}
• AI статус: {'✅ Активний' if self.openai_client else '❌ Неактивний'}

🔗 **Топ джерела:**
{sources_text}

⏰ **Найактивніші години:**
{hours_text}

🕐 **Останній пост:** {self.stats['last_post_time'].strftime('%H:%M:%S') if self.stats['last_post_time'] else 'Ще не було'}

🌍 **Середовище:** {ENVIRONMENT}
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def test_post_command(self, update, context):
        """Команда для тестової публікації"""
        if update.effective_user.id != self.admin_id:
            await update.message.reply_text("❌ Немає доступу")
            return
        
        await update.message.reply_text("🧪 Готую тестовий пост...")
        
        meme = await self.get_smart_meme()
        if meme:
            meme = await self.localize_with_ai(meme)
            success = await self.post_meme_to_channel(meme)
            
            if success:
                await update.message.reply_text("✅ Тестовий пост опублікований!")
            else:
                await update.message.reply_text("❌ Помилка публікації тестового поста")
        else:
            await update.message.reply_text("❌ Не вдалося отримати мем для тесту")

    async def start_command(self, update, context):
        """Команда /start"""
        welcome_text = f"""
🐕 **Вітаю в Бобік 2.0!**

🧠😂🔥 Україномовний AI мем-бот з розумною локалізацією

📊 **Статистика:**
• Постів сьогодні: {self.stats['posts_today']}
• Всього постів: {self.stats['total_posts']}
• AI статус: {'🤖 Активний' if self.openai_client else '🔧 Базовий режим'}

⏰ **Автопости:** 11 разів на день
🇺🇦 **Оптимізовано:** Для української IT аудиторії
🌍 **Середовище:** {ENVIRONMENT}

Приєднуйтесь до каналу: @BobikFun
        """
        
        if update.effective_user.id == self.admin_id:
            welcome_text += "\n\n🔧 **Адмін команди:**\n/stats - статистика\n/test - тестовий пост\n/health - статус бота"
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def create_http_server(self):
        """Створює HTTP сервер для Railway"""
        app = web.Application()
        
        # Додаємо маршрути
        app.router.add_get('/health', self.health_endpoint)
        app.router.add_get('/stats', self.stats_endpoint)
        app.router.add_post('/post', self.manual_post_endpoint)
        app.router.add_get('/', self.health_endpoint)  # Root endpoint
        
        logger.info(f"🌐 Запуск HTTP сервера на порті {PORT}")
        
        # Запускаємо сервер
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
        
        logger.info(f"✅ HTTP сервер запущено на http://0.0.0.0:{PORT}")
        return runner

    def main(self):
        """Головна функція запуску бота"""
        logger.info("🚀 Запуск Бобік 2.0...")
        
        # Створюємо додаток
        self.telegram_app = Application.builder().token(self.bot_token).build()
        self.bot = self.telegram_app.bot
        
        # Додаємо обробники команд
        self.telegram_app.add_handler(CommandHandler("start", self.start_command))
        self.telegram_app.add_handler(CommandHandler("stats", self.stats_command))
        self.telegram_app.add_handler(CommandHandler("test", self.test_post_command))
        self.telegram_app.add_handler(CommandHandler("health", self.health_check_handler))
        
        # Запускаємо бота та HTTP сервер
        async def start_bot():
            try:
                # Запускаємо HTTP сервер для Railway
                http_runner = await self.create_http_server()
                
                # ВАЖЛИВО: Ініціалізуємо Telegram Application
                await self.telegram_app.initialize()
                
                # Запускаємо Telegram бота
                await self.telegram_app.start()
                await self.telegram_app.updater.start_polling()
                
                logger.info("🎉 Бобік 2.0 успішно запущений!")
                logger.info(f"📱 Публікування в канал: {self.channel_id}")
                logger.info(f"⏰ Розклад: {len(self.posting_schedule)} публікацій на день")
                logger.info(f"🌐 HTTP сервер доступний на порті {PORT}")
                
                # Запускаємо планувальник постів ПІСЛЯ успішного запуску бота
                posting_task = asyncio.create_task(self.scheduled_posting())
                
                # Чекаємо завершення
                try:
                    await posting_task
                except KeyboardInterrupt:
                    logger.info("🛑 Отримано сигнал зупинки")
                finally:
                    logger.info("🔄 Зупиняємо бота...")
                    await self.telegram_app.stop()
                    await self.telegram_app.shutdown()
                    await http_runner.cleanup()
                    logger.info("✅ Бот зупинено")
                    
            except Exception as e:
                logger.error(f"❌ Помилка запуску: {e}")
                raise
        
        # Запускаємо асинхронний код
        try:
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            logger.info("🛑 Бот зупинено користувачем")
        except Exception as e:
            logger.error(f"❌ Критична помилка: {e}")

if __name__ == "__main__":
    bot = AdvancedBobikBot()
    bot.main()