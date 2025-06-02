import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

from svpg.init_db import initialize_database


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app(config_name='default'):
    from app.config import config

    app = Flask(
        __name__,
        static_folder=os.path.join(BASE_DIR, '..', 'static'),
        static_url_path='/static'
    )

    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    
    # Setup login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '이 페이지에 접근하려면 로그인이 필요합니다.'
    login_manager.login_message_category = 'info'
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.restaurant import restaurant_bp
    from svpg.reviews.routes import reviews_bp
    from svpg.users.routes import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(users_bp)
    
    # Create database tables if they don't exist
    with app.app_context():
        initialize_database()
        db.create_all()
    
    return app