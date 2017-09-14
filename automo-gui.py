"""AutoMO WxWidgets Interaface"""
import automo


def main():
    """start the app"""
    database_uri = automo.DEFAULT_DB_URI

    automo.start_gui(database_uri)


if __name__ == '__main__':
    main()
