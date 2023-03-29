from app import app, db, text
from app.models import Projects, GIPs
from app import helper_functions


# Проверка текстового запроса
with app.app_context():
    session = db.session
    res = session.execute(text("SELECT * FROM gips")).fetchall()
    # print("Text query result:\n")
    # print(res)

# Провекра select запроса
with app.app_context():
    select = db.select
    stmt = select(GIPs).where(GIPs.id == 1)
    res = db.session.execute(stmt).scalar()
    print(stmt)    
    print(res)

# Проерка order_by запроса
with app.app_context():
    select = db.select
    execute = db.session.execute
    res = execute(
        select(Projects).where(Projects.gip_id == 1)
    ).scalars()
    print(res.all())

