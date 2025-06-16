# 🧠😂🔥 Україномовний Telegram-бот - Інструкції розгортання

## 🚀 Швидкий запуск на Railway

### 1. Підготовка проекту

```bash
# Діагностика модулів
python3 check_modules.py

# Автоматичне розгортання
./deploy.sh
```

### 2. Налаштування на Railway

1. **Зайдіть на [Railway](https://railway.app)**
2. **Підключіть GitHub репозиторій**
3. **Додайте PostgreSQL сервіс**
4. **Налаштуйте змінні середовища:**

```env
BOT_TOKEN=7882259321:AAGGqql6LD6bzLHTOb1HdKUYs2IJBZqsd6E
ADMIN_ID=603047391
CHANNEL_ID=1002889574159
DATABASE_URL=postgresql://postgres:***@postgres.railway.internal:5432/railway
OPENAI_API_KEY=sk-proj-***
ENVIRONMENT=production
LOG_LEVEL=INFO
TIMEZONE=Europe/Kiev
PORT=8000
```

### 3. Перевірка роботи

Після deploy перевірте:
- ✅ Бот відповідає на `/start`
- ✅ База даних створена
- ✅ Логи без помилок

## 🔧 Локальна розробка

### Встановлення

```bash
# Клонування
git clone YOUR_REPO_URL
cd ukrainian-telegram-bot

# Віртуальне середовище
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# або venv\Scripts\activate  # Windows

# Залежності
pip install -r requirements.txt

# Налаштування
cp .env.example .env
nano .env
```

### Запуск

```bash
# Діагностика
python3 check_modules.py

# Запуск бота
python3 main.py
```

## 📊 Функції бота

### Користувацькі команди
- `/start` - запуск та головне меню
- `/meme` - випадковий мем
- `/anekdot` - український анекдот  
- `/submit` - надіслати свій жарт
- `/profile` - профіль користувача
- `/top` - таблиця лідерів
- `/duel` - дуель жартів
- `/daily` - щоденна розсилка
- `/help` - довідка

### Адміністративні команди
- `/admin_stats` - статистика бота
- `/moderate` - модерація контенту
- `/pending` - контент на розгляді
- `/approve_ID` - схвалити контент
- `/reject_ID` - відхилити контент

## 🎮 Гейміфікація

### Система балів
- **+5** - реакція на контент
- **+10** - подача жарту
- **+20** - схвалення жарту
- **+50** - ТОП жарт тижня
- **+15** - перемога в дуелі

### Ранги
1. 🤡 Новачок (0+ балів)
2. 😄 Сміхун (50+ балів)
3. 😂 Гуморист (150+ балів)
4. 🎭 Комік (350+ балів)
5. 👑 Мастер Рофлу (750+ балів)
6. 🏆 Король Гумору (1500+ балів)
7. 🌟 Легенда Мемів (3000+ балів)
8. 🚀 Гумористичний Геній (5000+ балів)

## 🛠️ Архітектура

```
ukrainian-telegram-bot/
├── main.py                 # Точка входу
├── config/
│   └── settings.py         # Налаштування
├── database/
│   ├── models.py           # Моделі БД  
│   └── database.py         # Робота з БД
├── handlers/
│   ├── __init__.py         # Реєстрація
│   ├── basic_commands.py   # /start, /help
│   ├── content_handlers.py # /meme, /anekdot, /submit
│   ├── gamification_handlers.py # /profile, /top, /duel
│   └── moderation_handlers.py   # /moderate, /approve
├── middlewares/
│   └── auth.py             # Аутентифікація
├── services/
│   ├── scheduler.py        # Щоденна розсилка
│   └── content_generator.py # AI генерація
└── requirements.txt        # Залежності
```

## 🔄 Робочий процес

### Додавання нової функції

1. **Створіть хендлер** в `handlers/`
2. **Додайте до `__init__.py`** реєстрацію
3. **Оновіть БД** якщо потрібно
4. **Протестуйте локально**
5. **Зробіть deploy:**

```bash
git add .
git commit -m "Додано нову функцію"
git push origin main
```

### Модерація контенту

1. **Користувач** надсилає `/submit Мій жарт`
2. **Бот** додає до черги модерації
3. **Адмін** отримує сповіщення
4. **Адмін** використовує `/approve_ID` або `/reject_ID`
5. **Користувач** отримує результат

### Дуелі жартів

1. **Користувач** запускає `/duel`
2. **Надсилає** свій жарт
3. **Система** підбирає опонента
4. **5 хвилин** голосування
5. **Переможець** отримує +15 балів

## 📈 Моніторинг

### Логи
- `logs/bot.log` - загальні логи
- Railway Dashboard - системні логи

### Статистика
- `/admin_stats` - статистика адміністратора
- Railway Metrics - використання ресурсів

## 🐛 Діагностика проблем

### Бот не відповідає
```bash
# Перевірка модулів
python3 check_modules.py

# Перевірка налаштувань
python3 -c "from config.settings import settings; print(f'Адмін: {settings.ADMIN_ID}')"
```

### Помилки БД
```bash
# Перевірка підключення
python3 -c "from database.database import get_db_session; print('БД OK')"
```

### Помилки AI
```bash
# Перевірка OpenAI
python3 -c "from services.content_generator import content_generator; print('AI OK')"
```

## 📞 Підтримка

- **GitHub Issues** - повідомлення про баги
- **Телеграм** - @your_username
- **Email** - your-email@example.com

---

**🇺🇦 Зроблено з ❤️ для української мем-спільноти! 🧠😂🔥**