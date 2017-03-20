# coding=utf-8

import os
import json
from flask import Flask, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_qrcode import QRcode
from flask_sslify import SSLify
from gridfs import GridFS
from bson.objectid import ObjectId


# App init
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'my_debug_key')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('FLASK_PASSWORD_SALT', 'my_debug_salt')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TOKEN_EXPIRATION'] = int(os.environ.get('TOKEN_EXPIRATION', 7200))

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Bcrypt
bcrypt = Bcrypt(app)

# QRCode
qrcode = QRcode(app)

# SSLify
sslify = SSLify(app)

# Storage init
from storage import init_storage, get_db
init_storage()
GridFS = GridFS(get_db(), collection='resumes')


@app.template_filter('to_companies')
def to_companies(day):
    if day == 'mercredi':
        duration = 'wed'
    elif day == 'jeudi':
        duration = 'thu'

    cur = get_db().companies.find({'duration': {'$in': [duration, 'both']}}, {
        'id': 1, 'name': 1, 'pole': 1, 'ambassadors.{}'.format(day): 1, '_id': 0})
    cur = list(cur)
    cur = [l for l in cur if l['id'] != 'admin']
    cur = [l for l in cur if l['id'] != 'test']
    res = []
    for c in cur:
        is_filled = bool(c.get('ambassadors') and c.get('ambassadors').get(day))
        d = {'id': c['id'], 'name': c['name'].lower().capitalize(), 'is_filled': is_filled}
        if c.get('pole'):
            res.append(d)
    return res


@app.context_processor
def get_companies():
    def _get_companies():
        companies = get_db().companies.aggregate([
            {'$match':
             {'id': {'$nin': ['test', 'admin']}}
             },
            {'$project':
             {
                 'duration': 1, 'id': '$id', 'name_old': '$name', 'name': '$info.name', 'sector': '$info.sector',
                 'city': '$info.city', 'country': '$info.country', 'revenue': '$info.revenue', '_id': 0
             }
             }])
        companies = list(companies)
        conv = {'wed': 'Mercredi', 'thu': 'Jeudi', 'both': 'Mercredi et Jeudi'}
        for c in companies:
            c['duration'] = conv[c['duration']]
        return companies
    return dict(get_companies=_get_companies)


@app.context_processor
def get_jobs():
    def _get_jobs():
        jobs = get_db().jobs.find(
            {},
            {"_id": 0, "company_id": 1, "description": 1, "title": 1, "url": 1, "location": 1, "duration": 1, "type": 1},
        )
        jobs = list(jobs)
        for j in jobs:
            doc = get_db().companies.find_one({"id": j["company_id"]})
            j['name'] = doc['info']['name'] if doc.get('info') else doc['name']
        return jobs
    return dict(get_jobs=_get_jobs)


@app.context_processor
def get_events():
    def _get_events():
        return list(get_db().events.find({}))
    return dict(get_events=_get_events)


@app.template_filter('to_fields')
def to_fields(type):
    if type == 'specialties':
        return ['Informatique', 'Electronique', 'Biochimie', u'Télécommunications',
                'Bioinformatique', 'Commercial & Marketing', 'Chimie', 'Biologie',
                u'Matériaux', 'Agronomie', u'Génie Industriel', u'Génie Civil', u'Génie Mécanique', u'Génie Electrique', u'Génie Énergétique']
    if type == 'schools':
        return ['INSA Lyon', 'CPE Lyon', 'Polytech Lyon', 'Centrale Lyon', 'EM Lyon',
                u'Université Lyon 1', u'Université Lyon 2', u'Université Lyon 3', 'IAE Lyon',
                'ECAM', 'Mines Saint-Etienne', 'INP Grenoble', 'EI Cesi', 'Polytech Grenoble', 'Telecom Saint-Etienne']
    if type == 'years':
        return ['Bac+{}'.format(i) for i in range(1, 6)]


@app.template_filter('to_str')
def to_jobs(lst):
    return ', '.join(json.loads(lst))


@app.template_filter('to_filename')
def to_filename(oid):
    file = GridFS.get(ObjectId(oid))
    return file.filename


@app.template_filter('to_info')
def to_info(oid):
    if not oid:
        return json.dumps({'empty': True})
    file = GridFS.get(ObjectId(oid))
    r = {"url": url_for('get_resume', oid=str(oid)),
         "size": file.length,
         "name": file.name}
    return json.dumps(r)


@app.template_filter('to_ambassador')
def to_ambassador(user_id):
    return get_db().users.find_one({'id': user_id}, {'events.fra.ambassador': 1})['events']['fra'].get('ambassador')


@app.template_filter('to_name')
def to_name(company_id):
    comp = get_db().companies.find_one({'id': company_id}, {'name': 1})
    return comp.get('name') if comp else None


import assets
import views
