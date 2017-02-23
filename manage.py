from flask_script import Manager
from forum import app
from pymongo import MongoClient
import os
import csv
from flask_assets import ManageAssets


client = MongoClient(host=os.environ.get('MONGODB_URI'))
db = client.get_default_database()


manager = Manager(app)
manager.add_command("assets", ManageAssets())


@manager.command
def drop_schools_():
    cur = db.users.find({'profile.school_': {'$exists': True}}, {'_id': 0, 'profile.school_': 1})
    for c in cur:
        print(c)
    #db.users.update({'profile.school_': {'$exists': True}}, {'$unset': {'profile.school_': 1}})


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
