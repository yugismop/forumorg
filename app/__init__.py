# coding=utf-8

import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_assets import Environment
from flask_login import LoginManager
from flask_qrcode import QRcode
from flask_sslify import SSLify
from gridfs import GridFS
from pymongo import MongoClient


# App init
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'my_debug_key')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('FLASK_PASSWORD_SALT', 'my_debug_salt')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TOKEN_EXPIRATION'] = int(os.environ.get('TOKEN_EXPIRATION', 7200))
db = None

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Bcrypt
bcrypt = Bcrypt()
bcrypt.init_app(app)

# QRCode
qrcode = QRcode()
qrcode.init_app(app)

# Flask-Assets
from assets import bundles
assets = Environment(app)
assets.append_path(os.path.join(os.path.dirname(__file__), './static'))
assets.append_path(os.path.join(os.path.dirname(__file__), './static/bower_components'))
assets.register(bundles)


# SSLify
with app.app_context():
    sslify = SSLify()
    sslify.init_app(app)


# Storage init
def get_db():
    global db
    client = MongoClient(host=os.environ.get('MONGODB_URI'))
    db = client.get_default_database()
    return db


GridFS = GridFS(get_db(), collection='resumes')

from users import helpers
from . import views
