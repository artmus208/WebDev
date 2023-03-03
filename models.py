
from flask_app import db
from sqlalchemy.sql import func

class Record_Keeping(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    employee = db.Column(db.String(250), nullable=False)
    project_name = db.Column(db.String(250), nullable=False)
    category_of_costs = db.Column(db.String(250), nullable=False)
    task = db.Column(db.String(250), nullable=False)
    hours = db.Column(db.Integer)
    minuts = db.Column(db.Integer)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
