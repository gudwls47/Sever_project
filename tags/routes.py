from flask import Blueprint, request, jsonify
from db import conn, cursor

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/tags', methods=['GET'])
def get_all_tags():
    cursor.execute("SELECT * FROM Tag")
    return jsonify(cursor.fetchall()), 200

@tags_bp.route('/tags', methods=['POST'])
def add_tag():
    name = request.json.get('name')
    if not name:
        return jsonify({"error": "Tag name is required"}), 400
    try:
        cursor.execute("INSERT INTO Tag (name) VALUES (%s)", (name,))
        conn.commit()
        return jsonify({"message": "tag added"}), 201
    except:
        return jsonify({"error": "tag already exists or db error"}), 500

@tags_bp.route('/restaurant/<int:restaurant_id>/tags', methods=['POST', 'DELETE'])
def manage_tag_link(restaurant_id):
    tag_id = request.json.get('tag_id')
    if not tag_id:
        return jsonify({"error": "tag_id is required"}), 400

    if request.method == 'POST':
        cursor.execute("""
            INSERT IGNORE INTO RestaurantTag (restaurant_id, tag_id)
            VALUES (%s, %s)
        """, (restaurant_id, tag_id))
        conn.commit()
        return jsonify({"message": "Tag linked"}), 201

    elif request.method == 'DELETE':
        cursor.execute("""
            DELETE FROM RestaurantTag
            WHERE restaurant_id = %s AND tag_id = %s
        """, (restaurant_id, tag_id))
        conn.commit()
        return jsonify({"message": "Tag unlinked"}), 200

@tags_bp.route('/restaurants/by-tag/<int:tag_id>', methods=['GET'])
def get_restaurants_by_tag(tag_id):
    cursor.execute("""
        SELECT r.* FROM Restaurant r
        JOIN RestaurantTag rt ON r.restaurant_id = rt.restaurant_id
        WHERE rt.tag_id = %s
    """, (tag_id,))
    return jsonify(cursor.fetchall()), 200
