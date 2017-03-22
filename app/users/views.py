from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('users', __name__)


# ADMIN
@bp.route('/dashboard/')
@bp.route('/dashboard/<page>')
@login_required
def dashboard(page=None):
    if page:
        if page in ['companies', 'ticket', 'jobs'] and not current_user.events['fra'].get('registered'):
            render_template('users/dashboard/sections/fra.html')
        return render_template(f'users/dashboard/sections/{page}.html')
    else:
        return render_template('users/dashboard/sections/dashboard.html')
