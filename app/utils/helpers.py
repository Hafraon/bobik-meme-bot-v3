#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛠️ УТИЛІТИ ТА ПОМІЧНИКИ УКРАЇНСЬКОГО TELEGRAM БОТА 🛠️

Колекція корисних функцій для всього проекту:
✅ Форматування тексту та часу
✅ Валідація даних
✅ Робота з файлами та медіа
✅ Статистичні функції
✅ Безпека та анти-спам
✅ Логування та діагностика
"""

import re
import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union, Tuple
from pathlib import Path
import random
import string

logger = logging.getLogger(__name__)

# ===== КОНСТАНТИ =====

# Українські символи для валідації
UKRAINIAN_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
UKRAINIAN_PATTERN = re.compile(f"[{UKRAINIAN_ALPHABET}{UKRAINIAN_ALPHABET.upper()}\\s\\d.,!?;:()\\-\"'—]+")

# Emoji для різних цілей
EMOJI_SETS = {
    'positive': ['😂', '🤣', '😄', '😊', '😁', '🙂', '🤭', '😃', '😆', '🤩'],
    'fire': ['🔥', '💯', '⚡', '🚀', '🌟', '💥', '✨', '🎯', '💫'],
    'hearts': ['❤️', '💙', '💚', '💛', '🧡', '💜', '🖤', '🤍', '💖'],
    'hands': ['👍', '👎', '👌', '🤝', '🙌', '👏', '💪', '🤘', '✌️'],
    'faces': ['😎', '🤓', '🧐', '🤔', '😏', '😌', '🤗', '🤯', '🤪']
}

# Часові константи
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 86400
SECONDS_IN_WEEK = 604800

# ===== ФОРМАТУВАННЯ ТЕКСТУ =====

def format_number(number: Union[int, float], locale: str = "uk") -> str:
    """
    Форматування чисел для українського локалю
    
    Args:
        number: Число для форматування
        locale: Локаль (uk, en)
    
    Returns:
        Відформатоване число
    """
    if locale == "uk":
        # Українське форматування (пробіли як роздільники тисяч)
        if isinstance(number, float):
            return f"{number:,.2f}".replace(",", " ").replace(".", ",")
        else:
            return f"{number:,}".replace(",", " ")
    else:
        # Англійське форматування
        return f"{number:,}"

def format_duration(seconds: int, short: bool = False) -> str:
    """
    Форматування тривалості часу українською
    
    Args:
        seconds: Кількість секунд
        short: Коротка форма (1г 30хв замість 1 година 30 хвилин)
    
    Returns:
        Відформатована тривалість
    """
    if seconds < 60:
        return f"{seconds} сек" if short else f"{seconds} секунд"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if short:
            return f"{minutes}хв" + (f" {remaining_seconds}с" if remaining_seconds > 0 else "")
        else:
            return f"{minutes} хвилин" + (f" {remaining_seconds} секунд" if remaining_seconds > 0 else "")
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours < 24:
        if short:
            result = f"{hours}г"
            if remaining_minutes > 0:
                result += f" {remaining_minutes}хв"
            return result
        else:
            result = f"{hours} годин"
            if remaining_minutes > 0:
                result += f" {remaining_minutes} хвилин"
            return result
    
    days = hours // 24
    remaining_hours = hours % 24
    
    if short:
        result = f"{days}д"
        if remaining_hours > 0:
            result += f" {remaining_hours}г"
        return result
    else:
        result = f"{days} днів"
        if remaining_hours > 0:
            result += f" {remaining_hours} годин"
        return result

def format_datetime(dt: datetime, format_type: str = "full") -> str:
    """
    Форматування дати та часу українською
    
    Args:
        dt: Об'єкт datetime
        format_type: Тип форматування (full, short, date, time)
    
    Returns:
        Відформатована дата/час
    """
    months_uk = {
        1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
        5: "травня", 6: "червня", 7: "липня", 8: "серпня",
        9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
    }
    
    if format_type == "date":
        return f"{dt.day} {months_uk[dt.month]} {dt.year}"
    elif format_type == "time":
        return f"{dt.hour:02d}:{dt.minute:02d}"
    elif format_type == "short":
        return f"{dt.day}.{dt.month:02d}.{dt.year} {dt.hour:02d}:{dt.minute:02d}"
    else:  # full
        return f"{dt.day} {months_uk[dt.month]} {dt.year} о {dt.hour:02d}:{dt.minute:02d}"

def format_time_ago(dt: datetime) -> str:
    """
    Форматування часу у стилі "X часу тому"
    
    Args:
        dt: Дата/час події
    
    Returns:
        Рядок типу "2 години тому"
    """
    now = datetime.now()
    if dt.tzinfo and not now.tzinfo:
        # Якщо dt має timezone, а now ні - конвертуємо
        now = now.replace(tzinfo=dt.tzinfo)
    elif not dt.tzinfo and now.tzinfo:
        # Або навпаки
        dt = dt.replace(tzinfo=now.tzinfo)
    
    diff = now - dt
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return "щойно"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} хв тому"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} год тому"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} дн тому"
    else:
        weeks = seconds // 604800
        return f"{weeks} тиж тому"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Обрізання тексту з додаванням суфіксу
    
    Args:
        text: Оригінальний текст
        max_length: Максимальна довжина
        suffix: Суфікс для обрізаного тексту
    
    Returns:
        Обрізаний текст
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_text(text: str) -> str:
    """
    Очищення тексту від зайвих символів
    
    Args:
        text: Оригінальний текст
    
    Returns:
        Очищений текст
    """
    # Видалення зайвих пробілів
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Видалення HTML тегів
    text = re.sub(r'<[^>]+>', '', text)
    
    # Видалення спеціальних символів (окрім базових)
    text = re.sub(r'[^\w\s\.,!?\-\'\"():]', '', text)
    
    return text.strip()

# ===== ВАЛІДАЦІЯ ДАНИХ =====

def is_valid_ukrainian_text(text: str, min_length: int = 1) -> bool:
    """
    Перевірка чи текст містить українські символи
    
    Args:
        text: Текст для перевірки
        min_length: Мінімальна довжина
    
    Returns:
        True якщо текст валідний
    """
    if len(text) < min_length:
        return False
    
    # Перевірка наявності українських літер
    ukrainian_letters = sum(1 for char in text.lower() if char in UKRAINIAN_ALPHABET)
    total_letters = sum(1 for char in text if char.isalpha())
    
    if total_letters == 0:
        return False
    
    # Мінімум 30% українських літер
    return (ukrainian_letters / total_letters) >= 0.3

def is_valid_content_length(text: str, min_length: int = 10, max_length: int = 2000) -> Tuple[bool, str]:
    """
    Перевірка довжини контенту
    
    Args:
        text: Текст для перевірки
        min_length: Мінімальна довжина
        max_length: Максимальна довжина
    
    Returns:
        Tuple (валідність, повідомлення про помилку)
    """
    length = len(text.strip())
    
    if length < min_length:
        return False, f"Контент занадто короткий (мінімум {min_length} символів)"
    
    if length > max_length:
        return False, f"Контент занадто довгий (максимум {max_length} символів)"
    
    return True, ""

def contains_profanity(text: str) -> bool:
    """
    Простий фільтр ненормативної лексики
    
    Args:
        text: Текст для перевірки
    
    Returns:
        True якщо знайдено нецензурні слова
    """
    # Базовий список слів (можна розширити)
    profanity_words = [
        # Тут будуть слова для фільтрації
        # Для демо використовуємо загальні patterns
    ]
    
    text_lower = text.lower()
    
    for word in profanity_words:
        if word in text_lower:
            return True
    
    return False

def is_spam_content(text: str, user_history: List[str] = None) -> bool:
    """
    Перевірка на спам
    
    Args:
        text: Текст для перевірки
        user_history: Історія повідомлень користувача
    
    Returns:
        True якщо контент схожий на спам
    """
    # Перевірка на повторення символів
    if re.search(r'(.)\1{5,}', text):  # 6+ однакових символів підряд
        return True
    
    # Перевірка на занадто багато великих літер
    upper_count = sum(1 for char in text if char.isupper())
    if len(text) > 10 and (upper_count / len(text)) > 0.7:
        return True
    
    # Перевірка на повторення в історії
    if user_history:
        for prev_text in user_history[-5:]:  # Останні 5 повідомлень
            if text.lower() == prev_text.lower():
                return True
    
    return False

# ===== СТАТИСТИЧНІ ФУНКЦІЇ =====

def calculate_engagement_rate(views: int, likes: int, dislikes: int = 0, comments: int = 0) -> float:
    """
    Розрахунок рівня залученості
    
    Args:
        views: Кількість переглядів
        likes: Кількість лайків
        dislikes: Кількість дизлайків
        comments: Кількість коментарів
    
    Returns:
        Відсоток залученості
    """
    if views == 0:
        return 0.0
    
    total_interactions = likes + dislikes + comments
    return (total_interactions / views) * 100

def calculate_content_score(likes: int, dislikes: int, views: int, 
                          days_since_posted: int = 1) -> float:
    """
    Розрахунок рейтингу контенту
    
    Args:
        likes: Кількість лайків
        dislikes: Кількість дизлайків
        views: Кількість переглядів
        days_since_posted: Днів з моменту публікації
    
    Returns:
        Рейтинг контенту (0-100)
    """
    if views == 0:
        return 0.0
    
    # Базовий рейтинг на основі лайків/дизлайків
    like_ratio = likes / (likes + dislikes + 1)  # +1 щоб уникнути ділення на 0
    
    # Рейтинг переглядів
    view_score = min(views / 100, 1.0)  # Нормалізація до 1.0
    
    # Штраф за час (старі пости мають менший рейтинг)
    time_penalty = max(0.1, 1.0 - (days_since_posted * 0.1))
    
    # Підсумковий рейтинг
    score = (like_ratio * 0.5 + view_score * 0.3) * time_penalty * 100
    
    return min(score, 100.0)

def get_trending_score(content_data: Dict[str, Any]) -> float:
    """
    Розрахунок трендовості контенту
    
    Args:
        content_data: Дані контенту з метриками
    
    Returns:
        Трендовий рейтинг
    """
    likes = content_data.get('likes', 0)
    views = content_data.get('views', 0)
    shares = content_data.get('shares', 0)
    created_at = content_data.get('created_at', datetime.now())
    
    # Розрахунок часу з моменту створення
    hours_since_posted = (datetime.now() - created_at).total_seconds() / 3600
    
    # Рейтинг активності
    activity_score = (likes * 2 + shares * 3) / max(views, 1)
    
    # Коефіцієнт свіжості (новий контент має перевагу)
    freshness = max(0.1, 1.0 - (hours_since_posted / 24))
    
    return activity_score * freshness * 100

# ===== БЕЗПЕКА ТА АНТИ-СПАМ =====

def generate_content_hash(text: str) -> str:
    """
    Генерація хешу для контенту (для виявлення дублікатів)
    
    Args:
        text: Текст контенту
    
    Returns:
        MD5 хеш тексту
    """
    # Нормалізація тексту перед хешуванням
    normalized = clean_text(text.lower())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def is_rate_limited(user_id: int, action: str, limit: int, window_seconds: int, 
                   storage: Dict[str, List] = None) -> bool:
    """
    Перевірка rate limiting для користувача
    
    Args:
        user_id: ID користувача
        action: Тип дії
        limit: Ліміт дій
        window_seconds: Часове вікно в секундах
        storage: Зовнішнє сховище для зберігання даних
    
    Returns:
        True якщо досягнуто ліміт
    """
    if storage is None:
        storage = {}
    
    key = f"{user_id}_{action}"
    now = datetime.now()
    
    if key not in storage:
        storage[key] = []
    
    # Очищення старих записів
    cutoff_time = now - timedelta(seconds=window_seconds)
    storage[key] = [timestamp for timestamp in storage[key] if timestamp > cutoff_time]
    
    # Перевірка ліміту
    if len(storage[key]) >= limit:
        return True
    
    # Додавання нового запису
    storage[key].append(now)
    return False

def sanitize_user_input(text: str) -> str:
    """
    Санітизація користувацького вводу
    
    Args:
        text: Оригінальний текст
    
    Returns:
        Безпечний текст
    """
    # Видалення потенційно небезпечних символів
    text = re.sub(r'[<>{}]', '', text)
    
    # Обмеження довжини
    text = text[:2000]
    
    # Очищення від зайвих пробілів
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text

# ===== РОБОТА З ФАЙЛАМИ =====

def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """
    Створення директорії якщо вона не існує
    
    Args:
        path: Шлях до директорії
    
    Returns:
        Path об'єкт директорії
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Отримання розміру файлу в МБ
    
    Args:
        file_path: Шлях до файлу
    
    Returns:
        Розмір файлу в МБ
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except FileNotFoundError:
        return 0.0

def save_json_data(data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
    """
    Збереження даних у JSON файл
    
    Args:
        data: Дані для збереження
        file_path: Шлях до файлу
        indent: Відступи для форматування
    
    Returns:
        True якщо успішно збережено
    """
    try:
        ensure_directory_exists(Path(file_path).parent)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, default=str)
        
        return True
    except Exception as e:
        logger.error(f"❌ Error saving JSON: {e}")
        return False

def load_json_data(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Завантаження даних з JSON файлу
    
    Args:
        file_path: Шлях до файлу
        default: Значення за замовчуванням
    
    Returns:
        Завантажені дані або default
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"⚠️ JSON file not found: {file_path}")
        return default
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error: {e}")
        return default

# ===== ГЕНЕРАЦІЯ ВИПАДКОВИХ ДАНИХ =====

def generate_random_emoji(category: str = 'positive') -> str:
    """
    Генерація випадкового emoji з категорії
    
    Args:
        category: Категорія emoji
    
    Returns:
        Випадковий emoji
    """
    emojis = EMOJI_SETS.get(category, EMOJI_SETS['positive'])
    return random.choice(emojis)

def generate_random_string(length: int = 8, include_digits: bool = True) -> str:
    """
    Генерація випадкового рядка
    
    Args:
        length: Довжина рядка
        include_digits: Включати цифри
    
    Returns:
        Випадковий рядок
    """
    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    
    return ''.join(random.choice(chars) for _ in range(length))

def get_random_greeting() -> str:
    """Отримання випадкового привітання українською"""
    greetings = [
        "Вітаю!", "Добрий день!", "Привіт!", "Доброго дня!",
        "Слава Україні!", "Добридень!", "Вітання!", "Здоровенькі були!"
    ]
    return random.choice(greetings)

def get_random_success_message() -> str:
    """Отримання випадкового повідомлення про успіх"""
    messages = [
        "Чудово!", "Відмінно!", "Супер!", "Класно!",
        "Дуже добре!", "Прекрасно!", "Молодець!", "Так тримати!"
    ]
    return random.choice(messages)

# ===== ЛОГУВАННЯ ТА ДІАГНОСТИКА =====

def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None):
    """
    Логування дій користувача
    
    Args:
        user_id: ID користувача
        action: Тип дії
        details: Додаткові деталі
    """
    log_data = {
        'user_id': user_id,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'details': details or {}
    }
    
    logger.info(f"👤 User action: {json.dumps(log_data, ensure_ascii=False)}")

def measure_execution_time(func_name: str):
    """
    Декоратор для вимірювання часу виконання функції
    
    Args:
        func_name: Назва функції для логування
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(f"⏱️ {func_name} executed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"❌ {func_name} failed after {duration:.3f}s: {e}")
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(f"⏱️ {func_name} executed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"❌ {func_name} failed after {duration:.3f}s: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# ===== ЕКСПОРТ =====
__all__ = [
    # Форматування
    'format_number', 'format_duration', 'format_datetime', 'format_time_ago',
    'truncate_text', 'clean_text',
    
    # Валідація
    'is_valid_ukrainian_text', 'is_valid_content_length', 'contains_profanity',
    'is_spam_content',
    
    # Статистика
    'calculate_engagement_rate', 'calculate_content_score', 'get_trending_score',
    
    # Безпека
    'generate_content_hash', 'is_rate_limited', 'sanitize_user_input',
    
    # Файли
    'ensure_directory_exists', 'get_file_size_mb', 'save_json_data', 'load_json_data',
    
    # Випадкові дані
    'generate_random_emoji', 'generate_random_string', 'get_random_greeting',
    'get_random_success_message',
    
    # Логування
    'log_user_action', 'measure_execution_time',
    
    # Константи
    'EMOJI_SETS', 'UKRAINIAN_ALPHABET'
]

logger.info(f"🛠️ Utils helpers завантажено: {len(__all__)} функцій")