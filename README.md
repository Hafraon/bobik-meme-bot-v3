# 🧠😂🔥 Професійний Україномовний Telegram-бот

**Повнофункціональна платформа для розваг з елементами гейміфікації, модерації контенту та можливостями монетизації.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.4+-green.svg)](https://docs.aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Особливості

### 🇺🇦 100% Українською мовою
- Всі тексти, команди та інтерфейс
- Контекстні привітання та мотиваційні фрази
- Адаптація під українську аудиторію

### 🎮 Повна гейміфікація
- **8 рангів** від Новачка до Гумористичного Генія
- **Система балів** за всі види активності
- **Профілі користувачів** з детальною статистикою
- **Таблиця лідерів** з різними категоріями
- **Система досягнень** та нагород

### ⚔️ Дуелі жартів
- Змагання між користувачами
- Голосування спільноти
- Турнірна система
- Рейтинги дуелянтів

### 🛡️ Професійна модерація
- Повний цикл перевірки контенту
- Автоматичні та ручні фільтри
- Система скарг та оскаржень
- Детальна статистика модерації

### 📊 Розширена аналітика
- Детальний моніторинг активності
- Prometheus метрики
- Grafana дашборди
- Автоматичні звіти

### 🚀 Production-ready
- Docker контейнеризація
- CI/CD з GitHub Actions
- Автоматичне масштабування
- Система backup та відновлення

## 📋 Зміст

- [Швидкий старт](#-швидкий-старт)
- [Встановлення](#-встановлення)
- [Конфігурація](#-конфігурація)
- [Розгортання](#-розгортання)
- [API документація](#-api)
- [Моніторинг](#-моніторинг)
- [Внесок у проект](#-внесок)

## 🚀 Швидкий старт

### Для Railway (рекомендовано)

1. **Форкните репозиторій**
2. **Підключіть до Railway**
3. **Додайте PostgreSQL сервіс**
4. **Встановіть змінні середовища**:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
DATABASE_URL=postgresql://...
```

5. **Виконайте міграцію БД**:
```bash
python emergency_db_migration.py
```

### Для локальної розробки

```bash
# Клонування
git clone https://github.com/your-username/ukrainian-telegram-bot.git
cd ukrainian-telegram-bot

# Віртуальне середовище
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або venv\Scripts\activate  # Windows

# Встановлення залежностей
pip install -r requirements.txt

# Налаштування
cp .env.example .env
# Редагуйте .env файл

# Міграція БД
python emergency_db_migration.py

# Запуск
python main.py
```

## 📦 Встановлення

### Системні вимоги

- **Python 3.9+**
- **PostgreSQL 12+** (або SQLite для розробки)
- **Redis** (опціонально, для кешування)
- **RAM**: мінімум 512MB, рекомендовано 1GB+
- **Disk**: мінімум 1GB

### Залежності

Основні залежності автоматично встановлюються з `requirements.txt`:

- `aiogram 3.4+` - Telegram Bot framework
- `SQLAlchemy 2.0+` - ORM для роботи з БД
- `psycopg2-binary` - PostgreSQL адаптер
- `APScheduler` - планувальник задач
- `FastAPI` - веб API (опціонально)
- `prometheus-client` - метрики (опціонально)

## ⚙️ Конфігурація

### Обов'язкові змінні

```env
# Основні
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
DATABASE_URL=postgresql://user:password@localhost/dbname

# Опціональні сервіси
OPENAI_API_KEY=sk-...
CHANNEL_ID=-1001234567890
```

### Гейміфікація

```env
POINTS_FOR_VIEW=1
POINTS_FOR_REACTION=5
POINTS_FOR_SUBMISSION=10
POINTS_FOR_APPROVAL=20
POINTS_FOR_DUEL_WIN=15
POINTS_FOR_DAILY_ACTIVITY=2
```

### Щоденна розсилка

```env
DAILY_BROADCAST_HOUR=9
DAILY_BROADCAST_MINUTE=0
TIMEZONE=Europe/Kiev
```

### Дуелі

```env
DUEL_VOTING_TIME=300
MIN_VOTES_FOR_DUEL=3
MAX_ACTIVE_DUELS=10
```

### Повний список налаштувань

Дивіться `config/settings.py` для всіх доступних опцій.

## 🔧 Архітектура

```
ukrainian-telegram-bot/
├── 📁 config/                 # Конфігурація
│   └── settings.py            # Налаштування
├── 📁 database/               # База даних
│   ├── models.py              # SQLAlchemy моделі
│   ├── database.py            # Операції з БД
│   └── __init__.py            # Експорти
├── 📁 handlers/               # Обробники команд
│   ├── basic_commands.py      # /start, /help
│   ├── content_handlers.py    # /meme, /anekdot, /submit
│   ├── gamification_handlers.py # /profile, /top, /duel
│   ├── admin_panel_handlers.py # Адмін функції
│   ├── duel_handlers.py       # Дуелі жартів
│   └── __init__.py            # Реєстрація
├── 📁 middlewares/            # Middleware
│   └── auth.py                # Аутентифікація
├── 📁 services/               # Сервіси
│   └── scheduler.py           # Планувальник
├── 📁 utils/                  # Утиліти
├── 📁 tests/                  # Тести
├── main.py                    # Точка входу
├── emergency_db_migration.py  # Міграція БД
└── requirements.txt           # Залежності
```

## 🎮 Функціональність

### Команди користувачів

| Команда | Опис | Бали |
|---------|------|------|
| `/start` | Головне меню та привітання | - |
| `/meme` | Випадковий мем | +1 |
| `/anekdot` | Український анекдот | +1 |
| `/submit [текст]` | Надіслати жарт на модерацію | +10 |
| `/profile` | Персональний профіль | - |
| `/top` | Таблиця лідерів | - |
| `/duel [текст]` | Створити дуель жартів | +15 за перемогу |
| `/daily` | Підписка на розсилку | +2 щодня |
| `/help` | Повна довідка | - |

### Адміністративні команди

| Команда | Опис |
|---------|------|
| `/admin` | Головна адмін-панель |
| `/stats` | Швидка статистика |
| `/pending` | Контент на модерації |
| `/approve_ID` | Схвалити контент |
| `/reject_ID` | Відхилити контент |

### Система рангів

1. 🤡 **Новачок** (0+ балів)
2. 😄 **Сміхун** (50+ балів)
3. 😂 **Гуморист** (150+ балів)
4. 🎭 **Комік** (350+ балів)
5. 👑 **Мастер Рофлу** (750+ балів)
6. 🏆 **Король Гумору** (1500+ балів)
7. 🌟 **Легенда Мемів** (3000+ балів)
8. 🚀 **Гумористичний Геній** (5000+ балів)

## 🚀 Розгортання

### Railway (рекомендовано)

1. **Створіть акаунт на [Railway](https://railway.app)**
2. **Підключіть GitHub репозиторій**
3. **Додайте PostgreSQL сервіс**
4. **Встановіть змінні середовища**
5. **Deploy відбудеться автоматично**

### Docker

```bash
# Збірка образу
docker build -t ukrainian-bot .

# Запуск з docker-compose
docker-compose up -d

# Або окремо
docker run -d \
  --name ukrainian-bot \
  --env-file .env \
  ukrainian-bot
```

### VPS/Dedicated

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip postgresql nginx

# Клонування проекту
git clone https://repo-url.git /opt/ukrainian-bot
cd /opt/ukrainian-bot

# Віртуальне середовище
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Systemd сервіс
sudo cp scripts/ukrainian-bot.service /etc/systemd/system/
sudo systemctl enable ukrainian-bot
sudo systemctl start ukrainian-bot
```

### Heroku

```bash
# Heroku CLI
heroku create your-bot-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set BOT_TOKEN=your_token
git push heroku main
```

## 📊 Моніторинг

### Prometheus метрики

- `telegram_bot_active_users` - активні користувачі
- `telegram_bot_total_users` - загальна кількість
- `telegram_bot_commands_total` - виконані команди
- `telegram_bot_errors_total` - кількість помилок
- `telegram_bot_pending_content` - контент на модерації

### Логування

```bash
# Реальний час
tail -f logs/bot.log

# Systemd
journalctl -u ukrainian-bot -f

# Docker
docker logs -f ukrainian-bot
```

### Health check

```
GET /health
```

Повертає статус системи та основні метрики.

## 🔧 Адміністрування

### Управління ботом

```bash
# Статистика
python scripts/manage.py stats

# Користувачі
python scripts/manage.py users list
python scripts/manage.py users add_points --user_id 123 --points 100

# Контент
python scripts/manage.py content pending
python scripts/manage.py content approve --content_id 1

# Очищення
python scripts/manage.py cleanup --days 30
```

### Backup

```bash
# Створення
python scripts/backup.py create --type full

# Відновлення
python scripts/backup.py restore backup_file.zip

# Автоматичне очищення
python scripts/backup.py cleanup --keep 7
```

## 🧪 Тестування

```bash
# Запуск всіх тестів
pytest

# З покриттям
pytest --cov=.

# Конкретний модуль
pytest tests/test_handlers.py

# Інтеграційні тести
pytest tests/integration/
```

## 📈 Масштабування

### Горизонтальне масштабування

```yaml
# docker-compose.yml
services:
  bot:
    image: ukrainian-bot
    deploy:
      replicas: 3
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
```

### Оптимізація продуктивності

1. **Включити Redis кешування**
2. **Налаштувати connection pooling**
3. **Оптимізувати запити до БД**
4. **Використовувати CDN для медіа**
5. **Налаштувати rate limiting**

## 🛡️ Безпека

### Рекомендації

- ✅ Використовуйте HTTPS для webhook
- ✅ Налаштуйте rate limiting
- ✅ Регулярно оновлюйте залежності
- ✅ Використовуйте сильні паролі БД
- ✅ Обмежте доступ до адмін функцій
- ✅ Регулярно робіть backup

### Firewall

```bash
# Дозволити тільки необхідні порти
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## 🤝 Внесок у проект

### Як долучитися

1. **Fork репозиторій**
2. **Створіть feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit зміни** (`git commit -m 'Add amazing feature'`)
4. **Push в branch** (`git push origin feature/amazing-feature`)
5. **Відкрийте Pull Request**

### Стандарти коду

```bash
# Форматування
black .
isort .

# Лінтинг
flake8 .
mypy .

# Тести
pytest --cov=.
```

### Guidelines

- Використовуйте типи Python (type hints)
- Пишіть докстрінги для функцій
- Покривайте код тестами
- Слідуйте PEP 8
- Коментуйте складну логіку

## 📝 Ліцензія

Цей проект ліцензований під MIT License - дивіться [LICENSE](LICENSE) файл для деталей.

## 👥 Автори

- **Розробник** - [@yourusername](https://github.com/yourusername)

## 🙏 Подяки

- [aiogram](https://docs.aiogram.dev/) - чудовий Telegram Bot framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - потужна ORM
- [FastAPI](https://fastapi.tiangolo.com/) - сучасний веб framework
- [Railway](https://railway.app/) - зручна платформа деплою

## 📞 Підтримка

- 🐛 **Bug reports**: [GitHub Issues](https://github.com/yourusername/ukrainian-telegram-bot/issues)
- 💡 **Feature requests**: [GitHub Discussions](https://github.com/yourusername/ukrainian-telegram-bot/discussions)
- 💬 **Загальні питання**: [Telegram](https://t.me/yourusername)

## 🔗 Корисні посилання

- [Документація aiogram](https://docs.aiogram.dev/)
- [PostgreSQL документація](https://www.postgresql.org/docs/)
- [Railway документація](https://docs.railway.app/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**🧠😂🔥 Зроблено з ❤️ для української спільноти**