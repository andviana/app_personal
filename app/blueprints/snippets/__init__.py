from flask import Blueprint

bp = Blueprint('snippets', __name__)

from app.blueprints.snippets import routes
