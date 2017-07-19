"""Admission Notes Panel"""
from dbrichtextctrl import DbRichTextCtrl


class AdmissionNotesPanel(DbRichTextCtrl):
    """Admission Notes Panel"""
    def __init__(self, parent, session, **kwds):
        super(AdmissionNotesPanel, self).__init__(parent, session, **kwds)


    def set_admission(self, admission, editable=True):
        """Set the current admission"""
        self.set_dbobject_attr(admission, 'admission_notes', editable)


class ProgressNotesPanel(DbRichTextCtrl):
    """Progress Notes Panel"""
    def __init__(self, parent, session, **kwds):
        super(ProgressNotesPanel, self).__init__(parent, session, **kwds)


    def set_admission(self, admission, editable=True):
        """Set the current admission"""
        self.set_dbobject_attr(admission, 'progress_notes', editable)


class DischargeSummaryPanel(DbRichTextCtrl):
    """Discharge Summary Panel"""
    def __init__(self, parent, session, **kwds):
        super(DischargeSummaryPanel, self).__init__(parent, session, **kwds)


    def set_admission(self, admission, editable=True):
        """Set the current admission"""
        self.set_dbobject_attr(admission, 'discharge_advice', editable)
