# Generated by Django 2.0.1 on 2020-09-22 15:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0053_remove_assessment_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Assessment Description'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='duration',
            field=models.IntegerField(help_text='Minutes', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='course',
            name='status',
            field=models.CharField(choices=[('upcoming', 'Upcoming'), ('in progress', 'InProgress'), ('finished', 'Finished')], default='upcoming', max_length=20),
        ),
    ]
