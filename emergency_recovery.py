#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path

def print_header():
    print("=" * 50)
    print("EMERGENCY RECOVERY - Ukrainian Telegram Bot")
    print("=" * 50)

def backup_files():
    print("\n1. Creating backup...")
    
    backup_dir = Path("backup_emergency")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "main.py",
        "app/main.py",
        "requirements.txt",
        "Procfile"
    ]
    
    for file_path in files_to_backup:
        source = Path(file_path)
        if source.exists():
            dest = backup_dir / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            print(f"   Backed up: {file_path}")

def create_clean_files():
    print("\n2. Creating clean files...")
    
    # Clean app/main.py
    app_main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class UkrainianTelegramBot:
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.startup_time = datetime.now()
    
    def load_settings(self):
        return {
            'bot_token': os.getenv('BOT_TOKEN'),
            'admin_id': int(os.getenv('ADMIN_ID', 0)),
            'database_url': os.getenv('DATABASE_URL', 'sqlite:///bot.db'),
            'debug': os.getenv('DEBUG', 'False').lower() == 'true'
        }
    
    def validate_settings(self, settings):
        if not settings.get('bot_token'):
            logger.error("BOT_TOKEN not found!")
            return False
        if not settings.get('admin_id'):
            logger.error("ADMIN_ID not found!")
            return False
        return True
    
    async def create_bot(self, settings):
        try:
            from aiogram import Bot, Dispatcher
            from aiogram.enums import ParseMode
            from aiogram.client.default import DefaultBotProperties
            
            self.bot = Bot(
                token=settings['bot_token'],
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            self.dp = Dispatcher()
            
            bot_info = await self.bot.get_me()
            logger.info(f"Bot created: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"Bot creation error: {e}")
            return False
    
    async def setup_handlers(self):
        try:
            from aiogram.filters import Command
            from aiogram.types import Message
            
            @self.dp.message(Command("start"))
            async def cmd_start(message: Message):
                await message.answer("Bot is working in basic mode!")
            
            @self.dp.message(Command("status"))
            async def cmd_status(message: Message):
                uptime = datetime.now() - self.startup_time
                await message.answer(f"Status: OK\\nUptime: {uptime}")
            
            logger.info("Basic handlers registered")
            return True
            
        except Exception as e:
            logger.error(f"Handlers setup error: {e}")
            return False
    
    async def main(self):
        logger.info("Starting Ukrainian Telegram Bot...")
        
        try:
            settings = self.load_settings()
            
            if not self.validate_settings(settings):
                return False
            
            if not await self.create_bot(settings):
                return False
            
            if not await self.setup_handlers():
                return False
            
            if settings.get('admin_id') and self.bot:
                try:
                    await self.bot.send_message(
                        settings['admin_id'],
                        "Bot started successfully!"
                    )
                except:
                    pass
            
            logger.info("Starting polling...")
            await self.dp.start_polling(self.bot, skip_updates=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Critical error: {e}")
            return False
        finally:
            if self.bot:
                await self.bot.session.close()

async def main():
    bot = UkrainianTelegramBot()
    try:
        result = await bot.main()
        return result
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        return True
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
'''

    # Clean root main.py
    root_main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import logging
from pathlib import Path

app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Ukrainian Telegram Bot...")
    
    try:
        if not app_dir.exists():
            logger.error("app/ directory not found!")
            return await run_minimal_bot()
        
        logger.info("Importing app/main.py...")
        
        try:
            import main as app_main
            
            if hasattr(app_main, 'main'):
                logger.info("Found main() function in app/main.py")
                return await app_main.main()
            elif hasattr(app_main, 'UkrainianTelegramBot'):
                logger.info("Found UkrainianTelegramBot class")
                bot = app_main.UkrainianTelegramBot()
                return await bot.main()
            else:
                logger.warning("No entry point found in app/main.py")
                return await run_minimal_bot()
                
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return await run_minimal_bot()
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return await run_minimal_bot()
            
    except Exception as e:
        logger.error(f"Critical error: {e}")
        return await run_minimal_bot()

async def run_minimal_bot():
    logger.info("Starting minimal bot...")
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from aiogram.filters import Command
        from aiogram.types import Message
        
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.error("BOT_TOKEN not found!")
            return False
        
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        
        @dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer("Minimal bot mode - working!")
        
        @dp.message(Command("status"))
        async def cmd_status(message: Message):
            await message.answer("Status: Minimal mode active")
        
        logger.info("Minimal bot ready")
        await dp.start_polling(bot, skip_updates=True)
        return True
        
    except Exception as e:
        logger.error(f"Minimal bot error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Stopped by Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
'''

    # Create files
    files_to_create = [
        ("app/main.py", app_main_content),
        ("main.py", root_main_content),
        ("Procfile", "web: python main.py"),
        ("requirements.txt", "aiogram>=3.4.0\\naiohttp>=3.9.0\\nasyncpg>=0.29.0\\npython-dotenv>=1.0.0")
    ]
    
    for file_path, content in files_to_create:
        file_obj = Path(file_path)
        file_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_obj, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   Created: {file_path}")

def test_files():
    print("\\n3. Testing files...")
    
    required_files = [
        "main.py",
        "app/main.py", 
        "Procfile",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   OK: {file_path}")
        else:
            print(f"   MISSING: {file_path}")
            all_exist = False
    
    return all_exist

def main():
    print_header()
    
    backup_files()
    create_clean_files()
    
    if test_files():
        print("\\n4. SUCCESS!")
        print("   All files created successfully")
        print("\\nNext steps:")
        print("   1. python main.py           # test locally")
        print("   2. git add .")
        print("   3. git commit -m 'Emergency fix: clean UTF-8 files'")
        print("   4. git push")
        print("\\nBot should now deploy successfully on Railway!")
    else:
        print("\\n4. ERROR!")
        print("   Some files were not created properly")

if __name__ == "__main__":
    main()