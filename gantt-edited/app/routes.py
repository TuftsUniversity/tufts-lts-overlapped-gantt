from flask import Blueprint, render_template, request, jsonify
from app.continuous_gantt import generate_gantt_chart
import logging
main = Blueprint("main", __name__)
from werkzeug.utils import secure_filename
from flask import current_app, send_file
import base64
import pandas as pd
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import io
import tempfile
app = Flask(__name__)

# Set upload folder and allowed extensions
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"xlsx", "xls"}



# Route to generate the chart
@main.route("/")
def index():
    
    return render_template("index.html")



@app.route('/download-image')
def download_image():
    # Serve the image file from the 'static/images' folder
    return send_file('static/images/chart.png', mimetype='image/png', as_attachment=True, download_name='chart.png')


@main.route('/upload', methods=['POST'])
def upload():
    # Ensure a file is part of the request
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400

    file = request.files['file']

    # Ensure a file was selected
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    # File upload successful - no need to save it to disk.
    # Simply respond that the upload was successful.
    return jsonify({"status": "success", "message": "File uploaded successfully"})
# @app.route('/generate', methods=['POST'])
# def generate():
#     data = request.get_json()

#     # Get the file content from the request
#     file_content = data.get('file_content')

#     if not file_content:
#         return jsonify({'status': 'error', 'message': 'No file content provided'}), 400

#     # Convert the file content into a DataFrame
#     file_stream = io.StringIO(file_content)
#     df = pd.read_excel(file_stream)

#     # Example of generating a response (replace with actual processing logic)
    

#     # Return a placeholder success response (replace with actual image generation logic)
#     return jsonify({'status': 'success', 'image_data': 'base64_encoded_image'})

@main.route('/generate', methods=['POST'])
def generate():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400

        file = request.files['file']

        # Try generating the chart
        try:
            result = generate_gantt_chart(file.read())
        except ValueError as e:
            # If start_date > end_date, catch the error and send it to the frontend
            return jsonify({'status': 'error', 'message': str(e)}), 400

        # Convert the result to a base64-encoded image
        result.seek(0)
        img_base64 = base64.b64encode(result.getvalue()).decode('utf-8')

        return jsonify({'status': 'success', 'image_data': img_base64})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@main.route('/download', methods=['GET'])
def download():
    """Provide the download of the generated Gantt chart."""
    temp_dir = os.path.join(os.getcwd(), 'downloads')
    output_path = os.path.join(temp_dir, 'gantt_chart.png')

    
    if os.path.exists(output_path):
        return send_file(output_path, mimetype='image/png', as_attachment=True, download_name='gantt_chart.png')
    else:
        return jsonify({'status': 'error', 'message': 'No chart available for download'}), 404