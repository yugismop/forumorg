from wtforms import fields, form, validators


class UserForm(form.Form):
    pass


class CompanyForm(form.Form):
    # Basic
    id = fields.StringField('Identifiant', validators=[validators.Required(), validators.Length(
        min=3, max=30)], render_kw={"placeholder": "Ex. loreal, amadeus, canalplus"})
    password = fields.StringField('Mot de passe', validators=[validators.Required(
    ), validators.Length(min=3, max=30)], render_kw={"placeholder": "Ex. password"})
    name = fields.StringField('Nom complet', validators=[validators.Required(), validators.Length(
        min=3, max=30)], render_kw={"placeholder": "Ex. L'Oreal, Amadeus, Canal+"})
    acompte = fields.BooleanField('Acompte paye?')
    # Equipement
    emplacement = fields.StringField('Emplacement', render_kw={"placeholder": "Ex. F13"})
    size = fields.SelectField('Surface', choices=[(4.5, '4.5 m2'), (9, '9 m2'), (12, '12 m2'),
                                                  (18, '18 m2'), (24, '24 m2'), (27, '27 m2'), (36, '36 m2')], coerce=float)
    duration = fields.SelectField('Jours de presence', choices=[('wed', 'Mercredi'), ('thu', 'Jeudi'), ('both', 'Mercredi et Jeudi')])
    equiped = fields.BooleanField('Equipe?')
    pole = fields.SelectField('Pole', choices=[('fra', 'Entreprises France'), ('si', 'Section Internationale'),
                                               ('cm', 'Carrefour Maghrebin'), ('school', 'Ecoles'), ('startup', 'Start-Up')])
    zone = fields.SelectField('Zone', choices=[["zone{}".format(i)] * 2 for i in range(1, 10)])
    # Dashboard
    equipement = fields.BooleanField('Equipement valide?')
    restauration = fields.BooleanField('Restauration valide?')
    badges = fields.BooleanField('Badges valide?')
    transport = fields.BooleanField('Transports valide?')
    programme = fields.BooleanField('Programme valide?')


class JobForm(form.Form):
    pass


class StreamForm(form.Form):
    validated = fields.BooleanField('Valider')
    delivered = fields.BooleanField('Livrer')
    denied = fields.BooleanField('Refuser')
    comment = fields.StringField('Commentaire')
