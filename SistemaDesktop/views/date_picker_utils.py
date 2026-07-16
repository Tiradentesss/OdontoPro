from datetime import date, datetime


MONTH_NAMES = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro',
}


def parse_br_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip(), '%d/%m/%Y').date()
    except ValueError:
        return None


def build_month_days(year, month, available_dates, selected_date=None):
    available_set = {parse_br_date(value) for value in (available_dates or [])}
    available_set = {item for item in available_set if item is not None}

    first_day = date(year, month, 1)
    next_month = date(year + (month // 12), month % 12 + 1, 1) if month < 12 else date(year + 1, 1, 1)
    days_in_month = (next_month - first_day).days

    cells = []
    first_weekday = first_day.weekday()

    for _ in range(first_weekday):
        cells.append({'day': None, 'date': None, 'enabled': False, 'selected': False})

    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        cells.append({
            'day': day,
            'date': current_date,
            'enabled': current_date in available_set,
            'selected': selected_date is not None and current_date == selected_date,
        })

    return cells


def format_month_label(year, month):
    return f"{MONTH_NAMES[month]} {year}"
