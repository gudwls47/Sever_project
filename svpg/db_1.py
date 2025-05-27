import pymysql
from flask import g

# MySQL 연결 설정
DB_CONFIG = {
    'host': 'localhost',
    'user': 'flask_app',
    'password': 'your_password_here',  # 실제 비밀번호로 변경
    'database': 'restaurant_review',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """데이터베이스 연결을 반환"""
    return pymysql.connect(**DB_CONFIG)

def close_db_connection(e=None):
    """요청이 끝날 때 데이터베이스 연결 닫기"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """Flask 앱에 데이터베이스 관련 설정 추가"""
    app.teardown_appcontext(close_db_connection)