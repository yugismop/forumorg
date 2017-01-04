from flask import redirect, url_for
from forum import login_manager
from storage import get_user, user

@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id, data=get_user(user_id))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

def validate_login(password_input, password_real):
    return password_input == password_real
