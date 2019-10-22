# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='detail_url',
            field=models.TextField(default=b'', null=True),
        ),
        migrations.AddField(
            model_name='notice',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='notice',
            name='is_display',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notice',
            name='is_popup',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notice',
            name='start_date',
            field=models.DateTimeField(null=True),
        ),
    ]
