# Generated by Django 3.2.4 on 2021-09-07 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tesla_ce', '0018_assessmentsession_auto_closed'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='allow_learner_audit',
            field=models.BooleanField(default=False, help_text='Learners can access the audit data of their reports', null=None),
        ),
        migrations.AddField(
            model_name='institution',
            name='allow_learner_report',
            field=models.BooleanField(default=False, help_text='Learners can access their reports', null=None),
        ),
        migrations.AddField(
            model_name='institution',
            name='allow_valid_audit',
            field=models.BooleanField(default=False, help_text='Audit data is available even when results are valid', null=None),
        ),
        migrations.AddField(
            model_name='reportactivityinstrument',
            name='audit_data',
            field=models.FileField(help_text='Path to the audit data.', max_length=250, null=True, upload_to=''),
        ),
    ]
