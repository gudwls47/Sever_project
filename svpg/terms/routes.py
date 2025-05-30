from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import terms_bp
from ..db_1 import get_db_connection

# 약관 목록
@terms_bp.route('/')
def list():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Terms ORDER BY is_required DESC, terms_id ASC"
            cursor.execute(sql)
            terms = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('terms/list.html', terms=terms)

# 약관 상세
@terms_bp.route('/<int:terms_id>')
def detail(terms_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Terms WHERE terms_id = %s"
            cursor.execute(sql, (terms_id,))
            term = cursor.fetchone()
            
            if not term:
                flash('약관을 찾을 수 없습니다.', 'error')
                return redirect(url_for('terms.list'))
    finally:
        connection.close()
    
    return render_template('terms/detail.html', term=term)

# 약관 동의 처리
@terms_bp.route('/agree', methods=['POST'])
@login_required
def agree():
    data = request.get_json()
    terms_id = data.get('terms_id')
    
    if not terms_id:
        return jsonify({"status": "error", "message": "약관 ID가 필요합니다"}), 400
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 이미 동의했는지 확인
            sql = "SELECT * FROM UserAgreement WHERE user_id = %s AND terms_id = %s"
            cursor.execute(sql, (current_user.user_id, terms_id))
            if cursor.fetchone():
                return jsonify({"status": "error", "message": "이미 동의한 약관입니다"}), 400
            
            # 동의 기록
            sql = "INSERT INTO UserAgreement (user_id, terms_id) VALUES (%s, %s)"
            cursor.execute(sql, (current_user.user_id, terms_id))
            connection.commit()
            
            return jsonify({"status": "success", "message": "약관에 동의했습니다"})
            
    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

# 약관 동의 철회
@terms_bp.route('/disagree', methods=['POST'])
@login_required
def disagree():
    data = request.get_json()
    terms_id = data.get('terms_id')
    
    if not terms_id:
        return jsonify({"status": "error", "message": "약관 ID가 필요합니다"}), 400
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 필수 약관인지 확인
            sql = "SELECT is_required FROM Terms WHERE terms_id = %s"
            cursor.execute(sql, (terms_id,))
            term = cursor.fetchone()
            
            if term and term['is_required']:
                return jsonify({"status": "error", "message": "필수 약관은 철회할 수 없습니다"}), 400
            
            # 동의 철회
            sql = "DELETE FROM UserAgreement WHERE user_id = %s AND terms_id = %s"
            cursor.execute(sql, (current_user.user_id, terms_id))
            connection.commit()
            
            return jsonify({"status": "success", "message": "약관 동의를 철회했습니다"})
            
    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

# 사용자의 약관 동의 현황
@terms_bp.route('/my-agreements')
@login_required
def my_agreements():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 전체 약관과 사용자의 동의 여부 조회
            sql = """
                SELECT t.*, 
                       CASE WHEN ua.user_id IS NOT NULL THEN 1 ELSE 0 END as is_agreed,
                       ua.agreed_at
                FROM Terms t
                LEFT JOIN UserAgreement ua ON t.terms_id = ua.terms_id AND ua.user_id = %s
                ORDER BY t.is_required DESC, t.terms_id ASC
            """
            cursor.execute(sql, (current_user.user_id,))
            agreements = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('terms/my_agreements.html', agreements=agreements)