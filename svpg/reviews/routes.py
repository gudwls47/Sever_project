from flask import Blueprint, request, jsonify
from db import conn, cursor

reviews_bp = Blueprint('reviews', __name__)

# ✅ 리뷰 등록 API
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
        receipt_text = data.get('receipt_text')  # OCR 결과

        if receipt_verified:
            cursor.execute("SELECT name FROM Restaurant WHERE restaurant_id = %s", (restaurant_id,))
            result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Restaurant not found"}), 404
        restaurant_name = result['name']
        if not receipt_text or restaurant_name not in receipt_text:
            return jsonify({"error": "Receipt does not match restaurant name."}), 403

    try:
        cursor.execute("""
            INSERT INTO Review (user_id, restaurant_id, rating, content, receipt_verified)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, restaurant_id, rating, content, receipt_verified))
        review_id = cursor.lastrowid

        if all([taste_rating, price_rating, service_rating]):
            cursor.execute("""
                INSERT INTO ReviewDetail (review_id, taste_rating, price_rating, service_rating)
                VALUES (%s, %s, %s, %s)
            """, (review_id, taste_rating, price_rating, service_rating))

        conn.commit()
        return jsonify({"message": "Review created", "review_id": review_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500



# ✅ 리뷰 수정 API
@reviews_bp.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    data = request.json
    rating = data.get('rating')
    content = data.get('content')
    receipt_verified = data.get('receipt_verified')
    taste_rating = data.get('taste_rating')
    price_rating = data.get('price_rating')
    service_rating = data.get('service_rating')

    try:
        cursor.execute("""
            UPDATE Review
            SET rating = %s, content = %s, receipt_verified = %s, updated_at = NOW()
            WHERE review_id = %s
        """, (rating, content, receipt_verified, review_id))

        cursor.execute("SELECT * FROM ReviewDetail WHERE review_id = %s", (review_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE ReviewDetail
                SET taste_rating = %s, price_rating = %s, service_rating = %s
                WHERE review_id = %s
            """, (taste_rating, price_rating, service_rating, review_id))
        else:
            cursor.execute("""
                INSERT INTO ReviewDetail (review_id, taste_rating, price_rating, service_rating)
                VALUES (%s, %s, %s, %s)
            """, (review_id, taste_rating, price_rating, service_rating))

        conn.commit()
        return jsonify({"message": "Review updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 리뷰 이미지 URL 저장 API
@reviews_bp.route('/review-images', methods=['POST'])
def add_review_image():
    data = request.json
    review_id = data.get('review_id')
    image_url = data.get('image_url')

    if not all([review_id, image_url]):
        return jsonify({"error": "review_id and image_url required"}), 400

    try:
        cursor.execute("""
            INSERT INTO ReviewImage (review_id, image_url)
            VALUES (%s, %s)
        """, (review_id, image_url))
        conn.commit()
        return jsonify({"message": "Image saved"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 좋아요 등록 API
@reviews_bp.route('/likes', methods=['POST'])
def like_review():
    data = request.json
    user_id = data.get('user_id')
    review_id = data.get('review_id')

    if not all([user_id, review_id]):
        return jsonify({"error": "user_id and review_id required"}), 400

    try:
        cursor.execute("""
            INSERT IGNORE INTO `Like` (user_id, review_id)
            VALUES (%s, %s)
        """, (user_id, review_id))
        conn.commit()
        return jsonify({"message": "Liked"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 좋아요 취소 API
@reviews_bp.route('/likes', methods=['DELETE'])
def unlike_review():
    data = request.json
    user_id = data.get('user_id')
    review_id = data.get('review_id')

    if not all([user_id, review_id]):
        return jsonify({"error": "user_id and review_id required"}), 400

    try:
        cursor.execute("""
            DELETE FROM `Like`
            WHERE user_id = %s AND review_id = %s
        """, (user_id, review_id))
        conn.commit()
        return jsonify({"message": "Unliked"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 특정 리뷰의 좋아요 수 조회 API
@reviews_bp.route('/reviews/<int:review_id>/likes', methods=['GET'])
def count_likes(review_id):
    cursor.execute("""
        SELECT COUNT(*) AS like_count
        FROM `Like`
        WHERE review_id = %s
    """, (review_id,))
    result = cursor.fetchone()
    return jsonify(result), 200

# ✅ 사용자가 좋아요 누른 리뷰 목록 조회 API
@reviews_bp.route('/users/<int:user_id>/liked-reviews', methods=['GET'])
def get_user_liked_reviews(user_id):
    cursor.execute("""
        SELECT r.* FROM Review r
        JOIN `Like` l ON r.review_id = l.review_id
        WHERE l.user_id = %s
        ORDER BY l.created_at DESC
    """, (user_id,))
    return jsonify(cursor.fetchall()), 200

# ✅ 특정 식당의 리뷰 목록 조회 API
@reviews_bp.route('/restaurants/<int:restaurant_id>/reviews', methods=['GET'])
def get_reviews_by_restaurant(restaurant_id):
    cursor.execute("""
        SELECT * FROM Review
        WHERE restaurant_id = %s
        ORDER BY created_at DESC
    """, (restaurant_id,))
    return jsonify(cursor.fetchall()), 200

# ✅ 리뷰 상세 조회 API (디테일, 이미지, 좋아요 포함)
@reviews_bp.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_detail(review_id):
    cursor.execute("SELECT * FROM Review WHERE review_id = %s", (review_id,))
    review = cursor.fetchone()
    if review:
        cursor.execute("SELECT * FROM ReviewDetail WHERE review_id = %s", (review_id,))
        detail = cursor.fetchone()
        review['detail'] = detail

        cursor.execute("SELECT image_url FROM ReviewImage WHERE review_id = %s", (review_id,))
        images = cursor.fetchall()
        review['images'] = [img['image_url'] for img in images]

        cursor.execute("SELECT COUNT(*) AS like_count FROM `Like` WHERE review_id = %s", (review_id,))
        review['like_count'] = cursor.fetchone()['like_count']

        return jsonify(review), 200
    else:
        return jsonify({"error": "Review not found"}), 404

# ✅ 리뷰 삭제 API (이미지, 디테일, 좋아요도 함께 삭제)
@reviews_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    cursor.execute("DELETE FROM ReviewImage WHERE review_id = %s", (review_id,))
    cursor.execute("DELETE FROM ReviewDetail WHERE review_id = %s", (review_id,))
    cursor.execute("DELETE FROM `Like` WHERE review_id = %s", (review_id,))
    cursor.execute("DELETE FROM Review WHERE review_id = %s", (review_id,))
    conn.commit()
    return jsonify({"message": "Review deleted"}), 200

# ✅ 사용자별 리뷰 목록 조회 API
@reviews_bp.route('/users/<int:user_id>/reviews', methods=['GET'])
def get_reviews_by_user(user_id):
    cursor.execute("""
        SELECT * FROM Review
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    return jsonify(cursor.fetchall()), 200

