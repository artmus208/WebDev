from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font

from app.reports_makers import project_report2


def create_xl_project(projects_data):

    wb = Workbook()
    ws = wb.active

    headers = [
        "Код проекта",
        "Название проекта",
        "Статьи расходов",
        "План, чел/день",
        "Факт, чел/день",
        "Отклонение, чел/день",
        "Отклонение, %"
    ]

    bold_font = Font(bold=True)

    for col_num, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = bold_font

    for project_name, expenses in projects_data.items():
        for expense in expenses:
            ws.append([project_name] + expense)

    ws.auto_filter.ref = f"A1:G{ws.max_row}"

    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        ws.column_dimensions[col].width = 30

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return file_stream


def get_info_project(id):
    detailed_p_report = project_report2(id)

    info_project = []

    c_c_list = detailed_p_report["cat_cost_list"]
    for i, c_c_name in enumerate(c_c_list):
        d_p_row = [
            c_c_name,
            round(c_c_list[c_c_name]["cat_cost_plan"] / 60 / 8, 1),
            round(c_c_list[c_c_name]["total_perf_time"] / 60 / 8, 1),
            round(c_c_list[c_c_name]["abs_diff"] / 60 / 8, 1),
            round(c_c_list[c_c_name]["rel_diff"], 1),
        ]
        info_project.append(d_p_row)
        # print(d_p_row)
    return info_project

