import json
import os
import requests

from flask import abort, flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user
from login import confirm_token, create_user, generate_confirmation_token, validate_login
from storage import User, confirm_user, get_events, get_user, get_users, user_exists

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
        email = request.form.get('email')
        password = request.form.get('password')
        user = get_user(id=email)
        if not user:
            return render_template('login.html', error="no_user_found")
        if not validate_login(user.password, password):
            return render_template('login.html', error="wrong_password")
        if not user.confirmed:
            return render_template('login.html', error="user_not_confirmed")
        # all is good
        user = User(id=email, password=password)
        login_user(user, remember=remember_me)
        return redirect(request.args.get('next') or url_for('dashboard'))

    for m in ['user_registered', 'confirm_link_expired', 'account_already_confirmed', 'account_confirmed', 'error']:
        if m in get_flashed_messages():
            return render_template('login.html', error=m)
    return render_template('login.html')

@app.route('/inscription', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if user_exists(email):
            return render_template('register.html', error="user_already_exists")
        # all is good
        user = User(id=email, password=password, created=True)
        token = generate_confirmation_token(email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        try:
            created = create_user(user)
            if created:
                send_mail(email, confirm_url)
                flash('user_registered')
            else:
                flash('error')
        except:
            print('big error', user, user.data)
        return redirect(request.args.get('next') or url_for('login'))
    return render_template('register.html')


@app.route('/confirmation/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('confirm_link_expired', 'danger')
    user = get_user(id=email)
    print(email, get_user(id=email), token)
    if not user:
        flash('error')
        return redirect(url_for('login'))
    if user.confirmed:
        flash('account_already_confirmed', 'success')
    else:
        confirm_user(user)
        flash('account_confirmed', 'success')
    return redirect(url_for('login'))


@app.route('/deconnexion')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/update_event', methods=["POST"])
@login_required
def update_event():
    mtype = request.form.get('type')
    name = request.form.get('name')
    time = request.form.get('time')

    events = get_events()
    users = get_users()

    event = events.find_one({"name": name, "type": mtype})
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
            events.update_one({'name': old_name, 'type': mtype}, {'$inc': {'places_left.{}'.format(time) : 1}}) if old_name else None
            events.update_one({'name': name, 'type': mtype}, {'$inc': {'places_left.{}'.format(time) : -1}})
        else:
            doc = { 'name' : name, 'registered' : True }
            events.update_one({'name': old_name, 'type': mtype}, {'$inc': {'places_left' : 1}}) if old_name else None
            events.update_one({'name': name, 'type': mtype}, {'$inc': {'places_left': -1}})
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

######## INDEXING ########
@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
