from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from config import Config
from app.email_service import mail

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    login_manager.login_view = 'auth.github_login'
    
    with app.app_context():
        # Register OAuth clients
        oauth.register(
            name='github',
            client_id=app.config['GITHUB_CLIENT_ID'],
            client_secret=app.config['GITHUB_CLIENT_SECRET'],
            access_token_url='https://github.com/login/oauth/access_token',
            access_token_params=None,
            authorize_url='https://github.com/login/oauth/authorize',
            authorize_params=None,
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'},
        )
        
        oauth.register(
            name='linkedin',
            client_id=app.config['LINKEDIN_CLIENT_ID'],
            client_secret=app.config['LINKEDIN_CLIENT_SECRET'],
            access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
            authorize_url='https://www.linkedin.com/oauth/v2/authorization',
            api_base_url='https://api.linkedin.com/v2/',
            client_kwargs={'scope': 'r_liteprofile r_emailaddress'},
        )
        
        # Import blueprints here to avoid circular imports
        from app.routes import main
        from app.auth import auth
        from app.scheduler import init_scheduler
        
        # Register blueprints
        app.register_blueprint(main)
        app.register_blueprint(auth, url_prefix='/auth')
        
        # Create database tables
        db.create_all()
        
        # Initialize scheduler
        init_scheduler(app)
    
    return app 