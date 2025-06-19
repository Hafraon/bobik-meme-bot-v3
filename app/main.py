#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
?????? �������� ������ �������������� TELEGRAM-���� ??????

������������: ukrainian-telegram-bot/app/main.py
������ �����: ukrainian-telegram-bot/main.py

��ղ�������:
? �������� ��������� � app/
? �������� ������� � ��������� �������
? �������� ����������� ��� ����������
? ��������� ������� �������
? Graceful shutdown
? Railway-��������
"""

import asyncio
import logging
import sys
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional
import traceback

# ������������ ��������� ��� app/ ������
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # ���� ����� � development (�� �� Railway)
        *([] if os.getenv('RAILWAY_ENVIRONMENT') else [
            logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'bot.log', encoding='utf-8')
        ])
    ]
)

logger = logging.getLogger(__name__)

# Aiogram imports � �������� �������
try:
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.exceptions import TelegramNetworkError, TelegramBadRequest
    AIOGRAM_AVAILABLE = True
except ImportError as e:
    logger.error(f"? ������� ������� aiogram: {e}")
    logger.error("?? ���������: pip install aiogram>=3.4.0")
    AIOGRAM_AVAILABLE = False

class UkrainianTelegramBot:
    """?? ����������� ���� ������������� Telegram-����"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.scheduler_service = None
        self.is_running = False
        self.startup_time = datetime.now()
        self.health_server = None
        
        # ������� ������� ��� ���������� ����������
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """������� ������� ����������"""
        logger.info(f"?? �������� ������ {signum}")
        self.is_running = False
    
    def print_banner(self):
        """�������� ����� �������"""
        print("\n" + "??????" * 20)
        print("?? �����Ѳ���� ������������� TELEGRAM-��� v2.0 ??")
        print("???? ���������� ���Ѳ� � PROPER ASYNC/AWAIT ????")
        print("??????" * 20 + "\n")
    
    def load_settings(self) -> dict:
        """������������ ����������� � �������� ������� ��� app/ ���������"""
        try:
            # ������ ������� � �������� ������
            from config.settings import settings
            return {
                'bot_token': settings.BOT_TOKEN,
                'admin_id': settings.ADMIN_ID,
                'database_url': getattr(settings, 'DATABASE_URL', 'sqlite:///bot.db'),
                'debug': getattr(settings, 'DEBUG', False),
                'timezone': getattr(settings, 'TIMEZONE', 'Europe/Kiev')
            }
        except ImportError:
            logger.warning("?? �� ������� ����������� config.settings � app/, ������������ env")
            return {
                'bot_token': os.getenv('BOT_TOKEN'),
                'admin_id': int(os.getenv('ADMIN_ID', 0)),
                'database_url': os.getenv('DATABASE_URL', 'sqlite:///ukrainian_bot.db'),
                'debug': os.getenv('DEBUG', 'False').lower() == 'true',
                'timezone': os.getenv('TIMEZONE', 'Europe/Kiev')
            }
    
    def validate_settings(self, settings: dict) -> bool:
        """�������� �����������"""
        if not settings.get('bot_token'):
            logger.error("? BOT_TOKEN �� �����������!")
            return False
        
        if not settings.get('admin_id'):
            logger.error("? ADMIN_ID �� �����������!")
            return False
        
        logger.info("? ������������ �����")
        return True
    
    async def init_database(self) -> bool:
        """�������� ����������� �� � ����������� app/ ���������"""
        try:
            # ������ ������� � app/database
            from database import init_db
            await init_db()
            logger.info("? ���� ����� ������������")
            return True
        except ImportError:
            logger.warning("?? ������ database ����������� � app/, ������ ��� ��")
            return True
        except Exception as e:
            logger.error(f"? ������� ����������� ��: {e}")
            return False
    
    async def create_bot(self, settings: dict) -> bool:
        """��������� ����"""
        try:
            if not AIOGRAM_AVAILABLE:
                logger.error("? aiogram �����������")
                return False
            
            self.bot = Bot(
                token=settings['bot_token'],
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML
                )
            )
            
            self.dp = Dispatcher()
            
            # ���� �'�������
            bot_info = await self.bot.get_me()
            logger.info(f"? ��� ��������: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"? ������� ��������� ����: {e}")
            return False
    
    async def setup_dispatcher(self) -> bool:
        """������������ ����������"""
        try:
            # ��������� ������� ������
            from aiogram.filters import Command
            from aiogram.types import Message
            
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message):
                await message.answer("?????? ��� ������ � ��������� �����!")
            
            @self.dp.message(Command("status"))
            async def cmd_status(message: Message):
                uptime = datetime.now() - self.startup_time
                await message.answer(f"? ������: ������\n? ��� ������: {uptime}")
            
            # ������ ��������� ��� �������� � app/handlers
            try:
                from handlers import register_all_handlers
                register_all_handlers(self.dp)
                logger.info("? �� �������� ������������ � app/handlers")
            except ImportError:
                logger.warning("?? app/handlers ���������, ������ � �������� ���������")
            except Exception as e:
                logger.warning(f"?? ������� ��������� ��������: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"? ������� ������������ ����������: {e}")
            return False
    
    async def setup_scheduler(self, settings: dict):
        """������������ ������������� � app/services"""
        try:
            from services.scheduler import SchedulerService
            self.scheduler_service = SchedulerService(self.bot)
            await self.scheduler_service.start()
            logger.info("? ������������ �������� � app/services")
        except ImportError:
            logger.warning("?? app/services/scheduler �����������")
        except Exception as e:
            logger.error(f"? ������� �������������: {e}")
    
    async def startup_checks(self, settings: dict):
        """�������� ��� �������"""
        try:
            # ����������� ������������ ��� ������
            if settings.get('admin_id') and self.bot:
                await self.bot.send_message(
                    settings['admin_id'],
                    "? <b>��� ��ϲ��� ��������</b>\n\n"
                    f"?? ��� �������: {self.startup_time.strftime('%H:%M:%S')}\n"
                    f"?? �����: 2.0 (����������)\n"
                    f"?? ����������: {'Production' if os.getenv('RAILWAY_ENVIRONMENT') else 'Development'}"
                )
        except Exception as e:
            logger.warning(f"?? �� ������� �������� ����������� �����: {e}")
    
    async def run_bot(self):
        """������ ��������� ����� ����"""
        try:
            self.is_running = True
            logger.info("?? ������� polling...")
            
            await self.dp.start_polling(
                self.bot,
                skip_updates=True,
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            
        except Exception as e:
            logger.error(f"? ������� polling: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """�������� ���������� ������"""
        try:
            logger.info("?? ������� ��������� ����������...")
            
            # ����������� ������������
            if self.bot:
                try:
                    from config.settings import settings
                    uptime = datetime.now() - self.startup_time
                    shutdown_message = (
                        "?? <b>��� ��������</b>\n\n"
                        f"? ��� ������: {uptime}\n"
                        f"?? ������: �������� ����������"
                    )
                    await self.bot.send_message(settings.ADMIN_ID, shutdown_message)
                except ImportError:
                    logger.warning("?? �� ������� ����������� ������������ ��� ����������� �����")
                except Exception:
                    pass
            
            # ������� �������������
            if self.scheduler_service:
                await self.scheduler_service.stop()
                logger.info("? ������������ ��������")
            
            # �������� ��� ����
            if self.bot:
                await self.bot.session.close()
                logger.info("?? ���� ���� �������")
            
            uptime = datetime.now() - self.startup_time
            logger.info(f"?? ��� ������: {uptime}")
            logger.info("?? ��� �������� ��������")
            
        except Exception as e:
            logger.error(f"? ������� ��� ���������: {e}")
    
    async def main(self):
        """?? ���������� ������� ������� �������"""
        self.print_banner()
        
        try:
            # ���� 1: ������������ �����������
            logger.info("?? ?? ������������ �����������...")
            settings = self.load_settings()
            
            if not self.validate_settings(settings):
                logger.error("? ������� �������� �����������")
                return False
            
            # ���� 2: ����������� ��
            logger.info("?? ?? ����������� ��...")
            if not await self.init_database():
                logger.error("? �������� ������� ��")
                return False
            
            # ���� 3: ��������� ����
            logger.info("?? ?? ��������� ����...")
            if not await self.create_bot(settings):
                logger.error("? �� ������� �������� ����")
                return False
            
            # ���� 4: ������������ ����������
            logger.info("?? ?? ������������ ����������...")
            if not await self.setup_dispatcher():
                logger.error("? ������� ������������ ����������")
                return False
            
            # ���� 5: ������������
            logger.info("?? ?? ������������ �������������...")
            await self.setup_scheduler(settings)
            
            # ���� 6: �������� ��� �������
            logger.info("?? ?? �������� ��� �������...")
            await self.startup_checks(settings)
            
            # ���� 7: ������
            logger.info("?? ?? ������ ����...")
            await self.run_bot()
            
            return True
            
        except Exception as e:
            logger.error(f"?? �������� �������: {e}")
            logger.error(traceback.format_exc())
            return False

async def main():
    """?? ���������� ����� ����� � ��������"""
    bot = UkrainianTelegramBot()
    
    try:
        result = await bot.main()
        return result
    except KeyboardInterrupt:
        logger.info("?? ������� ����� Ctrl+C")
        return True
    except Exception as e:
        logger.error(f"?? ����������� �������: {e}")
        logger.error(traceback.format_exc())
        return False

# ����� ����� ��� ����������� �������
def sync_main():
    """��������� �������� ��� main()"""
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("?? ������� ����� Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.error(f"?? ����������� �������: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_main()