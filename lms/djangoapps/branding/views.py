# -*- coding: utf-8 -*-
import logging
import urllib
import traceback
import json
import branding.api as branding_api
import courseware.views.views
import student.views.management
import pymongo
from urlparse import urlparse, parse_qs
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.urls import reverse
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils import translation
from django.utils.translation.trans_real import get_supported_language_variant
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from student.views.dashboard import effort_make_available
from edxmako.shortcuts import marketing_link, render_to_response
from openedx.core.djangoapps.lang_pref.api import released_languages
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from util.cache import cache_if_anonymous
from util.json_request import JsonResponse
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from bson import ObjectId

log = logging.getLogger(__name__)

# ==================================================================================================> login 오버라이딩 시작
from datetime import datetime
from datetime import timedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.module_loading import import_string
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'


def load_backend(path):
    return import_string(path)()


def _get_backends(return_tuples=False):
    backends = []
    for backend_path in settings.AUTHENTICATION_BACKENDS:
        backend = load_backend(backend_path)
        backends.append((backend, backend_path) if return_tuples else backend)
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does '
            'AUTHENTICATION_BACKENDS contain anything?'
        )
    return backends


def get_backends():
    return _get_backends(return_tuples=False)


def get_user_model():
    try:
        return django_apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.AUTH_USER_MODEL
        )


def _get_user_session_key(request):
    return get_user_model()._meta.pk.to_python(request.session[SESSION_KEY])


def login(request, user, backend=None):
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
                session_auth_hash and
                not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


# ==================================================================================================> login 오버라이딩 종료


# ==================================================================================================> AES 복호화 함수 시작
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode


def decrypt(key, _iv, enc):
    enc = enc.replace(' ', '+')
    BLOCK_SIZE = 16  # Bytes
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = b64decode(enc)
    iv = _iv
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc)).decode('utf8')


# ==================================================================================================> AES 복호화 함수 종료


@csrf_exempt
def multisite_error(request):
    context = {}

    error = request.GET.get('error')

    print "error -> ", error
    context['header'] = '디버깅 페이지'
    if error == 'error001':
        context['header'] = '등록되어 있지 않은 기관번호입니다.'
        context['info'] = '기관담당자에게 정확한 URL을 문의해주세요'
    if error == 'error002':
        context['info'] = 'in_url(접근URL)과 out_url(등록URL)이 일치하지 않습니다.'
    if error == 'error003':
        return redirect('signin_user')
    if error == 'error004':
        context['info'] = '복호화 데이터 파싱에 실패하였습니다.'
    if error == 'error005':
        context['info'] = '호출시간이 만료되었습니다'
    if error == 'error006':
        context['info'] = '접속한 org(기관번호)와 복호화된 orgid(기관번호)가 일치하지 않습니다.'
    if error == 'error007':
        context['info'] = '기관연계 되지 않은 사번입니다.'

    return render_to_response("multisite_error.html", context)


@csrf_exempt
def multisite_index(request, org):
    # 중앙교육연수원의 추가 정보 입력을 위한 변수
    addinfo = None

    log.info('multisite check multistie_success [%s]' % 'multistie_success' in request.session)

    if 'multistie_success' in request.session:
        if request.session['multistie_success'] == 1 and request.user.is_authenticated:
            return student.views.management.multisite_index(request, user=request.user)

    # 멀티사이트에 온 것을 환영합니다
    request.session['multisite_mode'] = 1
    request.session['multisite_org'] = org

    log.info("multisite check request.session['multisite_mode'] -> %s" % request.session['multisite_mode'])
    log.info("multisite check request.session['multisite_org'] -> %s" % request.session['multisite_org'])

    # 강좌 개수 확인
    with connections['default'].cursor() as cur:
        sql = '''
        select count(*)
        from multisite_course a
        join multisite b
        on a.site_id = b.site_id
        where b.site_code = '{0}';
        '''.format(org)
        cur.execute(sql)
        zero_mode = cur.fetchall()[0][0]

    # zero_mode = 0 # TEST

    # 로그인타입 / 등록URL / 암호화키 획득
    with connections['default'].cursor() as cur:
        sql = '''
        SELECT login_type, site_url, Encryption_key, ifnull(b.save_path, '/static/images/no_images_large.png') save_path
        FROM multisite a
        left join tb_attach b
        on a.logo_img = b.id
        where site_code = '{0}'
        '''.format(org)
        cur.execute(sql)
        rows = cur.fetchall()
        try:
            login_type = rows[0][0]
            out_url = rows[0][1]
            key = rows[0][2]
            save_path = rows[0][3]
        except BaseException as err:
            log.info('multisite check err [%s]' % traceback.format_exc(err))
            return redirect('/multisite_error?error=error001')

    request.session['save_path'] = save_path
    # DEBUG
    print "login_type -> ", login_type
    print "out_url -> ", out_url
    print "key -> ", key
    print "------------------------------------"

    # 접근URL 및 등록URL 획득
    if 'HTTP_REFERER' in request.META:
        in_url = request.META['HTTP_REFERER']
    else:
        in_url = ''
    in_url = in_url.replace('http://', "")
    in_url = in_url.replace('www.', "")
    out_url = out_url.replace('http://', "")
    out_url = out_url.replace('www.', "")

    # DEBUG
    log.info('multisite check in_url -> %s' % in_url)
    log.info('multisite check out_url -> %s' % out_url)
    print "------------------------------------"

    # 접근URL 과 등록URL 비교
    if out_url == 'passkey':
        pass
    elif out_url == 'passurl':
        pass
    elif out_url == 'passparam':
        pass
    elif out_url == 'debug':
        request.session['multistie_success'] = 1
        user = User.objects.get(email='staff@example.com')
        user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
        login(request, user)
        login_type = 'debug'
    else:
        if in_url.find(out_url) == -1:
            return redirect('/multisite_error?error=error002')

    # 파라미터 방식
    log.info('multisite check login_type [%s]' % login_type)

    if login_type == 'P':
        # 암호화 데이터 (get, post 구분 없음)
        if request.GET.get('encStr') or request.POST.get('encStr'):
            if request.GET.get('encStr'):
                encStr = request.GET.get('encStr')
            elif request.POST.get('encStr'):
                encStr = request.POST.get('encStr')
        else:
            encStr = None

        log.info('multisite check encStr [%s]' % encStr)

        # DEBUG
        # encStr = 'HMSFfWYS/NSUE93/Ra7TfEWuBhTPy9XZiHJoeD+QV+mMVgEEb9ezJ4OyYuDlwuNG'

        if request.user.is_staff:
            return student.views.management.multisite_index(request, user=request.user)

        if out_url == 'passparam' and encStr == None:
            request.session['multisite_mode'] = 2
            return redirect('/login')
        elif (out_url == 'passparam' and encStr != None) or (out_url != 'passparam'):
            # 암호화 데이터 복호화

            try:
                encStr = encStr.replace(' ', '+')

            except BaseException as err:
                log.info('multisite check err1 [%s]' % traceback.format_exc(err))
                return redirect('/multisite_error?error=error003')

            try:
                # url decode 처리
                encStr = urllib.unquote(encStr)

                raw_data = decrypt(key, key, encStr)
                qs = raw_data
                raw_data = raw_data.split('&')

                # addinfo 파라미터가 있는지 체크
                params = parse_qs(qs)

                if 'addinfo' in params:
                    addinfo = params['addinfo'][0]

            except BaseException as err:
                log.info('multisite check err2 [%s]' % traceback.format_exc(err))
                return redirect('/multisite_error?error=error003')
            except Exception as e:
                log.info('multisite check err3 [%s]' % traceback.format_exc(e))

            # DEBUG
            print 'raw_data -> ', raw_data
            print "------------------------------------"

            # 복호화 데이터 파싱
            try:
                calltime = raw_data[0].split('=')[1]
                userid = raw_data[1].split('=')[1]
                orgid = raw_data[2].split('=')[1]

                # 중앙교육 연수원의 경우 addinfo 파라미터를 추가적으로 보내고, 해당 내용은 multisite_member 테이블에 추가정보로 입력한다.
                if len(raw_data) > 3:
                    pass

            except BaseException as err:
                log.info('multisite check err4 [%s]' % traceback.format_exc(err))
                return redirect('/multisite_error?error=error004')

            # DEBUG
            log.info('multisite check calltime [%s] userid [%s] orgid [%s]' % (calltime, userid, orgid))

            # 호출시간 파싱
            calltime = str(calltime)
            year = int(calltime[0:4])
            mon = int(calltime[4:6])
            day = int(calltime[6:8])
            hour = int(calltime[8:10])
            min = int(calltime[10:12])
            sec = int(calltime[12:14])
            java_calltime = datetime(year, mon, day, hour, min, sec)
            python_calltime = datetime.utcnow() + timedelta(hours=9)

            # DEBUG
            log.info('multisite check java_calltime -> %s' % java_calltime)
            log.info('multisite check python_calltime -> %s' % python_calltime)

            # 호출시간 만료 체크
            if java_calltime + timedelta(seconds=180) < python_calltime:
                return redirect('/multisite_error?error=error005')

            # 복호화 기관코드와 접속 기관코드 비교
            if org != orgid:
                return redirect('/multisite_error?error=error006')

            # 기관연계 된 회원인지 확인
            with connections['default'].cursor() as cur:
                sql = '''
                       SELECT user_id
                       FROM multisite_member as a
                       join multisite as b
                       on a.site_id = b.site_id
                       where site_code = '{0}'
                       and org_user_id = '{1}'
                   '''.format(org, userid)

                cur.execute(sql)
                rows = cur.fetchall()

            log.info('multisite check len(rows) -> %s' % len(rows))

            # 기관연계 된 회원이라면 SSO 로그인
            if len(rows) != 0:
                request.session['multistie_success'] = 1
                user = User.objects.get(pk=rows[0][0])
                user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
                login(request, user)

                # addinfo 가 있다면 DB 저장
                if addinfo and len(addinfo) > 0:
                    try:
                        with connections['default'].cursor() as cur:
                            sql = '''
                                UPDATE multisite_member a
                                        JOIN
                                    multisite b ON a.site_id = b.site_id 
                                SET 
                                    a.addinfo = '{addinfo}'
                                WHERE
                                    b.site_code = '{org}' AND a.org_user_id = '{userid}'                               
                               '''.format(
                                addinfo=addinfo,
                                org=org,
                                userid=userid
                            )
                            cur.execute(sql)
                    except Exception as e:
                        print e

                # test code
                log.info('multisite check zero_mode [%s]' % zero_mode)

                if zero_mode == 0:
                    request.session['multisite_zero'] = 1
                    return redirect('/')
            # 아니라면 에러페이지 리다이렉트
            else:
                log.info('multisite check set multisite_userid [%s]' % userid)

                request.session['multistie_success'] = 1
                request.session['multisite_userid'] = userid
                if addinfo:
                    request.session['multisite_addinfo'] = addinfo

                return redirect('/login')

    # Oauth 방식
    elif login_type == 'O':
        url = 'https://www.kmooc.kr/auth/login/' + str(org) + '/?auth_entry=login&next=%2Forg%2F' + str(org)
        log.info("multisite check url -> %s" % url)
        if not request.user.is_authenticated:
            request.session['multisite_mode'] = 0
            return redirect(url)

    # basic logic
    if request.user.is_authenticated:
        if configuration_helpers.get_value(
                'ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER',
                settings.FEATURES.get('ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER', True)):
            pass
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from openedx.core.djangoapps.external_auth.views import ssl_login
        if not request.GET.get('next'):
            req_new = request.GET.copy()
            req_new['next'] = reverse('dashboard')
            request.GET = req_new
        return ssl_login(request)
    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )
    if enable_mktg_site:
        marketing_urls = configuration_helpers.get_value(
            'MKTG_URLS',
            settings.MKTG_URLS
        )
        return redirect(marketing_urls.get('ROOT'))
    domain = request.META.get('HTTP_HOST')
    if domain and 'edge.edx.org' in domain:
        return redirect(reverse("signin_user"))
    return student.views.management.multisite_index(request, user=request.user)


def get_multisite_list(request):
    user_id = request.POST.get('user_id')

    with connections['default'].cursor() as cur:
        sql = '''
            SELECT site_code, org_user_id, site_name
            FROM multisite_member AS a
            JOIN multisite AS b
            ON a.site_id = b.site_id
            WHERE user_id = {user_id}
        '''.format(user_id=user_id)

        print sql

        cur.execute(sql)
        rows = cur.fetchall()

    if len(rows) == 0:
        return JsonResponse({'return': 'zero'})

    print "------------------------> hello s"
    print "user_id = ", user_id
    print "------------------------> hello e"

    return JsonResponse({'return': rows})


def get_org_list(request):
    with connections['default'].cursor() as cur:
        query = """
            SELECT detail_code, detail_name
              FROM code_detail
             WHERE group_code = 003
             AND USE_YN = 'Y'
             ORDER BY detail_name;
        """
        cur.execute(query)
        org_index = cur.fetchall()
        org_list = list(org_index)
        org_count = len(org_list)

    return JsonResponse({'result': org_list, 'count': org_count})


def delete_multisite_account(request):
    user_id = request.POST.get('user_id')
    org = request.POST.get('org')

    with connections['default'].cursor() as cur:
        sql = '''
            delete a
            from multisite_member as a
            join multisite as b
            on a.site_id = b.site_id
            where b.site_code = '{org}' and a.user_id = '{user_id}'
        '''.format(org=org, user_id=user_id)

        print sql

        cur.execute(sql)

    return JsonResponse({'return': 'success'})


@ensure_csrf_cookie
@transaction.non_atomic_requests
@cache_if_anonymous()
def index(request):
    """
    Redirects to main page -- info page if user authenticated, or marketing if not
    수정시 mobile_index도 함께 수정해야함
    """

    # 멀티사이트 인덱스에서 더럽혀진 영혼을 정화하는 구간입니다.
    # 치유의 빛이 흐릿하게 빛나며 더럽혀진 영혼이 정화됩니다.
    if request.session.get('multisite_mode'):
        del request.session['multisite_mode']

    if request.session.get('multisite_org'):
        del request.session['multisite_org']

    if request.session.get('save_path'):
        del request.session['save_path']

    if request.session.get('multisite_addinfo'):
        del request.session['multisite_addinfo']

    if request.user.is_authenticated:
        # Only redirect to dashboard if user has
        # courses in his/her dashboard. Otherwise UX is a bit cryptic.
        # In this case, we want to have the user stay on a course catalog
        # page to make it easier to browse for courses (and register)
        if configuration_helpers.get_value(
                'ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER',
                settings.FEATURES.get('ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER', True)):
            # return redirect(reverse('dashboard'))
            pass

    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from openedx.core.djangoapps.external_auth.views import ssl_login
        # Set next URL to dashboard if it isn't set to avoid
        # caching a redirect to / that causes a redirect loop on logout
        if not request.GET.get('next'):
            req_new = request.GET.copy()
            req_new['next'] = reverse('dashboard')
            request.GET = req_new
        return ssl_login(request)

    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        marketing_urls = configuration_helpers.get_value(
            'MKTG_URLS',
            settings.MKTG_URLS
        )
        return redirect(marketing_urls.get('ROOT'))

    domain = request.META.get('HTTP_HOST')

    # keep specialized logic for Edge until we can migrate over Edge to fully use
    # configuration.
    if domain and 'edge.edx.org' in domain:
        return redirect(reverse("signin_user"))

    #  we do not expect this case to be reached in cases where
    #  marketing and edge are enabled
    return student.views.management.index(request, user=request.user)


@ensure_csrf_cookie
@transaction.non_atomic_requests
@cache_if_anonymous()
def mobile_index(request):
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from openedx.core.djangoapps.external_auth.views import ssl_login
        # Set next URL to dashboard if it isn't set to avoid
        # caching a redirect to / that causes a redirect loop on logout
        if not request.GET.get('next'):
            req_new = request.GET.copy()
            req_new['next'] = reverse('dashboard')
            request.GET = req_new
        return ssl_login(request)

    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        marketing_urls = configuration_helpers.get_value(
            'MKTG_URLS',
            settings.MKTG_URLS
        )
        return redirect(marketing_urls.get('ROOT'))


    #  we do not expect this case to be reached in cases where
    #  marketing and edge are enabled
    return student.views.management.mobile_index(request, user=request.user)


@ensure_csrf_cookie
@cache_if_anonymous()
def courses(request):
    """
    Render the "find courses" page. If the marketing site is enabled, redirect
    to that. Otherwise, if subdomain branding is on, this is the university
    profile page. Otherwise, it's the edX courseware.views.views.courses page
    수정시 mobile_courses도 함께 수정
    """
    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        return redirect(marketing_link('COURSES'), permanent=True)

    if not settings.FEATURES.get('COURSES_ARE_BROWSABLE'):
        raise Http404

    #  we do not expect this case to be reached in cases where
    #  marketing is enabled or the courses are not browsable
    return courseware.views.views.courses(request)


@ensure_csrf_cookie
# @cache_if_anonymous()
def mobile_courses(request):
    """
    Render the "find courses" page. If the marketing site is enabled, redirect
    to that. Otherwise, if subdomain branding is on, this is the university
    profile page. Otherwise, it's the edX courseware.views.views.courses page
    """

    # search_query 여부에따라 강좌 검색과 모바일 메인 페이지 분기
    search_query = request.GET.get('search_query')
    if search_query is None:
        return mobile_index(request)

    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        return redirect(marketing_link('COURSES'), permanent=True)

    if not settings.FEATURES.get('COURSES_ARE_BROWSABLE'):
        raise Http404

    #  we do not expect this case to be reached in cases where
    #  marketing is enabled or the courses are not browsable
    return courseware.views.views.mobile_courses(request)


def _footer_static_url(request, name):
    """Construct an absolute URL to a static asset. """
    return request.build_absolute_uri(staticfiles_storage.url(name))


def _footer_css_urls(request, package_name):
    """Construct absolute URLs to CSS assets in a package. """
    # We need this to work both in local development and in production.
    # Unfortunately, in local development we don't run the full asset pipeline,
    # so fully processed output files may not exist.
    # For this reason, we use the *css package* name(s), rather than the static file name
    # to identify the CSS file name(s) to include in the footer.
    # We then construct an absolute URI so that external sites (such as the marketing site)
    # can locate the assets.
    package = settings.PIPELINE_CSS.get(package_name, {})
    paths = [package['output_filename']] if not settings.DEBUG else package['source_filenames']
    return [
        _footer_static_url(request, path)
        for path in paths
    ]


def _render_footer_html(request, show_openedx_logo, include_dependencies, include_language_selector):
    """Render the footer as HTML.

    Arguments:
        show_openedx_logo (bool): If True, include the OpenEdX logo in the rendered HTML.
        include_dependencies (bool): If True, include JavaScript and CSS dependencies.
        include_language_selector (bool): If True, include a language selector with all supported languages.

    Returns: unicode

    """
    bidi = 'rtl' if translation.get_language_bidi() else 'ltr'
    css_name = settings.FOOTER_CSS['openedx'][bidi]

    context = {
        'hide_openedx_link': not show_openedx_logo,
        'footer_js_url': _footer_static_url(request, 'js/footer-edx.js'),
        'footer_css_urls': _footer_css_urls(request, css_name),
        'bidi': bidi,
        'include_dependencies': include_dependencies,
        'include_language_selector': include_language_selector
    }

    return render_to_response("footer.html", context)


@cache_control(must_revalidate=True, max_age=settings.FOOTER_BROWSER_CACHE_MAX_AGE)
def footer(request):
    """Retrieve the branded footer.

    This end-point provides information about the site footer,
    allowing for consistent display of the footer across other sites
    (for example, on the marketing site and blog).

    It can be used in one of two ways:
    1) A client renders the footer from a JSON description.
    2) A browser loads an HTML representation of the footer
        and injects it into the DOM.  The HTML includes
        CSS and JavaScript links.

    In case (2), we assume that the following dependencies
    are included on the page:
    a) JQuery (same version as used in edx-platform)
    b) font-awesome (same version as used in edx-platform)
    c) Open Sans web fonts

    Example: Retrieving the footer as JSON

        GET /api/branding/v1/footer
        Accepts: application/json

        {
            "navigation_links": [
                {
                  "url": "http://example.com/about",
                  "name": "about",
                  "title": "About"
                },
                # ...
            ],
            "social_links": [
                {
                    "url": "http://example.com/social",
                    "name": "facebook",
                    "icon-class": "fa-facebook-square",
                    "title": "Facebook",
                    "action": "Sign up on Facebook!"
                },
                # ...
            ],
            "mobile_links": [
                {
                    "url": "http://example.com/android",
                    "name": "google",
                    "image": "http://example.com/google.png",
                    "title": "Google"
                },
                # ...
            ],
            "legal_links": [
                {
                    "url": "http://example.com/terms-of-service.html",
                    "name": "terms_of_service",
                    "title': "Terms of Service"
                },
                # ...
            ],
            "openedx_link": {
                "url": "http://open.edx.org",
                "title": "Powered by Open edX",
                "image": "http://example.com/openedx.png"
            },
            "logo_image": "http://example.com/static/images/logo.png",
            "copyright": "EdX, Open edX and their respective logos are trademarks or registered trademarks of edX Inc."
        }


    Example: Retrieving the footer as HTML

        GET /api/branding/v1/footer
        Accepts: text/html


    Example: Including the footer with the "Powered by Open edX" logo

        GET /api/branding/v1/footer?show-openedx-logo=1
        Accepts: text/html


    Example: Retrieving the footer in a particular language

        GET /api/branding/v1/footer?language=en
        Accepts: text/html


    Example: Retrieving the footer with a language selector

        GET /api/branding/v1/footer?include-language-selector=1
        Accepts: text/html


    Example: Retrieving the footer with all JS and CSS dependencies (for testing)

        GET /api/branding/v1/footer?include-dependencies=1
        Accepts: text/html

    """
    if not branding_api.is_enabled():
        raise Http404

    # Use the content type to decide what representation to serve
    accepts = request.META.get('HTTP_ACCEPT', '*/*')

    # Show the OpenEdX logo in the footer
    show_openedx_logo = bool(request.GET.get('show-openedx-logo', False))

    # Include JS and CSS dependencies
    # This is useful for testing the end-point directly.
    include_dependencies = bool(request.GET.get('include-dependencies', False))

    # Override the language if necessary
    language = request.GET.get('language', translation.get_language())
    try:
        language = get_supported_language_variant(language)
    except LookupError:
        language = settings.LANGUAGE_CODE

    # Include a language selector
    include_language_selector = request.GET.get('include-language-selector', '') == '1'

    # Render the footer information based on the extension
    if 'text/html' in accepts or '*/*' in accepts:
        cache_params = {
            'language': language,
            'show_openedx_logo': show_openedx_logo,
            'include_dependencies': include_dependencies
        }
        if include_language_selector:
            cache_params['language_selector_options'] = ','.join(sorted([lang.code for lang in released_languages()]))
        cache_key = u"branding.footer.{params}.html".format(params=urllib.urlencode(cache_params))

        content = cache.get(cache_key)
        if content is None:
            with translation.override(language):
                content = _render_footer_html(
                    request, show_openedx_logo, include_dependencies, include_language_selector
                )
                cache.set(cache_key, content, settings.FOOTER_CACHE_TIMEOUT)
        return HttpResponse(content, status=200, content_type="text/html; charset=utf-8")

    elif 'application/json' in accepts:
        cache_key = u"branding.footer.{params}.json".format(
            params=urllib.urlencode({
                'language': language,
                'is_secure': request.is_secure(),
            })
        )
        footer_dict = cache.get(cache_key)
        if footer_dict is None:
            with translation.override(language):
                footer_dict = branding_api.get_footer(is_secure=request.is_secure())
                cache.set(cache_key, footer_dict, settings.FOOTER_CACHE_TIMEOUT)
        return JsonResponse(footer_dict, 200, content_type="application/json; charset=utf-8")

    else:
        return HttpResponse(status=406)
