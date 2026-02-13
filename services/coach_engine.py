from models import HabitLog, Habit, Mood, db
from datetime import datetime, date, timedelta

class CoachEngine:
    """Service for generating motivational messages and insights"""

    MOTIVATIONAL_QUOTES = [
        "Small steps lead to big changes.",
        "Your future self will thank you.",
        "Consistency is the gateway to mastery.",
        "You're building momentum!",
        "Every day is a fresh start.",
        "Progress over perfection.",
        "You've got this! 💪",
        "Building better habits, one day at a time.",
        "Your dedication is inspiring.",
        "Showing up is half the battle.",
    ]

    STREAK_MESSAGES = {
        3: "🔥 3-day streak! You're on fire!",
        7: "🌟 Week 1 complete! What a legend!",
        14: "🚀 Two weeks! You're unstoppable!",
        30: "👑 One month! You're a habit master!",
        60: "⚡ 60 days! This is incredible!",
        100: "💯 100 days! You're a living legend!",
    }

    COMEBACK_MESSAGES = [
        "Missing a day happens. Let's restart fresh today.",
        "Your streak may have reset, but your progress remains.",
        "This is your chance to start a new streak!",
        "Everyone stumbles. The important thing is getting back up.",
        "Today is a new opportunity.",
    ]

    @staticmethod
    def get_dashboard_message(user_id):
        """Generate a personalized dashboard message"""
        from services.streak_engine import StreakEngine

        habits = Habit.query.filter_by(user_id=user_id, active=True).all()

        if not habits:
            return "Create your first habit to get started!"

        # Get stats
        stats = StreakEngine.calculate_stats_for_user(user_id)

        if stats['total_habits'] == 0:
            return "Create your first habit to get started!"

        # Analyze performance
        if stats['combined_streak'] == 0:
            return "Let's start fresh today! Pick a habit and complete it."

        if stats['combined_streak'] > 0:
            return f"You're crushing it! {stats['combined_streak']} combined streak days. Keep it up! 🔥"

        return "Every day is an opportunity to build better habits."

    @staticmethod
    def get_streak_milestone_message(habit_id, user_id, current_streak):
        """Generate message for streak milestones"""
        from services.streak_engine import StreakEngine

        if current_streak in CoachEngine.STREAK_MESSAGES:
            return CoachEngine.STREAK_MESSAGES[current_streak]

        if current_streak % 7 == 0 and current_streak > 0:
            return f"🎉 {current_streak} days! You're on an amazing streak!"

        return None

    @staticmethod
    def detect_streak_drop(user_id):
        """Detect if user has had recent missed days"""
        habits = Habit.query.filter_by(user_id=user_id, active=True).all()

        if not habits:
            return None

        # Check last 7 days
        start_date = date.today() - timedelta(days=7)
        recent_logs = HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.date >= start_date
        ).all()

        if not recent_logs:
            return None

        missed_count = sum(1 for log in recent_logs if log.status == 'missed')
        total_expected = len(habits) * 7

        if missed_count > (total_expected * 0.3):  # More than 30% missed
            return {
                'type': 'streak_drop',
                'message': CoachEngine.COMEBACK_MESSAGES[0],
                'missed_count': missed_count,
                'severity': 'high' if missed_count > (total_expected * 0.5) else 'medium'
            }

        return None

    @staticmethod
    def detect_inactivity(user_id):
        """Detect if user hasn't logged anything recently"""
        last_log = HabitLog.query.filter_by(user_id=user_id).order_by(HabitLog.date.desc()).first()

        if not last_log:
            return None

        days_since_last_log = (date.today() - last_log.date).days

        if days_since_last_log >= 3:
            return {
                'type': 'inactivity',
                'message': f"We haven't seen you in {days_since_last_log} days. Let's get back on track!",
                'days_since': days_since_last_log
            }

        return None

    @staticmethod
    def analyze_mood_habit_correlation(user_id):
        """Analyze correlation between mood and habit completion"""
        last_30_days = date.today() - timedelta(days=30)

        moods = Mood.query.filter(
            Mood.user_id == user_id,
            Mood.date >= last_30_days
        ).all()

        habit_logs = HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.date >= last_30_days
        ).all()

        if not moods or not habit_logs:
            return None

        # Create mood map
        mood_map = {m.date: m.mood for m in moods}

        happy_days = 0
        happy_completed_days = 0
        completed_days = 0

        for log in habit_logs:
            if log.status == 'completed':
                completed_days += 1
                if log.date in mood_map and mood_map[log.date] == 'happy':
                    happy_completed_days += 1

        happy_day_count = sum(1 for m in moods if m.mood == 'happy')

        if happy_day_count > 0:
            correlation = (happy_completed_days / happy_day_count) * 100
            return {
                'happy_day_completion': int(correlation),
                'message': f"You're {int(correlation)}% more likely to complete habits on happy days!"
            }

        return None

    @staticmethod
    def get_best_day(user_id):
        """Find the day of week user performs best"""
        last_30_days = date.today() - timedelta(days=30)

        logs = HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.date >= last_30_days,
            HabitLog.status == 'completed'
        ).all()

        if not logs:
            return None

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = {i: 0 for i in range(7)}

        for log in logs:
            day_counts[log.date.weekday()] += 1

        best_day_num = max(day_counts, key=day_counts.get)
        best_day_name = day_names[best_day_num]

        return {
            'day': best_day_name,
            'completions': day_counts[best_day_num],
            'message': f"You're strongest on {best_day_name}s! 💪"
        }

    @staticmethod
    def get_all_insights(user_id):
        """Get all available insights for user"""
        insights = []

        # Streak drop
        streak_drop = CoachEngine.detect_streak_drop(user_id)
        if streak_drop:
            insights.append(streak_drop)

        # Inactivity
        inactivity = CoachEngine.detect_inactivity(user_id)
        if inactivity:
            insights.append(inactivity)

        # Mood correlation
        mood_correlation = CoachEngine.analyze_mood_habit_correlation(user_id)
        if mood_correlation:
            insights.append({
                'type': 'mood_correlation',
                'message': mood_correlation['message'],
                'data': mood_correlation
            })

        # Best day
        best_day = CoachEngine.get_best_day(user_id)
        if best_day:
            insights.append({
                'type': 'best_day',
                'message': best_day['message'],
                'data': best_day
            })

        return insights

    @staticmethod
    def get_random_quote():
        """Get a random motivational quote"""
        import random
        return random.choice(CoachEngine.MOTIVATIONAL_QUOTES)
