"""Reports"""

from .. import database as db
from . import discharge_summary
from . import prescription


db.Admission.get_discharge_summary_elements = discharge_summary.get_discharge_summary_elements
db.Admission.generate_discharge_summary = discharge_summary.generate_discharge_summary

db.ClinicalEncounter.get_prescription_pdf = prescription.get_prescription_pdf
