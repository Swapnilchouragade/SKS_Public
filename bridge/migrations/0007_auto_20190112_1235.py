# Generated by Django 2.0 on 2019-01-12 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0006_auto_20190112_1233'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expert',
            old_name='CompanyName',
            new_name='Company_Name',
        ),
    ]
