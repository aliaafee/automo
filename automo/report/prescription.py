import datetime
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, ListFlowable
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm

from .. import config
from .stylesheet import get_stylesheet


class PrescriptionTemplate(SimpleDocTemplate):
    def __init__(self, filename, encounter):
        SimpleDocTemplate.__init__(
            self,
            filename,
            pagesize=A5,
            topMargin=115*mm,
            bottomMargin=10*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )
        self.encounter = encounter

        diagnoses = []
        for problem in self.encounter.problems:
            if problem.icd10class is not None:
                diagnoses.append(
                    "{0} - {1}".format(problem.icd10class.code, problem.icd10class.preferred_plain)
                )
        self.diagnosis = ", ".join(diagnoses)


    def _draw_prescription_header(self, patient, diagnosis, presc_canvas):
        """ Draw header of prescription """
        presc_canvas.drawString(15*mm, 181*mm, patient.name)

        presc_canvas.drawString(15*mm, 173*mm, config.format_date(datetime.date.today()))
        presc_canvas.drawString(63*mm, 173*mm, config.format_duration(patient.age))
        presc_canvas.drawString(82*mm, 173*mm, patient.sex)

        if hasattr(self.encounter, 'bed'):
            if self.encounter.bed is not None:
                presc_canvas.drawString(63*mm, 165*mm, "Bed : {0}".format(self.encounter.bed))

        presc_canvas.drawString(104*mm, 173*mm, str(patient.hospital_no))

        presc_canvas.drawString(104*mm, 165*mm, "ID No : {0}".format(patient.national_id_no))

        presc_canvas.drawString(15*mm, 106*mm, diagnosis)


    def onPage(self, this_canvas, document):
        this_canvas.saveState()
        this_canvas.setFont("Helvetica", 10)
        self._draw_prescription_header(self.encounter.patient, self.diagnosis, this_canvas)


    def build(self, flowables):
        SimpleDocTemplate.build(self, flowables,
                                onFirstPage=self.onPage,
                                onLaterPages=self.onPage)



def get_prescription_pdf(encounter, session):
    filename = tempfile.mktemp(".pdf")

    stylesheet = get_stylesheet()
    elements = []

    prescription = []
    for item in encounter.prescription:
        if item.active:
            prescription.append(Paragraph(
                "{0} {1}".format(item.drug.name, item.drug_order),
                stylesheet['prescription-item-big']
            ))
    elements.append(ListFlowable(prescription, style=stylesheet['list-big']))

    doc = PrescriptionTemplate(filename, encounter)
    doc.build(elements)

    return filename
