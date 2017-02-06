# coding=utf-8

import os
import json
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_qrcode import QRcode

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

# QRCode
qrcode = QRcode(app)

# Storage init
from storage import get_events, get_users, init_storage, get_db
init_storage()


@app.template_filter('to_companies')
def to_companies(day):
    cur = get_db().companies.find({}, {'id': 1, 'name': 1, 'pole': 1, 'ambassadors.{}'.format(day): 1, '_id': 0})
    cur = [l for l in cur if l['id'] != 'admin' or l['id'] != 'forumorg']
    res = []
    for c in cur:
        is_filled = True if c.get('ambassadors') else False
        print(c)
        d = {'id': c['id'], 'name': c['name'].lower().capitalize(), 'is_filled': is_filled}
        if c.get('pole') and c.get('pole') != 'school':
            res.append(d)
    return res


@app.context_processor
def get_joi():
    def _get_joi():
        return list(get_events().find({}))
    return dict(get_joi=_get_joi)


@app.context_processor
def get_styf():
    def _get_styf():
        return list(get_events().find({}))
    return dict(get_styf=_get_styf)


@app.context_processor
def get_master_class():
    def _get_master_class():
        return list(get_events().find({}))
    return dict(get_master_class=_get_master_class)


@app.template_filter('to_str')
def to_jobs(lst):
    return ', '.join(json.loads(lst))


@app.template_filter('to_ambassador')
def to_ambassador(user_id):
    return get_db().users.find_one({'id': user_id}, {'events.fra.ambassador': 1})['events']['fra'].get('ambassador')


@app.template_filter('to_name')
def to_name(company_id):
    return get_db().companies.find_one({'id': company_id}, {'name': 1}).get('name')


import views
