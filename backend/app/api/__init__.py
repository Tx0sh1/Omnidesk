from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import auth, tickets, users, client, comments, categories, reports
