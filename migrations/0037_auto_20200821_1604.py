# Generated by Django 2.0.1 on 2020-08-21 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0036_auto_20200821_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='is_adaptive',
            field=models.BooleanField(default=False, verbose_name='Adaptive Course'),
        ),
    ]
