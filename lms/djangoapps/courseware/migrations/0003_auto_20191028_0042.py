# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0002_coursesection_coursesectioncourse'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesection',
            name='image',
            field=models.ImageField(default=b'', null=True, upload_to=b'', blank=True),
        ),
        migrations.AddField(
            model_name='coursesection',
            name='org_name',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
