from datetime import datetime, timedelta, date
from models import HabitLog, Habit

class StreakEngine:
    """Service for calculating habit streaks"""

    @staticmethod
    def calculate_current_streak(habit_id, user_id):
        """
        Calculate current streak for a habit.
        Streak continues as long as habit is completed or skipped (not missed).
        """
        logs = HabitLog.query.filter_by(habit_id=habit_id, user_id=user_id).order_by(HabitLog.date.desc()).all()

        if not logs:
            return 0

        current_streak = 0
        today = date.today()

        for log in logs:
            # Skip logs from the future
            if log.date > today:
                continue

            # If status is "missed", streak is broken
            if log.status == 'missed':
                break

            # If we find a gap in dates (more than 1 day), streak is broken
            if current_streak > 0:
                expected_date = today - timedelta(days=current_streak)
                if log.date != expected_date:
                    break

            current_streak += 1

        return current_streak

    @staticmethod
    def calculate_longest_streak(habit_id, user_id):
        """Calculate longest streak ever achieved for a habit"""
        logs = HabitLog.query.filter_by(habit_id=habit_id, user_id=user_id).order_by(HabitLog.date).all()

        if not logs:
            return 0

        longest_streak = 0
        current_streak = 0
        last_date = None

        for log in logs:
            if log.status == 'missed':
                longest_streak = max(longest_streak, current_streak)
                current_streak = 0
                last_date = None
            else:
                if last_date is None:
                    current_streak = 1
                elif (log.date - last_date).days == 1:
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1

                last_date = log.date

        longest_streak = max(longest_streak, current_streak)
        return longest_streak

    @staticmethod
    def get_total_completions(habit_id, user_id):
        """Get total number of completed days"""
        return HabitLog.query.filter_by(
            habit_id=habit_id,
            user_id=user_id,
            status='completed'
        ).count()

    @staticmethod
    def get_habit_history(habit_id, user_id, days=30):
        """Get habit completion history for the last N days"""
        start_date = date.today() - timedelta(days=days)
        logs = HabitLog.query.filter(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == user_id,
            HabitLog.date >= start_date
        ).order_by(HabitLog.date).all()

        return [
            {
                'date': log.date.isoformat(),
                'status': log.status
            }
            for log in logs
        ]

    @staticmethod
    def get_consistency_score(habit_id, user_id, days=30):
        """
        Calculate consistency score as percentage of completed + skipped days.
        Completed is 100%, skipped is 50%, missed is 0%.
        """
        start_date = date.today() - timedelta(days=days)
        logs = HabitLog.query.filter(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == user_id,
            HabitLog.date >= start_date
        ).all()

        if not logs:
            return 0

        score = 0
        for log in logs:
            if log.status == 'completed':
                score += 100
            elif log.status == 'skipped':
                score += 50

        return int(score / len(logs))

    @staticmethod
    def get_completion_rate(habit_id, user_id, days=30):
        """Calculate percentage of days completed (only counts completed, not skipped)"""
        start_date = date.today() - timedelta(days=days)
        logs = HabitLog.query.filter(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == user_id,
            HabitLog.date >= start_date
        ).all()

        if not logs:
            return 0

        completed = sum(1 for log in logs if log.status == 'completed')
        return int((completed / len(logs)) * 100)

    @staticmethod
    def calculate_stats_for_user(user_id):
        """Calculate overall stats for a user"""
        habits = Habit.query.filter_by(user_id=user_id, active=True).all()

        total_streaks = 0
        total_completions = 0
        total_habits = len(habits)

        for habit in habits:
            total_streaks += StreakEngine.calculate_current_streak(habit.id, user_id)
            total_completions += StreakEngine.get_total_completions(habit.id, user_id)

        return {
            'total_habits': total_habits,
            'total_completions': total_completions,
            'combined_streak': total_streaks
        }
