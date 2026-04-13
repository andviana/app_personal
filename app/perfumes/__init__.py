from flask import Blueprint

bp = Blueprint('perfumes', __name__)

from app.perfumes import routes
