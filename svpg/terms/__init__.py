# Terms module initialization
from flask import Blueprint

terms_bp = Blueprint('terms', __name__, url_prefix='/terms')

from . import routes