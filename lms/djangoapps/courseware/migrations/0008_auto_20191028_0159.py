# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0007_auto_20191028_0121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseorg',
            name='org_image',
            field=models.ImageField(default=b'images/azure_logo.png', null=True, upload_to=b'uploads', blank=True),
        ),
    ]
