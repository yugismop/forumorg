import os
from binascii import hexlify
from io import BytesIO

from flask import (Blueprint, abort, make_response, redirect, render_template,
                   request, send_file, send_from_directory, session, url_for)
from jinja2.exceptions import TemplateNotFound
from werkzeug import secure_filename

from app import app, s3_client
from app.storage import get_users
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

    users = get_users()
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            s3_client.put_object(ACL='public-read', Bucket=os.environ.get('BUCKET_NAME'), Metadata={'filename': filename},
                                 ContentType=file.content_type, Body=file, Key=f'resumes/{oid}.pdf')
            users.update_one({'id': current_user.id}, {'$set': {'profile.resume_id': str(oid)}})
        return 'success'
    if request.method == 'DELETE':
        oid = request.form['oid']
        s3_client.delete_object(Bucket=os.environ.get('BUCKET_NAME'), Key=f'resumes/{oid}.pdf')
        users.update_one({'id': current_user.id}, {'$unset': {'profile.resume_id': 1}})
        return 'success'
    if request.method == 'GET':
        try:
            file = s3_client.get_object(Bucket=os.environ.get('BUCKET_NAME'), Key=f'resumes/{oid}.pdf').get('Body')
            res = file.get('Body').read()
            response = make_response(res)
            response.mimetype = file.get('ContentType')
            return response
        except:
            abort(404)


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
