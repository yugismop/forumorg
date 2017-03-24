from flask import redirect, render_template, request, send_from_directory, url_for, send_file, session, Blueprint, make_response, abort
from flask_login import login_required, logout_user
from .identicon import render_identicon

from binascii import hexlify
from io import BytesIO
from jinja2.exceptions import TemplateNotFound

from app import app, GridFS

from flask_login import current_user
from app.storage import get_users
from werkzeug import secure_filename
from bson.objectid import ObjectId
from gridfs.errors import NoFile

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


@bp.route('/clear')
def clear():
    return str(session.clear())


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
