"""
AcDbTextCtrl

Auto complete Text ctrl that automatically updates database entry, on text change.

Modification of the text entry widget created by Raja Selvaraj <rajajs@gmail.com>
to enable options list to be obtained from sqlalchemy table with field "name"
Written to satisfy my need for a text entry widget with autocomplete and auto update
of database.

Find the original at https://github.com/RajaS/ACTextCtrl
"""
import wx

from .dbtextctrl import DbTextCtrl
from .dbqueryresultbox import DbQueryResultBox
from .events import DbCtrlChangedEvent


class AcDbTextCtrl(DbTextCtrl):
    """AcDbTextCtrl"""
    def __init__(self, parent, session, candidates_table,
                 max_results=20, **kwds):
        super(AcDbTextCtrl, self).__init__(parent, session,
                                           style=wx.TE_PROCESS_ENTER, **kwds)

        if wx.Platform == "__WXMAC__":
            #Popups dont work on mac, so act like a simple DbTextCtrl
            return

        self.candidates_table = candidates_table

        self.selected_object = None

        self.max_results = max_results
        self.select_candidates = []
        self.popup = ACPopup(self, self._on_click_choice)
        self.popupsize = wx.Size(-1, -1)

        self._set_bindings()

        self._screenheight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        self._popdown = True


    def _set_bindings(self):
        """
        One place to setup all the bindings
        """
        # text entry triggers update of the popup window
        self.Bind(wx.EVT_TEXT, self._on_text, self)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down, self)

        # loss of focus should hide the popup
        self.Bind(wx.EVT_KILL_FOCUS, self._on_focus_loss)


    def get_selected_object(self):
        return self.selected_object


    def SetValue(self, value):
        """
        Directly calling setvalue triggers textevent
        which results in popup appearing.
        To avoid this, call changevalue
        """
        super(AcDbTextCtrl, self).ChangeValue(value)


    def Clear(self):
        super(AcDbTextCtrl, self).ChangeValue("")
        self.selected_object = None


    def _on_text(self, event):
        """
        On text entry in the textctrl,
        Pop up the popup,
        or update candidates if its already visible
        """
        txt = self.GetValue()

        self.selected_object = None

        # if txt is empty (after backspace), hide popup
        # and save changes(ie: set data to "")
        if not txt:
            self._save_changes(event)
            if self.popup.IsShown():
                self.popup.Show(False)
                return

        # select candidates from database
        result = self.session.query(self.candidates_table)\
                             .filter(self.candidates_table.name.like("%{0}%".format(txt)))\
                             .order_by(self.candidates_table.name)\
                             .limit(self.max_results)

        self.select_candidates = []
        for candidate in result:
            self.select_candidates.append(candidate.name)

        self.popup.show_candidates(result, txt,
                                   self.GetScreenPositionTuple(), self.GetSizeTuple())
        #self.popup.show_candidates(self.select_candidates, txt,
        #                           self.GetScreenPositionTuple(), self.GetSizeTuple())


    def _on_focus_loss(self, event):
        """
        Close the popup when focus is lost
        """
        if self.db_object is not None and self.db_str_attr != "":
            self.SetValue(getattr(self.db_object, self.db_str_attr))
            self.SetInsertionPointEnd()

        if self.popup.IsShown():
            self.popup.Show(False)

        event.Skip()


    def _save_changes(self, event):
        if self.db_object is not None and self.db_str_attr != "":
            setattr(self.db_object, self.db_str_attr, self.GetValue())
            self.session.commit()

        event = DbCtrlChangedEvent(object=self.db_object)
        wx.PostEvent(self, event)


    def _on_key_down(self, event):
        """
        Handle key presses.
        Special keys are handled appropriately.
        For other keys, the event is skipped and allowed
        to be caught by ontext event
        """
        skip = True
        visible = self.popup.IsShown()
        sel = self.popup.candidatebox.GetSelection()

        # Escape key closes the popup if it is visible
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            if visible:
                self.popup.Show(False)
            if self.db_object is not None and self.db_str_attr != "":
                self.SetValue(getattr(self.db_object, self.db_str_attr))
                self.SetInsertionPointEnd()

        # Down key for navigation in list of candidates
        elif event.GetKeyCode() == wx.WXK_DOWN:
            if not visible:
                skip = True
            else:
                if sel + 1 < self.popup.candidatebox.GetItemCount():
                    self.popup.candidatebox.SetSelection(sel + 1)
                skip = False

        # Up key for navigation in list of candidates
        elif event.GetKeyCode() == wx.WXK_UP:
            if not visible:
                skip = True
            else:
                if sel > 0:
                    self.popup.candidatebox.SetSelection(sel - 1)
                skip = False

        # Enter - use current selection for text
        elif event.GetKeyCode() == wx.WXK_RETURN:
            if not visible:
                pass
            # Add option is only displayed
            elif self.popup.candidatebox.GetSelection() == -1:
                self.popup.Show(False)
                if self.db_object is not None and self.db_str_attr != "":
                    self.SetValue(getattr(self.db_object, self.db_str_attr))
                self.selected_object = None
            elif self.popup.candidatebox.GetSelection() == self.popup.add_index:
                self.selected_object = None
                self.SetValue(self.popup.add_text)
                self.SetInsertionPointEnd()

                candidates_count = self.session.query(self.candidates_table.name)\
                                    .filter(self.candidates_table.name == self.GetValue())\
                                    .count()
                if candidates_count == 0:
                    new_name = self.candidates_table(name=self.popup.add_text)
                    self.session.add(new_name)
                    self.session.commit()

                self.SetInsertionPointEnd()
                self.popup.Show(False)
                self._save_changes(event)
            else:
                self.selected_object = self.popup.get_selected()
                self.SetValue(unicode(self.selected_object))
                self.SetInsertionPointEnd()
                self.popup.Show(False)
                self._save_changes(event)

        # Tab  - set selected choice as text
        elif event.GetKeyCode() == wx.WXK_TAB:
            if visible:
                if self.popup.candidatebox.GetSelection() == self.popup.add_index:
                    self.selected_object = None
                    self.SetValue(self.popup.add_text)
                    self.SetInsertionPointEnd()
                else:
                    self.selected_object = self.popup.get_selected()
                    self.SetValue(unicode(self.selected_object))
                    self.SetInsertionPointEnd()
                skip = False

        if skip:
            event.Skip()


    def _on_click_choice(self, event):
        if self.popup.candidatebox.GetSelection() == self.popup.add_index:
            self.selected_object = None
            self.SetValue(self.popup.add_text)
            self.SetInsertionPointEnd()
        else:
            self.selected_object = self.popup.get_selected()
            self.SetValue(unicode(self.selected_object))
            self.SetInsertionPointEnd()




class ACPopup(wx.PopupWindow):
    """
    The popup that displays the candidates for
    autocompleting the current text in the textctrl
    """
    def __init__(self, parent, on_click_choice):
        wx.PopupWindow.__init__(self, parent)
        #self.candidatebox = wx.SimpleHtmlListBox(self, -1, choices=[], style=wx.BORDER_THEME)
        self.candidatebox = DbQueryResultBox(self)
        self.SetSize((100, 100))
        self.displayed_candidates = []
        self.add_index = -1
        self.add_text = ""
        self._popdown = True

        self._screenheight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        self.candidatebox.Bind(wx.EVT_LISTBOX, on_click_choice)


    def get_selected(self):
        """returns the item that is selected"""
        return self.candidatebox.get_selected_object()
        """
        TODO: Handle Pop Downs
        if self._popdown:
            return self.displayed_candidates[self.candidatebox.GetSelection()]
        return self.displayed_candidates[self.candidatebox.GetSelection() - 1]
        """

    def show_candidates(self, query_result, query_string, parent_screen_position, parent_size):
        """show the candidates box"""
        self.candidatebox.set_result(query_result, query_string, "Add: {0}".format(query_string))

        self.add_text = query_string
        self.add_index = self.candidatebox.GetItemCount() - 1

        #TODO: Donot show add option if exact match exists

        candidates_size = query_result.count() + 1

        self._resize_popup(candidates_size, parent_size)
        self._position_popup(parent_screen_position, parent_size)

        #TODO: Handle popdown

        self.candidatebox.SetSelection(0)

        if not self.IsShown():
            self.Show()


    def _resize_popup(self, candidate_count, parent_size):
        """
        Calculate the size for the popup to
        accomodate the candidates
        """
        #candidate_count = self.candidatebox.GetItemCount()
        if candidate_count == 0:
            candidate_count = 2.25
        else:
            candidate_count = min(5, candidate_count)
            candidate_count = max(2, candidate_count)
            candidate_count += 0.25

        charheight = self.candidatebox.GetCharHeight() + 7

        popup_height = int(float(charheight) * float(candidate_count))

        popupsize = wx.Size(parent_size[0], popup_height)

        self.candidatebox.SetSize(popupsize)
        self.SetClientSize(popupsize)


    def _position_popup(self, parent_screen_position, parent_size):
        """
        Calculate position of popup
        """
        left_x, upper_y = parent_screen_position

        _, height = parent_size
        _, popup_height = self.GetSizeTuple()

        if wx.Platform == "__WXMSW__":
            left_x -= 2
            height -= 2

        if upper_y + height + popup_height > self._screenheight:
            self._popdown = False
            self.SetPosition((left_x, upper_y - popup_height))
        else:
            self._popdown = True
            self.SetPosition((left_x, upper_y + height))
