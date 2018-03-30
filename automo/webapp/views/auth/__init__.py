"""Patient View"""
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import fresh_login_required, login_user, logout_user
from flask_login import UserMixin

from .... import database as db
from .forms import LoginForm, EditUserForm

auth_view = Blueprint('auth', __name__)


@auth_view.route('/login', methods=['GET', 'POST'])
def login():
    """ Handle requests to the /login route
      Log an employee in through the login form"""
    form = LoginForm()
    if form.validate_on_submit():

        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        user = db.User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            # log employee in
            login_user(user)

            # redirect to the dashboard page after login
            return redirect(url_for('patient.patient_search'))

        # when login details are incorrect
        else:
            flash('Invalid username or password.')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')


@auth_view.route('/logout')
def logout():
    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))


@auth_view.route('/user', methods=['GET', 'POST'])
@fresh_login_required
def user():
    """Update user data"""
    form = EditUserForm()
    if form.validate_on_submit():
        pass

    return render_template('auth/edituser.html', form=form, title='Edit User')
