# Mypage module initialization
from flask import Blueprint

mypage_bp = Blueprint('mypage', __name__, url_prefix='/mypage')

from . import routes