# Restaurants module initialization
from flask import Blueprint

restaurants_bp = Blueprint('restaurants', __name__, url_prefix='/restaurants')

from . import routes