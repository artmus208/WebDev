
#SQLAlchemy modules


import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base 
from flask_sqlalchemy import SQLAlchemy
# Подключение к БД
engine = create_engine("mariadb+mariadbconnector://root:pesk-2020@127.0.0.1:3306/time_managment_web_app")
# engine = create_engine("sqlite:///db.sqlite")
# Создание рабочей сессии c автокоммитом и автоотключением?
session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
# Суперкласс или базовый класс для моделей
Base = declarative_base()