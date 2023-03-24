from app import db
from sqlalchemy.sql import func
from passlib.hash import bcrypt


# TIPS:
# Должен быть способ через relationship получить данные из связанной таблицы

# DONE: 
# [x]: Обновить эту модель в БД с учетом измененного fk в cost_id
class Records(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    cost_id = db.Column(db.Integer, db.ForeignKey('project_costs.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('costs_tasks.id'))
    hours = db.Column(db.Integer, default=0)
    minuts = db.Column(db.Integer, default=0)

    def __init__(self, employee_id, project_id, cost_id, task_id, hours, minuts):
        self.employee_id = employee_id
        self.project_id = project_id
        self.cost_id = cost_id
        self.task_id = task_id
        self.hours = hours
        self.minuts = minuts


    def as_dict_name(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def commit(self):
        db.session.commit()

    def __repr__(self) -> str:
        s = f"{self.id},\
{self.time_created},\
{self.employee_id},\
{self.project_id},\
{self.cost_id},\
{self.task_id},\
{self.hours},\
{self.minuts}"
        return s
        
class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    login = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    records = db.relationship("Records", backref='Employees', lazy='dynamic')
    gip = db.relationship("GIPs", backref='Employees', lazy='dynamic')
    admin = db.relationship("Admins", backref='Employees', lazy='dynamic')

    def __init__(self, login, password):
        self.login = login
        self.password = password
    
    def as_dict_name(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def commit(self):
        db.session.commit()
        
    @classmethod
    def get_all_logins(cls):
        return [emp.login for emp in db.session.execute(db.select(cls)).scalars()]

    @classmethod
    def get(cls, id):
        try:
            return db.session.get(cls, id)
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def get_by_login(cls, login):
        return cls.query.filter_by(login=login).first()

    def register(self):
        try:
            db.session.add(self)
            db.session.commit()
            print(self.login, "is sccuessfuly register.")
        except Exception:
            db.session.rollback()
            print(self.login, "is does not register.")
            raise



class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    project_name = db.Column(db.String(250), nullable=False)
    gip_id = db.Column(db.Integer, db.ForeignKey('gips.id'))
    start_time = db.Column(db.DateTime(timezone=True))
    end_time = db.Column(db.DateTime(timezone=True))
    end_time_fact = db.Column(db.DateTime(timezone=True))
    project_costs = db.relationship("ProjectCosts",
                                backref='Projects', lazy='dynamic')

    def __init__(self, p_name, gip_id, start_time, end_time):
        self.project_name = p_name
        self.gip_id = gip_id
        self.start_time = start_time
        self.end_time = end_time

    @classmethod
    def get_projects_id_name_list(self):
        return [(p.id, p.project_name) for p in db.session.execute(db.select(Projects)).scalars()]

    def as_dict_name(self):
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
    project_costs_rel = db.relationship("ProjectCosts", backref="Costs", lazy='dynamic')
    
    def __init__(self, cost_name):
        self.cost_name = cost_name

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def commit(self):
        db.session.commit()

    @classmethod
    def get_costs_names(self):
        return [c.cost_name for c in db.session.execute(db.select(self)).scalars()]
    
    @classmethod
    def get_name_by_id(cls, fk_id):
        return cls.query.filter_by(id=fk_id).first().cost_name    
    @classmethod
    def get_id_by_name(cls, name):
        return cls.query.filter_by(cost_name=name).first().id



class ProjectCosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    cost_name_fk = db.Column(db.Integer, db.ForeignKey('costs.id'))
    man_days = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    def __init__(self, cost_id, man_days, project_id):
        self.cost_name_fk = cost_id
        self.man_days = man_days
        self.project_id = project_id

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def commit(self):
        db.session.commit()

    @classmethod
    def get_costs_info(cls, project_id):
        """Возвращает список списков, который состоит из id, id статьи расходов и чел.днями"""
        r = [[0,"Нет данных"]]
        q = cls.query.filter_by(project_id=project_id).all()
        if q is not None:
            r = []
            for c in q:
                cost = Costs.query.filter_by(id=c.cost_name_fk).one()
                r.append([c.id, cost.cost_name, str(c.man_days)])
        return r


    @classmethod
    def get_costs_id_name(cls, project_id):
        """Возвращает список, который состоит из имён категорий затрат данного проекта"""
        r = [[0,"Нет данных"]]
        q = cls.query.filter_by(project_id=project_id).all()
        if q is not None:
            for c in q:
                cost_id_fk = c.cost_name_fk
                cost_name = db.session.get(Costs, cost_id_fk).cost_name
                r.append([c.id, cost_name])
        return r

    @classmethod
    def get_id_and_man_days_by_project_id(cls, project_id):
        r = [[0,"Нет данных"]]
        q = cls.query.filter_by(project_id=project_id).all()
        if q is not None:
            r = [[c.id, c.man_days] for c in q] 
        return r



class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    task_name = db.Column(db.String(85), nullable=False, unique=True)
    costs_tasks_rel = db.relationship("CostsTasks", backref='Tasks', lazy='dynamic')
    
    
    def __init__(self, task_name):
        self.task_name = task_name

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def commit(self):
        db.session.commit()

    @classmethod
    def get_task_by_name_use_careful(cls, task_name):
        """Возвращает объект Tasks по её имени, но имя д.б. уникально.
            Если имя неуникально -- нельзя использоватьэту функцию.
        """
        q = cls.query.filter_by(task_name=task_name).first() 
        return q
        
    

class CostsTasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    task_name_fk = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    man_days = db.Column(db.Float, nullable=False)
    cost_id = db.Column(db.Integer, db.ForeignKey('project_costs.id'))
    
    def __init__(self, task_name_fk, man_days, cost_id):
        self.task_name_fk = task_name_fk
        self.man_days = man_days
        self.cost_id = cost_id

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def commit(self):
        db.session.commit()
    
    # Чтобы выбрать все задачи данного проекта, нужно
    # выбрать все статьи данного проекта и для каждой статьи
    # нужно изъять задачу и добавить в результат
    @classmethod
    def get_tasks_info(cls, project_id):
        """Возвращает список элементов [task_id, task_name]
        
        Метод извлекает из БД все статьи расходов в проекте, затем
        для каждой статьи расходов извлекаются задачи.
        Далее мы получаем имена задачи по её ID.
        """
        all_costs = ProjectCosts.query.filter_by(project_id=project_id).all()
        tasks_id = []
        
        r = [[0,"Нет данных", "Нет чел/день"]]
        for c in all_costs:
            costs_tasks = cls.query.filter_by(cost_id=c.id).all()
            for c_t in costs_tasks:
                task = Tasks.query.filter_by(id=c_t.task_name_fk).one()
                task_name = task.task_name
                if task_name != "blank_task":
                    tasks_id.append([c_t.id, task_name, str(c_t.man_days)])
        r = tasks_id
        return r


class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    def __init__(self, employee_id):
        self.employee_id = employee_id
