from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import restaurants_bp
from ..db import get_db_connection
import pymysql

# 식당 목록 페이지
@restaurants_bp.route('/')
def list():
    # 검색 파라미터
    search_query = request.args.get('q', '')
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'rating')  # rating, review_count
    page = int(request.args.get('page', 1))
    per_page = 20
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 기본 쿼리
            base_query = """
                SELECT r.*, 
                       COUNT(DISTINCT rev.review_id) as review_count,
                       AVG(rev.rating) as avg_rating
                FROM Restaurant r
                LEFT JOIN Review rev ON r.restaurant_id = rev.restaurant_id
                WHERE 1=1
            """
            params = []
            
            # 검색 조건 추가
            if search_query:
                base_query += " AND (r.name LIKE %s OR r.address LIKE %s)"
                params.extend([f'%{search_query}%', f'%{search_query}%'])
            
            if category:
                base_query += " AND r.category = %s"
                params.append(category)
            
            base_query += " GROUP BY r.restaurant_id"
            
            # 정렬
            if sort_by == 'rating':
                base_query += " ORDER BY avg_rating DESC"
            elif sort_by == 'review_count':
                base_query += " ORDER BY review_count DESC"
            
            # 페이징
            base_query += " LIMIT %s OFFSET %s"
            params.extend([per_page, (page - 1) * per_page])
            
            cursor.execute(base_query, params)
            restaurants = cursor.fetchall()
            
            # 전체 개수 조회
            count_query = "SELECT COUNT(DISTINCT restaurant_id) FROM Restaurant WHERE 1=1"
            count_params = []
            if search_query:
                count_query += " AND (name LIKE %s OR address LIKE %s)"
                count_params.extend([f'%{search_query}%', f'%{search_query}%'])
            if category:
                count_query += " AND category = %s"
                count_params.append(category)
            
            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()['COUNT(DISTINCT restaurant_id)']
            
    finally:
        connection.close()
    
    return render_template('restaurants/list.html', 
                         restaurants=restaurants,
                         total_count=total_count,
                         page=page,
                         per_page=per_page,
                         search_query=search_query,
                         category=category,
                         sort_by=sort_by)

# 식당 상세 페이지
@restaurants_bp.route('/<int:restaurant_id>')
def detail(restaurant_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 식당 정보 조회
            sql = """
                SELECT r.*, 
                       COUNT(DISTINCT rev.review_id) as review_count,
                       AVG(rev.rating) as avg_rating
                FROM Restaurant r
                LEFT JOIN Review rev ON r.restaurant_id = rev.restaurant_id
                WHERE r.restaurant_id = %s
                GROUP BY r.restaurant_id
            """
            cursor.execute(sql, (restaurant_id,))
            restaurant = cursor.fetchone()
            
            if not restaurant:
                flash('식당을 찾을 수 없습니다.', 'error')
                return redirect(url_for('restaurants.list'))
            
            # 태그 조회
            sql = """
                SELECT t.* FROM Tag t
                JOIN RestaurantTag rt ON t.tag_id = rt.tag_id
                WHERE rt.restaurant_id = %s
            """
            cursor.execute(sql, (restaurant_id,))
            tags = cursor.fetchall()
            
            # 리뷰 조회
            sql = """
                SELECT r.*, u.username, u.profile_image,
                       rd.taste_rating, rd.price_rating, rd.service_rating
                FROM Review r
                JOIN User u ON r.user_id = u.user_id
                LEFT JOIN ReviewDetail rd ON r.review_id = rd.review_id
                WHERE r.restaurant_id = %s
                ORDER BY r.created_at DESC
                LIMIT 10
            """
            cursor.execute(sql, (restaurant_id,))
            reviews = cursor.fetchall()
            
    finally:
        connection.close()
    
    return render_template('restaurants/detail.html', 
                         restaurant=restaurant,
                         tags=tags,
                         reviews=reviews)

# 식당 등록 (사장님 전용)
@restaurants_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # 사장님 권한 확인
    if current_user.user_type != 'admin':
        flash('식당 등록은 사장님만 가능합니다.', 'error')
        return redirect(url_for('restaurants.list'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name')
        address = data.get('address')
        category = data.get('category')
        phone = data.get('phone')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 식당 등록
                sql = """INSERT INTO Restaurant (name, address, category, phone, latitude, longitude) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (name, address, category, phone, latitude, longitude))
                restaurant_id = cursor.lastrowid
                
                # 태그 추가
                tags = data.getlist('tags') if hasattr(data, 'getlist') else data.get('tags', [])
                for tag_id in tags:
                    sql = "INSERT INTO RestaurantTag (restaurant_id, tag_id) VALUES (%s, %s)"
                    cursor.execute(sql, (restaurant_id, tag_id))
                
                connection.commit()
                
                if request.is_json:
                    return jsonify({"status": "success", "restaurant_id": restaurant_id})
                else:
                    flash('식당이 등록되었습니다!', 'success')
                    return redirect(url_for('restaurants.detail', restaurant_id=restaurant_id))
                    
        except Exception as e:
            connection.rollback()
            if request.is_json:
                return jsonify({"status": "error", "message": str(e)}), 500
            else:
                flash(f'오류가 발생했습니다: {str(e)}', 'error')
        finally:
            connection.close()
    
    # 태그 목록 조회
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Tag ORDER BY name"
            cursor.execute(sql)
            tags = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('restaurants/register.html', tags=tags)

# 식당 검색 API
@restaurants_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 5, type=float)  # km
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT r.*, 
                       COUNT(DISTINCT rev.review_id) as review_count,
                       AVG(rev.rating) as avg_rating
            """
            
            # 위치 기반 검색인 경우 거리 계산 추가
            if lat and lng:
                sql += """,
                    (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * 
                    cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * 
                    sin(radians(latitude)))) AS distance
                """
            
            sql += """
                FROM Restaurant r
                LEFT JOIN Review rev ON r.restaurant_id = rev.restaurant_id
                WHERE 1=1
            """
            
            params = []
            if lat and lng:
                params.extend([lat, lng, lat])
            
            if query:
                sql += " AND (r.name LIKE %s OR r.address LIKE %s)"
                params.extend([f'%{query}%', f'%{query}%'])
            
            if category:
                sql += " AND r.category = %s"
                params.append(category)
            
            sql += " GROUP BY r.restaurant_id"
            
            # 위치 기반 검색인 경우 거리 필터링
            if lat and lng:
                sql += f" HAVING distance <= %s"
                params.append(radius)
                sql += " ORDER BY distance"
            else:
                sql += " ORDER BY avg_rating DESC"
            
            sql += " LIMIT 20"
            
            cursor.execute(sql, params)
            restaurants = cursor.fetchall()
            
            return jsonify({
                "status": "success",
                "results": restaurants
            })
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()