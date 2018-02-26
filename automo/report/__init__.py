"""Reports"""

from .. import database as db
from . import circumcision_discharge_summary
from . import discharge_summary
from . import prescription

db.ClinicalEncounter.get_prescription_pdf = prescription.get_prescription_pdf

db.Admission.generate_discharge_summary = discharge_summary.generate_discharge_summary

db.CircumcisionAdmission.generate_discharge_summary = circumcision_discharge_summary.generate_discharge_summary
db.CircumcisionAdmission.generate_admission_summary = circumcision_discharge_summary.generate_admission_summary
db.CircumcisionAdmission.generate_ot_note = circumcision_discharge_summary.generate_ot_note
