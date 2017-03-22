from flask import Blueprint, render_template, flash, redirect, url_for, request, make_response, abort
from flask_login import login_required, current_user
from app import get_db, GridFS
from app.storage import get_user, confirm_user, get_users
from werkzeug import secure_filename
from app.login import confirm_token
from bson.objectid import ObjectId
from gridfs.errors import NoFile

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


@bp.route('/dashboard/companies/<company_id>')
@login_required
def companies(company_id=None):
    company = get_db().companies.find_one({'id': company_id})
    return render_template('users/dashboard/sections/company.html', company=company)


@bp.route('/confirmation/<token>')
def confirm_email(token):
    email = confirm_token(token)

    if not email:
        flash('confirm_link_expired', 'danger')
        return redirect(url_for('signin'))

    user = get_user(id=email)
    if not user:
        flash('error')
        return redirect(url_for('signin'))
    if user.confirmed:
        flash('account_already_confirmed', 'success')
    else:
        confirm_user(user)
        flash('account_confirmed', 'success')
    return redirect(url_for('signin'))


@bp.route('/cv', methods=['POST', 'DELETE'])
@bp.route('/cv/<oid>', methods=['GET'])
@login_required
def resume(oid=None):
    # Allowed files
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ['pdf', 'txt']

    users = get_users()
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            oid = GridFS.put(file, content_type=file.content_type, filename=filename)
            users.update_one({'id': current_user.id}, {'$set': {'profile.resume_id': str(oid)}})
        return 'success'
    if request.method == 'DELETE':
        GridFS.delete(ObjectId(request.form['oid']))
        users.update_one({'id': current_user.id}, {'$set': {'profile.resume_id': None}})
        return 'success'
    if request.method == 'GET':
        try:
            file = GridFS.get(ObjectId(oid))
            response = make_response(file.read())
            response.mimetype = file.content_type
            return response
        except NoFile:
            abort(404)
