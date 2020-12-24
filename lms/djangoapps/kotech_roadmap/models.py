# -*- coding: utf-8 -*-
from django.db import models
import logging

log = logging.getLogger(__name__)

class TbAi(models.Model):
    ai_id = models.CharField(unique=True, max_length=11)
    target = models.CharField(max_length=100, blank=True, null=True)
    basic_knowledge = models.CharField(max_length=30, blank=True, null=True)
    purpose_of_course = models.CharField(max_length=100, blank=True, null=True)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True)
    use_yn = models.CharField(max_length=1, blank=True, null=True)
    modify_id = models.IntegerField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_ai'
        app_label = 'kotech_roadmap'


class TbAiEdge(models.Model):
    from_node = models.IntegerField(blank=True, null=True)
    to_node = models.IntegerField(blank=True, null=True)
    opacity = models.CharField(max_length=4, blank=True, null=True)
    ai_id = models.CharField(max_length=10, blank=True, null=True)
    use_yn = models.CharField(max_length=1, blank=True, null=True)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True)
    modify_id = models.IntegerField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_ai_edge'
        app_label = 'kotech_roadmap'


class TbAiLink(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=300, blank=True, null=True)
    node_id = models.IntegerField(blank=True, null=True)
    ai_id = models.CharField(max_length=10, blank=True, null=True)
    link_type = models.CharField(max_length=1, blank=True, null=True)
    use_yn = models.CharField(max_length=1, blank=True, null=True)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True)
    modify_id = models.IntegerField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_ai_link'
        app_label = 'kotech_roadmap'


class TbAiNode(models.Model):
    label = models.CharField(max_length=500, blank=True, null=True)
    shape = models.CharField(max_length=10, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=8, blank=True, null=True)
    ai_id = models.CharField(max_length=10, blank=True, null=True)
    node_id = models.IntegerField(blank=True, null=True)
    use_yn = models.CharField(max_length=1, blank=True, null=True)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True)
    modify_id = models.IntegerField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_ai_node'
        app_label = 'kotech_roadmap'