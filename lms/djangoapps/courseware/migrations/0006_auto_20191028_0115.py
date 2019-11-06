# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0005_auto_20191028_0104'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseorg',
            old_name='image',
            new_name='org_image',
        ),
        migrations.AddField(
            model_name='courseorg',
            name='org_code',
            field=models.CharField(default=1, unique=True, max_length=20, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='courseorg',
            name='org_name',
            field=models.CharField(default=1, unique=True, max_length=20, db_index=True),
            preserve_default=False,
        ),
    ]
