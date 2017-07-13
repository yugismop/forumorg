import json
import os

from app import app, get_db, s3_client
from app.helpers import get_resume_url
from flask_login import current_user


@app.template_filter('to_companies')
def to_companies(day):
    if day == 'mercredi':
        duration = 'wed'
    if day == 'jeudi':
        duration = 'thu'

    cur = get_db().companies.find({'duration': {'$in': [duration, 'both']}}, {
        'id': 1, 'name': 1, 'pole': 1, f'ambassadors.{day}': 1, '_id': 0})
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


@app.template_filter('to_fields')
def to_fields(type):
    if type == 'specialties':
        return ['Informatique', 'Electronique', 'Biochimie', 'Télécommunications',
                'Bioinformatique', 'Commercial & Marketing', 'Chimie', 'Biologie',
                'Matériaux', 'Agronomie', 'Génie Industriel', 'Génie Civil', 'Génie Mécanique', 'Génie Electrique', 'Génie Énergétique']
    if type == 'schools':
        return ['INSA Lyon', 'CPE Lyon', 'Polytech Lyon', 'Centrale Lyon', 'EM Lyon', 'Université Jean Monnet',
                'Université Lyon 1', 'Université Lyon 2', 'Université Grenoble Alpes', 'Université Lyon 3', 'IAE Lyon',
                'ECAM', 'Mines Saint-Etienne', 'INP Grenoble', 'EI Cesi', 'Polytech Grenoble', 'Telecom Saint-Etienne']
    if type == 'years':
        return [f'Bac+{i}' for i in range(1, 6)]
    if type == 'transports':
        return ['Gare Part-Dieu', 'Forum Rhône-Alpes', 'Hôtel Okko', 'Hôtel Lyon Metropole', 'Aéroport Saint Exupéry',
                'Soirée Networking', 'Hôtel Ibis Part Dieu', 'Hôtel Le Roosvelt', 'Hôtel Carlton',
                'Hôtel Reine Astrid', 'Hôtel Park et Suites Lyon Part-Dieu', 'Gare Perrache', 'Hôtel Campanile Part-Dieu',
                'Hôtel Mercure Lyon Centre', 'B&B Hôtel Lyon Caluire Cité Internationale',
                'Hotel Ibis Lyon Gerland Musée des Confluences', 'Hôtel Tête d\'Or', 'Hôtel Comfort Suites Rive Gauche Lyon Centre']


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
            {'_id': 0, 'company_id': 1, 'description': 1, 'title': 1, 'url': 1, 'location': 1, 'duration': 1, 'type': 1},
        )
        jobs = list(jobs)
        for j in jobs:
            doc = get_db().companies.find_one({'id': j['company_id']})
            j['name'] = doc['info']['name'] if doc.get('info') else doc['name']
        return jobs
    return dict(get_jobs=_get_jobs)


@app.context_processor
def get_events():
    def _get_events():
        return list(get_db().events.find({}))
    return dict(get_events=_get_events)


@app.template_filter('to_str')
def to_jobs(lst):
    return ', '.join(json.loads(lst))


@app.template_filter('to_filename')
def to_filename(oid):
    try:
        return s3_client.get_object(Bucket=os.environ.get('BUCKET_NAME'), Key=f'resumes/{oid}.pdf').get('Metadata').get('filename')
    except:
        return None


@app.template_filter('to_info')
def to_info(oid):
    try:
        file = s3_client.get_object(Bucket=os.environ.get('BUCKET_NAME'), Key=f'resumes/{oid}.pdf')
        profile = current_user.data.get('profile')
        full_name = f'[{profile["name"]} {profile["first_name"]}'
        r = {'url': get_resume_url(oid, full_name),
             'size': file.get('ContentLength'),
             'name': file.get('Metadata').get('filename'),
             'oid': str(oid)}
        return json.dumps(r)
    except:
        return json.dumps({'empty': True})


@app.template_filter('to_ambassador')
def to_ambassador(user_id):
    return get_db().users.find_one({'id': user_id}, {'events.fra.ambassador': 1})['events']['fra'].get('ambassador')


@app.template_filter('to_name')
def to_name(company_id):
    comp = get_db().companies.find_one({'id': company_id}, {'name': 1})
    return comp.get('name') if comp else None
