# Generated by Django 2.0.1 on 2020-09-10 05:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0040_auto_20200909_1927'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='diagnostictestanswer',
            options={'verbose_name_plural': 'Test Answers'},
        ),
        migrations.RenameField(
            model_name='diagnostictestchoice',
            old_name='quiz_question',
            new_name='test_question',
        ),
    ]