"""Configuration"""

def format_duration(duration): #from_date, to_date):
    """Format python relative delta duration to human readable form."""
    if duration is None:
        return ""
    if duration.years < 1:
        if duration.months < 1:
            return "{0} d".format(duration.days)
        return "{0} m {1} d".format(duration.months, duration.days)
    if duration.years < 5:
        return "{0} y {1} m".format(duration.years, duration.months)
    return "{0} y".format(duration.years)


def format_date(date_object):
    """Format date"""
    if date_object is None:
        return ""

    return date_object.strftime("%d/%m/%Y")
