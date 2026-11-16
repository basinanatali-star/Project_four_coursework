from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.conf import settings


class Client(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )

    username = models.CharField(
        max_length=150,
        verbose_name="Ф.И.О.",
        blank=True,
        null=True,
        help_text="Введите ФИО",
    )

    comment = models.TextField(
        max_length=255,
        verbose_name="Комментарий",
        blank=True,
        null=True,
        help_text="Ваш комментарий",
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.email


class Message(models.Model):
    topic = models.CharField(max_length=150, verbose_name='Тема письма', blank=True, null=True,
                             help_text="Пожалуйста, введите тему сообщения")
    text = models.TextField(max_length=255, verbose_name="Тело письма", blank=True, null=True,
                            help_text="Пожалуйста, введите текст Вашего сообщения")

    def __str__(self):
        return f" {self.topic}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    STATUS_CHOICES = [
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
        ("Завершена", "Завершена"),
        ("Отключена", "Отключена"),
    ]

    start_time = models.DateTimeField(
        verbose_name="Дата и время начала отправки"
    )

    end_time = models.DateTimeField(
        verbose_name="Дата и время окончания отправки"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Создана",
        verbose_name="Статус",
    )

    message = models.ForeignKey(
        "service.Message",
        on_delete=models.CASCADE,
        verbose_name="Сообщение",
    )

    recipients = models.ManyToManyField(
        "service.Client",
        verbose_name="Получатели",
    )

    def clean(self):
        super().clean()

        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError({
                    "end_time": "Дата окончания должна быть позже даты начала."
                })

        if self.start_time and self.start_time < timezone.now():
            raise ValidationError({
                "start_time": "Дата начала не может быть в прошлом."
            })

    @property
    def current_status(self):
        """Возвращает актуальный статус рассылки."""

        if self.status == "Отключена":
            return "Отключена"

        now = timezone.now()

        if now < self.start_time:
            return "Создана"
        elif now <= self.end_time:
            return "Запущена"
        else:
            return "Завершена"

    def update_status(self):
        """Сохраняет актуальный статус в базе данных."""
        if self.status == "Отключена":
            return

        new_status = self.current_status

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    def __str__(self):
        return f"Рассылка №{self.pk} — {self.current_status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("Успешно", "Успешно"),
        ("Не успешно", "Не успешно"),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="mailing_attempts",
        verbose_name="Получатель",
    )

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время попытки",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Статус отправки",
    )

    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ответ почтового сервера",
    )

    def __str__(self):
        return (
            f"Рассылка №{self.mailing.pk} — "
            f"{self.client.email} — {self.status}"
        )

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"