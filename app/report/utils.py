import datetime
from datetime import date


def get_end_week_dates(date_from: date = datetime.date.today()):
    """Возврат дат понедельника и пятницы предыдущей недели"""
    
    today = date_from
    
    current_weekday = today.weekday()  # День недели сегодняшней даты (0 - понедельник, 6 - воскресенье)
    days_to_monday = current_weekday - 0  # Дни до понедельника
    days_to_friday = current_weekday - 4  # Дни до пятницы
    
    last_monday = today - datetime.timedelta(days=days_to_monday) # - datetime.timedelta(weeks=1)
    last_friday = today - datetime.timedelta(days=days_to_friday) # - datetime.timedelta(weeks=1)
    
    last_monday = datetime.datetime.combine(last_monday, datetime.datetime.min.time())
    last_friday = datetime.datetime.combine(last_friday, datetime.time(23, 59, 59))
    
    return last_monday, last_friday