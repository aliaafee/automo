"""Patient View"""
from flask import Blueprint, render_template
from flask_login import login_required

from ... import database as db

patient_view = Blueprint('patient', __name__)


@patient_view.route('/')
@login_required
def patient_search():
    patients = db.Patient.query.all()
    return render_template('patient/patient_search.html', patients=patients, title="Find Patient")


@patient_view.route('/<patient_id>')
@login_required
def patient_file(patient_id):
    patient = db.Patient.query.filter(db.Patient.id == patient_id).one()
    title = patient.name
    return render_template('patient/patient_file.html', title=title, patient=patient)


@patient_view.route('/new_patient')
@login_required
def new_patient():
    new_patient = db.Patient()
    new_patient.name = "New Patient"
    db.s_session.add(new_patient)
    db.s_session.commit()
    return "Success"
