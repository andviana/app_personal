from flask import Blueprint

bp = Blueprint('pessoas', __name__)

from app.pessoas import routes
