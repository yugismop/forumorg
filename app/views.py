import os
from binascii import hexlify
from io import BytesIO

from flask import (Blueprint, abort, redirect, render_template, request,
                   send_file, send_from_directory, session, url_for)
from jinja2.exceptions import TemplateNotFound
from werkzeug import secure_filename

from app import app, get_db, s3_client
from bson.objectid import ObjectId
from flask_login import current_user, login_required, logout_user

from .identicon import render_identicon

bp = Blueprint('main', __name__)


# INDEX
# start of app
@bp.route('/')
@bp.route('/<page>')
def index(page=None):
    cur_section = session.get('section')
    arg_section = request.args.get('section')
    if cur_section and not arg_section:
        return redirect(url_for(f'{cur_section}.index', page=page))
    return render_template('split.html')


@bp.route('/cv', methods=['POST', 'DELETE'])
@bp.route('/cv/<oid>', methods=['GET'])
@login_required
def resume(oid=None):
    # Allowed files
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ['pdf']

    if request.method == 'POST':
        file = request.files.get('resume')
        profile = current_user.data.get('profile')
        is_valid_profile = profile.get('first_name') and profile.get('name')
        if file and allowed_file(file.filename) and is_valid_profile:
            filename = secure_filename(file.filename)
            oid = ObjectId()
            s3_client.put_object(Bucket=os.environ.get('BUCKET_NAME'), Metadata={'filename': filename},
                                 ContentType=file.content_type, Body=file, Key=f'resumes/{oid}.pdf')
            get_db().users.update_one({'id': current_user.id}, {'$set': {'profile.resume_id': str(oid)}})
            return 'success'
        else:
            abort(500)
    if request.method == 'DELETE':
        oid = request.form['oid']
        s3_client.delete_object(Bucket=os.environ.get('BUCKET_NAME'), Key=f'resumes/{oid}.pdf')
        get_db().users.update_one({'id': current_user.id}, {'$unset': {'profile.resume_id': 1}})
        return 'success'


@bp.route('/deconnexion')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/identicon', methods=['GET'])
@login_required
def identicon():
    text = request.args.get('text', 'EMPTY')
    code = int(hexlify(text.encode('utf-8')), 16)
    size = 25
    img = render_identicon(code, size)
    stream = BytesIO()
    img.save(stream, format='png')
    stream.seek(0)
    return send_file(
        stream,
        mimetype='image/png'
    )


# SEO
@app.route('/sondage')
def typeform():
    return render_template('typeform.html')


# SEO
@app.route('/robots.txt')
@app.route('/favicon.ico')
def static_from_root():
    # Edge case to disallow staging env indexing
    if os.getenv('STAGING') and request.path[1:] == 'robots.txt':
        print(request.path, os.getenv('STAGING'))
        return send_from_directory(app.static_folder, 'robots_staging.txt')
    return send_from_directory(app.static_folder, request.path[1:])


# JS logging
@bp.route('/js_log', methods=['POST'])
def js_log():
    print('js_log', request.form.to_dict())
    return 'success'


# Error handling
@app.errorhandler(404)
@app.errorhandler(TemplateNotFound)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
