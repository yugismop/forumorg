# coding=utf-8

import json
import os
import requests
import datetime

from flask import abort, redirect, render_template, request, make_response, session, Blueprint, url_for
from flask_login import current_user, login_required, login_user
from app.storage import get_company, set_company
from app.login import validate_login
from app.models import Company

from app import app, GridFS, get_db
from gridfs.errors import NoFile
from .mailing import send_mail
from bson.objectid import ObjectId
from .stream import get_diff

bp = Blueprint('companies', __name__)


# INDEX
@bp.route('/')
@bp.route('/<page>')
def index(page='index'):
    session['section'] = 'companies'
    app.logger.info(f'COMPANIES->{page}//{session["section"]}')
    return render_template(f'companies/{page}.html')


@bp.route('/connexion', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        remember_me = 'remember_me' in request.form
        company_id = request.form.get('id')
        password = request.form.get('password')
        company = get_company(company_id)
        # checking stuff out
        if not company_id or not password:
            return render_template('companies/signin.html', error="blank_fields")
        if not company:
            return render_template('companies/signin.html', error="no_company_found")
        if not validate_login(company['password'], password, 'companies'):
            return render_template('companies/signin.html', error="wrong_password")
        # all is good
        company = Company(id=company_id, password=password)
        print(f'connected_as: {company_id}')
        login_user(company, remember=remember_me)
        return redirect(url_for('companies.dashboard'))
    else:
        return render_template('companies/signin.html')


# Admin
@bp.route('/dashboard')
@bp.route('/dashboard/<page>')
@login_required
def dashboard(page=None):
    company = None
    if current_user.id == 'admin':
        if request.args.get('id'):
            session['company_id'] = request.args.get('id')
        if not session.get('company_id'):
            return redirect('/admin')
        company = get_company(session['company_id'])
    if not page or page == 'accueil':
        return render_template('companies/dashboard/sections/dashboard.html', company=company)
    return render_template('companies/dashboard/sections/{}.html'.format(page), company=company)


@bp.route('/update_company', methods=["POST"])
@login_required
def update_company():
    page = request.form.get('page')
    if current_user.data.get(page) and current_user.id != 'admin':
        return "error"
    else:
        company = request.form.get('company')
        company = json.loads(company)
        old_company = get_db().companies.find_one({'id': company['id']}, {'_id': 0})
        set_company(company['id'], company)
        send_event(old_company, company, page)
        return "success"


def send_event(old_company, company, page):
    zone, company_id = company.get('zone'), company.get('name')
    dt = datetime.datetime.now().strftime('%A %H:%M:%S')
    try:
        diff = get_diff(old_company, company)
    except Exception as e:
        diff = {'error': e}
    if diff:
        get_db().stream.insert({'delivered': False, 'validated': False, 'section': page,
                                'zone': zone, 'created_on': dt, 'company': company_id, 'diff': diff})


@bp.route('/validate_section', methods=["POST"])
@login_required
def validate_section():
    page = request.form.get('page')
    if not current_user.data.get(page):
        get_db().companies.update_one({'id': current_user.id}, {'$set': {page: True}})
        return "success"
    else:
        return "error"


@bp.route('/update_banner', methods=["POST"])
@login_required
def update_banner():
    if not current_user.data.get('equipement'):
        company_id = request.form.get('pk')
        banner = request.form.get('value')

        company = get_company(company_id)
        company['banner'] = banner
        set_company(company['id'], company)
        return "success"
    else:
        abort(500)


@bp.route('/add_job', methods=["POST"])
@login_required
def add_job():
    job = request.form.get('job')
    job = json.loads(job)
    get_db().jobs.insert_one(job)
    return "success"


@bp.route('/remove_job', methods=["POST"])
@login_required
def remove_job():
    job_id = request.form.get('id')
    get_db().jobs.delete_one({'_id': ObjectId(job_id)})
    return "success"


@bp.route('/send_request', methods=["GET"])
def send_request():
    # Params
    email = request.args.get('email')
    contact_name = request.args.get('nom_complet')
    company_name = request.args.get('nom')
    telephone = request.args.get('tel')
    captcha = request.args.get('captcha')

    # ReCaptcha
    base_url = 'https://www.google.com/recaptcha/api/siteverify'
    secret = os.environ.get('RECAPTCHA_SECRET_KEY')
    res = requests.post(base_url, data={'response': captcha, 'secret': secret}).json()

    # Sending mail...
    if res.get('success'):
        return send_mail(email, contact_name, company_name, telephone)
    else:
        abort(500)
