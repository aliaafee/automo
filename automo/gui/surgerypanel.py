"""Surgical Procedures Panel"""
from .. import config
from .. import database as db
from .encounternotebooklist import EncounterNotebookList
from .dbform import DbDateTimeField, DbStringField, DbMultilineStringField, DbRelationField


class SurgeryPanel(EncounterNotebookList):
    """Surgical Procedures Notebook Page"""
    def __init__(self, parent, session, **kwds):
        self.fields = [
            DbDateTimeField("Time Started", 'start_time', required=True),
            DbDateTimeField("Time Completed", 'end_time', required=True),
            DbRelationField("Surgeon", 'personnel', session.query(db.Doctor)),
            DbStringField("Preop Diagnosis", 'preoperative_diagnosis'),
            DbStringField("Postop Diagnosis", 'postoperative_diagnosis'),
            DbStringField("Procedure Name", 'procedure_name'),
            DbMultilineStringField("Findings", 'findings'),
            DbMultilineStringField("Steps", 'steps'),
        ]
        super(SurgeryPanel, self).__init__(parent, session, db.SurgicalProcedure, self.fields, **kwds)


    def subencounter_list_decorator(self, encounter_object, query_string):
        date_str = config.format_date(encounter_object.start_time)
        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td valign="top" >&bull;</td>'\
                        '<td valign="top"><b>{0}</b></td>'\
                        '<td width="100%">{1}</td>'\
                    '</tr>'\
                '</table></font>'

        return html.format(date_str, encounter_object.procedure_name)
