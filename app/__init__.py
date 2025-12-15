from flask import Flask, Response
from flask_login import LoginManager
from flask_talisman import Talisman
from .config import config_by_name
from .models import db, User
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = "routes.login"  # Login page route
login_manager.session_protection = "strong"
csrf = CSRFProtect()


def create_app(config_name: str = "dev") -> Flask:
    """Create Flask application instance"""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    @app.after_request
    def remove_server_header(response: Response) -> Response:
        response.headers.pop('Server', None)
        return response

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager.init_app(app)

    csrf.init_app(app)

    # Security protection (CSP, HTTPS, etc.)
    Talisman(
        app,
        content_security_policy={
            "default-src": "'self'",
            "script-src": "'self' https://cdn.jsdelivr.net",
            "style-src": "'self' https://cdn.jsdelivr.net",
            "frame-ancestors": "'self'",
            "form-action": "'self'"
        },
        force_https=app.config["SESSION_COOKIE_SECURE"],  # Force HTTPS in production environment
    )

    # Load user callback (Flask-Login)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register route blueprint
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    csrf.exempt(routes_bp)

    # Create database tables (first run)
    with app.app_context():
        db.create_all()

    return app