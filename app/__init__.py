from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from .config import Config
from .dataBase_connect import Base, engine, session
import logging
app = Flask(__name__)
app.config.from_object(Config)
client = app.test_client()

Base.query = session.query_property()

docs = FlaskApiSpec()

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='videoblog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()]
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})


# Импорт модели данных 
from .models import *
# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

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



@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


from .main.views import records

app.register_blueprint(records)


jwt = JWTManager(app)
docs.init_app(app)