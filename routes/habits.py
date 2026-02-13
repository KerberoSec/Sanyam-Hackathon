from flask import Blueprint, request, jsonify
from models import Habit, HabitLog, db
from routes.auth import token_required
from services.streak_engine import StreakEngine
from services.gamification import GamificationEngine
from services.coach_engine import CoachEngine
from datetime import date, time
import json

habits_bp = Blueprint('habits', __name__, url_prefix='/api/habits')

@habits_bp.route('', methods=['GET'])
@token_required
def get_habits(current_user):
    """Get all habits for current user"""
    habits = Habit.query.filter_by(user_id=current_user.id, active=True).all()

    habits_data = []
    for habit in habits:
        habit_dict = habit.to_dict()
        habit_dict['current_streak'] = StreakEngine.calculate_current_streak(habit.id, current_user.id)
        habit_dict['longest_streak'] = StreakEngine.calculate_longest_streak(habit.id, current_user.id)
        habit_dict['total_completions'] = StreakEngine.get_total_completions(habit.id, current_user.id)
        habit_dict['consistency_score'] = StreakEngine.get_consistency_score(habit.id, current_user.id)
        habit_dict['completion_rate'] = StreakEngine.get_completion_rate(habit.id, current_user.id)

        # Get today's status
        today_log = HabitLog.query.filter_by(
            habit_id=habit.id,
            user_id=current_user.id,
            date=date.today()
        ).first()
        habit_dict['today_status'] = today_log.status if today_log else None

        habits_data.append(habit_dict)

    return jsonify({
        'habits': habits_data,
        'count': len(habits_data)
    }), 200

@habits_bp.route('', methods=['POST'])
@token_required
def create_habit(current_user):
    """Create a new habit"""
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400

    habit = Habit(
        user_id=current_user.id,
        title=data['title'],
        category=data.get('category', 'general'),
        icon=data.get('icon', '✨'),
        color=data.get('color', 'primary'),
        frequency=data.get('frequency', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']),
        reminder_time=None,
        active=True
    )

    if data.get('reminder_time'):
        try:
            reminder_time = time.fromisoformat(data['reminder_time'])
            habit.reminder_time = reminder_time
        except:
            pass

    db.session.add(habit)
    db.session.commit()

    habit_dict = habit.to_dict()
    habit_dict['current_streak'] = 0
    habit_dict['longest_streak'] = 0
    habit_dict['total_completions'] = 0
    habit_dict['consistency_score'] = 0
    habit_dict['today_status'] = None

    return jsonify({
        'message': 'Habit created successfully',
        'habit': habit_dict
    }), 201

@habits_bp.route('/<int:habit_id>', methods=['GET'])
@token_required
def get_habit(current_user, habit_id):
    """Get a specific habit"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    habit_dict = habit.to_dict()
    habit_dict['current_streak'] = StreakEngine.calculate_current_streak(habit.id, current_user.id)
    habit_dict['longest_streak'] = StreakEngine.calculate_longest_streak(habit.id, current_user.id)
    habit_dict['total_completions'] = StreakEngine.get_total_completions(habit.id, current_user.id)
    habit_dict['consistency_score'] = StreakEngine.get_consistency_score(habit.id, current_user.id)
    habit_dict['completion_rate'] = StreakEngine.get_completion_rate(habit.id, current_user.id)

    return jsonify({'habit': habit_dict}), 200

@habits_bp.route('/<int:habit_id>', methods=['PUT'])
@token_required
def update_habit(current_user, habit_id):
    """Update a habit"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    data = request.get_json()

    habit.title = data.get('title', habit.title)
    habit.category = data.get('category', habit.category)
    habit.icon = data.get('icon', habit.icon)
    habit.color = data.get('color', habit.color)
    habit.frequency = data.get('frequency', habit.frequency)
    habit.active = data.get('active', habit.active)

    if data.get('reminder_time'):
        try:
            reminder_time = time.fromisoformat(data['reminder_time'])
            habit.reminder_time = reminder_time
        except:
            pass

    db.session.commit()

    return jsonify({
        'message': 'Habit updated successfully',
        'habit': habit.to_dict()
    }), 200

@habits_bp.route('/<int:habit_id>', methods=['DELETE'])
@token_required
def delete_habit(current_user, habit_id):
    """Delete a habit (soft delete via active flag)"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    habit.active = False
    db.session.commit()

    return jsonify({'message': 'Habit deleted successfully'}), 200

@habits_bp.route('/<int:habit_id>/complete', methods=['POST'])
@token_required
def complete_habit(current_user, habit_id):
    """Mark habit as completed today"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    # Get or create today's log
    log = HabitLog.query.filter_by(
        habit_id=habit.id,
        user_id=current_user.id,
        date=date.today()
    ).first()

    if not log:
        log = HabitLog(
            habit_id=habit.id,
            user_id=current_user.id,
            date=date.today(),
            status='completed'
        )
        db.session.add(log)
    else:
        log.status = 'completed'

    db.session.commit()

    # Calculate new streak
    current_streak = StreakEngine.calculate_current_streak(habit.id, current_user.id)

    # Process XP and badges
    xp_result = GamificationEngine.process_completion_xp(current_user.id, habit.id, current_streak)

    # Get streak message
    streak_message = CoachEngine.get_streak_milestone_message(habit.id, current_user.id, current_streak)

    return jsonify({
        'message': 'Habit completed!',
        'status': 'completed',
        'current_streak': current_streak,
        'xp_earned': xp_result['xp_earned'],
        'xp_result': xp_result['xp_result'],
        'badges_unlocked': xp_result['badges_unlocked'],
        'streak_message': streak_message
    }), 200

@habits_bp.route('/<int:habit_id>/skip', methods=['POST'])
@token_required
def skip_habit(current_user, habit_id):
    """Mark habit as skipped today"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    log = HabitLog.query.filter_by(
        habit_id=habit.id,
        user_id=current_user.id,
        date=date.today()
    ).first()

    if not log:
        log = HabitLog(
            habit_id=habit.id,
            user_id=current_user.id,
            date=date.today(),
            status='skipped'
        )
        db.session.add(log)
    else:
        log.status = 'skipped'

    db.session.commit()

    current_streak = StreakEngine.calculate_current_streak(habit.id, current_user.id)

    return jsonify({
        'message': 'Habit skipped.',
        'status': 'skipped',
        'current_streak': current_streak
    }), 200

@habits_bp.route('/<int:habit_id>/miss', methods=['POST'])
@token_required
def miss_habit(current_user, habit_id):
    """Mark habit as missed today"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    log = HabitLog.query.filter_by(
        habit_id=habit.id,
        user_id=current_user.id,
        date=date.today()
    ).first()

    if not log:
        log = HabitLog(
            habit_id=habit.id,
            user_id=current_user.id,
            date=date.today(),
            status='missed'
        )
        db.session.add(log)
    else:
        log.status = 'missed'

    db.session.commit()

    current_streak = StreakEngine.calculate_current_streak(habit.id, current_user.id)

    return jsonify({
        'message': 'Habit marked as missed. Keep going tomorrow!',
        'status': 'missed',
        'current_streak': current_streak
    }), 200

@habits_bp.route('/<int:habit_id>/history', methods=['GET'])
@token_required
def get_habit_history(current_user, habit_id):
    """Get habit history (calendar data)"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()

    if not habit:
        return jsonify({'message': 'Habit not found'}), 404

    days = request.args.get('days', 30, type=int)
    history = StreakEngine.get_habit_history(habit.id, current_user.id, days)

    return jsonify({
        'habit_id': habit.id,
        'history': history
    }), 200
