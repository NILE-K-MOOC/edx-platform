# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0003_auto_20191028_0042'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesection',
            name='org_id',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
