import os

from flask_assets import Bundle, Environment
from app import app

assets = Environment(app)

assets.append_path(os.path.join(os.path.dirname(__file__), './static'))
assets.append_path(os.path.join(os.path.dirname(__file__), './static/bower_components'))

bundles = {
    ### COMMON ###
    'js_common': Bundle(
        Bundle(
            'jquery/dist/jquery.min.js',
            'bootstrap/dist/js/bootstrap.min.js',
            Bundle(
                'js/common.js',
                filters='jinja2'
            )
        ),
        output='build/common.min.js'),

    'css_common': Bundle(
        Bundle(
            'bootstrap/dist/css/bootstrap.min.css',
            'font-awesome/css/font-awesome.min.css',
            filters='cssrewrite'
        ),
        Bundle(
            'css/common.css',
            filters='cssmin',
        ),
        output='build/common.min.css'),


    ### HOME ###
    'js_home': Bundle(
        Bundle(
            'recaptcha/index.js',
            'typed.js/dist/typed.min.js',
            'jquery.scrollTo/jquery.scrollTo.min.js',
            Bundle(
                'jQuery-One-Page-Nav/jquery.nav.js',
                filters='jsmin',
            ),
        ),
        Bundle(
            'js/home.js',
            filters='jsmin',
        ),
        output='build/home.min.js'),

    'css_home': Bundle(
        Bundle(
            'css/index/nemo.css',
            'css/index/colors/blue.css',
            filters='cssmin'
        ),
        output='build/home.min.css'),

    ### LOGIN ###
    'css_sign': Bundle(
        Bundle(
            'AdminLTE/dist/css/AdminLTE.min.css'
        ),
        Bundle(
            'css/index/login.css',
            filters='cssmin'
        ),
        output='build/login.min.css'),

    'js_dashboard': Bundle(
        Bundle(
            'select2/dist/js/select2.min.js',
            'select2/dist/js/i18n/fr.js',
            'PACE/pace.min.js',
            'jquery.inputmask/dist/min/jquery.inputmask.bundle.min.js',
            'intl-tel-input/build/js/intlTelInput.min.js',
            'datatables.net/js/jquery.dataTables.min.js',
            'datatables.net-bs/js/dataTables.bootstrap.min.js',
            'AdminLTE/dist/js/app.min.js',
            'jquery.countdown/dist/jquery.countdown.min.js',
            'dropzone/dist/min/dropzone.min.js',
        ),
        Bundle(
            'notify-js/Notify.js',
            'js/dashboard.js',
            filters='jsmin',
        ),
        output='build/dashboard.min.js'),

    'css_dashboard': Bundle(
        Bundle(
            'AdminLTE/dist/css/AdminLTE.min.css',
            'AdminLTE/dist/css/skins/skin-blue.min.css',
            'select2/dist/css/select2.min.css',
            'datatables.net-bs/css/dataTables.bootstrap.min.css',
            'dropzone/dist/min/dropzone.min.css',
        ),
        Bundle(
            'PACE/themes/white/pace-theme-minimal.css',
            'intl-tel-input/build/css/intlTelInput.css',
            'css/admin.css',
            filters='cssmin',
        ),
        output='build/dashboard.min.css'),

    'css_split': Bundle(
        Bundle(
            'css/split.css'
        ),
        output='build/split.min.css'),

    ### ADMIN ###
    'js_admin': Bundle(
        Bundle(
            'chart.js/dist/Chart.min.js',
        ),
        output='build/admin.min.js'),

}

if os.environ.get('DEBUG'):
    assets.register(bundles)
