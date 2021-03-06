# Generated by Django 2.0.1 on 2020-09-14 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0049_auto_20200911_1554'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='diagnostictestchoice',
            options={'verbose_name': 'Choice', 'verbose_name_plural': 'Choices'},
        ),
        migrations.AlterModelOptions(
            name='diagnostictestquestion',
            options={'ordering': ['order'], 'verbose_name': 'Question', 'verbose_name_plural': 'Questions'},
        ),
        migrations.AlterModelOptions(
            name='diagnostictestquiz',
            options={},
        ),
        migrations.RemoveField(
            model_name='course',
            name='diagnostic_test_quiz',
        ),
        migrations.AddField(
            model_name='course',
            name='diagnostic_test_quiz',
            field=models.ForeignKey(default=1000000, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='group_courses.DiagnosticTestQuiz'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='diagnostictestquestion',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
