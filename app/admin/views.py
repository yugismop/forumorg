from flask import url_for
from jinja2 import Markup

from flask_admin.base import BaseView, expose
from flask_admin.contrib.pymongo import ModelView
from flask_admin.form import rules
from flask_login import current_user

from .export import _export
from .filters import FilterField, FilterRegister
from .forms import CompanyForm, JobForm, StreamForm, UserForm


def formatter(view, context, model, name):
    if model['id'] == 'admin':
        url = url_for('admin.index')
    else:
        url = url_for('companies.dashboard', id=model['id'])
    return Markup("<a target='_blank' href='{}'>{}</a>".format(url, model['id']))


class AdminView(ModelView):

    def __init__(self, *args, **kwargs):
        super(AdminView, self).__init__(*args, **kwargs)

    def is_accessible(self):
        return current_user.get_id() == 'admin' and current_user.is_authenticated


class StatisticsView(BaseView):

    def __init__(self, *args, **kwargs):
        super(StatisticsView, self).__init__(*args, **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'admin'

    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    def is_accessible(self):
        return current_user.get_id() == 'admin' and current_user.is_authenticated


class CompanyView(AdminView):
    form = CompanyForm
    column_list = ['id'] + ['equipement', 'transport',
                            'restauration', 'badges', 'programme']
    export_types = ['equipement', 'transport', 'restauration', 'badges', 'programme', 'secteurs']
    form_rules = [
        rules.FieldSet(('id', 'password', 'name', 'pole', 'zone'), 'Profil'),
        rules.FieldSet(('equipement', 'restauration', 'badges',
                        'programme', 'transport'), 'Suivi'),
        rules.FieldSet(('acompte',), 'Finances'),
        rules.FieldSet(('size', 'duration', 'equiped',
                        'emplacement'), 'Equipement'),
    ]
    can_export = True
    column_searchable_list = ['id']
    column_sortable_list = ['id']
    column_filters = (
        FilterField(column='pole', name='pole', options=(('fra', 'Entreprises France'), ('si', 'Section Internationale'),
                                                         ('cm', 'Carrefour Maghrebin'), ('school', 'Ecoles'), ('startup', 'Start-Up'))),
        FilterField(column='zone', name='zone', options=[["zone{}".format(i)] * 2 for i in range(1, 9)]),
        FilterField(column='duration', name='jours', options=[('wed', 'Mercredi'), ('thu', 'Jeudi')]))
    column_labels = dict(id='Identifiant')
    column_formatters = dict(id=formatter)

    @expose('/export/<export_type>/')
    def export(self, export_type):
        return _export(self, export_type)

    def _on_model_change(self, form, model, is_created):
        if is_created:
            model['sections'] = {
                'furnitures': {}, 'catering': {'wed': {}, 'thu': {}}, 'events': {},
                'persons': [], 'transports': [], 'profile': {'stand': {}, 'facturation': {}}
            }


class UserView(AdminView):
    column_list = ['id', 'events', 'confirmed_on', 'registered_on', 'profile']
    column_labels = dict(id='Email', confirmed_on='Confirmation', registered_on='Inscription', profile='Profil', events='Participations')
    export_types = ['general']
    can_export = True
    can_edit = False
    can_delete = False
    can_view_details = True
    form = UserForm
    column_details_list = column_list.copy()
    column_details_list.remove('confirmed_on')
    column_details_list.remove('events')
    column_searchable_list = ('id',)
    column_filters = (FilterRegister(column='events', name='inscrit', options=(
        ('master_class', 'Master Class'),
        ('fra', 'Forum Rhone-Alpes'),
        ('ambassador', 'Ambassadeur'),
        ('styf', 'Start-Up Your Future'),
        ('joi', 'Journee Objectif Ingenieur'))),)
    column_sortable_list = ['id', 'confirmed_on', 'registered_on']

    @expose('/export/<export_type>/')
    def export(self, export_type):
        return _export(self, export_type)


class JobView(AdminView):
    column_list = ['company_id', 'title', 'location', 'duration', 'description']
    column_labels = dict(company_id='Entreprise', duration='Duree', location='Lieu')
    can_edit = False
    can_delete = False
    form = JobForm
    can_view_details = True
    column_sortable_list = ['company_id', 'title', 'location', 'duration']
    column_details_list = column_list.copy()
    column_details_list.remove('description')


class StreamView(AdminView):
    column_list = ['created_on', 'company', 'zone', 'section', 'diff', 'validated', 'delivered', 'denied', 'comment']
    column_labels = dict(created_on=u'Créé le', company='Entreprise', diff='Message',
                         validated=u'Validé', delivered=u'Livré', denied=u'Refusé', comment='Commentaire')
    form = StreamForm
    can_delete = False
    column_filters = (
        FilterField(column='validated', name='validation', options=(
            ('oui', 'oui'), ('non', 'non'))),
        FilterField(column='delivered', name='livraison', options=(
            ('oui', 'oui'), ('non', 'non'))),
        FilterField(column='denied', name='refus', options=(
            ('oui', 'oui'), ('non', 'non'))),
        FilterField(column='zone', name='zone', options=[["zone{}".format(i)] * 2 for i in range(1, 9)]),
        FilterField(column='section', name='section', options=[['restauration', 'restauration'], [
                    'transport', 'transport'], ['badges', 'badges'], ['equipement', 'equipement']])
    )
