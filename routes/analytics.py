from flask import Blueprint, request, jsonify
from models import Habit, HabitLog, User, Mood, db
from routes.auth import token_required
from services.streak_engine import StreakEngine
from services.coach_engine import CoachEngine
from datetime import date, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('', methods=['GET'])
@token_required
def get_analytics(current_user):
    """Get analytics dashboard data"""
    habits = Habit.query.filter_by(user_id=current_user.id, active=True).all()

    if not habits:
        return jsonify({
            'summary': {
                'total_habits': 0,
                'total_completions': 0,
                'combined_streak': 0,
                'consistency_score': 0
            },
            'habits': [],
            'weekly_chart': [],
            'monthly_trend': [],
            'insights': []
        }), 200

    # Calculate summary stats
    stats = StreakEngine.calculate_stats_for_user(current_user.id)

    # Get consistency score (average across all habits)
    consistency_scores = [
        StreakEngine.get_consistency_score(h.id, current_user.id, 30)
        for h in habits
    ]
    avg_consistency = int(sum(consistency_scores) / len(consistency_scores)) if consistency_scores else 0

    # Build habits data
    habits_data = []
    for habit in habits:
        habits_data.append({
            'id': habit.id,
            'title': habit.title,
            'icon': habit.icon,
            'color': habit.color,
            'current_streak': StreakEngine.calculate_current_streak(habit.id, current_user.id),
            'longest_streak': StreakEngine.calculate_longest_streak(habit.id, current_user.id),
            'total_completions': StreakEngine.get_total_completions(habit.id, current_user.id),
            'completion_rate': StreakEngine.get_completion_rate(habit.id, current_user.id)
        })

    # Get weekly data
    weekly_data = get_weekly_completion_data(current_user.id)

    # Get monthly trend
    monthly_trend = get_monthly_trend_data(current_user.id)

    # Get insights
    insights = CoachEngine.get_all_insights(current_user.id)

    return jsonify({
        'summary': {
            'total_habits': stats['total_habits'],
            'total_completions': stats['total_completions'],
            'combined_streak': stats['combined_streak'],
            'consistency_score': avg_consistency
        },
        'habits': habits_data,
        'weekly_chart': weekly_data,
        'monthly_trend': monthly_trend,
        'insights': insights,
        'user_level': current_user.level,
        'user_xp': current_user.xp_points
    }), 200

@analytics_bp.route('/weekly', methods=['GET'])
@token_required
def get_weekly(current_user):
    """Get weekly completion data"""
    data = get_weekly_completion_data(current_user.id)
    return jsonify({'weekly': data}), 200

@analytics_bp.route('/monthly', methods=['GET'])
@token_required
def get_monthly(current_user):
    """Get monthly trend data"""
    data = get_monthly_trend_data(current_user.id)
    return jsonify({'monthly': data}), 200

@analytics_bp.route('/habit/<int:habit_id>', methods=['GET'])
@token_required
def get_habit_analytics(current_user, habit_id):
    """Get detailed analytics for a specific habit"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    return jsonify({
        'habit': {
            'id': habit.id,
            'title': habit.title,
            'icon': habit.icon
        },
        'stats': {
            'current_streak': StreakEngine.calculate_current_streak(habit.id, current_user.id),
            'longest_streak': StreakEngine.calculate_longest_streak(habit.id, current_user.id),
            'total_completions': StreakEngine.get_total_completions(habit.id, current_user.id),
            'consistency_score_7d': StreakEngine.get_consistency_score(habit.id, current_user.id, 7),
            'consistency_score_30d': StreakEngine.get_consistency_score(habit.id, current_user.id, 30),
            'completion_rate_7d': StreakEngine.get_completion_rate(habit.id, current_user.id, 7),
            'completion_rate_30d': StreakEngine.get_completion_rate(habit.id, current_user.id, 30)
        },
        'history': StreakEngine.get_habit_history(habit.id, current_user.id, 30)
    }), 200

def get_weekly_completion_data(user_id):
    """Calculate completion data by day of week"""
    last_30_days = date.today() - timedelta(days=30)

    logs = HabitLog.query.filter(
        HabitLog.user_id == user_id,
        HabitLog.date >= last_30_days
    ).all()

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_data = {day: {'completed': 0, 'skipped': 0, 'missed': 0} for day in day_names}

    for log in logs:
        day_name = day_names[log.date.weekday()]
        day_data[day_name][log.status] += 1

    # Convert to chart format
    chart_data = []
    for day in day_names:
        total = sum(day_data[day].values())
        completed = day_data[day]['completed']
        completion_rate = int((completed / total) * 100) if total > 0 else 0

        chart_data.append({
            'day': day,
            'completed': completed,
            'skipped': day_data[day]['skipped'],
            'missed': day_data[day]['missed'],
            'total': total,
            'rate': completion_rate
        })

    return chart_data

def get_monthly_trend_data(user_id):
    """Get monthly completion trend"""
    # Get last 12 months
    months_data = []
    today = date.today()

    for i in range(11, -1, -1):
        # Calculate month start and end
        first_day = today.replace(day=1) - timedelta(days=i*30)
        month_start = first_day.replace(day=1)

        # Next month's first day
        if first_day.month == 12:
            month_end = first_day.replace(year=first_day.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = first_day.replace(month=first_day.month + 1, day=1) - timedelta(days=1)

        # Count completions
        completions = HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.status == 'completed',
            HabitLog.date >= month_start,
            HabitLog.date <= month_end
        ).count()

        total_logs = HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.date >= month_start,
            HabitLog.date <= month_end
        ).count()

        completion_rate = int((completions / total_logs) * 100) if total_logs > 0 else 0

        months_data.append({
            'month': month_start.strftime('%b %y'),
            'completions': completions,
            'rate': completion_rate
        })

    return months_data
