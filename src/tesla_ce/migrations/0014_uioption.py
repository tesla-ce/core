# Generated by Django 3.2.4 on 2021-06-16 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tesla_ce', '0013_webhookclient_webhookmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='UIOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route', models.CharField(db_index=True, help_text='Affected Route.', max_length=250)),
                ('enabled', models.BooleanField(blank=None, default=False, help_text='Status', null=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('institution', models.ForeignKey(default=None, help_text='Affected institution', null=True, on_delete=django.db.models.deletion.CASCADE, to='tesla_ce.institution')),
                ('user', models.ForeignKey(default=None, help_text='Affected user', null=True, on_delete=django.db.models.deletion.CASCADE, to='tesla_ce.institutionuser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
