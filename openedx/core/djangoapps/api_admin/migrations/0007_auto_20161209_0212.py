# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_admin', '0006_catalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='status',
            field=models.CharField(default=b'pending', help_text='Status of this API access request', max_length=255, db_index=True, choices=[(b'pending', b'\xeb\x8c\x80\xea\xb8\xb0\xec\xa4\x91'), (b'denied', b'\xea\xb1\xb0\xec\xa0\x88\xeb\x90\xa8'), (b'approved', 'Approved')]),
        ),
        migrations.AlterField(
            model_name='historicalapiaccessrequest',
            name='status',
            field=models.CharField(default=b'pending', help_text='Status of this API access request', max_length=255, db_index=True, choices=[(b'pending', b'\xeb\x8c\x80\xea\xb8\xb0\xec\xa4\x91'), (b'denied', b'\xea\xb1\xb0\xec\xa0\x88\xeb\x90\xa8'), (b'approved', 'Approved')]),
        ),
    ]
