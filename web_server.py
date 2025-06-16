#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Веб-сервер для україномовного бота на Railway 🧠😂🔥
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from aiohttp import web, ClientSession
from aiohttp.web import Application, Request, Response
import json

from config.settings import settings, EMOJI

logger = logging.getLogger(__name__)

class BotWebServer:
    """Веб-сервер для бота на Railway"""
    
    def __init__(self, bot_instance=None):
        self.bot = bot_instance
        self.app = None
        self.start_time = datetime.now()
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint для Railway"""
        try:
            uptime = datetime.now() - self.start_time
            uptime_seconds = int(uptime.total_seconds())
            
            # Перевірка стану бота
            bot_status = "unknown"
            bot_info = None
            if self.bot:
                try:
                    me = await self.bot.get_me()
                    bot_status = "healthy"
                    bot_info = {
                        "id": me.id,
                        "username": me.username,
                        "first_name": me.first_name
                    }
                except Exception as e:
                    bot_status = f"unhealthy: {str(e)}"
            
            health_data = {
                "status": "healthy",
                "bot_status": bot_status,
                "bot_info": bot_info,
                "uptime_seconds": uptime_seconds,
                "uptime": str(uptime),
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0",
                "environment": "railway",
                "port": settings.PORT
            }
            
            return web.json_response(health_data, status=200)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return web.json_response({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)
    
    async def bot_info(self, request: Request) -> Response:
        """Інформація про бота"""
        try:
            if not self.bot:
                return web.json_response({
                    "error": "Bot not initialized"
                }, status=503)
            
            me = await self.bot.get_me()
            
            # Статистика з БД (якщо доступна)
            stats = {}
            try:
                from database.database import get_db_session
                from database.models import User, Content
                
                with get_db_session() as session:
                    stats = {
                        "total_users": session.query(User).count(),
                        "total_content": session.query(Content).count()
                    }
            except Exception as e:
                stats = {"db_status": f"unavailable: {str(e)}"}
            
            bot_info = {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "can_join_groups": me.can_join_groups,
                "can_read_all_group_messages": me.can_read_all_group_messages,
                "supports_inline_queries": me.supports_inline_queries,
                "stats": stats,
                "config": {
                    "admin_id": settings.ADMIN_ID,
                    "channel_id": settings.CHANNEL_ID,
                    "database_type": "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite",
                    "ai_enabled": bool(settings.OPENAI_API_KEY)
                }
            }
            
            return web.json_response(bot_info, status=200)
            
        except Exception as e:
            logger.error(f"Bot info error: {e}")
            return web.json_response({
                "error": str(e)
            }, status=500)
    
    async def webhook_handler(self, request: Request) -> Response:
        """Webhook endpoint (для майбутнього використання)"""
        return web.json_response({
            "message": "Webhook not configured, using long polling",
            "method": request.method,
            "timestamp": datetime.now().isoformat()
        }, status=200)
    
    async def metrics(self, request: Request) -> Response:
        """Простий metrics endpoint"""
        try:
            metrics_data = {
                "bot_uptime_seconds": int((datetime.now() - self.start_time).total_seconds()),
                "bot_start_time": self.start_time.isoformat(),
                "environment": "railway",
                "version": "2.0.0",
                "port": settings.PORT,
                "admin_id": settings.ADMIN_ID
            }
            
            # Додавання статистики з БД
            try:
                from database.database import get_db_session
                from database.models import User, Content, ContentStatus
                
                with get_db_session() as session:
                    metrics_data.update({
                        "total_users": session.query(User).count(),
                        "total_content": session.query(Content).count(),
                        "pending_content": session.query(Content).filter_by(status=ContentStatus.PENDING).count()
                    })
            except Exception as e:
                metrics_data["db_error"] = str(e)
            
            return web.json_response(metrics_data)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def root_handler(self, request: Request) -> Response:
        """Головна сторінка"""
        uptime = datetime.now() - self.start_time
        
        # Перевірка стану бота
        bot_status_text = "🤖 Статус бота: Невідомий"
        if self.bot:
            try:
                me = await self.bot.get_me()
                bot_status_text = f"🤖 Бот активний: @{me.username}"
            except:
                bot_status_text = "🤖 Бот: Помилка підключення"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']} Україномовний Telegram-бот</title>
            <style>
                body {{
                    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }}
                .container {{
                    background: rgba(255,255,255,0.15);
                    padding: 40px;
                    border-radius: 20px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    border: 1px solid rgba(255,255,255,0.2);
                    max-width: 600px;
                }}
                h1 {{ 
                    font-size: 3em; 
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                h2 {{
                    font-size: 1.5em;
                    margin-bottom: 30px;
                    opacity: 0.9;
                }}
                .status {{ 
                    margin: 20px 0; 
                    font-size: 1.1em;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 15px;
                    text-align: left;
                }}
                .endpoints {{ 
                    margin-top: 30px; 
                    text-align: left;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 15px;
                }}
                .endpoint {{ 
                    background: rgba(255,255,255,0.1); 
                    padding: 12px; 
                    margin: 8px 0; 
                    border-radius: 10px;
                    border-left: 4px solid #FFD700;
                }}
                a {{ 
                    color: #FFD700; 
                    text-decoration: none;
                    font-weight: bold;
                }}
                a:hover {{ 
                    text-decoration: underline;
                    color: #FFF;
                }}
                .footer {{
                    margin-top: 30px;
                    opacity: 0.8;
                    font-size: 0.9em;
                }}
                .status-indicator {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    background: #00ff00;
                    border-radius: 50%;
                    margin-right: 8px;
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{EMOJI['brain']}{EMOJI['laugh']}{EMOJI['fire']}</h1>
                <h2>Україномовний Telegram-бот</h2>
                
                <div class="status">
                    <div><span class="status-indicator"></span><strong>{EMOJI['rocket']} Статус:</strong> Активний</div>
                    <div><strong>{EMOJI['calendar']} Запущено:</strong> {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
                    <div><strong>{EMOJI['fire']} Час роботи:</strong> {str(uptime).split('.')[0]}</div>
                    <div><strong>{EMOJI['settings']} Порт:</strong> {settings.PORT}</div>
                    <div>{bot_status_text}</div>
                </div>
                
                <div class="endpoints">
                    <h3>{EMOJI['settings']} API Endpoints:</h3>
                    <div class="endpoint">
                        <strong>GET <a href="/health">/health</a></strong> - Перевірка здоров'я системи
                    </div>
                    <div class="endpoint">
                        <strong>GET <a href="/bot">/bot</a></strong> - Інформація про Telegram бота
                    </div>
                    <div class="endpoint">
                        <strong>GET <a href="/metrics">/metrics</a></strong> - Метрики та статистика
                    </div>
                    <div class="endpoint">
                        <strong>POST /webhook</strong> - Webhook endpoint (не активний)
                    </div>
                </div>
                
                <div class="footer">
                    <p>{EMOJI['heart']} Зроблено з любов'ю для української мем-спільноти</p>
                    <p>{EMOJI['rocket']} Працює на Railway • Version 2.0.0</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return web.Response(text=html_content, content_type='text/html')
    
    def create_app(self) -> Application:
        """Створення aiohttp додатка"""
        app = web.Application()
        
        # Маршрути
        app.router.add_get('/', self.root_handler)
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/bot', self.bot_info)
        app.router.add_get('/metrics', self.metrics)
        app.router.add_post('/webhook', self.webhook_handler)
        app.router.add_get('/webhook', self.webhook_handler)  # Для GET запитів теж
        
        # CORS middleware для API
        async def cors_handler(request, handler):
            try:
                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            except Exception as e:
                logger.error(f"CORS handler error: {e}")
                return web.json_response({"error": str(e)}, status=500)
        
        app.middlewares.append(cors_handler)
        
        self.app = app
        return app
    
    async def start_server(self):
        """Запуск веб-сервера"""
        try:
            app = self.create_app()
            
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', settings.PORT)
            await site.start()
            
            logger.info(f"{EMOJI['rocket']} Веб-сервер запущено на порту {settings.PORT}")
            logger.info(f"{EMOJI['fire']} Health check: http://0.0.0.0:{settings.PORT}/health")
            logger.info(f"{EMOJI['brain']} Bot info: http://0.0.0.0:{settings.PORT}/bot")
            
            return runner
            
        except Exception as e:
            logger.error(f"Помилка запуску веб-сервера: {e}")
            raise

async def run_web_server_only():
    """Запуск тільки веб-сервера (для тестування)"""
    server = BotWebServer()
    runner = await server.start_server()
    
    try:
        logger.info(f"{EMOJI['fire']} Веб-сервер працює. Ctrl+C для зупинки.")
        # Тримаємо сервер активним
        while True:
            await asyncio.sleep(3600)  # 1 година
    except KeyboardInterrupt:
        logger.info(f"{EMOJI['hand']} Зупинка веб-сервера...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Запуск тільки веб-сервера для тестування
    asyncio.run(run_web_server_only())