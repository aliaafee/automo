"""Progress Notes Panel"""
from .. import database as db
from .encounternotebooklist import EncounterNotebookList
from .dbform import DbDateField, DbMultilineStringField, DbRelationField


class ProgressPanel(EncounterNotebookList):
    """Surgical Procedures Notebook Page"""
    def __init__(self, parent, session, **kwds):
        self.fields = [
            DbDateField("Time Started", 'start_time', required=True),
            DbDateField("Time Completed", 'end_time', required=True),
            DbRelationField("Doctor", 'personnel', session.query(db.Doctor)),
            DbMultilineStringField("Subjective", 'subjective'),
            DbMultilineStringField("Objective", 'objective'),
            DbMultilineStringField("Assessment", 'assessment'),
            DbMultilineStringField("Plan", 'plan')
        ]
        super(ProgressPanel, self).__init__(parent, session, db.Progress, self.fields, **kwds)
