"""Encounter Notebook Page"""
import wx

class EncounterNotebookPage(wx.Panel):
    """Encounter Notebook Page"""
    def __init__(self, parent, session, toolbar=True, **kwds):
        super(EncounterNotebookPage, self).__init__(parent, **kwds)

        self.session = session
        self.encounter = None

        self.editable = True

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = None
        if toolbar:
            self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
            self.sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)

        self.SetSizer(self.sizer)


    def set_editable(self, editable):
        """Set control to editable or not"""
        if editable:
            self.editable_on()
        else:
            self.editable_off()

        if self.editable != editable:
            self.Layout()
        self.editable = editable


    def editable_on(self):
        """Make controls editable"""
        self.toolbar.Show()


    def editable_off(self):
        """Lock controls"""
        self.toolbar.Hide()


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing.
          Always false in this panel as all changes are autosaved"""
        return False


    def save_changes(self):
        """Save changes. Everything is auto saved."""
        pass


    def set_encounter(self, encounter):
        """Set the current encounter"""
        self.encounter = encounter
