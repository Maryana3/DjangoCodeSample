# Generated by Django 2.0.1 on 2020-07-09 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group_courses', '0012_groupquiz'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupQuizQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('single', 'Single'), ('multiple', 'Multiple')], default='single', max_length=20)),
                ('enabled', models.BooleanField(default=True)),
                ('group_quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_questions', to='group_courses.GroupQuiz')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]