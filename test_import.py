from app import app, db, text
from app.models import(
    Projects, GIPs,
    Costs, Records,
    Employees, ProjectCosts, 
    CostsTasks, Tasks,
    Admins
)


def load_emps():
    with app.app_context():
        with open("app/main/files/employees.txt", "r", encoding="utf-8") as f:
            for line in f:
                splited_list = line.split(",")
                new_rec = Employees(
                    id=splited_list[0],
                    login=splited_list[3],
                    password=splited_list[4]
                )               
                new_rec.save() 
                

def load_gips():
    with app.app_context():
        with open("app/main/files/gips.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                g = GIPs(
                    id=int(spl[0]),
                    emp_id=int(spl[2])
                )
                g.save()
            
            
def load_projects():
    with app.app_context():
        with open("app/main/files/projects.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                print(f"id: {spl[0]}, p_name: {spl[3]}, gip_id: {spl[4]}")
                p = Projects(
                    id=int(spl[0]),
                    p_name=spl[3],
                    gip_id=int(spl[4])
                )
                p.save()


def load_costs():
    with app.app_context():
        with open("app/main/files/costs.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                # print(f"id: {spl[0]}, c_name: {spl[3]}")
                c = Costs(
                    id=int(spl[0]),
                    cost_name=str(spl[3])
                )
                c.save()
                
def load_tasks():
    with app.app_context():
        with open("app/main/files/tasks.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                t = Tasks(
                    id=spl[0],
                    task_name=spl[3]
                )
                t.save()


def load_project_costs():
    with app.app_context():
        with open("app/main/files/project_costs.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                pc = ProjectCosts(
                    id=spl[0],
                    cost_id=spl[3],
                    man_days=spl[4],
                    project_id=spl[5]
                )
                pc.save()

def load_costs_tasks():
    with app.app_context():
        with open("app/main/files/costs_tasks.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                ct = CostsTasks(
                    id=spl[0],
                    task_name_fk=spl[3],
                    man_days=spl[4],
                    cost_id=spl[5]
                )
                ct.save()

def load_records():
    with app.app_context():
        with open("app/main/files/records.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                r = Records(
                    id=spl[0],
                    time_created=spl[1],
                    employee_id=spl[2],
                    project_id=spl[3],
                    cost_id=spl[4],
                    task_id=spl[5],
                    hours=spl[6],
                    minuts=spl[7]
                )
                r.save()


def load_admins():
    with app.app_context():
        with open("app/main/files/admins.txt", "r", encoding="utf-8") as f:
            for line in f:
                spl = line.split(",")
                a = Admins(
                    id=spl[0],
                    employee_id=spl[1]
                )
                a.save()


# load_emps()
# load_gips()
# load_projects()
# load_costs()
# load_tasks()
# load_project_costs()
# load_costs_tasks()
# load_records()
# load_admins()



