from flask import Flask
from flask import session
import os


def create_app():
    app = Flask(__name__)

    # Set upload folder and allowed extensions
    app.config["UPLOAD_FOLDER"] = "./uploads"
    app.config["ALLOWED_EXTENSIONS"] = {"xlsx", "xls"}
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default_secret_key")
    #app.config["ENV"] = os.environ.get("FLASK_ENV", "production")

    with app.app_context():
        # Import and register blueprints
        from .routes import main
        from .auth import auth

        app.register_blueprint(main)
        app.register_blueprint(auth)

    return app
