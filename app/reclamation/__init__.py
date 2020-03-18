from flask import Blueprint

bp = Blueprint('reclamation_bp',__name__)

from app.reclamation import routes