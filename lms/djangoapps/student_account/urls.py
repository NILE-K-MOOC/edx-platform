from django.conf import settings
from django.conf.urls import url

from student_account import views

urlpatterns = [
    url(r'^finish_auth$', views.finish_auth, name='finish_auth'),
    url(r'^settings$', views.account_settings, name='account_settings'),
]

if settings.FEATURES.get('ENABLE_COMBINED_LOGIN_REGISTRATION'):
    urlpatterns += [
        url(r'^password$', views.password_change_request_handler, name='password_change_request'),
        url(r'^settings_confirm$', views.account_settings_confirm, name='account_settings_confirm'),
        url(r'^settings_confirm_check$', views.account_settings_confirm_check, name='account_settings_confirm_check'),
        url(r'^account_settings2_confirm_check$', views.account_settings2_confirm_check,
            name='account_settings2_confirm_check'),
    ]
