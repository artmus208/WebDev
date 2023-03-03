from flask import Flask, redirect, render_template, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from reports_makers import make_query_to_dict_list, get_project_report_dict
db = SQLAlchemy()
from config import Config
import logging
# Импорт модели данных
from models import *
from forms import *
# Создание таблиц в БД

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Конфигурация логгера
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

@app.route("/", methods=['GET', 'POST'])
def home():
    try:
        form = UserForm()
        reportBtn = ProjectButton()
        if form.validate_on_submit():
            username = form.username.data
            return redirect(url_for('record', uname=username))
        else:
            return render_template('home.html', form=form, reportBtn=reportBtn)
    except Exception as e:
        logger.warning(f"In Index page fail has been ocured: {e}")

@app.route("/record/<uname>", methods=['GET', 'POST'])
def record(uname):
    try:
        form = Record()        
        if form.validate_on_submit():
            rec = Record_Keeping()
            rec.employee = uname
            rec.project_name = form.project_name.data
            rec.category_of_costs = form.category_of_costs.data
            rec.task = form.task.data
            rec.hours = form.hours.data
            rec.minuts = form.minuts.data
            db.session.add(rec)
            db.session.commit()
            return render_template('success.html', uname=uname)
        else:
            return render_template('records.html', form=form, uname=uname)
    except Exception as e:
        logger.warning(f"In record page fail has been ocured: {e}")

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.before_first_request
def create_database():
    with app.app_context():
        db.create_all()


@app.route('/rep', methods=['GET', 'POST'])
def project_report():
    try:
        form = ReportProjectForm()
        if form.validate_on_submit():
            selectedProj = form.project_name.data
            records = Record_Keeping.query.filter_by(project_name=selectedProj).all()
            rec_list_dict = make_query_to_dict_list(records)
            res_dict = get_project_report_dict(all_records=rec_list_dict, p_name=selectedProj)
            return jsonify(res_dict)
        else:
            return render_template('project_report.html', form=form)
    except Exception as e:
        logger.warning(f"In project_report fail has been ocured: {e}")

@app.route('/rep/<selectedProj>', methods=['GET'])
def show_report(selectedProj):
    pass

    



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1234)