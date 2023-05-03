# Generated by Django 4.1.1 on 2023-04-27 19:21

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Paslauga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Pavadinimas')),
                ('summary', models.TextField(help_text='Paslaugos aprašymas', max_length=1000, verbose_name='Aprašymas')),
                ('kaina', models.CharField(max_length=10, verbose_name='Paslaugu kaina')),
                ('cover', models.ImageField(null=True, upload_to='covers', verbose_name='Virselis')),
            ],
            options={
                'verbose_name': 'Paslauga',
                'verbose_name_plural': 'Paslaugos',
            },
        ),
        migrations.CreateModel(
            name='Salonas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pavadinimas', models.CharField(max_length=255)),
                ('miestas', models.CharField(blank=True, max_length=255)),
                ('adresas', models.CharField(max_length=255)),
                ('description', tinymce.models.HTMLField(default='Salonas description')),
                ('cover', models.ImageField(null=True, upload_to='covers', verbose_name='Virselis')),
            ],
            options={
                'verbose_name': 'Salonas',
                'verbose_name_plural': 'Salonai',
            },
        ),
        migrations.CreateModel(
            name='Specialistas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vardas', models.CharField(max_length=255)),
                ('pavarde', models.CharField(max_length=255)),
                ('patirtis', models.IntegerField()),
                ('description', tinymce.models.HTMLField(default='Apie specialista')),
                ('cover', models.ImageField(null=True, upload_to='covers', verbose_name='Specialisto nuotrauka')),
                ('klientas', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('paslaugos_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='specialistas_rn', to='salono_rezervacijos.paslauga')),
            ],
            options={
                'verbose_name': 'Specialistas',
                'verbose_name_plural': 'Specialistai',
            },
        ),
        migrations.CreateModel(
            name='SpecialistoReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField(max_length=1000, verbose_name='Atsiliepimas')),
                ('klientas', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('specialistas_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='salono_rezervacijos.specialistas')),
            ],
            options={
                'verbose_name': 'Atsiliepimas',
                'verbose_name_plural': 'Atsiliepimai',
                'ordering': ['date_created'],
            },
        ),
        migrations.CreateModel(
            name='Profilis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nuotrauka', models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaslaugosRezervacija',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=datetime.datetime(2023, 4, 27, 22, 21, 43, 205923, tzinfo=datetime.timezone.utc))),
                ('laikas_nuo', models.DateTimeField(blank=True, null=True, verbose_name='Laikas nuo')),
                ('laikas_iki', models.DateTimeField(blank=True, null=True, verbose_name='Laikas iki')),
                ('klientas', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('paslaugos_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='salono_rezervacijos.paslauga')),
                ('specialistas_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spec_paslaugos_rez_rn', to='salono_rezervacijos.specialistas')),
            ],
            options={
                'verbose_name': 'Rezervacija',
                'verbose_name_plural': 'Rezervacijos',
                'ordering': ['date_created'],
            },
        ),
        migrations.AddField(
            model_name='paslauga',
            name='salono_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paslauga_rn', to='salono_rezervacijos.salonas'),
        ),
    ]