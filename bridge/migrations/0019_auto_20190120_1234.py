# Generated by Django 2.0 on 2019-01-20 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0018_auto_20190120_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='Profile_piture',
            field=models.FileField(blank=True, null=True, upload_to='static/profile_images/'),
        ),
    ]
