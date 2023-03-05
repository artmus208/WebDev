from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, IntegerField
from wtforms.validators import data_required, length


class RecordsForm(FlaskForm):
    project_name = SelectField(u'Проект')
    category_of_costs = SelectField(u'Статья расходов')
    task = StringField(label='Задача',
                       default="blank_task",
                       render_kw={'disabled':''})
    hours = IntegerField(label='Кол-во часов', validators=[data_required()])
    minuts = IntegerField(label='Кол-во минут', validators=[data_required()])
    submit = SubmitField('Подтвердить')

class UserForm(FlaskForm):
    username = StringField(label='Логин сотрудника', validators=[data_required(), length(min=3)])
    submit = SubmitField('Продолжить')

class ProjectButton(FlaskForm):
    submit = SubmitField('Отчет по проекту')

class ReportProjectForm(FlaskForm):
    project_name = SelectField(u'Проект')
    submit = SubmitField('Создать отчет по проекту')
