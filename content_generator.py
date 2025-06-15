#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 AI генерація контенту для бота 🧠😂🔥
"""

import logging
import asyncio
import aiohttp
from typing import List, Optional, Dict
from datetime import datetime

from config.settings import settings, EMOJI

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Сервіс генерації контенту через OpenAI API"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"
        
    async def generate_jokes(self, count: int = 5, theme: str = "загальний") -> List[str]:
        """Генерація українських анекдотів"""
        if not self.api_key:
            logger.warning("🤖 OpenAI API ключ не налаштовано")
            return []
        
        try:
            prompt = self._create_joke_prompt(theme, count)
            
            async with aiohttp.ClientSession() as session:
                response = await self._make_openai_request(session, prompt)
                
                if response:
                    jokes = self._parse_jokes_response(response)
                    logger.info(f"🧠 Згенеровано {len(jokes)} анекдотів на тему '{theme}'")
                    return jokes
                
        except Exception as e:
            logger.error(f"Помилка генерації анекдотів: {e}")
        
        return []
    
    async def generate_meme_captions(self, count: int = 5) -> List[str]:
        """Генерація підписів для мемів"""
        if not self.api_key:
            return []
        
        try:
            prompt = self._create_meme_caption_prompt(count)
            
            async with aiohttp.ClientSession() as session:
                response = await self._make_openai_request(session, prompt)
                
                if response:
                    captions = self._parse_captions_response(response)
                    logger.info(f"😂 Згенеровано {len(captions)} підписів для мемів")
                    return captions
                
        except Exception as e:
            logger.error(f"Помилка генерації підписів: {e}")
        
        return []
    
    async def improve_user_joke(self, joke_text: str) -> str:
        """Покращення користувацького жарту"""
        if not self.api_key:
            return joke_text
        
        try:
            prompt = f"""
            Покращ цей український жарт, зроби його смішнішим та грамотнішим, але збережи основну ідею:

            Оригінальний жарт: {joke_text}

            Вимоги:
            - Українська мова
            - Збережи суть та ідею
            - Покращ структуру та подачу
            - Додай емоційності
            - Максимум 300 символів

            Покращений жарт:
            """
            
            async with aiohttp.ClientSession() as session:
                response = await self._make_openai_request(session, prompt)
                
                if response and response.strip():
                    improved_joke = response.strip()
                    logger.info(f"✨ Покращено жарт користувача")
                    return improved_joke
                
        except Exception as e:
            logger.error(f"Помилка покращення жарту: {e}")
        
        return joke_text
    
    async def generate_daily_motivation(self) -> str:
        """Генерація щоденної мотиваційної фрази"""
        if not self.api_key:
            return f"{EMOJI['fire']} Гарного дня, друже! Сміхайся та будь щасливим!"
        
        try:
            current_date = datetime.now().strftime("%d %B %Y")
            current_day = datetime.now().strftime("%A")
            
            day_names = {
                "Monday": "понеділок",
                "Tuesday": "вівторок", 
                "Wednesday": "середа",
                "Thursday": "четвер",
                "Friday": "п'ятниця",
                "Saturday": "субота",
                "Sunday": "неділя"
            }
            
            ukrainian_day = day_names.get(current_day, current_day)
            
            prompt = f"""
            Створи коротку мотиваційну фразу українською мовою для щоденної розсилки в Telegram боті.

            Сьогодні: {ukrainian_day}, {current_date}

            Вимоги:
            - Українська мова
            - Позитивний настрій
            - Максимум 100 символів
            - Згадка про гумор або сміх
            - Включи 1-2 емодзі
            - Враховуй день тижня

            Мотиваційна фраза:
            """
            
            async with aiohttp.ClientSession() as session:
                response = await self._make_openai_request(session, prompt)
                
                if response:
                    motivation = response.strip()
                    logger.info(f"💪 Згенеровано мотиваційну фразу")
                    return motivation
                
        except Exception as e:
            logger.error(f"Помилка генерації мотивації: {e}")
        
        return f"{EMOJI['fire']} Чудового {ukrainian_day}! Нехай день буде сповнений сміху!"
    
    async def check_content_appropriateness(self, content: str) -> Dict[str, any]:
        """Перевірка контенту на відповідність правилам"""
        if not self.api_key:
            return {"appropriate": True, "reason": "", "suggestion": ""}
        
        try:
            prompt = f"""
            Проаналізуй цей контент на відповідність правилам українського гумористичного бота:

            Контент: {content}

            Критерії перевірки:
            1. Чи немає образливих слів чи дискримінації?
            2. Чи підходить для аудиторії 16+?
            3. Чи дотримується норм української мови?
            4. Чи є смішним/розважальним?

            Відповідь надай у форматі:
            ПІДХОДИТЬ: так/ні
            ПРИЧИНА: (якщо не підходить)
            ПРОПОЗИЦІЯ: (як покращити)
            """
            
            async with aiohttp.ClientSession() as session:
                response = await self._make_openai_request(session, prompt)
                
                if response:
                    return self._parse_appropriateness_response(response)
                
        except Exception as e:
            logger.error(f"Помилка перевірки контенту: {e}")
        
        return {"appropriate": True, "reason": "", "suggestion": ""}
    
    def _create_joke_prompt(self, theme: str, count: int) -> str:
        """Створення промпту для генерації анекдотів"""
        themes_description = {
            "програмування": "про програмістів, код, комп'ютери, IT",
            "робота": "про роботу, офіс, колег, босів",
            "сім'я": "про сімейне життя, дітей, батьків",
            "школа": "про навчання, учнів, вчителів",
            "загальний": "на різні теми"
        }
        
        theme_desc = themes_description.get(theme, "на різні теми")
        
        return f"""
        Створи {count} коротких українських анекдотів {theme_desc}.

        Вимоги:
        - Українська мова
        - Кожен анекдот 2-4 речення
        - Смішні та сучасні
        - Без образ та мату
        - Позитивний гумор
        - Кожен анекдот на новому рядку, нумеровані

        Анекдоти:
        """
    
    def _create_meme_caption_prompt(self, count: int) -> str:
        """Створення промпту для підписів мемів"""
        return f"""
        Створи {count} смішних підписів для мемів українською мовою.

        Вимоги:
        - Українська мова
        - Короткі (до 50 символів)
        - Сучасні інтернет-меми
        - Можна використовувати сленг
        - Різноманітні теми
        - Кожен підпис на новому рядку

        Підписи:
        """
    
    async def _make_openai_request(self, session: aiohttp.ClientSession, prompt: str) -> Optional[str]:
        """Виконання запиту до OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Ти український гуморист, який створює смішний контент для Telegram бота. Відповідай тільки українською мовою."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.8
        }
        
        try:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API помилка {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Таймаут запиту до OpenAI API")
            return None
        except Exception as e:
            logger.error(f"Помилка запиту до OpenAI: {e}")
            return None
    
    def _parse_jokes_response(self, response: str) -> List[str]:
        """Парсинг відповіді з анекдотами"""
        jokes = []
        lines = response.strip().split('\n')
        
        current_joke = ""
        for line in lines:
            line = line.strip()
            if not line:
                if current_joke:
                    jokes.append(current_joke.strip())
                    current_joke = ""
                continue
            
            # Видаляємо нумерацію
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if current_joke:
                    jokes.append(current_joke.strip())
                current_joke = line[2:].strip()
            else:
                current_joke += " " + line
        
        # Додаємо останній жарт
        if current_joke:
            jokes.append(current_joke.strip())
        
        # Фільтруємо та очищуємо
        cleaned_jokes = []
        for joke in jokes:
            joke = joke.strip()
            if len(joke) > 20 and len(joke) < 500:  # Розумна довжина
                # Додаємо емодзі
                if not any(emoji in joke for emoji in ['😂', '🤣', '😄', '🧠', '🔥']):
                    joke += f" {EMOJI['brain']}"
                cleaned_jokes.append(joke)
        
        return cleaned_jokes[:5]  # Максимум 5 жартів
    
    def _parse_captions_response(self, response: str) -> List[str]:
        """Парсинг відповіді з підписами"""
        captions = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('Підписи:', 'Підпис')):
                # Видаляємо нумерацію
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    line = line[2:].strip()
                
                if 10 <= len(line) <= 100:  # Підходяща довжина
                    captions.append(line)
        
        return captions[:5]
    
    def _parse_appropriateness_response(self, response: str) -> Dict[str, any]:
        """Парсинг відповіді про відповідність контенту"""
        lines = response.strip().split('\n')
        result = {"appropriate": True, "reason": "", "suggestion": ""}
        
        for line in lines:
            line = line.strip()
            if line.startswith('ПІДХОДИТЬ:'):
                appropriate_text = line.split(':', 1)[1].strip().lower()
                result["appropriate"] = appropriate_text in ['так', 'yes', 'true']
            elif line.startswith('ПРИЧИНА:'):
                result["reason"] = line.split(':', 1)[1].strip()
            elif line.startswith('ПРОПОЗИЦІЯ:'):
                result["suggestion"] = line.split(':', 1)[1].strip()
        
        return result

# Глобальний екземпляр генератора
content_generator = ContentGenerator()

# Допоміжні функції

async def auto_generate_content_if_needed():
    """Автоматична генерація контенту при нестачі"""
    try:
        from database.database import get_db_session, submit_content
        from database.models import Content, ContentStatus, ContentType
        
        with get_db_session() as session:
            # Перевіряємо кількість схваленого контенту
            approved_jokes = session.query(Content).filter(
                Content.content_type == ContentType.JOKE,
                Content.status == ContentStatus.APPROVED
            ).count()
            
            # Якщо мало анекдотів, генеруємо нові
            if approved_jokes < 10:
                logger.info("🤖 Генеруємо нові анекдоти через AI...")
                
                new_jokes = await content_generator.generate_jokes(5, "загальний")
                
                for joke in new_jokes:
                    await submit_content(
                        user_id=settings.ADMIN_ID,
                        content_type=ContentType.JOKE,
                        text=joke
                    )
                    
                    # Автоматично схвалюємо AI контент
                    from database.database import moderate_content
                    content = session.query(Content).order_by(Content.id.desc()).first()
                    if content:
                        await moderate_content(
                            content.id,
                            settings.ADMIN_ID,
                            True,
                            "Автоматично схвалено AI"
                        )
                
                logger.info(f"✨ Додано {len(new_jokes)} AI анекдотів")
        
    except Exception as e:
        logger.error(f"Помилка автогенерації контенту: {e}")

async def generate_content_for_theme(theme: str, count: int = 3) -> List[str]:
    """Генерація контенту на конкретну тему"""
    return await content_generator.generate_jokes(count, theme)