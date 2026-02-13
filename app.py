from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from config import config
import os
from models import db
from routes.auth import auth_bp
from routes.habits import habits_bp
from routes.analytics import analytics_bp
from routes.mood import mood_bp

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')

    # Configuration
    app.config.from_object(config[config_name])

    # Database
    db.init_app(app)

    # CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(mood_bp)

    # Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/habit/<int:habit_id>')
    def habit_detail(habit_id):
        return render_template('habit_detail.html', habit_id=habit_id)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found'}, 404

    @app.errorhandler(500)
    def server_error(error):
        return {'message': 'Internal server error'}, 500

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(debug=True, host='0.0.0.0', port=5000)
