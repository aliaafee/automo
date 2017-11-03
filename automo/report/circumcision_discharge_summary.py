"""Discharge Summary Report"""
import tempfile
from reportlab.platypus import Paragraph, PageBreak, ListFlowable, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm

from .. import database as db
from .. import config
from .doctemplate import DocTemplate, DefaultHeader, TableExpandable
from .stylesheet import get_stylesheet


def get_discharge_summary_elements(admission, session, pagesize=A5):
    patient = admission.patient

    stylesheet = get_stylesheet()
    elements = [
        DefaultHeader(title="CIRCUMCISION DISCHARGE SUMMARY")
    ]

    elements.append(Paragraph("Patient Details", stylesheet['heading_1']))

    address = ""
    if patient.permanent_address:
        address = unicode(patient.permanent_address.line_1)

    weight = None
    measurements = session.query(db.Measurements)\
                            .filter(db.Measurements.patient == patient)\
                            .filter(db.Measurements.weight != None)\
                            .order_by(db.Measurements.start_time.desc())\
                            .limit(1)
    if measurements.count() == 1:
        measurement = measurements.one()
        weight = measurement.weight
    str_weight = ""
    if weight is not None:
        str_weight = "{} kg".format(round(weight,1))

    demography = [
        [
            "Hospital No:", patient.hospital_no,
            "National ID No:", patient.national_id_no
        ],
        [
            'Name:', Paragraph(patient.name, stylesheet['default']),
            "Age/Sex:", "{0} / {1}".format(config.format_duration(patient.age), patient.sex)
        ],
        [
            'Address:', Paragraph(address, stylesheet['default']),
            'Weight:', str_weight
        ],
        [
            'Admitted:', config.format_date(admission.start_time),
            'Discharged:', config.format_date(admission.end_time)
        ]
    ]

    demography_table = TableExpandable(
        demography,
        colWidths=[18*mm, None, 22*mm, 28*mm],
        pagesize=pagesize, rightMargin=10*mm, leftMargin=10*mm,
        style=stylesheet['table-default'])

    #demography_table.setStyle(stylesheet['table-default'])

    elements.append(demography_table)
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("History & Physical Examination", stylesheet['heading_1']))

    if patient.allergies is not None:
        elements.append(Paragraph("<b>Allergic to {}</b>".format(patient.allergies), stylesheet['text']))

    components = [
        ("Past History", admission.past_history),
        ("Chest", admission.exam_chest), 
        ("Abdomen", admission.exam_abdomen),
        ("Genitalia", admission.exam_genitalia),
        ("Others", admission.exam_other)
    ]

    for label, component in components:
        if component is not None:
            elements.append(Paragraph(
                "<b>{0}</b> {1}".format(label, component),
                stylesheet['text']
            ))

    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("Procedure Details", stylesheet['heading_1']))

    procedures = session.query(db.SurgicalProcedure)\
                    .filter(db.SurgicalProcedure.parent == admission)

    for procedure in procedures:
        procedure_data = [
            ["Procedure:", Paragraph(procedure.procedure_name, stylesheet['default'])],
            ["Surgeon:", Paragraph(unicode(procedure.personnel), stylesheet['default'])],
            ["Date:", Paragraph(config.format_date(procedure.start_time), stylesheet['default'])],
            ["Findings:", Paragraph(unicode(procedure.findings), stylesheet['default'])]
        ]
        procedure_table = TableExpandable(
            procedure_data,
            colWidths=[20*mm, None],
            pagesize=pagesize, rightMargin=10*mm, leftMargin=10*mm,
            style=stylesheet['table-default'])
        elements.append(procedure_table)
        elements.append(HRFlowable(width="100%"))

    str_hospital_course = admission.hospital_course
    if str_hospital_course is None:
        str_hospital_course = ""
    elements.append(KeepTogether([
        Paragraph("Hospital Course", stylesheet['heading_1']),
        Paragraph(str_hospital_course, stylesheet['text'])
    ]))
    elements.append(HRFlowable(width="100%"))

    elements.append(KeepTogether([
        Paragraph("Discharge Advice", stylesheet['heading_1']),
        Paragraph(unicode(admission.discharge_advice), stylesheet['text'])
    ]))
    elements.append(HRFlowable(width="100%"))

    prescription = []
    for item in admission.prescription:
        prescription.append(Paragraph(
            "{0} {1}".format(item.drug.name, item.drug_order),
            stylesheet['prescription-item']
        ))
    elements.append(KeepTogether([
        Paragraph("Prescription", stylesheet['heading_1']),
        ListFlowable(prescription, style=stylesheet['list-default'])
    ]))
    elements.append(HRFlowable(width="100%"))

    elements.append(KeepTogether([
        Paragraph("Follow up", stylesheet['heading_1']),
        Paragraph(unicode(admission.follow_up), stylesheet['text'])
    ]))
    elements.append(HRFlowable(width="100%"))

    signature = [
        [""],
        [
            "Admitting Surgeon:",
            Paragraph(unicode(admission.personnel), stylesheet['default']),
            "",
            ""
        ],
        [""],
        [
            "Discharge Prepared By:",
            "",
            "Signature",
            ""
        ]
    ]

    signature_table = TableExpandable(
        signature,
        colWidths=[25*mm, None, 15*mm, None],
        pagesize=pagesize, rightMargin=10*mm, leftMargin=10*mm,
        style=stylesheet['table-default'])
    elements.append(signature_table)

    elements.append(PageBreak())
    
    return elements


def generate_discharge_summary(admission, session, pagesize=A5):
    filename = tempfile.mktemp(".pdf")

    patient_name = admission.patient.name
    if len(patient_name) > 20:
        patient_name = patient_name[0:20] + "..."

    page_footer = "{0}, {1}, {2} / {3}".format(
        admission.patient.hospital_no,
        patient_name,
        config.format_duration(admission.patient.age),
        admission.patient.sex)

    doc = DocTemplate(
        filename,
        page_footer=page_footer,
        page_header="Circumcision Discharge Summary",
        pagesize=pagesize,
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    doc.build(get_discharge_summary_elements(admission, session, pagesize))

    return filename

