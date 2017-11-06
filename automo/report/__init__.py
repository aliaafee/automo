"""Reports"""

from .. import database as db
from . import circumcision_discharge_summary
from . import discharge_summary
from . import prescription


#db.Admission.get_discharge_summary_elements = discharge_summary.get_discharge_summary_elements
db.Admission.generate_discharge_summary = discharge_summary.generate_discharge_summary

#db.CircumcisionAdmission.get_discharge_summary_elements = circumcision_discharge_summary.get_discharge_summary_elements
db.CircumcisionAdmission.generate_discharge_summary = circumcision_discharge_summary.generate_discharge_summary
db.CircumcisionAdmission.generate_admission_summary = circumcision_discharge_summary.generate_admission_summary
db.ClinicalEncounter.get_prescription_pdf = prescription.get_prescription_pdf
