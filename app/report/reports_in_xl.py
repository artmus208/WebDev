# Здесь я выгружаю пока что только краткий отчет за всё время
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.utils import column_index_from_string
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from app.reports_makers import project_report2


def autosize_columns(worksheet):
    def value_of(value):
        return (str(value) if value is not None else "")

    for cells in worksheet.columns:
        length = max(len(value_of(cell.value)) for cell in cells)
        column_letter = get_column_letter(cells[0].column)
        worksheet.column_dimensions[column_letter].width = length

    return worksheet

def brief_p_report_xl(p_id=14):
    detailed_p_report = project_report2(p_id)
    
    p_title = detailed_p_report["p_name"]
    p_code = p_title.split()[0]

    wb = Workbook()

    ws: Worksheet = wb.create_sheet(f"Сжатый отчет {p_code}", 0)

    count_cat_costs = len(detailed_p_report["cat_cost_list"])
    count_rows = count_cat_costs + 4 + 1 # 4 - потому что таблица не от верхней границы, а от 4 строки вниз, 1 потмоу что есть ещё заголовок

    ref = ["C5", f"G{count_rows}"]

    caption_range = ws["C5":"G5"][0]

    for cell in caption_range:
        cell.font = Font(bold=True)

    caption_list = [
        "Статьи расходов", 
        "План, чел/день", 
        "Факт, чел/день",
        "Отклонение, чел/д", 
        "Отклонение, %", 
    ]

    for cell, caption  in zip(caption_range, caption_list):
        cell.value = caption
    
    index_c_col = column_index_from_string("C")
    index_g_col = column_index_from_string("G")
    c_c_list = detailed_p_report["cat_cost_list"]
    for i, c_c_name in enumerate(c_c_list):
        d_p_row = [
        c_c_name,
        round(c_c_list[c_c_name]["cat_cost_plan"] / 60 / 8, 1),
        round(c_c_list[c_c_name]["total_perf_time"] / 60 / 8, 1),
        round(c_c_list[c_c_name]["abs_diff"] / 60 / 8, 1),
        round(c_c_list[c_c_name]["rel_diff"], 1),
    ]
        for row in ws.iter_rows(min_row=6+i, max_row=6+i, min_col=index_c_col, max_col=index_g_col):
            for cell, value in zip(row, d_p_row):
                cell.value = value
            


    tab = Table(displayName="brief_project_report", ref=":".join(ref))
    style = TableStyleInfo(name="BriefStyle", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=False, showColumnStripes=False)
    tab.tableStyleInfo = style
    ws.add_table(tab)
    autosize_columns(ws)
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 20
    ws.column_dimensions["F"].width = 20
    ws.column_dimensions["G"].width = 20

    info = [f"Сжатый отчет по проекту", f"{p_title}", f"до {datetime.now().strftime('%d.%m.%Y')} включительно"]
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=3, min_col=1, max_col=1)):
        for cell in row:
            cell.value = info[i]
            if i == 1:
                cell.font = Font(bold=True)
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    wb.close()
    return file_stream, p_code








