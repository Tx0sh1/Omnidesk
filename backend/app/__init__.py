from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os

# Global variables for extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
jwt = JWTManager()

def create_app(config_class=Config):
    # Get the base directory (backend folder)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, '../frontend/templates'),
        static_folder=os.path.join(BASE_DIR, 'static')  # Keep backend static for uploads
    )
    
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS for React frontend
    CORS(app, 
         origins=["http://localhost:3000"],  # React dev server
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Flask-Login configuration
    login.login_view = 'auth.login'
    login.login_message = 'Please log in to access this page.'

    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Keep the main routes blueprint for any non-API routes you might need
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Email error handling (keep your existing logic)
    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='OMNIDESK Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # File logging (keep your existing logic)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/omnidesk.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('OMNIDESK startup')

    return app

# Import models to register them with SQLAlchemy
from app import models