class Config:
    SECRET_KEY = '8b2771f9bec9434f87d56749ccadad43'
    # SQLALCHEMY_DATABASE_URI = "{connectorname}://{username}:{password}@{hostname}/{databasename}".format(
    # connectorname="mariadb+mariadbconnector",
    # username="root",
    # password="pesk-2020",
    # hostname="127.0.0.1:3306",
    # databasename="time_managment_web_app",
    # )
    SQLALCHEMY_DATABASE_URI = "{connectorname}://{username}:{password}@{hostname}/{databasename}".format(
    connectorname="mysql+mysqlconnector",
    username="artmus208",
    password="pesk-2020",
    hostname="artmus208.mysql.pythonanywhere-services.com",
    databasename="artmus208$time_managment_web_app",
    )
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True