from sqlalchemy.orm import scoped_session
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user

from .. import start, DEFAULT_DB_URI
from .. import config
from .. import loginmanager
from .. import database as db
from .views.patient import patient_view
from .views.auth import auth_view
from .views.home import home_view

db.s_session = scoped_session(db.Session)
db.Base.query = db.s_session.query_property()


def create_app():
    start(DEFAULT_DB_URI)

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.s_session.remove()

    app.jinja_env.globals.update(
        format_duration=config.format_duration,
        format_duration_verbose=config.format_duration_verbose,
        format_date=config.format_date,
        format_datetime=config.format_datetime,
        formate_time=config.formate_time
    )

    app.register_blueprint(home_view)
    app.register_blueprint(auth_view)
    app.register_blueprint(patient_view, url_prefix="/patient")

    login_manager = LoginManager()

    @login_manager.user_loader
    def load_user(user_id):
        return db.User.query.get(int(user_id))

    def get_current_user_id():
        if not hasattr(current_user, 'id'):
            return None
        return current_user.id

    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"
    loginmanager.get_current_user_id = get_current_user_id

    Bootstrap(app)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    return app
