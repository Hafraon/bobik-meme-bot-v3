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
from typing import Dict, List, Optional, Tuple
import threading
import re

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

class QualityContentManager:
    """Менеджер високоякісного контенту"""
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client
        
        # Високоякісні Reddit джерела з жорсткими фільтрами
        self.reddit_sources = [
            {
                'name': 'Programming Humor Hot',
                'url': 'https://www.reddit.com/r/ProgrammerHumor/hot.json?limit=50',
                'min_upvotes': 800,  # Мінімум 800 upvotes
                'max_age_hours': 24,  # Не старше доби  
                'min_upvote_ratio': 0.85,  # Хороший ratio
                'min_comments': 30,  # Активне обговорення
                'weight': 5,
                'category': 'it_humor'
            },
            {
                'name': 'Memes Top Daily',
                'url': 'https://www.reddit.com/r/memes/top.json?t=day&limit=50',
                'min_upvotes': 3000,  # Топ контент
                'max_age_hours': 24,
                'min_upvote_ratio': 0.80,
                'min_comments': 50,
                'weight': 4,
                'category': 'general_humor'
            },
            {
                'name': 'Dank Memes Hot',
                'url': 'https://www.reddit.com/r/dankmemes/hot.json?limit=50',
                'min_upvotes': 1500,
                'max_age_hours': 18,
                'min_upvote_ratio': 0.82,
                'min_comments': 40,
                'weight': 4,
                'category': 'dank_humor'
            },
            {
                'name': 'Coding Humor',
                'url': 'https://www.reddit.com/r/coding/hot.json?limit=30',
                'min_upvotes': 200,  # Менше upvotes, але специфічний контент
                'max_age_hours': 48,
                'min_upvote_ratio': 0.85,
                'min_comments': 15,
                'weight': 3,
                'category': 'it_humor'
            }
        ]
        
        # Кураторський контент для різних часів дня
        self.curated_content = {
            'morning': [
                {
                    'title': 'Доброго ранку! Час дивитися чому prod впав вночі ☕',
                    'url': 'https://i.imgflip.com/1bij.jpg',
                    'source': 'Curated',
                    'quality_score': 95,
                    'ukrainian_context': True
                },
                {
                    'title': 'Понеділок, 9 ранку, планерка... І ти ще не встиг кави ☕😵',
                    'url': 'https://i.imgflip.com/30b1gx.jpg', 
                    'source': 'Curated',
                    'quality_score': 92,
                    'ukrainian_context': True
                }
            ],
            'work_day': [
                {
                    'title': 'Коли PM каже "це має бути швидка зміна" 🤡',
                    'url': 'https://i.imgflip.com/1g8my4.jpg',
                    'source': 'Curated', 
                    'quality_score': 98,
                    'ukrainian_context': True
                }
            ],
            'evening': [
                {
                    'title': 'Завершуємо день. Завтра точно пофіксимо всі bugs 🌅',
                    'url': 'https://i.imgflip.com/26am.jpg',
                    'source': 'Curated',
                    'quality_score': 90,
                    'ukrainian_context': True
                }
            ]
        }
        
        # Статистика якості контенту
        self.content_performance = {}
        self.posted_content_ids = set()
        
    async def get_reddit_posts(self, source: dict) -> List[dict]:
        """Отримує пости з Reddit API з фільтрацією по якості"""
        try:
            logger.info(f"🔍 Запит якісного контенту з {source['name']}")
            
            async with ClientSession() as session:
                # Додаємо User-Agent для Reddit API
                headers = {
                    'User-Agent': 'BobikBot/2.0 (Ukrainian Meme Bot)'
                }
                
                async with session.get(source['url'], headers=headers, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'data' in data and 'children' in data['data']:
                            posts = data['data']['children']
                            filtered_posts = self.filter_quality_posts(posts, source)
                            
                            logger.info(f"✅ {source['name']}: {len(filtered_posts)} якісних постів з {len(posts)}")
                            return filtered_posts
                        else:
                            logger.warning(f"⚠️ Незрозумілий формат від {source['name']}")
                    else:
                        logger.error(f"❌ HTTP {response.status} від {source['name']}")
                        
        except Exception as e:
            logger.error(f"❌ Помилка отримання з {source['name']}: {e}")
            
        return []
    
    def filter_quality_posts(self, posts: List[dict], source: dict) -> List[dict]:
        """Жорстко фільтрує пости за якістю"""
        filtered = []
        
        for post_wrapper in posts:
            post = post_wrapper['data']
            
            try:
                # Базові перевірки
                if post.get('stickied', False):  # Пропускаємо закріплені пости
                    continue
                    
                if post.get('over_18', False):  # Пропускаємо NSFW
                    continue
                    
                # Перевірка на зображення
                url = post.get('url', '')
                if not self.is_image_url(url):
                    continue
                
                # Фільтр по upvotes
                upvotes = post.get('ups', 0)
                if upvotes < source['min_upvotes']:
                    continue
                
                # Фільтр по ratio позитивних голосів
                upvote_ratio = post.get('upvote_ratio', 0)
                if upvote_ratio < source['min_upvote_ratio']:
                    continue
                
                # Фільтр по кількості коментарів (показник engagement)
                comments = post.get('num_comments', 0)
                if comments < source['min_comments']:
                    continue
                
                # Фільтр по віку поста
                created_utc = post.get('created_utc', 0)
                age_hours = (time.time() - created_utc) / 3600
                if age_hours > source['max_age_hours']:
                    continue
                
                # Фільтр по довжині заголовка (занадто довгі важко локалізувати)
                title = post.get('title', '')
                if len(title) > 200:
                    continue
                
                # Перевірка на дублікати
                post_id = post.get('id', '')
                if post_id in self.posted_content_ids:
                    continue
                
                # Розрахунок якості на основі метрик
                quality_score = self.calculate_quality_score(post)
                
                # Додаємо тільки високоякісний контент
                if quality_score >= 70:  # Мінімум 70% якості
                    filtered_post = {
                        'id': post_id,
                        'title': title,
                        'url': url,
                        'ups': upvotes,
                        'upvote_ratio': upvote_ratio,
                        'num_comments': comments,
                        'created_utc': created_utc,
                        'subreddit': post.get('subreddit', ''),
                        'author': post.get('author', ''),
                        'quality_score': quality_score,
                        'source': source['name'],
                        'category': source['category'],
                        'weight': source['weight']
                    }
                    filtered.append(filtered_post)
                    
            except Exception as e:
                logger.error(f"Помилка обробки поста: {e}")
                continue
                
        # Сортуємо за якістю
        filtered.sort(key=lambda x: x['quality_score'], reverse=True)
        return filtered[:10]  # Повертаємо топ-10 найякісніших
    
    def is_image_url(self, url: str) -> bool:
        """Перевіряє чи URL веде на зображення"""
        if not url:
            return False
            
        # Прямі посилання на зображення
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        if url.lower().endswith(image_extensions):
            return True
            
        # Reddit hosted images
        if 'i.redd.it' in url or 'i.reddit.com' in url:
            return True
            
        # Imgur images
        if 'imgur.com' in url and ('/a/' not in url and '/gallery/' not in url):
            return True
            
        return False
    
    def calculate_quality_score(self, post: dict) -> int:
        """Розраховує score якості поста (0-100)"""
        score = 0
        
        # Базовий score за upvotes (максимум 40 балів)
        upvotes = post.get('ups', 0)
        if upvotes >= 10000:
            score += 40
        elif upvotes >= 5000:
            score += 35
        elif upvotes >= 2000:
            score += 30
        elif upvotes >= 1000:
            score += 25
        elif upvotes >= 500:
            score += 20
        else:
            score += max(0, upvotes // 50)  # По 1 балу за кожні 50 upvotes
        
        # Бали за upvote ratio (максимум 20 балів)
        ratio = post.get('upvote_ratio', 0)
        score += int(ratio * 20)
        
        # Бали за engagement (коментарі) (максимум 20 балів)
        comments = post.get('num_comments', 0)
        if comments >= 500:
            score += 20
        elif comments >= 200:
            score += 15
        elif comments >= 100:
            score += 12
        elif comments >= 50:
            score += 10
        else:
            score += min(10, comments // 5)
        
        # Бали за свіжість (максимум 10 балів)
        age_hours = (time.time() - post.get('created_utc', 0)) / 3600
        if age_hours <= 6:
            score += 10
        elif age_hours <= 12:
            score += 8
        elif age_hours <= 24:
            score += 6
        else:
            score += max(0, 6 - int(age_hours // 12))
        
        # Бали за довжину заголовка (максимум 10 балів)
        title_len = len(post.get('title', ''))
        if 20 <= title_len <= 100:  # Оптимальна довжина
            score += 10
        elif 10 <= title_len <= 150:
            score += 7
        else:
            score += 3
        
        return min(100, score)  # Максимум 100 балів
    
    async def get_curated_content(self, time_context: str) -> Optional[dict]:
        """Повертає кураторський контент для конкретного контексту"""
        curated_list = self.curated_content.get(time_context, [])
        
        if not curated_list:
            return None
            
        # Фільтруємо неопубліковані
        unposted = [item for item in curated_list 
                   if item.get('url') not in self.posted_content_ids]
        
        if unposted:
            selected = random.choice(unposted)
            self.posted_content_ids.add(selected['url'])
            return selected
            
        return None
    
    async def get_best_quality_meme(self) -> Optional[dict]:
        """Отримує найкращий мем з усіх джерел"""
        all_posts = []
        
        # Збираємо пости з усіх Reddit джерел
        for source in self.reddit_sources:
            posts = await self.get_reddit_posts(source)
            all_posts.extend(posts)
        
        if not all_posts:
            logger.warning("⚠️ Не знайдено якісних постів з Reddit")
            # Fallback на кураторський контент
            time_context = self.get_time_context()
            return await self.get_curated_content(time_context)
        
        # Сортуємо за score якості та weight джерела
        all_posts.sort(key=lambda x: (x['quality_score'], x['weight']), reverse=True)
        
        # Повертаємо найкращий
        best_post = all_posts[0]
        self.posted_content_ids.add(best_post['id'])
        
        logger.info(f"🏆 Обрано топ мем: {best_post['title'][:50]}... (score: {best_post['quality_score']})")
        return best_post
    
    def get_time_context(self) -> str:
        """Визначає контекст часу"""
        hour = datetime.now().hour
        
        if 6 <= hour <= 10:
            return 'morning'
        elif 11 <= hour <= 17:
            return 'work_day'
        elif 18 <= hour <= 23:
            return 'evening'
        else:
            return 'work_day'  # Дефолт
    
    async def localize_with_advanced_ai(self, meme_data: dict) -> dict:
        """Розумна локалізація з урахуванням українського IT контексту"""
        if not self.openai_client:
            # Fallback без AI
            meme_data['localized_title'] = f"{meme_data['title']} 😄"
            return meme_data
        
        try:
            time_context = self.get_time_context()
            
            # Детальний промпт для якісної локалізації
            prompt = f'''
Ти - експерт з адаптації західних мемів для українських IT спеціалістів. 

КОНТЕКСТ МЕМУ:
- Оригінал: "{meme_data['title']}"
- Upvotes: {meme_data.get('ups', 0)} (показник якості)
- Коментарів: {meme_data.get('num_comments', 0)}
- Subreddit: r/{meme_data.get('subreddit', '')}
- Score якості: {meme_data.get('quality_score', 0)}/100
- Час дня: {time_context}

УКРАЇНСЬКІ IT РЕАЛІЇ:
- Замість "manager" → "тімлід", "PM", "менеджер"
- Замість "coffee" → "кава", "еспресо в офісі"
- Замість "salary" → "зарплата в доларах", "оклад"
- Замість "deadline" → "дедлайн", "терміни"
- Замість "bug" → "баг", "помилка"
- Замість "production" → "прод", "продакшн"

ПРАВИЛА ЛОКАЛІЗАЦІЇ:
1. НЕ ТІЛЬКИ ПЕРЕКЛАДИ - адаптуй суть гумору
2. Зберігай мемний стиль - коротко, влучно
3. Додавай емоджі (1-2, не більше)
4. Якщо західний контекст незрозумілий - замініть на український аналог
5. Використовуй сучасну українську IT мову
6. Максимум 90 символів

ПРИКЛАДИ ЯКІСНОЇ ЛОКАЛІЗАЦІЇ:
❌ Погано: "When your code works on first try" → "Коли твій код працює з першого разу"
✅ Добре: "Коли код запрацював з першого разу і ти підозрюєш підвох 🤔"

❌ Погано: "Monday morning standup" → "Понеділкова ранкова планерка"  
✅ Добре: "Понеділок, 9 ранку, стендап... А ти ще навіть кави не встиг ☕"

ЗАВДАННЯ: Створи ІДЕАЛЬНУ українську версію мему.

Українська локалізація (лише текст, без пояснень):
'''
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",  # GPT-4 для кращої якості
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.4,  # Баланс креативності та точності
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            localized_title = response.choices[0].message.content.strip()
            
            # Валідація результату
            if len(localized_title) > 100:
                localized_title = localized_title[:97] + "..."
            
            if len(localized_title) < 10:
                # Fallback якщо AI дав занадто короткий результат
                localized_title = f"{meme_data['title']} 😄"
            
            meme_data['localized_title'] = localized_title
            meme_data['localized'] = True
            meme_data['ai_quality'] = 'high'
            
            logger.info(f"🤖 AI локалізація (GPT-4): '{localized_title}'")
            
        except Exception as e:
            logger.error(f"🤖 Помилка AI локалізації: {e}")
            meme_data['localized_title'] = f"{meme_data['title']} 😄"
            meme_data['localized'] = False
            meme_data['ai_quality'] = 'fallback'
        
        return meme_data

class AdvancedBobikBot:
    def __init__(self):
        # Змінні середовища з Railway
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "7882259321:AAGGqql6LD6bzLHTODlHdKUYs2IJBZqsd6E")
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
                    logger.info("🤖 ChatGPT інтеграція активована (GPT-4)")
                except Exception as e:
                    logger.error(f"Помилка ініціалізації OpenAI: {e}")
            else:
                logger.info("🔑 OPENAI_API_KEY не налаштовано. Працюємо без AI.")
        
        # Ініціалізуємо менеджер якісного контенту
        self.content_manager = QualityContentManager(self.openai_client)
        
        # Покращена статистика
        self.stats = {
            'posts_today': 0,
            'total_posts': 0,
            'last_post_time': None,
            'successful_posts': 0,
            'failed_posts': 0,
            'high_quality_posts': 0,  # Пости з score > 80
            'ai_localized_posts': 0,
            'curated_posts': 0,
            'reddit_posts': 0,
            'average_quality_score': 0,
            'daily_stats': {},
            'posted_hashes': set(),
            'hourly_posts': {},
            'content_sources': {},
            'server_start_time': datetime.now()
        }
        
        # Оптимальний розклад для української аудиторії (11 постів)
        self.posting_schedule = [
            "06:00",  # 08:00 Київ - Ранкова кава ☕
            "08:00",  # 10:00 Київ - Початок робочого дня 💼
            "10:00",  # 12:00 Київ - Перед обідом
            "12:00",  # 14:00 Київ - Обідня перерва 🍽️
            "14:00",  # 16:00 Київ - Після обіду ⚡
            "16:00",  # 18:00 Київ - Кінець робочого дня
            "18:00",  # 20:00 Київ - Вечерня активність 🏠
            "20:00",  # 22:00 Київ - Прайм-тайм 📺
            "22:00",  # 00:00 Київ - Пізній вечір 🌙
            "00:00",  # 02:00 Київ - Нічні сови 🦉
            "03:00"   # 05:00 Київ - Рання пташка
        ]
        
        self.bot = None
        self.telegram_app = None
        logger.info("🐕 Бобік 2.0 з високоякісним контентом ініціалізовано!")

    def get_meme_hash(self, url: str) -> str:
        """Генерує хеш для мему для запобігання дублікатів"""
        return hashlib.md5(url.encode()).hexdigest()

    async def get_smart_meme(self) -> Optional[dict]:
        """Отримує найкращий мем з системи якісного контенту"""
        return await self.content_manager.get_best_quality_meme()

    def get_ukrainian_caption(self, meme_data: dict) -> str:
        """Генерує українську підпись для мему"""
        # Використовуємо AI локалізацію якщо доступна
        if meme_data.get('localized_title'):
            return meme_data['localized_title']
        
        # Fallback
        return f"{meme_data['title']} 😄"

    async def post_meme_to_channel(self, meme_data: dict) -> bool:
        """Публікує мем у канал Telegram"""
        try:
            caption = self.get_ukrainian_caption(meme_data)
            
            # Додаємо інформацію про якість та джерело
            footer_parts = []
            
            # Джерело
            footer_parts.append(f"🔗 {meme_data.get('source', 'Unknown')}")
            
            # AI локалізація
            if meme_data.get('localized'):
                footer_parts.append("🤖 AI")
            
            # Якість контенту
            quality_score = meme_data.get('quality_score', 0)
            if quality_score >= 90:
                footer_parts.append("🏆 TOP")
            elif quality_score >= 80:
                footer_parts.append("⭐ HIGH")
            
            # Reddit метрики (якщо є)
            if meme_data.get('ups'):
                if meme_data['ups'] >= 10000:
                    footer_parts.append(f"🔥 {meme_data['ups']//1000}K")
                elif meme_data['ups'] >= 1000:
                    footer_parts.append(f"👍 {meme_data['ups']//1000}K")
            
            footer = "\n\n" + " | ".join(footer_parts) if footer_parts else ""
            full_caption = caption + footer
            
            logger.info(f"📤 Публікуємо якісний мем: {caption[:50]}...")
            
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
            
            # Статистика якості
            quality_score = meme_data.get('quality_score', 0)
            if quality_score >= 80:
                self.stats['high_quality_posts'] += 1
            
            if meme_data.get('localized'):
                self.stats['ai_localized_posts'] += 1
            
            if meme_data.get('source') == 'Curated':
                self.stats['curated_posts'] += 1
            else:
                self.stats['reddit_posts'] += 1
            
            # Оновлюємо середній score якості
            if self.stats['total_posts'] > 0:
                current_avg = self.stats.get('average_quality_score', 0)
                self.stats['average_quality_score'] = (
                    (current_avg * (self.stats['total_posts'] - 1) + quality_score) / 
                    self.stats['total_posts']
                )
            
            # Додаємо хеш
            meme_hash = self.get_meme_hash(meme_data['url'])
            self.stats['posted_hashes'].add(meme_hash)
            
            # Зберігаємо джерело
            source = meme_data.get('source', 'Unknown')
            if source not in self.stats['content_sources']:
                self.stats['content_sources'][source] = 0
            self.stats['content_sources'][source] += 1
            
            # Годинна статистика
            current_hour = datetime.now().hour
            if current_hour not in self.stats['hourly_posts']:
                self.stats['hourly_posts'][current_hour] = 0
            self.stats['hourly_posts'][current_hour] += 1
            
            logger.info(f"✅ Якісний мем опубліковано! ID: {message.message_id}, Score: {quality_score}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка публікації мему: {e}")
            self.stats['failed_posts'] += 1
            return False

    async def scheduled_posting(self):
        """Автоматичне публікування за розкладом"""
        logger.info("⏰ Розпочато автоматичне публікування якісного контенту")
        
        while True:
            try:
                current_time = datetime.now().strftime("%H:%M")
                
                if current_time in self.posting_schedule:
                    logger.info(f"🎯 Час публікації якісного контенту: {current_time}")
                    
                    # Отримуємо найкращий мем
                    meme = await self.get_smart_meme()
                    if meme:
                        # Локалізуємо за допомогою AI
                        meme = await self.content_manager.localize_with_advanced_ai(meme)
                        
                        # Публікуємо
                        success = await self.post_meme_to_channel(meme)
                        if success:
                            logger.info(f"🎉 Якісний автопост успішний о {current_time}")
                        else:
                            logger.error(f"❌ Автопост невдалий о {current_time}")
                    else:
                        logger.error(f"❌ Не вдалося отримати якісний мем о {current_time}")
                    
                    # Чекаємо хвилину щоб не дублювати
                    await asyncio.sleep(70)
                
                # Перевіряємо кожні 30 секунд
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Помилка в автопубликуванні: {e}")
                await asyncio.sleep(60)

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
                "high_quality_posts": self.stats['high_quality_posts'],
                "average_quality_score": round(self.stats['average_quality_score'], 1),
                "ai_enabled": self.openai_client is not None,
                "ai_localized_posts": self.stats['ai_localized_posts'],
                "last_post": self.stats['last_post_time'].isoformat() if self.stats['last_post_time'] else None,
                "bot_status": "running" if self.bot else "initializing"
            }
            
            logger.info(f"✅ Health check OK: {self.stats['posts_today']} постів сьогодні, avg quality: {self.stats['average_quality_score']:.1f}")
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
            top_sources = sorted(self.stats['content_sources'].items(), key=lambda x: x[1], reverse=True)[:5]
            
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
                "quality": {
                    "high_quality_posts": self.stats['high_quality_posts'],
                    "average_score": round(self.stats['average_quality_score'], 1),
                    "quality_percentage": round((self.stats['high_quality_posts'] / max(1, self.stats['total_posts'])) * 100, 1)
                },
                "ai": {
                    "enabled": self.openai_client is not None,
                    "localized_posts": self.stats['ai_localized_posts'],
                    "localization_rate": round((self.stats['ai_localized_posts'] / max(1, self.stats['total_posts'])) * 100, 1)
                },
                "content_sources": dict(top_sources),
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
            logger.info("📤 Manual high-quality post requested via HTTP")
            
            # Отримуємо найкращий мем
            meme = await self.get_smart_meme()
            if meme:
                # Локалізуємо за допомогою AI
                meme = await self.content_manager.localize_with_advanced_ai(meme)
                
                # Публікуємо
                success = await self.post_meme_to_channel(meme)
                if success:
                    return json_response({
                        "status": "success",
                        "message": "Високоякісний мем опублікований",
                        "meme_title": meme.get('localized_title', meme.get('title', 'N/A')),
                        "source": meme.get('source', 'N/A'),
                        "quality_score": meme.get('quality_score', 0),
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
                    "message": "Не вдалося отримати якісний мем"
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

    # Telegram команди
    async def health_check_handler(self, update, context):
        """Health check handler для Telegram команд"""
        try:
            bot_info = await context.bot.get_me()
            
            health_text = f"""
🟢 **Бот здоровий!**

🤖 **Bot:** @{bot_info.username}
🌍 **Середовище:** {ENVIRONMENT}
📊 **Постів сьогодні:** {self.stats['posts_today']}
📈 **Всього постів:** {self.stats['total_posts']}
🏆 **Високоякісних:** {self.stats['high_quality_posts']}
⭐ **Середня якість:** {self.stats['average_quality_score']:.1f}/100
🧠 **AI локалізації:** {self.stats['ai_localized_posts']}
🤖 **AI статус:** {'✅ GPT-4 Активний' if self.openai_client else '❌ Неактивний'}
⏰ **Час:** {datetime.now().strftime('%H:%M:%S')}
            """
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=health_text,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Health check OK via Telegram")
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🔴 Помилка health check: {str(e)}"
            )

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
📊 **Статистика Бобік 2.0 - Якісний контент**

📈 **Загальна інформація:**
• Постів сьогодні: {self.stats['posts_today']}
• Всього постів: {self.stats['total_posts']}
• Успішних: {self.stats['successful_posts']}
• Помилок: {self.stats['failed_posts']}
• Успішність: {success_rate:.1f}%

🏆 **Якість контенту:**
• Високоякісних постів: {self.stats['high_quality_posts']}
• Середня якість: {self.stats['average_quality_score']:.1f}/100
• % якісного контенту: {(self.stats['high_quality_posts'] / max(1, self.stats['total_posts'])) * 100:.1f}%

🤖 **AI статистика:**
• Локалізовано постів: {self.stats['ai_localized_posts']}
• AI статус: {'✅ GPT-4 Активний' if self.openai_client else '❌ Неактивний'}
• % AI локалізації: {(self.stats['ai_localized_posts'] / max(1, self.stats['total_posts'])) * 100:.1f}%

📊 **Тип контенту:**
• Reddit постів: {self.stats['reddit_posts']}
• Кураторських постів: {self.stats['curated_posts']}

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
        
        await update.message.reply_text("🧪 Готую тестовий високоякісний пост...")
        
        meme = await self.get_smart_meme()
        if meme:
            meme = await self.content_manager.localize_with_advanced_ai(meme)
            success = await self.post_meme_to_channel(meme)
            
            if success:
                result_text = f"""
✅ **Тестовий пост опублікований!**

🔗 **Джерело:** {meme.get('source', 'N/A')}
⭐ **Якість:** {meme.get('quality_score', 0)}/100
🤖 **AI локалізація:** {'✅ Так' if meme.get('localized') else '❌ Ні'}
"""
                if meme.get('ups'):
                    result_text += f"👍 **Reddit upvotes:** {meme['ups']}\n"
                
                await update.message.reply_text(result_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Помилка публікації тестового поста")
        else:
            await update.message.reply_text("❌ Не вдалося отримати якісний мем для тесту")

    async def start_command(self, update, context):
        """Команда /start"""
        welcome_text = f"""
🐕 **Вітаю в Бобік 2.0!**

🧠😂🔥 Україномовний AI мем-бот з **високоякісним контентом**

📊 **Статистика:**
• Постів сьогодні: {self.stats['posts_today']}
• Всього постів: {self.stats['total_posts']}
• Середня якість: {self.stats['average_quality_score']:.1f}/100
• AI статус: {'🤖 GPT-4 Активний' if self.openai_client else '🔧 Базовий режим'}

🏆 **Особливості:**
• Тільки топ контент з Reddit (1000+ upvotes)
• Розумна AI локалізація українською  
• Фільтрація по якості та engagement
• Кураторський відбір мемів

⏰ **Автопости:** 11 разів на день
🇺🇦 **Оптимізовано:** Для української IT аудиторії
🌍 **Середовище:** {ENVIRONMENT}

Приєднуйтесь до каналу: @BobikFun
        """
        
        if update.effective_user.id == self.admin_id:
            welcome_text += "\n\n🔧 **Адмін команди:**\n/stats - детальна статистика\n/test - тестовий пост\n/health - статус бота"
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    def main(self):
        """Головна функція запуску бота"""
        logger.info("🚀 Запуск Бобік 2.0 з високоякісним контентом...")
        
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
                logger.info(f"🏆 Система високоякісного контенту активна")
                logger.info(f"🤖 AI локалізація: {'✅ GPT-4' if self.openai_client else '❌ Відключена'}")
                
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