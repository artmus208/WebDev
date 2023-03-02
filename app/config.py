class Config:
    SECRET_KEY = '8b2771f9bec9434f87d56749ccadad43'
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="artmus208",
    password="pesk-2020",
    hostname="artmus208.mysql.pythonanywhere-services.com",
    databasename="time_managment_web_app",
    )
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True