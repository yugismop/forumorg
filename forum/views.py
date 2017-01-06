import json
import os
import requests

from flask import abort, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user
from login import create_user, validate_login
from storage import User, get_events, get_user, get_users

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
        return redirect(request.args.get('next') or url_for('dashboard'))
    return render_template('login.html')


@app.route('/inscription', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        user_id = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        user = get_user(user_id)
        # checking stuff out
        if not user_id or not password or not re_password:
            return render_template('register.html', error="blank_fields")
        if re_password != password:
            return render_template('register.html', error="different_passwords")
        if user:
            return render_template('register.html', error="user_already_exists")
        # all is good
        user = User(id=user_id, password=password)
        create_user(user)
        flash('user_registered')
        return redirect(request.args.get('next') or url_for('login'))
    return render_template('register.html')


@app.route('/deconnexion')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/update_event', methods=["POST"])
@login_required
def update_event():
    mtype = request.form.get('type')
    name = request.form.get('name')
    time = request.form.get('time', None)

    events = get_events()
    users = get_users()

    event = events.find_one({"name": name})
    places_left = event['places_left']
    if mtype == 'table_ronde':
        places_left = event['places_left'][time]

    if places_left > 0:
        old_event = users.find_one({'id': current_user.id})
        old_name = old_event['events']['joi'].get(mtype)
        old_name = old_name['name'] if old_name else None
        doc = { 'name' : name, 'registered' : True }
        if mtype == 'table_ronde':
            doc = { 'name' : name, 'registered' : True, 'time': time }
            events.update_one({'name': old_name}, {'$inc': {'places_left.{}'.format(time) : 1}}) if old_name else None
            events.update_one({'name': name}, {'$inc': {'places_left.{}'.format(time) : -1}})
        else:
            doc = { 'name' : name, 'registered' : True }
            events.update_one({'name': old_name}, {'$inc': {'places_left' : 1}}) if old_name else None
            events.update_one({'name': name}, {'$inc': {'places_left': -1}})
        users.update_one({'id': current_user.id}, {'$set': {'events.joi.{}'.format(mtype) : doc } })
        return "success"
    else:
        return "error"


######### VITRINE ###########

# start of app
@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')

# joi
@app.route('/joi', methods=["GET"])
def joi():
    return render_template('joi.html')


@app.route('/send_request', methods=["GET"])
def send_request():
    #Params
    email = request.args.get('email')
    contact_name = request.args.get('nom_complet')
    company_name = request.args.get('nom')
    telephone = request.args.get('tel')
    captcha = request.args.get('captcha')

    # ReCaptcha
    base_url = 'https://www.google.com/recaptcha/api/siteverify'
    secret = os.environ.get('RECAPTCHA_SECRET_KEY')
    res = requests.post(base_url, data={'response':captcha, 'secret':secret}).json()
    ts, host, success = res.get('challenge_ts'), res.get('hostname'), res.get('success')

    # Logging bots...
    if ts and not success:
        print("Bot found from: {} at: {}".format(res.get('hostname'), res.get('challenge_ts')))

    # Sending mail...
    if success:
        return send_mail(email, contact_name, company_name, telephone)
    else:
        abort(500)

######## INDEXING ########
@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
