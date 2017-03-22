from flask import flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for, send_file, session
from flask_login import current_user, login_required, login_user, logout_user
from .login import create_user, generate_confirmation_token, validate_login
from .storage import User, get_events, get_user, get_users, user_exists, set_user
from .identicon import render_identicon

from binascii import hexlify
from io import BytesIO

import json
from jinja2.exceptions import TemplateNotFound

from app import app, get_db
from .mailing import send_mail


# INDEX
# start of app
@app.route('/')
@app.route('/<page>', methods=['GET'])
def index(page=None):
    section = request.args.get('section')
    if section == 'accueil':
        session.pop('section', None)
        section = None
    if not session.get('section') and not page and not section:
        return render_template('split.html')
    # session.section != None || page != None || section != None
    if section:
        section = 'users' if section == 'candidats' else 'companies'
        session['section'] = section
    # session.section != None || page != None
    page = page if page else 'index'
    if not session.get('section'):
        return redirect(url_for('index'))
    # session.section != None && page != None
    return render_template(f'{session["section"]}/{page}.html')


@app.route('/connexion', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = get_user(id=email)
        if not user:
            return render_template('users/signin.html', error=['no_user_found'])
        if not validate_login(user.password, password):
            return render_template('users/signin.html', error=['wrong_password'])
        if not user.confirmed:
            return render_template('users/signin.html', error=['user_not_confirmed'])
        # all is good
        user = User(id=email, password=password)
        print(f'connected_as: {email}')
        login_user(user)
        return redirect(url_for('users.dashboard'))
    print(f'flash: {get_flashed_messages()}')
    return render_template('users/signin.html', error=get_flashed_messages())


@app.route('/inscription', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not password or not email:
            flash('empty_fields')
            return render_template('users/users/signup.html')
        email = email.lower()
        if user_exists(email):
            user = get_user(id=email)
            if user.confirmed:
                return render_template('users/users/signup.html', error='user_already_exists')
            else:
                token = generate_confirmation_token(email)
                confirm_url = url_for(
                    'confirm_email', token=token, _external=True)
                send_mail(email, confirm_url)
                flash('user_registered')
                return redirect(url_for('signin'))
        else:
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
            except Exception as e:
                print('error', e, user, user.data)
            return redirect(request.args.get('next') or url_for('signin'))
    return render_template('users/signup.html')


@app.route('/identicon', methods=['GET'])
@login_required
def identicon():
    text = request.args.get('text', 'EMPTY')
    code = int(hexlify(text.encode('utf-8')), 16)
    size = 25
    img = render_identicon(code, size)
    stream = BytesIO()
    img.save(stream, format='png')
    stream.seek(0)
    return send_file(
        stream,
        mimetype='image/png'
    )


@app.route('/deconnexion')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    users = get_users()
    form = request.form.to_dict()
    app.logger.info(form)
    if form.get('school_'):
        form['school'] = form.get('school_')
    form.pop('school_', None)
    for k, v in form.items():
        users.update_one({'id': current_user.id}, {'$set': {'profile.{}'.format(k): v}})
    flash('profile_completed')
    return redirect(url_for('dashboard', page='profile'))


@app.route('/update_user', methods=['POST'])
@login_required
def update_user():
    user = request.form.get('user')
    user = json.loads(user)
    set_user(user['id'], user)
    return 'success'


@app.route('/update_event', methods=['POST'])
@login_required
def update_event():
    mevent = request.form.get('event')
    if mevent != 'fra':
        name = request.form.get('name')
        mtype = request.form.get('type')
        time = request.form.get('time')

        events = get_events()
        users = get_users()

        event = events.find_one({'name': name, 'type': mtype})
        places_left = event['places_left']
        if mtype == 'table_ronde':
            places_left = event['places_left'][time]

        if places_left > 0:
            old_event = users.find_one({'id': current_user.id})
            old_name = old_event['events']['joi'].get(mtype)
            old_name = old_name['name'] if old_name else None
            doc = {'name': name, 'registered': True}
            if mtype == 'table_ronde':
                doc = {'name': name, 'registered': True, 'time': time}
                events.update_one({'name': old_name, 'type': mtype},
                                  {'$inc': {'places_left.{}'.format(time): 1}}) if old_name else None
                events.update_one({'name': name, 'type': mtype}, {
                                  '$inc': {'places_left.{}'.format(time): -1}})
            else:
                doc = {'name': name, 'registered': True}
                events.update_one({'name': old_name, 'type': mtype},
                                  {'$inc': {'places_left': 1}}) if old_name else None
                events.update_one({'name': name, 'type': mtype},
                                  {'$inc': {'places_left': -1}})
            users.update_one({'id': current_user.id}, {
                             '$set': {'events.joi.{}'.format(mtype): doc}})
            return 'success'
        else:
            return 'error'
    else:
        users = get_users()
        user = current_user
        if user.profile.get('first_name') and user.profile.get('name') and user.profile.get('school') and user.profile.get('year') and user.profile.get('specialty'):
            users.update_one({'id': current_user.id}, {'$set': {'events.fra.registered': True}})
            return 'success'
        else:
            return 'incomplete_profile'


@app.route('/update_styf', methods=['POST'])
@login_required
def update_styf():
    users = get_users()
    events = get_events()
    places_left = events.find_one({'name': 'styf'}).get('places_left')

    user = current_user
    if user.profile.get('first_name') and user.profile.get('name') and user.profile.get('tel') and user.profile.get('school') and user.profile.get('year'):
        if places_left > 0 or current_user.events['styf'].get('registered'):
            users.update_one({'id': current_user.id}, {'$set': {'events.styf': request.form}})
            users.update_one({'id': current_user.id}, {'$set': {'events.styf.registered': True}})
            if not current_user.events['styf'].get('registered'):
                events.update_one({'name': 'styf'}, {'$inc': {'places_left': -1}})
            return 'success'
        else:
            return 'full_event'
    else:
        return 'incomplete_profile'


@app.route('/update_master_class', methods=['POST'])
@login_required
def update_master_class():
    registered = request.form.get('registered')
    registered = True if registered == 'true' else False
    users = get_users()
    user = current_user
    if user.profile.get('first_name') and user.profile.get('name') and user.profile.get('tel') and user.profile.get('school') and user.profile.get('year'):
        users.update_one({'id': current_user.id}, {'$set': {'events.master_class.registered': registered}})
        return 'success'
    else:
        return 'incomplete_profile'


@app.route('/update_ambassador', methods=['POST'])
@login_required
def update_ambassador():
    first = request.form.get('first')
    second = request.form.get('second')
    _update_ambassador(first, 'mercredi')
    _update_ambassador(second, 'jeudi')
    return 'success'


def _update_ambassador(value, day):
    old_val = get_db().users.find_one({'id': current_user.id}, {'events.fra.ambassador': 1})['events']['fra'].get('ambassador')
    if old_val and old_val.get(day):
        get_db().companies.update_one({'id': old_val.get(day)}, {'$unset': {'ambassadors.{}'.format(day): 1}})
        get_db().users.update_one({'id': current_user.id}, {'$unset': {'events.fra.ambassador.{}'.format(day): 1}})
    if value != 'none':
        get_db().companies.update_one({'id': value}, {'$set': {'ambassadors.{}'.format(day): current_user.id}})
        get_db().users.update_one({'id': current_user.id}, {'$set': {'events.fra.ambassador.{}'.format(day): value}})


# SEO
@app.route('/robots.txt')
@app.route('/favicon.ico')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


# JS logging
@app.route('/js_log', methods=['POST'])
def js_log():
    print('js_log', request.form.to_dict())
    return 'success'


# Error handling
@app.errorhandler(404)
@app.errorhandler(TemplateNotFound)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
