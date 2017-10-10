"""Reports"""

from .. import database as db
from . import discharge_summary


db.Admission.get_discharge_summary_elements = discharge_summary.get_discharge_summary_elements
db.Admission.generate_discharge_summary = discharge_summary.generate_discharge_summary
