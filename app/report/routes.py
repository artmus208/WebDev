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
            p_report, summury, caption = weekly_project_report(project_id=p.id)
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
        
    
        
    
    
