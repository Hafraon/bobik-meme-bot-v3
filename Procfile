# 🚢 PROCFILE ДЛЯ RAILWAY DEPLOYMENT - ВИПРАВЛЕНИЙ 🚢

# ===== ОСНОВНИЙ ПРОЦЕС =====
# ✅ ВИПРАВЛЕНО: Правильний запуск через main.py з app/
web: python main.py

# ===== АЛЬТЕРНАТИВНІ ВАРІАНТИ ЗАПУСКУ =====

# Якщо main.py в корені проекту:
# web: python main.py

# Через Python модуль:
# web: python -m app.main

# З додатковими параметрами:
# web: python main.py --production

# З логуванням:
# web: python main.py 2>&1 | tee bot.log

# ===== ДОДАТКОВІ ПРОЦЕСИ (ОПЦІОНАЛЬНО) =====

# Worker процес для фонових завдань:
# worker: cd app && python worker.py

# Веб-сервер для webhook режиму:
# webhook: cd app && python webhook_server.py

# Моніторинг процес:
# monitor: cd app && python monitor.py

# Backup процес:
# backup: cd app && python backup.py

# ===== КОМЕНТАРІ ДЛЯ RAILWAY =====

# 🚀 RAILWAY АВТОМАТИЧНО:
# - Встановлює залежності з requirements.txt
# - Запускає процес 'web' за замовчуванням
# - Надає PORT через змінну середовища
# - Автоматично перезапускає при крашах

# 🔧 ЗМІННІ СЕРЕДОВИЩА RAILWAY:
# BOT_TOKEN - токен Telegram бота
# ADMIN_ID - ID адміністратора
# DATABASE_URL - URL PostgreSQL бази даних
# PORT - порт для веб-сервера (надається автоматично)

# 📊 ЛОГУВАННЯ RAILWAY:
# Всі print() та logging виводи автоматично потрапляють в Railway логи
# Доступні через Railway dashboard -> Deployments -> Logs

# ⚡ АВТОМАТИЧНЕ SCALING:
# Railway автоматично скейлить процеси за навантаженням
# Можна налаштувати ліміти ресурсів в dashboard

# 🛡️ HEALTH CHECKS:
# Railway автоматично перевіряє здоров'я процесів
# Перезапускає при помилках або зависанні

# 💾 PERSISTENT STORAGE:
# За замовчуванням файлова система НЕ персистентна
# Використовуйте PostgreSQL для збереження даних
# Або Railway Volume для файлів

# 🌐 NETWORKING:
# Процес 'web' автоматично отримує публічний URL
# Інші процеси доступні тільки внутрішньо

# ===== TROUBLESHOOTING =====

# Якщо процес не запускається:
# 1. Перевірте що main.py існує в app/
# 2. Перевірте що всі залежності в requirements.txt
# 3. Перевірте логи Railway для детальної помилки
# 4. Переконайтеся що BOT_TOKEN встановлений

# Якщо процес крашиться:
# 1. Перевірте логи Railway
# 2. Додайте більше логування в код
# 3. Перевірте змінні середовища
# 4. Тестуйте локально перед deployment

# Якщо бот не відповідає:
# 1. Перевірте що BOT_TOKEN правильний
# 2. Перевірте що бот запущений в Railway логах
# 3. Перевірте що webhook НЕ активний в BotFather
# 4. Тестуйте з /start командою

# ===== DEPLOYMENT КОМАНДИ =====

# Для deploy на Railway:
# git add .
# git commit -m "Update bot"
# git push

# Для rollback:
# railway rollback

# Для перегляду логів:
# railway logs

# Для налаштування змінних:
# railway variables

# ===== ПРИКЛАД СТРУКТУРИ ПРОЕКТУ =====

# project-root/
# ├── Procfile                 ← цей файл
# ├── requirements.txt         ← залежності Python
# ├── app/                     ← основна папка з кодом
# │   ├── main.py             ← головний файл бота
# │   ├── config/             ← конфігурація
# │   ├── database/           ← моделі БД
# │   ├── handlers/           ← обробники команд
# │   └── services/           ← сервіси автоматизації
# └── README.md               ← документація

# ===== РЕСУРСИ RAILWAY =====

# Free Plan:
# - 500 часів виконання/місяць
# - 512MB RAM
# - 1GB disk
# - Публічні репозиторії

# Pro Plan ($5/місяць):
# - Unlimited часи виконання
# - 8GB RAM
# - 100GB disk  
# - Приватні репозиторії
# - Priority support