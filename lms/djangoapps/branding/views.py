# -*- coding: utf-8 -*- 
"""Views for the branding app. """
import logging
import urllib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, Http404, JsonResponse
from django.utils import translation
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.staticfiles.storage import staticfiles_storage

from edxmako.shortcuts import render_to_response
import student.views
from student.models import CourseEnrollment
import courseware.views.views
from edxmako.shortcuts import marketing_link
from util.cache import cache_if_anonymous
from util.json_request import JsonResponse
import branding.api as branding_api
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

import sys
import json
import MySQLdb as mdb

from django.db import connections
import pymysql
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import re

log = logging.getLogger(__name__)

def get_univ_name(univ_code):
    if univ_code == 'KYUNGNAMUNIVk':
        return '경남대학교'
    elif univ_code == 'KHUk':
        return '경희대학교'
    elif univ_code == 'KoreaUnivK':
        return '고려대학교'
    elif univ_code == 'DGUk':
        return '대구대학교'
    elif univ_code == 'PNUk':
        return '부산대학교'
    elif univ_code == 'SMUCk':
        return '상명대학교(천안)'
    elif univ_code == 'SMUk':
        return '상명대학교(서울)'
    elif univ_code == 'SNUk':
        return '서울대학교'
    elif univ_code == 'SKKUk':
        return '성균관대학교'
    elif univ_code == 'KKUk':
        return '건국대학교(글로컬)'
    elif univ_code == 'SSUk':
        return '성신여자대학교'
    elif univ_code == 'SejonguniversityK':
        return '세종대학교'
    elif univ_code == 'SookmyungK':
        return '숙명여자대학교'
    elif univ_code == 'YSUk':
        return '연세대학교'
    elif univ_code == 'YeungnamUnivK':
        return '영남대학교'
    elif univ_code == 'UOUk':
        return '울산대학교'
    elif univ_code == 'EwhaK':
        return '이화여자대학교'
    elif univ_code == 'INHAuniversityK':
        return '인하대학교'
    elif univ_code == 'CBNUk':
        return '전북대학교'
    elif univ_code == 'KonkukK':
        return '건국대학교'
    elif univ_code == 'KSUk':
        return '경성대학교'
    elif univ_code == 'SOGANGk':
        return '서강대학교'
    elif univ_code == 'POSTECHk':
        return '포항공과대학교'
    elif univ_code == 'KAISTk':
        return '한국과학기술원'
    elif univ_code == 'HYUk':
        return '한양대학교'
    elif univ_code == 'HongikUnivK':
        return '홍익대학교'
    elif univ_code == 'CAUk':
        return '중앙대학교'
    elif univ_code == 'GachonUnivK':
        return '가천대학교'
    elif univ_code == 'DonggukK':
        return '동국대학교'
    elif univ_code == 'DSUk':
        return '동신대학교'
    elif univ_code == 'DAUk':
        return '동아대학교'
    elif univ_code == 'TUk':
        return '동명대학교'
    elif univ_code == 'MokwonK':
        return '목원대학교'
    elif univ_code == 'PCUk':
        return ' 배재대학교'
    elif univ_code == 'PKNUk':
        return '부경대학교'
    elif univ_code == 'SunMoonK':
        return '선문대학교'
    elif univ_code == 'SCHk':
        return '순천향대학교'
    elif univ_code == 'WSUK':
        return '우송대학교'
    elif univ_code == 'WKUk':
        return '원광대학교'
    elif univ_code == 'InhatcK':
        return '인하공업전문대학교'
    elif univ_code == 'ChosunK':
        return ' 조선대학교'
    elif univ_code == 'CNUk':
        return '충남대학교'
    elif univ_code == 'ChungbukK':
        return '충북대학교'
    elif univ_code == 'KonYangK':
        return '건양대학교'
    elif univ_code == 'UOSk':
        return '서울시립대학교'
    elif univ_code == 'SoongsilUnivK':
        return '숭실대학교'
    elif univ_code == 'JNUk':
        return '전남대학교'
    elif univ_code == 'CKUk':
        return '가톨릭관동대학교'
    elif univ_code == 'HallymK':
        return '한림대학교'
    elif univ_code == 'KONGJUk':
        return '공주대학교'
    elif univ_code == 'SEOULTECHk':
        return '서울과학기술대학교'
    elif univ_code == 'SKUk':
        return '성결대학교'
    elif univ_code == 'AYUk':
        return '안양대학교'
    elif univ_code == 'YonseiWK':
        return '연세대학교(원주)'
    elif univ_code == 'HansungK':
        return '한성대학교'
    elif univ_code == 'KUMOHk':
        return '금오공과대학교'
    elif univ_code == 'DKUK':
        return '단국대학교'
    elif univ_code == 'BUFSk':
        return '부산외국어대학교'
    elif univ_code == 'SWUk':
        return '서울여자대학교'
    elif univ_code == 'SYUk':
        return '삼육대학교'
    elif univ_code == 'KNUk':
        return '경북대학교'
    elif univ_code == 'KIUk':
        return '경일대학교'
    elif univ_code == 'KMUk':
        return '국민대학교'
    elif univ_code == 'DCUk':
        return '대구가톨릭대학교'
    elif univ_code == 'DHUk':
        return '대구한의대학교'
    elif univ_code == 'DJUk':
        return '대전대학교'
    elif univ_code == 'CUKk':
        return '가톨릭대학교'
    elif univ_code == 'JEJUk':
        return '제주대학교'
    elif univ_code == 'HGUk':
        return '한동대학교'
    elif univ_code == 'SKP.KAISTk':
        return '서울대, 한국과학기술원, 포항공대'
    elif univ_code == 'SKP.SNUk':
        return '서울대, 한국과학기술원, 포항공대'
    elif univ_code == 'SKP.POSTECHk':
        return '서울대, 한국과학기술원, 포항공대'
    elif univ_code == 'SKP_KAISTk':
        return '서울대, 한국과학기술원, 포항공대'
    elif univ_code == 'SKP_SNUk':
        return '서울대, 한국과학기술원, 포항공대'
    elif univ_code == 'SKP_POSTECHk':
        return '서울대, 한국과학기술원, 포항공대'
    else:
        return '알수없음'

def course_api(request):
    conn = pymysql.connect(host='192.168.33.21', user='hello', password='0000',
                       db='edxapp', charset='utf8')
    cur = conn.cursor()
    #with connections['default'].cursor() as cur:
    sql = '''
    SELECT id, 
           display_name, 
           start, 
           end, 
           enrollment_start, 
           enrollment_end, 
           created, 
           modified, 
           course_video_url, 
           course_image_url 
    FROM   edxapp.course_overviews_courseoverview
    '''
    cur.execute(sql)
    slist = cur.fetchall()

    # ----- mongo ----- #
    m_org = 'POSTECHk'
    m_course = 'POSTECH.EECE341k'
    m_run = '2015-01'

    client = MongoClient('192.168.33.21', 27017)
    db = client["edxapp"]
    collection = db["modulestore.active_versions"]

    cursor = collection.find({'org':m_org, 'course':m_course, 'run':m_run})

    pb = str(cursor[0]['versions']['published-branch'])

    print pb #DEBUG

    collection = db["modulestore.structures"]
    cursor = collection.find({'_id':ObjectId(pb)})

    block_text = str(cursor[0]['blocks'])

    index = block_text.find("u'block_type': u'course'")
    course_text = block_text[index:]

    ct_start = course_text.find("u'children':")
    ct_end = course_text.find("u'linguistics'")

    children = course_text[ct_start:ct_end-2]
    children = children.replace('[','{')
    children = children.replace(']','}')
 
    print children #DEBUG

    #cc = children.count('chapter')
 
    chapter_list = []

    for m in re.finditer('chapter', children):
        chapter_list.append( children[ m.start()+12 : m.end()+37 ] )

    index = block_text.find(chapter_list[0])
    course_text = block_text[index: index+5000]
    dn_index = course_text.find("u'display_name'")
    dn = course_text[dn_index:dn_index+500]
    
    print "#########################"

    print dn

    print "#########################"

    #for i in chapter_list:
    #    print i
    #print len(chapter_list)
    #print children.find("u'",0)
    #print children.find("u'",1)

    #print cursor
    #cursor = collection.find({'versions':{'published-branch':pb}})
    #for document in cursor:
    #    print document

    # ----- mongo ----- #

    # init list
    display_name_list = []
    course_id_list = []
    univ_name_list = []
    start_time_list = []
    end_time_list = []
    enroll_start_list = []
    enroll_end_list = []
    created_list = []
    modified_list = []
    video_list = []
    img_list = []
    location_list = []

    for item in slist:
        # making
        course_id = item[0]
        start = course_id.find(':')
        end = course_id.find('+')
        univ_code = course_id[ start+1 : end ]
        univ_name = get_univ_name(univ_code)
        # insert
        univ_name_list.append(univ_name)
        course_id_list.append(course_id)

    for item in slist:
        # insert
        display_name_list.append(item[1])
        start_time_list.append(item[2])
        end_time_list.append(item[3])
        enroll_start_list.append(item[4])
        enroll_end_list.append(item[5])
        created_list.append(item[6])
        modified_list.append(item[7])
        video_list.append(item[8])
        img_list.append("http://www.kmooc.kr" + str(item[9]))

    # ----- DEBUG ----- #
    print "##############"
    print "total = {}".format(len(slist))
    """
    for n in range(0, len(slist) ):
        print "--------------------- {}".format(n)
        print course_id_list[n]
        print display_name_list[n]
        print univ_name_list[n]
        print start_time_list[n]
        print end_time_list[n]
        print enroll_start_list[n]
        print enroll_end_list[n]
        print created_list[n]
        print modified_list[n]
        print video_list[n]
        print img_list[n]
        print "---------------------"
    """
    print "##############"
    # ----- DEBUG ----- #

    return JsonResponse({'foo':slist})

def get_course_enrollments(user):
    """
    Returns the course enrollments for the passed in user within the context of current org, that
    is filtered by course_org_filter
    """
    enrollments = CourseEnrollment.enrollments_for_user(user)
    course_org = configuration_helpers.get_value('course_org_filter')
    if course_org:
        site_enrollments = [
            enrollment for enrollment in enrollments if enrollment.course_id.org == course_org
        ]
    else:
        site_enrollments = [
            enrollment for enrollment in enrollments
        ]
    return site_enrollments


@ensure_csrf_cookie
@cache_if_anonymous()
def index(request):
    '''
    Redirects to main page -- info page if user authenticated, or marketing if not
    '''
    print 'def index called'

    if request.user.is_authenticated():
        # Only redirect to dashboard if user has
        # courses in his/her dashboard. Otherwise UX is a bit cryptic.
        # In this case, we want to have the user stay on a course catalog
        # page to make it easier to browse for courses (and register)

        if configuration_helpers.get_value(
                'ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER',
                settings.FEATURES.get('ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER', True)):
            pass
            # return redirect(reverse('dashboard'))

    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from external_auth.views import ssl_login
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
        return redirect(settings.MKTG_URLS.get('ROOT'))

    domain = request.META.get('HTTP_HOST')

    # keep specialized logic for Edge until we can migrate over Edge to fully use
    # configuration.
    if domain and 'edge.edx.org' in domain:
        return redirect(reverse("signin_user"))

    #  we do not expect this case to be reached in cases where
    #  marketing and edge are enabled


    return student.views.index(request, user=request.user)


def index_en(request):
    request.session['_language'] = 'en'
    # redirect_to = request.GET.get('next', '/')
    return redirect('/')


def index_ko(request):
    request.session['_language'] = 'ko_kr'
    # redirect_to = request.GET.get('next', '/')
    return redirect('/')


def notice(request):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'), settings.DATABASES.get('default').get('USER'), settings.DATABASES.get('default').get('PASSWORD'), settings.DATABASES.get('default').get('NAME'));
    query = """
         SELECT title, link,
               concat(substring(sdate, 1, 4),
                      '/',
                      substring(sdate, 5, 2),
                      '/',
                      substring(sdate, 7, 2))
                  sdate,
               concat(substring(edate, 1, 4),
                      '/',
                      substring(edate, 5, 2),
                      '/',
                      substring(edate, 7, 2))
                  edate
          FROM tb_notice
         WHERE     useyn = 'Y'
               AND date_format(now(), '%Y%m%d%H%i') BETWEEN concat(sdate, stime)
                                                        AND concat(edate, etime)
        ORDER BY sdate, stime;
    """
    print 'notice query', query

    result = []
    with con:
        cur = con.cursor();
        cur.execute("set names utf8")
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        for row in rows:
            row = dict(zip(columns, row))
            result.append(row)

    cur.close()
    con.close()

    return HttpResponse(json.dumps(result))


@ensure_csrf_cookie
@cache_if_anonymous()
def courses(request):
    """
    Render the "find courses" page. If the marketing site is enabled, redirect
    to that. Otherwise, if subdomain branding is on, this is the university
    profile page. Otherwise, it's the edX courseware.views.views.courses page
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


def _render_footer_html(request, show_openedx_logo, include_dependencies):
    """Render the footer as HTML.

    Arguments:
        show_openedx_logo (bool): If True, include the OpenEdX logo in the rendered HTML.
        include_dependencies (bool): If True, include JavaScript and CSS dependencies.

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
            "copyright": "EdX, Open edX, and the edX and Open edX logos are \
                registered trademarks or trademarks of edX Inc."
        }


    Example: Retrieving the footer as HTML

        GET /api/branding/v1/footer
        Accepts: text/html


    Example: Including the footer with the "Powered by OpenEdX" logo

        GET /api/branding/v1/footer?show-openedx-logo=1
        Accepts: text/html


    Example: Retrieving the footer in a particular language

        GET /api/branding/v1/footer?language=en
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

    # Render the footer information based on the extension
    if 'text/html' in accepts or '*/*' in accepts:
        cache_key = u"branding.footer.{params}.html".format(
            params=urllib.urlencode({
                'language': language,
                'show_openedx_logo': show_openedx_logo,
                'include_dependencies': include_dependencies,
            })
        )
        content = cache.get(cache_key)
        if content is None:
            with translation.override(language):
                content = _render_footer_html(request, show_openedx_logo, include_dependencies)
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
