from flask import Blueprint

blueprint_main = Blueprint('main', __name__)

from app.main import views, errors
