# -*- coding: utf-8 -*-
""" Views for a student's account information. """
import logging
import json
import urlparse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, resolve
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest
)
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django_countries import countries
from edxmako.shortcuts import render_to_response
import pytz
from commerce.models import CommerceConfiguration
from external_auth.login_and_register import (
    login as external_auth_login,
    register as external_auth_register
)
from lang_pref.api import released_languages, all_languages
from openedx.core.djangoapps.commerce.utils import ecommerce_api_client
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.theming.helpers import is_request_in_themed_site
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api.accounts.api import request_password_change
from openedx.core.djangoapps.user_api.errors import UserNotFound
from openedx.core.lib.time_zone_utils import TIME_ZONE_CHOICES
from openedx.core.lib.edx_api_utils import get_edx_api_data
from student.models import UserProfile
from student.views import (
    signin_user as old_login_view,
    register_user as old_register_view
)
from student.helpers import get_next_url_for_login_page
import third_party_auth
from third_party_auth import pipeline
from third_party_auth.decorators import xframe_allow_whitelisted
from util.bad_request_rate_limiter import BadRequestRateLimiter
from util.date_utils import strftime_localized
import commands
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from student.views import register_user
from django.contrib.auth import authenticate
from util.json_request import JsonResponse
import commands
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from student.views import register_user
from django.contrib.auth import authenticate
from util.json_request import JsonResponse
# import schedule
# import threading
# from crontab import CronTab
from social.apps.django_app.default.models import UserSocialAuth
from openedx.core.djangoapps.user_api.accounts.image_helpers import get_profile_image_names, set_has_profile_image
from openedx.core.djangoapps.profile_images.images import remove_profile_images
from openedx.core.djangoapps.user_api.preferences.api import update_user_preferences
from django.contrib.auth.models import User
import datetime
from django.contrib.auth import logout
from pymongo import MongoClient
from django.db import connections
import ast
import urllib

# def job():
#     print("I'm working...")
#
# def run_threaded(job_func):
#     job_thread = threading.Thread(target=job_func)
#     job_thread.start()
#
# schedule.every(1).seconds.do(run_threaded, job)
# # schedule.every(1).minutes.do(job)
# # schedule.every().hour.do(job)
# # schedule.every().day.at("10:30").do(job)
# while 1:
#
#     schedule.run_continuously()
#     time.sleep(1)


# users_cron = CronTab(user='edxapp')
# job  = users_cron.new(command='echo "hello"')
# job.minutes.every(1)
# job.enable()
#
AUDIT_LOG = logging.getLogger("audit")
log = logging.getLogger(__name__)

@require_http_methods(['GET'])
@ensure_csrf_cookie
def registration_gubn(request):
    return render_to_response('student_account/registration_gubn.html')


@ensure_csrf_cookie
def agree(request):
    print 'request.method = ', request.method
    print "request.POST['division'] = ", request.POST['division']

    if request.method == 'POST' and request.POST['division']:
        request.session['division'] = request.POST['division']
        print "STEP1 : request.session['division'] = ", request.session['division']

        context = {
            'division': request.session['division'],
        }

        return render_to_response('student_account/agree.html', context)
    else:
        return render_to_response('student_account/registration_gubn.html')


@ensure_csrf_cookie
def agree_done(request):
    print 'request.is_ajax = ', request.is_ajax
    print 'request.method = ', request.method
    print "request.POST['division'] = ", request.POST['agreeYN']

    data = {}

    if request.method == 'POST' and request.POST['agreeYN'] and request.POST['agreeYN'] == 'Y':
        # print "STEP2 :  request.session['division'] = ", request.session['division']
        # print "STEP2 :  request.session['agreeYN'] = ", request.POST['agreeYN']
        request.session['agreeYN'] = request.POST['agreeYN']

        if request.POST['agreeYN'] == 'Y':
            data['agreeYN'] = request.session['agreeYN']
            data['division'] = request.session['division']
    else:
        data['agreeYN'] = request.POST['agreeYN']

    print 'data = ', data

    return HttpResponse(json.dumps(data))


@csrf_exempt
def parent_agree(request):
    ## IPIN info

    print 'ipin module called1'

    sSiteCode = 'M231'
    sSitePw = '76421752'
    sModulePath = '/edx/app/edxapp/IPINClient'
    sCPRequest = commands.getoutput(sModulePath + ' SEQ ' + sSiteCode)
    sReturnURL = 'https://www.kmooc.kr/parent_agree_done'
    sEncData = commands.getoutput(sModulePath + ' REQ ' + sSiteCode + ' ' + sSitePw + ' ' + sCPRequest + ' ' + sReturnURL)

    print '===================================================='
    print '1 = ', sModulePath + ' SEQ ' + sSiteCode
    print '===================================================='
    print '3 = ', sCPRequest
    print '===================================================='
    print '4 = ', sModulePath + ' REQ ' + sSiteCode + ' ' + sSitePw + ' ' + sCPRequest + ' ' + sReturnURL
    print '===================================================='
    print '5 = ', sEncData
    print '===================================================='

    if sEncData == -9:
        sRtnMsg = '입력값 오류 : 암호화 처리시 필요한 파라미터값의 정보를 정확하게 입력해 주시기 바랍니다.'
    else:
        sRtnMsg = sEncData + ' 변수에 암호화 데이터가 확인되면 정상 정상이 아닌경우 리턴코드 확인 후 NICE평가정보 개발 담당자에게 문의해 주세요.'

    print 'sRtnMsg = ', sRtnMsg

    context = {
        'sEncData': sEncData,
    }

    return render_to_response('student_account/parent_agree.html', context)


@csrf_exempt
def parent_agree_done(request):
    sSiteCode = 'M231'
    sSitePw = '76421752'
    sModulePath = '/edx/app/edxapp/IPINClient'
    sEncData = request.POST['enc_data']

    sDecData = commands.getoutput(sModulePath + ' RES ' + sSiteCode + ' ' + sSitePw + ' ' + sEncData)

    print 'sDecData', sDecData

    if sDecData:
        val = sDecData.split('^')
        if val[6] and len(val[6]) == 8:
            context = {
                'isAuth': 'succ',
                'age': int(date.today().year) - int(val[6][:4]),
            }

            if int(date.today().year) - int(val[6][:4]) < 20:
                pass
            else:
                request.session['auth'] = 'Y'
    else:
        context = {
            'isAuth': 'fail',
            'age': 0,
        }

    print 'context > ', context

    return render_to_response('student_account/parent_agree_done.html', context)


@require_http_methods(['GET'])
@ensure_csrf_cookie
def registration_gubn(request):
    return render_to_response('student_account/registration_gubn.html')


@ensure_csrf_cookie
def agree(request):
    # print 'request.method = ', request.method
    # print "request.POST['division'] = ", request.POST['division']

    if request.method == 'POST' and request.POST['division']:
        request.session['division'] = request.POST['division']
        # print "STEP1 : request.session['division'] = ", request.session['division']

        context = {
            'division': request.session['division'],
        }

        return render_to_response('student_account/agree.html', context)
    else:
        return render_to_response('student_account/registration_gubn.html')


@ensure_csrf_cookie
def agree_done(request):
    print 'request.is_ajax = ', request.is_ajax
    print 'request.method = ', request.method
    print "request.POST['division'] = ", request.POST['agreeYN']

    data = {}

    if request.method == 'POST' and request.POST['agreeYN'] and request.POST['agreeYN'] == 'Y':
        # print "STEP2 :  request.session['division'] = ", request.session['division']
        # print "STEP2 :  request.session['agreeYN'] = ", request.POST['agreeYN']
        request.session['agreeYN'] = request.POST['agreeYN']

        if request.POST['agreeYN'] == 'Y':
            data['agreeYN'] = request.session['agreeYN']
            data['division'] = request.session['division']
    else:
        data['agreeYN'] = request.POST['agreeYN']

    print 'data = ', data

    return HttpResponse(json.dumps(data))


@require_http_methods(['GET'])
@ensure_csrf_cookie
@xframe_allow_whitelisted
def login_and_registration_form(request, initial_mode="login"):
    # Determine the URL to redirect to following login/registration/third_party_auth
    redirect_to = get_next_url_for_login_page(request)
    provider_info = _third_party_auth_context(request, redirect_to)

    # print 'currentProvider:', provider_info['currentProvider']
    # add kocw logic
    division = None

    # 로그인중이거나 oauth2 인증이 되어있으면 화면전환을 건너뜀
    if initial_mode == "login" or provider_info['currentProvider']:
        print 'login_and_registration_form type 1'
        pass
    elif 'errorMessage' in provider_info and provider_info['errorMessage'] is not None:
        print 'login_and_registration_form type 2'
        pass
    elif 'division' in request.session and 'agreeYN' in request.session and 'auth' in request.session:
        print 'login_and_registration_form type 3'
        division = request.session['division']
        del request.session['division']
        del request.session['agreeYN']
        del request.session['auth']
    elif 'division' in request.session and 'agreeYN' in request.session:
        print 'login_and_registration_form type 4'
        division = request.session['division']
        if request.session['division'] == 'N':
            return render_to_response('student_account/registration_gubn.html')
        del request.session['division']
        del request.session['agreeYN']
    else:
        print 'login_and_registration_form type 5'
        return render_to_response('student_account/registration_gubn.html')

    # print 'division = ', division

    """Render the combined login/registration form, defaulting to login

    This relies on the JS to asynchronously load the actual form from
    the user_api.

    Keyword Args:
        initial_mode (string): Either "login" or "register".
    """

    """Render the combined login/registration form, defaulting to login

    This relies on the JS to asynchronously load the actual form from
    the user_api.

    Keyword Args:
        initial_mode (string): Either "login" or "register".

    """

    # If we're already logged in, redirect to the dashboard
    if request.user.is_authenticated():
        return redirect(redirect_to)

    # Retrieve the form descriptions from the user API
    form_descriptions = _get_form_descriptions(request)

    # If this is a themed site, revert to the old login/registration pages.
    # We need to do this for now to support existing themes.
    # Themed sites can use the new logistration page by setting
    # 'ENABLE_COMBINED_LOGIN_REGISTRATION' in their
    # configuration settings.
    if is_request_in_themed_site() and not configuration_helpers.get_value('ENABLE_COMBINED_LOGIN_REGISTRATION', False):
        if initial_mode == "login":
            return old_login_view(request)
        elif initial_mode == "register":
            return old_register_view(request)

    # Allow external auth to intercept and handle the request
    ext_auth_response = _external_auth_intercept(request, initial_mode)
    if ext_auth_response is not None:
        return ext_auth_response

    # Our ?next= URL may itself contain a parameter 'tpa_hint=x' that we need to check.
    # If present, we display a login page focused on third-party auth with that provider.
    third_party_auth_hint = None
    if '?' in redirect_to:
        try:
            next_args = urlparse.parse_qs(urlparse.urlparse(redirect_to).query)
            provider_id = next_args['tpa_hint'][0]
            if third_party_auth.provider.Registry.get(provider_id=provider_id):
                third_party_auth_hint = provider_id
                initial_mode = "hinted_login"
        except (KeyError, ValueError, IndexError):
            pass

    context = {
        'data': {
            'login_redirect_url': redirect_to,
            'initial_mode': initial_mode,
            'third_party_auth': provider_info,
            'third_party_auth_hint': third_party_auth_hint or '',
            'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),

            # Include form descriptions retrieved from the user API.
            # We could have the JS client make these requests directly,
            # but we include them in the initial page load to avoid
            # the additional round-trip to the server.
            'login_form_desc': json.loads(form_descriptions['login']),
            'registration_form_desc': json.loads(form_descriptions['registration']),
            'password_reset_form_desc': json.loads(form_descriptions['password_reset']),
        },
        'login_redirect_url': redirect_to,  # This gets added to the query string of the "Sign In" button in header
        'responsive': True,
        'allow_iframing': True,
        'disable_courseware_js': True,
        'disable_footer': True,
        'division': division,
    }

    return render_to_response('student_account/login_and_register.html', context)

# -------------------- nice check -------------------- #
@csrf_exempt
def nicecheckplus(request):


    edx_user_info = json.loads(request.COOKIES['edx-user-info'])
    edx_user_email = str(edx_user_info['email'])

    # ----- get user_id query ----- #
    with connections['default'].cursor() as cur:
        query = """
            SELECT * 
            FROM   edxapp.auth_user 
            WHERE  email = '{0}' 
        """.format(edx_user_email)
        cur.execute(query)
        table = cur.fetchall()
        user_id =  table[0][0]
    # ----- get user_id query ----- #

    # encode data 
    nice_sitecode       = 'AD521'                      # NICE로부터 부여받은 사이트 코드
    nice_sitepasswd     = 'z0lWlstxnw0u'               # NICE로부터 부여받은 사이트 패스워드
    nice_cb_encode_path = '/edx/app/edxapp/CPClient'
    enc_data = request.POST.get('EncodeData')
    nice_command = '{0} DEC {1} {2} {3}'.format(nice_cb_encode_path, nice_sitecode, nice_sitepasswd, enc_data)
    plain_data = commands.getoutput(nice_command)
    di_index = plain_data.find("DI64:")
    nice_di = plain_data[di_index+5 : di_index+5+64]
 
    # return data parsing
    result_dict = {}
    pos1 = 0
    while pos1 <= len(plain_data):
	pos1 = plain_data.find(':')
	key_size = int(plain_data[:pos1])
	plain_data = plain_data[pos1 + 1:]
	key = plain_data[:key_size]
	plain_data = plain_data[key_size:]
	pos2 = plain_data.find(':')
	val_size = int(plain_data[:pos2])
	val = plain_data[pos2 + 1: pos2 + val_size + 1]
	result_dict[key] = val
	plain_data = plain_data[pos2 + val_size + 1:]
    result_dict = str(result_dict)
    result_dict = result_dict.replace("'", '"')

    # ----- nice check insert query ----- #
    with connections['default'].cursor() as cur:
        query = """
            INSERT INTO edxapp.auth_user_nicecheck 
                        (user_id, 
                         nice_check, 
                         di, 
                         plain_data) 
            VALUES      ({0}, 
                         'Y', 
                         '{1}', 
                         '{2}')
        """.format(str(user_id), nice_di, result_dict)
        cur.execute(query)
    # ----- nice check insert query ----- #

    return render_to_response('student_account/nicecheckplus.html')

@csrf_exempt
def nicecheckplus_error(request):
    print 'nicecheckplus_error called'
    return render_to_response('student_account/nicecheckplus_error.html')
# -------------------- nice check -------------------- #

def redirectTo(request, redirectTo):
    '''redirect for https..'''
    return redirect("/" + redirectTo)


@require_http_methods(['POST'])
def password_change_request_handler(request):
    """Handle password change requests originating from the account page.

    Uses the Account API to email the user a link to the password reset page.

    Note:
        The next step in the password reset process (confirmation) is currently handled
        by student.views.password_reset_confirm_wrapper, a custom wrapper around Django's
        password reset confirmation view.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: 200 if the email was sent successfully
        HttpResponse: 400 if there is no 'email' POST parameter, or if no user with
            the provided email exists
        HttpResponse: 403 if the client has been rate limited
        HttpResponse: 405 if using an unsupported HTTP method

    Example usage:

        POST /account/password

    """
    limiter = BadRequestRateLimiter()
    if limiter.is_rate_limit_exceeded(request):
        AUDIT_LOG.warning("Password reset rate limit exceeded")
        return HttpResponseForbidden()

    user = request.user
    # Prefer logged-in user's email
    email = user.email if user.is_authenticated() else request.POST.get('email')

    if email:
        try:
            request_password_change(email, request.get_host(), request.is_secure())
        except UserNotFound:
            AUDIT_LOG.info("Invalid password reset attempt")
            # Increment the rate limit counter
            limiter.tick_bad_request_counter(request)

            return HttpResponseBadRequest(_("No user with the provided email address exists."))

        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest(_("No email address provided."))


def _third_party_auth_context(request, redirect_to):
    """Context for third party auth providers and the currently running pipeline.

    Arguments:
        request (HttpRequest): The request, used to determine if a pipeline
            is currently running.
        redirect_to: The URL to send the user to following successful
            authentication.

    Returns:
        dict

    """
    context = {
        "currentProvider": None,
        "providers": [],
        "secondaryProviders": [],
        "finishAuthUrl": None,
        "errorMessage": None,
    }

    if third_party_auth.is_enabled():
        for enabled in third_party_auth.provider.Registry.accepting_logins():
            info = {
                "id": enabled.provider_id,
                "name": enabled.name,
                "iconClass": enabled.icon_class or None,
                "iconImage": enabled.icon_image.url if enabled.icon_image else None,
                "loginUrl": pipeline.get_login_url(
                    enabled.provider_id,
                    pipeline.AUTH_ENTRY_LOGIN,
                    redirect_url=redirect_to,
                ),
                "registerUrl": pipeline.get_login_url(
                    enabled.provider_id,
                    pipeline.AUTH_ENTRY_REGISTER,
                    redirect_url=redirect_to,
                ),
            }
            context["providers" if not enabled.secondary else "secondaryProviders"].append(info)

        running_pipeline = pipeline.get(request)
        if running_pipeline is not None:
            current_provider = third_party_auth.provider.Registry.get_from_pipeline(running_pipeline)

            if current_provider is not None:
                context["currentProvider"] = current_provider.name
                context["finishAuthUrl"] = pipeline.get_complete_url(current_provider.backend_name)

                if current_provider.skip_registration_form:
                    # As a reliable way of "skipping" the registration form, we just submit it automatically
                    context["autoSubmitRegForm"] = True

        # Check for any error messages we may want to display:
        for msg in messages.get_messages(request):
            if msg.extra_tags.split()[0] == "social-auth":
                # msg may or may not be translated. Try translating [again] in case we are able to:
                context['errorMessage'] = _(unicode(msg))  # pylint: disable=translation-of-non-string
                break

    return context


def _get_form_descriptions(request):
    """Retrieve form descriptions from the user API.

    Arguments:
        request (HttpRequest): The original request, used to retrieve session info.

    Returns:
        dict: Keys are 'login', 'registration', and 'password_reset';
            values are the JSON-serialized form descriptions.

    """
    return {
        'login': _local_server_get('/user_api/v1/account/login_session/', request.session),
        'registration': _local_server_get('/user_api/v1/account/registration/', request.session),
        'password_reset': _local_server_get('/user_api/v1/account/password_reset/', request.session)
    }


def _local_server_get(url, session):
    """Simulate a server-server GET request for an in-process API.

    Arguments:
        url (str): The URL of the request (excluding the protocol and domain)
        session (SessionStore): The session of the original request,
            used to get past the CSRF checks.

    Returns:
        str: The content of the response

    """
    # Since the user API is currently run in-process,
    # we simulate the server-server API call by constructing
    # our own request object.  We don't need to include much
    # information in the request except for the session
    # (to get past through CSRF validation)
    request = HttpRequest()
    request.method = "GET"
    request.session = session

    # Call the Django view function, simulating
    # the server-server API call
    view, args, kwargs = resolve(url)
    response = view(request, *args, **kwargs)

    # Return the content of the response
    return response.content


def _external_auth_intercept(request, mode):
    """Allow external auth to intercept a login/registration request.

    Arguments:
        request (Request): The original request.
        mode (str): Either "login" or "register"

    Returns:
        Response or None

    """
    if mode == "login":
        return external_auth_login(request)
    elif mode == "register":
        return external_auth_register(request)


def get_user_orders(user):
    """Given a user, get the detail of all the orders from the Ecommerce service.

    Arguments:
        user (User): The user to authenticate as when requesting ecommerce.

    Returns:
        list of dict, representing orders returned by the Ecommerce service.
    """
    no_data = []
    user_orders = []
    allowed_course_modes = ['professional', 'verified', 'credit']
    commerce_configuration = CommerceConfiguration.current()
    user_query = {'username': user.username}

    use_cache = commerce_configuration.is_cache_enabled
    cache_key = commerce_configuration.CACHE_KEY + '.' + str(user.id) if use_cache else None
    api = ecommerce_api_client(user)
    commerce_user_orders = get_edx_api_data(
        commerce_configuration, user, 'orders', api=api, querystring=user_query, cache_key=cache_key
    )

    for order in commerce_user_orders:
        if order['status'].lower() == 'complete':
            for line in order['lines']:
                product = line.get('product')
                if product:
                    for attribute in product['attribute_values']:
                        if attribute['name'] == 'certificate_type' and attribute['value'] in allowed_course_modes:
                            try:
                                date_placed = datetime.strptime(order['date_placed'], "%Y-%m-%dT%H:%M:%SZ")
                                order_data = {
                                    'number': order['number'],
                                    'price': order['total_excl_tax'],
                                    'title': order['lines'][0]['title'],
                                    'order_date': strftime_localized(
                                        date_placed.replace(tzinfo=pytz.UTC), 'SHORT_DATE'
                                    ),
                                    'receipt_url': commerce_configuration.receipt_page + order['number']
                                }
                                user_orders.append(order_data)
                            except KeyError:
                                log.exception('Invalid order structure: %r', order)
                                return no_data

    return user_orders


@login_required
@require_http_methods(['GET'])
def finish_auth(request):  # pylint: disable=unused-argument
    """ Following logistration (1st or 3rd party), handle any special query string params.

    See FinishAuthView.js for details on the query string params.

    e.g. auto-enroll the user in a course, set email opt-in preference.

    This view just displays a "Please wait" message while AJAX calls are made to enroll the
    user in the course etc. This view is only used if a parameter like "course_id" is present
    during login/registration/third_party_auth. Otherwise, there is no need for it.

    Ideally this view will finish and redirect to the next step before the user even sees it.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: 200 if the page was sent successfully
        HttpResponse: 302 if not logged in (redirect to login page)
        HttpResponse: 405 if using an unsupported HTTP method

    Example usage:

        GET /account/finish_auth/?course_id=course-v1:blah&enrollment_action=enroll

    """
    return render_to_response('student_account/finish_auth.html', {
        'disable_courseware_js': True,
        'disable_footer': True,
    })


def account_settings_context(request):
    """ Context for the account settings page.

    Args:
        request: The request object.

    Returns:
        dict

    """
    # -------------------- nice core -------------------- #
    nice_sitecode       = 'AD521'                      # NICE로부터 부여받은 사이트 코드
    nice_sitepasswd     = 'z0lWlstxnw0u'               # NICE로부터 부여받은 사이트 패스워드
    nice_cb_encode_path = '/edx/app/edxapp/CPClient'

    nice_authtype       = ''                           # 없으면 기본 선택화면, X: 공인인증서, M: 핸드폰, C: 카드
    nice_popgubun       = 'N'                          # Y : 취소버튼 있음 / N : 취소버튼 없음
    nice_customize      = ''                           # 없으면 기본 웹페이지 / Mobile : 모바일페이지
    nice_gender         = ''                           # 없으면 기본 선택화면, 0: 여자, 1: 남자
    nice_reqseq         = 'REQ0000000001'              # 요청 번호, 이는 성공/실패후에 같은 값으로 되돌려주게 되므로
                                                       # 업체에서 적절하게 변경하여 쓰거나, 아래와 같이 생성한다.

    nice_returnurl      = "http://192.168.33.20:8000/nicecheckplus"        # 성공시 이동될 URL
    nice_errorurl       = "http://192.168.33.20:8000/nicecheckplus_error"  # 실패시 이동될 URL
    nice_returnMsg      = ''

    plaindata = '7:REQ_SEQ{0}:{1}8:SITECODE{2}:{3}9:AUTH_TYPE{4}:{5}7:RTN_URL{6}:{7}7:ERR_URL{8}:{9}11:POPUP_GUBUN{10}:{11}9:CUSTOMIZE{12}:{13}6:GENDER{14}:{15}'\
                .format(len(nice_reqseq),nice_reqseq,
                        len(nice_sitecode),nice_sitecode,
                        len(nice_authtype),nice_authtype,
                        len(nice_returnurl),nice_returnurl,
                        len(nice_errorurl),nice_errorurl,
                        len(nice_popgubun),nice_popgubun,
                        len(nice_customize),nice_customize,
                        len(nice_gender),nice_gender )

    nice_command = '{0} ENC {1} {2} {3}'.format(nice_cb_encode_path, nice_sitecode, nice_sitepasswd, plaindata)
    enc_data = commands.getoutput(nice_command)

    if enc_data == -1 :
        nice_returnMsg = "암/복호화 시스템 오류입니다."
        enc_data = ""
    elif enc_data== -2 :
        nice_returnMsg = "암호화 처리 오류입니다."
        enc_data = ""
    elif enc_data== -3 :
        nice_returnMsg = "암호화 데이터 오류 입니다."
        enc_data = ""
    elif enc_data== -9 :
        nice_returnMsg = "입력값 오류 입니다."
        enc_data = ""

    # ----- DEBUG ----- #
    """
    print "nice_sitecode = {}".format(nice_sitecode)
    print "nice_sitepasswd = {}".format(nice_sitepasswd)
    print "nice_cb_encode_path = {}".format(nice_cb_encode_path)
    print "nice_authtype = {}".format(nice_authtype)
    print "nice_popgubun = {}".format(nice_popgubun)
    print "nice_customize = {}".format(nice_customize)
    print "nice_gender = {}".format(nice_gender)
    print "nice_reqseq = {}".format(nice_reqseq)
    print "nice_returnurl = {}".format(nice_returnurl)
    print "nice_errorurl = {}".format(nice_errorurl)
    print "plaindata = {}".format(plaindata)
    print "enc_data = {}".format(enc_data)
    """
    # ----- DEBUG ----- #
    # -------------------- nice core -------------------- #

    # -------------------- nice check -------------------- #
    try:
        edx_user_info = json.loads(request.COOKIES['edx-user-info'])
        edx_user_email = str(edx_user_info['email'])
    except BaseException:
        edx_user_info = ''
        edx_user_email = ''

    # ----- get user_id query ----- #
    with connections['default'].cursor() as cur:
        try:
            query = """
            SELECT plain_data 
            FROM   edxapp.auth_user_nicecheck 
            WHERE  user_id IN (SELECT id 
                               FROM   edxapp.auth_user 
                               WHERE  email = '{0}'); 
            """.format(edx_user_email)
            cur.execute(query)
            table = cur.fetchall()
            nice_info = table[0][0]
        except BaseException:
            nice_info = None
    # ----- get user_id query ----- #

    if nice_info != None:
        nice_dict = ast.literal_eval(nice_info)

        # created user gender
        user_gender = str(nice_dict['GENDER'])
        if user_gender == '1':
            user_gender = '남자'
        elif user_gender == '2':
            user_gender = '여자'

        # created user birth day
        user_birthday = nice_dict['BIRTHDATE']
        user_birthday_y = str(user_birthday[0:4])
        user_birthday_m = str(user_birthday[4:6])
        user_birthday_d = str(user_birthday[6:8])
        user_birthday = "{0}.{1}.{2}".format(user_birthday_y, user_birthday_m, user_birthday_d)

        # created user name
        user_name = nice_dict['UTF8_NAME']
        user_name = urllib.unquote(user_name).decode('utf8') 
  
        # created flag
        nice_check = 'yes'

    else:
        user_gender = ''
        user_birthday = ''
        user_name = ''
        nice_check = 'no'
    # -------------------- nice check -------------------- #

    user = request.user

    year_of_birth_options = [(unicode(year), unicode(year)) for year in UserProfile.VALID_YEARS]
    try:
        user_orders = get_user_orders(user)
    except:  # pylint: disable=bare-except
        log.exception('Error fetching order history from Otto.')
        # Return empty order list as account settings page expect a list and
        # it will be broken if exception raised
        user_orders = []

    countries_list = list(countries)
    countries_list.insert(0, (u'KR', u'South Korea'))

    context = {
        'user_gender': user_gender,
        'user_birthday': user_birthday,
        'user_name': user_name,
        'nice_check': nice_check,
        'enc_data': enc_data,
        'auth': {},
        'duplicate_provider': None,
        'fields': {
            'country': {
                'options': countries_list,
            }, 'gender': {
                'options': [(choice[0], _(choice[1])) for choice in UserProfile.GENDER_CHOICES],  # pylint: disable=translation-of-non-string
            }, 'language': {
                'options': released_languages(),
            }, 'level_of_education': {
                'options': [(choice[0], _(choice[1])) for choice in UserProfile.LEVEL_OF_EDUCATION_CHOICES],  # pylint: disable=translation-of-non-string
            }, 'password': {
                'url': reverse('password_reset'),
            }, 'year_of_birth': {
                'options': year_of_birth_options,
            }, 'preferred_language': {
                'options': all_languages(),
            }, 'time_zone': {
                'options': TIME_ZONE_CHOICES,
                'enabled': settings.FEATURES.get('ENABLE_TIME_ZONE_PREFERENCE'),
            }
        },
        'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
        'user_accounts_api_url': reverse("accounts_api", kwargs={'username': user.username}),
        'user_preferences_api_url': reverse('preferences_api', kwargs={'username': user.username}),
        'disable_courseware_js': True,
        'show_program_listing': ProgramsApiConfig.current().show_program_listing,
        'order_history': user_orders
    }

    if third_party_auth.is_enabled():
        # If the account on the third party provider is already connected with another edX account,
        # we display a message to the user.
        context['duplicate_provider'] = pipeline.get_duplicate_provider(messages.get_messages(request))

        auth_states = pipeline.get_provider_user_states(user)

        context['auth']['providers'] = [{
                                            'id': state.provider.provider_id,
                                            'name': state.provider.name,  # The name of the provider e.g. Facebook
                                            'connected': state.has_account,  # Whether the user's edX account is connected with the provider.
                                            # If the user is not connected, they should be directed to this page to authenticate
                                            # with the particular provider, as long as the provider supports initiating a login.
                                            'connect_url': pipeline.get_login_url(
                                                state.provider.provider_id,
                                                pipeline.AUTH_ENTRY_ACCOUNT_SETTINGS,
                                                # The url the user should be directed to after the auth process has completed.
                                                redirect_url=reverse('account_settings'),
                                            ),
                                            'accepts_logins': state.provider.accepts_logins,
                                            # If the user is connected, sending a POST request to this url removes the connection
                                            # information for this provider from their edX account.
                                            'disconnect_url': pipeline.get_disconnect_url(state.provider.provider_id, state.association_id),
                                        } for state in auth_states]

    return context


@login_required
@require_http_methods(['GET'])
def account_settings_confirm(request):
    """Render the current user's account settings page.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: 200 if the page was sent successfully
        HttpResponse: 302 if not logged in (redirect to login page)
        HttpResponse: 405 if using an unsupported HTTP method

    Example usage:

        GET /account/settings

    """

    context = {
        'correct': None
    }

    return render_to_response('student_account/account_settings_confirm.html', context)


@login_required
@require_http_methods(['POST'])
def account_settings_confirm_check(request):
    """Render the current user's account settings page.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: 200 if the page was sent successfully
        HttpResponse: 302 if not logged in (redirect to login page)
        HttpResponse: 405 if using an unsupported HTTP method

    Example usage:

        GET /account/settings

    """
    print '********************'
    print request.user.is_authenticated()
    print '********************'
    print request.user
    print '********************'

    user = authenticate(username=request.user, password=request.POST['passwd'], request=request)

    if user is None:
        request.session['passwdcheck'] = 'N'
        return JsonResponse({
            "success": False,
        })
    else:
        request.session['passwdcheck'] = 'Y'
        return JsonResponse({
            "success": True,
        })


@login_required
@require_http_methods(['GET'])
def account_settings(request):
    """Render the current user's account settings page.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: 200 if the page was sent successfully
        HttpResponse: 302 if not logged in (redirect to login page)
        HttpResponse: 405 if using an unsupported HTTP method

    Example usage:

        GET /account/settings

    """

    if 'passwdcheck' in request.session and request.session['passwdcheck'] == 'Y':
        return render_to_response('student_account/account_settings.html', account_settings_context(request))

    elif 'passwdcheck' in request.session and request.session['passwdcheck'] == 'N':
        context = {
            'correct': False
        }
        return render_to_response('student_account/account_settings_confirm.html', context)

    else:
        context = {
            'correct': None
        }
        return render_to_response('student_account/account_settings_confirm.html', context)


@login_required
def remove_account_view(request):
    return render_to_response('student_account/remove_account.html')


@login_required
def remove_account(request):
    if request.user.is_authenticated():

        try:

            # user info delete in Mongo
            client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'), settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
            db = client.cs_comments_service_development
            user_cnt = db.users.find({"external_id": "%s" % request.user.id, "username": "%s" % request.user.username}).count()

            print 'user_cnt --> ', user_cnt
            if user_cnt > 0:
                result = db.users.remove({"external_id": "%s" % request.user.id, "username": "%s" % request.user.username})
                print 'deleted_count --------------------------> ', request.user.id, request.user.username, result

            set_has_profile_image(request.user.username, False)
            profile_image_names = get_profile_image_names(request.user.username)
            remove_profile_images(profile_image_names)
            account_privacy_setting = {u'account_privacy': u'private'}
            update_user_preferences(request.user, account_privacy_setting, request.user.username)
            find_user = User.objects.get(id=request.user.id)
            ts = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
            # find_user.is_active = False
            # find_user.email = 'delete_' + request.user.email + ts

            user_profile = UserProfile.objects.get(user_id=request.user.id)

            # .get() = only result one
            user_socialauth = UserSocialAuth.objects.filter(user_id=request.user.id)

            # print 'remove_account s -------------------------------------'
            # print request.user.id
            # print find_user
            # print user_profile
            # print 'remove_account e -------------------------------------'

            uid = request.user.id

            find_user.username = str(uid)
            find_user.first_name = str(uid)
            find_user.last_name = str(uid)
            find_user.email = 'delete_' + str(uid) + '@delete.' + ts
            find_user.password = str(uid)
            find_user.is_staff = False
            find_user.is_active = False
            find_user.is_superuser = False

            user_profile.name = str(uid)
            user_profile.language = ''
            user_profile.location = ''
            user_profile.meta = ''
            user_profile.courseware = ''
            user_profile.gender = None
            user_profile.mailing_address = None
            user_profile.year_of_birth = None
            user_profile.level_of_education = None
            user_profile.goals = None
            user_profile.country = None
            user_profile.city = None
            user_profile.bio = None
            user_profile.profile_image_uploaded_at = None

            find_user.save()
            user_profile.save()
            user_socialauth.delete()

            logout(request)
        except:
            pass

    return redirect('/')
