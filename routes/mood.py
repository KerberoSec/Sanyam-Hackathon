from flask import Blueprint, request, jsonify
from models import Mood, HabitLog, db
from routes.auth import token_required
from datetime import date, timedelta
from services.coach_engine import CoachEngine

mood_bp = Blueprint('mood', __name__, url_prefix='/api/mood')

MOOD_EMOJIS = {
    'happy': '😊',
    'neutral': '😐',
    'sad': '😢'
}

@mood_bp.route('', methods=['POST'])
@token_required
def log_mood(current_user):
    """Log mood for today"""
    data = request.get_json()

    if not data or data.get('mood') not in MOOD_EMOJIS:
        return jsonify({'message': 'Invalid mood. Must be happy, neutral, or sad.'}), 400

    # Check if mood already logged for today
    existing = Mood.query.filter_by(
        user_id=current_user.id,
        date=date.today()
    ).first()

    if existing:
        existing.mood = data['mood']
        existing.note = data.get('note', None)
    else:
        mood = Mood(
            user_id=current_user.id,
            date=date.today(),
            mood=data['mood'],
            note=data.get('note', None)
        )
        db.session.add(mood)

    db.session.commit()

    return jsonify({
        'message': 'Mood logged successfully',
        'mood': data['mood'],
        'emoji': MOOD_EMOJIS[data['mood']]
    }), 200

@mood_bp.route('/today', methods=['GET'])
@token_required
def get_todays_mood(current_user):
    """Get today's mood"""
    mood = Mood.query.filter_by(
        user_id=current_user.id,
        date=date.today()
    ).first()

    if not mood:
        return jsonify({'mood': None}), 200

    return jsonify({'mood': mood.to_dict()}), 200

@mood_bp.route('/history', methods=['GET'])
@token_required
def get_mood_history(current_user):
    """Get mood history"""
    days = request.args.get('days', 30, type=int)
    start_date = date.today() - timedelta(days=days)

    moods = Mood.query.filter(
        Mood.user_id == current_user.id,
        Mood.date >= start_date
    ).order_by(Mood.date).all()

    return jsonify({
        'moods': [m.to_dict() for m in moods]
    }), 200

@mood_bp.route('/analytics', methods=['GET'])
@token_required
def get_mood_analytics(current_user):
    """Get mood analytics and correlations"""
    last_30_days = date.today() - timedelta(days=30)

    moods = Mood.query.filter(
        Mood.user_id == current_user.id,
        Mood.date >= last_30_days
    ).all()

    if not moods:
        return jsonify({
            'mood_distribution': {
                'happy': 0,
                'neutral': 0,
                'sad': 0
            },
            'mood_streak': 0,
            'insights': []
        }), 200

    # Count moods
    mood_counts = {
        'happy': sum(1 for m in moods if m.mood == 'happy'),
        'neutral': sum(1 for m in moods if m.mood == 'neutral'),
        'sad': sum(1 for m in moods if m.mood == 'sad')
    }

    # Calculate mood streak (consecutive happy days)
    mood_dict = {m.date: m.mood for m in sorted(moods, key=lambda x: x.date)}
    happy_streak = 0
    current_happy_streak = 0

    for i in range(len(moods) - 1, -1, -1):
        mood = moods[i]
        if mood.mood == 'happy':
            current_happy_streak += 1
            happy_streak = max(happy_streak, current_happy_streak)
        else:
            current_happy_streak = 0

    # Get mood-habit correlation
    correlation = CoachEngine.analyze_mood_habit_correlation(current_user.id)

    return jsonify({
        'mood_distribution': mood_counts,
        'happy_streak': happy_streak,
        'mood_correlation': correlation,
        'insights': []
    }), 200

@mood_bp.route('/stats', methods=['GET'])
@token_required
def get_mood_stats(current_user):
    """Get detailed mood statistics"""
    periods = {
        '7d': 7,
        '30d': 30,
        '90d': 90
    }

    stats = {}

    for period_name, days in periods.items():
        start_date = date.today() - timedelta(days=days)

        moods = Mood.query.filter(
            Mood.user_id == current_user.id,
            Mood.date >= start_date
        ).all()

        happy_count = sum(1 for m in moods if m.mood == 'happy')
        neutral_count = sum(1 for m in moods if m.mood == 'neutral')
        sad_count = sum(1 for m in moods if m.mood == 'sad')
        total = len(moods)

        happy_percent = int((happy_count / total) * 100) if total > 0 else 0
        neutral_percent = int((neutral_count / total) * 100) if total > 0 else 0
        sad_percent = int((sad_count / total) * 100) if total > 0 else 0

        stats[period_name] = {
            'happy': happy_count,
            'neutral': neutral_count,
            'sad': sad_count,
            'happy_percent': happy_percent,
            'neutral_percent': neutral_percent,
            'sad_percent': sad_percent
        }

    return jsonify(stats), 200
