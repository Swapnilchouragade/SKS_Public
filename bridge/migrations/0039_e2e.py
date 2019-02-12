# Generated by Django 2.0 on 2019-02-08 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0038_auto_20190206_2106'),
    ]

    operations = [
        migrations.CreateModel(
            name='E2E',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expert_get', models.IntegerField()),
                ('is_connect_request', models.BooleanField(default=False)),
                ('is_connect', models.BooleanField(default=False)),
                ('expert_sent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bridge.Expert')),
            ],
        ),
    ]
