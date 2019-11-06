# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0009_auto_20191028_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesection',
            name='section_logo_large',
            field=models.ImageField(default=b'images/circle.png', null=True, upload_to=b'section_logo', blank=True),
        ),
        migrations.AddField(
            model_name='coursesection',
            name='section_logo_small',
            field=models.ImageField(default=b'images/circle.png', null=True, upload_to=b'section_logo', blank=True),
        ),
    ]
