from flask_script import Manager
from app import app
from pymongo import MongoClient
import os
import csv
from flask_assets import ManageAssets


client = MongoClient(host=os.environ.get('MONGODB_URI'))
db = client.get_default_database()


manager = Manager(app)
manager.add_command("assets", ManageAssets())


@manager.command
def fix_dates():
    from datetime import datetime
    cur = db.users.find({}, {'_id': 1, 'registered_on': 1, 'confirmed_on': 1})
    for c in cur:
        if type(c['registered_on']) == unicode:
            print('original: {}'.format(c['registered_on']))
            new_d = datetime.strptime(c['registered_on'], '%a, %d %b %Y %H:%M:%S %Z')
            db.users.update_one({'_id': c['_id']}, {'$set': {'registered_on': new_d}})
            print('fixed: {}'.format(new_d))
        if type(c['confirmed_on']) == unicode:
            print('original: {}'.format(c['confirmed_on']))
            new_d = datetime.strptime(c['confirmed_on'], '%a, %d %b %Y %H:%M:%S %Z')
            db.users.update_one({'_id': c['_id']}, {'$set': {'confirmed_on': new_d}})
            print('fixed: {}'.format(new_d))


@manager.command
def drop_schools_():
    cur = db.users.find({'profile.school_': {'$exists': True}}, {'_id': 0, 'profile.school_': 1})
    for c in cur:
        print(c)


@manager.command
def complete_companies():
    path = os.path.join(os.path.dirname(__file__), 'data/new_companies.csv')
    reader = csv.DictReader(open(path, 'rb'))
    for row in reader:
        db.companies.update_one({'id': row['id_entreprise']}, {'$set': {'info': row}})
        db.companies.update_one({'id': row['id_entreprise']}, {'$unset': {'info.id_entreprise': 1}})


@manager.command
def create_transport():
    db.users.update_many({}, {'$set': {'events.fra.transports': []}})


if __name__ == "__main__":
    manager.run()
