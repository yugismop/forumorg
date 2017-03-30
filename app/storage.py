import datetime

from app import get_db

from .models import User


def get_user(id):
    user = get_db().users.find_one({'id': id}, {'_id': 0})
    return User(id=id, password=user['password'], data=user) if user else None


def get_company(company_id):
    return get_db().companies.find_one({'id': company_id}, {'_id': 0})


def set_company(company_id, company_data):
    return get_db().companies.replace_one({'id': company_id}, company_data)


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
