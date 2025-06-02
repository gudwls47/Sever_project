import os
import sys

# svpg 폴더 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'svpg')))
from db_1 import init_db  # DB 초기화 함수만 불러오기

from app import create_app
from app import csrf

# 환경 변수에서 설정 모드 가져오기 (기본값: 'development')
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

# Flask 앱에 DB 종료 설정 연결
init_db(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)