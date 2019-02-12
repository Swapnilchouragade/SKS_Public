# Generated by Django 2.0 on 2019-02-06 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0035_auto_20190206_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expert',
            name='Department',
            field=models.CharField(choices=[('management', 'MANAGEMENT'), ('engineering', 'ENGINEERING'), ('pharamacy', 'PHARAMACY'), ('other', 'OTHER')], default='other', max_length=100),
        ),
    ]