import icu
from datetime import datetime


def update_proxy(proxy):
    return proxy


def parse_date(s_date):
    splint_date = s_date.split(" ")
    splint_date[1] = month_from_ru_to_eng(splint_date[1])
    str_date = ""
    for d in splint_date:
        str_date += " " + d
    str_date = str_date.strip()

    return datetime.strptime(str_date, "%d %m %Y %H:%M")


def month_from_ru_to_eng(month):
    out = ''
    if 'дек' in month: out = '12'
    elif 'янв' in month: out = '1'
    elif 'фев' in month: out = '2'
    elif 'мар' in month: out = '3'
    elif 'апр' in month: out = '4'
    elif 'ма' in month: out = '5'
    elif 'июн' in month: out = '6'
    elif 'июл' in month: out = '7'
    elif 'авг' in month: out = '8'
    elif 'сент' in month: out = '9'
    elif 'окт' in month: out = '10'
    elif 'ноя' in month: out = '11'
    return out
