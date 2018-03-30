"""Home Page"""
from flask import Blueprint, render_template
from flask_login import login_required

from ... import database as db

home_view = Blueprint('home', __name__)

@home_view.route('/')
def homepage():
    return render_template('base.html', title="AutoMO")
