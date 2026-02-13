from models import User, UserBadge, Badge, HabitLog, db
from datetime import datetime

class GamificationEngine:
    """Service for XP, levels, badges"""

    # XP rewards
    XP_COMPLETION = 10
    XP_STREAK_7 = 50
    XP_STREAK_14 = 100
    XP_STREAK_30 = 200

    @staticmethod
    def add_xp(user_id, amount, reason=""):
        """Add XP to user and return level up info"""
        user = User.query.get(user_id)
        if not user:
            return None

        old_level = user.level
        user.xp_points += amount
        new_level = user.xp_points // 100
        user.level = new_level
        db.session.commit()

        level_up = new_level > old_level
        return {
            'xp': user.xp_points,
            'level': user.level,
            'level_up': level_up,
            'old_level': old_level,
            'new_level': new_level
        }

    @staticmethod
    def get_xp_progress(user_id):
        """Get XP progress to next level"""
        user = User.query.get(user_id)
        if not user:
            return None

        xp_in_level = user.xp_points % 100
        return {
            'current_xp': user.xp_points,
            'level': user.level,
            'xp_to_next_level': 100 - xp_in_level,
            'xp_in_current_level': xp_in_level,
            'progress_percent': int((xp_in_level / 100) * 100)
        }

    @staticmethod
    def unlock_badge(user_id, badge_name, badge_description="", badge_icon="🏆"):
        """Unlock a badge for user if they don't already have it"""
        user = User.query.get(user_id)
        if not user:
            return None

        # Check if badge exists
        badge = Badge.query.filter_by(name=badge_name).first()

        if not badge:
            # Create new badge
            badge = Badge(name=badge_name, description=badge_description, icon=badge_icon)
            db.session.add(badge)
            db.session.flush()

        # Check if user already has this badge
        existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
        if existing:
            return None  # Already unlocked

        # Add badge to user
        user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
        db.session.add(user_badge)
        db.session.commit()

        return badge.to_dict()

    @staticmethod
    def check_and_unlock_badges(user_id, current_streak, total_completions):
        """Check for badge milestones and unlock them"""
        unlocked = []

        badges_to_check = [
            (7, "First Week", "Complete a habit for 7 days straight", "🔥"),
            (14, "Two Weeks Strong", "Complete a habit for 14 days straight", "💪"),
            (30, "Monthly Master", "Complete a habit for 30 days straight", "👑"),
            (100, "Centennial", "Complete 100 habit logs", "💯"),
            (365, "Yearly Champion", "Complete 365 habit logs", "🎯"),
        ]

        if current_streak > 0:
            for threshold, badge_name, description, icon in badges_to_check:
                if current_streak >= threshold:
                    result = GamificationEngine.unlock_badge(user_id, badge_name, description, icon)
                    if result:
                        unlocked.append(result)

        # Total completions badges
        completion_badges = [
            (10, "Getting Started", "Log 10 completions", "🚀"),
            (50, "Habit Builder", "Log 50 completions", "🏗️"),
            (100, "Consistency King", "Log 100 completions", "👑"),
        ]

        for threshold, badge_name, description, icon in completion_badges:
            if total_completions >= threshold:
                result = GamificationEngine.unlock_badge(user_id, badge_name, description, icon)
                if result:
                    unlocked.append(result)

        return unlocked

    @staticmethod
    def get_user_badges(user_id):
        """Get all badges earned by user"""
        user_badges = UserBadge.query.filter_by(user_id=user_id).all()
        return [
            {
                'badge': Badge.query.get(ub.badge_id).to_dict(),
                'earned_at': ub.earned_at.isoformat()
            }
            for ub in user_badges
        ]

    @staticmethod
    def process_completion_xp(user_id, habit_id, current_streak):
        """Process XP rewards for completing a habit"""
        xp_earned = GamificationEngine.XP_COMPLETION

        # Bonus XP for streak milestones
        if current_streak == 7:
            xp_earned += GamificationEngine.XP_STREAK_7
        elif current_streak == 14:
            xp_earned += GamificationEngine.XP_STREAK_14
        elif current_streak == 30:
            xp_earned += GamificationEngine.XP_STREAK_30
        elif current_streak % 7 == 0 and current_streak > 0:
            xp_earned += GamificationEngine.XP_STREAK_7

        result = GamificationEngine.add_xp(user_id, xp_earned)

        # Check for badge unlocks
        total_completions = HabitLog.query.filter_by(user_id=user_id, status='completed').count()
        badges = GamificationEngine.check_and_unlock_badges(user_id, current_streak, total_completions)

        return {
            'xp_earned': xp_earned,
            'xp_result': result,
            'badges_unlocked': badges
        }
