# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0006_auto_20191028_0115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesection',
            name='org',
            field=models.ForeignKey(blank=True, to='courseware.CourseOrg', null=True),
        ),
    ]
