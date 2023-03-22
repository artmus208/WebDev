from app import app
from app import helper_functions


with app.app_context():
    print(helper_functions.revise_records_for_ProjectCosts())
