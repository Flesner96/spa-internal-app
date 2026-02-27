from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_email(subject, message, recipient_list):
    mail = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=recipient_list,
        subject=subject,
        plain_text_content=message,
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = sg.send(mail)

    return response.status_code