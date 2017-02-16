import wx
import  wx.lib.newevent

from actextcontrol import ACTextControl

ACTextCtrlDoneEditEvent, EVT_ACT_DONE_EDIT = wx.lib.newevent.NewEvent()

class ACTextControlDB(ACTextControl):
    def __init__(self, parent, session, candidates_table):
        ACTextControl.__init__(self, parent, add_option=True)

        self.session = session
        self.candidates_table = candidates_table
        

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
                ).limit(10)
        self.select_candidates = []
        for candidate in result:
            self.select_candidates.append(candidate.name)
            
        if len(self.select_candidates) == 0:
            if not self.add_option:
                if self.popup.IsShown():
                    self.popup.Show(False)

            else:
                display = ['Add ' + txt]
                self.popup._set_candidates(display, 'Add')
                self._resize_popup(display, txt)
                self._position_popup()
                if not self.popup.IsShown():
                    self.popup.Show()
                
        else:
            self._show_popup(self.select_candidates, txt)


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
            elif len(self.select_candidates) == 0:
                #Add new candate to db table
                if self.session.query(self.candidates_table).filter(self.candidates_table.name == self.GetValue()).count() == 0:
                    new_name = self.candidates_table( name = self.GetValue())
                    self.session.add(new_name)
                    self.session.commit()
                    
                self.SetInsertionPointEnd()
                self.popup.Show(False)
                e = ACTextCtrlDoneEditEvent(value=self.GetValue())
                wx.PostEvent(self, e)

                
            elif self.popup.candidatebox.GetSelection() == -1:
                self.popup.Show(False)
                e = ACTextCtrlDoneEditEvent(value=self.GetValue())
                wx.PostEvent(self, e)

            elif self.popup.candidatebox.GetSelection() > -1:
                self.SetValue(self.select_candidates[self.popup.candidatebox.GetSelection()])
                self.SetInsertionPointEnd()
                self.popup.Show(False)
                e = ACTextCtrlDoneEditEvent(value=self.GetValue())
                wx.PostEvent(self, e)

        # Tab  - set selected choice as text
        elif event.GetKeyCode() == wx.WXK_TAB:
            if visible:
                self.SetValue(self.select_candidates[self.popup.candidatebox.GetSelection()])
                # set cursor at end of text
                self.SetInsertionPointEnd()
                skip = False                
                
        if skip:
            event.Skip()


