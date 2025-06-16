#!/bin/bash
# 🧠😂🔥 Швидке налаштування змінних середовища для Railway 🧠😂🔥

echo "🚀 НАЛАШТУВАННЯ УКРАЇНОМОВНОГО БОТА НА RAILWAY"
echo "=============================================="

# Перевірка чи встановлено Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI не встановлено"
    echo "📝 Встановіть з: https://docs.railway.app/develop/cli"
    echo "💾 npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI знайдено"

# Логін в Railway
echo "🔑 Логін в Railway..."
railway login

# Підключення до проекту
echo "🔗 Підключення до проекту..."
railway link

# Налаштування змінних середовища
echo ""
echo "📝 НАЛАШТУВАННЯ ЗМІННИХ СЕРЕДОВИЩА"
echo "=================================="

# BOT_TOKEN
read -p "🤖 Введіть BOT_TOKEN від @BotFather: " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN обов'язковий!"
    exit 1
fi
railway variables set BOT_TOKEN="$BOT_TOKEN"
echo "✅ BOT_TOKEN встановлено"

# ADMIN_ID  
read -p "👤 Введіть ваш Telegram ID від @userinfobot: " ADMIN_ID
if [ -z "$ADMIN_ID" ]; then
    echo "❌ ADMIN_ID обов'язковий!"
    exit 1
fi
railway variables set ADMIN_ID="$ADMIN_ID"
echo "✅ ADMIN_ID встановлено"

# CHANNEL_ID (опціонально)
read -p "📺 Введіть ID каналу (або залиште порожнім): " CHANNEL_ID
if [ ! -z "$CHANNEL_ID" ]; then
    railway variables set CHANNEL_ID="$CHANNEL_ID"
    echo "✅ CHANNEL_ID встановлено"
fi

# OPENAI_API_KEY (опціонально)
read -p "🧠 Введіть OpenAI API ключ (або залиште порожнім): " OPENAI_API_KEY
if [ ! -z "$OPENAI_API_KEY" ]; then
    railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
    echo "✅ OPENAI_API_KEY встановлено"
fi

# Додаткові налаштування
railway variables set LOG_LEVEL="INFO"
railway variables set TIMEZONE="Europe/Kiev"
railway variables set DEBUG="False"

echo ""
echo "🎉 НАЛАШТУВАННЯ ЗАВЕРШЕНО!"
echo "========================="
echo "✅ Всі змінні середовища встановлено"
echo "🚀 Запускаємо деплой..."

# Деплой
railway up

echo ""
echo "📊 Перевірити статус: railway status"
echo "📋 Переглянути логи: railway logs"
echo "⚙️ Управління змінними: railway variables"
echo ""
echo "🇺🇦 Слава Україні! Ваш бот готовий до роботи!"