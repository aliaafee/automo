import time
import math


def GenerateHeader(patient, canvas):
    canvas.drawString(40,513,patient.name) 
    canvas.drawString(178,513, "Bed : {0}".format(patient.bed_no))

    canvas.drawString(40,491,time.strftime("%d %B %Y"))
    canvas.drawString(178,491,str(patient.age))
    canvas.drawString(218,491,patient.sex)

    canvas.drawString(318,504,str(patient.hospital_no))
    canvas.drawString(318,492,"ID No : {0}".format(patient.national_id_no))
    
    canvas.drawString(40,300, patient.diagnosis)


def GeneratePrescription(patient, canvas):
    canvas.setFont("Helvetica", 10)
    GenerateHeader(patient, canvas)
    
    pages = int(math.floor(float(len(patient.rxs)) / 14.0) + 1)

    position = 242
    index = 1
    page = 1
    for row in patient.rxs:
        if (row.active):
            if (index > 14):
                canvas.drawString(318, 46, "page {0} of {1}".format(page, pages))
                canvas.showPage()
                canvas.setFont("Helvetica", 10)
                GenerateHeader(patient, canvas)
                position = 241
                index = 1
                page += 1
            totaIndex = ((page - 1)*14) + index
            canvas.drawString(40, position, "{0}) {1} {2}".format(totaIndex, row.drug_name, row.drug_order))
            position -= 14
            index += 1
    if pages > 1:
        canvas.drawString(318, 46, "page {0} of {1}".format(page, pages)) 
    canvas.showPage()
