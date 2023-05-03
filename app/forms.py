from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, StringField, SelectField, IntegerField, SelectMultipleField,
    DateField, BooleanField
    )
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import  ValidationError, Length, InputRequired, Regexp

class RecordsForm(FlaskForm):
    project_name = SelectField(u'Проект')
    category_of_costs = SelectField(u'Статья расходов')
    task = StringField(label='Задача',
                        default="blank_task",
                        render_kw={'disabled':''})
    hours = IntegerField(label='Кол-во часов', default=0)
    minuts = IntegerField(label='Кол-во минут', default=0)
    submit = SubmitField('Подтвердить')

def available_login(available_logins):
    def _available_login(form, field):

        if field.data.lower() not in available_logins:
            message = "Логин не зарегистрирован. Обратитесь к ЕАВ"
            raise ValidationError(message)
    return _available_login


# class SimpleForm(FlaskForm):
#     string_of_files = ['one\r\ntwo\r\nthree\r\n']
#     list_of_files = string_of_files[0].split()
#     # create a list of value/description tuples
#     files = [(x, x) for x in list_of_files]
#     example = MultiCheckboxField('Label', choices=files)

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ProjectAddForm(FlaskForm):

    code = StringField(u"Код проекта:", validators=[
        Length(min=5, max=5), InputRequired("Необходимо заполнить:"),
        Regexp('\d\d\D\d\d', message="Код проекта должен соответствовать формату: ЧЧБЧЧ") 
    ])
    name = StringField(u"Название проекта:", validators=[InputRequired("Необходимо заполнить")])
    cat_costs = MultiCheckboxField(
        u"Выберите категорию затрат проекта (по умолчанию 100 ч/д на каждой статье):",
        coerce=int)
    def validate_cat_costs(form, field):
        if not field.data:
            raise ValidationError("Выберите хотя бы одну статью расходов")
    gip = SelectField(u"ГИП проекта:")
    def validate_gip(form, field):
        if int(field.data) == -1:
            raise ValidationError("Не забудьте назначить ГИПа")
    submit = SubmitField("Добавить")

    

class ReportFormEmp(FlaskForm):
    employee = SelectField("Выбор сотрудника: ")
    def validate_employee(form, field):
        if int(field.data) == -1:
            raise ValidationError("Пожалуйста, выберите сотрудника")    
    is_all_period = BooleanField("За весь период:", 
                                render_kw = {"checked": True, "onchange":"disable_date(this)"})
    lower_date = DateField("Дата от: ", render_kw = {"disabled": True})
    upper_date = DateField("Дата до: ", render_kw = {"disabled": True})
    submit = SubmitField("Показать отчет")


class ProjectButton(FlaskForm):
    submit = SubmitField('Отчет по проекту')

class ReportProjectForm(FlaskForm):
    project_name = SelectField(u'Проект')
    submit = SubmitField('Создать отчет по проекту')

class ReturnButton(FlaskForm):
    submit = SubmitField('Выйти')