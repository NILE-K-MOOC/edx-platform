# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0004_coursesection_org_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseOrg',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('org_name', models.CharField(max_length=20, null=True, blank=True)),
                ('image', models.ImageField(default=b'images/azure_logo.png', null=True, upload_to=b'', blank=True)),
            ],
            options={
                'db_table': 'course_org_courseorg',
            },
        ),
        migrations.RemoveField(
            model_name='coursesection',
            name='image',
        ),
        migrations.RemoveField(
            model_name='coursesection',
            name='org_id',
        ),
        migrations.RemoveField(
            model_name='coursesection',
            name='org_name',
        ),
        migrations.AddField(
            model_name='coursesection',
            name='org',
            field=models.ForeignKey(to='courseware.CourseOrg', null=True),
        ),
    ]
