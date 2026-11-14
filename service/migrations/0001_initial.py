import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('username', models.CharField(blank=True, help_text='Введите ФИО', max_length=150, null=True, verbose_name='Ф.И.О.')),
                ('comment', models.TextField(blank=True, help_text='Ваш комментарий', max_length=255, null=True, verbose_name='Комментарий')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(blank=True, help_text='Пожалуйста, введите тему сообщения', max_length=150, null=True, verbose_name='Тема письма')),
                ('text', models.TextField(blank=True, help_text='Пожалуйста, введите текст Вашего сообщения', max_length=255, null=True, verbose_name='Тело письма')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(verbose_name='Дата и время начала отправки')),
                ('end_time', models.DateTimeField(verbose_name='Дата и время окончания отправки')),
                ('status', models.CharField(choices=[('Создана', 'Создана'), ('Запущена', 'Запущена'), ('Завершена', 'Завершена')], default='Создана', max_length=10, verbose_name='Статус')),
                ('recipients', models.ManyToManyField(to='service.client', verbose_name='Получатели')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.message', verbose_name='Сообщение')),
            ],
            options={
                'verbose_name': 'Рассылка',
                'verbose_name_plural': 'Рассылки',
            },
        ),
    ]
