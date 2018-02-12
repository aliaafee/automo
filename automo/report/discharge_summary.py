"""Discharge Summary Report"""
import tempfile
import dateutil.relativedelta
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
    right_margin = 20*mm
    left_margin = 20*mm
    sidebar_width = 40*mm

    patient = admission.patient

    stylesheet = get_stylesheet()

    #Patient Details######################################################
    patient_details = []
    age = patient.get_age(now=admission.start_time)
    address = ""
    if patient.permanent_address:
        address = unicode(patient.permanent_address.line_1)
    demography = [
        [
            'Name:', Paragraph("<b>{}</b>".format(patient.name), stylesheet['default']),
            "Age/Sex:", Paragraph("<b>{0} / {1}</b>".format(config.format_duration(age), patient.sex), stylesheet['default'])
        ],
        [
            "Hospital No:", Paragraph("<b>{}</b>".format(patient.hospital_no), stylesheet['default']),
            "National ID:", Paragraph("<b>{}</b>".format(patient.national_id_no), stylesheet['default'])
        ],
        [
            'Address:', Paragraph("<b>{}</b>".format(address), stylesheet['default']),
        ]
    ]

    patient_details.append(TableExpandable(
        demography,
        colWidths=[18*mm, None, 18*mm, 20*mm],
        pagesize=pagesize, rightMargin=right_margin+sidebar_width, leftMargin=left_margin,
        style=stylesheet['table-default']))

    #Admission############################################################
    admission_details = []
    bed = admission.discharged_bed
    if admission.is_active():
        bed = admission.bed
    duration_str = ""
    if admission.end_time is not None:
        duration = dateutil.relativedelta.relativedelta(admission.end_time, admission.start_time)
        duration_str = config.format_duration_verbose(duration)
        
    admission_data = [
        [
            'Admitted:', config.format_date(admission.start_time),
            'Discharged:', config.format_date(admission.end_time),
            'Duration:', Paragraph(duration_str, stylesheet['default'])
        ],
        [
            'Ward:', unicode(bed.ward),
            'Bed:', unicode(bed)
        ]
    ]

    admission_details.append(TableExpandable(
        admission_data,
        colWidths=[18*mm, None, 18*mm, None, 12*mm, None],
        pagesize=pagesize, rightMargin=right_margin+sidebar_width, leftMargin=left_margin,
        style=stylesheet['table-default']))

    #Diagnosis############################################################
    diagnosis = []
    problem_strs = []
    for problem in admission.problems:
        code = [problem.icd10class.code]
        preferred = [problem.icd10class.preferred_plain]
        for modifer_cls in [problem.icd10modifier_class, problem.icd10modifier_extra_class]:
            if modifer_cls is not None:
                code.append(modifer_cls.code_short)
                preferred.append(modifer_cls.preferred)
        code_str = "".join(code)
        preferred_str = ", ".join(preferred)
        comment_str = ""
        if problem.comment is not None:
            comment_str = "({})".format(problem.comment)
        problem_strs.append("<b>{0} - {1}</b>{2}".format(code_str, preferred_str, comment_str))
    diagnosis.append(
        Paragraph(
            "<b>;</b>".join(problem_strs),
            stylesheet['default']
        )
    )

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

    measurements = session.query(db.Measurements)\
                            .filter(db.Measurements.parent == admission)\
                            .filter(db.Measurements.patient == patient)\
                            .order_by(db.Measurements.start_time)\
                            .limit(1)
    if measurements.count() == 1:
        measurement = measurements.one()
        measurements_str = []
        measurement_components = [
            ("Weight", measurement.weight, "kg", 0),
            ("Height", measurement.height, "m", 0),
            (u"BMI", None if measurement.bmi is None else round(measurement.bmi, 2), u"kg/m\u00B2", 0),
        ]
        for label, value, unit, dp in measurement_components:
            if value is not None:
                value_adjusted = value
                measurements_str.append(u"<b>{0}</b> {1} {2}".format(label, value_adjusted, unit))
        if measurements_str:
            history_examination.append(Paragraph(
                u"<b>Measurements:</b> {}".format(", ".join(measurements_str)),
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
                .filter(db.Investigation.parent == admission)\
                .order_by(db.Investigation.start_time)
    for report in result:
        if report.type in report_fields.keys():
            site = report.site
            if report.type == 'imaging':
                site = "{0} {1}".format(report.imaging_type, report.site)
            reports.append(Paragraph("<b>{0}</b> {1}".format(report.type.title(), site), stylesheet['text']))
            table_content = [
                ["Time", config.format_datetime(report.start_time)],
                [report_fields[report.type][0].title(), getattr(report, report_fields[report.type][0])],
                ["Impression", report.impression]
            ]
            report_table = TableExpandable(
                table_content,
                colWidths=[20*mm, None],
                pagesize=pagesize, rightMargin=right_margin+sidebar_width, leftMargin=left_margin,
                style=stylesheet['table-default'])
            reports.append(report_table)
            reports.append(HRFlowable(width="100%"))

    #Treatment########################################################
    treatment = [Paragraph("Conservative Management", stylesheet['text'])]

    procedures = session.query(db.SurgicalProcedure)\
                    .filter(db.SurgicalProcedure.parent == admission)\
                    .order_by(db.SurgicalProcedure.start_time)
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
                pagesize=pagesize, rightMargin=right_margin+sidebar_width, leftMargin=left_margin,
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
            treatment.append(HRFlowable(width="100%"))

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
    follow_up = Paragraph(unicode(admission.follow_up), stylesheet['default'])


    #Combine to one main table
    main_contents = [
        [
            Paragraph("Patient", stylesheet['heading_1']),
            patient_details
        ],
        None,
        [
            Paragraph("Admission", stylesheet['heading_1']),
            admission_details
        ],
        None,
        [
            Paragraph("Diagnosis", stylesheet['heading_1']),
            diagnosis
        ],
        None,
        [
            Paragraph("History & Examination", stylesheet['heading_1']),
            history_examination
        ],
        None,
        [
            Paragraph("Investigations", stylesheet['heading_1']),
            reports[0]
        ]
    ]

    if len(reports) > 1:
        for item in reports[1:]:
            main_contents.append(["", item])

    main_contents.append(None)

    main_contents.append([
            Paragraph("Treatment", stylesheet['heading_1']),
            treatment[0]
        ])

    if len(treatment) > 1:
        for item in treatment[1:]:
            main_contents.append(["", item])

    main_contents.extend([
        None,
        [
            Paragraph("Hospital Course", stylesheet['heading_1']),
            hospital_course
        ],
        None,
        [
            Paragraph("Prescription", stylesheet['heading_1']),
            prescription
        ],
        None,
        [
            Paragraph("Advice on Discharge", stylesheet['heading_1']),
            discharge_advice
        ],
        None,
        [
            Paragraph("Follow up", stylesheet['heading_1']),
            follow_up
        ],
        None,
        [
            Paragraph("Admitting Surgeon", stylesheet['heading_1']),
            Paragraph(unicode(admission.personnel), stylesheet['default'])
        ],
        None,
        [
            Paragraph("Discharge Prepared by", stylesheet['heading_1']),
            ""
        ]
    ])

    elements = []
    if admission.is_active():
        elements.append(DefaultHeader(title="!!DRAFT!! DISCHARGE SUMMARY !!DRAFT!!"))
    else:
        elements.append(DefaultHeader(title="DISCHARGE SUMMARY"))

    elements.append(Paragraph('<para alignment="center">Department of Surgery</para>', stylesheet['heading_1']))

    elements.append(Paragraph('&nbsp;', stylesheet['default']))

    elements.append(Paragraph('&nbsp;', stylesheet['default']))

    for row in main_contents:
        if row is None:
            elements.append(HRFlowable(width="100%"))
        else:
            table = TableExpandable(
                [row],
                colWidths=[sidebar_width, None],
                pagesize=pagesize, rightMargin=right_margin, leftMargin=left_margin,
                style=stylesheet['table-default'])
            elements.append(table)

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
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=25*mm,
        bottomMargin=25*mm
    )
    doc.build(get_discharge_summary_elements(admission, session, pagesize))

    return filename
