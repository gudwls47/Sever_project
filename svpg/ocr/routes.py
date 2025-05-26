from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import os
from db import conn, cursor

ocr_bp = Blueprint('ocr', __name__, url_prefix='/ocr')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ocr_bp.route('/verify-receipt', methods=['POST'])
def verify_receipt():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    file = request.files['image']
    restaurant_id = request.form.get('restaurant_id')

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid image file"}), 400
    if not restaurant_id:
        return jsonify({"error": "restaurant_id is required"}), 400

    cursor.execute("SELECT name FROM Restaurant WHERE restaurant_id = %s", (restaurant_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Restaurant not found"}), 404
    restaurant_name = result['name']

    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    text = pytesseract.image_to_string(Image.open(path), lang='kor+eng')

    matched = restaurant_name in text

    return jsonify({
        "restaurant_name": restaurant_name,
        "ocr_text": text,
        "match": matched,
        "image_url": f"/static/uploads/{filename}"
    }), 200