from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
import logging


@shared_task
def send_verification_email(user_id, verification_code):
    """
    Задача для отправки письма подтверждения почты
    """
    from .models import User
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "Пользователь не найден"

    verification_url = f"{settings.SITE_URL}/api/users/verify-email/?token={verification_code}"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Подтверждение аккаунта</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4A90E2; color: white; padding: 15px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .button {{ display: inline-block; padding: 10px 20px; background-color: #4A90E2; 
                    color: white; text-decoration: none; border-radius: 5px; }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #777; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Благотворительный аукцион</h1>
            </div>
            <div class="content">
                <h2>Здравствуйте, {user.first_name or 'Пользователь'}!</h2>
                <p>Благодарим вас за регистрацию на нашем благотворительном аукционе.</p>
                <p>Для подтверждения вашего аккаунта, пожалуйста, нажмите на кнопку ниже:</p>
                <p style="text-align: center;">
                    <a class="button" href="{verification_url}">Подтвердить аккаунт</a>
                </p>
                <p>Если кнопка не работает, вы можете скопировать и вставить следующую ссылку в адресную строку браузера:</p>
                <p style="word-break: break-all;">{verification_url}</p>
                <p>Ссылка действительна в течение 24 часов.</p>
                <p>Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.</p>
            </div>
            <div class="footer">
                <p>С уважением, команда благотворительного аукциона</p>
                <p>&copy; {settings.COPYRIGHT_YEAR if hasattr(settings, 'COPYRIGHT_YEAR') else '2025'} Благотворительный аукцион. Все права защищены.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = f"""
    Здравствуйте, {user.first_name or 'Пользователь'}!
    
    Благодарим вас за регистрацию на нашем благотворительном аукционе.
    
    Для подтверждения вашего аккаунта пройдите по следующей ссылке:
    {verification_url}
    
    Ссылка действительна в течение 24 часов.
    
    Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.
    
    С уважением,
    Команда благотворительного аукциона
    """
    
    subject = "Подтверждение вашего аккаунта"

    send_mailgun_email(subject, plain_message, html_message, user.email)
    
    return f"Письмо с подтверждением отправлено на {user.email}"


@shared_task
def send_notification_email(user_id, subject, message):
    """
    Задача для отправки уведомлений пользователям
    """
    from .models import User
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "Пользователь не найден"
    
    send_mailgun_email(subject, message, message, user.email)
    
    return f"Уведомление отправлено на {user.email}"


def send_mailgun_email(subject, text, html, to_email):
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
            auth=("api", settings.MAILGUN_API_KEY),
            data={
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "text": text,
                "html": html,
            },
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"Mailgun: письмо успешно отправлено на {to_email}. Ответ: {response.text}")
        return response.text
    except Exception as e:
        logging.error(f"Mailgun: ошибка при отправке письма на {to_email}: {e}. Ответ: {getattr(e, 'response', None)}")
        return f"Ошибка отправки письма: {e}";
