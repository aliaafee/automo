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


def get_discharge_summary_elements(admission, session, pagesize=A4):
    patient = admission.patient

    stylesheet = get_stylesheet()

    #Patient Details
    patient_details = Paragraph("Name etec etc", stylesheet['default'])

    #Diagnosis
    diagnosis = ""

    #History and examination##############################################
    history_examination = []
    if patient.allergies is not None:
        history_examination.append(Paragraph("<b>Allergic to {}</b>".format(patient.allergies), stylesheet['text']))

    hx_components = [
        ("Chief Complaints", admission.chief_complaints),
        ("History of Present Illness", admission.history),
        ("Past History", admission.past_history)
    ]

    for label, component in hx_components:
        if component is not None:
            history_examination.append(Paragraph(
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
            history_examination.append(Paragraph(
                u"<b>Vital Signs:</b> {}".format(", ".join(vitals_str)),
                stylesheet['text']
            ))

    ex_components = [
        ("General", admission.general_inspection),
        ("Head", admission.exam_head),
        ("Neck", admission.exam_neck),
        ("Chest", admission.exam_chest),
        ("Abdomen", admission.exam_abdomen),
        ("Genitalia", admission.exam_genitalia),
        ("Pelvic/Rectal", admission.exam_pelvic_rectal),
        ("Extremities", admission.exam_extremities),
        ("Others", admission.exam_other)
    ]

    for label, component in ex_components:
        if component is not None:
            history_examination.append(Paragraph(
                "<b>{0}</b> {1}".format(label, component),
                stylesheet['text']
            ))


    #Reports#########################################################
    report_fields = {
        'imaging':['radiologist', 'impression', 'report'],
        'endoscopy':['endoscopist', 'impression', 'report'],
        'histopathology':['pathologist', 'impression', 'report']
    }
    reports = []
    reports.append(Paragraph("All enclosed", stylesheet['text']))
    result = session.query(db.Investigation)\
                .filter(db.Investigation.parent == admission)
    for report in result:
        if report.type in report_fields.keys():
            site = report.site
            if report.type == 'imaging':
                site = "{0} {1}".format(report.imaging_type, report.site)
            reports.append(Paragraph("<b>{0}</b> {1}".format(report.type.title(), site), stylesheet['text']))
            table_content = [
                [report_fields[report.type][0].title(), getattr(report, report_fields[report.type][0])],
                ["Impression", report.impression]
            ]
            report_table = TableExpandable(
                table_content,
                colWidths=[20*mm, None],
                pagesize=pagesize, rightMargin=40*mm, leftMargin=10*mm,
                style=stylesheet['table-default'])
            reports.append(report_table)

    #Treatment########################################################
    treatment = Paragraph("Conservative Management", stylesheet['text'])

    procedures = session.query(db.SurgicalProcedure)\
                    .filter(db.SurgicalProcedure.parent == admission)
    if procedures.count() > 0:
        treatment = []
        for procedure in procedures:
            treatment.append(Paragraph(unicode(procedure.procedure_name), stylesheet['heading_1']))
            info_content = [
                [
                    "Time",
                    config.format_datetime(procedure.start_time)
                ],
                [
                    "Surgeon",
                    Paragraph("<b>{}</b>".format(procedure.personnel), stylesheet['text']),
                    "Assistant(s)",
                    Paragraph(unicode(procedure.assistant), stylesheet['text'])
                ],
                [
                    "Anesthetist",
                    Paragraph(unicode(procedure.anesthetist), stylesheet['text'])
                ]
            ]
            info_table = TableExpandable(
                info_content,
                colWidths=[20*mm, None, 20*mm, None],
                pagesize=pagesize, rightMargin=40*mm, leftMargin=10*mm,
                style=stylesheet['table-default'])
            treatment.append(info_table)
            treatment.append(
                Paragraph(
                    "<b>Findings</b> {}".format(procedure.findings),
                    stylesheet['default']   
                )
            )
            treatment.append(
                Paragraph(
                    "<b>Procedure</b> {}".format(procedure.steps),
                    stylesheet['default']   
                )
            )

    #Hospital Course########################################################
    hospital_course = Paragraph(unicode(admission.hospital_course), stylesheet['default'])

    #Prescription
    prescription = []
    prescription_list = []
    for item in admission.prescription:
        if item.active:
            prescription_list.append(Paragraph(
                "{0} {1}".format(item.drug.name, item.drug_order),
                stylesheet['prescription-item']
            ))
    prescription.append(ListFlowable(prescription_list, style=stylesheet['list-default']))

    #Discharge Advice
    discharge_advice = Paragraph(unicode(admission.discharge_advice), stylesheet['default'])

    #Followup
    follow_up = Paragraph(unicode(admission.discharge_advice), stylesheet['default'])


    #Combine to one main table
    main_contents = [
        [
            Paragraph("Diagnosis", stylesheet['heading_1']),
            diagnosis
        ],
        [
            Paragraph("History & Examination", stylesheet['heading_1']),
            history_examination
        ],
        [
            Paragraph("Investigations", stylesheet['heading_1']),
            reports
        ],
        [
            Paragraph("Treatment", stylesheet['heading_1']),
            treatment
        ],
        [
            Paragraph("Hospital Course", stylesheet['heading_1']),
            hospital_course
        ],
        [
            Paragraph("Prescription", stylesheet['heading_1']),
            prescription
        ],
        [
            Paragraph("Advice on Discharge", stylesheet['heading_1']),
            discharge_advice
        ],
        [
            Paragraph("Follow up", stylesheet['heading_1']),
            follow_up
        ],
        [
            Paragraph("Admitting Surgeon", stylesheet['default']),
            Paragraph(unicode(admission.personnel), stylesheet['default'])
        ],
        [
            Paragraph("Discharge Prepared by", stylesheet['default']),
            ""
        ]
    ]

    main_table = TableExpandable(
        main_contents,
        colWidths=[30*mm, None],
        pagesize=pagesize, rightMargin=10*mm, leftMargin=10*mm,
        style=stylesheet['table-default'])

    elements = []
    elements.append(DefaultHeader(title="DISCHARGE SUMMARY"))
    elements.append(Paragraph("Patient Details", stylesheet['heading_1']))
    elements.append(patient_details)
    elements.append(main_table)

    return elements


def get_discharge_summary_elements2(admission, session, pagesize=A4):
    patient = admission.patient

    stylesheet = get_stylesheet()
    elements = [
        DefaultHeader(title="DISCHARGE SUMMARY")
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

    elements.append(demography_table)
    elements.append(HRFlowable(width="100%"))

    elements.append(Paragraph("History & Physical Examination", stylesheet['heading_1']))

    if patient.allergies is not None:
        elements.append(Paragraph("<b>Allergic to {}</b>".format(patient.allergies), stylesheet['text']))

    hx_components = [
        ("Chief Complaints", admission.chief_complaints),
        ("History of Present Illness", admission.history),
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
        ("General", admission.general_inspection),
        ("Head", admission.exam_head),
        ("Neck", admission.exam_neck),
        ("Chest", admission.exam_chest),
        ("Abdomen", admission.exam_abdomen),
        ("Genitalia", admission.exam_genitalia),
        ("Pelvic/Rectal", admission.exam_pelvic_rectal),
        ("Extremities", admission.exam_extremities),
        ("Others", admission.exam_other)
    ]

    for label, component in ex_components:
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
            ["Procedure:", Paragraph(unicode(procedure.procedure_name), stylesheet['default'])],
            ["Surgeon:", Paragraph(unicode(procedure.personnel), stylesheet['default'])],
            ["Time:", Paragraph(config.format_datetime(procedure.start_time), stylesheet['default'])],
            ["Findings:", Paragraph(unicode(procedure.findings), stylesheet['default'])]
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
        if item.active:
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
            "Admitting Doctor:",
            Paragraph(unicode(admission.personnel), stylesheet['default']),
            "",
            ""
        ],
        [
            "Prepared By:",
            "",
            "Signature:",
            ""
        ]
    ]

    signature_table = TableExpandable(
        signature,
        colWidths=[25*mm, None, 25*mm, None],
        pagesize=pagesize, rightMargin=10*mm, leftMargin=10*mm,
        style=stylesheet['table-default'])
    elements.append(signature_table)

    elements.append(PageBreak())
    
    return elements


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
        page_header="Discharge Summary",
        pagesize=pagesize,
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    doc.build(get_discharge_summary_elements(admission, session, pagesize))

    return filename
