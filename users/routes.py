from flask import Blueprint, request, jsonify
from db import conn, cursor

users_bp = Blueprint('users', __name__)

# ✅ 프로필 이미지 변경 API
@users_bp.route('/users/<int:user_id>/profile-image', methods=['PUT'])
def update_profile_image(user_id):
    data = request.json
    image_url = data.get('profile_image_url')
    if not image_url:
        return jsonify({"error": "profile_image_url is required"}), 400
    try:
        cursor.execute("""
            UPDATE User
            SET profile_image_url = %s
            WHERE user_id = %s
        """, (image_url, user_id))
        conn.commit()
        return jsonify({"message": "Profile image updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 유저 정보 조회 API
@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    try:
        cursor.execute("SELECT user_id, username, email, profile_image_url FROM User WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        cursor.execute("SELECT trust_score, activity_score FROM UserScore WHERE user_id = %s", (user_id,))
        scores = cursor.fetchone()
        user.update(scores or {})
        return jsonify(user), 200
    except Exception as e:
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
