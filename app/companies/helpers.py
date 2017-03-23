import datetime
from collections import OrderedDict, defaultdict

from flask import url_for
from app import app, get_db


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
        users = list(get_db().users.find({'events.fra.registered': True, 'profile.resume_id': {'$ne': None}}, {'profile': 1, '_id': 0}))
        users = [u['profile'] for u in users]
        for u in users:
            u['name'] = u'{} {}'.format(u.pop('name', None), u.pop('first_name', None))
            u['resume_url'] = url_for('main.resume', oid=u.pop('resume_id', None))
        return users
    return dict(get_resumes=_get_resumes)


@app.context_processor
def get_stats():
    def _get_stats():
        result = defaultdict(dict)
        for s in ['equipement', 'restauration', 'badges', 'transport', 'programme']:
            cur = get_db().companies.aggregate([{'$skip': 1}, {'$group': {'_id': '$pole', 'all': {
                '$sum': 1}, 'validated': {'$sum': {'$cmp': ['${}'.format(s), False]}}}}])
            for c in cur:
                pole, total, validated = c['_id'], c['all'], c['validated']
                result[pole][s] = round(100.0 * validated / total, 2)
        for k, v in result.items():
            result[k] = OrderedDict(sorted(v.items()))
        result = OrderedDict(sorted(result.items()))
        return result
    return dict(get_stats=_get_stats)


@app.context_processor
def get_users():
    def _get_users():
        start = datetime.datetime(2017, 1, 9)  # pre-launch date
        days = (datetime.datetime.today() - start).days
        dates = [start + datetime.timedelta(inc) for inc in range(days + 2)]
        result = {}
        confirmed = []
        registered = []
        fra = []
        for d in dates:
            registered.append(get_db().users.find({'registered_on': {'$lte': d}}).count())
            confirmed.append(get_db().users.find({'confirmed': True, 'registered_on': {'$lte': d}}).count())
            fra.append(get_db().users.find({'events.fra.registered': True, 'registered_on': {'$lte': d}}).count())
        result['labels'] = [d.strftime('%d-%m') for d in dates]
        result['fra'] = fra
        result['confirmed'] = confirmed
        result['registered'] = registered
        return result
    return dict(get_users=_get_users)


@app.context_processor
def get_schools():
    def _get_schools():
        res = list(get_db().users.aggregate([{'$match': {'profile.school': {'$exists': True}}}, {'$group': {
                   '_id': '$profile.school', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}, {'$limit': 6}]))
        result = {}
        result['labels'] = [r['_id'] for r in res]
        result['count'] = [r['count'] for r in res]
        return result
    return dict(get_schools=_get_schools)


# Jinja Filters
@app.template_filter('to_jobs')
def to_jobs(company_id):
    jobs = list(get_db().jobs.find({'company_id': company_id}))
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
