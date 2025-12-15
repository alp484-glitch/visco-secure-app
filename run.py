import os
from app import create_app

# Get the configuration environment (development environment by default)
config_name = os.environ.get("FLASK_ENV", "dev")
app = create_app(config_name)

if __name__ == "__main__":
    # Start the application (Gunicorn is recommended for production environment)
    if app.config["SESSION_COOKIE_SECURE"]:
        app.run(
            host="0.0.0.0",
            port=5001,
            debug=app.config["DEBUG"],
            ssl_context=("certs/cert.pem", "certs/key.pem")
        )
    else:
        app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5001)),
            debug=app.config["DEBUG"]
        )


