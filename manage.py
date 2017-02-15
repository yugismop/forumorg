from flask_script import Manager
from forum import app
from pymongo import MongoClient
import os
from flask_assets import ManageAssets


client = MongoClient(host=os.environ.get('MONGODB_URI'))
db = client.get_default_database()


manager = Manager(app)
manager.add_command("assets", ManageAssets())


@manager.command
def create_transport():
    db.users.update_many({}, {'$set': {'events.fra.transports': []}})


if __name__ == "__main__":
    manager.run()
