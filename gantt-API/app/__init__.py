from flask import Flask

def create_app():
    app = Flask(__name__)

    # Set upload folder and allowed extensions
    app.config["UPLOAD_FOLDER"] = "./uploads"
    app.config["ALLOWED_EXTENSIONS"] = {"xlsx", "xls"}

    with app.app_context():
        # Import and register blueprints
        from .routes import main
        app.register_blueprint(main)

    return app
