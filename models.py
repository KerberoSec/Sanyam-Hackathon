from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    xp_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    habits = db.relationship('Habit', backref='user', lazy=True, cascade='all, delete-orphan')
    habit_logs = db.relationship('HabitLog', backref='user', lazy=True, cascade='all, delete-orphan')
    moods = db.relationship('Mood', backref='user', lazy=True, cascade='all, delete-orphan')
    badges = db.relationship('Badge', secondary='user_badges', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'xp_points': self.xp_points,
            'level': self.level,
            'created_at': self.created_at.isoformat()
        }

class Habit(db.Model):
    __tablename__ = 'habits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), default='general')
    icon = db.Column(db.String(50), default='✨')
    color = db.Column(db.String(20), default='primary')
    frequency = db.Column(db.JSON, default=lambda: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
    reminder_time = db.Column(db.Time, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'icon': self.icon,
            'color': self.color,
            'frequency': self.frequency,
            'reminder_time': self.reminder_time.strftime('%H:%M') if self.reminder_time else None,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }

class HabitLog(db.Model):
    __tablename__ = 'habit_logs'

    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='missed')  # completed, skipped, missed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('habit_id', 'date', name='uq_habit_date'),)

    def to_dict(self):
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'date': self.date.isoformat(),
            'status': self.status
        }

class Mood(db.Model):
    __tablename__ = 'moods'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    mood = db.Column(db.String(20), nullable=False)  # happy, neutral, sad
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='uq_mood_date'),)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'mood': self.mood,
            'note': self.note
        }

class Badge(db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }

class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False, index=True)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),)

    def to_dict(self):
        return {
            'id': self.id,
            'badge_id': self.badge_id,
            'earned_at': self.earned_at.isoformat()
        }

class AIMessage(db.Model):
    __tablename__ = 'ai_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message_type = db.Column(db.String(50), nullable=False)  # daily, weekly, recommendation, mood_insight
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, default=date.today, index=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    cached = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'message_type', 'date', name='uq_user_message_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'message_type': self.message_type,
            'content': self.content,
            'date': self.date.isoformat(),
            'generated_at': self.generated_at.isoformat()
        }
