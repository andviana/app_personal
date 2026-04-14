from flask import Blueprint

bp = Blueprint('pessoas', __name__)

from app.blueprints.pessoas import routes
