import datetime
from collections import OrderedDict, defaultdict
from app import app, get_db


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
            result[k] = list(OrderedDict(sorted(v.items())).values())
            print(result[k], v)
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
