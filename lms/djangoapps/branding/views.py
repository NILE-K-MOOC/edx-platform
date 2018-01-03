# -*- coding: utf-8 -*-
"""Views for the branding app. """
import logging
import urllib
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, Http404
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
<<<<<<< HEAD
import sys
import json
import MySQLdb as mdb
=======
>>>>>>> origin

log = logging.getLogger(__name__)


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
<<<<<<< HEAD
            ]
=======
        ]
>>>>>>> origin
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
<<<<<<< HEAD

=======
>>>>>>> origin
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

    # we do not expect this case to be reached in cases where
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
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'), settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'), settings.DATABASES.get('default').get('NAME'));
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

    # we do not expect this case to be reached in cases where
    #  marketing is enabled or the courses are not browsable

    return courseware.views.views.courses(request)

@ensure_csrf_cookie
@cache_if_anonymous()
def mobile_courses(request):
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


from django.db import connections
from pymongo import MongoClient
from bson.objectid import ObjectId
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse
import json


def course_api(request):
    mongo_course_info = {}
    json_list = list()

    lms_base = 'http://' + settings.ENV_TOKENS.get("LMS_BASE")

    if lms_base.find("http://") < 0:
        lms_base = 'http://' + lms_base

    # mysql
    with connections['default'].cursor() as cur, MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'), settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port')) as client:

        print 'get mysql info.'
        sql = '''
            SELECT coc.id                           AS course_id,
                   coc.display_name,
                   coc.start                        AS start_time,
                   coc.end                          AS end_time,
                   coc.enrollment_start             AS enroll_start,
                   coc.enrollment_end               AS enroll_end,
                   coc.created,
                   coc.modified,
                   replace(coc.course_video_url,
                           'www.youtube.com/watch?v=',
                           'www.youtube.com/embed/')
                      AS video,
                   coc.course_image_url             AS img,
                   coc.org,
                   coc.course,
                   Substring_index(coc.id, '+', -1) AS RUN,
                   coc.effort,
                   c.cert_date,
                   coa.name                         AS teacher_name
              FROM (  SELECT a.id,
                             a.display_name,
                             a.start,
                             a.end,
                             a.enrollment_start,
                             a.enrollment_end,
                             a.created,
                             a.modified,
                             a.course_video_url,
                             a.course_image_url,
                             a.effort,
                             CASE
                                WHEN     a.org = @org
                                     AND a.display_number_with_default = @course
                                THEN
                                   @rn := @rn + 1
                                ELSE
                                   @rn := 1
                             END
                                rn,
                             @org := a.org                          org,
                             @course := a.display_number_with_default`course`
                        FROM course_overviews_courseoverview a,
                             (SELECT @rn := 0, @org := 0, @course := 0) b
                       WHERE a.start < a.end
                    ORDER BY a.org, a.display_number_with_default, a.start DESC) coc
                   LEFT OUTER JOIN (  SELECT course_id, Min(created_date) AS cert_date
                                        FROM edxapp.certificates_generatedcertificate
                                    GROUP BY course_id) AS c
                      ON coc.id = c.course_id
                   LEFT JOIN
                   (  SELECT group_concat(c.name) AS name, course_id
                        FROM student_courseaccessrole a, auth_user b, auth_userprofile c
                       WHERE a.user_id = b.id AND role = 'instructor' AND b.id = c.user_id
                    GROUP BY course_id) coa
                      ON coc.id = coa.course_id
             WHERE rn = 1;
        '''
        cur.execute(sql)
        rows = cur.fetchall()

        course_ids = [row[0] for row in rows]

        columns = [desc[0] for desc in cur.description]
        courses = [dict(zip(columns, (str(r) for r in row))) for row in rows]

        # print 'len(courses):', len(courses)

        print 'get mongo info.'

        db = client.edxapp
        cursors = db.modulestore.active_versions.find({"run": {"$ne": "library"}}, {"_id": 0, "versions.published-branch": 1, "org": 1, "course": 1, "run": 1})
        for cursor in cursors:
            _org = cursor.get('org')
            _course = cursor.get('course')
            _run = cursor.get('run')

            _course_id = 'course-v1:{org}+{course}+{run}'.format(
                org=_org,
                course=_course,
                run=_run,
            )

            if _course_id not in course_ids:
                continue

            pb = cursor.get('versions').get('published-branch')
            course = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"_id": 0, "blocks": {"$elemMatch": {"block_type": "course"}}})
            block = course.get('blocks')[0]
            fields = block.get('fields')
            classfy = fields.get('classfy') if 'classfy' in fields else ''
            middle_classfy = fields.get('middle_classfy') if 'middle_classfy' in fields else ''

            mongo_course_info[_course_id] = {
                'classfy': classfy,
                'middle_classfy': middle_classfy
            }

        # print 'len(mongo_course_info):', len(mongo_course_info)

        for course in courses:
            _course_id = course['course_id']
            course['univ_name'] = str(_(course['org']))
            course['img'] = lms_base + course['img']

            if _course_id in mongo_course_info:
                course['classfy'] = mongo_course_info[_course_id]['classfy']
                course['middle_classfy'] = mongo_course_info[_course_id]['middle_classfy']

            if 'effort' in course:
                effort = course['effort']

                if effort is None:
                    course['e0'] = 'null'
                    course['e1'] = 'null'
                    course['e2'] = 'null'
                    course['et'] = 'null'
                elif '@' in effort and '#' in effort:
                    tmp = effort.replace('@', '#')
                    tmp = tmp.split('#')
                    t = tmp[0].split(':')
                    tt = ((int(t[0]) * 60) + int(t[1])) * int(tmp[1])
                    th = tt / 60
                    tm = tt % 60
                    if len(str(th)) == 1:
                        th = "0" + str(th)
                    if len(str(tm)) == 1:
                        tm = "0" + str(tm)
                    total_time = str(th) + ":" + str(tm)
                    course['e0'] = tmp[0]
                    course['e1'] = tmp[1]
                    course['e2'] = tmp[2]
                    course['et'] = total_time
                elif '@' in effort:
                    tmp = effort
                    tmp = tmp.split('@')
                    course['e0'] = tmp[0]
                    course['e1'] = tmp[1]
                    course['e2'] = 'null'
                    t = tmp[0].split(':')
                    tt = ((int(t[0]) * 60) + int(t[1])) * int(tmp[1])
                    th = tt / 60
                    tm = tt % 60
                    if len(str(th)) == 1:
                        th = "0" + str(th)
                    if len(str(tm)) == 1:
                        tm = "0" + str(tm)
                    total_time = str(th) + ":" + str(tm)
                    course['et'] = total_time
                elif '#' in effort:
                    tmp = effort
                    tmp = tmp.split('#')
                    course['e0'] = tmp[0]
                    course['e1'] = 'null'
                    course['e2'] = 'null'
                    course['et'] = 'null'

            # 전부 없는 로직 ex)
            else:
                course['e0'] = 'null'
                course['e1'] = 'null'
                course['e2'] = 'null'
                course['et'] = 'null'

            json_list.append(course)

        result = {
            "results": json_list,
            "total_cnt": len(json_list)
        }

        print 'return api courses'

    return HttpResponse(json.dumps(result, ensure_ascii=False))


def common_course_status(startDt, endDt):
    # input
    # startDt = 2016-12-19 00:00:00
    # endDt   = 2017-02-10 23:00:00
    # nowDt   = 2017-11-10 00:11:28

    # import
    from datetime import datetime
    from django.utils.timezone import UTC as UTC2

    # making nowDt
    # nowDt = datetime.now(UTC2()).strftime("%Y-%m-%d-%H-%m-%S")
    startDt = startDt.strftime("%Y%m%d%H%m%S")
    endDt = endDt.strftime("%Y%m%d%H%m%S")
    nowDt = datetime.now(UTC2()).strftime("%Y%m%d%H%m%S")
    # nowDt = nowDt.split('-')
    # nowDt = datetime(int(nowDt[0]), int(nowDt[1]), int(nowDt[2]), int(nowDt[3]), int(nowDt[4]), int(nowDt[5]))

    # logic
    if startDt is None or startDt == '' or endDt is None or endDt == '':
        status = 'none'
    elif nowDt < startDt:
        status = 'ready'
    elif startDt <= nowDt <= endDt:
        status = 'ing'
    elif endDt < nowDt:
        status = 'end'
    else:
        status = 'none'

    # return status
    return status


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
