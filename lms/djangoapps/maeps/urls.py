# home/urls.py

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^MaSample$', views.MaSample, name='MaSample'),
    url(r'MaMakeCookie', views.MaMakeCookie, name='MaMakeCookie'),
    url(r'MaIePopup', views.MaIePopup, name='MaIePopup'),
    url(r'MaSetInstall', views.MaSetInstall, name='MaSetInstall'),
    url(r'MaSessionCheck', views.MaSessionCheck, name='MaSessionCheck'),
    url(r'Mafndown', views.Mafndown, name='Mafndown'),
    url(r'MaGetSession', views.MaGetSession, name='MaGetSession'),
    url(r'MaInstallPage', views.MaInstallPage, name='MaInstallPage'),
    url(r'certificate_print$', views.certificate_print, name='certificate_print'),
    url(r'special_certificate_print$', views.special_certificate_print, name='special_certificate_print'),
    url(r'series_print$', views.series_print, name='series_print'),
    url(r'servey_check$', views.servey_check, name='servey_check'),
]