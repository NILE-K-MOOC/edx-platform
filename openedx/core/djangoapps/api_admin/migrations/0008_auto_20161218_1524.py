# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_admin', '0007_auto_20161209_0212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='reason',
            field=models.TextField(help_text=b'\xec\x82\xac\xec\x9a\xa9\xec\x9e\x90\xea\xb0\x80 API\xec\x97\x90 \xec\xa0\x91\xec\x86\x8d\xed\x95\x98\xea\xb3\xa0 \xec\x8b\xb6\xec\x96\xb4\xed\x95\x98\xeb\x8a\x94 \xec\x82\xac\xec\x9c\xa0.'),
        ),
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='status',
            field=models.CharField(default=b'pending', help_text=b'API \xec\xa0\x91\xec\x86\x8d \xec\x9a\x94\xec\xb2\xad \xec\x83\x81\xed\x83\x9c', max_length=255, db_index=True, choices=[(b'pending', b'\xeb\x8c\x80\xea\xb8\xb0\xec\xa4\x91'), (b'denied', b'\xea\xb1\xb0\xec\xa0\x88\xeb\x90\xa8'), (b'approved', b'\xec\x8a\xb9\xec\x9d\xb8 \xec\x99\x84\xeb\xa3\x8c')]),
        ),
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='website',
            field=models.URLField(help_text=b'\xec\x9d\xb4 API \xec\x82\xac\xec\x9a\xa9\xec\x9e\x90\xec\x99\x80 \xea\xb4\x80\xeb\xa0\xa8\xeb\x90\x9c \xec\x9b\xb9\xec\x82\xac\xec\x9d\xb4\xed\x8a\xb8 URL.'),
        ),
        migrations.AlterField(
            model_name='historicalapiaccessrequest',
            name='reason',
            field=models.TextField(help_text=b'\xec\x82\xac\xec\x9a\xa9\xec\x9e\x90\xea\xb0\x80 API\xec\x97\x90 \xec\xa0\x91\xec\x86\x8d\xed\x95\x98\xea\xb3\xa0 \xec\x8b\xb6\xec\x96\xb4\xed\x95\x98\xeb\x8a\x94 \xec\x82\xac\xec\x9c\xa0.'),
        ),
        migrations.AlterField(
            model_name='historicalapiaccessrequest',
            name='status',
            field=models.CharField(default=b'pending', help_text=b'API \xec\xa0\x91\xec\x86\x8d \xec\x9a\x94\xec\xb2\xad \xec\x83\x81\xed\x83\x9c', max_length=255, db_index=True, choices=[(b'pending', b'\xeb\x8c\x80\xea\xb8\xb0\xec\xa4\x91'), (b'denied', b'\xea\xb1\xb0\xec\xa0\x88\xeb\x90\xa8'), (b'approved', b'\xec\x8a\xb9\xec\x9d\xb8 \xec\x99\x84\xeb\xa3\x8c')]),
        ),
        migrations.AlterField(
            model_name='historicalapiaccessrequest',
            name='website',
            field=models.URLField(help_text=b'\xec\x9d\xb4 API \xec\x82\xac\xec\x9a\xa9\xec\x9e\x90\xec\x99\x80 \xea\xb4\x80\xeb\xa0\xa8\xeb\x90\x9c \xec\x9b\xb9\xec\x82\xac\xec\x9d\xb4\xed\x8a\xb8 URL.'),
        ),
    ]
