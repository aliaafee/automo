"""Discharge Interface"""
import wx
import os
import shutil
from slugify import slugify

from .... import database as db
from ... import images
from ... import events
from .dischargelistpanel import DischargeListPanel
from .dischargepanel import DischargePanel
from ...dischargewizard import DischargeWizard
from ..shellinterface import ShellInterface
from ..baseinterface import BaseInterface

ID_SHELL = wx.NewId()
ID_NEW_DISCHARGE = wx.NewId()
ID_EXPORT_ALL = wx.NewId()


class DischargeInterface(BaseInterface):
    """Discharge Interface"""
    def __init__(self, parent, session=None):
        super(DischargeInterface, self).__init__(parent, session)

        self.set_title("Discharges")

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.create_toolbar()
        self.toolbar.Realize()

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.discharge_list_panel = DischargeListPanel(splitter, self.session, style=wx.BORDER_THEME)

        self.discharge_panel = DischargePanel(splitter, self.session, style=wx.BORDER_THEME)

        splitter.SplitVertically(self.discharge_list_panel, self.discharge_panel)
        splitter.SetMinimumPaneSize(5)
        splitter.SetSashPosition(250)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(events.AM_ENCOUNTER_SELECTED, self._on_encounter_selected)

        self.Layout()

    
    def create_toolbar(self):
        self.toolbar.AddTool(wx.ID_REFRESH, "Refresh", images.get("refresh_24"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "Refresh", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_NEW_DISCHARGE, "New Discharge", images.get("discharge"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "New Discharge", "")

        self.toolbar.Bind(wx.EVT_TOOL, self._on_refresh, id=wx.ID_REFRESH)


    def create_file_menu(self):
        self.file_menu.Append(ID_NEW_DISCHARGE, "New Discharge", "Create New Discharge")
        self.file_menu.Append(ID_EXPORT_ALL, "Export All", "Export All Discharges as PDFs")
        self.file_menu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self._on_new_discharge, id=ID_NEW_DISCHARGE)
        self.Bind(wx.EVT_MENU, self._on_export_all, id=ID_EXPORT_ALL)
        super(DischargeInterface, self).create_file_menu()


    def create_tool_menu(self):
        super(DischargeInterface, self).create_tool_menu()
        self.tool_menu.Append(ID_SHELL, "Python Shell", "AutoMO Python Shell")
        self.Bind(wx.EVT_MENU, self._on_python_shell, id=ID_SHELL)


    def refresh(self):
        super(DischargeInterface, self).refresh()
        self.discharge_list_panel.refresh()
        self.discharge_panel.refresh()


    def _on_refresh(self, event):
        self.refresh()


    def _on_python_shell(self, event):
        shell = ShellInterface(self, self.session)
        shell.Show()


    def _on_new_discharge(self, event):
        with DischargeWizard(self, self.session) as dlg:
            done = False
            while not done:
                dlg.ShowModal()
                if dlg.GetReturnCode() == wx.ID_OK:
                    try:
                        admission = dlg.get_admission()
                        self.session.add(admission)
                    except db.dbexception.AutoMODatabaseError as e:
                        self.session.rollback()
                        with wx.MessageDialog(None,
                            "Database Error Occured. {}".format(e.message),
                            "Database Error",
                            wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                            err_dlg.ShowModal()
                    except Exception as e:
                        self.session.rollback()
                        with wx.MessageDialog(None,
                            "Error Occured. {}".format(e.message),
                            "Error",
                            wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                            err_dlg.ShowModal()
                    else:
                        self.session.commit()
                        self.discharge_list_panel.refresh()
                        self.discharge_panel.set_admission(admission)
                        done = True
                else:
                    done = True


    def _on_export_all(self, event):
        dlg = wx.DirDialog (None, "Choose input directory", "", wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_CANCEL:
            return

        admissions = self.session.query(db.Admission).all()

        for adm in admissions:
            year = "{}".format(adm.start_time.year)
            month = "{}".format(adm.start_time.month)
            filename = slugify("{} {} {}.pdf".format(adm.patient.national_id_no, adm.patient.hospital_no, adm.patient.name))

            src_fpath = adm.generate_discharge_summary(self.session)

            dest_fpath = os.path.join(dlg.GetPath(), year, month, filename)

            print "Generating... {}".format(dest_fpath)
            
            try:
                shutil.copy(src_fpath, dest_fpath)
            except IOError as io_err:
                os.makedirs(os.path.dirname(dest_fpath))
                shutil.copy(src_fpath, dest_fpath)



    def _on_encounter_selected(self, event):
        self.discharge_panel.set_admission(event.object)
