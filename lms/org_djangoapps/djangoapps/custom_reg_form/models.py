# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

# Backwards compatible settings.AUTH_USER_MODEL
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class ExtraInfo(models.Model):
    """
    This model contains two extra fields that will be saved when a user registers.
    The form that wraps this model is in the forms.py file.
    """
    user = models.OneToOneField(USER_MODEL, null=True)
    TYPE_CHOICES = (
        (u'대학생', u'대학생'),
        (u'대학원생', u'대학원생'),
        (u'교직원', u'교직원'),
        (u'교수', u'교수'),
        (u'졸업생', u'졸업생'),
        (u'기타', u'기타'),
    )

    org = models.CharField(
        verbose_name="소속기관",
        max_length=100,
    )
    type = models.CharField(
        verbose_name="구분",
        choices=TYPE_CHOICES,
        blank=True,
        max_length=20,
    )
    username_kor = models.CharField(
        verbose_name="한글명",
        max_length=50,
    )
    department = models.CharField(
        verbose_name="학과",
        max_length=100,
    )
    student_id = models.CharField(
        verbose_name="학번",
        max_length=50,
    )
