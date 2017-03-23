"""
AutoMO
------

Program to automate the tedious job of hand writing prescriptions everyday

Copyright (C) 2017 Ali Aafee
"""
import sys
import getopt
import wx

from mainframe import MainFrame

import database


class MoPresc(wx.App):
    """
    The Main wx App Object
    """
    def __init__(self, parent=None):
        self.main_frame = None;
        wx.App.__init__(self, parent)


    def OnInit(self):
        """ Initializes the App """
        self.main_frame = MainFrame(None)
        self.main_frame.Show()
        return True


def app_license():
    """ App license """
    print "Auto MO"
    print "--------------------------------"
    print "Copyright (C) 2017 Ali Aafee"
    print ""


def usage():
    """ App usage """
    app_license()
    print "Usage:"
    print "    -h, --help"
    print "       Displays this help"
    print "    -d, --debug"
    print "       Output database debug data"


def start(uri, debug):
    """ starts db session at the given db uri """
    database.StartEngine(uri, debug)

    app = MoPresc()

    app.MainLoop()


def main(argv):
    """ starts the app, also reads command line arguments """
    debug = False

    try:
        opts, args = getopt.getopt(argv, "hd", ["help", "debug"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("-d", "--debug"):
            debug = True

    start("sqlite:///wardpresc-data.db", debug)


if __name__ == '__main__':
    main(sys.argv[1:])
