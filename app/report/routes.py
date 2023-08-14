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
    
    return render_template("report/example_table.html", form=form)
    
