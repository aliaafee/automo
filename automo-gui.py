"""AutoMO WxWidgets Interaface"""
import automo


def main():
    """start the app"""
    database_uri = automo.DEFAULT_DB_URI
    debug = False

    automo.start_gui(database_uri, 'gui-ward', debug)


if __name__ == '__main__':
    main()
