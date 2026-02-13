from flask import Blueprint, request, jsonify
from models import User, db, AIMessage
from routes.auth import token_required
from services.ai_coach import AICoachService
from services.streak_engine import StreakEngine
from datetime import date, datetime, timedelta

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/daily-message', methods=['GET'])
@token_required
def get_daily_message(current_user):
    """
    Get today's daily coaching message.
    Checks cache first, generates new if needed.
    """
    today = date.today()

    # Check cache
    cached_message = AIMessage.query.filter_by(
        user_id=current_user.id,
        message_type='daily',
        date=today
    ).first()

    if cached_message:
        return jsonify({
            'message': cached_message.content,
            'cached': True,
            'generated_at': cached_message.generated_at.isoformat()
        }), 200

    # Check if AI is available
    if not AICoachService.is_available():
        return jsonify({
            'message': AICoachService.FALLBACK_MESSAGES['daily'],
            'cached': False,
            'error': 'AI service not configured'
        }), 200

    # Get user stats
    stats = StreakEngine.calculate_stats_for_user(current_user.id)
    habits = [h.to_dict() for h in current_user.habits if h.active]

    # Generate new message
    result = AICoachService.generate_daily_coach_message(stats, habits)

    if 'error' not in result or result['error'] is None:
        # Cache the message
        ai_message = AIMessage(
            user_id=current_user.id,
            message_type='daily',
            content=result['message'],
            date=today,
            cached=True
        )
        db.session.add(ai_message)
        db.session.commit()

    return jsonify({
        'message': result.get('message', AICoachService.FALLBACK_MESSAGES['daily']),
        'cached': False,
        'generated_at': result.get('generated_at'),
        'error': result.get('error')
    }), 200

@ai_bp.route('/weekly-summary', methods=['GET'])
@token_required
def get_weekly_summary(current_user):
    """
    Get weekly performance summary from AI.
    Generated on-demand.
    """
    # Get user stats
    stats = StreakEngine.calculate_stats_for_user(current_user.id)
    habits = [h.to_dict() for h in current_user.habits if h.active]

    # Get weekly data from analytics
    from routes.analytics import get_weekly_completion_data
    weekly_data = get_weekly_completion_data(current_user.id)

    # Generate summary
    result = AICoachService.generate_weekly_summary(stats, habits, weekly_data)

    # Cache the latest weekly summary
    latest_weekly = AIMessage.query.filter_by(
        user_id=current_user.id,
        message_type='weekly'
    ).order_by(AIMessage.generated_at.desc()).first()

    # Only cache if it's different from the last one or older than 1 day
    should_cache = not latest_weekly or (datetime.utcnow() - latest_weekly.generated_at).days >= 1

    if should_cache and 'error' not in result or result['error'] is None:
        ai_message = AIMessage(
            user_id=current_user.id,
            message_type='weekly',
            content=result.get('summary', AICoachService.FALLBACK_MESSAGES['weekly']),
            cached=True
        )
        db.session.add(ai_message)
        db.session.commit()

    return jsonify({
        'summary': result.get('summary', AICoachService.FALLBACK_MESSAGES['weekly']),
        'generated_at': result.get('generated_at'),
        'error': result.get('error')
    }), 200

@ai_bp.route('/habit-recommendations', methods=['POST'])
@token_required
def get_habit_recommendations(current_user):
    """
    Get AI-powered habit recommendations based on user's goal.
    """
    data = request.get_json()
    user_goal = data.get('goal', 'better focus')

    if not user_goal:
        return jsonify({'message': 'Goal is required'}), 400

    # Get user stats
    stats = StreakEngine.calculate_stats_for_user(current_user.id)
    existing_habits = [h.to_dict() for h in current_user.habits if h.active]

    # Generate recommendations
    result = AICoachService.generate_habit_recommendations(user_goal, stats, existing_habits)

    return jsonify({
        'recommendations': result.get('recommendations', []),
        'goal': user_goal,
        'generated_at': result.get('generated_at'),
        'error': result.get('error')
    }), 200

@ai_bp.route('/mood-insights', methods=['GET'])
@token_required
def get_mood_insights(current_user):
    """
    Get AI insights on mood-habit correlations.
    """
    from datetime import timedelta

    # Get mood data
    last_30_days = date.today() - timedelta(days=30)
    moods = [m.to_dict() for m in current_user.moods if m.date >= last_30_days]

    if not moods:
        return jsonify({
            'insight': 'Start logging your mood daily to unlock AI insights!',
            'error': 'Insufficient mood data'
        }), 200

    # Get habit completion rate
    from routes.analytics import get_weekly_completion_data
    stats = StreakEngine.calculate_stats_for_user(current_user.id)
    completion_rate = stats.get('total_completions', 0)

    # Generate insight
    result = AICoachService.analyze_mood_habit_correlation(moods, completion_rate)

    return jsonify({
        'insight': result.get('insight', 'Your mood and habits are interconnected.'),
        'happy_percent': result.get('happy_percent'),
        'generated_at': result.get('generated_at'),
        'error': result.get('error')
    }), 200

@ai_bp.route('/health', methods=['GET'])
@token_required
def ai_health_check(current_user):
    """Check if AI service is available"""
    available = AICoachService.is_available()

    return jsonify({
        'ai_available': available,
        'model': AICoachService.MODEL_NAME if available else None,
        'status': 'healthy' if available else 'disabled'
    }), 200
