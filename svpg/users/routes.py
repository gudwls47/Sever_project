from flask import Blueprint, request, jsonify
from ..db import conn, cursor
from ..db_1 import get_db_connection
from werkzeug.security import generate_password_hash
from app import csrf
from werkzeug.security import check_password_hash
from flask import request
import os
from werkzeug.utils import secure_filename
users_bp = Blueprint('users', __name__)

#회원가입
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
        # 아이디 중복 확인
        cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "Username already exists"}), 409

        # 비밀번호 암호화
        hashed_password = generate_password_hash(password)

        # 회원정보 저장
        cursor.execute("""
            INSERT INTO User (username, password_hash, nickname, gender, phone_number)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, nickname, gender, phone_number))
        conn.commit()

        return jsonify({"message": "Signup successful"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

#로그인
@users_bp.route('/users/login', methods=['POST'])
@csrf.exempt
def login_user():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT user_id, password_hash FROM User WHERE username = %s", (username,))
    user = cursor.fetchone()

    print("DEBUG user:", user)
    print("DEBUG user type:", type(user))

    if user and check_password_hash(user['password_hash'], password):
        return jsonify({"message": "Login successful", "user_id": user['user_id']}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

#닉네임 업로드
@users_bp.route('/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    try:
        cursor.execute("SELECT nickname, profile_image FROM User WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "nickname": user['nickname'],
            "profile_image": user['profile_image']
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#닉네임 수정
@users_bp.route('/users/<int:user_id>/nickname', methods=['PUT'])
@csrf.exempt
def update_user_nickname(user_id):
    print("Request headers:", dict(request.headers))
    print("Raw request data:", request.data)
    data = request.get_json(force=True, silent=True)
    print("Received JSON data:", data)

    new_nickname = data.get('nickname') if data else None
    if not new_nickname:
        return jsonify({"error": "Nickname is required"}), 400
    try:
        cursor.execute("UPDATE User SET nickname = %s WHERE user_id = %s", (new_nickname, user_id))
        conn.commit()
        return jsonify({"message": "Nickname updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# 프로필 이미지 변경 API
@users_bp.route('/users/upload/profile-image', methods=['POST'])
def upload_profile_image_file():  # user_id 추가
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join('uploads', filename)
    file.save(save_path)

    # 실제 서버 IP/도메인으로 수정 필요
    file_url = f"http://192.168.219.105:5000/uploads/{filename}"

    return jsonify({"url": file_url}), 200

@users_bp.route('/users/<int:user_id>/profile-image', methods=['PUT'])
@csrf.exempt
def update_profile_image(user_id):
    print("Request JSON:", request.json)
    data = request.json
    image_url = data.get('profile_image_url')
    if not image_url:
        return jsonify({"error": "profile_image_url is required"}), 400

    try:
        cursor.execute("""
            UPDATE User
            SET profile_image = %s
            WHERE user_id = %s
        """, (image_url, user_id))
        conn.commit()
        return jsonify({"message": "Profile image updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500


# ✅ 유저별 trust_score, activity_score 갱신 API
@users_bp.route('/users/<int:user_id>/update-scores', methods=['POST'])
def update_user_scores(user_id):
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM Review r
            JOIN `Like` l ON r.review_id = l.review_id
            WHERE r.user_id = %s
        """, (user_id,))
        like_count = cursor.fetchone()['COUNT(*)']

        cursor.execute("SELECT COUNT(*) FROM Review WHERE user_id = %s AND receipt_verified = TRUE", (user_id,))
        verified_count = cursor.fetchone()['COUNT(*)']
        trust_score = like_count + verified_count

        cursor.execute("SELECT COUNT(*) FROM Review WHERE user_id = %s", (user_id,))
        review_count = cursor.fetchone()['COUNT(*)']
        activity_score = review_count

        cursor.execute("""
            UPDATE UserScore
            SET trust_score = %s, activity_score = %s, updated_at = NOW()
            WHERE user_id = %s
        """, (trust_score, activity_score, user_id))
        conn.commit()
        return jsonify({"trust_score": trust_score, "activity_score": activity_score}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 유저 랭킹 조회 API
@users_bp.route('/users/rankings', methods=['GET'])
def get_user_rankings():
    score_type = request.args.get('type')
    if score_type not in ['trust', 'activity']:
        return jsonify({"error": "Invalid type. Must be 'trust' or 'activity'"}), 400
    order_column = 'trust_score' if score_type == 'trust' else 'activity_score'

    cursor.execute(f"""
        SELECT u.user_id, u.username, s.{order_column}
        FROM User u
        JOIN UserScore s ON u.user_id = s.user_id
        ORDER BY s.{order_column} DESC
        LIMIT 50
    """)
    return jsonify(cursor.fetchall()), 200

# ✅ 즐겨찾기 추가 API
@users_bp.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_id = data.get('user_id')
    restaurant_id = data.get('restaurant_id')
    if not all([user_id, restaurant_id]):
        return jsonify({"error": "user_id and restaurant_id required"}), 400
    try:
        cursor.execute("""
            INSERT IGNORE INTO Favorite (user_id, restaurant_id)
            VALUES (%s, %s)
        """, (user_id, restaurant_id))
        conn.commit()
        return jsonify({"message": "Favorite added"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 즐겨찾기 삭제 API
@users_bp.route('/favorites', methods=['DELETE'])
def remove_favorite():
    data = request.json
    user_id = data.get('user_id')
    restaurant_id = data.get('restaurant_id')
    if not all([user_id, restaurant_id]):
        return jsonify({"error": "user_id and restaurant_id required"}), 400
    try:
        cursor.execute("DELETE FROM Favorite WHERE user_id = %s AND restaurant_id = %s", (user_id, restaurant_id))
        conn.commit()
        return jsonify({"message": "Favorite removed"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 유저의 즐겨찾기한 식당 목록 API
@users_bp.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    cursor.execute("""
        SELECT r.* FROM Restaurant r
        JOIN Favorite f ON r.restaurant_id = f.restaurant_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """, (user_id,))
    return jsonify(cursor.fetchall()), 200
