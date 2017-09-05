"""Admission Notes Panel"""
from .dbrichtextctrl import DbRichTextCtrl


class EncounterNote(DbRichTextCtrl):
    """Admission Notes Panel"""
    def __init__(self, parent, session, str_note_attr, **kwds):
        super(EncounterNote, self).__init__(parent, session, **kwds)
        self.str_note_attr = str_note_attr


    def set_encounter(self, encounter):
        """Set the current ecnounter"""
        self.set_dbobject_attr(encounter, self.str_note_attr)
