import time
from functools import wraps
from app.models import Records, Projects
from app import app, logger
from datetime import datetime


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logger.info(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper

def update_date_in_records():
    with app.app_context():
        with open("backup24_03_2023_records.txt") as f:
            for line in f:
                l = line.split(",")
                date_, time_ = l[1].split(" ")
                year_, month_, day_ =  map(int, date_.split("-"))
                hours_, minutes_, seconds_ = map(int, time_.split(":"))
                dt = datetime(year_, month_, day_, hours_, minutes_, seconds_)
                id_ = int(l[0])
                emp = Records.get(id_)
                if emp:
                    emp.time_created = dt
                    emp.commit()
                else:
                    print(f"Записью c id:{id_} нет в базе")

def update_p_name_in_projects():
    with app.app_context():
        with open("projects.txt", encoding="UTF8") as f:
            for line in f:
                id_ = int(line.split(",")[0])
                name_ = line.split(",")[1]
                if id_ == 22:
                    name_ = "23R01 Система TCS"
                p = Projects.get(id_)
                p.project_name = name_
                p.commit()
                print(id_, name_.__repr__())

if __name__ == "__main__":          
    update_p_name_in_projects()
