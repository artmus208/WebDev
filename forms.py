from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, IntegerField
from wtforms.validators import data_required, length

List_of_Category_Of_Costs = [
    'Управление проектом',
    'Проектирование',
    'Программирование',
    'Сборка',
    'Тестирование',
    'ПНР и ШМР'
]

List_of_Projects = [
    "Проект 1",
    "Проект 2",
    "Проект 3",
    "Проект 4"
]

class Record(FlaskForm):
    project_name = SelectField(u'Проект', choices=List_of_Projects)
    category_of_costs = SelectField(u'Статья расходов', choices=List_of_Category_Of_Costs)
    task = StringField(label='Задача', validators=[data_required(), length(min=3)])
    hours = IntegerField(label='Кол-во часов', validators=[data_required()])
    minuts = IntegerField(label='Кол-во минут', validators=[data_required()])
    submit = SubmitField('Подтвердить')

class UserForm(FlaskForm):
    username = StringField(label='Имя сотрудника', validators=[data_required(), length(min=3)])
    submit = SubmitField('Продолжить')