from flask import redirect, request, url_for
from itsdangerous import URLSafeTimedSerializer

from app import app, bcrypt, login_manager, storage
from app.models import Company


@login_manager.user_loader
def load_user(user_id):
    if '@' in user_id:
        return storage.get_user(user_id)
    else:
        return Company(id=user_id, data=storage.get_company(user_id))


@login_manager.unauthorized_handler
def unauthorized_handler():
    if 'candidats' in request.path:
        return redirect(url_for('users.signin'))
    else:
        return redirect(url_for('companies.signin'))


def validate_login(password_hashed, password_entered, section):
    if section == 'users':
        return bcrypt.check_password_hash(password_hashed, password_entered)
    else:
        return password_hashed == password_entered


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

# Handles both expiration variables


def confirm_token(token, expiration='TOKEN_EXPIRATION'):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=app.config[expiration]
        )
        return email
    except BaseException:
        return None
