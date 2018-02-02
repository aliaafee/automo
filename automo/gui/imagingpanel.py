"""Progress Notes Panel"""
from .. import config
from .. import database as db
from .encounternotebooklist import EncounterNotebookList
from .dbform import DbDateTimeField, DbMultilineStringField, DbStringField, DbRelationField


class ImagingPanel(EncounterNotebookList):
    """Surgical Procedures Notebook Page"""
    def __init__(self, parent, session, **kwds):
        self.fields = [
            DbDateTimeField("Time", 'record_time', required=True),
            DbStringField("Imagin Type", 'imaging_type'),
            DbStringField("Site", 'site'),
            DbStringField("Radiologist", 'radiologist'),
            DbMultilineStringField("Impression", 'impression'),
            DbMultilineStringField("Report", 'report')
        ]
        super(ImagingPanel, self).__init__(parent, session, db.Imaging, self.fields, **kwds)


    def subencounter_list_decorator(self, encounter_object, query_string):
        """Decorator of Subencounter List"""
        date_str = config.format_date(encounter_object.start_time)
        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td valign="top">&bull;</td>'\
                        '<td valign="top"><b>{0}</b></td>'\
                        '<td valign="top" width="100%">{1} {2}</td>'\
                    '</tr>'\
                '</table></font>'

        return html.format(date_str, encounter_object.imaging_type, encounter_object.site)