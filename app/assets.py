from flask_assets import Bundle

bundles = {
    ### COMMON ###
    'js_common': Bundle(
        Bundle(
            'js/common.js',
            filters='jinja2'
        ),
        output='build/common.min.js'),

    'css_common': Bundle(
        Bundle(
            'css/common.css',
            filters='cssmin',
        ),
        output='build/common.min.css'),


    ### HOME ###
    'js_home': Bundle(
        Bundle(
            'typed.js/dist/typed.min.js',
            'jquery.scrollTo/jquery.scrollTo.min.js',
        ),
        Bundle(
            'js/home.js',
            filters='jsmin',
        ),
        output='build/home.min.js'),

    'css_home': Bundle(
        Bundle(
            'css/home/nemo.css',
            'css/home/colors/blue.css',
            'css/home/home.css',
            filters='cssrewrite,cssmin'
        ),
        output='build/home.min.css'),

    ### LOGIN ###
    'css_login': Bundle(
        Bundle(
            'AdminLTE/dist/css/AdminLTE.min.css'
        ),
        Bundle(
            'css/login.css',
            filters='cssmin'
        ),
        output='build/login.min.css'),

    ### DASHBOARD ###
    'js_dashboard': Bundle(
        Bundle(
            'select2/dist/js/select2.min.js',
            'select2/dist/js/i18n/fr.js',
            'PACE/pace.min.js',
            'jquery.inputmask/dist/min/jquery.inputmask.bundle.min.js',
            'intl-tel-input/build/js/intlTelInput.min.js',
            'datatables.net/js/jquery.dataTables.min.js',
            'datatables.net-bs/js/dataTables.bootstrap.min.js',
            'AdminLTE/dist/js/adminlte.min.js',
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
            filters='cssmin,cssrewrite',
        ),
        output='build/dashboard.min.css'),

    ### SPLIT ###
    'css_split': Bundle(
        Bundle(
            'css/split.css',
            filters='cssmin',
        ),
        output='build/split.min.css'),

}
