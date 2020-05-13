from flask import Blueprint

bp = Blueprint("ticket_bp", __name__)

from app.ticket import routes
