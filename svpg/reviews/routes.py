import os
import uuid
from flask import Blueprint, request, jsonify
from ..db import conn, cursor
from app import csrf
from werkzeug.utils import secure_filename

# 이미지 업로드 폴더 경로 설정
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

reviews_bp = Blueprint('reviews', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_trust_score(user_id):
    try:
        cursor.execute("""
            SELECT review_count, receipt_verified_count, like_received_count
            FROM user_score
            WHERE user_id = %s
        """, (user_id,))
        user_score = cursor.fetchone()

        if not user_score:
            return

        review_count = user_score['review_count'] or 0
        verified_count = user_score['receipt_verified_count'] or 0
        like_count = user_score['like_received_count'] or 0

        base_score = min(30, review_count * 2)
        verified_ratio = (verified_count / review_count * 40) if review_count else 0
        like_score = min(30, like_count)

        trust_score = int(min(100, base_score + verified_ratio + like_score))

        cursor.execute("""
            UPDATE user_score
            SET trust_score = %s
            WHERE user_id = %s
        """, (trust_score, user_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Error updating trust_score:", e)

@csrf.exempt
@reviews_bp.route('/reviews', methods=['POST'])
def create_review():
    data = request.json
    user_id = data.get('user_id')
    restaurant_id = data.get('restaurant_id')
    rating = data.get('rating')
    content = data.get('content')
    receipt_verified = data.get('receipt_verified', False)
    taste_rating = data.get('taste_rating')
    price_rating = data.get('price_rating')
    service_rating = data.get('service_rating')

    if not all([user_id, restaurant_id, rating, content]):
        return jsonify({"error": "일반 항목 누락"}), 400

    try:
        cursor.execute("""
            INSERT INTO review (user_id, restaurant_id, rating, content, receipt_verified)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, restaurant_id, rating, content, receipt_verified))
        review_id = cursor.lastrowid

        if all([taste_rating, price_rating, service_rating]):
            cursor.execute("""
                INSERT INTO review_detail (review_id, taste_rating, price_rating, service_rating)
                VALUES (%s, %s, %s, %s)
            """, (review_id, taste_rating, price_rating, service_rating))

        cursor.execute("SELECT * FROM user_score WHERE user_id = %s", (user_id,))
        score = cursor.fetchone()
        if score:
            cursor.execute("""
                UPDATE user_score
                SET review_count = review_count + 1,
                    receipt_verified_count = receipt_verified_count + %s
                WHERE user_id = %s
            """, (1 if receipt_verified else 0, user_id))
        else:
            cursor.execute("""
                INSERT INTO user_score (user_id, review_count, receipt_verified_count)
                VALUES (%s, %s, %s)
            """, (user_id, 1, 1 if receipt_verified else 0))

        calculate_trust_score(user_id)
        conn.commit()
        return jsonify({"message": "Review created", "review_id": review_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

@csrf.exempt
@reviews_bp.route('/review-upload', methods=['POST'])
def upload_review_image():
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    ext = os.path.splitext(secure_filename(file.filename))[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    file_url = f"http://{request.host}/static/uploads/{filename}"
    return jsonify({"url": file_url}), 200

@csrf.exempt
@reviews_bp.route('/review-images', methods=['POST'])
def add_review_image():
    data = request.json
    review_id = data.get('review_id')
    image_url = data.get('image_url')

    if not all([review_id, image_url]):
        return jsonify({"error": "review_id and image_url required"}), 400

    try:
        cursor.execute("""
            INSERT INTO review_image (review_id, image_url)
            VALUES (%s, %s)
        """, (review_id, image_url))
        conn.commit()
        return jsonify({"message": "Image saved"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500


@reviews_bp.route('/users/<int:user_id>/reviews', methods=['GET'])
def get_reviews_by_user(user_id):
    try:
        conn.ping(reconnect=True)

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT r.*, 
                       u.nickname, u.profile_image, 
                       res.name AS restaurant_name
                FROM review r
                JOIN user u ON r.user_id = u.user_id
                JOIN restaurant res ON r.restaurant_id = res.restaurant_id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
            """, (user_id,))
            reviews = cursor.fetchall()

        for review in reviews:
            review_id = review['review_id']

            # taste, price, service rating 가져오기
            with conn.cursor(dictionary=True) as cursor2:
                cursor2.execute("SELECT * FROM review_detail WHERE review_id = %s", (review_id,))
                detail = cursor2.fetchone()
                review['taste_rating'] = detail['taste_rating'] if detail else None
                review['price_rating'] = detail['price_rating'] if detail else None
                review['service_rating'] = detail['service_rating'] if detail else None

            # ✅ 리뷰 이미지 고정 (무조건 test.jpg 반환)
            test_image_url = f"http://{request.host}/static/uploads/test.jpg"
            review['images'] = [test_image_url]

            # 좋아요 수
            with conn.cursor(dictionary=True) as cursor3:
                cursor3.execute("SELECT COUNT(*) AS like_count FROM `like` WHERE review_id = %s", (review_id,))
                review['like_count'] = cursor3.fetchone()['like_count']

        return jsonify(reviews), 200
    except Exception as e:
        print("리뷰 조회 중 오류:", e)
        return jsonify({"error": str(e)}), 500


