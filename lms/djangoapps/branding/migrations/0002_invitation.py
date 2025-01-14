# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2021-12-23 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('branding', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('username', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('job', models.CharField(max_length=100)),
                ('purpose', models.CharField(max_length=150)),
                ('agree', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
