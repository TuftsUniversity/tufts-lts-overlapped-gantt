from flask import Flask
import os
import logging
def create_app():
    app = Flask(__name__)

    # Set upload folder and allowed extensions
    app.config["UPLOAD_FOLDER"] = "./uploads"
    app.config["ALLOWED_EXTENSIONS"] = {"xlsx", "xls"}

    with app.app_context():
        # Import and register blueprints
        from .routes import main
        app.register_blueprint(main)
	    # Set up logging
    if not app.debug:
        logging.basicConfig(filename='app.log', level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

    return app
