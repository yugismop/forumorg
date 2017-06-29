import datetime
import time
from collections import defaultdict

from app import app, get_db


@app.context_processor
def get_stats():
    def _get_stats():
        s = int(time.time())
        result = defaultdict(dict)
        sections = ['equipement', 'restauration', 'badges', 'transport', 'programme']
        for s in sections:
            cur = get_db().companies.aggregate([{'$skip': 1}, {'$group': {'_id': '$pole', 'all': {
                '$sum': 1}, 'validated': {'$sum': {'$cmp': ['${}'.format(s), False]}}}}])
            for c in cur:
                pole, total, validated = c['_id'], c['all'], c['validated']
                result[pole][s] = round(100.0 * validated / total, 2)
        result = {k: list(v.values()) for k, v in result.items()}
        result['labels'] = sections
        print('GET_STATS()')
        print(int(time.time())-s)
        return result
    return dict(get_stats=_get_stats)


@app.context_processor
def get_users():
    def _get_users():
        s = time.time()
        start = datetime.datetime(2017, 1, 9)  # pre-launch date
        days = (datetime.datetime.today() - start).days
        dates = [start + datetime.timedelta(inc) for inc in range(1, days + 2, 10)] # Stats every 10 days
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
        print('GET_USERS()')
        print(int(time.time())-s)
        return result
    return dict(get_users=_get_users)


@app.context_processor
def get_schools():
    def _get_schools():
        s = time.time()
        res = list(get_db().users.aggregate([{'$match': {'profile.school': {'$exists': True}}}, {'$group': {
                   '_id': '$profile.school', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}, {'$limit': 6}]))
        result = {}
        result['labels'] = [r['_id'] for r in res]
        result['count'] = [r['count'] for r in res]
        print('GET_SCHOOLS()')
        print(int(time.time())-s)
        return result
    return dict(get_schools=_get_schools)
