from flask import Blueprint

bp = Blueprint('lists', __name__)

from app.blueprints.lists import routes
