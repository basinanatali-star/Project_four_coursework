import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailingAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempt_time', models.DateTimeField(auto_now_add=True, verbose_name='Время попытки')),
                ('status', models.CharField(choices=[('Успешно', 'Успешно'), ('Не успешно', 'Не успешно')], max_length=20, verbose_name='Статус отправки')),
                ('server_response', models.TextField(blank=True, null=True, verbose_name='Ответ почтового сервера')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mailing_attempts', to='service.client', verbose_name='Получатель')),
                ('mailing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='service.mailing', verbose_name='Рассылка')),
            ],
            options={
                'verbose_name': 'Попытка отправки',
                'verbose_name_plural': 'Попытки отправки',
            },
        ),
    ]
