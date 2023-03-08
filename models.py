
from flask_app import db
from sqlalchemy.sql import func
from passlib.hash import bcrypt

class Records(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    cost_id = db.Column(db.Integer, db.ForeignKey('costs.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    hours = db.Column(db.Integer, default=0)
    minuts = db.Column(db.Integer, default=0)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    login = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    records = db.relationship("Records", backref='Employees', lazy='dynamic')
    gip = db.relationship("GIPs", backref='Employees', lazy='dynamic')
    admin = db.relationship("Admins", backref='Employees', lazy='dynamic')

    def __init__(self, login, password):
        self.login = login
        self.password = bcrypt.hash(password)

class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    project_name = db.Column(db.String(250), nullable=False)
    gip_id = db.Column(db.Integer, db.ForeignKey('gips.id'))
    start_time = db.Column(db.DateTime(timezone=True))
    end_time = db.Column(db.DateTime(timezone=True))
    end_time_fact = db.Column(db.DateTime(timezone=True))
    costs_tasks = db.relationship("CostsProjectsTasks",
                                backref='Projects', lazy='dynamic')

    def __init__(self, p_name, gip_id, start_time, end_time):
        self.project_name = p_name
        self.gip_id = gip_id
        self.start_time = start_time
        self.end_time = end_time

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GIPs(db.Model):
    __tablename__ = "gips"
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    project = db.relationship("Projects", backref='gips', lazy='dynamic')

    def __init__(self, gip_id):
        self.employee_id = gip_id


class Costs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    cost_name = db.Column(db.String(85), nullable=False, unique=True)
    projects_tasks = db.relationship("CostsProjectsTasks",
                                backref='Costs', lazy='dynamic')
    def __init__(self, cost_name):
        self.cost_name = cost_name

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    task_name = db.Column(db.String(85), nullable=False)
    projects_costs = db.relationship("CostsProjectsTasks",
                                backref='tasks', lazy='dynamic')

    def __init__(self, task_name):
        self.task_name = task_name
class CostsProjectsTasks(db.Model):
    """Соответсвие задач в статьях расходов, a статьи расходов по проектам

        Для фиксации человеко-дней в статье расходов не нужно указывать задачу.
        Если задача указана, то человеко-дни относятся к ней.
    """
    __tablename__ = "costs_projects_tasks"
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    cost_id = db.Column(db.Integer, db.ForeignKey('costs.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    man_days = db.Column(db.Integer)
    man_days_fact = db.Column(db.Integer)



class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    def __init__(self, employee_id):
        self.employee_id = employee_id
