from flask import Flask
from flask import session
import os
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-key-for-dev")
    # Set upload folder and allowed extensions
    app.config["UPLOAD_FOLDER"] = "./uploads"
    app.config["ALLOWED_EXTENSIONS"] = {"xlsx", "xls"}
    app.config["BEARER_ACCESS_TOKEN"] = os.environ.get(
        "BEARER_ACCESS_TOKEN", "default_secret_key"
    )
    # app.config["ENV"] = os.environ.get("FLASK_ENV", "production")

    with app.app_context():
        # Import and register blueprints
        from .routes import main
        from .auth import auth

        app.register_blueprint(main)
        app.register_blueprint(main)
        app.register_blueprint(auth)
        from .routes import routes
        app.register_blueprint(routes)

    return app
