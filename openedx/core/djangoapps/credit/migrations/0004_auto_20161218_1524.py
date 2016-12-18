# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0003_auto_20160511_2227'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='creditrequirementstatus',
            options={'verbose_name_plural': '\ud544\uc218 \ud06c\ub808\ub527 \uc0c1\ud0dc'},
        ),
        migrations.AlterField(
            model_name='creditconfig',
            name='cache_ttl',
            field=models.PositiveIntegerField(default=0, help_text=b'\xec\xb4\x88\xeb\xa1\x9c \xed\x91\x9c\xec\x8b\x9c\xeb\x90\xa9\xeb\x8b\x88\xeb\x8b\xa4. \xec\x9d\xb4 \xea\xb0\x92\xec\x9d\x84 0 \xec\x9d\xb4\xec\x83\x81\xec\x9d\x98 \xec\x88\xab\xec\x9e\x90\xeb\xa1\x9c \xec\x84\xa4\xec\xa0\x95\xed\x95\xb4 \xec\xba\x90\xec\x8b\x9c\xeb\xa5\xbc \xed\x97\x88\xec\x9a\xa9\xed\x95\xa9\xeb\x8b\x88\xeb\x8b\xa4.', verbose_name=b'\xec\x8b\xa4\xec\x8b\x9c\xea\xb0\x84 \xec\xba\x90\xec\x8b\x9c \xec\x8b\x9c\xea\xb0\x84'),
        ),
    ]
