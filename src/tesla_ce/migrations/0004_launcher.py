# Generated by Django 3.0.6 on 2020-05-20 13:36

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('tesla_ce', '0003_providernotification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Launcher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target', models.IntegerField(choices=[(0, 'Dashboard'), (1, 'LAPI')], default=0, help_text='Target for this launcher')),
                ('target_url', models.CharField(default=None, help_text='Url to redirect', max_length=250, null=True)),
                ('token', models.UUIDField(help_text='Token to allow authentication for this user')),
                ('token_pair', models.TextField(help_text='Pair of tokens to authenticate with target')),
                ('expires_at', models.DateTimeField(help_text='When this access token expires')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(default=None, help_text='Related assessment session', null=True, on_delete=django.db.models.deletion.SET_NULL, to='tesla_ce.AssessmentSession')),
                ('user', models.ForeignKey(help_text='Related user', on_delete=django.db.models.deletion.CASCADE, to='tesla_ce.InstitutionUser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
