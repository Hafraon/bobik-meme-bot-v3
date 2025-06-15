#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠😂🔥 Alembic середовище для міграцій БД 🧠😂🔥
"""

from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Додавання поточної директорії до PATH
sys.path.insert(0, str(Path(__file__).parent.parent))

# Імпорт налаштувань та моделей
from config.settings import settings
from database.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_database_url():
    """Отримання URL бази даних з налаштувань"""
    return settings.DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True  # Для SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Отримання URL з налаштувань
    database_url = get_database_url()
    
    # Оновлення конфігурації з реальним URL
    config.set_main_option("sqlalchemy.url", database_url)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,  # Для SQLite
            # Додаткові опції для кращої роботи
            transaction_per_migration=True,
            # Включення імен індексів
            include_name=lambda name, type_, parent_names: True,
            # Порівняння типів колонок
            compare_type=lambda context, inspected_column, metadata_column, inspected_type, metadata_type: True
        )

        with context.begin_transaction():
            context.run_migrations()

def include_name(name, type_, parent_names):
    """
    Функція для визначення, які об'єкти включати в міграції
    """
    if type_ == "table":
        # Включаємо всі таблиці
        return True
    elif type_ == "column":
        # Включаємо всі колонки
        return True
    elif type_ == "index":
        # Включаємо індекси
        return True
    elif type_ == "unique_constraint":
        # Включаємо unique constraints
        return True
    elif type_ == "foreign_key_constraint":
        # Включаємо foreign keys
        return True
    else:
        return True

def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """
    Порівняння типів колонок для автогенерації міграцій
    """
    # Ігноруємо незначні відмінності у типах
    if str(inspected_type).lower() == str(metadata_type).lower():
        return False
    
    # Спеціальна обробка для SQLite
    if "sqlite" in str(context.connection.engine.url):
        # SQLite зберігає всі INTEGER як INTEGER, незалежно від розміру
        if "INTEGER" in str(inspected_type).upper() and "INTEGER" in str(metadata_type).upper():
            return False
        
        # SQLite не розрізняє VARCHAR та TEXT
        if ("VARCHAR" in str(inspected_type).upper() or "TEXT" in str(inspected_type).upper()) and \
           ("VARCHAR" in str(metadata_type).upper() or "TEXT" in str(metadata_type).upper()):
            return False
    
    return True

def compare_server_default(context, inspected_column, metadata_column, inspected_default, metadata_default, rendered_metadata_default):
    """
    Порівняння серверних значень за замовчуванням
    """
    # Ігноруємо незначні відмінності
    if inspected_default is None and metadata_default is None:
        return False
    
    # Спеціальна обробка для різних БД
    return True

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()