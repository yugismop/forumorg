# coding=utf-8

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# App init
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or 'my_debug_key'
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get(
    'FLASK_PASSWORD_SALT') or 'my_debug_salt'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Bcrypt
bcrypt = Bcrypt(app)

# Storage init
from storage import get_events, get_users, init_storage
init_storage()


@app.context_processor
def get_joi():
    def _get_joi():
        return list(get_events().find({}))
    return dict(get_joi=_get_joi)


@app.template_filter('empty_event')
def empty_event(e):
    return not any([v['registered'] for v in e.values()])


import views
