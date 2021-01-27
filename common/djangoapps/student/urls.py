# -*- coding: utf-8 -*-
"""
URLs for student app
"""

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import password_reset_complete

from . import views

urlpatterns = [
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),

    # TODO: standardize login

    # 강좌 설정 > 난이도
    url(r'^modi_course_level', views.modi_course_level, name='modi_course_level'),

    # 강좌 설정 > 교수자명
    url(r'^modi_teacher_name', views.modi_teacher_name, name='modi_teacher_name'),

    # 강좌 설정 > 강좌 미리보기
    url(r'^modi_preview_video', views.modi_preview_video, name='modi_preview_video'),

    # 강좌 설정 > 강좌자막언어
    url(r'^modi_course_language', views.modi_course_language, name='modi_course_language'),

    # 강좌 설정 > 강좌자막언어
    url(r'^modi_subtitle', views.modi_subtitle, name='modi_subtitle'),

    # 학습인정시간 파일 다운로드
    url(r'^guide_download', views.guide_download, name='guide_download'),

    # login endpoint used by cms.
    url(r'^login_post$', views.login_user, name='login_post'),
    # login endpoints used by lms.
    url(r'^login_ajax$', views.login_user, name="login"),
    url(r'^login_ajax/(?P<error>[^/]*)$', views.login_user),

    url(r'^email_confirm/(?P<key>[^/]*)$', views.confirm_email_change, name='confirm_email_change'),

    url(r'^create_account$', views.create_account, name='create_account'),
    url(r'^activate/(?P<key>[^/]*)$', views.activate_account, name="activate"),

    url(r'^accounts/disable_account_ajax$', views.disable_account_ajax, name="disable_account_ajax"),
    url(r'^accounts/manage_user_standing', views.manage_user_standing, name='manage_user_standing'),

    url(r'^change_setting$', views.change_setting, name='change_setting'),
    url(r'^change_email_settings$', views.change_email_settings, name='change_email_settings'),

    # password reset in views (see below for password reset django views)
    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(
        r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        views.password_reset_confirm_wrapper,
        name='password_reset_confirm',
    ),

    url(r'accounts/verify_password', views.verify_user_password, name='verify_password'),

    url(r'^course_run/{}/refund_status$'.format(settings.COURSE_ID_PATTERN),
        views.course_run_refund_status,
        name="course_run_refund_status"),
]

# enable automatic login
if settings.FEATURES.get('AUTOMATIC_AUTH_FOR_TESTING'):
    urlpatterns += [
        url(r'^auto_auth$', views.auto_auth),
    ]

# password reset django views (see above for password reset views)
urlpatterns += [
    # TODO: Replace with Mako-ized views
    url(
        r'^password_reset_complete/$',
        password_reset_complete,
        name='password_reset_complete',
    ),
]
