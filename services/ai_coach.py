import os
import json
from datetime import datetime, date
import google.generativeai as genai
from functools import wraps

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AICoachService:
    """Service to integrate Gemini API for intelligent habit coaching"""

    MODEL_NAME = "gemini-2.0-flash"

    # Fallback messages if API fails
    FALLBACK_MESSAGES = {
        'daily': "Keep the momentum going! Every daily completion builds your foundation of consistency.",
        'weekly': "Great effort this week! You're building the habit loops that stick. Stay focused on your goals.",
        'recommendation': "Consider adding a micro-habit that complements your existing routine. Small changes compound!"
    }

    @staticmethod
    def is_available():
        """Check if Gemini API is configured"""
        return GEMINI_API_KEY is not None

    @staticmethod
    def generate_daily_coach_message(user_stats, user_habits):
        """
        Generate a daily coaching message based on user stats.
        Called once per day and cached in database.
        """
        if not AICoachService.is_available():
            return {'message': AICoachService.FALLBACK_MESSAGES['daily'], 'error': 'API not configured'}

        try:
            # Build context string from stats
            context = AICoachService._build_user_context(user_stats, user_habits)

            prompt = f"""You are a supportive, encouraging habit coach. Your role is to provide personalized, brief daily motivation to help users build consistency.

User Current Stats:
{context}

Based on these stats, generate a SHORT, encouraging daily message (2-3 sentences max) that:
1. Acknowledges their current progress
2. Identifies one specific area to focus on today
3. Provides one actionable tip

Keep the tone warm, friendly, and motivational. Avoid generic platitudes."""

            model = genai.GenerativeModel(AICoachService.MODEL_NAME)
            response = model.generate_content(prompt)

            message = response.text.strip() if response.text else AICoachService.FALLBACK_MESSAGES['daily']

            return {
                'message': message,
                'generated_at': datetime.utcnow().isoformat(),
                'model': AICoachService.MODEL_NAME
            }
        except Exception as e:
            print(f"AI Coach Error: {str(e)}")
            return {
                'message': AICoachService.FALLBACK_MESSAGES['daily'],
                'error': str(e)
            }

    @staticmethod
    def generate_weekly_summary(user_stats, user_habits, weekly_data):
        """
        Generate a detailed weekly performance summary with insights and recommendations.
        """
        if not AICoachService.is_available():
            return {'summary': AICoachService.FALLBACK_MESSAGES['weekly'], 'error': 'API not configured'}

        try:
            context = AICoachService._build_user_context(user_stats, user_habits)
            weekly_context = AICoachService._build_weekly_context(weekly_data)

            prompt = f"""You are a habit psychologist and behavioral coach. Generate a weekly performance review that transforms numbers into insights.

User Profile:
{context}

Weekly Performance:
{weekly_context}

Create a structured weekly summary (3-4 sentences) that:
1. Celebrates wins and acknowledges challenges
2. Identifies the user's strongest and weakest days (pattern recognition)
3. Provides ONE specific, actionable recommendation
4. Builds emotional connection ("you're building momentum", etc.)

Be encouraging but honest. Use behavioral psychology language."""

            model = genai.GenerativeModel(AICoachService.MODEL_NAME)
            response = model.generate_content(prompt)

            summary = response.text.strip() if response.text else AICoachService.FALLBACK_MESSAGES['weekly']

            return {
                'summary': summary,
                'generated_at': datetime.utcnow().isoformat(),
                'model': AICoachService.MODEL_NAME
            }
        except Exception as e:
            print(f"AI Coach Error: {str(e)}")
            return {
                'summary': AICoachService.FALLBACK_MESSAGES['weekly'],
                'error': str(e)
            }

    @staticmethod
    def generate_habit_recommendations(user_goal, user_stats, existing_habits):
        """
        Generate smart habit recommendations based on user's stated goal and behavior pattern.
        """
        if not AICoachService.is_available():
            return {'recommendations': [], 'error': 'API not configured'}

        try:
            context = AICoachService._build_user_context(user_stats, existing_habits)
            habits_list = ', '.join([h['title'] for h in existing_habits]) if existing_habits else 'None yet'

            prompt = f"""You are a habit formation expert. Recommend EXACTLY 3 small, micro-habits that fit the user's goal and current capacity.

User Goal: {user_goal}
Current Stats:
{context}

Existing Habits: {habits_list}

Generate 3 micro-habit recommendations in JSON format (no extra text):
[
  {{"habit": "specific action", "why": "psychological reason in 1 sentence", "frequency": "daily/3x per week", "duration": "estimated time"}},
  ...
]

Rules:
- Each habit should take <5 minutes
- Avoid duplicating existing habits
- Prioritize habits aligned with behavioral psychology (habit stacking, body doubling, etc.)
- Focus on consistency over intensity
- Make habits SPECIFIC and measurable"""

            model = genai.GenerativeModel(AICoachService.MODEL_NAME)
            response = model.generate_content(prompt)

            response_text = response.text.strip() if response.text else "[]"

            # Extract JSON from response
            try:
                # Remove markdown code blocks if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                recommendations = json.loads(response_text.strip())
            except json.JSONDecodeError:
                recommendations = []

            return {
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat(),
                'model': AICoachService.MODEL_NAME
            }
        except Exception as e:
            print(f"AI Coach Error: {str(e)}")
            return {
                'recommendations': [],
                'error': str(e)
            }

    @staticmethod
    def analyze_mood_habit_correlation(user_moods, user_habits_completion):
        """
        Analyze the correlation between mood and habit completion.
        AI translates statistics into emotional insights.
        """
        if not AICoachService.is_available():
            return {'insight': 'Track your mood to unlock AI insights', 'error': 'API not configured'}

        try:
            # Calculate mood stats
            happy_days = sum(1 for m in user_moods if m['mood'] == 'happy')
            sad_days = sum(1 for m in user_moods if m['mood'] == 'sad')
            total_days = len(user_moods)

            if total_days == 0:
                return {'insight': 'Log more moods for better insights', 'error': 'Insufficient data'}

            happy_percent = (happy_days / total_days) * 100

            prompt = f"""You are an emotional intelligence coach analyzing habit-mood correlations.

Mood Data:
- Happy days: {happy_days}/{total_days} ({happy_percent:.0f}%)
- Sad days: {sad_days}/{total_days}
- Habit completion rate: {user_habits_completion:.0f}%

Generate a 2-3 sentence insight that:
1. Explains the mood-habit connection
2. Provides emotional validation
3. Suggests one micro-action to improve mood through habits

Be warm and psychological, not clinical."""

            model = genai.GenerativeModel(AICoachService.MODEL_NAME)
            response = model.generate_content(prompt)

            insight = response.text.strip() if response.text else "Your mood and habits are interconnected. Keep tracking to discover patterns."

            return {
                'insight': insight,
                'happy_percent': happy_percent,
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"AI Coach Error: {str(e)}")
            return {
                'insight': "Keep tracking your mood and habits to unlock personalized insights.",
                'error': str(e)
            }

    # Helper methods
    @staticmethod
    def _build_user_context(user_stats, habits):
        """Build structured context string from user statistics"""
        context_lines = [
            f"Total Habits: {user_stats.get('total_habits', 0)}",
            f"Combined Streak: {user_stats.get('combined_streak', 0)} days",
            f"Total Completions: {user_stats.get('total_completions', 0)}",
            f"Consistency Score: {user_stats.get('consistency_score', 0)}%",
            f"User Level: {user_stats.get('level', 1)}",
        ]

        if habits:
            context_lines.append(f"Active Habits: {', '.join([h.get('title', 'Unnamed') for h in habits[:5]])}")

        return '\n'.join(context_lines)

    @staticmethod
    def _build_weekly_context(weekly_data):
        """Build structured context from weekly data"""
        context_lines = []

        for day in weekly_data:
            rate = day.get('rate', 0)
            completed = day.get('completed', 0)
            context_lines.append(f"{day.get('day', 'Unknown')}: {completed} completed ({rate}%)")

        return '\n'.join(context_lines)
