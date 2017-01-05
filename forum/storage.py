import os

import flask_login

from pymongo import MongoClient

db = None

def init_storage():
    global db
    client = MongoClient(host=os.environ.get('MONGODB_URI'))
    db = client.get_default_database()

def get_user(user_id):
    user = db.users.find_one({'id': user_id})
    user.pop('_id', None) if user else None
    return user

def new_user(user):
    try:
        db.users.insert_one({'id': user.id, 'password': user.password, 'events': {'joi': {}}})
        return True
    except:
        return False

def get_users():
    return db.users

def get_events():
    return db.events

class User(flask_login.UserMixin):

    def __init__(self, id, password=None, data=None):
        self.id = id
        self.password = password
        self.data = data

    def get_id(self):
        return self.id
