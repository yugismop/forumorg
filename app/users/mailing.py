import os

import sendgrid

from sendgrid.helpers.mail import Email, Mail, Personalization, Substitution


def send_mail(recipient, confirm_url):
    # Create a text/plain message
    me = 'no-reply@forumorg.org'
    subject = 'Bienvenue à Forum Organisation!'
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    # Creating mail
    mail = Mail()
    mail.from_email = Email(me)
    mail.template_id = '494a8322-4f93-4a71-b8e1-6afb8dfa6ba6'
    personalization = Personalization()
    personalization.add_to(Email(recipient))
    mail.add_personalization(personalization)
    mail.personalizations[0].add_substitution(Substitution('-registration_link-', confirm_url))
    mail.personalizations[0].add_substitution(Substitution('-subject-', subject))

    # Sending email
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        return f'Email sent. {response}'
    except:
        return 'Email not sent.'
