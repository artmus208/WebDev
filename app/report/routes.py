from datetime import datetime
from io import BytesIO
import time

from flask import (
    Blueprint, flash, redirect,
    render_template, request, send_file,
    session, g, url_for
)

from app import logger
from app.forms import ReportProjectForm

from app.models import (
    Employees, GIPs, Projects,
    Costs, Tasks, ProjectCosts,
    CostsTasks, Records, Admins
)
from app.report.reports_generators import weekly_project_report
from app.report.reports_in_xl import brief_p_report_xl, week_create_xl
from app.reports_makers import project_report2
from app.report.reports_all_in_xl import create_xl_project, get_info_project

report = Blueprint(
    'report',
    __name__,
    url_prefix="/report"
)


@report.route("/xl/p/<int:p_id>")
def xl_p_report(p_id):
    try:
        file_stream, p_code = brief_p_report_xl(p_id)
        date = datetime.now().strftime('%d.%m.%Y')
        return send_file(
            file_stream, download_name=f"Отчет {p_code} {date}.xlsx", 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except:
        flash("Ошибка при составлении XL документа")
        logger.exception("XL")
        return redirect(url_for("main.detailed_project_report"))


@report.route("/xl/all/p")
def all_xl_report():
    projects_data = {}

    all_projects = Projects.query.all()
    for project in all_projects:
        list_project = project.project_name.split()
        code = list_project[0]
        name_project = ' '.join(list_project[1:-1])

        info_project_list = get_info_project(project.id)

        projects_data[code] = [[name_project] + i for i in info_project_list]


    p_code = 'Все проекты'
    date = f"до {datetime.now().strftime('%d.%m.%Y')} включительно"

    file_stream = create_xl_project(projects_data)
    return send_file(
        file_stream, download_name=f"Отчет {p_code} {date}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    

@report.route("/xl/weekly/project/<int:p_id>")
def xl_weekly_project(p_id):
    try:
        report, summury, caption, project_id = weekly_project_report(p_id)

        date = datetime.now().strftime('%d.%m.%Y')
        file_stream, p_code = week_create_xl(report, caption)
        return send_file(
            file_stream, download_name=f"Отчет {date}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except:
        flash("Ошибка при составлении XL документа")
        logger.exception("XL")
        return redirect(url_for("main.detailed_project_report"))


@report.route("/weekly", methods=["GET", "POST"])
def weekly():
    if g.emp is None:
        return redirect(url_for('auth.login'))
    form = ReportProjectForm()
    form.project_name.choices = Projects.get_projects_id_name_list()
    try:
        if form.validate_on_submit():
            proj_id = int(form.project_name.data)
            report, summury, caption, project_id = weekly_project_report(project_id=proj_id)
            return render_template(
                "report/weekly_report.html", 
                form=form,
                report=report,
                summury=summury,
                caption=caption,
                project_id=project_id
            )
        else:
            return render_template("report/weekly_report.html", form=form)    
    except:
        flash("Произошла ошибка при генерации отчета", category="error")
        logger.exception("Еженедельный отчет")
        return redirect(url_for('report.weekly'))
    
@report.route("/inspect-2", methods=['GET'])
def inspect_2():
    if g.emp is None:
        return redirect(url_for('auth.login'))
    try:
        report = []
        all_p = Projects.query.all()
        for p in all_p:
            inner = {"caption": None, "costs": []}
            p_report, summury, caption, project_id = weekly_project_report(project_id=p.id)
            for c in p_report:
                if p_report[c]["week_labor"] == 0.0:
                    if inner["caption"] is None:
                        inner["caption"] = caption
                    inner["costs"].append(c)
            if inner["caption"] is not None:
                report.append(inner)
        return render_template("report/inspect_weekly_rec.html", report=report)
    except:
        flash("Ошибка inspect-2")
        logger.exception("inspect-2")
        return redirect(url_for("main.index"))
    
@report.route("/inspect-3", methods=['GET'])
def inspect_3():
    if g.emp is None:
        return redirect(url_for("auth.login"))
    try:
        report = []
        all_p = Projects.query.all()
        for p in all_p:
            inner = {"caption": None, "p_report": {}}
            p_report, summury, caption, project_id = weekly_project_report(project_id=p.id, is_before_last_week=True)
            report.append(
                {
                    "caption": caption,
                    "p_report": p_report,
                    "p_id": p.id
                }
            )
        return render_template("report/inspect3.html", report=report)
    
    except:
        flash("Ошибка в inspect-3")
        logger.exception("inspect-3")
        return redirect(url_for("main.index"))
    
    
@report.route("/detailed/<int:p_id>")
def detailed(p_id):
    if g.emp is None:
        return redirect(url_for("auth.login"))
    try:
        project_report = project_report2(p_id=p_id)
        return render_template('main/detailed_project_report.html', project_report=project_report)
    except:
        flash("Ошибка при составлении отчета")
        logger.exception("detailed")
        return redirect(url_for("main.detailed_project_report"))
        
        
    
    
    
        
    
    
