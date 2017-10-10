"""Discharge Summary Report"""
import tempfile
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle, ListFlowable
from reportlab.lib.pagesizes import A5, A4, cm
from reportlab.lib.units import mm

from .. import database as db
from .. import config
from .doctemplate import DocTemplate
from .stylesheet import get_stylesheet


def get_discharge_summary_elements(admission, session):
    patient = admission.patient

    stylesheet = get_stylesheet()
    elements = [
        Paragraph("INDIRA GANDHI MEMORIAL HOSPITAL", stylesheet["header"]),
        Paragraph("Kan'baa Aisaarani Hingun, Male', 20402, Republic of Maldives", stylesheet["header-subscript"]),
        Paragraph("CIRCUMCISION DISCHARGE SUMMARY", stylesheet["title"])
    ]

    elements.append(Paragraph("Patient Details", stylesheet['heading_1']))

    address = ""
    if patient.permanent_address:
        address = patient.permanent_address.line_1

    demography = [
        [
            'Name:', Paragraph(patient.name, stylesheet['default']),
            "Hospital No:", patient.hospital_no
        ],
        [
            'Address:', Paragraph(address, stylesheet['default']),
            "Age/Sex:", "{0} / {1}".format(config.format_duration(patient.age), patient.sex)
        ],
        [
            'Admitted:', config.format_date(admission.start_time),
            'Discharged:', config.format_date(admission.end_time)
        ]
    ]

    demography_table = Table(
        demography,
        colWidths=[18*mm, 60*mm, 22*mm, 28*mm])

    demography_table.setStyle(stylesheet['table-default'])

    elements.append(demography_table)

    elements.append(Paragraph("Procedure Details", stylesheet['heading_1']))

    procedures = session.query(db.SurgicalProcedure)\
                    .filter(db.SurgicalProcedure.parent == admission)

    for procedure in procedures:
        procedure_data = [
            ["Procedure:", procedure.procedure_name],
            ["Surgeon:", unicode(procedure.personnel)],
            ["Time:", config.format_datetime(procedure.start_time)],
            ["Findings", procedure.findings]
        ]
        procedure_table = Table(
            procedure_data,
            colWidths=[18*mm, 110*mm],
            style=stylesheet['table-default'])
        elements.append(procedure_table)


    elements.append(Paragraph("Hospital Course", stylesheet['heading_1']))
    elements.append(Paragraph(admission.hospital_course, stylesheet['default']))

    elements.append(Paragraph("Discharge Advice", stylesheet['heading_1']))
    elements.append(Paragraph(admission.discharge_advice, stylesheet['default']))

    elements.append(Paragraph("Prescription", stylesheet['heading_1']))
    prescription = []
    for item in admission.prescription:
        prescription.append(Paragraph(
            "{0} {1}".format(item.drug.name, item.drug_order),
            stylesheet['default']
        ))
    elements.append(ListFlowable(prescription, style=stylesheet['list-default']))

    elements.append(Paragraph("Follow up", stylesheet['heading_1']))
    elements.append(Paragraph(admission.follow_up, stylesheet['default']))

    elements.append(Paragraph("Admitting Surgeon: {}".format(unicode(admission.personnel)), stylesheet['heading_2']))
    
    return elements


def generate_discharge_summary(admission, session):
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
        pagesize=A5,
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=10*mm,
        bottomMargin=15*mm
    )
    doc.build(admission.get_discharge_summary_elements(session))

    return filename
