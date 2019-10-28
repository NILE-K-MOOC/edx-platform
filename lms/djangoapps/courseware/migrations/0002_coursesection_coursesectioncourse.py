# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section_name', models.CharField(unique=True, max_length=100, db_index=True)),
                ('order_no', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'course_sections_coursesesion',
            },
        ),
        migrations.CreateModel(
            name='CourseSectionCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(unique=True, max_length=255, db_index=True)),
                ('section', models.ForeignKey(to='courseware.CourseSection')),
            ],
            options={
                'db_table': 'course_sections_coursesesion_course',
            },
        ),
    ]
