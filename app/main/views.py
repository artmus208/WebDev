from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import data_required, length

from app import logger


records = Blueprint('records', __name__)

@records.route("/", methods=['GET'])
def index():
    try:
        return "Hello, WebApp!"
    except Exception as e:
        logger.warning("In Index page fail has been ocured: {e}")