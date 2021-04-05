# Generated by Django 2.0.1 on 2020-09-23 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0055_studentscore'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentscore',
            options={'verbose_name_plural': 'Students Scores'},
        ),
        migrations.AlterField(
            model_name='assessment',
            name='total_score',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]
