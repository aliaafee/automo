"""Print functions"""
import time
import math
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5, cm
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from sqlalchemy import and_

from database import Patient, Rx


class PageNumCanvas(canvas.Canvas):
    """
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    """
    def __init__(self, *args, **kwargs):
        """Constructor"""
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """
        Add the page number, dont draw page number if only one page
        """
        if page_count == 1:
            return

        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 9)
        self.drawRightString(195*mm, 20*mm, page)




def generate_patient_list(session, docfilename):
    """ Generate list of prescriptions """
    doc = SimpleDocTemplate(
        docfilename,
        pagesize=A4,
        rightMargin=12,
        leftMargin=12,
        topMargin=25*mm,
        bottomMargin=25*mm
    )

    style_sheet = getSampleStyleSheet()

    elements = []

    data = [
        [
            Paragraph("<b>Prescriptions {0}</b>".format(time.strftime("%d %B %Y")),
            style_sheet["BodyText"]),
            '', '', '',
            'Prescription Hand Over To Pharmacy', '',
            'Medication Recieved To Ward', ''
        ],
        ['Bed', 'Patient Name', 'ID No', 'Hosp No', 'Name', 'Sign', 'Name', 'Sign'],
    ]

    for patient in session.query(Patient).filter(Patient.active == True).order_by(Patient.bed_no):
        bed_no = Paragraph("<para>{0}</para>".format(patient.bed_no), style_sheet["BodyText"])
        name = Paragraph("<para>{0}</para>".format(patient.name), style_sheet["BodyText"])
        national_id_no = Paragraph("<para>{0}</para>".format(patient.national_id_no), style_sheet["BodyText"])
        hospital_no = Paragraph("<para>{0}</para>".format(patient.hospital_no), style_sheet["BodyText"])

        data.append([bed_no, name, national_id_no, hospital_no])

    t = Table(
        data,
        colWidths=[1.5*cm, 4*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm],
        repeatRows=[0, 1]
    )

    t.setStyle(TableStyle([
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('BOX', (0, 1), (-1, 1), 1, colors.black),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (4, 0), (5, -1), 1, colors.black),
        ('BOX', (6, 0), (7, -1), 1, colors.black),
        ('SPAN', (4, 0), (5, 0)),
        ('SPAN', (6, 0), (7, 0)),
        ('SPAN', (0, 0), (3, 0)),
        ('ALIGN', (4, 0), (7, 0), 'CENTER'),
        ('FONTSIZE', (4, 0), (7, 0), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    elements.append(t)

    doc.build(elements, canvasmaker=PageNumCanvas)


def generate_patient_census_list(session, docfilename):
    """ Generate census list """
    doc = SimpleDocTemplate(
        docfilename,
        pagesize=A4,
        rightMargin=12,
        leftMargin=12,
        topMargin=25*mm,
        bottomMargin=25*mm
    )

    style_sheet = getSampleStyleSheet()

    elements = []

    data = [
        [
            Paragraph("<b>Census {0}</b>".format(time.strftime("%d %B %Y")), style_sheet["BodyText"]),
            '', ''
        ],
        ['#', 'Hosp No', 'Bed', 'Patient Name'],
    ]

    patients = session.query(Patient).order_by(Patient.bed_no)
    for i, patient in enumerate(patients):
        index = Paragraph("<para>{0}</para>".format(i+1), style_sheet["BodyText"])
        bed_no = Paragraph("<para>{0}</para>".format(patient.bed_no), style_sheet["BodyText"])
        name = Paragraph("<para>{0}</para>".format(patient.name), style_sheet["BodyText"])
        hospital_no = Paragraph("<para>{0}</para>".format(patient.hospital_no), style_sheet["BodyText"])

        data.append([index, hospital_no, bed_no, name])

    t = Table(
        data,
        colWidths=[1*cm, 4*cm, 2.5*cm, 12*cm],
        repeatRows=[0, 1]
    )

    t.setStyle(TableStyle([
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('BOX', (0, 1), (-1, 1), 1, colors.black),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (0, 0), (3, 0))
    ]))

    elements.append(t)

    doc.build(elements, canvasmaker=PageNumCanvas)


def draw_prescription_header(patient, doctor_name, presc_canvas):
    """ Draw header of prescription """
    presc_canvas.drawString(15*mm, 181*mm, patient.name)

    presc_canvas.drawString(15*mm, 173*mm, time.strftime("%d %B %Y"))
    presc_canvas.drawString(63*mm, 173*mm, str(patient.age))
    presc_canvas.drawString(82*mm, 173*mm, patient.sex)

    presc_canvas.drawString(63*mm, 165*mm, "Bed : {0}".format(patient.bed_no))

    presc_canvas.drawString(104*mm, 173*mm, str(patient.hospital_no))

    presc_canvas.drawString(104*mm, 165*mm, "ID No : {0}".format(patient.national_id_no))

    presc_canvas.drawString(15*mm, 106*mm, patient.diagnosis)

    if doctor_name != "":
        presc_canvas.drawString(29*mm, 10*mm, "DR. {0}".format(doctor_name))


def draw_prescription(session, patient, doctor_name, presc_canvas):
    """ Draw the prescription, overflow into new page if too long """
    presc_canvas.setFont("Helvetica", 10)
    draw_prescription_header(patient, doctor_name, presc_canvas)

    active_rx_count = session.query(Rx)\
                             .filter(and_(Rx.patient_id == patient.id, Rx.active == True))\
                             .count()
    pages = int(math.floor(float(active_rx_count) / 14.0) + 1)

    position = 85*mm
    index = 1
    page = 1
    for row in patient.rxs:
        if row.active:
            if index > 14:
                presc_canvas.drawString(130*mm, 10*mm, "page {0} of {1}".format(page, pages))
                presc_canvas.showPage()
                presc_canvas.setFont("Helvetica", 10)
                draw_prescription_header(patient, doctor_name, presc_canvas)
                position = 241
                index = 1
                page += 1
            total_index = ((page - 1)*14) + index
            presc_canvas.drawString(14*mm, position, "{0}) {1} {2}"\
                        .format(total_index, row.drug_name, row.drug_order))
            position -= 5*mm
            index += 1
    if pages > 1:
        presc_canvas.drawString(130*mm, 10*mm, "page {0} of {1}".format(page, pages))
    presc_canvas.showPage()


def generate_prescription(session, patient, doctor_name, filename):
    """ Generate prescription """
    presc_canvas = canvas.Canvas(filename, pagesize=A5)

    draw_prescription(session, patient, doctor_name, presc_canvas)

    presc_canvas.save()


def generate_all_prescriptions(session, doctor_name, filename):
    """ Generate all prescriptions """
    presc_canvas = canvas.Canvas(filename, pagesize=A5)

    for patient in session.query(Patient).filter(Patient.active == True).order_by(Patient.bed_no):
        draw_prescription(session, patient, doctor_name, presc_canvas)

    presc_canvas.save()
