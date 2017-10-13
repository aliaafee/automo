"""Discharge Summary Report"""
import tempfile
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle, ListFlowable, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.pagesizes import A5, A4, cm, A3
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

    demography_table = TableExpandable(
        demography,
        colWidths=[18*mm, None, 22*mm, 28*mm],
        pagesize=pagesize, rightMargin=10*mm, leftMargin=10*mm,
        style=stylesheet['table-default'])

    #demography_table.setStyle(stylesheet['table-default'])

    elements.append(demography_table)
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("Procedure Details", stylesheet['heading_1']))

    procedures = session.query(db.SurgicalProcedure)\
                    .filter(db.SurgicalProcedure.parent == admission)

    for procedure in procedures:
        procedure_data = [
            ["Procedure:", Paragraph(procedure.procedure_name, stylesheet['default'])],
            ["Surgeon:", Paragraph(unicode(procedure.personnel), stylesheet['default'])],
            ["Time:", Paragraph(config.format_datetime(procedure.start_time), stylesheet['default'])],
            ["Findings:", Paragraph(procedure.findings, stylesheet['default'])]
        ]
        procedure_table = TableExpandable(
            procedure_data,
            colWidths=[20*mm, None],
            pagesize=pagesize, rightMargin=10*mm, leftMargin=10*mm,
            style=stylesheet['table-default'])
        elements.append(procedure_table)
        elements.append(HRFlowable(width="100%"))


    elements.append(Paragraph("Hospital Course", stylesheet['heading_1']))
    elements.append(Paragraph(unicode(admission.hospital_course), stylesheet['text']))
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("Discharge Advice", stylesheet['heading_1']))
    elements.append(Paragraph(unicode(admission.discharge_advice), stylesheet['text']))
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("Prescription", stylesheet['heading_1']))
    prescription = []
    for item in admission.prescription:
        prescription.append(Paragraph(
            "{0} {1}".format(item.drug.name, item.drug_order),
            stylesheet['prescription-item']
        ))
    elements.append(ListFlowable(prescription, style=stylesheet['list-default']))
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("Follow up", stylesheet['heading_1']))
    elements.append(Paragraph(unicode(admission.follow_up), stylesheet['text']))
    elements.append(HRFlowable(width="100%"))

    signature = [
        [
            "Doctor:",
            Paragraph(unicode(admission.personnel), stylesheet['default']),
            "Signature:",
            ""
        ]
    ]

    signature_table = TableExpandable(
        signature,
        colWidths=[None, None],
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
        pagesize=pagesize,
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=10*mm,
        bottomMargin=15*mm
    )
    doc.build(admission.get_discharge_summary_elements(session, pagesize))

    return filename
