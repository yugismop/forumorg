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
def complete_companies():
    path = os.path.join(os.path.dirname(__file__), 'data/companies.csv')
    reader = csv.reader(open(path, 'rb'))
    for row in reader:
        db.companies.update({'id': row[0]})
    #companies = [row for row in reader][1:]
    #print(companies[0])


@manager.command
def create_transport():
    db.users.update_many({}, {'$set': {'events.fra.transports': []}})


if __name__ == "__main__":
    manager.run()
