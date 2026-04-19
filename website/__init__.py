from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv  # Import getenv
from dotenv import load_dotenv # Import load_dotenv
from flask_login import LoginManager

# Load the .env file
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = getenv('SECRET_KEY', 'mwanza_pilot_key')

    # Construct TiDB Connection String
    DB_USER = getenv('DB_USER')
    DB_PASS = getenv('DB_PASSWORD')
    DB_HOST = getenv('DB_HOST')
    DB_PORT = getenv('DB_PORT')
    DB_NAME = getenv('DB_NAME')

    # TiDB Connection String using pymysql
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl_verify_cert=true"
    
    # Extra TiDB configuration for stability
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"ssl": {"fake_config": True}}, # Simplifies SSL for TiDB Cloud
        "pool_pre_ping": True,
    }

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Result

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app