import time


def GeneratePrescription(patient, canvas):
    canvas.setFont("Helvetica", 10)

    canvas.drawString(40,535,patient.name)
    canvas.drawString(40,513,time.strftime("%d %B %Y"))
    canvas.drawString(178,535, "Bed : {0}".format(patient.bed_no))
    canvas.drawString(178,513,str(patient.age))
    canvas.drawString(218,513,patient.sex)
    canvas.drawString(318,526,str(patient.hospital_no))
    canvas.drawString(318,514,"ID No : {0}".format(patient.national_id_no))
    canvas.drawString(40,340, patient.diagnosis)

    position = 300
    index = 1
    for row in patient.rxs:
        if (row.active):
            canvas.drawString(40, position, "{0}) {1} {2}".format(index, row.drug_name, row.drug_order))
            position -= 18
            index += 1
    canvas.showPage()
