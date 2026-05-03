from flask import Blueprint

bp = Blueprint('simple_lists', __name__)

from app.blueprints.simple_lists import routes
