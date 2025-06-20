# 🧠😂🔥 ПРОФЕСІЙНИЙ УКРАЇНОМОВНИЙ TELEGRAM БОТ

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.4+-green.svg)](https://aiogram.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Railway](https://img.shields.io/badge/Railway-Deployed-purple.svg)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Повнофункціональний україномовний Telegram бот з автоматизацією, дуелями, гейміфікацією та професійною архітектурою.**

## 🎯 ОГЛЯД

Цей проект представляє професійного україномовного Telegram бота з повною автоматизацією та широким функціоналом для розваг, спілкування та гейміфікації.

### ✨ Ключові особливості

- 🇺🇦 **100% українською мовою** - повна локалізація
- 🤖 **Повна автоматизація** - 9 автоматичних завдань
- ⚔️ **Дуелі жартів** - змагання між користувачами
- 🎮 **Гейміфікація** - система балів, рангів та досягнень
- 🛡️ **Модерація контенту** - професійна система перевірки
- 📊 **Детальна аналітика** - статистика та метрики
- 🐳 **Docker готовність** - легке розгортання
- 🚀 **Railway сумісність** - готово до production

---

## 📋 ЗМІСТ

- [🚀 Швидкий старт](#-швидкий-старт)
- [⚙️ Встановлення](#️-встановлення)
- [🎮 Функціональність](#-функціональність)
- [🏗️ Архітектура](#️-архітектура)
- [🐳 Docker розгортання](#-docker-розгортання)
- [📊 Моніторинг](#-моніторинг)
- [🔧 Налаштування](#-налаштування)
- [📖 API документація](#-api-документація)
- [🤝 Внесок у проект](#-внесок-у-проект)

---

## 🚀 ШВИДКИЙ СТАРТ

### Варіант 1: Railway (Рекомендується)

1. **Клонуйте репозиторій:**
   ```bash
   git clone https://github.com/your-username/ukrainian-telegram-bot.git
   cd ukrainian-telegram-bot
   ```

2. **Налаштуйте змінні середовища в Railway:**
   ```
   BOT_TOKEN=your_bot_token_from_botfather
   ADMIN_ID=your_telegram_user_id
   ```

3. **Deploy на Railway:**
   ```bash
   git add .
   git commit -m "Initial deploy"
   git push
   ```

### Варіант 2: Docker (Локально)

1. **Створіть .env файл:**
   ```bash
   cp .env.example .env
   # Відредагуйте .env з вашими налаштуваннями
   ```

2. **Запустіть через Docker Compose:**
   ```bash
   docker-compose up -d
   ```

### Варіант 3: Звичайний Python

1. **Встановіть залежності:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Запустіть бота:**
   ```bash
   cd app && python main.py
   ```

---

## ⚙️ ВСТАНОВЛЕННЯ

### 📋 Вимоги

- **Python 3.11+**
- **PostgreSQL 15+** (опціонально)
- **Redis** (для кешування, опціонально)
- **Docker & Docker Compose** (для контейнеризації)

### 🔧 Детальне встановлення

#### 1. Підготовка середовища

```bash
# Клонування репозиторію
git clone https://github.com/your-username/ukrainian-telegram-bot.git
cd ukrainian-telegram-bot

# Створення віртуального середовища
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows

# Встановлення залежностей
pip install -r requirements.txt
```

#### 2. Налаштування бота

1. **Створіть бота через [@BotFather](https://t.me/BotFather):**
   - Відправте `/newbot`
   - Виберіть ім'я та username
   - Збережіть отриманий токен

2. **Отримайте ваш Telegram ID:**
   - Напишіть [@userinfobot](https://t.me/userinfobot)
   - Збережіть ваш User ID

#### 3. Конфігурація

Створіть файл `.env`:

```env
# ===== ОСНОВНІ НАЛАШТУВАННЯ =====
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=YourBot_bot
ADMIN_ID=your_telegram_user_id

# ===== БАЗА ДАНИХ =====
DATABASE_URL=postgresql://username:password@localhost:5432/bot_db
# або для SQLite (development)
# DATABASE_URL=sqlite:///data/bot.db

# ===== ДОДАТКОВІ НАЛАШТУВАННЯ =====
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# ===== АВТОМАТИЗАЦІЯ =====
AUTOMATION_ENABLED=true
MORNING_BROADCAST_HOUR=9
EVENING_STATS_HOUR=20

# ===== БЕЗПЕКА =====
RATE_LIMITING_ENABLED=true
MAX_MESSAGES_PER_MINUTE=10
```

#### 4. Ініціалізація бази даних

```bash
# Автоматична ініціалізація при першому запуску
cd app && python main.py

# Або ручна ініціалізація
python -c "import asyncio; from database import init_db; asyncio.run(init_db())"
```

---

## 🎮 ФУНКЦІОНАЛЬНІСТЬ

### 🎯 Основні можливості

#### 📝 Система контенту
- **Жарти** - українські гуморні історії
- **Меми** - інтернет гумор та зображення
- **Анекдоти** - класичні українські анекдоти
- **Інтерактивні кнопки** - лайки, дизлайки, поділитися
- **Модерація** - професійна система перевірки

#### ⚔️ Дуелі жартів
- **Змагання** між користувачами
- **Голосування** спільноти
- **Рейтингова система** з 8 рангами
- **Турніри** тижневі та спеціальні
- **Статистика** перемог та поразок

#### 🎮 Гейміфікація
- **Система балів** за активність
- **8 рангів** від Новачка до Легенди
- **Досягнення** за різні активності
- **Щоденні завдання** та виклики
- **Таблиця лідерів** найактивніших

#### 🤖 Автоматизація (9 завдань)
- **09:00** - Ранкова розсилка контенту
- **20:00** - Вечірня статистика
- **П'ятниця 19:00** - Тижневий турнір
- **03:00** - Автоматична очистка даних
- **Кожну хвилину** - Перевірка дуелей
- **Кожні 15 хв** - Нагадування про дуелі
- **1 число** - Місячні підсумки
- **Кожні 30 хв** - Перевірка досягнень
- **Неділя 18:00** - Тижневий дайджест

#### 🛡️ Адміністрування
- **Повна адмін панель** з кнопками
- **Модерація контенту** (схвалення/відхилення)
- **Управління користувачами** (бани, попередження)
- **Статистика в реальному часі**
- **Система розсилок** з rate limiting
- **Резервне копіювання** даних

### 📱 Команди користувача

```
/start - Головне меню та привітання
/help - Довідка по командах
/joke - Випадковий жарт
/meme - Випадковий мем
/anekdot - Випадковий анекдот
/content - Меню вибору контенту
/submit - Подати свій контент
/duel - Почати дуель жартів
/profile - Мій профіль та статистика
/stats - Загальна статистика бота
/leaderboard - Таблиця лідерів
```

### 🛡️ Команди адміністратора

```
/admin - Адмін панель
/moderate - Модерація контенту
/pending - Контент на модерації
/broadcast - Розсилка повідомлень
/users - Управління користувачами
/ban <user_id> - Заблокувати користувача
/unban <user_id> - Розблокувати користувача
/stats_admin - Детальна статистика
/backup - Створити резервну копію
/automation - Статус автоматизації
```

---

## 🏗️ АРХІТЕКТУРА

### 📁 Структура проекту

```
ukrainian-telegram-bot/
├── 📁 app/                          # Основний код програми
│   ├── 📁 config/                   # Конфігурація
│   │   └── settings.py              # Централізовані налаштування
│   ├── 📁 database/                 # База даних
│   │   ├── __init__.py              # Експорт функцій БД
│   │   ├── models.py                # SQLAlchemy моделі
│   │   └── database.py              # Функції БД
│   ├── 📁 handlers/                 # Обробники команд
│   │   ├── __init__.py              # Реєстрація хендлерів
│   │   ├── basic_commands.py        # Основні команди
│   │   ├── content_handlers.py      # Система контенту
│   │   ├── admin_panel_handlers.py  # Адмін панель
│   │   ├── duel_handlers.py         # Дуелі жартів
│   │   ├── moderation_handlers.py   # Модерація
│   │   └── gamification_handlers.py # Гейміфікація
│   ├── 📁 services/                 # Сервіси та автоматизація
│   │   ├── automated_scheduler.py   # Планувальник завдань
│   │   └── broadcast_system.py      # Система розсилок
│   ├── 📁 utils/                    # Утиліти
│   │   └── helpers.py               # Допоміжні функції
│   └── main.py                      # Точка входу програми
├── 📁 scripts/                      # Скрипти обслуговування
│   ├── apply_all_fixes.py           # Автоматичне виправлення
│   └── health_check.sh              # Health check
├── 📁 config/                       # Конфігурація зовнішніх сервісів
│   ├── nginx.conf                   # Nginx конфігурація
│   ├── redis.conf                   # Redis налаштування
│   └── prometheus.yml               # Моніторинг
├── requirements.txt                 # Python залежності
├── Dockerfile                       # Docker образ
├── docker-compose.yml               # Повний стек
├── Procfile                         # Railway конфігурація
└── README.md                        # Документація
```

### 🔧 Технічний стек

- **Backend**: Python 3.11, asyncio
- **Bot Framework**: aiogram 3.4+
- **База даних**: PostgreSQL 15+ / SQLite (fallback)
- **ORM**: SQLAlchemy 2.0+
- **Кеш**: Redis 7+
- **Планувальник**: APScheduler 3.10+
- **Моніторинг**: Prometheus + Grafana
- **Контейнеризація**: Docker + Docker Compose
- **Deployment**: Railway, Docker, VPS

### 🔄 Архітектурні принципи

- **Модульність** - кожен компонент незалежний
- **Асинхронність** - повна підтримка async/await
- **Fallback режим** - робота без БД
- **Горизонтальне масштабування** - готовність до кластеру
- **Graceful degradation** - поступове зниження функціональності
- **12-Factor App** - сумісність з cloud platforms

---

## 🐳 DOCKER РОЗГОРТАННЯ

### 🚀 Швидкий запуск

```bash
# Клонування та запуск
git clone https://github.com/your-username/ukrainian-telegram-bot.git
cd ukrainian-telegram-bot

# Копіювання конфігурації
cp .env.example .env
# Відредагуйте .env файл

# Запуск повного стеку
docker-compose up -d

# Перевірка статусу
docker-compose ps
```

### 🔧 Налаштування компонентів

#### Основний бот
```bash
# Тільки бот + БД + Redis
docker-compose up -d telegram-bot postgres redis

# Перегляд логів
docker-compose logs -f telegram-bot

# Перезапуск бота
docker-compose restart telegram-bot
```

#### База даних
```bash
# Підключення до PostgreSQL
docker-compose exec postgres psql -U bot_user -d ukrainian_bot

# Backup бази даних
docker-compose exec postgres pg_dump -U bot_user ukrainian_bot > backup.sql

# Відновлення з backup
cat backup.sql | docker-compose exec -T postgres psql -U bot_user -d ukrainian_bot
```

#### Моніторинг
```bash
# Перегляд метрик Prometheus
open http://localhost:9091

# Grafana дашборди
open http://localhost:3000
# Логін: admin / Пароль: admin123
```

### 🔒 Production налаштування

Для production використовуйте:

```bash
# Production compose файл
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# З SSL та безпекою
docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.ssl.yml up -d
```

---

## 📊 МОНІТОРИНГ

### 📈 Метрики

Бот збирає детальні метрики:

- **Система**: CPU, RAM, мережа
- **База даних**: З'єднання, запити, час відповіді
- **Бот**: Повідомлення/сек, користувачі, помилки
- **Контент**: Подачі, схвалення, перегляди
- **Дуелі**: Активні, завершені, голоси

### 🔍 Логування

```bash
# Логи бота
docker-compose logs -f telegram-bot

# Логи бази даних
docker-compose logs -f postgres

# Всі логи
docker-compose logs -f

# Пошук помилок
docker-compose logs telegram-bot | grep ERROR
```

### ⚠️ Алерти

Налаштовані алерти для:
- Падіння бота
- Помилки БД
- Високе навантаження
- Заповнення диску
- Аномальна активність

---

## 🔧 НАЛАШТУВАННЯ

### ⚙️ Основні параметри

#### config/settings.py
```python
# Автоматизація
AUTOMATION_ENABLED = True
MORNING_BROADCAST_HOUR = 9
EVENING_STATS_HOUR = 20

# Безпека
RATE_LIMITING_ENABLED = True
MAX_MESSAGES_PER_MINUTE = 10

# Контент
MAX_CONTENT_LENGTH = 2000
MAX_SUBMISSIONS_PER_DAY = 10

# Дуелі
DUEL_DURATION_HOURS = 24
TOURNAMENT_ENABLED = True
```

#### Environment Variables
```env
# Режим роботи
ENVIRONMENT=production  # development, production, testing
DEBUG=false
LOG_LEVEL=INFO

# Автоматизація
AUTOMATION_ENABLED=true
TIMEZONE=Europe/Kiev

# Розсилки
BROADCAST_ENABLED=true
BROADCAST_RATE_LIMIT=30
DAILY_DIGEST_ENABLED=true

# Гейміфікація
POINTS_FOR_SUBMISSION=5
POINTS_FOR_APPROVAL=15
POINTS_FOR_DUEL_WIN=20
```

### 🎨 Кастомізація

#### Додавання нових команд
```python
# handlers/custom_handlers.py
@dp.message(Command("custom"))
async def custom_command(message: Message):
    await message.answer("Кастомна команда!")

# Реєстрація в handlers/__init__.py
from .custom_handlers import register_custom_handlers
register_custom_handlers(dp)
```

#### Нові типи контенту
```python
# config/settings.py
CONTENT_TYPES = ["joke", "meme", "anekdot", "story"]

# database/models.py
# Додайте до enum'у ContentType
```

#### Кастомні досягнення
```python
# Додайте в database.py -> create_default_achievements()
("Новачок-блогер", "Написати 100 постів", "✍️", "content", "posts", 100, 500, None)
```

---

## 📖 API ДОКУМЕНТАЦІЯ

### 🔌 REST API

Бот надає REST API для інтеграцій:

```
GET  /health              - Health check
GET  /stats               - Статистика бота
POST /webhook/{token}     - Telegram webhook
GET  /metrics             - Prometheus метрики
POST /api/content         - Додати контент
GET  /api/leaderboard     - Таблиця лідерів
```

### 📝 Приклади використання

#### Отримання статистики
```bash
curl http://localhost:8000/stats
```

```json
{
  "total_users": 1250,
  "total_content": 3420,
  "active_duels": 15,
  "automation_status": "active",
  "uptime_hours": 168.5
}
```

#### Додавання контенту через API
```bash
curl -X POST http://localhost:8000/api/content \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Новий жарт",
    "type": "joke",
    "author_id": 123456789
  }'
```

### 🔗 Webhook налаштування

Для production з webhook:

```python
# config/settings.py
WEBHOOK_URL = "https://yourdomain.com"
WEBHOOK_PATH = "/webhook/your_bot_token"
```

---

## 🚨 ВИПРАВЛЕННЯ ПРОБЛЕМ

### ❌ Поширені помилки

#### 1. `sqlalchemy-pool` помилка
```bash
# ПРИЧИНА: Неіснуючий пакет в requirements.txt
# РІШЕННЯ: Видаліть рядок sqlalchemy-pool>=1.3.0

# Автоматичне виправлення:
python apply_all_fixes.py
```

#### 2. `name 'List' is not defined`
```bash
# ПРИЧИНА: Відсутні typing імпорти
# РІШЕННЯ: Додайте в файли handlers

from typing import Optional, List, Dict, Any, Union
```

#### 3. `can't adapt type 'ContentStatus'`
```bash
# ПРИЧИНА: PostgreSQL не сумісний з Python enum
# РІШЕННЯ: Використовуйте string замість enum

# В models.py:
status = Column(String(20), default="pending")  # замість SQLEnum
```

#### 4. `AutomatedScheduler takes 2 positional arguments but 3 were given`
```bash
# ПРИЧИНА: Неправильні аргументи ініціалізації
# РІШЕННЯ: Виправте __init__ метод

def __init__(self, bot, db_available: bool = False):  # 2 аргументи
```

### 🛠️ Автоматичне виправлення

```bash
# Запустіть скрипт виправлень
python apply_all_fixes.py

# Або примініть файли з артефактів Claude
# 1. Замініть models.py на виправлену версію
# 2. Замініть database.py на виправлену версію
# 3. Замініть main.py на виправлену версію
# 4. Замініть requirements.txt на виправлену версію
```

### 🔧 Діагностика

```bash
# Перевірка статусу компонентів
python -c "from app.config.settings import *; print('Config OK')"
python -c "from app.database import *; print('Database OK')"
python -c "from app.handlers import *; print('Handlers OK')"

# Тест підключення до БД
python -c "import asyncio; from app.database import init_db; print(asyncio.run(init_db()))"

# Перевірка Docker
docker-compose config
docker-compose ps
```

---

## 🤝 ВНЕСОК У ПРОЕКТ

### 🛠️ Для розробників

```bash
# Форк репозиторію
git clone https://github.com/your-username/ukrainian-telegram-bot.git
cd ukrainian-telegram-bot

# Створення гілки для фічі
git checkout -b feature/new-awesome-feature

# Встановлення development залежностей
pip install -r requirements-dev.txt

# Запуск тестів
pytest tests/

# Лінтинг коду
black app/
flake8 app/
mypy app/

# Commit та Push
git add .
git commit -m "Add awesome new feature"
git push origin feature/new-awesome-feature
```

### 📝 Стайл коду

- **Python**: PEP 8, type hints
- **Docstrings**: Google style
- **Commit messages**: Conventional Commits
- **Мова коментарів**: Українська + English для API

### 🧪 Тестування

```bash
# Запуск всіх тестів
pytest

# Тести з покриттям
pytest --cov=app tests/

# Тести інтеграції
pytest tests/integration/

# Performance тести
pytest tests/performance/ -s
```

### 📋 TODO / Roadmap

- [ ] **Веб інтерфейс** - React админка
- [ ] **Мобільний додаток** - Flutter companion
- [ ] **AI інтеграція** - GPT для генерації жартів
- [ ] **Голосові повідомлення** - TTS/STT підтримка
- [ ] **Multilang підтримка** - інші мови
- [ ] **Blockchain інтеграція** - NFT досягнення
- [ ] **Video контент** - підтримка відео мемів
- [ ] **Live стріми** - інтерактивні трансляції

---

## 📄 ЛІЦЕНЗІЯ

```
MIT License

Copyright (c) 2024 Ukrainian Telegram Bot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 ПІДТРИМКА

### 💬 Контакти

- **Telegram**: [@BobikFun_bot](https://t.me/BobikFun_bot)
- **Email**: support@ukrainianbot.com
- **GitHub Issues**: [Створити issue](https://github.com/your-username/ukrainian-telegram-bot/issues)
- **Telegram канал**: [@UkrainianBotNews](https://t.me/UkrainianBotNews)

### 🆘 Допомога

1. **Перевірте [FAQ](#-виправлення-проблем)**
2. **Шукайте в [Issues](https://github.com/your-username/ukrainian-telegram-bot/issues)**
3. **Створіть новий Issue з детальним описом**
4. **Приєднуйтесь до Telegram чату для швидкої допомоги**

### 💖 Подяки

Особлива подяка всім хто робить внесок у проект:

- **Розробники** - за код та ідеї
- **Тестувальники** - за знаходження багів
- **Користувачі** - за зворотний зв'язок
- **Спільнота** - за підтримку українських проектів

---

## 🎉 ВИСНОВОК

**🧠😂🔥 Професійний україномовний Telegram бот** - це не просто бот, а повноцінна платформа для розваг, спілкування та гейміфікації українською мовою.

### ✨ Чому обрати цей бот?

- ✅ **Професійна архітектура** - готово до enterprise
- ✅ **Повна автоматизація** - мінімум ручної роботи
- ✅ **Масштабованість** - від 100 до 100,000+ користувачів
- ✅ **Відкритий код** - повна прозорість
- ✅ **Українська мова** - підтримка національного контенту
- ✅ **Активний розвиток** - регулярні оновлення

### 🚀 Готові почати?

```bash
git clone https://github.com/your-username/ukrainian-telegram-bot.git
cd ukrainian-telegram-bot
docker-compose up -d
```

**Слава Україні! 🇺🇦**

---

<div align="center">

**📱 [Demo Bot](https://t.me/BobikFun_bot) | 📖 [Документація](https://docs.ukrainianbot.com) | 💬 [Telegram](https://t.me/UkrainianBotChat) | ⭐ [GitHub](https://github.com/your-username/ukrainian-telegram-bot)**

*Зроблено з ❤️ для України*

</div>