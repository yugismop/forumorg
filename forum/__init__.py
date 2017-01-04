import datetime
import locale
import os

from flask import Flask
from flask_login import LoginManager

from storage import get_users, init_storage

# App init
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'my-debug-key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Storage init
init_storage()

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.template_filter('empty_event')
def empty_event(e):
    return any([v['registered'] for k, v in e.items()])

import views
