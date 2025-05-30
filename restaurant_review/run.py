import os
from app import create_app
from app import csrf

# 환경 변수에서 설정 모드 가져오기 (기본값: 'development')
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)