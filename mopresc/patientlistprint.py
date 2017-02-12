import time

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, cm
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas

from database import Patient


class PageNumCanvas(canvas.Canvas):
    """
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    """
 
    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
 
    #----------------------------------------------------------------------
    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()
 
    #----------------------------------------------------------------------
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
 
    #----------------------------------------------------------------------
    def draw_page_number(self, page_count):
        """
        Add the page number
        """
        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 9)
        self.drawRightString(195*mm, 272*mm, page)
 
#----------------------------------------------------------------------


def GeneratePatientList(session, docfilename):
    doc = SimpleDocTemplate(
        docfilename, 
        pagesize = A4,
        rightMargin = 12,
        leftMargin = 12,
        topMargin = 72,
        bottomMargin = 48
    )

    styleSheet = getSampleStyleSheet()

    elements = []

    heading = Paragraph('Prescriptions {0}'.format(time.strftime("%d %B %Y")), styleSheet["Heading1"])

    elements.append(heading)

    data= [
        ['', '', '', '', 'Prescription Hand Over To Pharmacy', '', 'Medication Recieved To Ward', ''],
        ['Bed', 'Patient Name', 'ID No', 'Hosp No', 'Name', 'Sign', 'Name', 'Sign'],
    ]

    index = 1
    for patient in session.query(Patient).order_by(Patient.bed_no):
        bed_no = Paragraph("<para>{0}</para>".format(patient.bed_no), styleSheet["BodyText"])
        name = Paragraph("<para>{0}</para>".format(patient.name), styleSheet["BodyText"])
        national_id_no = Paragraph("<para>{0}</para>".format(patient.national_id_no), styleSheet["BodyText"])
        hospital_no = Paragraph("<para>{0}</para>".format(patient.hospital_no), styleSheet["BodyText"])


        data.append([bed_no, name, patient.national_id_no, patient.hospital_no])
        index += 1

    t=Table(
        data, 
        colWidths=[1.5*cm, 4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm],
        repeatRows=[0,1]
    )

    t.setStyle(TableStyle([
        ('ALIGN',(0,1),(-1,1),'CENTER'),
        ('BOX', (0,1),(-1,1),1,colors.black),
        ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('BOX', (4,0), (5,-1), 1, colors.black),
        ('BOX', (6,0), (7,-1), 1, colors.black),
        ('FONTSIZE', (4,0), (7,0), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')

    ]))
    
    elements.append(t)

    doc.build(elements, canvasmaker=PageNumCanvas)
