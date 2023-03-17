import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import Employees
from app import logger
auth = Blueprint('auth', __name__, 
               url_prefix="/auth", 
               template_folder="templates/auth", 
               static_folder="static/auth")


@auth.route("/register", methods=("GET", "POST"))
def register():
    try:
        if request.method == 'POST':
            login = request.form['login']
            password = request.form['password']
            error = None
            if not login:
                error = 'Введите логин'
            elif not password:
                error = 'Введите пароль'
            if error is None:
                try:
                    emp = Employees.get_by_login(login=login)
                    if emp is None:
                        print("Такого пользователя не существует, добавляем...")
                        hashed_password = generate_password_hash(password=password)
                        new_one = Employees(login, hashed_password)
                        new_one.register()
                    else:
                        print("Пользователь найден, изменяем пароль...")
                        emp.password = generate_password_hash(password=password)
                        emp.commit()
                except Exception as e:
                    error = f"User {login} is fail registered."
                    logger.warning(f'In login andpoint fail: {e}')
                else:
                    return redirect(url_for("auth.login"))
            flash(error)
        return render_template('auth/register.html')
    except Exception as e:
        flash("Ошибка регистрации", category='error')
        logger.warning(f"In register fail: {e}")
        return redirect(url_for("main.index"))

@auth.route('/login', methods=('GET', 'POST'))
def login():
    try:
        if request.method == 'POST':
            login = request.form['login'].lower()
            password = request.form['password']
            error = None
            employee = Employees.query.filter_by(login=login).first()
            if employee is None:
                error = 'Неверный логин'
            elif not check_password_hash(employee.password, password):
                error = 'Неверный пароль'


            if error is None:
                session.clear()
                session['emp_id'] = employee.id
                return redirect(url_for('main.index'))
            
            flash(error, category='error')

        return render_template('auth/login.html')
    except Exception as e:
        flash("Ошибка авторизации", category='error')
        logger.warning(f"In register fail: {e}")
        return redirect(url_for("main.index"))


@auth.before_app_request
def load_logged_in_emp():
    emp_id = session.get('emp_id')
    if emp_id is None:
        g.emp = None
    else:
        g.emp = Employees.get(emp_id)

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view