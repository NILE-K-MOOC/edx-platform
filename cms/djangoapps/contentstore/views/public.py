"""
Public views
"""
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.clickjacking import xframe_options_deny
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.conf import settings

from edxmako.shortcuts import render_to_response

from openedx.core.djangoapps.external_auth.views import (
    ssl_login_shortcut,
    ssl_get_cert_from_request,
    redirect_with_get,
)
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from django.utils.http import urlencode
from django.http import HttpResponseRedirect, HttpResponse

import logging
import urllib
import json
log = logging.getLogger(__name__)

__all__ = ['signup', 'login_page', 'howitworks', 'newlogin_page']

@ensure_csrf_cookie
@xframe_options_deny
def signup(request):
    """
    Display the signup form.
    """
    csrf_token = csrf(request)['csrf_token']
    if request.user.is_authenticated():
        return redirect('/course/')
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES_IMMEDIATE_SIGNUP'):
        # Redirect to course to login to process their certificate if SSL is enabled
        # and registration is disabled.
        return redirect_with_get('login', request.GET, False)

    return render_to_response('register.html', {'csrf': csrf_token})

###########################################
@ssl_login_shortcut
@ensure_csrf_cookie
@xframe_options_deny
def newlogin_page(request):
    """
    Display the login form.
    """
    csrf_token = csrf(request)['csrf_token']
    if (settings.FEATURES['AUTH_USE_CERTIFICATES'] and
            ssl_get_cert_from_request(request)):
        # SSL login doesn't require a login view, so redirect
        # to course now that the user is authenticated via
        # the decorator.
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect('/course/')
    #if settings.FEATURES.get('AUTH_USE_CAS'):
        # If CAS is enabled, redirect auth handling to there
        #return redirect(reverse('cas-login'))


    return render_to_response(
        'login.html',
        {
            'csrf': csrf_token,
            'forgot_password_link': "//{base}/login#forgot-password-modal".format(base=settings.LMS_BASE),
            'platform_name': configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME),
        }
    )
###########################################

@ssl_login_shortcut
@ensure_csrf_cookie
@xframe_options_deny
def login_page(request):
    """
    Display the login form.
    """
    csrf_token = csrf(request)['csrf_token']
    if (settings.FEATURES['AUTH_USE_CERTIFICATES'] and
            ssl_get_cert_from_request(request)):
        # SSL login doesn't require a login view, so redirect
        # to course now that the user is authenticated via
        # the decorator.
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect('/course/')

    #================ LGE SSO CHECK ================#
    use_lgesso = request.COOKIES.get('LNETID')
    log.info("####### cookie check")
    log.info(use_lgesso)

    #1
    try:
        url_string1 = "http://10.185.219.196:8180/api/auth/limelogin.do?key=3q5e7a8d9f4q5as65f4g7&jjsessionid=" + str(use_lgesso)
        html = urllib.urlopen(url_string1)
        json_data = html.read()
        data = json.loads(json_data)
        code_data = data['result']
        code1 = code_data['code']
        log.info("####### code1")
        log.info(code1)
    except BaseException:
        log.info("####### code1 exception")
        code1 = 'error'
    #2
    try:
        url_string2 = "http://10.185.219.29:8180/api/auth/limelogin.do?key=3q5e7a8d9f4q5as65f4g7&jjsessionid=" + str(use_lgesso)
        html = urllib.urlopen(url_string2)
        json_data = html.read()
        data = json.loads(json_data)
        code_data = data['result']
        code2 = code_data['code']
        log.info("####### code2")
        log.info(code2)
    except BaseException:
        log.info("####### code2 exception")
        code2 = 'error'

    if settings.FEATURES.get('AUTH_USE_CAS'):
        ext_auth_response = urlencode({'next': request.GET.get('next', None)})
    ext_auth_response = str(ext_auth_response)
    ext_next = '?' + ext_auth_response
    re_url = 'http://studiolearning.lge.com/newsignin'
    full_url = re_url + ext_next
    log.info("*****************")
    log.info(full_url)

    if code1 == 'error' and code2 == 'error' :
        return redirect(full_url)
    #================ LGE SSO CHECK ================#

    if settings.FEATURES.get('AUTH_USE_CAS'):
        redirect_to = urlencode({'next': request.GET.get('next', None)})
        return redirect(reverse('cas-login')+'?'+redirect_to)

    return render_to_response(
        'login.html',
        {
            'csrf': csrf_token,
            'forgot_password_link': "//{base}/login#forgot-password-modal".format(base=settings.LMS_BASE),
            'platform_name': configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME),
        }
    )


def howitworks(request):
    "Proxy view"
    if request.user.is_authenticated():
        return redirect('/home/')
    else:
        return render_to_response('howitworks.html', {})
