# Generated by Django 2.0.1 on 2020-09-09 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0039_auto_20200904_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='description',
            field=models.TextField(null=True),
        ),
    ]