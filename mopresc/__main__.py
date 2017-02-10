import sys, os
import getopt
import wx

from mainframe import MainFrame

import database


class MoPresc(wx.App):
    def __init__(self, parent=None):
        wx.App.__init__(self, parent)


    def OnInit(self):
        self.mainFrame = MainFrame(None)
        self.mainFrame.Show()
        return True


def license():
    print "Ward Prescription"
    print "--------------------------------"
    print "Copyright (C) 2017 Surgery Department IT Unit"
    print ""


def usage():
    license()
    print "Usage:"
    print "    -h, --help"
    print "       Displays this help"


def start(uri):
    database.StartEngine(uri)

    app = MoPresc()

    app.MainLoop()


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

    start("sqlite:///wardpresc-data.db")


if __name__ == '__main__':
    main(sys.argv[1:])
