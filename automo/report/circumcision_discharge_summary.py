"""Discharge Summary Report"""
import string
import tempfile
from reportlab.platypus import Paragraph, PageBreak, ListFlowable, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from .. import config
from .. import database as db
from .. import config
from .doctemplate import DocTemplate, DefaultHeader, TableExpandable
from .stylesheet import get_stylesheet


def get_discharge_summary_elements(admission, session, pagesize=A4):
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
                            .filter(db.Measurements.parent == admission)\
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
        colWidths=[22*mm, None, 22*mm, 28*mm],
        pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
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
            pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
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
        colWidths=[28*mm, None, 15*mm, None],
        pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
        style=stylesheet['table-default'])
    elements.append(signature_table)

    elements.append(PageBreak())
    
    return elements


def get_admission_summary_elements(admission, session, pagesize=A4):
    patient = admission.patient

    stylesheet = get_stylesheet()
    elements = [
        DefaultHeader(title="CIRCUMCISION ADMISSION SHEET")
    ]

    elements.append(Paragraph("Patient Details", stylesheet['heading_1']))

    address = ""
    if patient.permanent_address:
        address = unicode(patient.permanent_address.line_1)

    weight = None
    measurements = session.query(db.Measurements)\
                            .filter(db.Measurements.parent == admission)\
                            .filter(db.Measurements.patient == patient)\
                            .filter(db.Measurements.weight != None)\
                            .order_by(db.Measurements.start_time)\
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
            'Admitted:', config.format_date(admission.start_time)
        ]
    ]

    demography_table = TableExpandable(
        demography,
        colWidths=[18*mm, None, 22*mm, 28*mm],
        pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
        style=stylesheet['table-default'])

    #demography_table.setStyle(stylesheet['table-default'])

    elements.append(demography_table)
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("History & Physical Examination", stylesheet['heading_1']))

    if patient.allergies is not None:
        elements.append(Paragraph("<b>Allergic to {}</b>".format(patient.allergies), stylesheet['text']))

    hx_components = [
        ("Past History", admission.past_history)
    ]

    for label, component in hx_components:
        if component is not None:
            elements.append(Paragraph(
                "<b>{0}</b> {1}".format(label, component),
                stylesheet['text']
            ))

    vitals = session.query(db.VitalSigns)\
                            .filter(db.VitalSigns.parent == admission)\
                            .filter(db.VitalSigns.patient == patient)\
                            .order_by(db.VitalSigns.start_time)\
                            .limit(1)
    if vitals.count() == 1:
        vital = vitals.one()
        vitals_str = []
        bp = None
        if vital.diastolic_bp is not None and vital.systolic_bp is not None:
            bp = "{0}/{1}".format(int(round(vital.systolic_bp, 0)), int(round(vital.diastolic_bp, 0)))
        vital_components = [
            ("Pulse", vital.pulse_rate, "bpm", 0),
            ("BP", bp, "mmHg", None),
            ("RR", vital.respiratory_rate, "bpm", 0),
            (u"T\u00B0", vital.temperature, u"\u00B0C", 1)
        ]
        for label, value, unit, dp in vital_components:
            if value is not None:
                value_adjusted = value
                if dp is not None:
                    if dp == 0:
                        value_adjusted = int(round(value, 0))
                    else:
                        value_adjusted = round(value, dp)
                vitals_str.append(u"<b>{0}</b> {1} {2}".format(label, value_adjusted, unit))
        if vitals_str:
            elements.append(Paragraph(
                u"<b>Vital Signs:</b> {}".format(", ".join(vitals_str)),
                stylesheet['text']
            ))

    ex_components = [
        ("Chest", admission.exam_chest),
        ("Abdomen", admission.exam_abdomen),
        ("Genitalia", admission.exam_genitalia),
        ("Others", admission.exam_other)
    ]

    for label, component in ex_components:
        if component is not None:
            elements.append(Paragraph(
                "<b>{0}</b> {1}".format(label, component),
                stylesheet['text']
            ))

    elements.append(HRFlowable(width="100%"))

    elements.append(KeepTogether([
        Paragraph("Preoperative Orders", stylesheet['heading_1']),
        Paragraph(unicode(admission.preoperative_orders), stylesheet['text'])
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
            "Admission Sheet Prepared By:",
            "",
            "Signature",
            ""
        ]
    ]

    signature_table = TableExpandable(
        signature,
        colWidths=[25*mm, None, 15*mm, None],
        pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
        style=stylesheet['table-default'])
    elements.append(signature_table)

    elements.append(PageBreak())
    
    return elements



def get_ot_note_elements(admission, session, pagesize=A4):
    patient = admission.patient

    stylesheet = get_stylesheet()
    elements = [
        DefaultHeader(title="CIRCUMCISION OPERATIVE NOTE")
    ]

    elements.append(Paragraph("Patient Details", stylesheet['heading_1']))

    address = ""
    if patient.permanent_address:
        address = unicode(patient.permanent_address.line_1)

    weight = None
    measurements = session.query(db.Measurements)\
                            .filter(db.Measurements.parent == admission)\
                            .filter(db.Measurements.patient == patient)\
                            .filter(db.Measurements.weight != None)\
                            .order_by(db.Measurements.start_time)\
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
        ]
    ]

    demography_table = TableExpandable(
        demography,
        colWidths=[18*mm, None, 22*mm, 28*mm],
        pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
        style=stylesheet['table-default'])

    elements.append(demography_table)
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("Procedure Details", stylesheet['heading_1']))

    details = [
        ["Surgeon:", "Assistant:"],
        [""],
        ["Anesthetist:", "Anesthesia:"],
        [""],
        ["Nurse:"],
        [""],
        ["Type of Operation:"],
        [u"     Open [ ]"],
        [u"     Plastibell [ ]"],
        [u"     Other:"],
        [""],
        ["Operative Findings"],
        [u"     Normal [ ]"],
        [u"     Phimosis [ ]"],
        [u"     Other Findings:"],
        [""],
        [""],
        [""],
        [""]
    ]

    details_table = TableExpandable(
        details,
        colWidths=[ None, None],
        pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
        style=stylesheet['table-default'])
    elements.append(details_table)
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("Post Operative Orders", stylesheet['heading_1']))

    meds = string.split(config.CIRCUM_MEDS, ";")

    prescription = []
    for med in meds:
        if med != "":
            prescription.append(
                Paragraph(med, stylesheet['prescription-item'])
            )

    elements.append(ListFlowable(prescription, style=stylesheet['list-default']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))
    elements.append(Paragraph(" ", stylesheet['text']))


    signature = [
        [""],
        [
            "Signature:",
            "",
            "",
            ""
        ]
    ]

    signature_table = TableExpandable(
        signature,
        colWidths=[25*mm, None, 15*mm, None],
        pagesize=pagesize, rightMargin=20*mm, leftMargin=20*mm,
        style=stylesheet['table-default'])
    elements.append(signature_table)

    print elements

    return elements




def generate_ot_note(admission, session, pagesize=A4):
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
        page_header="Operative Note",
        pagesize=pagesize,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    doc.build(get_ot_note_elements(admission, session, pagesize))

    return filename


def generate_discharge_summary(admission, session, pagesize=A4):
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
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    doc.build(get_discharge_summary_elements(admission, session, pagesize))

    return filename


def generate_admission_summary(admission, session, pagesize=A4):
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
        page_header="Circumcision Admission Sheet",
        pagesize=pagesize,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    doc.build(get_admission_summary_elements(admission, session, pagesize))

    return filename
