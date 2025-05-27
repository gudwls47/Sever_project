from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from . import mypage_bp
from ..db import get_db_connection

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 마이페이지 메인
@mypage_bp.route('/')
@login_required
def index():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 사용자 정보 조회
            sql = """
                SELECT u.*, us.review_count, us.trust_score, us.activity_score
                FROM User u
                LEFT JOIN UserScore us ON u.user_id = us.user_id
                WHERE u.user_id = %s
            """
            cursor.execute(sql, (current_user.user_id,))
            user_info = cursor.fetchone()
            
            # 최근 리뷰 조회
            sql = """
                SELECT r.*, res.name as restaurant_name, res.category
                FROM Review r
                JOIN Restaurant res ON r.restaurant_id = res.restaurant_id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
                LIMIT 5
            """
            cursor.execute(sql, (current_user.user_id,))
            recent_reviews = cursor.fetchall()
            
            # 평균 별점 계산
            sql = "SELECT AVG(rating) as avg_rating FROM Review WHERE user_id = %s"
            cursor.execute(sql, (current_user.user_id,))
            avg_rating = cursor.fetchone()['avg_rating'] or 0
            
    finally:
        connection.close()
    
    return render_template('mypage/index.html', 
                         user_info=user_info,
                         recent_reviews=recent_reviews,
                         avg_rating=avg_rating)

# 프로필 수정
@mypage_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # 업데이트할 필드들
        real_name = data.get('real_name')
        phone_number = data.get('phone_number')
        email = data.get('email')
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 이메일 중복 확인
                if email != current_user.email:
                    sql = "SELECT * FROM User WHERE email = %s AND user_id != %s"
                    cursor.execute(sql, (email, current_user.user_id))
                    if cursor.fetchone():
                        if request.is_json:
                            return jsonify({"status": "error", "message": "이미 사용중인 이메일입니다"}), 400
                        else:
                            flash('이미 사용중인 이메일입니다.', 'error')
                            return redirect(url_for('mypage.profile'))
                
                # 프로필 업데이트
                sql = """
                    UPDATE User 
                    SET real_name = %s, phone_number = %s, email = %s
                    WHERE user_id = %s
                """
                cursor.execute(sql, (real_name, phone_number, email, current_user.user_id))
                
                # 프로필 이미지 처리
                if 'profile_image' in request.files:
                    file = request.files['profile_image']
                    if file and allowed_file(file.filename):
                        filename = f"profile_{current_user.user_id}_{secure_filename(file.filename)}"
                        filepath = os.path.join('static/uploads/profiles', filename)
                        file.save(filepath)
                        
                        sql = "UPDATE User SET profile_image = %s WHERE user_id = %s"
                        cursor.execute(sql, (filepath, current_user.user_id))
                
                connection.commit()
                
                if request.is_json:
                    return jsonify({"status": "success", "message": "프로필이 수정되었습니다"})
                else:
                    flash('프로필이 수정되었습니다.', 'success')
                    return redirect(url_for('mypage.index'))
                    
        except Exception as e:
            connection.rollback()
            if request.is_json:
                return jsonify({"status": "error", "message": str(e)}), 500
            else:
                flash(f'오류가 발생했습니다: {str(e)}', 'error')
        finally:
            connection.close()
    
    return render_template('mypage/profile.html')

# 비밀번호 변경
@mypage_bp.route('/password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # 새 비밀번호 확인
        if new_password != confirm_password:
            if request.is_json:
                return jsonify({"status": "error", "message": "새 비밀번호가 일치하지 않습니다"}), 400
            else:
                flash('새 비밀번호가 일치하지 않습니다.', 'error')
                return redirect(url_for('mypage.change_password'))
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 현재 비밀번호 확인
                sql = "SELECT password_hash FROM User WHERE user_id = %s"
                cursor.execute(sql, (current_user.user_id,))
                user = cursor.fetchone()
                
                if not check_password_hash(user['password_hash'], current_password):
                    if request.is_json:
                        return jsonify({"status": "error", "message": "현재 비밀번호가 일치하지 않습니다"}), 400
                    else:
                        flash('현재 비밀번호가 일치하지 않습니다.', 'error')
                        return redirect(url_for('mypage.change_password'))
                
                # 비밀번호 업데이트
                new_password_hash = generate_password_hash(new_password)
                sql = "UPDATE User SET password_hash = %s WHERE user_id = %s"
                cursor.execute(sql, (new_password_hash, current_user.user_id))
                connection.commit()
                
                if request.is_json:
                    return jsonify({"status": "success", "message": "비밀번호가 변경되었습니다"})
                else:
                    flash('비밀번호가 변경되었습니다.', 'success')
                    return redirect(url_for('mypage.index'))
                    
        except Exception as e:
            connection.rollback()
            if request.is_json:
                return jsonify({"status": "error", "message": str(e)}), 500
            else:
                flash(f'오류가 발생했습니다: {str(e)}', 'error')
        finally:
            connection.close()
    
    return render_template('mypage/password.html')

# 내 리뷰 목록
@mypage_bp.route('/reviews')
@login_required
def my_reviews():
    page = int(request.args.get('page', 1))
    per_page = 10
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 리뷰 조회
            sql = """
                SELECT r.*, res.name as restaurant_name, res.category,
                       rd.taste_rating, rd.price_rating, rd.service_rating,
                       COUNT(l.user_id) as like_count
                FROM Review r
                JOIN Restaurant res ON r.restaurant_id = res.restaurant_id
                LEFT JOIN ReviewDetail rd ON r.review_id = rd.review_id
                LEFT JOIN `Like` l ON r.review_id = l.review_id
                WHERE r.user_id = %s
                GROUP BY r.review_id
                ORDER BY r.created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (current_user.user_id, per_page, (page - 1) * per_page))
            reviews = cursor.fetchall()
            
            # 전체 리뷰 수
            sql = "SELECT COUNT(*) as total FROM Review WHERE user_id = %s"
            cursor.execute(sql, (current_user.user_id,))
            total_count = cursor.fetchone()['total']
            
    finally:
        connection.close()
    
    return render_template('mypage/reviews.html',
                         reviews=reviews,
                         page=page,
                         per_page=per_page,
                         total_count=total_count)

# 로그아웃
@mypage_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index'))