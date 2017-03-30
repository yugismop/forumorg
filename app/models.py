import datetime

import flask_login
from app import bcrypt


class User(flask_login.UserMixin):

    def __init__(self, id=None, password=None, data={}, created=False):
        self.data = data
        self.data['id'] = id
        if created:
            self.data['password'] = bcrypt.generate_password_hash(password).decode('utf-8')
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


class Company(flask_login.UserMixin):

    def __init__(self, id, password=None, data=None):
        self.id = id
        self.password = password
        self.data = data

    def get_id(self):
        return self.id
