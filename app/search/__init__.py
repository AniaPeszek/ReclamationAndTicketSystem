from flask import Blueprint

bp = Blueprint('search_bp', __name__)

from app.search import search