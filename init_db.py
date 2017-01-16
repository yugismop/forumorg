import os

from pymongo import MongoClient

try:
    client = MongoClient(host=os.environ.get('MONGODB_URI'))
    db = client.get_default_database()

    # Creating index
    db.users.create_index(keys='id', name='index_id', unique=True)

    # creating events
    db.events.insert_one({'name': 'styf', 'quota': 50, 'places_left': 50})
    db.users.update_many({}, {'$set': {'events.styf': {}}}) # Verifie que old and new users ont events.styf
except Exception as e:
    print(e)
