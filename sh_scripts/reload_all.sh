#! /usr/bin/bash
flask main admins_backup
flask main costs_backup 
flask main costs_tasks_backup 
flask main employees_backup
flask main gips_backup
flask main projects_backup
flask main project_costs_backup
flask main records_backup
flask main tasks_backup
flask main drop_db
flask main create_db
flask main load_employees
flask main load_costs
flask main load_tasks
flask main load_gips
flask main load_admins
flask main load_projects
flask main load_project_costs
flask main load_costs_tasks
flask main load_records