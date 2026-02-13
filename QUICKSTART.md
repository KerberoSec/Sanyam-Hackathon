# ⚡ HabitFlow - Quick Start Guide

Get HabitFlow running in **5 minutes**!

## Prerequisites

- Python 3.9+
- MySQL 5.7+
- Windows/Mac/Linux

## 🚀 Quick Setup

### Step 1: Set up MySQL Database (1 minute)

```bash
# Open MySQL
mysql -u root -p

# Create database
CREATE DATABASE habit_tracker DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Step 2: Setup Python Environment (2 minutes)

**Windows:**
```bash
cd habit-tracker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd habit-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure Environment (1 minute)

Copy `.env.example` to `.env`:

**Windows:**
```bash
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

Edit `.env` with your MySQL password:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/habit_tracker
```

### Step 4: Run Application (1 minute)

```bash
python app.py
```

Open your browser and visit: **http://localhost:5000**

## 🎯 Quick Demo

1. **Register** an account
2. **Create** your first habit (e.g., "Morning Meditation")
3. **Log** activity (Complete, Skip, or Miss)
4. **Watch** your streak grow and XP accumulate
5. **Track** your mood and view insights

## 🛠️ Common Issues

### MySQL Error
```
Check your DATABASE_URL in .env
Make sure MySQL is running
Verify username/password
```

### Port 5000 Already in Use
```bash
python app.py --port 5001
```

### Module Not Found
```bash
pip install -r requirements.txt  # Re-run if you missed this
```

## 📚 Next Steps

- Read the [full README.md](README.md) for detailed documentation
- Check out the [API endpoints](README.md#-api-endpoints)
- Learn about [gamification](README.md#-gamification-system)
- Deploy to [Heroku](README.md#-deployment)

## 💡 Features Overview

| Feature | Description |
|---------|-------------|
| 🔥 Streaks | Track consecutive days of habit completion |
| 📊 Analytics | Beautiful charts and insights |
| 🎮 Gamification | Earn XP and unlock badges |
| 😊 Mood Tracking | Log mood and see correlations |
| 🤖 Smart Coach | Get personalized suggestions |
| 🌙 Dark Mode | Easy on the eyes |
| 📱 Mobile Ready | Fully responsive design |

## 🚀 Future Commands

**Development Mode:**
```bash
python app.py
```

**Production Mode:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Reset Database:**
```bash
flask shell
>>> from models import db
>>> db.drop_all()
>>> db.create_all()
>>> exit()
```

## 🎉 You're Done!

Start building better habits! If you need help, check the README.md or open an issue on GitHub.

Happy tracking! 🚀
