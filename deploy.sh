#!/bin/bash
# 🧠😂🔥 Скрипт розгортання україномовного Telegram-бота 🧠😂🔥

echo "🚀 ПОЧИНАЮ РОЗГОРТАННЯ УКРАЇНОМОВНОГО БОТА НА RAILWAY"
echo "🧠😂🔥 =============================================== 🧠😂🔥"

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для виводу кольорових повідомлень
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Перевірка чи встановлений Git
if ! command -v git &> /dev/null; then
    print_error "Git не встановлений!"
    exit 1
fi

print_status "Git знайдено"

# Перевірка чи є зміни для commit
if [ -z "$(git status --porcelain)" ]; then
    print_warning "Немає змін для commit"
else
    print_info "Знайдені зміни. Виконую commit..."
    
    # Додавання всіх файлів
    git add .
    
    # Commit з автоматичним повідомленням
    COMMIT_MSG="🚀 Deploy: $(date '+%Y-%m-%d %H:%M:%S') - Оновлення бота"
    git commit -m "$COMMIT_MSG"
    
    print_status "Commit виконано: $COMMIT_MSG"
fi

# Перевірка remote origin
if ! git remote get-url origin &> /dev/null; then
    print_error "Git remote 'origin' не налаштовано!"
    print_info "Налаштуйте remote: git remote add origin YOUR_REPO_URL"
    exit 1
fi

print_status "Git remote налаштовано"

# Push до GitHub
print_info "Відправляю зміни до GitHub..."
if git push origin main; then
    print_status "Зміни відправлено до GitHub"
else
    # Спробувати з master якщо main не працює
    if git push origin master; then
        print_status "Зміни відправлено до GitHub (master branch)"
    else
        print_error "Не вдалося відправити зміни до GitHub"
        print_info "Перевірте налаштування Git та права доступу"
        exit 1
    fi
fi

# Інформація про Railway
echo ""
print_info "🚂 НАСТУПНІ КРОКИ ДЛЯ RAILWAY:"
echo "1. Зайдіть на https://railway.app"
echo "2. Підключіть GitHub репозиторій"
echo "3. Переконайтеся що змінні середовища налаштовані:"
echo "   - BOT_TOKEN"
echo "   - ADMIN_ID" 
echo "   - DATABASE_URL (автоматично для PostgreSQL)"
echo "   - OPENAI_API_KEY (опціонально)"
echo "4. Railway автоматично виконає deploy"

# Перевірка модулів (якщо є скрипт)
echo ""
if [ -f "check_modules.py" ]; then
    print_info "Запускаю діагностику модулів..."
    python3 check_modules.py
else
    print_warning "Скрипт діагностики не знайдено"
fi

echo ""
print_status "РОЗГОРТАННЯ ЗАВЕРШЕНО!"
print_info "Бот буде доступний на Railway через 2-3 хвилини"
echo "🧠😂🔥 Успіхів з україномовним ботом! 🧠😂🔥"