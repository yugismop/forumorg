# coding=utf-8

import datetime
import os

import flask_login

from pymongo import MongoClient

from forum import bcrypt

db = None


def init_storage():
    global db
    client = MongoClient(host=os.environ.get('MONGODB_URI'))
    db = client.get_default_database()


def get_user(id):
    user = db.users.find_one({'id': id})
    if user:
        user.pop('_id', None)
        return User(id=user['id'], password=user['password'], data=user)
    else:
        return None


def confirm_user(user):
    return db.users.update_one(
        {'id': user.id},
        {'$set': {'confirmed': True, 'confirmed_on': datetime.datetime.now()}}
    )


def new_user(user):
    data = user.data
    data.pop('_id', None)
    return True if db.users.insert_one(data) else False


def get_users():
    return db.users


def get_events():
    return db.events

def get_profile():
    return db.profile

def user_exists(id):
    return True if db.users.find_one({'id': id}) else False


class User(flask_login.UserMixin):

    def __init__(self, id=None, password=None, data={}, created=False):
        self.data = data
        self.data['id'] = id
        if created:
            self.data['password'] = bcrypt.generate_password_hash(password)
            self.data['registered_on'] = datetime.datetime.now()
            self.data['confirmed'] = False
            self.data['confirmed_on'] = None
            self.data['events'] = {'joi': {'registered': False}, 'styf': {'registered': False}, 'master_class': {'registered': False}}
            self.data['profile'] = {}

    def get_id(self):
        return self.id

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError(item)
