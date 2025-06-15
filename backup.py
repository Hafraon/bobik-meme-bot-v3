#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Система резервного копіювання для україномовного бота 🧠😂🔥

Використання:
    python scripts/backup.py create [--type full|db|files] [--output path]
    python scripts/backup.py restore <backup_file> [--force]
    python scripts/backup.py list
    python scripts/backup.py cleanup [--keep 7]
    python scripts/backup.py schedule [--enable|--disable]
"""

import asyncio
import sys
import os
import argparse
import logging
import json
import zipfile
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

# Додавання поточної директорії до PATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings
from database.database import get_db_session

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackupManager:
    """Менеджер резервного копіювання"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Конфігурація backup
        self.config = {
            "database_files": ["*.db", "*.sqlite", "*.sqlite3"],
            "log_files": ["logs/*.log"],
            "config_files": [".env", "config/*.py"],
            "data_files": ["data/*"],
            "exclude_patterns": [
                "__pycache__",
                "*.pyc",
                ".git",
                "venv",
                "node_modules",
                "*.tmp"
            ]
        }
    
    def create_backup(self, backup_type: str = "full", output_path: Optional[str] = None) -> str:
        """Створення резервної копії"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_path:
            backup_file = Path(output_path)
        else:
            backup_file = self.backup_dir / f"backup_{backup_type}_{timestamp}.zip"
        
        backup_file.parent.mkdir(exist_ok=True)
        
        logger.info(f"🔄 Створення backup типу '{backup_type}': {backup_file}")
        
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Метадані backup
                metadata = {
                    "created_at": datetime.now().isoformat(),
                    "backup_type": backup_type,
                    "version": "1.0.0",
                    "settings": {
                        "admin_id": settings.ADMIN_ID,
                        "database_url": settings.DATABASE_URL.split('/')[-1],  # Тільки назва БД
                    }
                }
                
                zip_file.writestr("backup_metadata.json", json.dumps(metadata, indent=2))
                
                if backup_type in ["full", "db"]:
                    self._backup_database(zip_file)
                
                if backup_type in ["full", "files"]:
                    self._backup_files(zip_file)
                
                if backup_type == "full":
                    self._backup_configuration(zip_file)
                    self._backup_logs(zip_file)
            
            logger.info(f"✅ Backup створено: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"❌ Помилка створення backup: {e}")
            if backup_file.exists():
                backup_file.unlink()
            raise
    
    def _backup_database(self, zip_file: zipfile.ZipFile):
        """Резервне копіювання бази даних"""
        logger.info("📊 Backup бази даних...")
        
        try:
            # Експорт даних з БД у JSON
            db_export = self._export_database_to_json()
            zip_file.writestr("database_export.json", json.dumps(db_export, indent=2, ensure_ascii=False))
            
            # Копіювання файлів БД (для SQLite)
            if "sqlite" in settings.DATABASE_URL:
                db_path = settings.DATABASE_URL.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    zip_file.write(db_path, f"database/{os.path.basename(db_path)}")
            
            logger.info("✅ База даних скопійована")
            
        except Exception as e:
            logger.error(f"❌ Помилка backup БД: {e}")
            raise
    
    def _export_database_to_json(self) -> Dict:
        """Експорт БД у JSON формат"""
        from database.models import User, Content, Duel, Rating, AdminAction
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "users": [],
            "content": [],
            "duels": [],
            "ratings": [],
            "admin_actions": []
        }
        
        with get_db_session() as session:
            # Експорт користувачів
            for user in session.query(User).all():
                export_data["users"].append({
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "points": user.points,
                    "rank": user.rank,
                    "daily_subscription": user.daily_subscription,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "jokes_submitted": user.jokes_submitted,
                    "jokes_approved": user.jokes_approved,
                    "memes_submitted": user.memes_submitted,
                    "memes_approved": user.memes_approved
                })
            
            # Експорт контенту
            for content in session.query(Content).all():
                export_data["content"].append({
                    "id": content.id,
                    "content_type": content.content_type.value,
                    "text": content.text,
                    "file_id": content.file_id,
                    "status": content.status.value,
                    "author_id": content.author_id,
                    "views": content.views,
                    "likes": content.likes,
                    "dislikes": content.dislikes,
                    "created_at": content.created_at.isoformat() if content.created_at else None
                })
            
            # Експорт дуелей
            for duel in session.query(Duel).all():
                export_data["duels"].append({
                    "id": duel.id,
                    "initiator_id": duel.initiator_id,
                    "opponent_id": duel.opponent_id,
                    "status": duel.status.value,
                    "initiator_votes": duel.initiator_votes,
                    "opponent_votes": duel.opponent_votes,
                    "created_at": duel.created_at.isoformat() if duel.created_at else None,
                    "completed_at": duel.completed_at.isoformat() if duel.completed_at else None
                })
        
        return export_data
    
    def _backup_files(self, zip_file: zipfile.ZipFile):
        """Резервне копіювання файлів"""
        logger.info("📁 Backup файлів...")
        
        patterns_to_backup = [
            "data/*",
            "logs/*.log",
            "*.json",
            "*.txt"
        ]
        
        import glob
        
        for pattern in patterns_to_backup:
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path) and not self._should_exclude(file_path):
                    zip_file.write(file_path, f"files/{file_path}")
        
        logger.info("✅ Файли скопійовані")
    
    def _backup_configuration(self, zip_file: zipfile.ZipFile):
        """Резервне копіювання конфігурації"""
        logger.info("⚙️ Backup конфігурації...")
        
        config_files = [
            "requirements.txt",
            "railway.toml",
            "docker-compose.yml",
            "Dockerfile",
            ".env.example"
        ]
        
        for file_name in config_files:
            if os.path.exists(file_name):
                zip_file.write(file_name, f"config/{file_name}")
        
        # Конфігурація без секретів
        safe_config = {
            "bot_version": "1.0.0",
            "backup_created": datetime.now().isoformat(),
            "python_version": sys.version,
            "settings": {
                "points_for_reaction": settings.POINTS_FOR_REACTION,
                "points_for_submission": settings.POINTS_FOR_SUBMISSION,
                "points_for_approval": settings.POINTS_FOR_APPROVAL,
                "duel_voting_time": settings.DUEL_VOTING_TIME,
                "max_joke_length": settings.MAX_JOKE_LENGTH
            }
        }
        
        zip_file.writestr("config/bot_settings.json", json.dumps(safe_config, indent=2))
        
        logger.info("✅ Конфігурація скопійована")
    
    def _backup_logs(self, zip_file: zipfile.ZipFile):
        """Резервне копіювання логів"""
        logger.info("📋 Backup логів...")
        
        import glob
        
        log_patterns = ["*.log", "logs/*.log"]
        
        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                if os.path.isfile(log_file):
                    zip_file.write(log_file, f"logs/{os.path.basename(log_file)}")
        
        logger.info("✅ Логи скопійовані")
    
    def _should_exclude(self, file_path: str) -> bool:
        """Перевірка чи потрібно виключити файл"""
        for pattern in self.config["exclude_patterns"]:
            if pattern in file_path:
                return True
        return False
    
    def restore_backup(self, backup_file: str, force: bool = False):
        """Відновлення з резервної копії"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup файл не знайдено: {backup_file}")
        
        logger.info(f"🔄 Відновлення з backup: {backup_file}")
        
        if not force:
            confirm = input("⚠️ Це замінить поточні дані. Продовжити? (y/N): ")
            if confirm.lower() != 'y':
                logger.info("❌ Відновлення скасовано")
                return
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Розпаковка backup
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    zip_file.extractall(temp_dir)
                
                # Читання метаданих
                metadata_file = Path(temp_dir) / "backup_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    logger.info(f"📋 Metadata: {metadata}")
                
                # Відновлення БД
                self._restore_database(temp_dir)
                
                # Відновлення файлів
                self._restore_files(temp_dir)
            
            logger.info("✅ Відновлення завершено")
            
        except Exception as e:
            logger.error(f"❌ Помилка відновлення: {e}")
            raise
    
    def _restore_database(self, temp_dir: str):
        """Відновлення бази даних"""
        logger.info("📊 Відновлення бази даних...")
        
        # Відновлення з JSON експорту
        json_export_file = Path(temp_dir) / "database_export.json"
        if json_export_file.exists():
            with open(json_export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            self._import_database_from_json(export_data)
        
        # Відновлення SQLite файлу
        db_dir = Path(temp_dir) / "database"
        if db_dir.exists():
            for db_file in db_dir.glob("*.db"):
                target_path = Path(db_file.name)
                shutil.copy2(db_file, target_path)
                logger.info(f"📁 Відновлено файл БД: {target_path}")
        
        logger.info("✅ База даних відновлена")
    
    def _import_database_from_json(self, export_data: Dict):
        """Імпорт БД з JSON"""
        from database.models import User, Content, ContentType, ContentStatus
        
        with get_db_session() as session:
            # Очищення існуючих даних (обережно!)
            session.query(User).delete()
            session.query(Content).delete()
            session.commit()
            
            # Відновлення користувачів
            for user_data in export_data.get("users", []):
                user = User(
                    id=user_data["id"],
                    username=user_data.get("username"),
                    first_name=user_data.get("first_name"),
                    points=user_data.get("points", 0),
                    rank=user_data.get("rank", "🤡 Новачок"),
                    daily_subscription=user_data.get("daily_subscription", False),
                    jokes_submitted=user_data.get("jokes_submitted", 0),
                    jokes_approved=user_data.get("jokes_approved", 0),
                    memes_submitted=user_data.get("memes_submitted", 0),
                    memes_approved=user_data.get("memes_approved", 0)
                )
                session.add(user)
            
            # Відновлення контенту
            for content_data in export_data.get("content", []):
                content = Content(
                    id=content_data["id"],
                    content_type=ContentType(content_data["content_type"]),
                    text=content_data.get("text"),
                    file_id=content_data.get("file_id"),
                    status=ContentStatus(content_data["status"]),
                    author_id=content_data["author_id"],
                    views=content_data.get("views", 0),
                    likes=content_data.get("likes", 0),
                    dislikes=content_data.get("dislikes", 0)
                )
                session.add(content)
            
            session.commit()
            logger.info(f"📊 Відновлено {len(export_data.get('users', []))} користувачів та {len(export_data.get('content', []))} контенту")
    
    def _restore_files(self, temp_dir: str):
        """Відновлення файлів"""
        logger.info("📁 Відновлення файлів...")
        
        files_dir = Path(temp_dir) / "files"
        if files_dir.exists():
            for file_path in files_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(files_dir)
                    target_path = Path(relative_path)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, target_path)
        
        logger.info("✅ Файли відновлені")
    
    def list_backups(self) -> List[Dict]:
        """Список всіх backup файлів"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            try:
                stat = backup_file.stat()
                
                # Спроба прочитати метадані
                metadata = {}
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zip_file:
                        if "backup_metadata.json" in zip_file.namelist():
                            metadata_content = zip_file.read("backup_metadata.json")
                            metadata = json.loads(metadata_content.decode('utf-8'))
                except:
                    pass
                
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime),
                    "type": metadata.get("backup_type", "unknown"),
                    "metadata": metadata
                })
            except Exception as e:
                logger.warning(f"Не вдалося прочитати backup {backup_file}: {e}")
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def cleanup_old_backups(self, keep: int = 7):
        """Видалення старих backup файлів"""
        backups = self.list_backups()
        
        if len(backups) <= keep:
            logger.info(f"📁 Всі {len(backups)} backup файлів збережені")
            return
        
        to_delete = backups[keep:]
        
        for backup in to_delete:
            try:
                Path(backup["path"]).unlink()
                logger.info(f"🗑️ Видалено старий backup: {backup['filename']}")
            except Exception as e:
                logger.error(f"❌ Не вдалося видалити {backup['filename']}: {e}")
        
        logger.info(f"✅ Очищення завершено. Збережено {keep} останніх backup файлів")

def main():
    """Головна функція"""
    parser = argparse.ArgumentParser(description="Система резервного копіювання")
    
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")
    
    # Команда create
    create_parser = subparsers.add_parser("create", help="Створити backup")
    create_parser.add_argument("--type", choices=["full", "db", "files"], default="full", help="Тип backup")
    create_parser.add_argument("--output", help="Шлях до вихідного файлу")
    
    # Команда restore
    restore_parser = subparsers.add_parser("restore", help="Відновити з backup")
    restore_parser.add_argument("backup_file", help="Файл backup для відновлення")
    restore_parser.add_argument("--force", action="store_true", help="Відновити без підтвердження")
    
    # Команда list
    list_parser = subparsers.add_parser("list", help="Список backup файлів")
    
    # Команда cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Очистити старі backup")
    cleanup_parser.add_argument("--keep", type=int, default=7, help="Кількість файлів для збереження")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = BackupManager()
    
    try:
        if args.command == "create":
            backup_file = manager.create_backup(args.type, args.output)
            print(f"✅ Backup створено: {backup_file}")
            
        elif args.command == "restore":
            manager.restore_backup(args.backup_file, args.force)
            print("✅ Відновлення завершено")
            
        elif args.command == "list":
            backups = manager.list_backups()
            if backups:
                print(f"📁 Знайдено {len(backups)} backup файлів:")
                for backup in backups:
                    size_mb = backup["size"] / 1024 / 1024
                    print(f"  {backup['filename']} ({size_mb:.1f}MB, {backup['type']}, {backup['created'].strftime('%Y-%m-%d %H:%M')})")
            else:
                print("📭 Backup файлів не знайдено")
                
        elif args.command == "cleanup":
            manager.cleanup_old_backups(args.keep)
            
    except Exception as e:
        logger.error(f"❌ Помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()