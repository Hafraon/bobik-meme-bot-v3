"""Початкова схема БД для україномовного бота

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Створення початкової схеми"""
    
    # Створення таблиці користувачів
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True, default=0),
        sa.Column('rank', sa.String(length=100), nullable=True, default='🤡 Новачок'),
        sa.Column('daily_subscription', sa.Boolean(), nullable=True, default=False),
        sa.Column('language_code', sa.String(length=10), nullable=True, default='uk'),
        sa.Column('jokes_submitted', sa.Integer(), nullable=True, default=0),
        sa.Column('jokes_approved', sa.Integer(), nullable=True, default=0),
        sa.Column('memes_submitted', sa.Integer(), nullable=True, default=0),
        sa.Column('memes_approved', sa.Integer(), nullable=True, default=0),
        sa.Column('reactions_given', sa.Integer(), nullable=True, default=0),
        sa.Column('duels_won', sa.Integer(), nullable=True, default=0),
        sa.Column('duels_lost', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Створення таблиці контенту
    op.create_table('content',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('content_type', sa.Enum('MEME', 'JOKE', name='contenttype'), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('file_id', sa.String(length=255), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='contentstatus'), nullable=True),
        sa.Column('author_id', sa.BigInteger(), nullable=False),
        sa.Column('moderator_id', sa.BigInteger(), nullable=True),
        sa.Column('moderation_comment', sa.Text(), nullable=True),
        sa.Column('views', sa.Integer(), nullable=True, default=0),
        sa.Column('likes', sa.Integer(), nullable=True, default=0),
        sa.Column('dislikes', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Індекси для контенту
    op.create_index(op.f('ix_content_author_id'), 'content', ['author_id'], unique=False)
    op.create_index(op.f('ix_content_status'), 'content', ['status'], unique=False)
    op.create_index(op.f('ix_content_type'), 'content', ['content_type'], unique=False)
    op.create_index(op.f('ix_content_created_at'), 'content', ['created_at'], unique=False)
    
    # Створення таблиці рейтингів
    op.create_table('ratings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('points_awarded', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Індекси для рейтингів
    op.create_index(op.f('ix_ratings_user_id'), 'ratings', ['user_id'], unique=False)
    op.create_index(op.f('ix_ratings_content_id'), 'ratings', ['content_id'], unique=False)
    op.create_index(op.f('ix_ratings_action_type'), 'ratings', ['action_type'], unique=False)
    
    # Створення таблиці дуелей
    op.create_table('duels',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('initiator_id', sa.BigInteger(), nullable=False),
        sa.Column('opponent_id', sa.BigInteger(), nullable=True),
        sa.Column('initiator_content_id', sa.Integer(), nullable=True),
        sa.Column('opponent_content_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'CANCELLED', name='duelstatus'), nullable=True),
        sa.Column('winner_id', sa.BigInteger(), nullable=True),
        sa.Column('initiator_votes', sa.Integer(), nullable=True, default=0),
        sa.Column('opponent_votes', sa.Integer(), nullable=True, default=0),
        sa.Column('total_votes', sa.Integer(), nullable=True, default=0),
        sa.Column('voting_ends_at', sa.DateTime(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['initiator_content_id'], ['content.id'], ),
        sa.ForeignKeyConstraint(['initiator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['opponent_content_id'], ['content.id'], ),
        sa.ForeignKeyConstraint(['opponent_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Індекси для дуелей
    op.create_index(op.f('ix_duels_initiator_id'), 'duels', ['initiator_id'], unique=False)
    op.create_index(op.f('ix_duels_status'), 'duels', ['status'], unique=False)
    op.create_index(op.f('ix_duels_created_at'), 'duels', ['created_at'], unique=False)
    
    # Створення таблиці голосів у дуелях
    op.create_table('duel_votes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('duel_id', sa.Integer(), nullable=False),
        sa.Column('voter_id', sa.BigInteger(), nullable=False),
        sa.Column('vote_for', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['duel_id'], ['duels.id'], ),
        sa.ForeignKeyConstraint(['voter_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Унікальний індекс для запобігання повторного голосування
    op.create_index('ix_duel_votes_unique_vote', 'duel_votes', ['duel_id', 'voter_id'], unique=True)
    
    # Створення таблиці адміністративних дій
    op.create_table('admin_actions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('admin_id', sa.BigInteger(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Індекси для адміністративних дій
    op.create_index(op.f('ix_admin_actions_admin_id'), 'admin_actions', ['admin_id'], unique=False)
    op.create_index(op.f('ix_admin_actions_action_type'), 'admin_actions', ['action_type'], unique=False)
    op.create_index(op.f('ix_admin_actions_created_at'), 'admin_actions', ['created_at'], unique=False)
    
    # Створення таблиці статистики бота
    op.create_table('bot_statistics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('total_users', sa.Integer(), nullable=True, default=0),
        sa.Column('active_users_today', sa.Integer(), nullable=True, default=0),
        sa.Column('new_users_today', sa.Integer(), nullable=True, default=0),
        sa.Column('total_content', sa.Integer(), nullable=True, default=0),
        sa.Column('pending_content', sa.Integer(), nullable=True, default=0),
        sa.Column('approved_content_today', sa.Integer(), nullable=True, default=0),
        sa.Column('active_duels', sa.Integer(), nullable=True, default=0),
        sa.Column('completed_duels_today', sa.Integer(), nullable=True, default=0),
        sa.Column('commands_executed_today', sa.Integer(), nullable=True, default=0),
        sa.Column('memes_sent_today', sa.Integer(), nullable=True, default=0),
        sa.Column('jokes_sent_today', sa.Integer(), nullable=True, default=0),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Індекс для статистики по даті
    op.create_index(op.f('ix_bot_statistics_date'), 'bot_statistics', ['date'], unique=False)


def downgrade() -> None:
    """Видалення схеми"""
    
    # Видалення таблиць у зворотному порядку
    op.drop_table('bot_statistics')
    op.drop_table('admin_actions')
    op.drop_table('duel_votes')
    op.drop_table('duels')
    op.drop_table('ratings')
    op.drop_table('content')
    op.drop_table('users')
    
    # Видалення enum типів (для PostgreSQL)
    try:
        op.execute("DROP TYPE IF EXISTS contenttype")
        op.execute("DROP TYPE IF EXISTS contentstatus")
        op.execute("DROP TYPE IF EXISTS duelstatus")
    except:
        # Ігноруємо помилки для SQLite
        pass