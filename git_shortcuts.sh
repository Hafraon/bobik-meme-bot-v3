#!/bin/bash
# 🧠😂🔥 Git команди та shortcuts для деплою модернізації 🧠😂🔥

# ===== БАЗОВІ GIT КОМАНДИ =====

# Перевірка поточного стану
echo "📊 Поточний стан Git:"
git status --short
git log --oneline -5

echo ""
echo "🔧 Доступні команди:"
echo ""

# ===== ФУНКЦІЯ 1: ШВИДКИЙ COMMIT =====
quick_commit() {
    echo "🚀 Швидкий commit всіх змін..."
    
    git add .
    
    # Автоматичний commit message з датою
    COMMIT_MSG="🚀 Модернізація адмін-панелі $(date +'%Y-%m-%d %H:%M')

✅ Виправлено SQLAlchemy detached objects  
✅ Реалізовано всі 6 stub функцій
✅ Додано безпечне форматування HTML
✅ Створена централізована архітектура БД

Нові файли:
- database/services.py (централізовані сервіси)
- utils/formatters.py (безпечне форматування) 
- services/admin_services.py (розширені функції)
- handlers/admin_panel_handlers.py (повністю переписаний)

Функції:
👥 Управління користувачами
📝 Аналітика контенту  
🔥 Трендовий контент
⚙️ Налаштування бота
🚀 Масові дії
💾 Резервне копіювання"

    git commit -m "$COMMIT_MSG"
    echo "✅ Commit створено"
}

# ===== ФУНКЦІЯ 2: PUSH TO GITHUB =====
push_to_github() {
    echo "📤 Відправка до GitHub..."
    
    # Отримати поточну гілку
    BRANCH=$(git branch --show-current)
    echo "📋 Гілка: $BRANCH"
    
    # Push
    git push origin $BRANCH
    
    if [ $? -eq 0 ]; then
        echo "✅ Успішно відправлено до GitHub!"
        echo "🌐 https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[\/:]//; s/.git$//')"
    else
        echo "❌ Помилка при відправці до GitHub"
        return 1
    fi
}

# ===== ФУНКЦІЯ 3: RAILWAY DEPLOY =====
railway_deploy() {
    echo "🚂 Деплой на Railway..."
    
    # Перевірка чи встановлений Railway CLI
    if ! command -v railway &> /dev/null; then
        echo "⚠️ Railway CLI не знайдено. Встановлюю..."
        npm install -g @railway/cli || {
            echo "❌ Не вдалося встановити Railway CLI"
            echo "Встановіть вручну: https://railway.app/cli"
            return 1
        }
    fi
    
    # Перевірка авторизації
    if ! railway whoami &> /dev/null; then
        echo "🔐 Потрібна авторизація..."
        railway login
    fi
    
    # Перевірка підключення проекту
    if ! railway status &> /dev/null; then
        echo "🔗 Підключення проекту..."
        railway link
    fi
    
    # Деплой
    echo "🚀 Починаю деплой..."
    railway up
    
    if [ $? -eq 0 ]; then
        echo "✅ Деплой завершено успішно!"
        
        # Показати статус та логи
        echo ""
        echo "📊 Статус:"
        railway status
        
        echo ""
        echo "📋 Останні логи:"
        railway logs --tail 10
        
        # URL додатку
        echo ""
        echo "🌐 URL додатку:"
        railway domain 2>/dev/null || echo "Немає публічного домену"
        
    else
        echo "❌ Помилка деплою"
        return 1
    fi
}

# ===== ФУНКЦІЯ 4: ПОВНИЙ ДЕПЛОЙ =====
full_deploy() {
    echo "🎯 ПОВНИЙ ДЕПЛОЙ: Git + Railway"
    echo ""
    
    # Commit
    quick_commit
    if [ $? -ne 0 ]; then
        echo "❌ Помилка commit"
        return 1
    fi
    
    echo ""
    
    # Push to GitHub  
    push_to_github
    if [ $? -ne 0 ]; then
        echo "❌ Помилка push до GitHub"
        return 1
    fi
    
    echo ""
    
    # Railway deploy
    railway_deploy
    if [ $? -ne 0 ]; then
        echo "❌ Помилка Railway деплою"
        return 1
    fi
    
    echo ""
    echo "🎉 ПОВНИЙ ДЕПЛОЙ ЗАВЕРШЕНО УСПІШНО!"
}

# ===== ФУНКЦІЯ 5: ROLLBACK =====
rollback() {
    echo "🔄 Rollback до попередньої версії..."
    
    # Показати останні коміти
    echo "📋 Останні коміти:"
    git log --oneline -10
    
    echo ""
    read -p "Введіть hash коміту для rollback (або Enter для HEAD~1): " COMMIT_HASH
    
    if [ -z "$COMMIT_HASH" ]; then
        COMMIT_HASH="HEAD~1"
    fi
    
    # Rollback
    git checkout $COMMIT_HASH
    
    # Новий коміт з rollback
    git checkout -b rollback-$(date +%Y%m%d-%H%M%S)
    git add .
    git commit -m "🔄 Rollback до $COMMIT_HASH

Причина: відкат через проблеми після модернізації
Дата: $(date +'%Y-%m-%d %H:%M:%S')"
    
    # Push rollback
    ROLLBACK_BRANCH=$(git branch --show-current)
    git push origin $ROLLBACK_BRANCH
    
    echo "✅ Rollback завершено"
    echo "📋 Нова гілка: $ROLLBACK_BRANCH"
    
    # Railway deploy rollback
    read -p "Деплоїти rollback на Railway? (y/n): " DEPLOY_ROLLBACK
    if [ "$DEPLOY_ROLLBACK" = "y" ]; then
        railway_deploy
    fi
}

# ===== ФУНКЦІЯ 6: ПЕРЕВІРКА СТАНУ =====
check_status() {
    echo "🔍 ПЕРЕВІРКА СТАНУ ПРОЕКТУ"
    echo ""
    
    # Git статус
    echo "📊 Git статус:"
    git status --short
    
    # Останні коміти
    echo ""
    echo "📋 Останні коміти:"
    git log --oneline -5
    
    # Railway статус
    echo ""
    echo "🚂 Railway статус:"
    if command -v railway &> /dev/null; then
        if railway whoami &> /dev/null; then
            railway status 2>/dev/null || echo "⚠️ Проект не підключений"
        else
            echo "⚠️ Не авторизовані в Railway"
        fi
    else
        echo "⚠️ Railway CLI не встановлено"
    fi
    
    # Перевірка структури файлів
    echo ""
    echo "📁 Структура файлів модернізації:"
    
    FILES=(
        "database/services.py"
        "utils/formatters.py"
        "utils/__init__.py" 
        "services/admin_services.py"
        "handlers/admin_panel_handlers.py"
    )
    
    for file in "${FILES[@]}"; do
        if [ -f "$file" ]; then
            SIZE=$(wc -l < "$file")
            echo "✅ $file ($SIZE рядків)"
        else
            echo "❌ $file - НЕ ЗНАЙДЕНО"
        fi
    done
    
    # Перевірка імпортів
    echo ""
    echo "🧪 Тестування імпортів:"
    python3 -c "
try:
    from database.services import DatabaseService
    print('✅ database.services')
except Exception as e:
    print(f'❌ database.services: {e}')

try:
    from utils.formatters import SafeFormatter
    print('✅ utils.formatters') 
except Exception as e:
    print(f'❌ utils.formatters: {e}')

try:
    from services.admin_services import BackupService
    print('✅ services.admin_services')
except Exception as e:
    print(f'❌ services.admin_services: {e}')
" 2>/dev/null
}

# ===== ФУНКЦІЯ 7: ЛОГИ ТА МОНІТОРИНГ =====
monitor() {
    echo "📊 МОНІТОРИНГ"
    echo ""
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI не встановлено"
        return 1
    fi
    
    echo "Виберіть дію:"
    echo "1. Переглянути логи"
    echo "2. Моніторинг в реальному часі"
    echo "3. Статус сервісів"
    echo "4. Змінні середовища"
    echo "5. Перезапуск"
    
    read -p "Введіть номер (1-5): " CHOICE
    
    case $CHOICE in
        1)
            echo "📋 Останні логи:"
            railway logs --tail 50
            ;;
        2)
            echo "📊 Моніторинг в реальному часі (Ctrl+C для виходу):"
            railway logs --follow
            ;;
        3)
            echo "📊 Статус сервісів:"
            railway status
            ;;
        4)
            echo "🔧 Змінні середовища:"
            railway variables
            ;;
        5)
            echo "🔄 Перезапуск..."
            railway restart
            ;;
        *)
            echo "❌ Невірний вибір"
            ;;
    esac
}

# ===== МЕНЮ =====
show_menu() {
    echo ""
    echo "🛠️ ===== GIT & RAILWAY SHORTCUTS ====="
    echo ""
    echo "1. 🚀 Швидкий commit"
    echo "2. 📤 Push до GitHub"  
    echo "3. 🚂 Railway deploy"
    echo "4. 🎯 Повний деплой (все разом)"
    echo "5. 🔄 Rollback"
    echo "6. 🔍 Перевірка стану"
    echo "7. 📊 Моніторинг"
    echo "8. ❌ Вихід"
    echo ""
    echo "======================================"
    echo ""
}

# ===== ОСНОВНЕ МЕНЮ =====
main() {
    while true; do
        show_menu
        read -p "Оберіть дію (1-8): " CHOICE
        
        case $CHOICE in
            1)
                quick_commit
                ;;
            2)
                push_to_github
                ;;
            3)
                railway_deploy
                ;;
            4)
                full_deploy
                ;;
            5)
                rollback
                ;;
            6)
                check_status
                ;;
            7)
                monitor
                ;;
            8)
                echo "👋 До побачення!"
                exit 0
                ;;
            *)
                echo "❌ Невірний вибір. Спробуйте ще раз."
                ;;
        esac
        
        echo ""
        read -p "⏎ Натисніть Enter для продовження..."
    done
}

# ===== ШВИДКІ КОМАНДИ ДЛЯ BASH ALIAS =====
create_aliases() {
    echo "🔧 Створення bash aliases..."
    
    ALIASES='
# 🧠😂🔥 Україномовний бот shortcuts
alias bot-status="git status && railway status"
alias bot-logs="railway logs --tail 20"
alias bot-deploy="git add . && git commit -m \"Quick update $(date)\" && git push && railway up"
alias bot-restart="railway restart"
alias bot-monitor="railway logs --follow"
alias bot-rollback="git checkout HEAD~1 && git push origin main && railway up"
'
    
    echo "$ALIASES" >> ~/.bashrc
    echo "✅ Aliases додані до ~/.bashrc"
    echo ""
    echo "Перезавантажте термінал або виконайте: source ~/.bashrc"
    echo ""
    echo "Доступні команди:"
    echo "• bot-status   - статус Git та Railway"
    echo "• bot-logs     - останні логи"  
    echo "• bot-deploy   - швидкий деплой"
    echo "• bot-restart  - перезапуск"
    echo "• bot-monitor  - моніторинг логів"
    echo "• bot-rollback - швидкий rollback"
}

# ===== ЗАПУСК =====

# Перевірка аргументів командного рядка
case "${1:-}" in
    "commit")
        quick_commit
        ;;
    "push")
        push_to_github
        ;;
    "deploy")
        railway_deploy
        ;;
    "full")
        full_deploy
        ;;
    "rollback")
        rollback
        ;;
    "status")
        check_status
        ;;
    "monitor")
        monitor
        ;;
    "aliases")
        create_aliases
        ;;
    "help"|"-h"|"--help")
        echo "🧠😂🔥 Git Shortcuts для україномовного бота"
        echo ""
        echo "Використання:"
        echo "  $0                    - інтерактивне меню"
        echo "  $0 commit            - швидкий commit"
        echo "  $0 push              - push до GitHub"
        echo "  $0 deploy            - Railway deploy"
        echo "  $0 full              - повний деплой"
        echo "  $0 rollback          - rollback змін"
        echo "  $0 status            - перевірка стану"
        echo "  $0 monitor           - моніторинг логів"
        echo "  $0 aliases           - створити bash aliases"
        echo ""
        ;;
    *)
        # Якщо немає аргументів - показати меню
        main
        ;;
esac