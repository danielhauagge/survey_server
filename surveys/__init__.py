from os import path
import os
import canonicaljson

from flask import Flask, send_from_directory, render_template, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app_dir = path.dirname(__file__.replace('fai_', ''))

# Config
# app.config.from_object('config')
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'com.peachylabs.surveys'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def is_safe_path(basedir, fname, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        return path.realpath(fname).startswith(basedir)

    return path.abspath(fname).startswith(basedir)


# Basic calls to grab static content
@app.route('/js/<fname>')
def send_js(fname):
    return send_from_directory(path.join(app_dir, 'static/js'), fname)


@app.route('/css/<fname>')
def send_css(fname):
    return send_from_directory(path.join(app_dir, 'static/css'), fname)


@app.route('/fonts/<fname>')
def send_fonts(fname):
    return send_from_directory(path.join(app_dir, 'static/fonts'), fname)


@app.route('/survey/data/<fname>')
def send_local_data(fname):
    basedir = os.getcwd()
    fname = path.join('data', fname)

    if is_safe_path(basedir, fname):
        return send_from_directory(basedir, fname)
    else:
        return abort(404)


@app.route('/survey/img/<fname>')
def send_local_image(fname):
    basedir = os.getcwd()
    fname = path.join('img', fname)

    if is_safe_path(basedir, fname):
        return send_from_directory(basedir, fname, mimetype='image/jpeg')
    else:
        return abort(404)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(os.getcwd(), 'surveys.db')
db = SQLAlchemy(app)

# Login view
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

# Bootstrap
Bootstrap(app)


def encode_json(obj):
    return canonicaljson.encode_canonical_json(obj)


# import rest of project
from . import survey_views, auth
