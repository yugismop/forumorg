from flask import flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for, send_file, session
from flask_login import login_required, login_user, logout_user
from .login import generate_confirmation_token, validate_login
from .storage import get_user, user_exists, new_user
from .models import User
from .identicon import render_identicon

from binascii import hexlify
from io import BytesIO

from jinja2.exceptions import TemplateNotFound

from app import app, mailing


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
                    'users.confirm_email', token=token, _external=True)
                mailing.send_mail(email, confirm_url)
                flash('user_registered')
                return redirect(url_for('signin'))
        else:
            user = User(id=email, password=password, created=True)
            token = generate_confirmation_token(email)
            confirm_url = url_for('users.confirm_email', token=token, _external=True)
            try:
                created = new_user(user)
                if created:
                    mailing.send_mail(email, confirm_url)
                    flash('user_registered')
                else:
                    flash('error')
            except Exception as e:
                print('error', e, user, user.data)
            return redirect(request.args.get('next') or url_for('signin'))
    return render_template('users/signup.html')


@app.route('/deconnexion')
def logout():
    logout_user()
    return redirect(url_for('index'))


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
