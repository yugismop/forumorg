from app import app, get_db
from app.helpers import get_resume_url


@app.context_processor
def get_furnitures():
    def _get_furnitures():
        return list(get_db().furnitures.find({}, {'_id': False}))
    return dict(get_furnitures=_get_furnitures)


@app.context_processor
def get_events():
    def _get_events():
        return list(get_db().events.find({}, {'_id': False}))
    return dict(get_events=_get_events)


@app.context_processor
def get_resumes():
    def _get_resumes():
        users = list(
            get_db().users.find(
                {
                    'events.fra.registered': True, 'profile.resume_id': {
                        '$ne': None}}, {
                    'profile': 1, '_id': 0}))
        users = [u['profile'] for u in users]
        for u in users:
            full_name = '{} {}'.format(
                u.pop(
                    'name', None), u.pop(
                    'first_name', None))
            u['name'] = full_name
            u['resume_url'] = get_resume_url(
                u.pop('resume_id', None), u['name'])
        return users
    return dict(get_resumes=_get_resumes)


# Jinja Filters
@app.template_filter('to_jobs')
def to_jobs(company_id):
    jobs = list(get_db().jobs.find({'company_id': company_id}))
    # Casting id to prevent errors
    for j in jobs:
        j['_id'] = str(j['_id'])
    return jobs


@app.template_filter('to_furniture')
def to_furniture(furniture_id):
    return get_db().furnitures.find_one({'id': furniture_id})


@app.template_filter('to_days')
def to_days(duration):
    opts = {
        "wed": "Mercredi",
        "thu": "Jeudi",
        "both": "Mercredi & Jeudi"
    }
    return opts[duration]


@app.template_filter('to_size')
def to_size(size):
    return int(size) if float(size).is_integer() else float(size)


@app.template_filter('to_human')
def to_human(num):
    return str(num)


@app.template_filter('nb_dishes')
def nb_dishes(size):
    if size <= 12:
        return 2
    elif 12 < size <= 18:
        return 4
    elif size > 18:
        return 6


@app.template_filter('empty_furnitures')
def empty_furniture(f):
    return sum(f.values()) == 0


@app.template_filter('empty_events')
def empty_events(e):
    return any(e.values())


@app.template_filter('empty_dishes')
def empty_dishes(d):
    return sum([sum(a.values()) for a in d.values()]) == 0
