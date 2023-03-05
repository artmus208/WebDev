
from flask_app import db
from sqlalchemy.sql import func


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    login = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    records = db.relationship("records", backref='employees', lazy='dynamic')
    gip = db.relationship("gips", backref='employees', lazy='dynamic')
    admin = db.relationship("admins", backref='employees', lazy='dynamic')

class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    gip_id = db.Column(db.Integer, db.ForeignKey('gips.id'))
    start_time = db.Column(db.DateTime(timezone=True))
    end_time = db.Column(db.DateTime(timezone=True))
    costs_tasks = db.relationship("costs_projects_tasks", 
                                backref='projects', lazy='dynamic')

class GIPs(db.Model):
    __tablename__ = "gips"
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    project = db.relationship("projects", backref='gips', lazy='dynamic')

   
class Costs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    cost_name = db.Column(db.String(85), nullable=False)
    man_days = db.Column(db.Integer)
    projects_tasks = db.relationship("costs_projects_tasks", 
                                backref='costs', lazy='dynamic')
    

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    task_name = db.Column(db.String(85), nullable=False)
    man_days = db.Column(db.Integer)
    projects_costs = db.relationship("costs_projects_tasks", 
                                backref='tasks', lazy='dynamic')
class CostsProjectsTasks(db.Model):
    __tablename__ = "costs_projects_tasks"
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    cost_id = db.Column(db.Integer, db.ForeignKey('costs.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))


class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))


class Records(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    cost_id = db.Column(db.Integer, db.ForeignKey('costs.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    hours = db.Column(db.Integer)
    minuts = db.Column(db.Integer)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Record_Keeping(db.Model):
    __tablename__ = 'records_old'
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    employee = db.Column(db.String(250), nullable=False)
    project_name = db.Column(db.String(250), nullable=False)
    category_of_costs = db.Column(db.String(250), nullable=False)
    task = db.Column(db.String(250), nullable=False)
    hours = db.Column(db.Integer)
    minuts = db.Column(db.Integer)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
