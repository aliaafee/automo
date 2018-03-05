"""Configuration"""
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

REPORT_HEAD_SUPTITLE = ""
REPORT_HEAD_TITLE = "SOME MEMORIAL HOSPITAL"
REPORT_HEAD_SUBTITLE1 = "Street Address of Hospital, City, 20041, Country"
REPORT_HEAD_SUBTITLE2 = "Phone 0000000, Fax 000000, Email mail@somehospital.com"
REPORT_HEAD_SUBTITLE3 = "Department of Surgery"
REPORT_HEAD_LOGO_RIGHT = ""
REPORT_HEAD_LOGO_LEFT = ""

CIRCUM_CHIEF_COMPLAINT = "Admission for Circumcision"
CIRCUM_PREOP_ORDERS = "Followe PAC Orders, NPO from 2am. Inj Cefazolin 50mg/kg stat before incision."
CIRCUM_DISCHARGE_ADVICE = "Olive oil application QID"
CIRCUM_FOLLOW_UP = "Take shower and follow up in opd on ___________"
CIRCUM_MEDS = "SYP PARACETAMOL (250MG/5ML)"

BATCH_IMPORT_COLUMNS = "national_id_no,name,age,sex,weight,address,bed_number,hospital_no"

def format_duration(duration): #from_date, to_date):
    """Format python relative delta duration to human readable form."""
    if duration is None:
        return ""
    if duration.years < 1:
        if duration.months < 1:
            if duration.days < 1:
                if duration.hours < 1:
                    return "{0}min {1}sec".format(duration.minutes, duration.seconds)
                return "{0}h".format(duration.hours)
            return "{0}d".format(duration.days)
        return "{0}m {1}d".format(duration.months, duration.days)
    if duration.years < 5 and duration.months > 0:
        return "{0}y {1}m".format(duration.years, duration.months)
    return "{0}y".format(duration.years)


def format_duration_verbose(duration): #from_date, to_date):
    """Format python relative delta duration to human readable form."""
    if duration is None:
        return ""
    if duration.years < 1:
        if duration.months < 1:
            if duration.days < 1:
                if duration.hours < 1:
                    return "{0}minutes {1}seconds".format(duration.minutes, duration.seconds)
                return "{0}hours".format(duration.hours)
            return "{0}days".format(duration.days)
        return "{0}months {1}days".format(duration.months, duration.days)
    if duration.years < 5 and duration.months > 0:
        return "{0}years {1}months".format(duration.years, duration.months)
    return "{0}years".format(duration.years)


def parse_duration(duration_str):
    """Parse duration in the form _y _m _d to relativedelta.
      if string contains only a number it is interpreted as years"""

    duration_str = duration_str.lower()

    if re.match("^[0-9]+$", duration_str) is not None:
        return relativedelta(years=int(duration_str))

    years = 0
    months = 0
    days = 0

    isvalid = False
    result = re.search("[0-9]+y", duration_str)
    if result is not None:
        isvalid = True
        years = int(result.group()[0:-1])

    result = re.search("[0-9]+m", duration_str)
    if result is not None:
        isvalid = True
        months = int(result.group()[0:-1])

    result = re.search("[0-9]+d", duration_str)
    if result is not None:
        isvalid = True
        days = int(result.group()[0:-1])

    if not isvalid:
        raise ValueError("No valid duration found in string.")

    return relativedelta(years=years, months=months, days=days, hours=0, minutes=0, seconds=0, microseconds=0)


def format_date(date_object):
    """Format date"""
    if date_object is None:
        return ""

    return date_object.strftime(DATE_FORMAT)


def parse_date(date_str):
    """Parse date"""
    return datetime.strptime(date_str, DATE_FORMAT)


def format_datetime(datetime_object):
    """Format datetime"""
    if datetime_object is None:
        return ""

    return datetime_object.strftime(DATETIME_FORMAT)


def parse_datetime(datetime_str):
    """Parse datetime"""
    return datetime.strptime(datetime_str, DATETIME_FORMAT)
