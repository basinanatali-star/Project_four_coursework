
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from service.models import MailingAttempt


def send_mailing(mailing):
    """
    Отправляет письма всем получателям рассылки
    и сохраняет результат каждой попытки.
    """
    if mailing.status == "Отключена":
        raise ValueError("Нельзя отправить отключённую рассылку.")

    # Получаем текущее время
    now = timezone.now()

    # Проверяем разрешённый период отправки
    if not (mailing.start_time <= now <= mailing.end_time):
        raise ValueError(
            "Нельзя отправить рассылку. "
            "Текущее время находится за пределами "
            "разрешённого периода отправки."
        )

    # Получаем сообщение рассылки
    message = mailing.message

    # Получаем всех получателей
    recipients = mailing.recipients.all()

    results = []

    # Отправляем письмо каждому получателю
    for client in recipients:
        try:
            sent = send_mail(
                subject=message.topic,
                message=message.text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )

            if sent == 1:
                status = "Успешно"
                response = "Письмо принято почтовой системой."
            else:
                status = "Не успешно"
                response = "Письмо не было отправлено."

        except Exception as error:
            status = "Не успешно"
            response = str(error)

        # Сохраняем результат попытки
        MailingAttempt.objects.create(
            mailing=mailing,
            client=client,
            status=status,
            server_response=response,
        )

        results.append({
            "client": client,
            "status": status,
            "response": response,
        })

    return results
