"""GUI Configuration"""
import re
import string

STARTUP_INTERFACE = ""


def higlight_query(value, query_string):
    """Highlight a string for display in html"""
    str_value = unicode(value)
    result = re.search(re.escape(query_string), str_value, re.IGNORECASE)
    if result is not None:
        group = unicode(result.group())
        str_value = string.replace(str_value, group, u'<b>' + group + u'</b>', 1)
    return str_value
