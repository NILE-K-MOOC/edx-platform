# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('org', models.CharField(max_length=100, verbose_name=b'\xec\x86\x8c\xec\x86\x8d\xea\xb8\xb0\xea\xb4\x80')),
                ('type', models.CharField(blank=True, max_length=20, verbose_name=b'\xea\xb5\xac\xeb\xb6\x84', choices=[('\ub300\ud559\uc0dd', '\ub300\ud559\uc0dd'), ('\ub300\ud559\uc6d0\uc0dd', '\ub300\ud559\uc6d0\uc0dd'), ('\uad50\uc9c1\uc6d0', '\uad50\uc9c1\uc6d0'), ('\uad50\uc218', '\uad50\uc218'), ('\uc878\uc5c5\uc0dd', '\uc878\uc5c5\uc0dd'), ('\uae30\ud0c0', '\uae30\ud0c0')])),
                ('username_kor', models.CharField(max_length=50, verbose_name=b'\xed\x95\x9c\xea\xb8\x80\xeb\xaa\x85')),
                ('department', models.CharField(max_length=100, verbose_name=b'\xed\x95\x99\xea\xb3\xbc')),
                ('student_id', models.CharField(max_length=50, verbose_name=b'\xed\x95\x99\xeb\xb2\x88')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
