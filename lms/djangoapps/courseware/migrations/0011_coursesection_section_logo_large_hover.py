# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0010_auto_20191104_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesection',
            name='section_logo_large_hover',
            field=models.ImageField(default=b'images/circle.png', null=True, upload_to=b'section_logo', blank=True),
        ),
    ]
