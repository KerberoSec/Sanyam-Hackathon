# 🤖 HabitFlow with Gemini AI Integration

## Overview

HabitFlow now includes an intelligent AI coaching layer powered by **Google Gemini API**. The AI is not just a feature—it's a core transformation layer that converts raw habit tracking data into personalized, emotionally intelligent coaching insights.

---

## 🧠 AI Architecture

### Three-Layer Design

1. **Backend Analytics (Deterministic)**
   - Streak calculations
   - Completion percentages
   - Consistency scoring
   - Structured data aggregation

2. **AI Service Layer (Intelligent)**
   - Receives structured metrics (not raw DB dumps)
   - Generates human-readable coaching language
   - Provides behavioral insights
   - Emotional and motivational framing

3. **Frontend Presentation (Beautiful)**
   - Displays AI-generated messages
   - Seamless integration with existing UI
   - Mobile-responsive design

---

## 🔧 Setup

### 1. Get Your Gemini API Key

- Visit [https://ai.google.dev](https://ai.google.dev)
- Create a new API key
- Copy your API key

### 2. Update `.env` File

```bash
# In your .env file, add:
GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Install Dependencies

```bash
pip install google-generativeai==0.7.2
```

The requirement is already in `requirements.txt`.

### 4. Run the Application

```bash
docker-compose up
```

---

## 🤖 AI Features

### 1. **Daily Coach Message**
- **Trigger**: User opens dashboard
- **Frequency**: Once per day (cached)
- **Content**: Personalized daily motivation based on:
  - Current streak
  - Completion rate
  - Best performing habits
  - Weak performance areas
- **Example Output**:
  > "You're building strong momentum this week! You're especially consistent on Mondays. Focus on protecting your habit streak on Saturdays where you tend to slip."

### 2. **Weekly AI Summary**
- **Trigger**: User clicks "View Summary" or auto-loads on analytics page
- **Frequency**: Once per week
- **Content**: Interprets weekly trends and provides:
  - Performance celebration
  - Pattern recognition
  - Actionable recommendations
  - Behavioral psychology insights
- **Example Output**:
  > "Great effort this week! You completed 85% of your habits. Your strongest performance is on weekdays (90% completion), so consider adjusting weekend habits to be more achievable. Try habit stacking your weekend goals with existing activities like morning coffee or evening wind-down."

### 3. **Mood-Habit Correlation Insights**
- **Trigger**: User logs mood entries
- **Content**: AI analyzes mood vs completion:
  - Correlations between mood and habit completion
  - Emotional impact of habits
  - Psychological insights
- **Example Output**:
  > "You're 68% happier on workout days! Exercise is clearly boosting your emotional wellbeing. Consider when you're feeling down that starting with just 5 minutes of movement can shift your mood."

### 4. **Smart Habit Recommendations**
- **Trigger**: User starts onboarding or requests suggestions
- **Content**: AI generates 3 micro-habits based on:
  - User stated goal
  - Current habit capacity
  - Performance patterns
  - Behavioral psychology principles
- **Returns JSON with**:
  - Specific habit action
  - Psychological reason
  - Recommended frequency
  - Time estimate

---

## 🏗️ Code Structure

### Service Module: `services/ai_coach.py`

```python
# Main functions you can call:
AICoachService.generate_daily_coach_message(user_stats, habits)
AICoachService.generate_weekly_summary(user_stats, habits, weekly_data)
AICoachService.analyze_mood_habit_correlation(moods, completion_rate)
AICoachService.generate_habit_recommendations(goal, stats, habits)
```

### Routes: `routes/ai.py`

```
GET  /api/ai/daily-message         → Today's coaching message
GET  /api/ai/weekly-summary        → Weekly performance review
POST /api/ai/habit-recommendations → Smart habit suggestions
GET  /api/ai/mood-insights         → Mood-habit correlation
GET  /api/ai/health                → AI service status check
```

### Database: `AIMessage` Model

```python
class AIMessage(db.Model):
    id: int
    user_id: int
    message_type: str  # daily, weekly, recommendation, mood_insight
    content: Text
    date: Date
    generated_at: DateTime
    cached: Boolean
```

Caching prevents API overuse and keeps costs low.

---

## 💾 Caching Strategy

### Daily Messages
- **Cache Duration**: 24 hours
- **Logic**: Check if cached message exists for today. If yes, return it. If no, generate new one with API.
- **Cost Savings**: Reduces API calls by 95%+ for active users

### Weekly Summaries
- **Cache Duration**: 7 days
- **Trigger**: On-demand or scheduled
- **Cost Savings**: ~4 API calls per user per month vs. unlimited refreshes

### Mood Insights
- **Cache Duration**: Until mood data changes
- **Trigger**: After user logs new mood

---

## 🔐 Security

### API Key Protection

✅ **Server-Side Only**
- API key stored in `.env`
- Never exposed to frontend
- All Gemini API calls happen in Flask backend

✅ **No JavaScript Key Access**
```javascript
// NEVER do this:
const response = await fetch('https://generativeai.googleapis.com/...', {
    headers: { 'Authorization': `Bearer ${GEMINI_API_KEY}` }
});

// ALWAYS do this:
const response = await fetch('/api/ai/daily-message'); // Backend handles API call
```

✅ **Rate Limiting**
- Check cache before API call
- Prevent repeated refreshes
- Monitor API usage

---

## 🚀 API Workflow

### Daily Message Flow

1. **User loads dashboard**
2. **Frontend calls**: `GET /api/ai/daily-message`
3. **Backend checks**: Is there a cached message from today?
4. **If YES**: Return cached message (instant response)
5. **If NO**: Call Gemini API with structured prompt
6. **Gemini returns**: Personalized coaching text
7. **Backend caches**: Store in `AIMessage` table
8. **Frontend displays**: Beautiful alert box with message

### Weekly Summary Flow

1. **User views analytics**
2. **Frontend calls**: `GET/api/ai/weekly-summary`
3. **Backend aggregates**: Weekly stats (completion %, best day, etc.)
4. **Calls Gemini**: With formatted prompt
5. **AI interprets**: Converts numbers to behavioral insights
6. **Returns**: Structured weekly narrative
7. **Frontend displays**: Card with summary and "Refresh" button

---

## 🎯 Prompt Engineering

Each AI call uses carefully crafted prompts with:

1. **Role Definition**
   > "You are a supportive habit coach..."

2. **Context Data**
   > Raw metrics (streaks, completions, consistency scores)

3. **Behavioral Instructions**
   > "Celebrate wins, identify patterns, suggest psychology-based habits..."

4. **Tone & Style**
   > "Speak in an encouraging, friendly tone. Keep responses to 2-3 sentences."

5. **Format Specifications**
   > "Return JSON for habit recommendations" or "Generate 3-sentence summary"

---

## 📊 Example Interactions

### Scenario 1: User Opens Dashboard

**Backend gathers**:
- 5-day current streak
- 82% completion rate this week
- Worst day: Saturday (45% completion)
- Best day: Monday (95% completion)

**Prompt to Gemini**:
```
You are a supportive habit coach...
User Stats: 5-day streak, 82% completion, worst Saturday, best Monday
Generate a 2-3 sentence daily message that:
1. Celebrates current streak
2. Identifies pattern (weekend weakness)
3. Suggests action
```

**Gemini Response**:
```
"You're on a great 5-day streak! 🔥 I've noticed you're strongest on Mondays but struggle on Saturdays.
This weekend, try habit stacking your goals with something you already enjoy—like doing morning yoga
with your coffee. Small adjustments compound."
```

---

### Scenario 2: User Requests Habit Suggestions

**User Input**: "I want to improve my health"

**Backend gathers**:
- Current habits: [Workout, Meditation, Sleep tracking]
- Completion rate: 75%
- Time commitment: 45 min/day average
- Best time: Morning

**Prompt to Gemini**:
```
Recommend 3 micro-habits for health improvement that:
- Fit user's current 45-min/day capacity
- Complement existing habits
- Align with user's morning preference
- Are specific and measurable
Return JSON with habit, why, frequency, duration
```

**Gemini Response**:
```json
[
  {
    "habit": "Drink 1 glass of water immediately after waking",
    "why": "Hydration improves energy and focus—perfect morning boost",
    "frequency": "daily",
    "duration": "1 min"
  },
  {
    "habit": "5-min stretching before workout",
    "why": "Bodydubling effect—primes nervous system for exercise",
    "frequency": "daily",
    "duration": "5 min"
  },
  {
    "habit": "Log sleep quality (1-10 scale) in notes",
    "why": "Awareness drives behavior—you'll notice sleep impact on mood",
    "frequency": "daily",
    "duration": "2 min"
  }
]
```

---

## ⚡ Error Handling

### Graceful Fallbacks

If Gemini API fails:

```python
if not AICoachService.is_available():
    return {
        'message': AICoachService.FALLBACK_MESSAGES['daily'],
        'cached': False,
        'error': 'API not configured'
    }
```

**Fallback behavior**:
- User still gets motivation (from hardcoded library)
- No crash or broken UX
- Logs error for debugging
- Retries next time user loads

---

## 🔄 Request/Response Examples

### Get Daily Message

**Request**:
```bash
GET /api/ai/daily-message
Header: Authorization: Bearer <token>
```

**Response**:
```json
{
  "message": "You're on a great 5-day streak! I've noticed...",
  "cached": true,
  "generated_at": "2024-02-13T10:30:00Z"
}
```

### Get Weekly Summary

**Request**:
```bash
GET /api/ai/weekly-summary
Header: Authorization: Bearer <token>
```

**Response**:
```json
{
  "summary": "Great effort this week! You completed 85% of...",
  "generated_at": "2024-02-13T10:30:00Z"
}
```

### Get Habit Recommendations

**Request**:
```bash
POST /api/ai/habit-recommendations
Header: Authorization: Bearer <token>
Body: { "goal": "better focus" }
```

**Response**:
```json
{
  "recommendations": [
    { "habit": "...", "why": "...", "frequency": "...", "duration": "..." },
    ...
  ],
  "goal": "better focus",
  "generated_at": "2024-02-13T10:30:00Z"
}
```

---

## 📈 Metrics & Analytics

### AI Usage Dashboard (Future)

Track:
- API calls per day
- Cache hit rate
- Response times
- User engagement with AI features
- Cost per user

---

## 🎓 Learning Value

This integration demonstrates:

1. **AI Integration**: Proper API key handling, prompt engineering
2. **Service Architecture**: Separating AI logic into dedicated service
3. **Caching Strategy**: Reducing API costs and latency
4. **Security**: Server-side API calls, no client-side exposure
5. **Error Handling**: Graceful fallbacks
6. **UX Design**: Making AI feel natural and helpful

---

## 🚀 Production Ready

The AI integration is production-ready with:

✅ Error handling
✅ API key security
✅ Caching strategy
✅ Fallback messages
✅ Rate limiting
✅ Structured prompts
✅ Response validation
✅ Logging

---

## 📝 Next Steps

1. **Add your Gemini API key** to `.env`
2. **Run the application**: `docker-compose up`
3. **Create an account** and add habits
4. **Watch AI coaching messages** appear on dashboard
5. **Check weekly summary** in analytics
6. **Request habit recommendations** via API

---

## 🔗 Resources

- [Google Generative AI Docs](https://ai.google.dev/docs)
- [Gemini API Reference](https://ai.google.dev/api/python/google/generativeai)
- [Prompt Engineering Guide](https://ai.google.dev/docs/guides/prompt_eng)

---

**HabitFlow + Gemini = Intelligent Habit Tracking** 🚀
