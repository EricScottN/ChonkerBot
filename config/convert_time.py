from datetime import datetime

def convert_date_to_str(datetime_object):
    return datetime_object.strftime("%d-%m-%y %H:%M:%S")

def convert_str_to_date(str_datetime_object):
    return datetime.strptime(str_datetime_object, "%d-%m-%y %H:%M:%S")
