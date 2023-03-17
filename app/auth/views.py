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
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        error = None
        if not login:
            error = 'login is required.'
        elif not password:
            error = 'Password is required.'
        if error is None:
            try:
                hashed_password = generate_password_hash(password=password)
                new_one = Employees(login, hashed_password)
                new_one.register()
            except Exception as e:
                error = f"User {login} is fail registered."
                logger.warning(f'In login andpoint fail: {e}')
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/register.html')

@auth.route('/login', methods=('GET', 'POST'))
def login():
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