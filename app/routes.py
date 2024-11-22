from flask import Blueprint, session, render_template, request, jsonify
from app.continuous_gantt import generate_gantt_chart
from app.jira_api import fetch_API
from app.auth import login, login_required, logout
import logging



main = Blueprint("main", __name__)
from werkzeug.utils import secure_filename
from .auth import login_required
from flask import current_app, send_file
import base64

from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():

    return render_template('index.html')

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"xlsx", "xls"}


# @main.route("/", methods=['GET', 'POST'])
# @login_required
# def index():
#     return render_template("index.html")



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



@main.route("/fetchAPI", methods=["GET"])
def fetchAPI():
    print(request.args["label"])

    response = fetch_API(request.args["label"], request.args["assignee"])

    print(response)
    return response


@app.route("/download-image")
def download_image():
    # Serve the image file from the 'static/images' folder
    return send_file(
        "static/images/chart.png",
        mimetype="image/png",
        as_attachment=True,
        download_name="chart.png",
    )


@main.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Process the data (this part should contain your processing logic)
    projects_df = data.get("projects_df")

    try:
        # Your logic here
        # For example, generating a chart and returning the image data
        # In this case, we will simulate the result for demo purposes

        result = generate_gantt_chart(projects_df)

        print(projects_df)
        result.seek(0)
        img_base64 = base64.b64encode(result.getvalue()).decode("utf-8")

        return jsonify({"status": "success", "image_data": img_base64})
    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# @main.route("/generate", methods=["POST"])
# def generate():
#     # Retrieve the JSON data sent in the request body
#     jira_json = request.get_json()  # Get JSON data from the request

#     if jira_json is None:
#         return jsonify({'status': 'error', 'message': 'No data provided'}), 400

#     else:
#         print(jira_json)  # Print the JSON to inspect it


#         result = generate_gantt_chart(jira_json)


#         result.seek(0)
#         img_base64 = base64.b64encode(result.getvalue()).decode('utf-8')


#         return jsonify({"status": "success", "image_data": img_base64})
#         #return send_file(result, mimetype='image/png', as_attachment=True, download_name='chart.png')
