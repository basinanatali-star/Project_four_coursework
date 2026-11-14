from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    username = models.CharField(max_length=150, verbose_name='Ф.И.О.',
                                blank=True, null=True, help_text="Введите ФИО")
    comment = models.TextField(max_length=255, verbose_name="Комментарий",
                               blank=True, null=True, help_text="Ваш комментарий")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.email

class Message(models.Model):
    topic = models.CharField(max_length=150, verbose_name='Тема письма',
                             blank=True, null=True, help_text="Пожалуйста, введите тему сообщения")
    text = models.TextField(max_length=255, verbose_name="Тело письма",
                            blank=True, null=True, help_text="Пожалуйста, введите текст Вашего сообщения")

    def __str__(self):
        return f" {self.topic}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
        ("Завершена", "Завершена"),
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
                    "end_time": (
                        "Дата окончания должна быть позже даты начала."
                    )
                })

        if self.start_time and self.start_time < timezone.now():
            raise ValidationError({
                "start_time": "Дата начала не может быть в прошлом."
            })

    def update_status(self):
        now = timezone.now()

        if now < self.start_time:
            new_status = "Создана"
        elif now <= self.end_time:
            new_status = "Запущена"
        else:
            new_status = "Завершена"

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    def __str__(self):
        return f"Рассылка №{self.pk} — {self.status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"