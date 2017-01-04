import json
import os
import requests

from flask import abort, redirect, render_template, request, send_from_directory, url_for
from flask_login import login_required, login_user, logout_user
from login import validate_login
from storage import User, get_user, set_user

from forum import app
from mailing import send_mail


######### ADMIN ###########

@app.route('/dashboard')
@app.route('/dashboard/<page>')
@login_required
def dashboard(page=None):
    # asking for specific page
    if page:
        return render_template('dashboard/sections/{}.html'.format(page))
    # default option is main dashboard
    else:
        return render_template('dashboard/dashboard.html')


@app.route('/connexion', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        remember_me = 'remember_me' in request.form
        user_id = request.form.get('id', None)
        password = request.form.get('password', None)
        user = get_user(user_id)
        # checking stuff out
        if not user_id or not password:
            return render_template('login.html', error="blank_fields")
        if not user:
            return render_template('login.html', error="no_user_found")
        if not validate_login(user['password'], password):
            return render_template('login.html', error="wrong_password")
        # all is good
        user = User(id=user_id, password=password)
        login_user(user, remember=remember_me)
        if user_id == "admin":
            return redirect('/admin')
        else:
            return redirect(request.args.get('next') or url_for('dashboard'))
    return render_template('login.html')


@app.route('/deconnexion')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/update_user', methods=["POST"])
def update_user():
    user = request.form.get('user')
    user = json.loads(user)
    set_user(user['id'], user)
    return "Success."


######### VITRINE ###########

# start of app
@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')

######## INDEXING ########
@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
