from typing import List

from app import app, db, text
from app.models import (
    Projects, GIPs,
    Costs, Records,
    Employees, ProjectCosts, CostsTasks, Tasks)
from app import helper_functions
from app import select, execute

from app.reports_makers import report_about_employee
# with app.app_context():
#     res = execute(
#         select(Records)
#     ).first()
#     print(res)

with app.app_context():
    # res = Records.get_all_employee_projects_id(34)
    res = Records.get_all_employee_cat_costs_id(34, 22)
    for r in res:
        print(r)


with app.app_context():
    report_about_employee(34)


# with app.app_context():
#     res = Records.get_last_5_records()
#     [print(i, item, type(item)) for i, item in enumerate(res)]

# with app.app_context():
#     res:List[Records] = Records.get_last_5_records()
#     for r in res:
#         # print("Before replacement:\n", r, sep="")
#         record_with_names = r.replace_ids_to_names(
#             EmployeesObj=Employees, ProjectsObj=Projects,
#             ProjectCostObj=ProjectCosts,  CostsObj=Costs
#         )
#         print("After replacement:\n", record_with_names,sep='')
        

# with app.app_context():
#     res:List[Records] = Records.get_last_5_records(emp_id=34)
#     for r in res:
#         # print("Before replacement:\n", r, sep="")
#         record_with_names = r.replace_ids_to_names(
#             EmployeesObj=Employees, ProjectsObj=Projects,
#             ProjectCostObj=ProjectCosts,  CostsObj=Costs
#         )
#         print("After replacement:\n", record_with_names,sep='')

# with app.app_context():
#     print(f"ProjectCosts.query.first().id: {ProjectCosts.query.order_by(ProjectCosts.id.desc()).first().id}")

# with app.app_context():
#     cost_name = Costs.query.filter_by(id=1).first().cost_name
#     print(Costs.query.filter_by(cost_name=cost_name).first().cost_name.__repr__())
    

# # Проверка текстового запроса
# with app.app_context():
#     session = db.session
#     res = session.execute(text("SELECT * FROM gips")).fetchall()
#     # print("Text query result:\n")
#     # print(res)

# # Провекра select запроса
# with app.app_context():
#     select = db.select
#     stmt = select(GIPs).where(GIPs.id == 1)
#     res = db.session.execute(stmt).scalar()
#     print(stmt)    
#     print(res)

# # Проерка order_by запроса
# with app.app_context():
#     select = db.select
#     execute = db.session.execute
#     res = execute(
#         select(Projects).where(Projects.gip_id == 1)
#     ).scalars()
#     print(res.all())


