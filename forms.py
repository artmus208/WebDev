from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, IntegerField
from wtforms.validators import data_required, length, ValidationError

class RecordsForm(FlaskForm):
    project_name = SelectField(u'Проект')
    category_of_costs = SelectField(u'Статья расходов')
    task = StringField(label='Задача',
                       default="blank_task",
                       render_kw={'disabled':''})
    hours = IntegerField(label='Кол-во часов', validators=[data_required()])
    minuts = IntegerField(label='Кол-во минут', validators=[data_required()])
    submit = SubmitField('Подтвердить')


def available_login(available_logins):

    def _available_login(form, field):
        
        if field.data.lower() not in available_logins:
            message = "Логин не зарегистрирован. Обратитесь к ЕАВ"
            raise ValidationError(message)
    return _available_login\
    

def my_length_check(form, field):
    if len(field.data) > 50:
        raise ValidationError('Field must be less than 50 characters')
class ProjectButton(FlaskForm):
    submit = SubmitField('Отчет по проекту')

class ReportProjectForm(FlaskForm):
    project_name = SelectField(u'Проект')
    submit = SubmitField('Создать отчет по проекту')

class ReturnButton(FlaskForm):
    submit = SubmitField('Назад')