# Generated by Django 3.2.4 on 2021-07-09 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tesla_ce', '0015_uioption_roles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityinstrument',
            name='required',
        ),
        migrations.RemoveField(
            model_name='enrolmentsamplevalidation',
            name='included',
        ),
        migrations.AlterUniqueTogether(
            name='requestproviderresult',
            unique_together={('provider', 'request')},
        ),
    ]
