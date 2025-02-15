
from flask import Blueprint, render_template, request, jsonify
from app.continuous_gantt import generate_gantt_chart

main = Blueprint("main", __name__)
from werkzeug.utils import secure_filename
from flask import current_app, send_file

from flask import Flask, request, jsonify
import os

# Set upload folder and allowed extensions
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}
current_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle file upload
@main.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        return jsonify({"message": "File successfully uploaded"}), 200
    return jsonify({"message": "Invalid file format"}), 400

@main.route("/generate", methods=["POST"])
def generate():
    try:
        result = generate_gantt_chart()
        return send_file(result, mimetype='image/png', as_attachment=True, download_name='chart.png')
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
