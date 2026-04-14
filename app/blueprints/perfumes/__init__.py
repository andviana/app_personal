from flask import Blueprint

bp = Blueprint('perfumes', __name__)

from app.blueprints.perfumes import routes
