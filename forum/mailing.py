import os

import sendgrid

from sendgrid.helpers.mail import *

BASE_EMAIL = """
<p>Bienvenue a la plateforme de Forum Organisation!</p>
<p><a href="{}">Veuillez cliquer sur ce lien pour activer votre compte</a></p>
<p>La bise,</p>
<p>L'equipe Forum Organisation.</p>
"""

def send_mail(recipient, confirm_url):
    # Create a text/plain message
    me = 'no-reply@forumorg.org'
    you = recipient
    subject = '[ForumOrg] Lien d\'activation'
    text = BASE_EMAIL.format(confirm_url)

    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    # Setting from, subject, content, reply to
    from_email = Email(me)
    to_email = Email(you)
    content = Content('text/html', text)
    mail = Mail(from_email, subject, to_email, content)
    # Adding bcc
    mail.personalizations[0].add_bcc(Email('elmehdi.baha@forumorg.org'))
    # Sending email
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        return 'Email sent.'
    except:
        return 'Email not sent.'
