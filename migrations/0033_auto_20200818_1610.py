# Generated by Django 2.0.1 on 2020-08-18 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0032_auto_20200817_1443'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupanswer',
            options={'verbose_name_plural': 'Quiz Answers'},
        ),
        migrations.AlterModelOptions(
            name='groupcategory',
            options={'verbose_name_plural': 'Courses Categories'},
        ),
        migrations.AlterModelOptions(
            name='lecture',
            options={'verbose_name_plural': 'Course Lectures'},
        ),
        migrations.AlterModelOptions(
            name='material',
            options={'verbose_name_plural': 'Course Materials'},
        ),
        migrations.AlterModelOptions(
            name='rating',
            options={'verbose_name_plural': 'Course Ratings'},
        ),
    ]