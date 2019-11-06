# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0008_auto_20191028_0159'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseorg',
            name='org_body',
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseorg',
            name='org_image',
            field=models.ImageField(default=b'images/azure_logo.png', null=True, upload_to=b'org_logo', blank=True),
        ),
    ]
