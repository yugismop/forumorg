import os

from pymongo import MongoClient


def main():
    try:
        client = MongoClient(host=os.environ.get('MONGODB_URI'))
        db = client.get_default_database()
        # Creating index
        db.users.create_index(keys='id', name='index_id', unique=True)
        # creating events
        # create_joi(db)
        # create_styf(db)
    except Exception as e:
        print(e)


def create_joi(db):
    fn = os.path.join(os.path.dirname(__file__), 'events.db')
    events = open(fn).read()
    events = events.split('\n')
    confs = [e.split(' - ') for e in events[:7]]
    tables = events[7:][:-1]
    for c in confs:
        db.events.insert_one({'name': c[0], 'type': 'conference', 'quota': int(c[1]), 'places_left': int(c[1])})
    for t in tables:
        db.events.insert_one({'name': t, 'quota': 30, 'type': 'table_ronde', 'places_left': {'first': 30, 'second': 30}})
    db.users.update_many({}, {'$set': {'events.joi': {}}})


def create_styf(db):
    # creating events
    db.events.insert_one({'name': 'styf', 'quota': 50, 'places_left': 50})
    db.users.update_many({}, {'$set': {'events.styf': {}}})
    db.users.update_many({}, {'$set': {'profile': {}}})


if __name__ == '__main__':
    main()
