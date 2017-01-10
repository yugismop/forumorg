# coding=utf-8

from flask import redirect, url_for
from forum import app, bcrypt, login_manager
from itsdangerous import URLSafeTimedSerializer
from storage import get_user, new_user


@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


def validate_login(password_hashed, password_entered):
    return bcrypt.check_password_hash(password_hashed, password_entered)


def create_user(user):
    return new_user(user)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except:
        return None
