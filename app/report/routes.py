import time
from flask import (
    Blueprint, flash, redirect,
    render_template, request,
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

report = Blueprint(
    'report',
    __name__,
    url_prefix="/report"
)

@report.route("/weekly", methods=["GET", "POST"])
def weekly():
    if g.emp is None:
        return redirect(url_for('auth.login'))
    form = ReportProjectForm()
    form.project_name.choices = Projects.get_projects_id_name_list()
    try:
        if form.validate_on_submit():
            proj_id = int(form.project_name.data)
            report, summury, caption = weekly_project_report(project_id=proj_id)
            return render_template(
                "report/weekly_report.html", 
                form=form,
                report=report,
                summury=summury,
                caption=caption
            )
        else:
            return render_template("report/weekly_report.html", form=form)    
    except:
        flash("Произошла ошибка при генерации отчета", category="error")
        logger.exception("Еженедельный отчет")
        time.sleep(1)
        return redirect(url_for('report.weekly'))
        
    
    
