# ===== ДУЕЛІ ТА ГОЛОСУВАННЯ =====

async def create_duel(content1_id: int, content2_id: int, ends_at, min_votes: int = 3) -> Optional[Dict[str, Any]]:
    """Створення нової дуелі"""
    try:
        from .models import Duel, DuelStatus
        
        with get_db_session() as session:
            # Створюємо нову дуель
            duel = Duel(
                content1_id=content1_id,
                content2_id=content2_id,
                status=DuelStatus.ACTIVE,
                ends_at=ends_at,
                min_votes=min_votes,
                content1_votes=0,
                content2_votes=0,
                total_votes=0
            )
            
            session.add(duel)
            session.commit()
            session.refresh(duel)
            
            logger.info(f"Created duel {duel.id} between content {content1_id} and {content2_id}")
            
            # Повертаємо дуель з повною інформацією
            return await get_duel_by_id(duel.id)
            
    except Exception as e:
        logger.error(f"Error creating duel: {e}")
        return None

async def get_duel_by_id(duel_id: int) -> Optional[Dict[str, Any]]:
    """Отримання дуелі за ID з повною інформацією"""
    try:
        from .models import Duel, Content, User, DuelStatus
        
        with get_db_session() as session:
            # Отримуємо дуель з join'ами на контент
            result = session.query(
                Duel,
                Content.text.label('content1_text'),
                Content.content_type.label('content1_type'),
                Content.author_id.label('content1_author'),
            ).join(
                Content, Duel.content1_id == Content.id
            ).filter(Duel.id == duel_id).first()
            
            if not result:
                return None
                
            duel = result.Duel
            
            # Отримуємо другий контент окремо
            content2 = session.query(Content).filter(Content.id == duel.content2_id).first()
            
            if not content2:
                return None
            
            # Формуємо результат
            duel_data = {
                'id': duel.id,
                'status': duel.status,
                'content1_id': duel.content1_id,
                'content2_id': duel.content2_id,
                'content1_votes': duel.content1_votes,
                'content2_votes': duel.content2_votes,
                'total_votes': duel.total_votes,
                'min_votes': duel.min_votes,
                'ends_at': duel.ends_at,
                'created_at': duel.created_at,
                'finished_at': duel.finished_at,
                'winner_content_id': duel.winner_content_id,
                
                # Інформація про контент
                'content1': {
                    'id': duel.content1_id,
                    'text': result.content1_text,
                    'type': result.content1_type,
                    'author_id': result.content1_author
                },
                'content2': {
                    'id': content2.id,
                    'text': content2.text,
                    'type': content2.content_type,
                    'author_id': content2.author_id
                }
            }
            
            return duel_data
            
    except Exception as e:
        logger.error(f"Error getting duel {duel_id}: {e}")
        return None

async def get_active_duels(limit: int = 10) -> List[Dict[str, Any]]:
    """Отримання списку активних дуелів"""
    try:
        from .models import Duel, DuelStatus
        
        with get_db_session() as session:
            duels = session.query(Duel).filter(
                Duel.status == DuelStatus.ACTIVE
            ).order_by(Duel.created_at.desc()).limit(limit).all()
            
            result = []
            for duel in duels:
                result.append({
                    'id': duel.id,
                    'status': duel.status,
                    'content1_votes': duel.content1_votes,
                    'content2_votes': duel.content2_votes,
                    'total_votes': duel.total_votes,
                    'ends_at': duel.ends_at,
                    'created_at': duel.created_at,
                    'min_votes': duel.min_votes
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting active duels: {e}")
        return []

async def vote_in_duel(duel_id: int, user_id: int, vote_for: str) -> Dict[str, Any]:
    """Голосування в дуелі
    
    Args:
        duel_id: ID дуелі
        user_id: ID користувача
        vote_for: 'content1' або 'content2'
    
    Returns:
        Dict з результатом: {'success': bool, 'error': str, 'votes': dict}
    """
    try:
        from .models import Duel, DuelVote, DuelStatus
        
        with get_db_session() as session:
            # Перевіряємо дуель
            duel = session.query(Duel).filter(Duel.id == duel_id).first()
            
            if not duel:
                return {'success': False, 'error': 'Дуель не знайдена'}
            
            if duel.status != DuelStatus.ACTIVE:
                return {'success': False, 'error': 'duel_finished'}
            
            # Перевіряємо чи користувач вже голосував
            existing_vote = session.query(DuelVote).filter(
                DuelVote.duel_id == duel_id,
                DuelVote.user_id == user_id
            ).first()
            
            if existing_vote:
                return {'success': False, 'error': 'already_voted'}
            
            # Валідуємо vote_for
            if vote_for not in ['content1', 'content2']:
                return {'success': False, 'error': 'Некоректний вибір'}
            
            # Створюємо голос
            content_id = duel.content1_id if vote_for == 'content1' else duel.content2_id
            
            vote = DuelVote(
                duel_id=duel_id,
                user_id=user_id,
                content_id=content_id
            )
            
            session.add(vote)
            
            # Оновлюємо лічильники дуелі
            if vote_for == 'content1':
                duel.content1_votes += 1
            else:
                duel.content2_votes += 1
            
            duel.total_votes += 1
            
            session.commit()
            
            logger.info(f"User {user_id} voted for {vote_for} in duel {duel_id}")
            
            return {
                'success': True,
                'votes': {
                    'content1_votes': duel.content1_votes,
                    'content2_votes': duel.content2_votes,
                    'total_votes': duel.total_votes
                }
            }
            
    except Exception as e:
        logger.error(f"Error voting in duel {duel_id}: {e}")
        return {'success': False, 'error': 'Помилка голосування'}

async def finish_duel(duel_id: int) -> Optional[Dict[str, Any]]:
    """Завершення дуелі та визначення переможця"""
    try:
        from .models import Duel, DuelStatus, Content
        from datetime import datetime
        
        with get_db_session() as session:
            duel = session.query(Duel).filter(Duel.id == duel_id).first()
            
            if not duel or duel.status != DuelStatus.ACTIVE:
                return None
            
            # Визначаємо переможця
            winner_content_id = None
            if duel.content1_votes > duel.content2_votes:
                winner_content_id = duel.content1_id
            elif duel.content2_votes > duel.content1_votes:
                winner_content_id = duel.content2_id
            # Якщо голоси рівні - нічия (winner_content_id залишається None)
            
            # Оновлюємо дуель
            duel.status = DuelStatus.FINISHED
            duel.winner_content_id = winner_content_id
            duel.finished_at = datetime.utcnow()
            
            session.commit()
            
            # Нараховуємо бали учасникам
            await award_duel_points(duel_id, winner_content_id)
            
            logger.info(f"Duel {duel_id} finished, winner: content {winner_content_id}")
            
            return await get_duel_by_id(duel_id)
            
    except Exception as e:
        logger.error(f"Error finishing duel {duel_id}: {e}")
        return None

async def award_duel_points(duel_id: int, winner_content_id: Optional[int]):
    """Нарахування балів за дуель"""
    try:
        from .models import Duel, Content
        
        # Отримуємо повну інформацію про дуель
        duel_info = await get_duel_by_id(duel_id)
        if not duel_info:
            return
        
        content1_author = duel_info['content1']['author_id']
        content2_author = duel_info['content2']['author_id']
        
        votes1 = duel_info['content1_votes']
        votes2 = duel_info['content2_votes']
        total_votes = duel_info['total_votes']
        
        # Базові бали за участь
        await update_user_points(content1_author, 10, f"Участь у дуелі #{duel_id}")
        await update_user_points(content2_author, 10, f"Участь у дуелі #{duel_id}")
        
        if winner_content_id:
            # Бали за перемогу
            winner_author = content1_author if winner_content_id == duel_info['content1_id'] else content2_author
            winner_votes = votes1 if winner_content_id == duel_info['content1_id'] else votes2
            
            base_win_points = 25
            
            # Бонус за розгромну перемогу (70%+ голосів)
            if total_votes > 0:
                win_percentage = winner_votes / total_votes
                if win_percentage >= 0.7:
                    base_win_points += 25  # Epic victory bonus
                    await update_user_points(winner_author, 50, f"Розгромна перемога в дуелі #{duel_id}")
                else:
                    await update_user_points(winner_author, base_win_points, f"Перемога в дуелі #{duel_id}")
            else:
                await update_user_points(winner_author, base_win_points, f"Перемога в дуелі #{duel_id}")
        else:
            # Нічия - додаткові бали обом
            await update_user_points(content1_author, 5, f"Нічия в дуелі #{duel_id}")
            await update_user_points(content2_author, 5, f"Нічия в дуелі #{duel_id}")
        
    except Exception as e:
        logger.error(f"Error awarding duel points for duel {duel_id}: {e}")

async def get_user_duel_stats(user_id: int) -> Optional[Dict[str, Any]]:
    """Отримання статистики дуелів користувача"""
    try:
        from .models import Duel, Content, DuelStatus
        
        with get_db_session() as session:
            # Знаходимо всі дуелі де користувач брав участь
            user_duels = session.query(Duel).join(
                Content, 
                (Duel.content1_id == Content.id) | (Duel.content2_id == Content.id)
            ).filter(
                Content.author_id == user_id,
                Duel.status == DuelStatus.FINISHED
            ).all()
            
            if not user_duels:
                return None
            
            wins = 0
            losses = 0
            draws = 0
            total_votes_received = 0
            best_win_streak = 0
            current_streak = 0
            
            for duel in user_duels:
                # Визначаємо чи користувач переміг
                user_content_id = None
                user_votes = 0
                opponent_votes = 0
                
                # Знаходимо контент користувача
                if duel.content1_id:
                    content1 = session.query(Content).filter(Content.id == duel.content1_id).first()
                    if content1 and content1.author_id == user_id:
                        user_content_id = duel.content1_id
                        user_votes = duel.content1_votes
                        opponent_votes = duel.content2_votes
                
                if not user_content_id and duel.content2_id:
                    content2 = session.query(Content).filter(Content.id == duel.content2_id).first()
                    if content2 and content2.author_id == user_id:
                        user_content_id = duel.content2_id
                        user_votes = duel.content2_votes
                        opponent_votes = duel.content1_votes
                
                total_votes_received += user_votes
                
                # Підраховуємо результат
                if user_votes > opponent_votes:
                    wins += 1
                    current_streak += 1
                    best_win_streak = max(best_win_streak, current_streak)
                elif user_votes < opponent_votes:
                    losses += 1
                    current_streak = 0
                else:
                    draws += 1
                    current_streak = 0
            
            # Розрахунок рейтингу (базовий алгоритм)
            total_duels = len(user_duels)
            win_rate = wins / total_duels if total_duels > 0 else 0
            base_rating = 1000
            rating = base_rating + int((wins * 30) - (losses * 15) + (draws * 5))
            
            # Мінімальний та максимальний рейтинг
            rating = max(500, min(3000, rating))
            
            return {
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'total_duels': total_duels,
                'win_rate': win_rate,
                'rating': rating,
                'total_votes_received': total_votes_received,
                'best_win_streak': best_win_streak,
                'current_streak': current_streak
            }
            
    except Exception as e:
        logger.error(f"Error getting duel stats for user {user_id}: {e}")
        return None

async def get_user_active_duels(user_id: int) -> List[Dict[str, Any]]:
    """Отримання активних дуелів користувача"""
    try:
        from .models import Duel, Content, DuelStatus
        
        with get_db_session() as session:
            # Знаходимо активні дуелі де користувач має контент
            active_duels = session.query(Duel).join(
                Content,
                (Duel.content1_id == Content.id) | (Duel.content2_id == Content.id)
            ).filter(
                Content.author_id == user_id,
                Duel.status == DuelStatus.ACTIVE
            ).all()
            
            result = []
            for duel in active_duels:
                result.append({
                    'id': duel.id,
                    'content1_votes': duel.content1_votes,
                    'content2_votes': duel.content2_votes,
                    'total_votes': duel.total_votes,
                    'ends_at': duel.ends_at,
                    'created_at': duel.created_at
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting active duels for user {user_id}: {e}")
        return []

async def get_random_approved_content(content_type: 'ContentType') -> Optional[Dict[str, Any]]:
    """Отримання випадкового схваленого контенту"""
    try:
        from .models import Content, ContentStatus
        import random
        
        with get_db_session() as session:
            # Отримуємо всі схвалені контенти заданого типу
            contents = session.query(Content).filter(
                Content.content_type == content_type,
                Content.status == ContentStatus.APPROVED
            ).all()
            
            if not contents:
                return None
            
            # Вибираємо випадковий
            selected = random.choice(contents)
            
            return {
                'id': selected.id,
                'text': selected.text,
                'type': selected.content_type,
                'author_id': selected.author_id,
                'created_at': selected.created_at
            }
            
    except Exception as e:
        logger.error(f"Error getting random approved content: {e}")
        return None

async def get_duel_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Отримання топу дуелістів"""
    try:
        from .models import User
        
        leaderboard = []
        
        with get_db_session() as session:
            # Отримуємо топових користувачів за балами
            top_users = session.query(User).order_by(
                User.total_points.desc()
            ).limit(limit * 2).all()  # Беремо більше щоб відфільтрувати тих хто має дуельну статистику
            
            for user in top_users:
                stats = await get_user_duel_stats(user.id)
                if stats and stats['total_duels'] > 0:
                    leaderboard.append({
                        'user_id': user.id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'total_points': user.total_points,
                        'duel_rating': stats['rating'],
                        'duel_wins': stats['wins'],
                        'duel_total': stats['total_duels'],
                        'win_rate': stats['win_rate']
                    })
                
                if len(leaderboard) >= limit:
                    break
            
            # Сортуємо за дуельним рейтингом
            leaderboard.sort(key=lambda x: x['duel_rating'], reverse=True)
            
            return leaderboard[:limit]
            
    except Exception as e:
        logger.error(f"Error getting duel leaderboard: {e}")
        return []

async def cleanup_old_duels():
    """Очистка старих завершених дуелів (старше 30 днів)"""
    try:
        from .models import Duel, DuelStatus, DuelVote
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        with get_db_session() as session:
            # Знаходимо старі дуелі
            old_duels = session.query(Duel).filter(
                Duel.status == DuelStatus.FINISHED,
                Duel.finished_at < cutoff_date
            ).all()
            
            deleted_count = 0
            
            for duel in old_duels:
                # Видаляємо пов'язані голоси
                session.query(DuelVote).filter(DuelVote.duel_id == duel.id).delete()
                
                # Видаляємо дуель
                session.delete(duel)
                deleted_count += 1
            
            session.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old duels")
            
            return deleted_count
            
    except Exception as e:
        logger.error(f"Error cleaning up old duels: {e}")
        return 0

# ===== ПЛАНУВАЛЬНИК ДУЕЛІВ =====

async def auto_finish_expired_duels():
    """Автоматичне завершення прострочених дуелів"""
    try:
        from .models import Duel, DuelStatus
        from datetime import datetime
        
        with get_db_session() as session:
            # Знаходимо прострочені активні дуелі
            now = datetime.utcnow()
            expired_duels = session.query(Duel).filter(
                Duel.status == DuelStatus.ACTIVE,
                Duel.ends_at <= now,
                Duel.total_votes >= Duel.min_votes
            ).all()
            
            finished_count = 0
            
            for duel in expired_duels:
                await finish_duel(duel.id)
                finished_count += 1
            
            if finished_count > 0:
                logger.info(f"Auto-finished {finished_count} expired duels")
            
            return finished_count
            
    except Exception as e:
        logger.error(f"Error auto-finishing duels: {e}")
        return 0