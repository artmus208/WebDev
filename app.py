from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

import logging
app = Flask(__name__)
app.config.from_object(Config)
client = app.test_client()


docs = FlaskApiSpec()




# Импорт модели данных 
from .models import *
# Создание таблиц в БД


# Конфигурация логгера
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()


session = db.session
Base = db.Model
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


from .main.views import records

app.register_blueprint(records)

db = SQLAlchemy(app)


jwt = JWTManager(app)
docs.init_app(app)