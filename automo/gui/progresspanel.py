"""Progress Notes Panel"""
from .. import database as db
from .encounternotebooklist import EncounterNotebookList
from .dbform import DbDateTimeField, DbMultilineStringField, DbRelationField


class ProgressPanel(EncounterNotebookList):
    """Surgical Procedures Notebook Page"""
    def __init__(self, parent, session, **kwds):
        self.fields = [
            DbDateTimeField("Time", 'examination_time', required=True),
            DbRelationField("Doctor", 'personnel', session.query(db.Doctor)),
            DbMultilineStringField("Subjective", 'subjective'),
            DbMultilineStringField("Objective", 'objective'),
            DbMultilineStringField("Assessment", 'assessment'),
            DbMultilineStringField("Plan", 'plan')
        ]
        super(ProgressPanel, self).__init__(parent, session, db.Progress, self.fields, **kwds)