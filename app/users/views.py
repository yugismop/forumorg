import json
from flask import Blueprint, render_template, flash, redirect, url_for, request, session, get_flashed_messages
from flask_login import login_required, current_user, login_user
from app import app, get_db
from app.storage import get_user, confirm_user, get_users, set_user, get_events, user_exists, new_user
from app.login import validate_login, confirm_token, generate_confirmation_token
from app.models import User
from .mailing import send_mail

bp = Blueprint('users', __name__)


# INDEX
@bp.route('/')
@bp.route('/<page>')
def index(page='index'):
    session['section'] = 'users'
    return render_template(f'users/{page}.html')


@bp.route('/connexion', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = get_user(id=email)
        if not user:
            return render_template('users/signin.html', error=['no_user_found'])
        if not validate_login(user.password, password, 'users'):
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


@bp.route('/inscription', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not password or not email:
            flash('empty_fields')
            return render_template('users/signup.html')
        email = email.lower()
        if user_exists(email):
            user = get_user(id=email)
            if user.confirmed:
                return render_template('users/signup.html', error='user_already_exists')
            else:
                token = generate_confirmation_token(email)
                confirm_url = url_for(
                    'users.confirm_email', token=token, _external=True)
                send_mail(email, confirm_url)
                flash('user_registered')
                return redirect(url_for('main.signin'))
        else:
            user = User(id=email, password=password, created=True)
            token = generate_confirmation_token(email)
            confirm_url = url_for('users.confirm_email', token=token, _external=True)
            try:
                created = new_user(user)
                if created:
                    send_mail(email, confirm_url)
                    flash('user_registered')
                else:
                    flash('error')
            except Exception as e:
                print('error', e, user, user.data)
            return redirect(url_for('main.signin'))
    return render_template('users/signup.html')


# ADMIN
@bp.route('/dashboard/')
@bp.route('/dashboard/<page>')
@login_required
def dashboard(page=None):
    if page:
        if page in ['companies', 'ticket', 'jobs'] and not current_user.events['fra'].get('registered'):
            render_template('users/dashboard/sections/fra.html')
        return render_template(f'users/dashboard/sections/{page}.html')
    else:
        return render_template('users/dashboard/sections/dashboard.html')


@bp.route('/dashboard/companies/<company_id>')
@login_required
def companies(company_id=None):
    company = get_db().companies.find_one({'id': company_id})
    return render_template('users/dashboard/sections/company.html', company=company)


@bp.route('/confirmation/<token>')
def confirm_email(token):
    email = confirm_token(token)

    if not email:
        flash('confirm_link_expired', 'danger')
        return redirect(url_for('main.signin'))

    user = get_user(id=email)
    if not user:
        flash('error')
        return redirect(url_for('main.signin'))
    if user.confirmed:
        flash('account_already_confirmed', 'success')
    else:
        confirm_user(user)
        flash('account_confirmed', 'success')
    return redirect(url_for('main.signin'))


@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    users = get_users()
    form = request.form.to_dict()
    if form.get('school_'):
        form['school'] = form.get('school_')
    form.pop('school_', None)
    for k, v in form.items():
        users.update_one({'id': current_user.id}, {'$set': {'profile.{}'.format(k): v}})
    flash('profile_completed')
    return redirect(url_for('users.dashboard', page='profile'))


@bp.route('/update_user', methods=['POST'])
@login_required
def update_user():
    user = request.form.get('user')
    user = json.loads(user)
    set_user(user['id'], user)
    return 'success'


@bp.route('/update_event', methods=['POST'])
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


@bp.route('/update_styf', methods=['POST'])
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


@bp.route('/update_master_class', methods=['POST'])
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


@bp.route('/update_ambassador', methods=['POST'])
@login_required
def update_ambassador():
    def _update_ambassador(value, day):
        old_val = get_db().users.find_one({'id': current_user.id}, {'events.fra.ambassador': 1})['events']['fra'].get('ambassador')
        if old_val and old_val.get(day):
            get_db().companies.update_one({'id': old_val.get(day)}, {'$unset': {'ambassadors.{}'.format(day): 1}})
            get_db().users.update_one({'id': current_user.id}, {'$unset': {'events.fra.ambassador.{}'.format(day): 1}})
        if value != 'none':
            get_db().companies.update_one({'id': value}, {'$set': {'ambassadors.{}'.format(day): current_user.id}})
            get_db().users.update_one({'id': current_user.id}, {'$set': {'events.fra.ambassador.{}'.format(day): value}})
    first = request.form.get('first')
    second = request.form.get('second')
    _update_ambassador(first, 'mercredi')
    _update_ambassador(second, 'jeudi')
    return 'success'
