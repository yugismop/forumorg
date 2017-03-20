# coding=utf-8

import datetime

import flask_login

from app import bcrypt, get_db


def get_user(id):
    user = get_db().users.find_one({'id': id})
    if user:
        user.pop('_id', None)
        return User(id=user['id'], password=user['password'], data=user)
    else:
        return None


def confirm_user(user):
    return get_db().users.update_one(
        {'id': user.id},
        {'$set': {'confirmed': True, 'confirmed_on': datetime.datetime.now()}}
    )


def set_user(user_id, user_data):
    return get_db().users.replace_one({'id': user_id}, user_data)


def new_user(user):
    data = user.data
    data.pop('_id', None)
    return True if get_db().users.insert_one(data) else False


def get_users():
    return get_db().users


def get_events():
    return get_db().events


def user_exists(user_id):
    return bool(get_db().users.find_one({'id': user_id}))


class User(flask_login.UserMixin):

    def __init__(self, id=None, password=None, data={}, created=False):
        self.data = data
        self.data['id'] = id
        if created:
            self.data['password'] = bcrypt.generate_password_hash(password)
            self.data['registered_on'] = datetime.datetime.now()
            self.data['confirmed'] = False
            self.data['confirmed_on'] = None
            self.data['events'] = {'fra': {'registered': False}, 'joi': {'registered': False},
                                   'styf': {'registered': False}, 'master_class': {'registered': False}}
            self.data['profile'] = {}

    def get_id(self):
        return self.id

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError(item)
