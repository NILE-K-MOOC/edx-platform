"""Views for the branding app. """
import logging
import urllib

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

import branding.api as branding_api
import courseware.views.views
import student.views.management
from edxmako.shortcuts import marketing_link, render_to_response
from openedx.core.djangoapps.lang_pref.api import released_languages
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from util.cache import cache_if_anonymous
from util.json_request import JsonResponse
from django.db import connections
from django.views.decorators.csrf import csrf_exempt

log = logging.getLogger(__name__)


@csrf_exempt
def series_cancel(request):

    id = request.POST.get('id')
    user_id = request.user.id

    with connections['default'].cursor() as cur:
        sql = '''
            update series_student
            set delete_yn = 'Y'
            where user_id = '{user_id}'
            and series_seq in (
                select series_seq
                from series
                where series_id = '{id}'
            );
        '''.format(user_id=user_id, id=id)

        print sql
        cur.execute(sql)

    return JsonResponse({'result':'success'})


def new_dashboard(request):

    user_id = request.user.id

    with connections['default'].cursor() as cur:
        sql = '''
            select y.series_seq, y.series_id, y.series_name, y.save_path, y.detail_name
            from series_student x
            join (
            select a.series_seq, a.series_id, a.series_name, b.save_path, c.detail_name
            from series a
            left join tb_attach b
            on a.sumnail_file_id = id
            join code_detail c
            on a.org = c.detail_code
            where c.group_code = '003'
            ) y
            on x.series_seq = y.series_seq
            where x.user_id = '{user_id}'
            and x.delete_yn = 'N';
        '''.format(user_id=user_id)

        print sql
        cur.execute(sql)
        temps = cur.fetchall()

    packages = []
    for temp in temps:
        tmp_dict = {}
        tmp_dict['series_seq'] = temp[0]
        tmp_dict['series_id'] = temp[1]
        tmp_dict['series_name'] = temp[2]
        tmp_dict['save_path'] = temp[3]
        tmp_dict['detail_name'] = temp[4]

        with connections['default'].cursor() as cur:
            sql1 = '''
                select sum(result)
                from (
                select x.org, x.display_number_with_default, case when status is not null then sum(1) when status is null then sum(0) end as result
                from (
                select org, display_number_with_default
                from series_course
                where series_seq = '{series_seq}'
                ) x
                left join (
                select a.org, a.display_number_with_default, b.status
                from course_overviews_courseoverview a
                join certificates_generatedcertificate b
                on b.course_id = a.id
                where b.user_id = '{user_id}'
                ) y
                on x.org = y.org
                and x.display_number_with_default = y.display_number_with_default
                group by x.org, x.display_number_with_default
                ) xxx
            '''.format(series_seq=temp[0],
                       user_id=user_id)

            print sql1
            cur.execute(sql1)
            is_cert = cur.fetchall()[0][0]

            sql2 = '''
                select sum(result)
                from (
                select t1.org, t1.display_number_with_default, case when t2.id is not null then sum(1) when t2.id is null then sum(0) end as result
                from (
                  select org, display_number_with_default
                  from series_course
                  where series_seq = '{series_seq}'
                ) t1
                left join (
                  select *
                  from (
                      select id, org, display_number_with_default
                      from course_overviews_courseoverview
                      where start < now()
                      and end < now()
                  ) x
                  join (
                      select course_id
                      from student_courseenrollment
                      where user_id = '{user_id}'
                      and mode = 'honor'
                  ) y
                  on x.id = y.course_id
                )t2
                on t1.org = t2.org
                and t1.display_number_with_default = t2.display_number_with_default
                group by t1.org, t1.display_number_with_default
                ) xxx;
                    '''.format(series_seq=temp[0],
                               user_id=user_id)

            print sql2
            cur.execute(sql2)
            is_ing = cur.fetchall()[0][0]

            sql3 = '''
                select count(*)
                from series_course
                where series_seq = '{series_seq}';
            '''.format(series_seq=temp[0],
                       user_id=user_id)

            print sql3
            cur.execute(sql3)
            is_total = cur.fetchall()[0][0]

        if is_cert == None:
            is_cert = 0

        if is_ing == None:
            is_ing = 0

        print "is_cert -> ", is_cert
        print "is_ing -> ", is_ing
        print "is_total -> ", is_total

        print "type is_cert -> ", type(is_cert)
        print "type is_ing -> ", type(is_ing)
        print "type is_total -> ", type(is_total)

        tmp_dict['is_cert'] = is_cert
        tmp_dict['is_ing'] = is_ing
        tmp_dict['is_noing'] = is_total - is_ing
        packages.append(tmp_dict)

    print packages

    context = {}
    context['packages'] = packages
    return render_to_response("new_dashboard.html", context)

def get_multisite_list(request):

    user_id = request.POST.get('user_id')

    with connections['default'].cursor() as cur:
        sql = '''
            SELECT site_code, org_user_id
            FROM multisite_member AS a
            JOIN multisite AS b
            ON a.site_id = b.site_id
            WHERE user_id = {user_id}
        '''.format(user_id = user_id)

        print sql

        cur.execute(sql)
        rows = cur.fetchall()

    if len(rows) == 0:
        return JsonResponse({'return':'zero'})

    print "------------------------> hello s"
    print "user_id = ", user_id
    print "------------------------> hello e"

    return JsonResponse({'return':rows})

    return JsonResponse({'':''})


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

    return JsonResponse({'result':org_list, 'count':org_count})


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
        '''.format(org = org, user_id = user_id)

        print sql

        cur.execute(sql)

    return JsonResponse({'return':'success'})

@ensure_csrf_cookie
@transaction.non_atomic_requests
@cache_if_anonymous()
def index(request):
    """
    Redirects to main page -- info page if user authenticated, or marketing if not
    """
    print "request.user.is_authenticated",request.user.is_authenticated
    if request.user.is_authenticated:
        # Only redirect to dashboard if user has
        # courses in his/her dashboard. Otherwise UX is a bit cryptic.
        # In this case, we want to have the user stay on a course catalog
        # page to make it easier to browse for courses (and register)
        if configuration_helpers.get_value(
                'ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER',
                settings.FEATURES.get('ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER', True)):
            #return redirect(reverse('dashboard'))
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
