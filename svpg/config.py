import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """기본 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    
    # MySQL 설정
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or '127.0.0.1'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'root'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'restaurant_review'

    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'restaurant_review', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 세션 설정
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1시간
    
    # JSON 설정
    JSON_AS_ASCII = False
    
    # 카카오 지도 API 키
    KAKAO_MAP_API_KEY = os.environ.get('KAKAO_MAP_API_KEY') or ''

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}