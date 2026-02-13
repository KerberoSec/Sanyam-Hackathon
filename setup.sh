#!/bin/bash

# HabitFlow Quick Setup Script
# This script sets up the development environment

echo "🚀 HabitFlow - Habit Tracker Setup"
echo "=================================="
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate || . venv\Scripts\activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file
echo "⚙️  Creating .env file..."
cp .env.example .env

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your MySQL credentials"
echo "2. Create the MySQL database:"
echo "   mysql -u root -p"
echo "   CREATE DATABASE habit_tracker DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo ""
echo "3. Run the application:"
echo "   python app.py"
echo ""
echo "4. Open http://localhost:5000 in your browser"
echo ""
echo "Happy habit tracking! 🔥"
