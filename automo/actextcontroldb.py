import wx
import  wx.lib.newevent

from actextcontrol import ACTextControl

ACTextCtrlDoneEditEvent, EVT_ACT_DONE_EDIT = wx.lib.newevent.NewEvent()


# Modification of the text entry widget created by Raja Selvaraj <rajajs@gmail.com>
# To enable options list to be obtained from sqlalchemy table with field "name"
# Written to satisfy my need for a text entry widget with autocomplete.

import wx

class ACTextControlDB(wx.TextCtrl):
    """
    The list of choices is from sqlalchemy Table object candidates_table,
    the sqlalchemy session should also be passed
    """
    def __init__(self, parent, session, candidates_table):
        #ACTextControl.__init__(self, parent, add_option=True)
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)

        self.session = session
        self.candidates_table = candidates_table        

        self.all_candidates = []
        self.match_at_start = False
        self.add_option = True
        self.case_sensitive = False
        self.max_candidates = 5   # maximum no. of candidates to show
        self.select_candidates = []
        self.popup = ACPopup(self)

        self._set_bindings()

        self._screenheight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        self._popdown = True # Does the popup go down from the textctrl ?

    def _set_bindings(self):
        """
        One place to setup all the bindings
        """
        # text entry triggers update of the popup window
        self.Bind(wx.EVT_TEXT, self._on_text, self)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down, self)

        # loss of focus should hide the popup
        self.Bind(wx.EVT_KILL_FOCUS, self._on_focus_loss)
        self.Bind(wx.EVT_SET_FOCUS, self._on_focus)
        
    
    def SetValue(self, value):
        """
        Directly calling setvalue triggers textevent
        which results in popup appearing.
        To avoid this, call changevalue
        """
        super(ACTextControlDB, self).ChangeValue(value)


    def SetCandidates(self, candidates):
        self.all_candidates = candidates


    def _on_text(self, event):
        """
        On text entry in the textctrl,
        Pop up the popup,
        or update candidates if its already visible
        """
        txt = self.GetValue()

        # if txt is empty (after backspace), hide popup
        if not txt:
            if self.popup.IsShown:
                self.popup.Show(False)
                event.Skip()
                return

        # select candidates from database
        result = self.session.query(self.candidates_table).filter(
                    self.candidates_table.name.like("%{0}%".format(txt))
                ).order_by(self.candidates_table.name)
        self.select_candidates = []
        for candidate in result:
            self.select_candidates.append(candidate.name)

        self._show_popup(self.select_candidates, txt)


    def _show_popup(self, candidates, txt):
            # set up the popup and bring it on
            self._resize_popup(candidates, txt)
            self._position_popup()

            candidates.sort()
            
            if self._popdown:
                # TODO: Allow custom ordering
                self.popup._set_candidates(candidates, txt)
                self.popup.candidatebox.SetSelection(0)
                
            else:
                candidates.reverse()
                self.popup._set_candidates(candidates, txt)
                self.popup.candidatebox.SetSelection(len(candidates)-1)

            if not self.popup.IsShown():
                self.popup.Show()
        

                
    def _on_focus_loss(self, event):
        """Close the popup when focus is lost"""
        if self.popup.IsShown():
            self.popup.Show(False)
        event.Skip()

            
    def _on_focus(self, event):
        """
        When focus is gained,
        if empty, show all candidates,
        else, show matches
        """
        txt =  self.GetValue()
        if txt == '':
            self.select_candidates = self.all_candidates
            #self._show_popup(self.all_candidates, '')
        else:
            self._on_text(event)

        event.Skip()

            
    def _position_popup(self):
        """Calculate position for popup and
        display it"""
        left_x, upper_y = self.GetScreenPositionTuple()
        _, height = self.GetSizeTuple()
        popup_width, popup_height = self.popupsize
        
        if upper_y + height + popup_height > self._screenheight:
            self._popdown = False
            self.popup.SetPosition((left_x, upper_y - popup_height))
        else:
            self._popdown = True
            self.popup.SetPosition((left_x, upper_y + height))


    def _resize_popup(self, candidates, entered_txt):
        """Calculate the size for the popup to
        accomodate the selected candidates"""
        # Handle empty list (no matching candidates)
        if len(candidates) == 0:
            candidate_count = 3.5 # one line
            longest = len(entered_txt) + 4 + 4 #4 for 'Add '

        else:
            # additional 3 lines needed to show all candidates without scrollbar        
            candidate_count = min(self.max_candidates, len(candidates)) + 2.5
            longest = max([len(candidate) for candidate in candidates]) + 4

        
        charheight = self.popup.candidatebox.GetCharHeight()
        charwidth = self.popup.candidatebox.GetCharWidth()

        #self.popupsize = wx.Size( charwidth*longest, charheight*candidate_count )
        self.popupsize = wx.Size( self.Size[0], charheight*candidate_count )

        self.popup.candidatebox.SetSize(self.popupsize)
        self.popup.SetClientSize(self.popupsize)
        

    def _on_key_down(self, event):
        """Handle key presses.
        Special keys are handled appropriately.
        For other keys, the event is skipped and allowed
        to be caught by ontext event"""
        skip = True
        visible = self.popup.IsShown() 
        sel = self.popup.candidatebox.GetSelection()
        
        # Escape key closes the popup if it is visible
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            if visible:
                self.popup.Show(False)

        # Down key for navigation in list of candidates
        elif event.GetKeyCode() == wx.WXK_DOWN:
            if not visible:
                skip = False
                pass
            # 
            if sel + 1 < self.popup.candidatebox.GetItemCount():
                self.popup.candidatebox.SetSelection(sel + 1)
            else:
                skip = False

        # Up key for navigation in list of candidates
        elif event.GetKeyCode() == wx.WXK_UP:
            if not visible:
                skip = False
                pass
            if sel > -1:
                self.popup.candidatebox.SetSelection(sel - 1)
            else:
                skip = False

        # Enter - use current selection for text
        elif event.GetKeyCode() == wx.WXK_RETURN:
            if not visible:
                #TODO: trigger event?
                pass
            # Add option is only displayed
            elif self.popup.candidatebox.GetSelection() == -1:
                self.popup.Show(False)
            elif self.popup.candidatebox.GetSelection() == self.popup.add_index:
                self.SetValue(self.popup.add_text)
                self.SetInsertionPointEnd()

                if self.session.query(self.candidates_table).filter(self.candidates_table.name == self.GetValue()).count() == 0:
                    new_name = self.candidates_table( name = self.popup.add_text)
                    self.session.add(new_name)
                    self.session.commit()
                    
                self.SetInsertionPointEnd()
                self.popup.Show(False)
                e = ACTextCtrlDoneEditEvent(value=self.GetValue())
                wx.PostEvent(self, e)
            else:
                self.SetValue(self.select_candidates[self.popup.candidatebox.GetSelection()])
                self.SetInsertionPointEnd()
                self.popup.Show(False)
                e = ACTextCtrlDoneEditEvent(value=self.GetValue())
                wx.PostEvent(self, e) 

        # Tab  - set selected choice as text
        elif event.GetKeyCode() == wx.WXK_TAB:
            if visible:
                if (self.popup.candidatebox.GetSelection() == self.popup.add_index):
                    self.SetValue(self.popup.add_text)
                    self.SetInsertionPointEnd()
                else:
                    self.SetValue(self.select_candidates[self.popup.candidatebox.GetSelection()])
                    # set cursor at end of text
                    self.SetInsertionPointEnd()
                skip = False                
                
        if skip:
            event.Skip()
            

    def get_choices(self):
        """Return the current choices.
        Useful if choices have been added by the user"""
        return self.all_candidates        



            
class ACPopup(wx.PopupWindow):
    """
    The popup that displays the candidates for
    autocompleting the current text in the textctrl
    """
    def __init__(self, parent):
        wx.PopupWindow.__init__(self, parent)
        self.candidatebox = wx.SimpleHtmlListBox(self, -1, choices=[])
        self.SetSize((100, 100))
        self.displayed_candidates = []

    def _set_candidates(self, candidates, txt):
        """
        Clear existing candidates and use the supplied candidates
        Candidates is a list of strings.
        """
        # if there is no change, do not update
        if candidates == sorted(self.displayed_candidates):
            pass

        # Remove the current candidates
        self.candidatebox.Clear()
        
        #self.candidatebox.Append(['te<b>st</b>', 'te<b>st</b>'])
        exact_match = False
        for ch in candidates:
            if ch.lower() == txt.lower():
                exact_match = True
            self.candidatebox.Append(self._htmlformat(ch, txt))

        self.displayed_candidates = candidates

        if not exact_match:
            self.candidatebox.Append("<b>Add</b> {0}".format(txt))
            self.add_index = self.candidatebox.GetItemCount() - 1
            self.add_text = txt
        else:
            self.add_index = -1
            self.add_text = ""


    def _htmlformat(self, text, substring):
        """
        For displaying in the popup, format the text
        to highlight the substring in html
        """
        # empty substring
        if len(substring) == 0:
            return text

        else:
            return text.replace(substring, '<b>' + substring + '</b>', 1)
