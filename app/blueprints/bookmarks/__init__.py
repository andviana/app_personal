from flask import Blueprint

bp = Blueprint('bookmarks', __name__)

from app.blueprints.bookmarks import routes
