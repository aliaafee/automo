"""AutoMO WxWidgets Interaface"""
import automo
import automo.gui


def main():
    """start the app"""
    database_uri = automo.DEFAULT_DB_URI

    automo.start(database_uri)

    app = automo.gui.AutoMOApp()

    app.MainLoop()


if __name__ == '__main__':
    main()
