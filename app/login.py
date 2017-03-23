from flask import redirect, url_for
from app import app, bcrypt, login_manager, storage
from itsdangerous import URLSafeTimedSerializer


@login_manager.user_loader
def load_user(user_id):
    return storage.get_user(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('signin'))


def validate_login(password_hashed, password_entered):
    return bcrypt.check_password_hash(password_hashed, password_entered)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=app.config['TOKEN_EXPIRATION']
        )
        return email
    except:
        return None
