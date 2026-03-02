# 🚀 HabitFlow - Your Personal Habit Tracker

Build better habits, one day at a time. HabitFlow is a beautiful, polished habit tracking application that combines gamification, analytics, and emotional UX to help you achieve consistency and personal growth.

## ✨ Features

- **🔥 Streak Tracking**: Watch your streaks grow and celebrate consistency
- **📊 Analytics Dashboard**: Deep insights into your habits and patterns
- **🎮 Gamification**: Earn XP, unlock badges, and climb levels
- **😊 Mood Tracking**: Connect your habits with emotional wellbeing
- **🤖 Smart Coach**: Personalized insights and motivational messages
- **📱 Fully Responsive**: Works beautifully on desktop, tablet, and mobile
- **🌙 Dark Mode**: Easy on the eyes, any time of day
- **✨ Smooth Animations**: Delightful interactions and confetti celebrations

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT authentication
- **MySQL** - Database
- **Flask-CORS** - Cross-origin requests

### Frontend
- **HTML5** - Markup
- **Bootstrap 5** - CSS framework
- **Chart.js** - Analytics charts
- **Vanilla JavaScript** - Interactivity
- **Canvas Confetti** - Celebrations

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- MySQL 5.7 or higher
- Git

### Step 1: Clone and Setup

```bash
cd habit-tracker
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Database

Create a `.env` file in the project root:

```env
FLASK_ENV=development
FLASK_APP=app.py
DATABASE_URL=mysql+pymysql://root:password@localhost/habit_tracker
JWT_SECRET_KEY=your-secret-key-here-change-in-production
SECRET_KEY=your-app-secret-key-here
```

### Step 4: Create MySQL Database

```bash
mysql -u root -p
CREATE DATABASE habit_tracker DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Step 5: Initialize Database

```bash
flask shell
>>> from models import db, Badge
>>> db.create_all()
>>>
>>> # Create default badges
>>> default_badges = [
...     Badge(name='First Week', description='Complete a habit for 7 days straight', icon='🔥'),
...     Badge(name='Two Weeks Strong', description='Complete a habit for 14 days straight', icon='💪'),
...     Badge(name='Monthly Master', description='Complete a habit for 30 days straight', icon='👑'),
...     Badge(name='Centennial', description='Complete 100 habit logs', icon='💯'),
...     Badge(name='Yearly Champion', description='Complete 365 habit logs', icon='🎯'),
... ]
>>> db.session.add_all(default_badges)
>>> db.session.commit()
>>> exit()
```

### Step 6: Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser!

## 📂 Project Structure

```
habit-tracker/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # SQLAlchemy models
├── database.sql          # Database schema
│
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── habits.py         # Habit CRUD routes
│   ├── analytics.py      # Analytics routes
│   └── mood.py           # Mood tracking routes
│
├── services/
│   ├── streak_engine.py  # Streak calculation logic
│   ├── gamification.py   # XP and badge logic
│   └── coach_engine.py   # AI coach insights
│
├── templates/
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   └── dashboard.html    # Main dashboard
│
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── app.js        # JavaScript app logic
│   └── images/           # Images and icons
│
└── requirements.txt      # Python dependencies
```

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Habits
- `GET /api/habits` - Get all habits
- `POST /api/habits` - Create new habit
- `GET /api/habits/<id>` - Get specific habit
- `PUT /api/habits/<id>` - Update habit
- `DELETE /api/habits/<id>` - Delete habit
- `POST /api/habits/<id>/complete` - Log completion
- `POST /api/habits/<id>/skip` - Skip habit
- `POST /api/habits/<id>/miss` - Mark missed
- `GET /api/habits/<id>/history` - Get calendar history

### Analytics
- `GET /api/analytics` - Get dashboard analytics
- `GET /api/analytics/weekly` - Get weekly data
- `GET /api/analytics/monthly` - Get monthly data
- `GET /api/analytics/habit/<id>` - Get habit-specific stats

### Mood
- `POST /api/mood` - Log mood
- `GET /api/mood/today` - Get today's mood
- `GET /api/mood/history` - Get mood history
- `GET /api/mood/analytics` - Get mood analytics
- `GET /api/mood/stats` - Get mood statistics

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    xp_points INT DEFAULT 0,
    level INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Habits Table
```sql
CREATE TABLE habits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    icon VARCHAR(50),
    color VARCHAR(20),
    frequency JSON,
    reminder_time TIME,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Habit Logs Table
```sql
CREATE TABLE habit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    habit_id INT NOT NULL,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('completed', 'skipped', 'missed'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_habit_date (habit_id, date),
    FOREIGN KEY (habit_id) REFERENCES habits(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Moods Table
```sql
CREATE TABLE moods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    mood ENUM('happy', 'neutral', 'sad'),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_mood_date (user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Badges Table
```sql
CREATE TABLE badges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50)
);
```

### User Badges Table
```sql
CREATE TABLE user_badges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    badge_id INT NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_badge (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (badge_id) REFERENCES badges(id)
);
```

## 🎮 Gamification System

### XP Rules
- **+10 XP** for each habit completion
- **+50 XP** for 7-day streak
- **+100 XP** for 14-day streak
- **+200 XP** for 30-day streak

### Levels
```
Level = Total XP // 100
```

### Badges
- 🔥 First Week - 7 days
- 💪 Two Weeks - 14 days
- 👑 Monthly Master - 30 days
- 💯 Centennial - 100 completions
- 🎯 Yearly Champion - 365 completions
- 🚀 Getting Started - 10 completions
- 🏗️ Habit Builder - 50 completions
- 👑 Consistency King - 100 completions

## 🤖 Coach Engine

The Smart Coach detects:
- **Streak drops** - Missed days after good streaks
- **Inactivity** - No logs for 3+ days
- **Mood patterns** - Correlations between mood and habits
- **Best days** - When you perform best

## 🌙 Dark Mode

Toggle dark mode by clicking the menu button. Your preference is saved in localStorage.

## 🔒 Security

- Passwords hashed with Werkzeug
- JWT tokens for authentication
- CORS enabled for API
- Environment variables for sensitive data
- SQL injection prevention via SQLAlchemy ORM

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1920px+)
- Tablet (768px - 1920px)
- Mobile (320px - 768px)

## 🚀 Deployment

### Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Create `runtime.txt`:
```
python-3.10.0
```

3. Deploy:
```bash
heroku login
heroku create your-app-name
heroku addons:create cleardb:ignite
git push heroku main
heroku run flask shell
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 Performance Tips

1. Use indexes on frequently queried columns
2. Cache analytics calculations
3. Implement pagination for large datasets
4. Use lazy loading for images
5. Minify CSS and JavaScript

## 🐛 Troubleshooting

### Database Connection Error
```
Check DATABASE_URL in .env
Ensure MySQL is running
Verify database exists
```

### CORS Issues
```
Flask-CORS is configured
Check request headers and origin
```

### Token Expired
```
Clear localStorage
Log in again
Token expires after 30 days
```

## 🤝 Contributing

Feel free to fork and submit pull requests!

## 📝 License

MIT License - see LICENSE file for details

## 💡 Future Features

- Social features (friend challenges, leaderboards)
- Email reminders and notifications
- Mobile app (React Native)
- Integration with wearables
- Advanced analytics with ML insights
- Community habit library
- Habit templates

## 📞 Support

For issues, please create an issue on GitHub or email support.

---

**Developers:** Arun Kumar, Sourav 

