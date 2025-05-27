from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
from ..db import get_db_connection
import pymysql

# 로그인 페이지
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 사용자 조회
                sql = "SELECT * FROM User WHERE username = %s AND is_active = TRUE"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    # 로그인 성공
                    if request.is_json:
                        return jsonify({"status": "success", "message": "로그인 성공"})
                    else:
                        flash('로그인 성공!', 'success')
                        return redirect(url_for('main.index'))
                else:
                    if request.is_json:
                        return jsonify({"status": "error", "message": "아이디 또는 비밀번호가 잘못되었습니다"}), 401
                    else:
                        flash('아이디 또는 비밀번호가 잘못되었습니다.', 'error')
        finally:
            connection.close()
    
    return render_template('auth/login.html')

# 회원가입 페이지
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # 필수 정보 추출
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        real_name = data.get('real_name')
        phone_number = data.get('phone_number')
        user_type = data.get('user_type', 'normal')
        
        # 약관 동의 여부 확인
        terms_agreed = data.get('terms_agreed', [])
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 중복 확인
                sql = "SELECT * FROM User WHERE username = %s OR email = %s"
                cursor.execute(sql, (username, email))
                if cursor.fetchone():
                    if request.is_json:
                        return jsonify({"status": "error", "message": "이미 존재하는 아이디 또는 이메일입니다"}), 400
                    else:
                        flash('이미 존재하는 아이디 또는 이메일입니다.', 'error')
                        return redirect(url_for('auth.register'))
                
                # 비밀번호 해싱
                password_hash = generate_password_hash(password)
                
                # 사용자 등록
                sql = """INSERT INTO User (username, password_hash, email, real_name, phone_number, user_type) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (username, password_hash, email, real_name, phone_number, user_type))
                user_id = cursor.lastrowid
                
                # 약관 동의 기록
                for term_id in terms_agreed:
                    sql = "INSERT INTO UserAgreement (user_id, terms_id) VALUES (%s, %s)"
                    cursor.execute(sql, (user_id, term_id))
                
                connection.commit()
                
                if request.is_json:
                    return jsonify({"status": "success", "message": "회원가입이 완료되었습니다"})
                else:
                    flash('회원가입이 완료되었습니다!', 'success')
                    return redirect(url_for('auth.login'))
                    
        except Exception as e:
            connection.rollback()
            if request.is_json:
                return jsonify({"status": "error", "message": str(e)}), 500
            else:
                flash(f'오류가 발생했습니다: {str(e)}', 'error')
        finally:
            connection.close()
    
    # GET 요청시 약관 목록 조회
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Terms ORDER BY is_required DESC, terms_id ASC"
            cursor.execute(sql)
            terms = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('auth/register.html', terms=terms)

# 로그아웃
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index'))

# 약관 동의 API
@auth_bp.route('/terms/agree', methods=['POST'])
def agree_terms():
    data = request.get_json()
    user_id = data.get('user_id')
    terms_id = data.get('terms_id')
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO UserAgreement (user_id, terms_id) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, terms_id))
            connection.commit()
            return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()