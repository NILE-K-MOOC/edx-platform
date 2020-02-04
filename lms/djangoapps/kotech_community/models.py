# -*- coding: utf-8 -*-
from django.db import models
import logging

log = logging.getLogger(__name__)


class TbBoard(models.Model):
    board_id = models.AutoField(primary_key=True)
    head_title = models.CharField(max_length=50, blank=True, null=True)
    subject = models.TextField()
    content = models.TextField(blank=True, null=True)
    reg_date = models.DateTimeField()
    mod_date = models.DateTimeField()
    # section
    # N : notice, F: faq, K: k-mooc news, R: reference
    section = models.CharField(max_length=10)
    use_yn = models.CharField(max_length=1)
    odby = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_board'
        app_label = 'kotech_community'

    def __init__(self):
        log.info('TbBoard init [%s]' % __name__)


class TbAttach(models.Model):
    group_name = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.CharField(max_length=255, blank=True, null=True)
    real_name = models.CharField(max_length=255, blank=True, null=True)
    save_name = models.CharField(max_length=255, blank=True, null=True)
    ext = models.CharField(max_length=10, blank=True, null=True)
    real_size = models.IntegerField(blank=True, null=True)
    save_size = models.CharField(max_length=255, blank=True, null=True)
    save_path = models.CharField(max_length=255, blank=True, null=True)
    use_yn = models.IntegerField(default=True)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    delete_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_attach'
        app_label = 'kotech_community'


class TbBoardAttach(models.Model):
    attatch_id = models.AutoField(primary_key=True)
    # board_id = models.ForeignKey('TbBoard', on_delete=models.CASCADE, related_name='attaches', null=True)
    board_id = models.IntegerField(11)
    attach_file_path = models.CharField(max_length=255)
    attatch_file_name = models.CharField(max_length=255)
    attach_org_name = models.CharField(max_length=255, blank=True, null=True)
    attatch_file_ext = models.CharField(max_length=50, blank=True, null=True)
    attatch_file_size = models.CharField(max_length=50, blank=True, null=True)
    attach_gubun = models.CharField(max_length=20, blank=True, null=True)
    del_yn = models.CharField(max_length=1)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_board_attach'
        app_label = 'kotech_community'
