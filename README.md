# 🧠😂🔥 Україномовний Telegram-бот

> Повнофункціональний бот з мемами, анекдотами, гейміфікацією, модерацією та можливістю монетизації

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.4+-green.svg)](https://aiogram.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)

## 📋 Зміст

- [🚀 Швидкий старт](#-швидкий-старт)
- [✨ Функції](#-функції)
- [🔧 Встановлення](#-встановлення)
- [🌐 Розгортання](#-розгортання)
- [📊 API та команди](#-api-та-команди)
- [🎮 Гейміфікація](#-гейміфікація)
- [🛠️ Адміністрування](#️-адміністрування)
- [📈 Моніторинг](#-моніторинг)

## 🚀 Швидкий старт

### 1. Створення бота

1. Відкрийте [@BotFather](https://t.me/BotFather) у Telegram
2. Створіть нового бота командою `/newbot`
3. Дайте йому ім'я та username
4. Збережіть отриманий токен

### 2. Клонування та налаштування

```bash
# Клонування репозиторію
git clone https://github.com/yourusername/ukrainian-telegram-bot.git
cd ukrainian-telegram-bot

# Встановлення залежностей
pip install -r requirements.txt

# Копіювання конфігурації
cp .env.example .env

# Редагування конфігурації
nano .env
```

### 3. Мінімальна конфігурація .env

```bash
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
DATABASE_URL=sqlite:///ukrainian_bot.db
```

### 4. Запуск

```bash
python main.py
```

## ✨ Функції

### 🎭 Контент
- **📱 /start** - вітання та головне меню
- **😂 /meme** - випадковий мем з базі
- **🧠 /anekdot** - український анекдот
- **📝 /submit** - подача власного контенту
- **📅 /daily** - щоденна розсилка
- **❓ /help** - довідка по командах

### 🎮 Гейміфікація
- **👤 /profile** - профіль користувача
- **🏆 /top** - таблиця лідерів
- **⚔️ /duel** - дуель жартів
- **⭐ Система рангів** - від "Новачок" до "Геній"
- **🔥 Бали за активність** - за всі дії в боті

### 🛡️ Модерація
- **✅ /approve_ID** - схвалення контенту
- **❌ /reject_ID** - відхилення контенту
- **📊 /admin_stats** - статистика для адміна
- **🔍 /moderate** - інтерфейс модерації

### 🤖 AI Можливості
- **Автогенерація** анекдотів при нестачі
- **Покращення** користувацьких жартів
- **Перевірка** відповідності контенту
- **Щоденна мотивація** через ChatGPT

## 🔧 Встановлення

### Системні вимоги

- Python 3.9+
- SQLite (для розвитку) або PostgreSQL (для production)
- 512MB RAM мінімум
- Інтернет-з'єднання

### Крок за кроком

```bash
# 1. Створення віртуального середовища
python -m venv venv

# Активація (Linux/Mac)
source venv/bin/activate

# Активація (Windows)
venv\Scripts\activate

# 2. Встановлення залежностей
pip install -r requirements.txt

# 3. Ініціалізація бази даних
python -c "from database.database import init_db; import asyncio; asyncio.run(init_db())"

# 4. Запуск в режимі розробки
python main.py
```

### Docker (опціонально)

```bash
# Збірка образу
docker build -t ukrainian-bot .

# Запуск контейнера
docker run -d \
  --name ukrainian-bot \
  -e BOT_TOKEN=your_token \
  -e ADMIN_ID=your_id \
  ukrainian-bot
```

## 🌐 Розгортання

### Railway (рекомендовано)

1. **Підготовка коду**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Розгортання на Railway**
   - Зайдіть на [railway.app](https://railway.app)
   - Підключіть GitHub репозиторій
   - Додайте змінні середовища:
     ```
     BOT_TOKEN=your_bot_token
     ADMIN_ID=your_telegram_id
     DATABASE_URL=postgresql://... (автоматично)
     ```

3. **Налаштування домену (опціонально)**
   - Додайте custom domain в Railway
   - Налаштуйте webhook для кращої продуктивності

### Heroku

```bash
# Встановлення Heroku CLI
heroku create your-bot-name

# Додавання PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Налаштування змінних
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_ID=your_id

# Деплой
git push heroku main
```

### VPS/Dedicated Server

```bash
# Оновлення системи
sudo apt update && sudo apt upgrade -y

# Встановлення Python та PostgreSQL
sudo apt install python3 python3-pip postgresql nginx

# Клонування та налаштування
git clone https://your-repo.git
cd ukrainian-telegram-bot
pip3 install -r requirements.txt

# Створення systemd сервісу
sudo nano /etc/systemd/system/ukrainian-bot.service
```

## 📊 API та команди

### Користувацькі команди

| Команда | Опис | Приклад |
|---------|------|---------|
| `/start` | Запуск бота | `/start` |
| `/meme` | Випадковий мем | `/meme` |
| `/anekdot` | Український анекдот | `/anekdot` |
| `/submit TEXT` | Надіслати анекдот | `/submit Чому програмісти...` |
| `/submit` + фото | Надіслати мем | Прикріпити картинку |
| `/profile` | Мій профіль | `/profile` |
| `/top` | Таблиця лідерів | `/top` |
| `/duel` | Почати дуель | `/duel` |
| `/daily` | Увімкнути розсилку | `/daily` |
| `/help` | Довідка | `/help` |

### Адміністративні команди

| Команда | Опис | Доступ |
|---------|------|--------|
| `/admin_stats` | Статистика бота | Тільки адмін |
| `/moderate` | Модерація контенту | Тільки адмін |
| `/approve_123` | Схвалити контент #123 | Тільки адмін |
| `/reject_123` | Відхилити контент #123 | Тільки адмін |
| `/pending` | Список на модерації | Тільки адмін |
| `/stats` | Загальна статистика | Всі |

## 🎮 Гейміфікація

### 🏆 Система балів

| Дія | Бали | Умови |
|-----|------|-------|
| Реакція на контент | +5 | Лайк/дизлайк |
| Подача контенту | +10 | За кожну заявку |
| Схвалення контенту | +20 | Модератор схвалив |
| ТОП контент | +50 | Попав до ТОПу тижня |
| Перемога в дуелі | +15 | Виграв голосування |
| Щоденна активність | +2 | За користування |

### 🎭 Ранги користувачів

| Ранг | Необхідно балів | Особливості |
|------|----------------|-------------|
| 🤡 Новачок | 0+ | Базовий функціонал |
| 😄 Сміхун | 50+ | Додаткові емодзі |
| 😂 Гуморист | 150+ | Пріоритет у дуелях |
| 🎭 Комік | 350+ | Автосхвалення контенту |
| 👑 Мастер Рофлу | 750+ | Модераторські права |
| 🏆 Король Гумору | 1500+ | Створення тем дуелей |
| 🌟 Легенда Мемів | 3000+ | Преміум функції |
| 🚀 Гумористичний Геній | 5000+ | Всі можливості |

### ⚔️ Дуелі жартів

```
1. Ініціатор створює дуель зі своїм жартом
2. Система підбирає опонента (випадковий жарт)
3. Користувачі голосують протягом 5 хвилин
4. Переможець отримує +15 балів
5. Всі учасники голосування отримують +2 бали
```

## 🛠️ Адміністрування

### Модерація контенту

1. **Автоматичне сповіщення** при новому контенті
2. **Швидкі команди** схвалення/відхилення
3. **Інтерфейс модерації** через `/moderate`
4. **Статистика** та аналітика

### Управління користувачами

```python
# Через базу даних
from database.database import get_db_session
from database.models import User

with get_db_session() as session:
    # Пошук користувача
    user = session.query(User).filter(User.id == 123456).first()
    
    # Зміна балів
    user.points += 100
    session.commit()
```

### Backup та відновлення

```bash
# Створення backup
python scripts/backup.py create

# Відновлення з backup
python scripts/backup.py restore backup_file.zip

# Автоматичний backup (через cron)
0 2 * * * /path/to/python scripts/backup.py create
```

## 📈 Моніторинг

### Логування

Бот веде детальні логи:
- **bot.log** - основні події
- **errors.log** - тільки помилки
- **admin.log** - дії адміністраторів

### Метрики

При увімкненні `ENABLE_METRICS=True`:
- Кількість активних користувачів
- Швидкість обробки команд
- Статистика контенту
- Помилки та винятки

### Здоров'я системи

```bash
# Перевірка статусу
curl http://your-bot-url/health

# Відповідь
{
  "status": "healthy",
  "uptime": "2 days, 3 hours",
  "users": 1234,
  "messages_today": 5678
}
```

## 🔧 Розробка

### Структура проекту

```
ukrainian-telegram-bot/
├── main.py                 # Точка входу
├── config/
│   └── settings.py         # Конфігурація
├── database/
│   ├── models.py           # Моделі БД
│   └── database.py         # Робота з БД
├── handlers/
│   ├── __init__.py         # Реєстрація
│   ├── basic_commands.py   # Основні команди
│   ├── content_handlers.py # Контент
│   ├── gamification_handlers.py # Гейміфікація
│   ├── moderation_handlers.py   # Модерація
│   └── duel_handlers.py    # Дуелі
├── middlewares/
│   └── auth.py             # Аутентифікація
├── services/
│   ├── scheduler.py        # Планувальник
│   └── content_generator.py # AI генерація
├── requirements.txt        # Залежності
├── .env.example           # Приклад конфігурації
└── README.md              # Документація
```

### Додавання нових функцій

1. **Нова команда**
   ```python
   # handlers/new_handler.py
   async def cmd_new_feature(message: Message):
       await message.answer("Нова функція!")
   
   # handlers/__init__.py
   def register_handlers(dp: Dispatcher):
       dp.message.register(cmd_new_feature, Command("new"))
   ```

2. **Нова модель БД**
   ```python
   # database/models.py
   class NewModel(Base):
       __tablename__ = "new_table"
       id = Column(Integer, primary_key=True)
       # інші поля...
   ```

3. **Новий планувальник**
   ```python
   # services/scheduler.py
   self.scheduler.add_job(
       self.new_task,
       CronTrigger(hour=12),
       id='new_task'
   )
   ```

## 🤝 Внесок у розвиток

1. **Fork** репозиторію
2. **Створіть** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** змін (`git commit -m 'Add amazing feature'`)
4. **Push** до branch (`git push origin feature/amazing-feature`)
5. **Створіть** Pull Request

### Стиль коду

- Використовуйте **type hints**
- Дотримуйтесь **PEP 8**
- Додавайте **docstrings**
- Пишіть **тести** для нових функцій

## 📄 Ліцензія

Цей проект ліцензовано під MIT License - дивіться [LICENSE](LICENSE) для деталей.

## 🙏 Подяки

- [aiogram](https://aiogram.dev) - чудова бібліотека для Telegram
- [SQLAlchemy](https://sqlalchemy.org) - потужна ORM
- [Railway](https://railway.app) - зручний хостинг
- Українська спільнота розробників

## 📞 Підтримка

- **Issues**: [GitHub Issues](https://github.com/yourusername/ukrainian-telegram-bot/issues)
- **Телеграм**: [@your_username](https://t.me/your_username)
- **Email**: your-email@example.com

---

**🇺🇦 Зроблено з ❤️ для української мем-спільноти!**