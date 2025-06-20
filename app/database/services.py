# ===== РОЗСИЛКИ ТА АВТОМАТИЗАЦІЯ =====

async def get_active_users_for_broadcast(days: int = 7) -> List[Dict[str, Any]]:
    """Отримання активних користувачів для розсилки"""
    try:
        from .models import User
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with get_db_session() as session:
            users = session.query(User).filter(
                User.last_activity >= cutoff_date,
                User.is_active == True
            ).all()
            
            result = []
            for user in users:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'last_activity': user.last_activity,
                    'total_points': user.total_points
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting active users for broadcast: {e}")
        return []

async def get_all_users_for_broadcast() -> List[Dict[str, Any]]:
    """Отримання всіх користувачів для розсилки"""
    try:
        from .models import User
        
        with get_db_session() as session:
            users = session.query(User).filter(
                User.is_active == True
            ).all()
            
            result = []
            for user in users:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'created_at': user.created_at,
                    'total_points': user.total_points
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting all users for broadcast: {e}")
        return []

async def get_duel_participants_for_broadcast() -> List[Dict[str, Any]]:
    """Отримання користувачів що брали участь у дуелях"""
    try:
        from .models import User, Duel, Content
        
        with get_db_session() as session:
            # Знаходимо користувачів які мають контент в дуелях
            participants = session.query(User).join(
                Content, User.id == Content.author_id
            ).join(
                Duel, 
                (Duel.content1_id == Content.id) | (Duel.content2_id == Content.id)
            ).filter(
                User.is_active == True
            ).distinct().all()
            
            result = []
            for user in participants:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'total_points': user.total_points
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting duel participants: {e}")
        return []

async def get_users_who_can_vote(duel_id: int) -> List[Dict[str, Any]]:
    """Отримання користувачів які можуть голосувати в дуелі"""
    try:
        from .models import User, DuelVote
        
        with get_db_session() as session:
            # Знаходимо користувачів які ще не голосували в цій дуелі
            users_who_voted = session.query(DuelVote.user_id).filter(
                DuelVote.duel_id == duel_id
            ).subquery()
            
            eligible_users = session.query(User).filter(
                User.is_active == True,
                User.id.notin_(users_who_voted)
            ).all()
            
            result = []
            for user in eligible_users:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting users who can vote: {e}")
        return []

async def get_daily_best_content() -> Optional[Dict[str, Any]]:
    """Отримання кращого контенту за день"""
    try:
        from .models import Content, Rating, ContentStatus
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        with get_db_session() as session:
            # Знаходимо контент з найбільшою кількістю лайків за останню добу
            best_content = session.query(
                Content,
                func.count(Rating.id).label('likes_count')
            ).outerjoin(
                Rating, 
                (Rating.content_id == Content.id) & (Rating.rating_type == 'like')
            ).filter(
                Content.status == ContentStatus.APPROVED,
                Content.created_at >= yesterday
            ).group_by(Content.id).order_by(
                func.count(Rating.id).desc()
            ).first()
            
            if best_content:
                content, likes_count = best_content
                return {
                    'id': content.id,
                    'text': content.text,
                    'type': content.content_type,
                    'author_id': content.author_id,
                    'likes': likes_count,
                    'created_at': content.created_at
                }
            
            # Якщо немає контенту за добу, беремо випадковий схвалений
            random_content = session.query(Content).filter(
                Content.status == ContentStatus.APPROVED
            ).order_by(func.random()).first()
            
            if random_content:
                # Підраховуємо лайки для випадкового контенту
                likes_count = session.query(Rating).filter(
                    Rating.content_id == random_content.id,
                    Rating.rating_type == 'like'
                ).count()
                
                return {
                    'id': random_content.id,
                    'text': random_content.text,
                    'type': random_content.content_type,
                    'author_id': random_content.author_id,
                    'likes': likes_count,
                    'created_at': random_content.created_at
                }
            
            return None
            
    except Exception as e:
        logger.error(f"Error getting daily best content: {e}")
        return None

async def generate_weekly_stats() -> Dict[str, Any]:
    """Генерація тижневої статистики"""
    try:
        from .models import User, Content, Duel, DuelVote, DuelStatus
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        with get_db_session() as session:
            # Дуелі за тиждень
            duels_completed = session.query(Duel).filter(
                Duel.status == DuelStatus.FINISHED,
                Duel.completed_at >= week_ago
            ).count()
            
            # Голоси за тиждень
            total_votes = session.query(DuelVote).filter(
                DuelVote.created_at >= week_ago
            ).count()
            
            # Новий контент за тиждень
            new_content = session.query(Content).filter(
                Content.created_at >= week_ago
            ).count()
            
            # Активні користувачі
            active_users = session.query(User).filter(
                User.last_activity >= week_ago
            ).count()
            
            # Топ дуеліст (найбільше перемог за тиждень)
            top_duelist_data = session.query(
                User.full_name,
                func.count(Duel.id).label('wins_count')
            ).join(
                Content, User.id == Content.author_id
            ).join(
                Duel, Duel.winner_content_id == Content.id
            ).filter(
                Duel.completed_at >= week_ago
            ).group_by(User.id, User.full_name).order_by(
                func.count(Duel.id).desc()
            ).first()
            
            top_duelist = "Невідомо"
            top_wins = 0
            if top_duelist_data:
                top_duelist, top_wins = top_duelist_data
            
            # Найпопулярніший контент
            top_content_data = session.query(
                Content.text,
                func.count(DuelVote.id).label('votes_count')
            ).join(
                DuelVote, DuelVote.content_id == Content.id
            ).filter(
                DuelVote.created_at >= week_ago
            ).group_by(Content.id, Content.text).order_by(
                func.count(DuelVote.id).desc()
            ).first()
            
            top_content = "Завантаження..."
            if top_content_data:
                top_content, _ = top_content_data
            
            return {
                'duels_completed': duels_completed,
                'total_votes': total_votes,
                'new_content': new_content,
                'active_users': active_users,
                'top_duelist': top_duelist,
                'top_wins': top_wins,
                'top_content': top_content,
                'period': 'week',
                'generated_at': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error generating weekly stats: {e}")
        return {
            'duels_completed': 0,
            'total_votes': 0,
            'new_content': 0,
            'active_users': 0,
            'top_duelist': 'Невідомо',
            'top_wins': 0,
            'top_content': 'Помилка завантаження',
            'error': str(e)
        }

async def get_recent_achievements(hours: int = 24) -> List[Dict[str, Any]]:
    """Отримання недавніх досягнень користувачів"""
    try:
        from .models import User
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Поки що базова реалізація - можна розширити
        achievements = []
        
        with get_db_session() as session:
            # Знаходимо користувачів які досягли нових рангів
            users_with_high_points = session.query(User).filter(
                User.last_activity >= cutoff_time,
                User.total_points >= 100  # Приклад досягнення
            ).all()
            
            for user in users_with_high_points:
                # Перевіряємо чи це нове досягнення
                if user.total_points >= 1000 and user.total_points < 1100:  # Недавно досяг 1000
                    achievements.append({
                        'id': f"milestone_1000_{user.id}",
                        'user_id': user.id,
                        'title': "Майстер Гумору!",
                        'description': "Досягнуто 1000 балів",
                        'points': 100,
                        'achieved_at': user.last_activity
                    })
        
        return achievements
        
    except Exception as e:
        logger.error(f"Error getting recent achievements: {e}")
        return []

async def get_recent_rank_ups(hours: int = 24) -> List[Dict[str, Any]]:
    """Отримання недавніх підвищень рангу"""
    try:
        from .models import User
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        rank_ups = []
        
        with get_db_session() as session:
            # Знаходимо користувачів з недавньою активністю
            recent_users = session.query(User).filter(
                User.last_activity >= cutoff_time
            ).all()
            
            for user in recent_users:
                # Визначаємо поточний ранг
                points = user.total_points
                current_rank = get_rank_by_points(points)
                
                # Перевіряємо чи це нове досягнення рангу
                # (тут можна додати логіку перевірки попереднього рангу)
                
                # Розраховуємо до наступного рангу
                next_rank_points = get_next_rank_points(points)
                points_to_next = max(0, next_rank_points - points)
                
                # Додаємо приклад rank up (можна розширити логіку)
                if points >= 500 and points < 600:  # Недавно досяг 500
                    rank_ups.append({
                        'user_id': user.id,
                        'new_rank': current_rank,
                        'total_points': points,
                        'points_to_next': points_to_next,
                        'achieved_at': user.last_activity
                    })
        
        return rank_ups
        
    except Exception as e:
        logger.error(f"Error getting recent rank ups: {e}")
        return []

def get_rank_by_points(points: int) -> str:
    """Визначення рангу за балами"""
    if points >= 5000:
        return "🚀 Гумористичний Геній"
    elif points >= 3000:
        return "🌟 Легенда Мемів"
    elif points >= 1500:
        return "🏆 Король Гумору"
    elif points >= 750:
        return "👑 Мастер Рофлу"
    elif points >= 350:
        return "🎭 Комік"
    elif points >= 150:
        return "😂 Гуморист"
    elif points >= 50:
        return "😄 Сміхун"
    else:
        return "🤡 Новачок"

def get_next_rank_points(current_points: int) -> int:
    """Отримання балів для наступного рангу"""
    rank_thresholds = [50, 150, 350, 750, 1500, 3000, 5000]
    
    for threshold in rank_thresholds:
        if current_points < threshold:
            return threshold
    
    return 10000  # Максимальний рівень

async def mark_user_inactive(user_id: int):
    """Позначити користувача як неактивного"""
    try:
        from .models import User
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = False
                session.commit()
                logger.info(f"User {user_id} marked as inactive")
                
    except Exception as e:
        logger.error(f"Error marking user inactive: {e}")

async def get_broadcast_statistics() -> Dict[str, Any]:
    """Статистика для розсилок"""
    try:
        from .models import User, Content, Duel
        from datetime import datetime, timedelta
        
        with get_db_session() as session:
            # Загальна статистика
            total_users = session.query(User).filter(User.is_active == True).count()
            
            # Активність за різні періоди
            day_ago = datetime.utcnow() - timedelta(days=1)
            week_ago = datetime.utcnow() - timedelta(days=7)
            month_ago = datetime.utcnow() - timedelta(days=30)
            
            active_today = session.query(User).filter(
                User.last_activity >= day_ago,
                User.is_active == True
            ).count()
            
            active_week = session.query(User).filter(
                User.last_activity >= week_ago,
                User.is_active == True
            ).count()
            
            active_month = session.query(User).filter(
                User.last_activity >= month_ago,
                User.is_active == True
            ).count()
            
            # Контент статистика
            total_content = session.query(Content).count()
            active_duels = session.query(Duel).filter(
                Duel.status == 'ACTIVE'
            ).count()
            
            return {
                'total_users': total_users,
                'active_today': active_today,
                'active_week': active_week,
                'active_month': active_month,
                'engagement_rate': (active_week / total_users * 100) if total_users > 0 else 0,
                'total_content': total_content,
                'active_duels': active_duels,
                'last_updated': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error getting broadcast statistics: {e}")
        return {
            'total_users': 0,
            'active_today': 0,
            'active_week': 0,
            'active_month': 0,
            'engagement_rate': 0,
            'total_content': 0,
            'active_duels': 0,
            'error': str(e)
        }