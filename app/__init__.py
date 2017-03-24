import os
from flask import Flask, g
from flask_bcrypt import Bcrypt
from flask_assets import Environment
from flask_login import LoginManager
from flask_qrcode import QRcode
from flask_sslify import SSLify
from gridfs import GridFS
from pymongo import MongoClient


# Storage init
def get_db():
    with app.app_context():
        if not hasattr(g, 'db'):
            client = MongoClient(host=os.environ.get('MONGODB_URI'))
            g.db = client.get_default_database()
        return g.db


# App init
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'my_debug_key')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('FLASK_PASSWORD_SALT', 'my_debug_salt')
app.config['TOKEN_EXPIRATION'] = int(os.environ.get('TOKEN_EXPIRATION', 7200))
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.add_extension('jinja2_time.TimeExtension')

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.signin'

# Bcrypt
bcrypt = Bcrypt()
bcrypt.init_app(app)

# QRCode
qrcode = QRcode()
qrcode.init_app(app)

# Flask-Assets
from .assets import bundles
assets = Environment(app)
assets.append_path(os.path.join(os.path.dirname(__file__), './static'))
assets.append_path(os.path.join(os.path.dirname(__file__), './static/bower_components'))
assets.register(bundles)

# SSLify
with app.app_context():
    sslify = SSLify()
    sslify.init_app(app)

GridFS = GridFS(get_db(), collection='resumes')

# Blueprints
from .views import bp as bp_main
app.register_blueprint(bp_main)
from .users.views import bp as bp_users
app.register_blueprint(bp_users, url_prefix='/candidats')
from .companies.views import bp as bp_companies
app.register_blueprint(bp_companies, url_prefix='/recruteurs')

# Init
from .users import helpers
from .companies import helpers
from . import helpers, storage, login
