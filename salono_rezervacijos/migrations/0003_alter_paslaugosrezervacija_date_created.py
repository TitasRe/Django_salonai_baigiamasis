# Generated by Django 4.1.1 on 2023-05-03 09:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salono_rezervacijos', '0002_alter_paslaugosrezervacija_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paslaugosrezervacija',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 3, 12, 46, 23, 251286, tzinfo=datetime.timezone.utc)),
        ),
    ]
