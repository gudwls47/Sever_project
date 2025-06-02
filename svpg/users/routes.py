from flask import Blueprint, request, jsonify
from ..db import conn, cursor
from ..db_1 import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from app import csrf
import os
from werkzeug.utils import secure_filename

users_bp = Blueprint('users', __name__)

# 회원가입
@users_bp.route('/users/signup', methods=['POST'])
@csrf.exempt
def signup_user():
    data = request.get_json(force=True)

    username = data.get('username')
    password = data.get('password_hash')
    nickname = data.get('nickname')
    gender = data.get('gender')
    if gender == "여성":
        gender = "female"
    elif gender == "남성":
        gender = "male"
    contact = data.get('contact')
    phone_number = contact

    if not all([username, password, nickname, gender, contact]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "Username already exists"}), 409

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO user (username, password_hash, nickname, gender, phone_number)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, nickname, gender, phone_number))
        conn.commit()

        return jsonify({"message": "Signup successful"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# 로그인
@users_bp.route('/users/login', methods=['POST'])
@csrf.exempt
def login_user():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT user_id, password_hash FROM user WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password_hash'], password):
        return jsonify({"message": "Login successful", "user_id": user['user_id']}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# 닉네임, 프로필 로딩
@users_bp.route('/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    try:
        cursor.execute("SELECT nickname, profile_image FROM user WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"nickname": user['nickname'], "profile_image": user['profile_image']}), 200
    except Exception as e:
        print("프로필 조회 오류:", e)
        return jsonify({"error": str(e)}), 500

# 닉네임 수정
@users_bp.route('/users/<int:user_id>/nickname', methods=['PUT'])
@csrf.exempt
def update_user_nickname(user_id):
    data = request.get_json(force=True, silent=True)
    new_nickname = data.get('nickname') if data else None
    if not new_nickname:
        return jsonify({"error": "Nickname is required"}), 400
    try:
        cursor.execute("UPDATE user SET nickname = %s WHERE user_id = %s", (new_nickname, user_id))
        conn.commit()
        return jsonify({"message": "Nickname updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# 프로필 이미지 업로드
@users_bp.route('/users/upload/profile-image', methods=['POST'])
def upload_profile_image_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join('uploads', filename)
    file.save(save_path)
    file_url = f"http://192.168.219.105:5000/uploads/{filename}"

    return jsonify({"url": file_url}), 200

@users_bp.route('/users/<int:user_id>/profile-image', methods=['PUT'])
@csrf.exempt
def update_profile_image(user_id):
    data = request.json
    image_url = data.get('profile_image_url')
    if not image_url:
        return jsonify({"error": "profile_image_url is required"}), 400

    try:
        cursor.execute("UPDATE user SET profile_image = %s WHERE user_id = %s", (image_url, user_id))
        conn.commit()
        return jsonify({"message": "Profile image updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# 스코어 갱신
@users_bp.route('/users/<int:user_id>/update-scores', methods=['POST'])
def update_user_scores(user_id):
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM review r
            JOIN `like` l ON r.review_id = l.review_id
            WHERE r.user_id = %s
        """, (user_id,))
        like_count = cursor.fetchone()['COUNT(*)']

        cursor.execute("SELECT COUNT(*) FROM review WHERE user_id = %s AND receipt_verified = TRUE", (user_id,))
        verified_count = cursor.fetchone()['COUNT(*)']
        trust_score = like_count + verified_count

        cursor.execute("SELECT COUNT(*) FROM review WHERE user_id = %s", (user_id,))
        review_count = cursor.fetchone()['COUNT(*)']
        activity_score = review_count

        cursor.execute("""
            UPDATE user_score
            SET trust_score = %s, activity_score = %s
            WHERE user_id = %s
        """, (trust_score, activity_score, user_id))
        conn.commit()
        return jsonify({"trust_score": trust_score, "activity_score": activity_score}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# 랭킹 조회
@users_bp.route('/users/rankings', methods=['GET'])
def get_user_rankings():
    score_type = request.args.get('type')
    if score_type not in ['trust', 'activity']:
        return jsonify({"error": "Invalid type. Must be 'trust' or 'activity'"}), 400
    order_column = 'trust_score' if score_type == 'trust' else 'activity_score'

    cursor.execute(f"""
        SELECT u.user_id, u.username, s.{order_column}
        FROM user u
        JOIN user_score s ON u.user_id = s.user_id
        ORDER BY s.{order_column} DESC
        LIMIT 50
    """)
    return jsonify(cursor.fetchall()), 200

# 즐겨찾기 추가
@users_bp.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_id = data.get('user_id')
    restaurant_id = data.get('restaurant_id')
    if not all([user_id, restaurant_id]):
        return jsonify({"error": "user_id and restaurant_id required"}), 400
    try:
        cursor.execute("""
            INSERT IGNORE INTO favorite (user_id, restaurant_id)
            VALUES (%s, %s)
        """, (user_id, restaurant_id))
        conn.commit()
        return jsonify({"message": "Favorite added"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# 즐겨찾기 삭제
@users_bp.route('/favorites', methods=['DELETE'])
def remove_favorite():
    data = request.json
    user_id = data.get('user_id')
    restaurant_id = data.get('restaurant_id')
    if not all([user_id, restaurant_id]):
        return jsonify({"error": "user_id and restaurant_id required"}), 400
    try:
        cursor.execute("DELETE FROM favorite WHERE user_id = %s AND restaurant_id = %s", (user_id, restaurant_id))
        conn.commit()
        return jsonify({"message": "Favorite removed"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# 즐겨찾기 목록
@users_bp.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    cursor.execute("""
        SELECT r.* FROM restaurant r
        JOIN favorite f ON r.restaurant_id = f.restaurant_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """, (user_id,))
    return jsonify(cursor.fetchall()), 200
