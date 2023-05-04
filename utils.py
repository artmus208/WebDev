from app.models import Records
from app import app
from datetime import datetime


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
