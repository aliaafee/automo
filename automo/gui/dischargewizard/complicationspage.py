"""Complications Page"""
from ... import database as db
from .. import dbform as fm
from .formpage import FormPage


class ComplicationsPage(FormPage):
    """Complications Page"""
    def __init__(self, parent, session):
        fields = [
            fm.OptionsRelationField("Complication Grade",
                                   'complication_grade',
                                   session.query(db.ComplicationGrade),
                                   value_formatter=lambda v:"Grade {0} - {1}".format(v.id, v.description),
                                   required=True),
            fm.CheckBoxField("Disability on Discharge", 'complication_disability'),
            fm.MultilineStringField("Complication Summary", 'complication_summary', lines=8)
        ]
        super(ComplicationsPage, self).__init__(parent, session, 
            "Surgical Complication Grade", db.Admission, fields)


    def must_skip(self):
        if not self.Parent.get_surgical_procedures():
            return True
        return False
