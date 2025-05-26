# users/__init__.py
from flask import Blueprint
from .routes import users_bp

__all__ = ['users_bp']