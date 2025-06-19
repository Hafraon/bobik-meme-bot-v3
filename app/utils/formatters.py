#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Утиліти для безпечного форматування та обробки помилок 🧠😂🔥
"""

import html
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SafeFormatter:
    """Безпечне форматування даних для Telegram"""
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Екранування HTML символів"""
        if not text:
            return "Невідомо"
        return html.escape(str(text))
    
    @staticmethod
    def format_user_name(first_name: str, username: str = None) -> str:
        """Безпечне форматування імені користувача"""
        name = SafeFormatter.escape_html(first_name or "Невідомий")
        if username:
            return f"{name} (@{SafeFormatter.escape_html(username)})"
        return name
    
    @staticmethod
    def format_number(number: int) -> str:
        """Форматування чисел з розділовими комами"""
        return f"{number:,}".replace(",", " ")
    
    @staticmethod
    def format_percentage(value: float, total: float) -> str:
        """Розрахунок та форматування відсотків"""
        if total == 0:
            return "0%"
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"
    
    @staticmethod
    def format_content_preview(text: str, max_length: int = 100) -> str:
        """Безпечний превью контенту"""
        if not text:
            return "Без тексту"
        
        safe_text = SafeFormatter.escape_html(text)
        if len(safe_text) > max_length:
            return safe_text[:max_length] + "..."
        return safe_text
    
    @staticmethod
    def format_rank_emoji(rank: str) -> str:
        """Емодзі для рангів"""
        rank_emojis = {
            "Новачок": "🤡",
            "Сміхун": "😄", 
            "Гуморист": "😂",
            "Комік": "🎭",
            "Мастер Рофлу": "👑",
            "Король Гумору": "🏆",
            "Легенда Мемів": "🌟",
            "Гумористичний Геній": "🚀"
        }
        return rank_emojis.get(rank, "🤔")
    
    @staticmethod
    def format_date_relative(date: datetime) -> str:
        """Відносне форматування дати"""
        if not date:
            return "Невідомо"
        
        now = datetime.utcnow()
        diff = now - date
        
        if diff.days == 0:
            if diff.seconds < 3600:
                return f"{diff.seconds // 60} хв тому"
            else:
                return f"{diff.seconds // 3600} год тому"
        elif diff.days == 1:
            return "Вчора"
        elif diff.days < 7:
            return f"{diff.days} дн тому"
        else:
            return date.strftime("%d.%m.%Y")

class StatsFormatter:
    """Форматування статистичних даних"""
    
    @staticmethod
    def format_basic_stats(stats: Dict[str, int]) -> str:
        """Форматування базової статистики"""
        return (
            f"👥 Користувачів: {SafeFormatter.format_number(stats.get('total_users', 0))}\n"
            f"📝 Контенту: {SafeFormatter.format_number(stats.get('total_content', 0))}\n"
            f"⏳ На модерації: {SafeFormatter.format_number(stats.get('pending_content', 0))}\n"
            f"✅ Схвалено: {SafeFormatter.format_number(stats.get('approved_content', 0))}\n"
            f"💖 Оцінок сьогодні: {SafeFormatter.format_number(stats.get('today_ratings', 0))}\n"
            f"⚔️ Активних дуелей: {SafeFormatter.format_number(stats.get('active_duels', 0))}"
        )
    
    @staticmethod
    def format_top_users(users: List[Dict[str, Any]], show_count: int = 10) -> str:
        """Форматування топ користувачів"""
        if not users:
            return "Немає даних про користувачів"
        
        text = "🏆 <b>ТОП КОРИСТУВАЧІ:</b>\n\n"
        
        for i, user in enumerate(users[:show_count], 1):
            rank_emoji = SafeFormatter.format_rank_emoji(user.get('rank', ''))
            name = SafeFormatter.escape_html(user.get('name', 'Невідомий'))
            points = SafeFormatter.format_number(user.get('points', 0))
            
            text += f"{i}. {rank_emoji} {name}: {points} балів\n"
        
        return text
    
    @staticmethod
    def format_content_analytics(analytics: Dict[str, Any]) -> str:
        """Форматування аналітики контенту"""
        status_dist = analytics.get('status_distribution', {})
        
        text = "📊 <b>АНАЛІТИКА КОНТЕНТУ:</b>\n\n"
        
        # Розподіл по статусах
        total_content = sum(status_dist.values())
        if total_content > 0:
            text += "📈 <b>Розподіл по статусах:</b>\n"
            for status, count in status_dist.items():
                percentage = SafeFormatter.format_percentage(count, total_content)
                text += f"• {status}: {count} ({percentage})\n"
            text += "\n"
        
        # ТОП контент
        top_content = analytics.get('top_content', [])
        if top_content:
            text += "🔥 <b>Популярний контент:</b>\n"
            for i, content in enumerate(top_content[:5], 1):
                preview = SafeFormatter.format_content_preview(content.get('text', ''), 50)
                views = SafeFormatter.format_number(content.get('views', 0))
                likes = content.get('likes', 0)
                dislikes = content.get('dislikes', 0)
                
                text += f"{i}. {preview}\n"
                text += f"   👀 {views} | 👍 {likes} | 👎 {dislikes}\n\n"
        
        return text
    
    @staticmethod
    def format_trending_content(trending: List[Dict[str, Any]]) -> str:
        """Форматування трендового контенту"""
        if not trending:
            return "🔥 Поки немає трендового контенту"
        
        text = "🔥 <b>ТРЕНДОВИЙ КОНТЕНТ:</b>\n\n"
        
        for i, item in enumerate(trending[:10], 1):
            preview = SafeFormatter.format_content_preview(item.get('text', ''), 80)
            score = SafeFormatter.format_number(item.get('trend_score', 0))
            author = SafeFormatter.escape_html(item.get('author', 'Невідомий'))
            created = item.get('created', 'Невідомо')
            
            text += f"{i}. {preview}\n"
            text += f"   🚀 Трендинг: {score} | Автор: {author} | {created}\n\n"
        
        return text

class ErrorHandler:
    """Безпечна обробка помилок"""
    
    @staticmethod
    def format_error(error: Exception, context: str = "") -> str:
        """Безпечне форматування помилок для користувача"""
        error_text = str(error)
        safe_error = SafeFormatter.escape_html(error_text)
        
        if context:
            return f"❌ Помилка {context}: {safe_error}"
        return f"❌ Помилка: {safe_error}"
    
    @staticmethod
    def log_and_format_error(error: Exception, context: str = "", user_id: int = None) -> str:
        """Логування помилки та повернення безпечного повідомлення"""
        # Логування повної помилки
        log_message = f"Помилка {context}: {error}"
        if user_id:
            log_message += f" (user_id: {user_id})"
        
        logger.error(log_message, exc_info=True)
        
        # Повернення безпечного повідомлення користувачу
        return ErrorHandler.format_error(error, context)

class TableFormatter:
    """Форматування таблиць та списків"""
    
    @staticmethod
    def format_users_table(users_data: Dict[str, Any]) -> str:
        """Форматування таблиці користувачів"""
        users = users_data.get('users', [])
        page = users_data.get('page', 1)
        total_pages = users_data.get('total_pages', 1)
        
        if not users:
            return "👤 Користувачі не знайдені"
        
        text = f"👥 <b>КОРИСТУВАЧІ</b> (сторінка {page}/{total_pages}):\n\n"
        
        for i, user in enumerate(users, 1):
            rank_emoji = SafeFormatter.format_rank_emoji(user.get('rank', ''))
            name = SafeFormatter.escape_html(user.get('name', 'Невідомий'))
            points = SafeFormatter.format_number(user.get('points', 0))
            submissions = user.get('submissions', 0)
            status = "🟢" if user.get('is_active', True) else "🔴"
            
            text += f"{i}. {status} {rank_emoji} {name}\n"
            text += f"   💰 {points} балів | 📝 {submissions} подань\n"
            text += f"   🕐 {user.get('last_activity', 'Невідомо')}\n\n"
        
        return text
    
    @staticmethod
    def format_pending_content(pending: List[Dict[str, Any]]) -> str:
        """Форматування контенту на модерації"""
        if not pending:
            return "✅ Немає контенту на модерації!"
        
        content = pending[0]  # Перший в черзі
        
        text = f"🛡️ <b>МОДЕРАЦІЯ #{content.get('id')}</b>\n\n"
        
        # Автор
        author = SafeFormatter.escape_html(content.get('author_name', 'Невідомий'))
        username = content.get('author_username')
        if username:
            text += f"👤 Автор: {author} (@{SafeFormatter.escape_html(username)})\n"
        else:
            text += f"👤 Автор: {author}\n"
        
        # Тип контенту
        content_type = content.get('type', 'невідомо')
        text += f"📝 Тип: {content_type}\n"
        text += f"🕐 Дата: {content.get('created', 'Невідомо')}\n\n"
        
        # Контент
        if content.get('text'):
            preview = SafeFormatter.format_content_preview(content['text'], 200)
            text += f"💬 Текст:\n{preview}\n\n"
        
        if content.get('file_id'):
            text += "🖼️ Містить медіа-файл\n\n"
        
        return text

class ProgressFormatter:
    """Форматування прогресу та статистики"""
    
    @staticmethod
    def format_progress_bar(current: int, total: int, length: int = 10) -> str:
        """Створення текстового прогрес-бара"""
        if total == 0:
            return "▱" * length
        
        filled = int((current / total) * length)
        return "▰" * filled + "▱" * (length - filled)
    
    @staticmethod
    def format_weekly_activity(activity: List[Dict[str, Any]]) -> str:
        """Форматування тижневої активності"""
        if not activity:
            return "📊 Немає даних за тиждень"
        
        text = "📊 <b>АКТИВНІСТЬ ЗА ТИЖДЕНЬ:</b>\n\n"
        
        max_activity = max(item.get('activity', 0) for item in activity)
        
        for item in activity:
            date = item.get('date', 'Невідомо')
            count = item.get('activity', 0)
            bar = ProgressFormatter.format_progress_bar(count, max_activity, 8)
            
            text += f"{date}: {bar} {count}\n"
        
        return text