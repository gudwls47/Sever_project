import os
from flask import Flask
from tags import tags_bp
from reviews import reviews_bp
from users import users_bp
from ocr import ocr_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(tags_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(ocr_bp)
app.register_blueprint(users_bp, url_prefix='/users')

if __name__ == '__main__':
    app.run(debug=True)