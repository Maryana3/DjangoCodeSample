# Generated by Django 2.0.1 on 2020-08-09 15:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group_courses', '0025_auto_20200805_1715'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testcourse', to='group_courses.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='testcourse', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
