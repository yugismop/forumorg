# coding=utf-8

import datetime

from app import get_db
from models import User


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
