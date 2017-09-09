"""AutoMO Command Line Interface"""
import sys
import getopt

import automo


def app_license():
    """App license"""
    print "Auto MO {0}".format(automo.__version__)
    print "----------------------------"
    print "Copyright (C) 2017 Ali Aafee"
    print ""


def usage():
    """App usage"""
    app_license()
    print "Usage:"
    print "    -f, --interface (Option is required)"
    print "       Set the interface to start with."
    print "       available interfaces:"
    print '           cli: "{}"'.format('", "'.join(automo.CLI_INTERFACES))
    print '           gui: "{}"'.format('", "'.join(automo.GUI_INTERFACES))
    print "    -h, --help"
    print "       Displays this help"
    print "    -d, --debug"
    print "       Output database debug data"
    print "    -i, --icd10claml [filename]"
    print "       Import ICD10 2016 Classification from ClaML xml file"


def main(argv):
    """starts the app, also reads command line arguments"""
    database_uri = automo.DEFAULT_DB_URI
    debug = False
    interface = 'shell'

    try:
        opts, args = getopt.getopt(argv, "hdi:f:", ["help", "debug", "icd10claml=", "interface="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("-i", "--icd10claml"):
            automo.import_icd10claml(arg, database_uri, debug)
            sys.exit()
        if opt in ("-f", "--interface"):
            interface = arg
        if opt in ("-d", "--debug"):
            debug = True

    if interface in automo.CLI_INTERFACES:
        automo.start_cli(database_uri, interface, debug)
    elif interface in automo.GUI_INTERFACES:
        automo.start_gui(database_uri, interface, debug)
    else:
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
