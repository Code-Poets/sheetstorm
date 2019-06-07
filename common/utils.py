from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.models import CustomUser
from users.tokens import account_activation_token


def send_email(mail_subject: str, message: str, addressee: str) -> None:
    email = EmailMessage(mail_subject, message, to=[addressee])
    email.send()


def render_confirmation_email(user: CustomUser, domain: str) -> str:
    user_name = user.email if user.first_name in ["", " "] else user.first_name
    return render_to_string(
        "account_confirmation/confirmation_email.html",
        {
            "user_name": user_name,
            "domain": domain,
            "encoded_user_id": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )
