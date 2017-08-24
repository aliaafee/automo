"""Python Shell for AutoMO"""

import wx
from wx.py.shell import Shell

import database as db


class AutoMOShell(wx.Dialog):
    """Python Shell for AutoMO"""
    def __init__(self, parent, session, title="Auto MO Python Shell",
                 style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
                 **kwds):
        super(AutoMOShell, self).__init__(parent, title=title, style=style, **kwds)

        self.session = session

        self.shell = Shell(self)

        patients = self.session.query(db.Patient).all()
        self.shell.interp.locals = {
            'p': patients,
            'session': self.session,
            'query': self.session.query,
            'db': db,
            'quit': self.EndModal
        }


def main():
    db.StartEngine("sqlite:///wardpresc-data.db", False, "")
    session = db.Session()

    app = wx.PySimpleApp(0)

    dlg = AutoMOShell(None, session)

    app.SetTopWindow(dlg)

    dlg.Show()

    app.MainLoop()

if __name__ == "__main__":
    main()
