# -*- coding: utf-8 -*-
import logging
import urllib
import requests
import analytics
import bleach
import shoppingcart
import survey.views
import MySQLdb as mdb
import sys
import json
import crum
import pytz
from collections import OrderedDict, namedtuple
from datetime import datetime, date,timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.context_processors import csrf
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlquote_plus
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.views.generic import View
from markupsafe import escape
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey
from pytz import UTC
from rest_framework import status
from six import text_type
from web_fragments.fragment import Fragment
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from util.json_request import JsonResponse
from django.db import connections
from course_modes.models import CourseMode, get_course_prices
from courseware.access import has_access, has_ccx_coach_role
from courseware.access_utils import check_course_open_for_learner
from courseware.courses import (
    can_self_enroll_in_course,
    course_open_for_self_enrollment,
    get_course,
    get_course_overview_with_access,
    get_course_with_access,
    get_courses,
    get_current_child,
    get_permission_for_course_about,
    get_studio_url,
    sort_by_announcement,
    sort_by_start_date
)
from courseware.masquerade import setup_masquerade
from courseware.model_data import FieldDataCache
from courseware.models import BaseStudentModuleHistory, StudentModule, CodeDetail, Multisite, MultisiteMember
from kotech_community.models import TbAttach
from courseware.url_helpers import get_redirect_url
from courseware.user_state_client import DjangoXBlockUserStateClient
from edxmako.shortcuts import marketing_link, render_to_response, render_to_string
from enrollment.api import add_enrollment
from ipware.ip import get_ip
from lms.djangoapps.ccx.custom_exception import CCXLocatorValidationException
from lms.djangoapps.certificates import api as certs_api
from lms.djangoapps.certificates.models import CertificateStatuses
from lms.djangoapps.commerce.utils import EcommerceService
from lms.djangoapps.courseware.exceptions import CourseAccessRedirect, Redirect
from lms.djangoapps.experiments.utils import get_experiment_user_metadata_context
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from lms.djangoapps.instructor.enrollment import uses_shib
from lms.djangoapps.instructor.views.api import require_global_staff
from lms.djangoapps.verify_student.services import IDVerificationService
from openedx.core.djangoapps.catalog.utils import get_programs, get_programs_with_type
from openedx.core.djangoapps.certificates import api as auto_certs_api
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.credit.api import (
    get_credit_requirement_status,
    is_credit_course,
    is_user_eligible_for_credit
)
from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.core.djangoapps.monitoring_utils import set_custom_metrics_for_course_key
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from openedx.core.djangoapps.programs.utils import ProgramMarketingDataExtender
from openedx.core.djangoapps.self_paced.models import SelfPacedConfiguration
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.util.user_messages import PageLevelMessages
from openedx.core.djangolib.markup import HTML, Text
from openedx.features.course_experience import UNIFIED_COURSE_TAB_FLAG, course_home_url_name
from openedx.features.course_experience.course_tools import CourseToolsPluginManager
from openedx.features.course_experience.views.course_dates import CourseDatesFragmentView
from openedx.features.course_experience.waffle import ENABLE_COURSE_ABOUT_SIDEBAR_HTML
from openedx.features.course_experience.waffle import waffle as course_experience_waffle
from openedx.features.enterprise_support.api import data_sharing_consent_required
from shoppingcart.utils import is_shopping_cart_enabled
from student.models import CourseEnrollment, UserTestGroup
from util.cache import cache, cache_if_anonymous
from util.db import outer_atomic
from util.milestones_helpers import get_prerequisite_courses_display
from util.views import _record_feedback_in_zendesk, ensure_valid_course_key, ensure_valid_usage_key
from web_fragments.fragment import Fragment
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError, NoPathToItem
from xmodule.tabs import CourseTabList
from xmodule.x_module import STUDENT_VIEW
from ..entrance_exams import user_can_skip_entrance_exam
from ..module_render import get_module, get_module_by_usage_id, get_module_for_descriptor
from ..context_processor import user_timezone_locale_prefs
from pytz import timezone
from urlparse import urlparse, parse_qs
import traceback
from django.core.exceptions import ObjectDoesNotExist
from pymongo import MongoClient
from bson import ObjectId

log = logging.getLogger("edx.courseware")

# Only display the requirements on learner dashboard for
# credit and verified modes.
REQUIREMENTS_DISPLAY_MODES = CourseMode.CREDIT_MODES + [CourseMode.VERIFIED]

CertData = namedtuple(
    "CertData", ["cert_status", "title", "msg", "download_url", "cert_web_view_url"]
)

AUDIT_PASSING_CERT_DATA = CertData(
    CertificateStatuses.audit_passing,
    _('Your enrollment: Audit track'),
    _('You are enrolled in the audit track for this course. The audit track does not include a certificate.'),
    download_url=None,
    cert_web_view_url=None
)

HONOR_PASSING_CERT_DATA = CertData(
    CertificateStatuses.honor_passing,
    _('Your enrollment: Honor track'),
    # _('You are enrolled in the honor track for this course. The honor track does not include a certificate.'),
    _(''),
    download_url=None,
    cert_web_view_url=None
)

GENERATING_CERT_DATA = CertData(
    CertificateStatuses.generating,
    _("We're working on it..."),
    _(
        "We're creating your certificate. You can keep working in your courses and a link "
        "to it will appear here and on your Dashboard when it is ready."
    ),
    download_url=None,
    cert_web_view_url=None
)

INVALID_CERT_DATA = CertData(
    CertificateStatuses.invalidated,
    _('Your certificate has been invalidated'),
    _('Please contact your course team if you have any questions.'),
    download_url=None,
    cert_web_view_url=None
)

REQUESTING_CERT_DATA = CertData(
    CertificateStatuses.requesting,
    _('Congratulations, you qualified for a certificate!'),
    _("You've earned a certificate for this course."),
    download_url=None,
    cert_web_view_url=None
)

UNVERIFIED_CERT_DATA = CertData(
    CertificateStatuses.unverified,
    _('Certificate unavailable'),
    _(
        'You have not received a certificate because you do not have a current {platform_name} '
        'verified identity.'
    ).format(platform_name=configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)),
    download_url=None,
    cert_web_view_url=None
)


def _downloadable_cert_data(download_url=None, cert_web_view_url=None):
    return CertData(
        CertificateStatuses.downloadable,
        _('Your certificate is available'),
        _("You've earned a certificate for this course."),
        download_url=download_url,
        cert_web_view_url=cert_web_view_url
    )


def user_groups(user):
    """
    TODO (vshnayder): This is not used. When we have a new plan for groups, adjust appropriately.
    """
    if not user.is_authenticated:
        return []

    # TODO: Rewrite in Django
    key = 'user_group_names_{user.id}'.format(user=user)
    cache_expiration = 60 * 60  # one hour

    # Kill caching on dev machines -- we switch groups a lot
    group_names = cache.get(key)  # pylint: disable=no-member
    if settings.DEBUG:
        group_names = None

    if group_names is None:
        group_names = [u.name for u in UserTestGroup.objects.filter(users=user)]
        cache.set(key, group_names, cache_expiration)  # pylint: disable=no-member

    return group_names


@ensure_csrf_cookie
@cache_if_anonymous()
def search_org_name(request):
    org_names = CodeDetail.objects.filter(group_code='003', use_yn='Y', delete_yn='N')
    if request.LANGUAGE_CODE == 'ko-kr':
        org_dict = [{org.detail_code: org.detail_name} for org in org_names]
    else:
        org_dict = [{org.detail_code: org.detail_ename} for org in org_names]

    context = {'org_dict': org_dict}
    return JsonResponse(context)


@ensure_csrf_cookie
@cache_if_anonymous()
def courses(request):
    """
    Render "find courses" page.  The course selection work is done in courseware.courses.
    수정시 mobile_courses도 함께 수정
    """
    courses_list = []
    course_discovery_meanings = getattr(settings, 'COURSE_DISCOVERY_MEANINGS', {})
    if not settings.FEATURES.get('ENABLE_COURSE_DISCOVERY'):
        courses_list = get_courses(request.user)

        if configuration_helpers.get_value("ENABLE_COURSE_SORTING_BY_START_DATE",
                                           settings.FEATURES["ENABLE_COURSE_SORTING_BY_START_DATE"]):
            courses_list = sort_by_start_date(courses_list)
        else:
            courses_list = sort_by_announcement(courses_list)

    import time
    try:
        from urllib import urlencode
    except ImportError:
        CourseDescriptorWithMixins

    from elasticsearch.exceptions import ConnectionError
    from elasticsearch.connection.http_urllib3 import Urllib3HttpConnection

    def perform_request(self, method, url, params=None, body=None, timeout=None, ignore=()):

        print '##### perform_request called 111'
        log.info('##### perform_request called 111')

        url = self.url_prefix + url
        if 'size' in params:
            params['sort'] = '_score:desc,enrollment_start:desc,start:desc,enrollment_end:desc,end:desc,display_name:asc'

        if params:
            url = '%s?%s' % (url, urlencode(params or {}))
        full_url = self.host + url

        start = time.time()

        if body:

            log.info('##### body ------------------------------------------------------- s1')
            log.info(body)
            log.info('##### body ------------------------------------------------------- e1')

            if '{"term": {"org": "SMUk"}}' in body:
                body = body.replace('{"term": {"org": "SMUk"}}', '{"terms": {"org": ["SMUk", "SMUCk"]}}')

            if '{"term": {"linguistics": "all"}' in body:
                body = body.replace('{"term": {"linguistics": "all"}', '{"terms": {"linguistics": ["Korean", "Korean Culture"]}')

            log.info('##### body ------------------------------------------------------- s2')
            log.info(body)
            log.info('##### body ------------------------------------------------------- e2')

        try:
            kw = {}
            if timeout:
                kw['timeout'] = timeout
            response = self.pool.urlopen(method, url, body, **kw)
            duration = time.time() - start
            raw_data = response.data.decode('utf-8')
        except Exception as e:
            self.log_request_fail(method, full_url, body, time.time() - start, exception=e)
            raise ConnectionError('N/A', str(e), e)

        if not (200 <= response.status < 300) and response.status not in ignore:
            self.log_request_fail(method, url, body, duration, response.status)
            self._raise_error(response.status, raw_data)

        self.log_request_success(method, full_url, url, body, response.status,
                                 raw_data, duration)

        return response.status, response.getheaders(), raw_data

    Urllib3HttpConnection.perform_request = perform_request

    # Add marketable programs to the context.
    programs_list = get_programs_with_type(request.site, include_hidden=False)

    # course post parameter setting to html
    parameter_list = ['job_edu_yn', 'fourth_industry_yn', 'ribbon_yn', 'linguistics', 'linguistics_yn', 'classfy', 'middle_classfy', 'ai_sec_yn', 'basic_science_sec_yn']
    parameter_json = {key: str(request.POST.get(key)) for key in parameter_list if key in request.POST}

    return render_to_response(
        "courseware/courses.html",
        {
            'courses': courses_list,
            'course_discovery_meanings': course_discovery_meanings,
            'programs_list': programs_list,
            'parameter_json': parameter_json
        }
    )


@ensure_csrf_cookie
# @cache_if_anonymous()
def mobile_courses(request):
    """
    Render "find courses" page.  The course selection work is done in courseware.courses.
    """
    courses_list = []
    course_discovery_meanings = getattr(settings, 'COURSE_DISCOVERY_MEANINGS', {})
    if not settings.FEATURES.get('ENABLE_COURSE_DISCOVERY'):
        courses_list = get_courses(request.user)

        if configuration_helpers.get_value("ENABLE_COURSE_SORTING_BY_START_DATE",
                                           settings.FEATURES["ENABLE_COURSE_SORTING_BY_START_DATE"]):
            courses_list = sort_by_start_date(courses_list)
        else:
            courses_list = sort_by_announcement(courses_list)
    import time
    try:
        from urllib import urlencode
    except ImportError:
        CourseDescriptorWithMixins

    from elasticsearch.exceptions import ConnectionError
    from elasticsearch.connection.http_urllib3 import Urllib3HttpConnection

    def perform_request(self, method, url, params=None, body=None, timeout=None, ignore=()):

        print '##### perform_request called 2'

        url = self.url_prefix + url
        if 'size' in params:
            params['sort'] = '_score:desc,enrollment_start:desc,start:desc,enrollment_end:desc,end:desc,display_name:asc'

        if params:
            url = '%s?%s' % (url, urlencode(params or {}))
        full_url = self.host + url

        start = time.time()

        if body:
            if '{"term": {"org": "SMUk"}}' in body:
                body = body.replace('{"term": {"org": "SMUk"}}', '{"terms": {"org": ["SMUk", "SMUCk"]}}')

        try:
            kw = {}
            if timeout:
                kw['timeout'] = timeout
            response = self.pool.urlopen(method, url, body, **kw)
            duration = time.time() - start
            raw_data = response.data.decode('utf-8')
        except Exception as e:
            self.log_request_fail(method, full_url, body, time.time() - start, exception=e)
            raise ConnectionError('N/A', str(e), e)

        if not (200 <= response.status < 300) and response.status not in ignore:
            self.log_request_fail(method, url, body, duration, response.status)
            self._raise_error(response.status, raw_data)

        self.log_request_success(method, full_url, url, body, response.status,
                                 raw_data, duration)

        return response.status, response.getheaders(), raw_data

    Urllib3HttpConnection.perform_request = perform_request
    # Add marketable programs to the context.
    programs_list = get_programs_with_type(request.site, include_hidden=False)

    # course post parameter setting to html
    parameter_list = ['job_edu_yn', 'fourth_industry_yn', 'ribbon_yn', 'linguistics', 'linguistics_yn', 'classfy', 'middle_classfy', 'ai_sec_yn', 'basic_science_sec_yn']
    parameter_json = {key: str(request.POST.get(key)) for key in parameter_list if key in request.POST}

    return render_to_response(
        "mobile_main.html",
        {
            'courses': courses_list,
            'course_discovery_meanings': course_discovery_meanings,
            'programs_list': programs_list,
            'parameter_json': parameter_json,
            'mobile_title': '강좌 찾기',
            'mobile_template': 'mobile_courses'
        }
    )


@ensure_csrf_cookie
@ensure_valid_course_key
def jump_to_id(request, course_id, module_id):
    """
    This entry point allows for a shorter version of a jump to where just the id of the element is
    passed in. This assumes that id is unique within the course_id namespace
    """
    course_key = CourseKey.from_string(course_id)
    items = modulestore().get_items(course_key, qualifiers={'name': module_id})

    if len(items) == 0:
        raise Http404(
            u"Could not find id: {0} in course_id: {1}. Referer: {2}".format(
                module_id, course_id, request.META.get("HTTP_REFERER", "")
            ))
    if len(items) > 1:
        log.warning(
            u"Multiple items found with id: %s in course_id: %s. Referer: %s. Using first: %s",
            module_id,
            course_id,
            request.META.get("HTTP_REFERER", ""),
            text_type(items[0].location)
        )

    return jump_to(request, course_id, text_type(items[0].location))


@ensure_csrf_cookie
def jump_to(_request, course_id, location):
    """
    Show the page that contains a specific location.
    If the location is invalid or not in any class, return a 404.
    Otherwise, delegates to the index view to figure out whether this user
    has access, and what they should see.
    """
    try:
        course_key = CourseKey.from_string(course_id)
        usage_key = UsageKey.from_string(location).replace(course_key=course_key)
    except InvalidKeyError:
        raise Http404(u"Invalid course_key or usage_key")
    try:
        redirect_url = get_redirect_url(course_key, usage_key)
    except ItemNotFoundError:
        raise Http404(u"No data at this location: {0}".format(usage_key))
    except NoPathToItem:
        raise Http404(u"This location is not in any class: {0}".format(usage_key))

    return redirect(redirect_url)


@ensure_csrf_cookie
@ensure_valid_course_key
@data_sharing_consent_required
def course_info(request, course_id):
    """
    Display the course's info.html, or 404 if there is no such course.
    Assumes the course_id is in a valid format.
    """

    # TODO: LEARNER-611: This can be deleted with Course Info removal.  The new
    #    Course Home is using its own processing of last accessed.
    def get_last_accessed_courseware(course, request, user):
        """
        Returns the courseware module URL that the user last accessed, or None if it cannot be found.
        """
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course.id, request.user, course, depth=2
        )
        course_module = get_module_for_descriptor(
            user, request, course, field_data_cache, course.id, course=course
        )
        chapter_module = get_current_child(course_module)
        if chapter_module is not None:
            section_module = get_current_child(chapter_module)
            if section_module is not None:
                url = reverse('courseware_section', kwargs={
                    'course_id': text_type(course.id),
                    'chapter': chapter_module.url_name,
                    'section': section_module.url_name
                })
                return url
        return None

    course_key = CourseKey.from_string(course_id)

    # If the unified course experience is enabled, redirect to the "Course" tab
    if UNIFIED_COURSE_TAB_FLAG.is_enabled(course_key):
        return redirect(reverse(course_home_url_name(course_key), args=[course_id]))

    with modulestore().bulk_operations(course_key):
        course = get_course_with_access(request.user, 'load', course_key)

        staff_access = has_access(request.user, 'staff', course)
        masquerade, user = setup_masquerade(request, course_key, staff_access, reset_masquerade_data=True)

        # LEARNER-612: CCX redirect handled by new Course Home (DONE)
        # LEARNER-1697: Transition banner messages to new Course Home (DONE)
        # if user is not enrolled in a course then app will show enroll/get register link inside course info page.
        user_is_enrolled = CourseEnrollment.is_enrolled(user, course.id)
        show_enroll_banner = request.user.is_authenticated and not user_is_enrolled

        # If the user is not enrolled but this is a course that does not support
        # direct enrollment then redirect them to the dashboard.
        if not user_is_enrolled and not can_self_enroll_in_course(course_key):
            return redirect(reverse('dashboard'))

        # LEARNER-170: Entrance exam is handled by new Course Outline. (DONE)
        # If the user needs to take an entrance exam to access this course, then we'll need
        # to send them to that specific course module before allowing them into other areas
        if not user_can_skip_entrance_exam(user, course):
            return redirect(reverse('courseware', args=[text_type(course.id)]))

        # TODO: LEARNER-611: Remove deprecated course.bypass_home.
        # If the user is coming from the dashboard and bypass_home setting is set,
        # redirect them straight to the courseware page.
        is_from_dashboard = reverse('dashboard') in request.META.get('HTTP_REFERER', [])
        if course.bypass_home and is_from_dashboard:
            return redirect(reverse('courseware', args=[course_id]))

        # Construct the dates fragment
        dates_fragment = None

        if request.user.is_authenticated:
            # TODO: LEARNER-611: Remove enable_course_home_improvements
            if SelfPacedConfiguration.current().enable_course_home_improvements:
                # Shared code with the new Course Home (DONE)
                dates_fragment = CourseDatesFragmentView().render_to_fragment(request, course_id=course_id)

        # This local import is due to the circularity of lms and openedx references.
        # This may be resolved by using stevedore to allow web fragments to be used
        # as plugins, and to avoid the direct import.
        from openedx.features.course_experience.views.course_reviews import CourseReviewsModuleFragmentView

        # Shared code with the new Course Home (DONE)
        # Get the course tools enabled for this user and course
        course_tools = CourseToolsPluginManager.get_enabled_course_tools(request, course_key)

        course_homepage_invert_title = \
            configuration_helpers.get_value(
                'COURSE_HOMEPAGE_INVERT_TITLE',
                False
            )

        course_homepage_show_subtitle = \
            configuration_helpers.get_value(
                'COURSE_HOMEPAGE_SHOW_SUBTITLE',
                True
            )

        course_homepage_show_org = \
            configuration_helpers.get_value('COURSE_HOMEPAGE_SHOW_ORG', True)

        course_title = course.display_number_with_default
        course_subtitle = course.display_name_with_default
        if course_homepage_invert_title:
            course_title = course.display_name_with_default
            course_subtitle = course.display_number_with_default

        context = {
            'request': request,
            'masquerade_user': user,
            'course_id': text_type(course_key),
            'url_to_enroll': CourseTabView.url_to_enroll(course_key),
            'cache': None,
            'course': course,
            'course_title': course_title,
            'course_subtitle': course_subtitle,
            'show_subtitle': course_homepage_show_subtitle,
            'show_org': course_homepage_show_org,
            'staff_access': staff_access,
            'masquerade': masquerade,
            'supports_preview_menu': True,
            'studio_url': get_studio_url(course, 'course_info'),
            'show_enroll_banner': show_enroll_banner,
            'user_is_enrolled': user_is_enrolled,
            'dates_fragment': dates_fragment,
            'course_tools': course_tools,
        }
        context.update(
            get_experiment_user_metadata_context(
                course,
                user,
            )
        )

        # Get the URL of the user's last position in order to display the 'where you were last' message
        context['resume_course_url'] = None
        # TODO: LEARNER-611: Remove enable_course_home_improvements
        if SelfPacedConfiguration.current().enable_course_home_improvements:
            context['resume_course_url'] = get_last_accessed_courseware(course, request, user)

        if not check_course_open_for_learner(user, course):
            # Disable student view button if user is staff and
            # course is not yet visible to students.
            context['disable_student_access'] = True
            context['supports_preview_menu'] = False
        course_id = request.POST.get('course_id')

        return render_to_response('courseware/info.html', context)


class StaticCourseTabView(EdxFragmentView):
    """
    View that displays a static course tab with a given name.
    """

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(ensure_valid_course_key)
    def get(self, request, course_id, tab_slug, **kwargs):
        """
        Displays a static course tab page with a given name
        """
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, 'load', course_key)
        tab = CourseTabList.get_tab_by_slug(course.tabs, tab_slug)
        if tab is None:
            raise Http404

        # Show warnings if the user has limited access
        CourseTabView.register_user_access_warning_messages(request, course_key)

        return super(StaticCourseTabView, self).get(request, course=course, tab=tab, **kwargs)

    def render_to_fragment(self, request, course=None, tab=None, **kwargs):
        """
        Renders the static tab to a fragment.
        """
        return get_static_tab_fragment(request, course, tab)

    def render_standalone_response(self, request, fragment, course=None, tab=None, **kwargs):
        """
        Renders this static tab's fragment to HTML for a standalone page.
        """
        return render_to_response('courseware/static_tab.html', {
            'course': course,
            'active_page': 'static_tab_{0}'.format(tab['url_slug']),
            'tab': tab,
            'fragment': fragment,
            'uses_pattern_library': False,
            'disable_courseware_js': True,
        })


class CourseTabView(EdxFragmentView):
    """
    View that displays a course tab page.
    """

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(ensure_valid_course_key)
    @method_decorator(data_sharing_consent_required)
    def get(self, request, course_id, tab_type, **kwargs):
        """
        Displays a course tab page that contains a web fragment.
        """
        course_key = CourseKey.from_string(course_id)

        encStr = request.GET.get('encStr')
        org = request.GET.get('org')

        # encStr 이 있을 경우 멀티사이트에서 온것으로 보고, 멀티사이트 복호화를 수행하고, 로그인 처리를 하도록 함
        if org and encStr:
            from branding.views import decrypt, login

            try:
                multisite = Multisite.objects.get(site_code=org)
                key = multisite.encryption_key
                logo_img_id = multisite.logo_img

                try:
                    raw_data = decrypt(key, key, encStr)
                except Exception as e:
                    raw_data = None
                    log.info(traceback.format_exc(e))

                if raw_data:
                    user_id = None
                    params = parse_qs(raw_data)

                    site_id = multisite.site_id
                    org_user_id = params.get('userid')

                    # parse_qs 자체는 value 를 리스트로 변환하여 반환하기 때문에 다음의 코드가 필요
                    if org_user_id:
                        org_user_id = org_user_id[0]

                    # org 와 기관내 사번으로 등록된 사용자가 있는지 확인하여 없다면 등록을 위해 세션에 정보 저장

                    if org:
                        request.session['multisite_org'] = org

                    if org_user_id:
                        request.session['multisite_userid'] = org_user_id

                    try:
                        # multisite_member 에 사번과 동일한 사용자가 있는지 확인. params.get('user_id') 의 값은 기관의 사번
                        multisite_member = MultisiteMember.objects.get(site_id=site_id, org_user_id=org_user_id)
                        user_id = multisite_member.user_id

                    except ObjectDoesNotExist as e3:
                        # 데이터가 없다면 세션에 정보를 저장
                        log.info('CourseTabView ObjectDoesNotExist [%s]' % e3.message)

                        # save_path 도 세션에 저장
                        # '/static/images/no_images_large.png'

                        # 로그인 화면으로 리다이렉트
                        from student.helpers import get_next_url_for_login_page

                        redirect_url = get_next_url_for_login_page(request)

                        path = str(request.path)
                        # return redirect('/login?next=' + urllib.urlencode(path))
                        enc_path = urllib.quote_plus(path)
                        return redirect('/login?next=' + enc_path)

                        # traceback.format_exc(e)

                    except Exception as e4:
                        log.info('CourseTabView Exception [%s]' % e4.message)

                    if user_id and not request.user.is_authenticated:
                        user = User.objects.get(pk=user_id)
                        user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
                        login(request, user)

                    pass

            except ObjectDoesNotExist as e:
                pass
            except Exception as e1:
                pass

        with modulestore().bulk_operations(course_key):
            course = get_course_with_access(request.user, 'load', course_key)
            try:
                # Render the page
                tab = CourseTabList.get_tab_by_type(course.tabs, tab_type)
                page_context = self.create_page_context(request, course=course, tab=tab, **kwargs)

                # Show warnings if the user has limited access
                # Must come after masquerading on creation of page context
                self.register_user_access_warning_messages(request, course_key)

                set_custom_metrics_for_course_key(course_key)
                return super(CourseTabView, self).get(request, course=course, page_context=page_context, **kwargs)
            except Exception as exception:  # pylint: disable=broad-except
                return CourseTabView.handle_exceptions(request, course, exception)

    @staticmethod
    def url_to_enroll(course_key):
        """
        Returns the URL to use to enroll in the specified course.
        """
        url_to_enroll = reverse('about_course', args=[text_type(course_key)])
        if settings.FEATURES.get('ENABLE_MKTG_SITE'):
            url_to_enroll = marketing_link('COURSES')
        return url_to_enroll

    @staticmethod
    def register_user_access_warning_messages(request, course_key):
        """
        Register messages to be shown to the user if they have limited access.
        """
        if request.user.is_anonymous:
            PageLevelMessages.register_warning_message(
                request,
                Text(_("To see course content, {sign_in_link} or {register_link}.")).format(
                    sign_in_link=HTML('<a href="/login?next={current_url}">{sign_in_label}</a>').format(
                        sign_in_label=_("sign in"),
                        current_url=urlquote_plus(request.path),
                    ),
                    register_link=HTML('<a href="/register?next={current_url}">{register_label}</a>').format(
                        register_label=_("register"),
                        current_url=urlquote_plus(request.path),
                    ),
                )
            )
        else:
            if not CourseEnrollment.is_enrolled(request.user, course_key):
                # Only show enroll button if course is open for enrollment.
                if course_open_for_self_enrollment(course_key):
                    enroll_message = _('You must be enrolled in the course to see course content. \
                            {enroll_link_start}Enroll now{enroll_link_end}.')
                    PageLevelMessages.register_warning_message(
                        request,
                        Text(enroll_message).format(
                            enroll_link_start=HTML('<button class="enroll-btn btn-link">'),
                            enroll_link_end=HTML('</button>')
                        )
                    )
                else:
                    PageLevelMessages.register_warning_message(
                        request,
                        Text(_('You must be enrolled in the course to see course content.'))
                    )

    @staticmethod
    def handle_exceptions(request, course, exception):
        """
        Handle exceptions raised when rendering a view.
        """
        if isinstance(exception, Redirect) or isinstance(exception, Http404):
            raise
        if isinstance(exception, UnicodeEncodeError):
            raise Http404("URL contains Unicode characters")
        if settings.DEBUG:
            raise
        user = request.user
        log.exception(
            u"Error in %s: user=%s, effective_user=%s, course=%s",
            request.path,
            getattr(user, 'real_user', user),
            user,
            text_type(course.id),
        )
        try:
            return render_to_response(
                'courseware/courseware-error.html',
                {
                    'staff_access': has_access(user, 'staff', course),
                    'course': course,
                },
                status=500,
            )
        except:
            # Let the exception propagate, relying on global config to
            # at least return a nice error message
            log.exception("Error while rendering courseware-error page")
            raise

    def uses_bootstrap(self, request, course, tab):
        """
        Returns true if this view uses Bootstrap.
        """
        return tab.uses_bootstrap

    def create_page_context(self, request, course=None, tab=None, **kwargs):
        """
        Creates the context for the fragment's template.
        """
        staff_access = has_access(request.user, 'staff', course)
        supports_preview_menu = tab.get('supports_preview_menu', False)
        uses_bootstrap = self.uses_bootstrap(request, course, tab=tab)
        if supports_preview_menu:
            masquerade, masquerade_user = setup_masquerade(request, course.id, staff_access, reset_masquerade_data=True)
            request.user = masquerade_user
        else:
            masquerade = None

        if course and not check_course_open_for_learner(request.user, course):
            # Disable student view button if user is staff and
            # course is not yet visible to students.
            supports_preview_menu = False

        context = {
            'course': course,
            'tab': tab,
            'active_page': tab.get('type', None),
            'staff_access': staff_access,
            'masquerade': masquerade,
            'supports_preview_menu': supports_preview_menu,
            'uses_bootstrap': uses_bootstrap,
            'uses_pattern_library': not uses_bootstrap,
            'disable_courseware_js': True,
        }
        context.update(
            get_experiment_user_metadata_context(
                course,
                request.user,
            )
        )
        return context

    def render_to_fragment(self, request, course=None, page_context=None, **kwargs):
        """
        Renders the course tab to a fragment.
        """
        tab = page_context['tab']
        return tab.render_to_fragment(request, course, **kwargs)

    def render_standalone_response(self, request, fragment, course=None, tab=None, page_context=None, **kwargs):
        """
        Renders this course tab's fragment to HTML for a standalone page.
        """
        if not page_context:
            page_context = self.create_page_context(request, course=course, tab=tab, **kwargs)
        tab = page_context['tab']
        page_context['fragment'] = fragment
        if self.uses_bootstrap(request, course, tab=tab):
            return render_to_response('courseware/tab-view.html', page_context)
        else:
            return render_to_response('courseware/tab-view-v2.html', page_context)


@ensure_csrf_cookie
@ensure_valid_course_key
def syllabus(request, course_id):
    """
    Display the course's syllabus.html, or 404 if there is no such course.
    Assumes the course_id is in a valid format.
    """

    course_key = CourseKey.from_string(course_id)

    course = get_course_with_access(request.user, 'load', course_key)
    staff_access = bool(has_access(request.user, 'staff', course))

    return render_to_response('courseware/syllabus.html', {
        'course': course,
        'staff_access': staff_access,
    })


def registered_for_course(course, user):
    """
    Return True if user is registered for course, else False
    """
    if user is None:
        return False
    if user.is_authenticated:
        return CourseEnrollment.is_enrolled(user, course.id)
    else:
        return False


class EnrollStaffView(View):
    """
    Displays view for registering in the course to a global staff user.
    User can either choose to 'Enroll' or 'Don't Enroll' in the course.
      Enroll: Enrolls user in course and redirects to the courseware.
      Don't Enroll: Redirects user to course about page.
    Arguments:
     - request    : HTTP request
     - course_id  : course id
    Returns:
     - RedirectResponse
    """
    template_name = 'enroll_staff.html'

    @method_decorator(require_global_staff)
    @method_decorator(ensure_valid_course_key)
    def get(self, request, course_id):
        """
        Display enroll staff view to global staff user with `Enroll` and `Don't Enroll` options.
        """
        user = request.user
        course_key = CourseKey.from_string(course_id)
        with modulestore().bulk_operations(course_key):
            course = get_course_with_access(user, 'load', course_key)
            if not registered_for_course(course, user):
                context = {
                    'course': course,
                    'csrftoken': csrf(request)["csrf_token"]
                }
                return render_to_response(self.template_name, context)

    @method_decorator(require_global_staff)
    @method_decorator(ensure_valid_course_key)
    def post(self, request, course_id):
        """
        Either enrolls the user in course or redirects user to course about page
        depending upon the option (Enroll, Don't Enroll) chosen by the user.
        """
        _next = urllib.quote_plus(request.GET.get('next', 'info'), safe='/:?=')
        course_key = CourseKey.from_string(course_id)
        enroll = 'enroll' in request.POST
        if enroll:
            add_enrollment(request.user.username, course_id)
            log.info(
                u"User %s enrolled in %s via `enroll_staff` view",
                request.user.username,
                course_id
            )
            return redirect(_next)

        # In any other case redirect to the course about page.
        return redirect(reverse('about_course', args=[text_type(course_key)]))


from django.http import JsonResponse


@csrf_exempt
@cache_if_anonymous()
@require_http_methods(['POST'])
def course_interest(request):
    if request.method == 'POST':

        if request.POST['method'] == 'add':

            user_id = request.POST.get('user_id')
            org = request.POST.get('org')
            display_number_with_default = request.POST.get('display_number_with_default')

            sys.setdefaultencoding('utf-8')
            con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
            cur = con.cursor()
            query = """
                 select count(user_id) from interest_course where user_id = '""" + user_id + """' and org = '""" + org + """' and display_number_with_default = '""" + display_number_with_default + """';
            """
            cur.execute(query)
            count = cur.fetchall()
            ctn = count[0][0]
            cur.close()

            if (ctn == 1):
                cur = con.cursor()
                query = """
                     UPDATE interest_course
                       SET use_yn = 'Y'
                     WHERE user_id = '""" + user_id + """' and org = '""" + org + """' and display_number_with_default = '""" + display_number_with_default + """';
                """
                cur.execute(query)
                cur.execute('commit')
                cur.close()
                data = json.dumps('success')
            elif (ctn == 0):
                cur = con.cursor()
                query = """
                     insert into interest_course(user_id, org, display_number_with_default)
                     VALUES ('""" + user_id + """',
                             '""" + org + """',
                             '""" + display_number_with_default + """');
                """
                cur.execute(query)
                cur.execute('commit')
                cur.close()
                data = json.dumps('success')
            return HttpResponse(data, 'application/json')

        elif request.POST['method'] == 'modi':

            user_id = request.POST.get('user_id')
            org = request.POST.get('org')
            display_number_with_default = request.POST.get('display_number_with_default')

            sys.setdefaultencoding('utf-8')
            con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
            cur = con.cursor()
            query = """
                 UPDATE interest_course
                   SET use_yn = 'N'
                 WHERE user_id = '""" + user_id + """' and org = '""" + org + """' and display_number_with_default = '""" + display_number_with_default + """';
            """
            cur.execute(query)
            cur.execute('commit')
            cur.close()
            data = json.dumps('success')

            return HttpResponse(data, 'application/json')

        elif request.POST['method'] == 'flag':
            user_id = request.POST.get('user_id')
            org = request.POST.get('org')
            display_number_with_default = request.POST.get('display_number_with_default')

            sys.setdefaultencoding('utf-8')
            con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')

            cur = con.cursor()
            query = """
                 SELECT count(user_id)
                  FROM interest_course
                 WHERE user_id = '{0}' AND org = '{1}' AND display_number_with_default = '{2}' AND use_yn = 'Y';
             """.format(user_id, org, display_number_with_default)
            cur.execute(query)
            count = cur.fetchall()
            flag = count[0][0]
            cur.close()

            data = json.dumps(flag)

            return HttpResponse(data, 'application/json')

        return HttpResponse('success', 'application/json')


@ensure_csrf_cookie
@ensure_valid_course_key
@cache_if_anonymous()
def course_about(request, course_id):
    # 현대자동차의 로그인 연동을 위한 소스 추가
    encStr = request.GET.get('encStr')
    org = request.GET.get('org')

    # encStr 이 있을 경우 멀티사이트에서 온것으로 보고, 멀티사이트 복호화를 수행하고, 로그인 처리를 하도록 함
    if org and encStr:
        from branding.views import decrypt, login

        try:
            multisite = Multisite.objects.get(site_code=org)
            key = multisite.encryption_key
            logo_img_id = multisite.logo_img

            try:
                raw_data = decrypt(key, key, encStr)
            except Exception as e:
                raw_data = None
                log.info(traceback.format_exc(e))

            if raw_data:
                user_id = None
                params = parse_qs(raw_data)

                site_id = multisite.site_id
                org_user_id = params.get('userid')

                # parse_qs 자체는 value 를 리스트로 변환하여 반환하기 때문에 다음의 코드가 필요
                if org_user_id:
                    org_user_id = org_user_id[0]

                # org 와 기관내 사번으로 등록된 사용자가 있는지 확인하여 없다면 등록을 위해 세션에 정보 저장

                if org:
                    request.session['multisite_org'] = org

                if org_user_id:
                    request.session['multisite_userid'] = org_user_id

                try:
                    # multisite_member 에 사번과 동일한 사용자가 있는지 확인. params.get('user_id') 의 값은 기관의 사번
                    multisite_member = MultisiteMember.objects.get(site_id=site_id, org_user_id=org_user_id)
                    user_id = multisite_member.user_id

                except ObjectDoesNotExist as e3:
                    # 데이터가 없다면 세션에 정보를 저장
                    log.info('CourseTabView ObjectDoesNotExist [%s]' % e3.message)

                    # save_path 도 세션에 저장
                    # '/static/images/no_images_large.png'

                    # 로그인 화면으로 리다이렉트
                    from student.helpers import get_next_url_for_login_page

                    redirect_url = get_next_url_for_login_page(request)

                    path = str(request.path)
                    # return redirect('/login?next=' + urllib.urlencode(path))
                    enc_path = urllib.quote_plus(path)
                    return redirect('/login?next=' + enc_path)

                    # traceback.format_exc(e)

                except Exception as e4:
                    log.info('CourseTabView Exception [%s]' % e4.message)

                if user_id and not request.user.is_authenticated:
                    user = User.objects.get(pk=user_id)
                    user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
                    login(request, user)

                pass

        except ObjectDoesNotExist as e:
            pass
        except Exception as e1:
            pass

    """
    Display the course's about page.
    수정시 mobile_course_about도 함께 수정
    """
    try:
        review_email = str(request.user.email)
        review_username = str(request.user.username)
        login_status = 'o'
    except BaseException:
        review_email = 'x'
        review_username = 'x'

    # login check
    if not request.user.is_authenticated():
        login_status = 'x'
    user_id = request.user.id
    course_key = CourseKey.from_string(course_id)
    course_id_str = str(course_id)
    index_org_start = course_id_str.find(':') + 1
    index_org_end = course_id_str.find('+')
    index_number_start = index_org_end + 1
    index_number_end = course_id_str.rfind('+')
    course_org = course_id_str[index_org_start:index_org_end]
    course_number = course_id_str[index_number_start:index_number_end]

    print "course_org", course_org
    print "course_number", course_number

    # If a user is not able to enroll in a course then redirect
    # them away from the about page to the dashboard.
    if not can_self_enroll_in_course(course_key):
        return redirect(reverse('dashboard'))

    with modulestore().bulk_operations(course_key):
        permission = get_permission_for_course_about()
        course = get_course_with_access(request.user, permission, course_key)
        course_details = CourseDetails.populate(course)
        modes = CourseMode.modes_for_course_dict(course_key)

        if configuration_helpers.get_value('ENABLE_MKTG_SITE', settings.FEATURES.get('ENABLE_MKTG_SITE', False)):
            return redirect(reverse(course_home_url_name(course.id), args=[text_type(course.id)]))

        registered = registered_for_course(course, request.user)

        staff_access = bool(has_access(request.user, 'staff', course))
        studio_url = get_studio_url(course, 'settings/details')

        if has_access(request.user, 'load', course):
            course_target = reverse(course_home_url_name(course.id), args=[text_type(course.id)])
        else:
            course_target = reverse('about_course', args=[text_type(course.id)])

        show_courseware_link = bool(
            (
                has_access(request.user, 'load', course)
            ) or settings.FEATURES.get('ENABLE_LMS_MIGRATION')
        )

        # Note: this is a flow for payment for course registration, not the Verified Certificate flow.
        in_cart = False
        reg_then_add_to_cart_link = ""

        _is_shopping_cart_enabled = is_shopping_cart_enabled()
        if _is_shopping_cart_enabled:
            if request.user.is_authenticated:
                cart = shoppingcart.models.Order.get_cart_for_user(request.user)
                in_cart = shoppingcart.models.PaidCourseRegistration.contained_in_order(cart, course_key) or \
                          shoppingcart.models.CourseRegCodeItem.contained_in_order(cart, course_key)

            reg_then_add_to_cart_link = "{reg_url}?course_id={course_id}&enrollment_action=add_to_cart".format(
                reg_url=reverse('register_user'), course_id=urllib.quote(str(course_id))
            )

        # If the ecommerce checkout flow is enabled and the mode of the course is
        # professional or no id professional, we construct links for the enrollment
        # button to add the course to the ecommerce basket.
        ecomm_service = EcommerceService()
        ecommerce_checkout = ecomm_service.is_enabled(request.user)
        ecommerce_checkout_link = ''
        ecommerce_bulk_checkout_link = ''
        professional_mode = None
        is_professional_mode = CourseMode.PROFESSIONAL in modes or CourseMode.NO_ID_PROFESSIONAL_MODE in modes
        if ecommerce_checkout and is_professional_mode:
            professional_mode = modes.get(CourseMode.PROFESSIONAL, '') or \
                                modes.get(CourseMode.NO_ID_PROFESSIONAL_MODE, '')
            if professional_mode.sku:
                ecommerce_checkout_link = ecomm_service.get_checkout_page_url(professional_mode.sku)
            if professional_mode.bulk_sku:
                ecommerce_bulk_checkout_link = ecomm_service.get_checkout_page_url(professional_mode.bulk_sku)

        registration_price, course_price = get_course_prices(course)

        # Determine which checkout workflow to use -- LMS shoppingcart or Otto basket
        can_add_course_to_cart = _is_shopping_cart_enabled and registration_price and not ecommerce_checkout_link

        # Used to provide context to message to student if enrollment not allowed
        can_enroll = bool(has_access(request.user, 'enroll', course))
        invitation_only = course.invitation_only
        is_course_full = CourseEnrollment.objects.is_course_full(course)

        # Register button should be disabled if one of the following is true:
        # - Student is already registered for course
        # - Course is already full
        # - Student cannot enroll in course
        active_reg_button = not (registered or is_course_full or not can_enroll)
        print 'registered', registered
        print 'is_course_full', is_course_full
        print 'can_enroll', can_enroll
        print 'active_reg_button', active_reg_button
        is_shib_course = uses_shib(course)
        print 'is_shib_course', is_shib_course
        # get prerequisite courses display names
        pre_requisite_courses = get_prerequisite_courses_display(course)

        # Overview
        overview = CourseOverview.get_from_id(course.id)

        sidebar_html_enabled = course_experience_waffle().is_enabled(ENABLE_COURSE_ABOUT_SIDEBAR_HTML)

        # This local import is due to the circularity of lms and openedx references.
        # This may be resolved by using stevedore to allow web fragments to be used
        # as plugins, and to avoid the direct import.
        from openedx.features.course_experience.views.course_reviews import CourseReviewsModuleFragmentView

        # Embed the course reviews tool
        reviews_fragment_view = CourseReviewsModuleFragmentView().render_to_fragment(request, course=course)
        #######E ADD.###########
        # D-day
        today = datetime.now()
        course_start = course.start
        today_val = today.strptime(str(today)[0:10], "%Y-%m-%d").date()
        course_start_val = course_start.strptime(str(course_start)[0:10], "%Y-%m-%d").date()
        d_day = (course_start_val - today_val)

        if d_day.days > 0:
            day = {'day': 'D-' + str(d_day.days)}
        else:
            day = {'day': ''}

        # short description
        short_description = {'short_description': course_details.short_description}

        # classfy name
        classfy_dict = {
            # add classfy
            "edu": "Education",
            "hum": "Humanities",
            "social": "Social Sciences",
            "eng": "Engineering",
            "nat": "Natural Sciences",
            "med": "Medical Sciences",
            "art": "Arts & Physical",
            "intd": "Interdisciplinary",
        }

        middle_classfy_dict = {
            "lang": "Linguistics & Literature",
            "husc": "Human Sciences",
            "busn": "Business Administration & Economics",
            "law": "Law",
            "scsc": "Social Sciences",
            "enor": "General Education",
            "ekid": "Early Childhood Education",
            "espc": "Special Education",
            "elmt": "Elementary Education",
            "emdd": "Secondary Education",
            "cons": "Architecture",
            "civi": "Civil Construction & Urban Engineering",
            "traf": "Transportation",
            "mach": "Mechanical & Metallurgical Engineering",
            "elec": "Electricity & Electronics",
            "deta": "Precision & Energy",
            "matr": "Materials",
            "comp": "Computers & Communication",
            "indu": "Industrial Engineering",
            "cami": "Chemical Engineering",
            "other": "Others",
            "agri": "Agriculture & Fisheries",
            "bio": "Biology, Chemistry & Environmental Science",
            "life": "Living Science",
            "math": "Mathematics, Physics, Astronomy & Geography",
            "metr": "Medical Science",
            "nurs": "Nursing",
            "phar": "Pharmacy",
            "heal": "Therapeutics & Public Health",
            "dsgn": "Design",
            "appl": "Applied Arts",
            "danc": "Dancing & Physical Education",
            "form": "FineArts & Formative Arts",
            "play": "Drama & Cinema",
            "musc": "Music",
            "intd_m": "Interdisciplinary",
        }

        global classfy_name
        if course_details.classfy is None or course_details.classfy == '':
            classfy_name = 'Etc'
        else:
            classfy_name = classfy_dict[
                course_details.classfy] if course_details.classfy in classfy_dict else course_details.classfy

        if course_details.middle_classfy is None or course_details.middle_classfy == '':
            middle_classfy_name = 'Etc'
        else:
            middle_classfy_name = middle_classfy_dict[
                course_details.middle_classfy] if course_details.middle_classfy in middle_classfy_dict else course_details.middle_classfy

        # org name
        try:
            org_model = CodeDetail.objects.get(group_code='003', use_yn='Y', delete_yn='N',
                                               detail_code=course_details.org)
            org_name = org_model.detail_name if request.LANGUAGE_CODE == 'ko-kr' else org_model.detail_ename
        except CodeDetail.DoesNotExist:
            org_name = course_details.org

        if course_details.enrollment_start:
            enroll_start = course_details.enrollment_start.strptime(str(course_details.enrollment_start)[0:10],
                                                                    "%Y-%m-%d").date()
            enroll_end = course_details.enrollment_end.strptime(str(course_details.enrollment_end)[0:10],
                                                                "%Y-%m-%d").date()

            if _("Agree") == "Agree":
                enroll_sdate = {'enroll_sdate': enroll_start.strftime("%Y/%m/%d")}
                enroll_edate = {'enroll_edate': enroll_end.strftime("%Y/%m/%d")}
            else:
                enroll_sdate = {'enroll_sdate': enroll_start.strftime("%Y.%m.%d")}
                enroll_edate = {'enroll_edate': enroll_end.strftime("%Y.%m.%d")}
        else:
            enroll_sdate = {'enroll_sdate': ''}
            enroll_edate = {'enroll_edate': ''}

        if course_details.end_date:
            start = course_details.start_date.strftime("%Y.%m.%d")
            end = course_details.end_date.strftime("%Y.%m.%d")
        else:
            start = course_details.start_date
            end = ''

        # print "review_list = {}".format(review_list)
        # print "review_email = {}".format(review_email)
        print "course_id = {}".format(course_id)
        # print "already_list = {}".format(already_list)
        # print "enroll_list = {}".format(enroll_list)
        print "course_org = {}".format(course_org)
        print "course_number = {}".format(course_number)
        # print "course_total = {}".format(course_total)
        print "login_status = {}".format(login_status)

        sys.setdefaultencoding('utf-8')
        con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                          settings.DATABASES.get('default').get('USER'),
                          settings.DATABASES.get('default').get('PASSWORD'),
                          settings.DATABASES.get('default').get('NAME'),
                          charset='utf8')

        flag = 0

        if (login_status != 'x'):
            cur = con.cursor()
            query = """
                        SELECT count(user_id)
                          FROM interest_course
                         WHERE user_id = '{0}' AND org = '{1}' AND display_number_with_default = '{2}' AND use_yn = 'Y';
                    """.format(user_id, course_org, course_number)
            cur.execute(query)
            flag_index = cur.fetchall()
            cur.close()
            flag = flag_index[0][0]

        cur = con.cursor()
        query = """
                    SELECT concat(Date_format(start, '%Y/%m/%d'),
                            '~',
                            Date_format(end, '%Y/%m/%d')),
                             id
                      FROM course_overviews_courseoverview
                     WHERE org = '{0}' AND display_number_with_default = '{1}' AND id NOT IN ('{2}')
                     ORDER BY start DESC;
                """.format(course_org, course_number, overview)
        cur.execute(query)
        pre_course_index = cur.fetchall()
        cur.close()
        pre_course = pre_course_index

        # 청강 - course.end < today
        today_val = today.strptime(str(today)[0:10], "%Y-%m-%d").date()
        course_end = course.end
        time_compare = 'N'
        if course_end is not None:
            course_end_val = course_end.strptime(str(course_end)[0:10], "%Y-%m-%d").date()
            if today_val > course_end_val:
                time_compare = 'Y'

        cur = con.cursor()
        query = """
                    SELECT audit_yn
                      FROM course_overview_addinfo
                     WHERE course_id = '{0}';
                """.format(course_id)

        cur.execute(query)
        audit_index = cur.fetchall()
        cur.close()
        if len(audit_index) != 0 and time_compare == 'Y':
            audit_flag = audit_index[0][0]
        else:
            audit_flag = 'N'

        cur = con.cursor()
        query = '''
                    SELECT ifnull(b.detail_ename, ''), ifnull(a.course_subtitle, '-'), ifnull(a.course_language, '-')
                      FROM course_overview_addinfo a
                           LEFT JOIN code_detail b
                              ON a.course_level = b.detail_code AND b.group_code = '007'
                     WHERE a.course_id = '{course_id}';
                '''.format(course_id=course_id)
        cur.execute(query)
        coai = cur.fetchall()
        try:
            course_level = coai[0][0]
        except BaseException:
            course_level = '-'
        try:
            course_subtitle = coai[0][1]
        except BaseException:
            course_subtitle = '-'
        try:
            course_language = coai[0][2]
        except BaseException:
            course_language = '-'
        cur.close()

        cur = con.cursor()
        query = """
                    SELECT ifnull(effort, '00:00@0#00:00$00:00')
                      FROM course_overviews_courseoverview
                     WHERE id = '{course_id}'
                """.format(course_id=course_id)
        cur.execute(query)
        effort = cur.fetchall()[0][0]
        cur.close()
        effort_week = effort.split('@')[1].split('#')[0] if effort and '@' in effort and '#' in effort else ''
        study_time = effort.split('$')[1].split(':')[0] + "시간 " + effort.split('$')[1].split(':')[
            1] + "분" if effort and '$' in effort else '-'

        try:
            with connections['default'].cursor() as cur:
                query = """
                    select count(*)
                    from course_review a
                    left join auth_user b on a.user_id = b.id
                    where course_id ="{course_id}" and b.username ="{user_name}";
                    """.format(course_id=course_id, user_name=request.user)
                cur.execute(query)
                r_c = cur.fetchall()
                review_val = r_c[0][0]
                print "reivew_chk", review_val
                print "query", query
                if review_val > 0:
                    review_chk = 'o'
                else:
                    review_chk = 'x'
        except:
            review_chk = 'x'
            pass

        with connections['default'].cursor() as cur:
            query = """
                    select a.content,a.point,a.user_id,DATE_FORMAT(a.reg_time, "%Y/%m/%d "),a.id,b.username
                    from course_review a
                    left join auth_user b on a.user_id = b.id
                    where course_id LIKE "course-v1:{course_org}+{course_number}+%"
                """.format(course_id=course_id, course_org=course_org, course_number=course_number)
            cur.execute(query)
            review_list = cur.fetchall()

            data_list = []

            for data in review_list:
                data_dict = dict()
                data_dict['content'] = data[0]
                data_dict['point'] = data[1]
                data_dict['user_id'] = data[2]
                data_dict['reg_time'] = data[3]
                data_dict['seq'] = data[4]
                data_dict['username'] = data[5]
                data_dict['like'] = 0
                data_dict['bad'] = 0

                with connections['default'].cursor() as cur:
                    query = """
                            select  count(good_bad),review_seq, good_bad
                            from course_review_user
                            where review_id = '{review_id}' and review_seq='{review_seq}'
                            group by good_bad;
                        """.format(review_id=data[2], review_seq=data[4])
                    cur.execute(query)
                    like_list = cur.fetchall()
                    for like in like_list:
                        if like[2] == 'g':
                            data_dict['like'] = like[0]
                        elif like[2] == 'b':
                            data_dict['bad'] = like[0]

                data_list.append(data_dict)

        # 강좌 만족도 별점
        course_survey_data = survey_result_star(course_org, course_number)

        # today d-day와 청강에서 사용
        today = datetime.now()

        # 청강 - course.end < today
        today_val = today.strptime(str(today)[0:10], "%Y-%m-%d").date()
        course_end = course.end
        time_compare = 'N'
        if course_end is not None:
            course_end_val = course_end.strptime(str(course_end)[0:10], "%Y-%m-%d").date()
            if today_val > course_end_val:
                time_compare = 'Y'

        with connections['default'].cursor() as cur:
            query = '''
                SELECT audit_yn
                  FROM course_overview_addinfo
                 WHERE course_id = '{course_id}';
            '''.format(course_id=course_id)
            cur.execute(query)
            audit_yn = cur.fetchall()

            if len(audit_yn) != 0 and time_compare == 'Y':
                audit_flag = audit_yn[0][0]
            else:
                audit_flag = 'N'

        # 유사강좌 -> 백엔드 로직 시작
        # LMS_BASE = settings.ENV_TOKENS.get('LMS_BASE')
        # LMS_BASE = 'www.kmooc.kr' # TEST
        LMS_BASE = 'localhost'

        url = 'http://' + LMS_BASE + '/search/course_discovery/'

        search_string = course_details.short_description

        if not search_string or search_string == '':
            search_string = course.display_name

        # 유사강좌 -> 엘라스틱 서치에 데이터 요청
        payload = {}
        headers = {}
        payload['search_string'] = search_string
        payload['page_size'] = '20'
        payload['page_index'] = '0'
        headers['X-Requested-With'] = 'XMLHttpRequest'

        # print "url -> ", url
        # print "payload -> ", payload
        # print "headers -> ", headers

        try:
            r = requests.post(url, data=payload, headers=headers, timeout=2)
            # logging.info(r.text)
            # logging.info(r.text)
            # logging.info(r.text)
            data = json.loads(r.text)

            print "data -> ", data

            # 유사강좌 -> 데이터 파싱

            # course_id 비교를 위한 course_id 선언
            cid = course_id

            similar_course = []
            for result in data['results']:
                course_dict = {}
                course_id = result['_id']
                image_url = result['data']['image_url']
                org = result['data']['org']
                display_name = result['data']['content']['display_name']

                # 자신과 동일한 강좌는 제외
                if cid == course_id:
                    continue

                try:
                    compare_start = sim_start = datetime.strptime(result['data']['start'][:19], '%Y-%m-%dT%H:%M:%S')
                    sim_start = sim_start.strftime('%Y-%m-%d')
                except BaseException:
                    sim_start = '0000-00-00'

                try:
                    compare_end = sim_end = datetime.strptime(result['data']['end'][:19], '%Y-%m-%dT%H:%M:%S')
                    sim_end = sim_end.strftime('%Y-%m-%d')
                except BaseException:
                    sim_end = '0000-00-00'

                with connections['default'].cursor() as cur:
                    query = '''
                        select detail_name
                        from code_detail
                        where group_code = '003'
                        and detail_code = '{org}'
                    '''.format(org=org)
                    print "---------------------------------"
                    print query
                    print "---------------------------------"
                    cur.execute(query)
                    try:
                        org = cur.fetchall()[0][0]
                    except BaseException:
                        org = '기관없음'

                print "org -> ", org
                print "org -> ", org
                print "org -> ", org

                # 유사강좌 진행 상태 추가
                utcnow = datetime.utcnow()

                if compare_start > utcnow:
                    sim_status = 'ready'
                elif compare_start <= utcnow <= compare_end:
                    sim_status = 'ing'
                else:
                    sim_status = 'end'

                course_dict['course_id'] = course_id
                course_dict['image_url'] = image_url
                course_dict['org'] = org
                course_dict['display_name'] = display_name
                course_dict['sim_start'] = sim_start
                course_dict['sim_end'] = sim_end
                course_dict['sim_status'] = sim_status
                similar_course.append(course_dict)

        except BaseException as err:
            similar_course = []
            log.info('*** similar_course logic error DEBUG -> lms/djangoapps/courseware/views/views.py ***')
            log.info(err)

        print "len(similar_course) -> ", len(similar_course)
        # TIME_ZONE 작업중
        s1 = course_details.start_date.strftime("%Y")
        s2 = course_details.start_date.strftime("%m")
        s3 = course_details.start_date.strftime("%d")
        s4 = course_details.start_date.strftime("%H")
        s5 = course_details.start_date.strftime("%M")
        s6 = course_details.start_date.strftime("%S")

        if course_details.end_date is not None:
            e1 = course_details.end_date.strftime("%Y")
            e2 = course_details.end_date.strftime("%m")
            e3 = course_details.end_date.strftime("%d")
            e4 = course_details.end_date.strftime("%H")
            e5 = course_details.end_date.strftime("%M")
            e6 = course_details.end_date.strftime("%S")

        if course_details.enrollment_start is not None:
            rs1 = course_details.enrollment_start.strftime("%Y")
            rs2 = course_details.enrollment_start.strftime("%m")
            rs3 = course_details.enrollment_start.strftime("%d")
            rs4 = course_details.enrollment_start.strftime("%H")
            rs5 = course_details.enrollment_start.strftime("%M")
            rs6 = course_details.enrollment_start.strftime("%S")

        if course_details.enrollment_end is not None:
            re1 = course_details.enrollment_end.strftime("%Y")
            re2 = course_details.enrollment_end.strftime("%m")
            re3 = course_details.enrollment_end.strftime("%d")
            re4 = course_details.enrollment_end.strftime("%H")
            re5 = course_details.enrollment_end.strftime("%M")
            re6 = course_details.enrollment_end.strftime("%S")
        try:
            # locale = to_locale(get_language())
            user_timezone = user_timezone_locale_prefs(crum.get_current_request())['user_timezone']
            print "origin_start", start
            # CourseStartDate.date
            utc = pytz.utc
            print "user_timezone = ", utc.zone

            user_tz = timezone(user_timezone)
        except:
            user_tz = timezone('Asia/Seoul')

        utc_dt_start = datetime(int(s1), int(s2), int(s3), int(s4), int(s5), int(s6), tzinfo=utc)
        print 'utc_dt_start',utc_dt_start
        utc_dt_end = datetime(int(e1), int(e2), int(e3), int(e4), int(e5), int(e6), tzinfo=utc) if course_details.end_date is not None else None
        utc_dt_enroll_start = datetime(int(rs1), int(rs2), int(rs3), int(rs4), int(rs5), int(rs6), tzinfo=utc) if course_details.enrollment_start is not None else None
        utc_dt_enroll_end = datetime(int(re1), int(re2), int(re3), int(re4), int(re5), int(re6), tzinfo=utc) if course_details.enrollment_end is not None else None
        # fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        fmt = '%Y.%m.%d'
        fmt2 = '%H:%M:%S'
        loc_dt_start = utc_dt_start.astimezone(user_tz)
        loc_dt_end = utc_dt_end.astimezone(user_tz) if utc_dt_end is not None else None
        utc_dt_enroll_start = utc_dt_enroll_start.astimezone(user_tz) if utc_dt_enroll_start is not None else None
        utc_dt_enroll_end = utc_dt_enroll_end.astimezone(user_tz) if utc_dt_enroll_end is not None else None

        if loc_dt_end.strftime(fmt2) == '00:00:00':
            loc_dt_end = loc_dt_end - timedelta(minutes=1)
        if utc_dt_enroll_end.strftime(fmt2) == '00:00:00':
            utc_dt_enroll_end = utc_dt_enroll_end - timedelta(minutes=1)

        start = loc_dt_start.strftime(fmt)
        end = loc_dt_end.strftime(fmt) if loc_dt_end is not None else None
        enroll_sdate = utc_dt_enroll_start.strftime(fmt) if utc_dt_enroll_start is not None else None
        enroll_edate = utc_dt_enroll_end.strftime(fmt) if utc_dt_enroll_end is not None else None

        # 학습자가 등록한 모드 확인
        enroll_mode, enroll_active = CourseEnrollment.enrollment_mode_for_user(request.user, course.id)

        enroll_audit = True if enroll_mode == 'audit' and enroll_active == True else False

        # print "later_start", start
        with connections['default'].cursor() as cur:
            query = """
                    select org, org_name, org_type
                    from tb_enroll_org 
                    where use_yn = 'Y' order by org_name
                """
            cur.execute(query)
            recog_org = cur.fetchall()

        context = {
            'similar_course': similar_course,  # 유사강좌
            'course': course,
            'course_details': course_details,
            'staff_access': staff_access,
            'studio_url': studio_url,
            'registered': registered,
            'course_target': course_target,
            'day': day,
            'is_cosmetic_price_enabled': settings.FEATURES.get('ENABLE_COSMETIC_DISPLAY_PRICE'),
            'course_price': course_price,
            'in_cart': in_cart,
            'ecommerce_checkout': ecommerce_checkout,
            'ecommerce_checkout_link': ecommerce_checkout_link,
            'ecommerce_bulk_checkout_link': ecommerce_bulk_checkout_link,
            'professional_mode': professional_mode,
            'reg_then_add_to_cart_link': reg_then_add_to_cart_link,
            'show_courseware_link': show_courseware_link,
            'is_course_full': is_course_full,
            'can_enroll': can_enroll,
            'invitation_only': invitation_only,
            'active_reg_button': active_reg_button,
            'is_shib_course': is_shib_course,
            # We do not want to display the internal courseware header, which is used when the course is found in the
            # context. This value is therefor explicitly set to render the appropriate header.
            'disable_courseware_header': True,
            'can_add_course_to_cart': can_add_course_to_cart,
            'cart_link': reverse('shoppingcart.views.show_cart'),
            'pre_requisite_courses': pre_requisite_courses,
            'course_image_urls': overview.image_urls,
            'reviews_fragment_view': reviews_fragment_view,
            'sidebar_html_enabled': sidebar_html_enabled,
            'rev': data_list,
            'review_chk': review_chk,
            # 'classfy' : classfy,
            'classfy_name': classfy_name,
            'middle_classfy_name': middle_classfy_name,
            'org_name': org_name,
            'enroll_sdate': enroll_sdate,
            'enroll_edate': enroll_edate,
            # --- REVIEW CONTEXT --- #
            # 'review_list': review_list,
            # 'review_email': review_email,
            'course_id': course_id,
            # 'already_list': already_list,
            # 'enroll_list': enroll_list,
            'course_org': course_org,
            'course_number': course_number,
            # 'course_total': course_total,
            'login_status': login_status,
            'flag': flag,
            'pre_course': pre_course,
            'audit_flag': audit_flag,
            'effort_week': effort_week,
            # 'course_link': course_link,
            'course_level': course_level,
            'course_subtitle': course_subtitle,
            'course_language': course_language,
            'study_time': study_time,
            'start': start,
            'end': end,
            'enroll_audit': enroll_audit,
            'course_survey_data': course_survey_data,
            'recog_org':recog_org
        }

        return render_to_response('courseware/course_about.html', context)


@ensure_csrf_cookie
@ensure_valid_course_key
@cache_if_anonymous()
def mobile_course_about(request, course_id):
    """
    Display the course's about page.
    """
    try:
        review_email = str(request.user.email)
        review_username = str(request.user.username)
        login_status = 'o'
    except BaseException:
        review_email = 'x'
        review_username = 'x'

    # login check
    if not request.user.is_authenticated():
        login_status = 'x'
    user_id = request.user.id
    course_key = CourseKey.from_string(course_id)
    course_id_str = str(course_id)
    index_org_start = course_id_str.find(':') + 1
    index_org_end = course_id_str.find('+')
    index_number_start = index_org_end + 1
    index_number_end = course_id_str.rfind('+')
    course_org = course_id_str[index_org_start:index_org_end]
    course_number = course_id_str[index_number_start:index_number_end]

    print "course_org", course_org
    print "course_number", course_number
    # If a user is not able to enroll in a course then redirect
    # them away from the about page to the dashboard.
    if not can_self_enroll_in_course(course_key):
        return redirect(reverse('dashboard'))

    with modulestore().bulk_operations(course_key):
        permission = get_permission_for_course_about()
        course = get_course_with_access(request.user, permission, course_key)
        course_details = CourseDetails.populate(course)
        modes = CourseMode.modes_for_course_dict(course_key)

        if configuration_helpers.get_value('ENABLE_MKTG_SITE', settings.FEATURES.get('ENABLE_MKTG_SITE', False)):
            return redirect(reverse(course_home_url_name(course.id), args=[text_type(course.id)]))

        registered = registered_for_course(course, request.user)

        staff_access = bool(has_access(request.user, 'staff', course))
        studio_url = get_studio_url(course, 'settings/details')

        if has_access(request.user, 'load', course):
            course_target = reverse(course_home_url_name(course.id), args=[text_type(course.id)])
        else:
            course_target = reverse('about_course', args=[text_type(course.id)])

        course_link = course_target.replace("/courses/", "edxapp://enroll?course_id=")
        course_link = course_link.replace("/info", "&email_opt_in=true")
        course_link = course_link.replace("/course/", "&email_opt_in=true")
        course_link = course_link.replace('/about', '&email_opt_in=true')

        show_courseware_link = bool(
            (
                has_access(request.user, 'load', course)
            ) or settings.FEATURES.get('ENABLE_LMS_MIGRATION')
        )

        # Note: this is a flow for payment for course registration, not the Verified Certificate flow.
        in_cart = False
        reg_then_add_to_cart_link = ""

        _is_shopping_cart_enabled = is_shopping_cart_enabled()
        if _is_shopping_cart_enabled:
            if request.user.is_authenticated:
                cart = shoppingcart.models.Order.get_cart_for_user(request.user)
                in_cart = shoppingcart.models.PaidCourseRegistration.contained_in_order(cart, course_key) or \
                          shoppingcart.models.CourseRegCodeItem.contained_in_order(cart, course_key)

            reg_then_add_to_cart_link = "{reg_url}?course_id={course_id}&enrollment_action=add_to_cart".format(
                reg_url=reverse('register_user'), course_id=urllib.quote(str(course_id))
            )

        # If the ecommerce checkout flow is enabled and the mode of the course is
        # professional or no id professional, we construct links for the enrollment
        # button to add the course to the ecommerce basket.
        ecomm_service = EcommerceService()
        ecommerce_checkout = ecomm_service.is_enabled(request.user)
        ecommerce_checkout_link = ''
        ecommerce_bulk_checkout_link = ''
        professional_mode = None
        is_professional_mode = CourseMode.PROFESSIONAL in modes or CourseMode.NO_ID_PROFESSIONAL_MODE in modes
        if ecommerce_checkout and is_professional_mode:
            professional_mode = modes.get(CourseMode.PROFESSIONAL, '') or \
                                modes.get(CourseMode.NO_ID_PROFESSIONAL_MODE, '')
            if professional_mode.sku:
                ecommerce_checkout_link = ecomm_service.get_checkout_page_url(professional_mode.sku)
            if professional_mode.bulk_sku:
                ecommerce_bulk_checkout_link = ecomm_service.get_checkout_page_url(professional_mode.bulk_sku)

        registration_price, course_price = get_course_prices(course)

        # Determine which checkout workflow to use -- LMS shoppingcart or Otto basket
        can_add_course_to_cart = _is_shopping_cart_enabled and registration_price and not ecommerce_checkout_link

        # Used to provide context to message to student if enrollment not allowed
        can_enroll = bool(has_access(request.user, 'enroll', course))
        invitation_only = course.invitation_only
        is_course_full = CourseEnrollment.objects.is_course_full(course)

        # Register button should be disabled if one of the following is true:
        # - Student is already registered for course
        # - Course is already full
        # - Student cannot enroll in course
        active_reg_button = not (registered or is_course_full or not can_enroll)

        is_shib_course = uses_shib(course)

        # get prerequisite courses display names
        pre_requisite_courses = get_prerequisite_courses_display(course)

        # Overview
        overview = CourseOverview.get_from_id(course.id)

        sidebar_html_enabled = course_experience_waffle().is_enabled(ENABLE_COURSE_ABOUT_SIDEBAR_HTML)

        # This local import is due to the circularity of lms and openedx references.
        # This may be resolved by using stevedore to allow web fragments to be used
        # as plugins, and to avoid the direct import.
        from openedx.features.course_experience.views.course_reviews import CourseReviewsModuleFragmentView

        # Embed the course reviews tool
        reviews_fragment_view = CourseReviewsModuleFragmentView().render_to_fragment(request, course=course)
        #######E ADD.###########
        # D-day
        today = datetime.now()
        course_start = course.start
        today_val = today.strptime(str(today)[0:10], "%Y-%m-%d").date()
        course_start_val = course_start.strptime(str(course_start)[0:10], "%Y-%m-%d").date()
        d_day = (course_start_val - today_val)

        if d_day.days > 0:
            day = {'day': 'D-' + str(d_day.days)}
        else:
            day = {'day': ''}

        # short description
        short_description = {'short_description': course_details.short_description}

        # classfy name
        classfy_dict = {
            # add classfy
            "edu": "Education",
            "hum": "Humanities",
            "social": "Social Sciences",
            "eng": "Engineering",
            "nat": "Natural Sciences",
            "med": "Medical Sciences",
            "art": "Arts & Physical",
            "intd": "Interdisciplinary",
        }

        middle_classfy_dict = {
            "lang": "Linguistics & Literature",
            "husc": "Human Sciences",
            "busn": "Business Administration & Economics",
            "law": "Law",
            "scsc": "Social Sciences",
            "enor": "General Education",
            "ekid": "Early Childhood Education",
            "espc": "Special Education",
            "elmt": "Elementary Education",
            "emdd": "Secondary Education",
            "cons": "Architecture",
            "civi": "Civil Construction & Urban Engineering",
            "traf": "Transportation",
            "mach": "Mechanical & Metallurgical Engineering",
            "elec": "Electricity & Electronics",
            "deta": "Precision & Energy",
            "matr": "Materials",
            "comp": "Computers & Communication",
            "indu": "Industrial Engineering",
            "cami": "Chemical Engineering",
            "other": "Others",
            "agri": "Agriculture & Fisheries",
            "bio": "Biology, Chemistry & Environmental Science",
            "life": "Living Science",
            "math": "Mathematics, Physics, Astronomy & Geography",
            "metr": "Medical Science",
            "nurs": "Nursing",
            "phar": "Pharmacy",
            "heal": "Therapeutics & Public Health",
            "dsgn": "Design",
            "appl": "Applied Arts",
            "danc": "Dancing & Physical Education",
            "form": "FineArts & Formative Arts",
            "play": "Drama & Cinema",
            "musc": "Music",
            "intd_m": "Interdisciplinary",
        }

        # if course_details.classfy != 'all':
        #     classfy_name = ClassDict[course_details.classfy]
        # else:
        #     classfy_name = 'Etc'

        global classfy_name
        if course_details.classfy is None or course_details.classfy == '':
            classfy_name = 'Etc'
        else:
            classfy_name = classfy_dict[
                course_details.classfy] if course_details.classfy in classfy_dict else course_details.classfy

        if course_details.middle_classfy is None or course_details.middle_classfy == '':
            middle_classfy_name = 'Etc'
        else:
            middle_classfy_name = middle_classfy_dict[
                course_details.middle_classfy] if course_details.middle_classfy in middle_classfy_dict else course_details.middle_classfy

        # org name
        try:
            org_model = CodeDetail.objects.get(group_code='003', use_yn='Y', delete_yn='N',
                                               detail_code=course_details.org)
            org_name = org_model.detail_name if request.LANGUAGE_CODE == 'ko-kr' else org_model.detail_ename
        except CodeDetail.DoesNotExist:
            org_name = course_details.org

        if course_details.enrollment_start:
            enroll_start = course_details.enrollment_start.strptime(str(course_details.enrollment_start)[0:10],
                                                                    "%Y-%m-%d").date()
            enroll_end = course_details.enrollment_end.strptime(str(course_details.enrollment_end)[0:10],
                                                                "%Y-%m-%d").date()

            if _("Agree") == "Agree":
                enroll_sdate = {'enroll_sdate': enroll_start.strftime("%Y/%m/%d")}
                enroll_edate = {'enroll_edate': enroll_end.strftime("%Y/%m/%d")}
            else:
                enroll_sdate = {'enroll_sdate': enroll_start.strftime("%Y.%m.%d")}
                enroll_edate = {'enroll_edate': enroll_end.strftime("%Y.%m.%d")}
        else:
            enroll_sdate = {'enroll_sdate': ''}
            enroll_edate = {'enroll_edate': ''}

        if course_details.end_date:
            start = course_details.start_date.strftime("%Y.%m.%d")
            end = course_details.end_date.strftime("%Y.%m.%d")
        else:
            start = course_details.start_date
            end = ''

        # print "review_list = {}".format(review_list)
        # print "review_email = {}".format(review_email)
        print "course_id = {}".format(course_id)
        # print "already_list = {}".format(already_list)
        # print "enroll_list = {}".format(enroll_list)
        print "course_org = {}".format(course_org)
        print "course_number = {}".format(course_number)
        # print "course_total = {}".format(course_total)
        print "login_status = {}".format(login_status)

        sys.setdefaultencoding('utf-8')
        con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                          settings.DATABASES.get('default').get('USER'),
                          settings.DATABASES.get('default').get('PASSWORD'),
                          settings.DATABASES.get('default').get('NAME'),
                          charset='utf8')

        flag = 0

        if (login_status != 'x'):
            cur = con.cursor()
            query = """
                        SELECT count(user_id)
                          FROM interest_course
                         WHERE user_id = '{0}' AND org = '{1}' AND display_number_with_default = '{2}' AND use_yn = 'Y';
                    """.format(user_id, course_org, course_number)
            cur.execute(query)
            flag_index = cur.fetchall()
            cur.close()
            flag = flag_index[0][0]

        cur = con.cursor()
        query = """
                    SELECT concat(Date_format(start, '%Y/%m/%d'),
                            '~',
                            Date_format(end, '%Y/%m/%d')),
                             id
                      FROM course_overviews_courseoverview
                     WHERE org = '{0}' AND display_number_with_default = '{1}' AND id NOT IN ('{2}')
                     ORDER BY start DESC;
                """.format(course_org, course_number, overview)
        cur.execute(query)
        pre_course_index = cur.fetchall()
        cur.close()
        pre_course = pre_course_index

        # 청강 - course.end < today
        today_val = today.strptime(str(today)[0:10], "%Y-%m-%d").date()
        course_end = course.end
        time_compare = 'N'
        if course_end is not None:
            course_end_val = course_end.strptime(str(course_end)[0:10], "%Y-%m-%d").date()
            if today_val > course_end_val:
                time_compare = 'Y'

        cur = con.cursor()
        query = """
                    SELECT audit_yn
                      FROM course_overview_addinfo
                     WHERE course_id = '{0}';
                """.format(course_id)

        cur.execute(query)
        audit_index = cur.fetchall()
        cur.close()
        if len(audit_index) != 0 and time_compare == 'Y':
            audit_flag = audit_index[0][0]
        else:
            audit_flag = 'N'

        cur = con.cursor()
        query = '''
                    SELECT ifnull(b.detail_ename, '')
                      FROM course_overview_addinfo a
                           LEFT JOIN code_detail b
                              ON a.course_level = b.detail_code AND b.group_code = '007'
                     WHERE a.course_id = '{course_id}';
                '''.format(course_id=course_id)
        cur.execute(query)
        course_level = cur.fetchall()
        print "course_level", course_level
        course_level = course_level[0][0]
        cur.close()

        cur = con.cursor()
        query = """
                    SELECT ifnull(effort, '00:00@0#00:00$00:00')
                      FROM course_overviews_courseoverview
                     WHERE id = '{course_id}'
                """.format(course_id=course_id)
        cur.execute(query)
        effort = cur.fetchall()[0][0]
        cur.close()
        effort_week = effort.split('@')[1].split('#')[0] if effort and '@' in effort and '#' in effort else ''
        study_time = effort.split('$')[1].split(':')[0] + "시간 " + effort.split('$')[1].split(':')[
            1] + "분" if effort and '$' in effort else '-'

        #######E ADD.###########
        # coure_review
        try:
            with connections['default'].cursor() as cur:
                query = """
                    select count(*)
                    from course_review a
                    left join auth_user b on a.user_id = b.id
                    where course_id ="{course_id}" and b.username ="{user_name}";
                    """.format(course_id=course_id, user_name=request.user)
                cur.execute(query)
                r_c = cur.fetchall()
                review_val = r_c[0][0]
                print "reivew_chk", review_val
                print "query", query
                if review_val > 0:
                    review_chk = 'o'
                else:
                    review_chk = 'x'
        except:
            review_chk = 'x'
            pass

        with connections['default'].cursor() as cur:
            query = """
                    select a.content,a.point,a.user_id,DATE_FORMAT(a.reg_time, "%Y/%m/%d "),a.id,b.username
                    from course_review a
                    left join auth_user b on a.user_id = b.id
                    where course_id LIKE "course-v1:{course_org}+{course_number}+%"
                """.format(course_id=course_id, course_org=course_org, course_number=course_number)
            cur.execute(query)
            review_list = cur.fetchall()

            data_list = []

            for data in review_list:
                data_dict = dict()
                data_dict['content'] = data[0]
                data_dict['point'] = data[1]
                data_dict['user_id'] = data[2]
                data_dict['reg_time'] = data[3]
                data_dict['seq'] = data[4]
                data_dict['username'] = data[5]
                # data_list.append(data_dict)
                data_dict['like'] = 0
                data_dict['bad'] = 0

                with connections['default'].cursor() as cur:
                    query = """
                            select  count(good_bad),review_seq, good_bad
                            from course_review_user
                            where review_id = '{review_id}' and review_seq='{review_seq}'
                            group by good_bad;
                        """.format(review_id=data[2], review_seq=data[4])
                    cur.execute(query)
                    like_list = cur.fetchall()
                    for like in like_list:
                        if like[2] == 'g':
                            data_dict['like'] = like[0]
                        elif like[2] == 'b':
                            data_dict['bad'] = like[0]

                data_list.append(data_dict)

        # 강좌 만족도 별점
        course_survey_data = survey_result_star(course_org, course_number)

        # today d-day와 청강에서 사용
        today = datetime.now()

        # 청강 - course.end < today
        today_val = today.strptime(str(today)[0:10], "%Y-%m-%d").date()
        course_end = course.end
        time_compare = 'N'
        if course_end is not None:
            course_end_val = course_end.strptime(str(course_end)[0:10], "%Y-%m-%d").date()
            if today_val > course_end_val:
                time_compare = 'Y'

        with connections['default'].cursor() as cur:
            query = '''
                SELECT audit_yn
                  FROM course_overview_addinfo
                 WHERE course_id = '{course_id}';
            '''.format(course_id=course_id)
            cur.execute(query)
            audit_yn = cur.fetchall()

            if len(audit_yn) != 0 and time_compare == 'Y':
                audit_flag = audit_yn[0][0]
            else:
                audit_flag = 'N'

        context = {
            # 'similar_course': similar_course,  # 유사강좌
            'course': course,
            'course_details': course_details,
            'staff_access': staff_access,
            'studio_url': studio_url,
            'registered': registered,
            'course_target': course_target,
            'day': day,
            'is_cosmetic_price_enabled': settings.FEATURES.get('ENABLE_COSMETIC_DISPLAY_PRICE'),
            'course_price': course_price,
            'in_cart': in_cart,
            'ecommerce_checkout': ecommerce_checkout,
            'ecommerce_checkout_link': ecommerce_checkout_link,
            'ecommerce_bulk_checkout_link': ecommerce_bulk_checkout_link,
            'professional_mode': professional_mode,
            'reg_then_add_to_cart_link': reg_then_add_to_cart_link,
            'show_courseware_link': show_courseware_link,
            'is_course_full': is_course_full,
            'can_enroll': can_enroll,
            'invitation_only': invitation_only,
            'active_reg_button': active_reg_button,
            'is_shib_course': is_shib_course,
            # We do not want to display the internal courseware header, which is used when the course is found in the
            # context. This value is therefor explicitly set to render the appropriate header.
            'disable_courseware_header': True,
            'can_add_course_to_cart': can_add_course_to_cart,
            'cart_link': reverse('shoppingcart.views.show_cart'),
            'pre_requisite_courses': pre_requisite_courses,
            'course_image_urls': overview.image_urls,
            'reviews_fragment_view': reviews_fragment_view,
            'sidebar_html_enabled': sidebar_html_enabled,
            'rev': data_list,
            'review_chk': review_chk,
            # 'classfy' : classfy,
            'classfy_name': classfy_name,
            'middle_classfy_name': middle_classfy_name,
            'org_name': org_name,
            'enroll_sdate': enroll_sdate,
            'enroll_edate': enroll_edate,
            # --- REVIEW CONTEXT --- #
            # 'review_list': review_list,
            # 'review_email': review_email,
            'course_id': course_id,
            # 'already_list': already_list,
            # 'enroll_list': enroll_list,
            'course_org': course_org,
            'course_number': course_number,
            # 'course_total': course_total,
            'login_status': login_status,
            'flag': flag,
            'pre_course': pre_course,
            'audit_flag': audit_flag,
            'effort_week': effort_week,
            'course_link': course_link,
            'course_level': course_level,
            'study_time': study_time,
            'start': start,
            'end': end,
            'course_survey_data': course_survey_data,
            'mobile_title': 'Course Overview',
            'mobile_template': 'courseware/mobile_course_about'
        }

        return render_to_response('mobile_main.html', context)


# 강좌 만족도 설문 결과 별점(about page)
def survey_result_star(org, display_number_with_default):
    with connections['default'].cursor() as cur:
        query = '''
            SELECT 
                ROUND(COUNT(*) / 2, 0) AS cnt, ROUND(AVG(score), 1)
            FROM
                (SELECT 
                    org, course, IF(rn = 1, question_06, question_07) score
                FROM
                    (SELECT 
                    org,
                        display_number_with_default course,
                        question_06,
                        question_07
                FROM
                    survey_result
                WHERE
                    org = '{org}'
                        AND display_number_with_default = '{course}') t1, (SELECT 
                    @rn:=@rn + 1 rn
                FROM
                    code_detail a, (SELECT @rn:=0) b
                LIMIT 2) t2) t3
            GROUP BY org , course;
        '''.format(org=org, course=display_number_with_default)
        cur.execute(query)
        result_data = cur.fetchone()

    data = dict()
    if result_data is None:
        data = False
    elif result_data[0] >= 30 and result_data[1] >= 4.0:  # 응답자 30명 이상, 만족도 4.0 이상 노출
        data['r_total'] = result_data[0]  # 총 응답자
        # 강좌 만족도
        data['r_course'] = [int(result_data[1]), str(result_data[1] % int(result_data[1]))[2]] if result_data[1] != 0.0 else [0, 0]
        data['r_rating'] = result_data[1]
    else:
        data = False
    return data


@ensure_csrf_cookie
@cache_if_anonymous()
def program_marketing(request, program_uuid):
    """
    Display the program marketing page.
    """
    program_data = get_programs(request.site, uuid=program_uuid)

    if not program_data:
        raise Http404

    program = ProgramMarketingDataExtender(program_data, request.user).extend()
    program['type_slug'] = slugify(program['type'])
    skus = program.get('skus')
    ecommerce_service = EcommerceService()

    context = {'program': program}

    if program.get('is_learner_eligible_for_one_click_purchase') and skus:
        context['buy_button_href'] = ecommerce_service.get_checkout_page_url(*skus, program_uuid=program_uuid)

    context['uses_bootstrap'] = True

    return render_to_response('courseware/program_marketing.html', context)


from lms.djangoapps.courseware.views.views import CourseTabView


@transaction.non_atomic_requests
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@ensure_valid_course_key
@data_sharing_consent_required
def video(request, course_id):
    print 'video called'

    """ Display the progress page. """
    course_key = CourseKey.from_string(course_id)

    course = get_course_with_access(request.user, 'load', course_key)

    # 강좌의 영상목록 생성 --- s

    client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'), settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
    db = client.edxapp

    o = course_id.split('+')[0].replace('course-v1:', '')
    c = course_id.split('+')[1]
    r = course_id.split('+')[2]

    active_versions = db.modulestore.active_versions.find({"org": o, "course": c, "run": r})

    temp_list = []

    for active_version in active_versions:
        pb = active_version.get('versions').get('published-branch')
        wiki_slug = active_version.get('search_targets').get('wiki_slug')

        if wiki_slug and pb:
            print 'published-branch is [%s]' % pb

            structure = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_type": "course"}}})
            block = structure.get('blocks')[0]

            course_fields = block.get('fields')
            chapters = course_fields.get('children')

            for chapter_type, chapter_id in chapters:
                # print block_type, block_id
                chapter = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_id": chapter_id, "fields.visible_to_staff_only": {"$ne": True}}}})

                if not 'blocks' in chapter:
                    continue

                chapter_fields = chapter['blocks'][0].get('fields')

                if not chapter_fields:
                    continue

                chapter_name = chapter_fields.get('display_name')
                chapter_start = chapter_fields.get('start')
                sequentials = chapter_fields.get('children')

                for sequential_type, sequential_id in sequentials:
                    sequential = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_id": sequential_id, "fields.visible_to_staff_only": {"$ne": True}}}})

                    if not 'blocks' in sequential:
                        continue

                    sequential_fields = sequential['blocks'][0].get('fields')

                    if not sequential_fields:
                        continue

                    sequential_name = sequential_fields.get('display_name')
                    sequential_start = sequential_fields.get('start')
                    verticals = sequential_fields.get('children')

                    for vertical_type, vertical_id in verticals:
                        vertical = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_id": vertical_id, "fields.visible_to_staff_only": {"$ne": True}}}})

                        if not 'blocks' in vertical:
                            continue

                        vertical_fields = vertical['blocks'][0].get('fields')

                        if not vertical_fields:
                            continue

                        xblocks = vertical_fields.get('children')

                        for xblock_type, xblock_id in xblocks:

                            if xblock_type != 'video':
                                continue

                            xblock = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_id": xblock_id}}})
                            xblock_fields = xblock['blocks'][0].get('fields')

                            if not xblock_fields:
                                continue

                            vertical_name = xblock_fields.get('display_name')

                            html5_sources = xblock_fields.get('html5_sources')

                            if not html5_sources:
                                continue

                            for html5_source in html5_sources:
                                # print org_name, classfy_name, middle_classfy_name, teacher_name, display_name, chapter_name, sequential_name, enrollment_start, enrollment_end, start, end, short_description, html5_source

                                if html5_source == '':
                                    continue

                                temp_dict = {
                                    'chapter_name': chapter_name,
                                    'chapter_id': chapter_id,
                                    'chapter_start': chapter_start,
                                    'sequential_name': sequential_name,
                                    'sequential_id': sequential_id,
                                    'sequential_start': sequential_start,
                                    'vertical_name': vertical_name,
                                    'vertical_id': vertical_id,
                                    'html5_source': html5_source
                                }

                                temp_list.append(temp_dict)

                                # print '----------------------------------------------------------- s'
                                # print chapter_name, chapter_start, sequential_name, sequential_start, vertical_name, html5_source
                                # print '----------------------------------------------------------- e'

    video_tree = {}

    _chapter_name1 = None
    _chapter_name2 = None
    _sequential_name1 = None
    _sequential_name2 = None
    _vertical_name1 = None
    _vertical_name2 = None
    _html5_source1 = None
    _html5_source2 = None
    chapter_list = []
    print 'video_tree check -------------------------------------------------------------->'

    # 주제
    for temp1 in temp_list:

        if True:
            _chapter_name1 = temp1['chapter_name']
            _chapter_id = temp1['chapter_id']
            _chapter_start = temp1['chapter_start']

            if _chapter_start and _chapter_start > datetime.utcnow():
                continue

            if not _chapter_name2:
                _chapter_name2 = temp1['chapter_name']
            elif _chapter_name1 and _chapter_name2 and _chapter_name1 == _chapter_name2:
                continue
            else:
                _chapter_name2 = temp1['chapter_name']

            # print _chapter_name2

            _sequential_name1 = None
            _sequential_name2 = None
            _sequential_start = None

            sequential_list = list()
            for temp2 in temp_list:
                if _chapter_name1 == temp2['chapter_name']:

                    _sequential_name1 = temp2['sequential_name']
                    _sequential_id = temp2['sequential_id']
                    _sequential_start = temp2['sequential_start']

                    if _sequential_start and _sequential_start > datetime.utcnow():
                        continue

                    if not _sequential_name2:
                        _sequential_name2 = temp2['sequential_name']
                    elif _sequential_name1 and _sequential_name2 and _sequential_name1 == _sequential_name2:
                        continue
                    else:
                        _sequential_name2 = temp2['sequential_name']

                    # print '\t', _sequential_name1

                    _html5_source1 = None
                    _html5_source2 = None

                    vertical_list = list()
                    for temp3 in temp_list:
                        if _chapter_name1 == temp3['chapter_name'] and _sequential_name1 == temp3['sequential_name']:

                            _html5_source1 = temp3['html5_source']

                            if not _html5_source2:
                                _html5_source2 = temp3['html5_source']
                            elif _html5_source1 and _html5_source2 and _html5_source1 == _html5_source2:
                                continue
                            else:
                                _html5_source2 = temp3['html5_source']

                            _vertical_name1 = temp3['vertical_name']
                            _vertical_id = temp3['vertical_id']

                            jump_url = 'http://{domain}/courses/{course_id}/jump_to/block-v1:{course}+type@vertical+block@{vertical_id}'.format(
                                domain=request.META.get('HTTP_HOST'),
                                course_id=course_id,
                                course=course_id.replace('course-v1:', ''),
                                vertical_id=_vertical_id
                            )

                            # print '\t\t', _vertical_name1, _html5_source2, jump_url

                            vertical_list.append({
                                'vertical_id': _vertical_id,
                                'vertical_name': _vertical_name1,
                                'video_url': _html5_source2,
                                'jump_url': jump_url
                            })

                    sequential_list.append({
                        'sequential_id': _sequential_id,
                        'sequential_name': _sequential_name1,
                        'vertical_list': vertical_list
                    })

            chapter_list.append({
                'chapter_id': _chapter_id,
                'chapter_name': _chapter_name1,
                'sequential_list': sequential_list
            })

    # 강좌의 영상목록 생성 --- e

    # print 'chapter_list ------------------------- s'
    # print chapter_list
    # print 'chapter_list ------------------------- e'

    CourseTabView.register_user_access_warning_messages(request, course_key)

    context = {
        'course': course,
        'chapter_list': chapter_list
    }

    return render_to_response('courseware/video.html', context)


@transaction.non_atomic_requests
@login_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@ensure_valid_course_key
@data_sharing_consent_required
def progress(request, course_id, student_id=None):
    """ Display the progress page. """
    course_key = CourseKey.from_string(course_id)

    with modulestore().bulk_operations(course_key):
        return _progress(request, course_key, student_id)


def _progress(request, course_key, student_id):
    """
    Unwrapped version of "progress".
    User progress. We show the grade bar and every problem score.
    Course staff are allowed to see the progress of students in their class.
    """

    if student_id is not None:
        try:
            student_id = int(student_id)
        # Check for ValueError if 'student_id' cannot be converted to integer.
        except ValueError:
            raise Http404

    course = get_course_with_access(request.user, 'load', course_key)

    staff_access = bool(has_access(request.user, 'staff', course))

    masquerade = None
    if student_id is None or student_id == request.user.id:
        # This will be a no-op for non-staff users, returning request.user
        masquerade, student = setup_masquerade(request, course_key, staff_access, reset_masquerade_data=True)
    else:
        try:
            coach_access = has_ccx_coach_role(request.user, course_key)
        except CCXLocatorValidationException:
            coach_access = False

        has_access_on_students_profiles = staff_access or coach_access
        # Requesting access to a different student's profile
        if not has_access_on_students_profiles:
            raise Http404
        try:
            student = User.objects.get(id=student_id)
        except User.DoesNotExist:
            raise Http404

    # NOTE: To make sure impersonation by instructor works, use
    # student instead of request.user in the rest of the function.

    # The pre-fetching of groups is done to make auth checks not require an
    # additional DB lookup (this kills the Progress page in particular).
    student = User.objects.prefetch_related("groups").get(id=student.id)
    if request.user.id != student.id:
        # refetch the course as the assumed student
        course = get_course_with_access(student, 'load', course_key, check_if_enrolled=True)

    # NOTE: To make sure impersonation by instructor works, use
    # student instead of request.user in the rest of the function.

    course_grade = CourseGradeFactory().read(student, course)
    courseware_summary = course_grade.chapter_grades.values()

    studio_url = get_studio_url(course, 'settings/grading')
    # checking certificate generation configuration
    enrollment_mode, _ = CourseEnrollment.enrollment_mode_for_user(student, course_key)

    context = {
        'course': course,
        'courseware_summary': courseware_summary,
        'studio_url': studio_url,
        'grade_summary': course_grade.summary,
        'staff_access': staff_access,
        'masquerade': masquerade,
        'supports_preview_menu': True,
        'student': student,
        'credit_course_requirements': _credit_course_requirements(course_key, student),
        'certificate_data': _get_cert_data(student, course, enrollment_mode, course_grade),
    }
    context.update(
        get_experiment_user_metadata_context(
            course,
            student,
        )
    )

    with outer_atomic():
        response = render_to_response('courseware/progress.html', context)

    return response


def _downloadable_certificate_message(course, cert_downloadable_status):
    if certs_api.has_html_certificates_enabled(course):
        if certs_api.get_active_web_certificate(course) is not None:
            return _downloadable_cert_data(
                download_url=None,
                cert_web_view_url=certs_api.get_certificate_url(
                    course_id=course.id, uuid=cert_downloadable_status['uuid']
                )
            )
        elif not cert_downloadable_status['download_url']:
            return GENERATING_CERT_DATA

    return _downloadable_cert_data(download_url=cert_downloadable_status['download_url'])


def _missing_required_verification(student, enrollment_mode):
    return (
            enrollment_mode in CourseMode.VERIFIED_MODES and not IDVerificationService.user_is_verified(student)
    )


def _certificate_message(student, course, enrollment_mode):
    if certs_api.is_certificate_invalid(student, course.id):
        return INVALID_CERT_DATA

    cert_downloadable_status = certs_api.certificate_downloadable_status(student, course.id)

    if cert_downloadable_status['is_generating']:
        return GENERATING_CERT_DATA

    if cert_downloadable_status['is_unverified'] or _missing_required_verification(student, enrollment_mode):
        return UNVERIFIED_CERT_DATA

    if cert_downloadable_status['is_downloadable']:
        return _downloadable_certificate_message(course, cert_downloadable_status)

    return REQUESTING_CERT_DATA


def _get_cert_data(student, course, enrollment_mode, course_grade=None):
    """Returns students course certificate related data.
    Arguments:
        student (User): Student for whom certificate to retrieve.
        course (Course): Course object for which certificate data to retrieve.
        enrollment_mode (String): Course mode in which student is enrolled.
        course_grade (CourseGrade): Student's course grade record.
    Returns:
        returns dict if course certificate is available else None.
    """
    if not CourseMode.is_eligible_for_certificate(enrollment_mode):
        return AUDIT_PASSING_CERT_DATA if enrollment_mode == CourseMode.AUDIT else HONOR_PASSING_CERT_DATA

    certificates_enabled_for_course = certs_api.cert_generation_enabled(course.id)
    if course_grade is None:
        course_grade = CourseGradeFactory().read(student, course)

    if not auto_certs_api.can_show_certificate_message(course, student, course_grade, certificates_enabled_for_course):
        return

    return _certificate_message(student, course, enrollment_mode)


def _credit_course_requirements(course_key, student):
    """Return information about which credit requirements a user has satisfied.
    Arguments:
        course_key (CourseKey): Identifier for the course.
        student (User): Currently logged in user.
    Returns: dict if the credit eligibility enabled and it is a credit course
    and the user is enrolled in either verified or credit mode, and None otherwise.
    """
    # If credit eligibility is not enabled or this is not a credit course,
    # short-circuit and return `None`.  This indicates that credit requirements
    # should NOT be displayed on the progress page.
    if not (settings.FEATURES.get("ENABLE_CREDIT_ELIGIBILITY", False) and is_credit_course(course_key)):
        return None

    # This indicates that credit requirements should NOT be displayed on the progress page.
    enrollment = CourseEnrollment.get_enrollment(student, course_key)
    if enrollment and enrollment.mode not in REQUIREMENTS_DISPLAY_MODES:
        return None

    # Credit requirement statuses for which user does not remain eligible to get credit.
    non_eligible_statuses = ['failed', 'declined']

    # Retrieve the status of the user for each eligibility requirement in the course.
    # For each requirement, the user's status is either "satisfied", "failed", or None.
    # In this context, `None` means that we don't know the user's status, either because
    # the user hasn't done something (for example, submitting photos for verification)
    # or we're waiting on more information (for example, a response from the photo
    # verification service).
    requirement_statuses = get_credit_requirement_status(course_key, student.username)

    # If the user has been marked as "eligible", then they are *always* eligible
    # unless someone manually intervenes.  This could lead to some strange behavior
    # if the requirements change post-launch.  For example, if the user was marked as eligible
    # for credit, then a new requirement was added, the user will see that they're eligible
    # AND that one of the requirements is still pending.
    # We're assuming here that (a) we can mitigate this by properly training course teams,
    # and (b) it's a better user experience to allow students who were at one time
    # marked as eligible to continue to be eligible.
    # If we need to, we can always manually move students back to ineligible by
    # deleting CreditEligibility records in the database.
    if is_user_eligible_for_credit(student.username, course_key):
        eligibility_status = "eligible"

    # If the user has *failed* any requirements (for example, if a photo verification is denied),
    # then the user is NOT eligible for credit.
    elif any(requirement['status'] in non_eligible_statuses for requirement in requirement_statuses):
        eligibility_status = "not_eligible"

    # Otherwise, the user may be eligible for credit, but the user has not
    # yet completed all the requirements.
    else:
        eligibility_status = "partial_eligible"

    return {
        'eligibility_status': eligibility_status,
        'requirements': requirement_statuses,
    }


@login_required
@ensure_valid_course_key
def submission_history(request, course_id, student_username, location):
    """Render an HTML fragment (meant for inclusion elsewhere) that renders a
    history of all state changes made by this user for this problem location.
    Right now this only works for problems because that's all
    StudentModuleHistory records.
    """

    course_key = CourseKey.from_string(course_id)

    try:
        usage_key = UsageKey.from_string(location).map_into_course(course_key)
    except (InvalidKeyError, AssertionError):
        return HttpResponse(escape(_(u'Invalid location.')))

    course = get_course_overview_with_access(request.user, 'load', course_key)
    staff_access = bool(has_access(request.user, 'staff', course))

    # Permission Denied if they don't have staff access and are trying to see
    # somebody else's submission history.
    if (student_username != request.user.username) and (not staff_access):
        raise PermissionDenied

    user_state_client = DjangoXBlockUserStateClient()
    try:
        history_entries = list(user_state_client.get_history(student_username, usage_key))
    except DjangoXBlockUserStateClient.DoesNotExist:
        return HttpResponse(escape(_(u'User {username} has never accessed problem {location}').format(
            username=student_username,
            location=location
        )))

    # This is ugly, but until we have a proper submissions API that we can use to provide
    # the scores instead, it will have to do.
    csm = StudentModule.objects.filter(
        module_state_key=usage_key,
        student__username=student_username,
        course_id=course_key)

    scores = BaseStudentModuleHistory.get_history(csm)

    if len(scores) != len(history_entries):
        log.warning(
            "Mismatch when fetching scores for student "
            "history for course %s, user %s, xblock %s. "
            "%d scores were found, and %d history entries were found. "
            "Matching scores to history entries by date for display.",
            course_id,
            student_username,
            location,
            len(scores),
            len(history_entries),
        )
        scores_by_date = {
            score.created: score
            for score in scores
        }
        scores = [
            scores_by_date[history.updated]
            for history in history_entries
        ]

    context = {
        'history_entries': history_entries,
        'scores': scores,
        'username': student_username,
        'location': location,
        'course_id': text_type(course_key)
    }

    return render_to_response('courseware/submission_history.html', context)


def get_static_tab_fragment(request, course, tab):
    """
    Returns the fragment for the given static tab
    """
    loc = course.id.make_usage_key(
        tab.type,
        tab.url_slug,
    )
    field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
        course.id, request.user, modulestore().get_item(loc), depth=0
    )
    tab_module = get_module(
        request.user, request, loc, field_data_cache, static_asset_path=course.static_asset_path, course=course
    )

    logging.debug('course_module = %s', tab_module)

    fragment = Fragment()
    if tab_module is not None:
        try:
            fragment = tab_module.render(STUDENT_VIEW, {})
        except Exception:  # pylint: disable=broad-except
            fragment.content = render_to_string('courseware/error-message.html', None)
            log.exception(
                u"Error rendering course=%s, tab=%s", course, tab['url_slug']
            )

    return fragment


@require_GET
@ensure_valid_course_key
def get_course_lti_endpoints(request, course_id):
    """
    View that, given a course_id, returns the a JSON object that enumerates all of the LTI endpoints for that course.
    The LTI 2.0 result service spec at
    http://www.imsglobal.org/lti/ltiv2p0/uml/purl.imsglobal.org/vocab/lis/v2/outcomes/Result/service.html
    says "This specification document does not prescribe a method for discovering the endpoint URLs."  This view
    function implements one way of discovering these endpoints, returning a JSON array when accessed.
    Arguments:
        request (django request object):  the HTTP request object that triggered this view function
        course_id (unicode):  id associated with the course
    Returns:
        (django response object):  HTTP response.  404 if course is not found, otherwise 200 with JSON body.
    """

    course_key = CourseKey.from_string(course_id)

    try:
        course = get_course(course_key, depth=2)
    except ValueError:
        return HttpResponse(status=404)

    anonymous_user = AnonymousUser()
    anonymous_user.known = False  # make these "noauth" requests like module_render.handle_xblock_callback_noauth
    lti_descriptors = modulestore().get_items(course.id, qualifiers={'category': 'lti'})
    lti_descriptors.extend(modulestore().get_items(course.id, qualifiers={'category': 'lti_consumer'}))

    lti_noauth_modules = [
        get_module_for_descriptor(
            anonymous_user,
            request,
            descriptor,
            FieldDataCache.cache_for_descriptor_descendents(
                course_key,
                anonymous_user,
                descriptor
            ),
            course_key,
            course=course
        )
        for descriptor in lti_descriptors
    ]

    endpoints = [
        {
            'display_name': module.display_name,
            'lti_2_0_result_service_json_endpoint': module.get_outcome_service_url(
                service_name='lti_2_0_result_rest_handler') + "/user/{anon_user_id}",
            'lti_1_1_result_service_xml_endpoint': module.get_outcome_service_url(
                service_name='grade_handler'),
        }
        for module in lti_noauth_modules
    ]

    return HttpResponse(json.dumps(endpoints), content_type='application/json')


@login_required
def course_survey(request, course_id):
    """
    URL endpoint to present a survey that is associated with a course_id
    Note that the actual implementation of course survey is handled in the
    views.py file in the Survey Djangoapp
    """

    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, 'load', course_key, check_survey_complete=False)

    redirect_url = reverse(course_home_url_name(course.id), args=[course_id])

    # if there is no Survey associated with this course,
    # then redirect to the course instead
    if not course.course_survey_name:
        return redirect(redirect_url)

    return survey.views.view_student_survey(
        request.user,
        course.course_survey_name,
        course=course,
        redirect_url=redirect_url,
        is_required=course.course_survey_required,
    )


def is_course_passed(student, course, course_grade=None):
    """
    check user's course passing status. return True if prows1assed
    Arguments:
        student : user object
        course : course object
        course_grade (CourseGrade) : contains student grade details.
    Returns:
        returns bool value
    """
    if course_grade is None:
        course_grade = CourseGradeFactory().read(student, course)
    return course_grade.passed


# Grades can potentially be written - if so, let grading manage the transaction.
@transaction.non_atomic_requests
@require_POST
def generate_user_cert(request, course_id):
    """Start generating a new certificate for the user.
    Certificate generation is allowed if:
    * The user has passed the course, and
    * The user does not already have a pending/completed certificate.
    Note that if an error occurs during certificate generation
    (for example, if the queue is down), then we simply mark the
    certificate generation task status as "error" and re-run
    the task with a management command.  To students, the certificate
    will appear to be "generating" until it is re-run.
    Args:
        request (HttpRequest): The POST request to this view.
        course_id (unicode): The identifier for the course.
    Returns:
        HttpResponse: 200 on success, 400 if a new certificate cannot be generated.
    """

    if not request.user.is_authenticated:
        log.info(u"Anon user trying to generate certificate for %s", course_id)
        return HttpResponseBadRequest(
            _('You must be signed in to {platform_name} to create a certificate.').format(
                platform_name=configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
            )
        )

    student = request.user
    course_key = CourseKey.from_string(course_id)

    course = modulestore().get_course(course_key, depth=2)
    if not course:
        return HttpResponseBadRequest(_("Course is not valid"))

    if not is_course_passed(student, course):
        log.info(u"User %s has not passed the course: %s", student.username, course_id)
        return HttpResponseBadRequest(_("Your certificate will be available when you pass the course."))

    certificate_status = certs_api.certificate_downloadable_status(student, course.id)

    log.info(
        u"User %s has requested for certificate in %s, current status: is_downloadable: %s, is_generating: %s",
        student.username,
        course_id,
        certificate_status["is_downloadable"],
        certificate_status["is_generating"],
    )

    if certificate_status["is_downloadable"]:
        return HttpResponseBadRequest(_("Certificate has already been created."))
    elif certificate_status["is_generating"]:
        return HttpResponseBadRequest(_("Certificate is being created."))
    else:
        # If the certificate is not already in-process or completed,
        # then create a new certificate generation task.
        # If the certificate cannot be added to the queue, this will
        # mark the certificate with "error" status, so it can be re-run
        # with a management command.  From the user's perspective,
        # it will appear that the certificate task was submitted successfully.
        certs_api.generate_user_certificates(student, course.id, course=course, generation_mode='self')
        _track_successful_certificate_generation(student.id, course.id)
        return HttpResponse()


def _track_successful_certificate_generation(user_id, course_id):  # pylint: disable=invalid-name
    """
    Track a successful certificate generation event.
    Arguments:
        user_id (str): The ID of the user generating the certificate.
        course_id (CourseKey): Identifier for the course.
    Returns:
        None
    """
    if settings.LMS_SEGMENT_KEY:
        event_name = 'edx.bi.user.certificate.generate'
        tracking_context = tracker.get_tracker().resolve_context()

        analytics.track(
            user_id,
            event_name,
            {
                'category': 'certificates',
                'label': text_type(course_id)
            },
            context={
                'ip': tracking_context.get('ip'),
                'Google Analytics': {
                    'clientId': tracking_context.get('client_id')
                }
            }
        )


@require_http_methods(["GET", "POST"])
@ensure_valid_usage_key
def render_xblock(request, usage_key_string, check_if_enrolled=True):
    """
    Returns an HttpResponse with HTML content for the xBlock with the given usage_key.
    The returned HTML is a chromeless rendering of the xBlock (excluding content of the containing courseware).
    """
    usage_key = UsageKey.from_string(usage_key_string)

    usage_key = usage_key.replace(course_key=modulestore().fill_in_run(usage_key.course_key))
    course_key = usage_key.course_key

    requested_view = request.GET.get('view', 'student_view')
    if requested_view != 'student_view':
        return HttpResponseBadRequest(
            "Rendering of the xblock view '{}' is not supported.".format(bleach.clean(requested_view, strip=True))
        )

    with modulestore().bulk_operations(course_key):
        # verify the user has access to the course, including enrollment check
        try:
            course = get_course_with_access(request.user, 'load', course_key, check_if_enrolled=check_if_enrolled)
        except CourseAccessRedirect:
            raise Http404("Course not found.")

        # get the block, which verifies whether the user has access to the block.
        block, _ = get_module_by_usage_id(
            request, text_type(course_key), text_type(usage_key), disable_staff_debug_info=True, course=course
        )

        student_view_context = request.GET.dict()
        student_view_context['show_bookmark_button'] = False

        enable_completion_on_view_service = False
        completion_service = block.runtime.service(block, 'completion')
        if completion_service and completion_service.completion_tracking_enabled():
            if completion_service.blocks_to_mark_complete_on_view({block}):
                enable_completion_on_view_service = True
                student_view_context['wrap_xblock_data'] = {
                    'mark-completed-on-view-after-delay': completion_service.get_complete_on_view_delay_ms()
                }

        context = {
            'fragment': block.render('student_view', context=student_view_context),
            'course': course,
            'disable_accordion': True,
            'allow_iframing': True,
            'disable_header': True,
            'disable_footer': True,
            'disable_window_wrap': True,
            'enable_completion_on_view_service': enable_completion_on_view_service,
            'staff_access': bool(has_access(request.user, 'staff', course)),
            'xqa_server': settings.FEATURES.get('XQA_SERVER', 'http://your_xqa_server.com'),
        }
        return render_to_response('courseware/courseware-chromeless.html', context)


# Translators: "percent_sign" is the symbol "%". "platform_name" is a
# string identifying the name of this installation, such as "edX".
FINANCIAL_ASSISTANCE_HEADER = _(
    '{platform_name} now offers financial assistance for learners who want to earn Verified Certificates but'
    ' who may not be able to pay the Verified Certificate fee. Eligible learners may receive up to 90{percent_sign} off'
    ' the Verified Certificate fee for a course.\nTo apply for financial assistance, enroll in the'
    ' audit track for a course that offers Verified Certificates, and then complete this application.'
    ' Note that you must complete a separate application for each course you take.\n We plan to use this'
    ' information to evaluate your application for financial assistance and to further develop our'
    ' financial assistance program.'
).format(
    percent_sign="%",
    platform_name=configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
).split('\n')

FA_INCOME_LABEL = _('Annual Household Income')
FA_REASON_FOR_APPLYING_LABEL = _(
    'Tell us about your current financial situation. Why do you need assistance?'
)
FA_GOALS_LABEL = _(
    'Tell us about your learning or professional goals. How will a Verified Certificate in'
    ' this course help you achieve these goals?'
)
FA_EFFORT_LABEL = _(
    'Tell us about your plans for this course. What steps will you take to help you complete'
    ' the course work and receive a certificate?'
)
FA_SHORT_ANSWER_INSTRUCTIONS = _('Use between 250 and 500 words or so in your response.')


@login_required
def financial_assistance(_request):
    """Render the initial financial assistance page."""
    return render_to_response('financial-assistance/financial-assistance.html', {
        'header_text': FINANCIAL_ASSISTANCE_HEADER
    })


@login_required
@require_POST
def financial_assistance_request(request):
    """Submit a request for financial assistance to Zendesk."""
    try:
        data = json.loads(request.body)
        # Simple sanity check that the session belongs to the user
        # submitting an FA request
        username = data['username']
        if request.user.username != username:
            return HttpResponseForbidden()

        course_id = data['course']
        course = modulestore().get_course(CourseKey.from_string(course_id))
        legal_name = data['name']
        email = data['email']
        country = data['country']
        income = data['income']
        reason_for_applying = data['reason_for_applying']
        goals = data['goals']
        effort = data['effort']
        marketing_permission = data['mktg-permission']
        ip_address = get_ip(request)
    except ValueError:
        # Thrown if JSON parsing fails
        return HttpResponseBadRequest(u'Could not parse request JSON.')
    except InvalidKeyError:
        # Thrown if course key parsing fails
        return HttpResponseBadRequest(u'Could not parse request course key.')
    except KeyError as err:
        # Thrown if fields are missing
        return HttpResponseBadRequest(u'The field {} is required.'.format(text_type(err)))

    zendesk_submitted = _record_feedback_in_zendesk(
        legal_name,
        email,
        u'Financial assistance request for learner {username} in course {course_name}'.format(
            username=username,
            course_name=course.display_name
        ),
        u'Financial Assistance Request',
        {'course_id': course_id},
        # Send the application as additional info on the ticket so
        # that it is not shown when support replies. This uses
        # OrderedDict so that information is presented in the right
        # order.
        OrderedDict((
            ('Username', username),
            ('Full Name', legal_name),
            ('Course ID', course_id),
            ('Annual Household Income', income),
            ('Country', country),
            ('Allowed for marketing purposes', 'Yes' if marketing_permission else 'No'),
            (FA_REASON_FOR_APPLYING_LABEL, '\n' + reason_for_applying + '\n\n'),
            (FA_GOALS_LABEL, '\n' + goals + '\n\n'),
            (FA_EFFORT_LABEL, '\n' + effort + '\n\n'),
            ('Client IP', ip_address),
        )),
        group_name='Financial Assistance',
        require_update=True
    )

    if not zendesk_submitted:
        # The call to Zendesk failed. The frontend will display a
        # message to the user.
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@login_required
def financial_assistance_form(request):
    """Render the financial assistance application form page."""
    user = request.user
    enrolled_courses = get_financial_aid_courses(user)
    incomes = ['Less than $5,000', '$5,000 - $10,000', '$10,000 - $15,000', '$15,000 - $20,000', '$20,000 - $25,000']
    annual_incomes = [
        {'name': _(income), 'value': income} for income in incomes  # pylint: disable=translation-of-non-string
    ]
    return render_to_response('financial-assistance/apply.html', {
        'header_text': FINANCIAL_ASSISTANCE_HEADER,
        'student_faq_url': marketing_link('FAQ'),
        'dashboard_url': reverse('dashboard'),
        'account_settings_url': reverse('account_settings'),
        'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
        'user_details': {
            'email': user.email,
            'username': user.username,
            'name': user.profile.name,
            'country': text_type(user.profile.country.name),
        },
        'submit_url': reverse('submit_financial_assistance_request'),
        'fields': [
            {
                'name': 'course',
                'type': 'select',
                'label': _('Course'),
                'placeholder': '',
                'defaultValue': '',
                'required': True,
                'options': enrolled_courses,
                'instructions': _(
                    'Select the course for which you want to earn a verified certificate. If'
                    ' the course does not appear in the list, make sure that you have enrolled'
                    ' in the audit track for the course.'
                )
            },
            {
                'name': 'income',
                'type': 'select',
                'label': FA_INCOME_LABEL,
                'placeholder': '',
                'defaultValue': '',
                'required': True,
                'options': annual_incomes,
                'instructions': _('Specify your annual household income in US Dollars.')
            },
            {
                'name': 'reason_for_applying',
                'type': 'textarea',
                'label': FA_REASON_FOR_APPLYING_LABEL,
                'placeholder': '',
                'defaultValue': '',
                'required': True,
                'restrictions': {
                    'min_length': settings.FINANCIAL_ASSISTANCE_MIN_LENGTH,
                    'max_length': settings.FINANCIAL_ASSISTANCE_MAX_LENGTH
                },
                'instructions': FA_SHORT_ANSWER_INSTRUCTIONS
            },
            {
                'name': 'goals',
                'type': 'textarea',
                'label': FA_GOALS_LABEL,
                'placeholder': '',
                'defaultValue': '',
                'required': True,
                'restrictions': {
                    'min_length': settings.FINANCIAL_ASSISTANCE_MIN_LENGTH,
                    'max_length': settings.FINANCIAL_ASSISTANCE_MAX_LENGTH
                },
                'instructions': FA_SHORT_ANSWER_INSTRUCTIONS
            },
            {
                'name': 'effort',
                'type': 'textarea',
                'label': FA_EFFORT_LABEL,
                'placeholder': '',
                'defaultValue': '',
                'required': True,
                'restrictions': {
                    'min_length': settings.FINANCIAL_ASSISTANCE_MIN_LENGTH,
                    'max_length': settings.FINANCIAL_ASSISTANCE_MAX_LENGTH
                },
                'instructions': FA_SHORT_ANSWER_INSTRUCTIONS
            },
            {
                'placeholder': '',
                'name': 'mktg-permission',
                'label': _(
                    'I allow edX to use the information provided in this application '
                    '(except for financial information) for edX marketing purposes.'
                ),
                'defaultValue': '',
                'type': 'checkbox',
                'required': False,
                'instructions': '',
                'restrictions': {}
            }
        ],
    })


def get_financial_aid_courses(user):
    """ Retrieve the courses eligible for financial assistance. """
    financial_aid_courses = []
    for enrollment in CourseEnrollment.enrollments_for_user(user).order_by('-created'):

        if enrollment.mode != CourseMode.VERIFIED and \
                enrollment.course_overview and \
                enrollment.course_overview.eligible_for_financial_aid and \
                CourseMode.objects.filter(
                    Q(_expiration_datetime__isnull=True) | Q(_expiration_datetime__gt=datetime.now(UTC)),
                    course_id=enrollment.course_id,
                    mode_slug=CourseMode.VERIFIED).exists():
            financial_aid_courses.append(
                {
                    'name': enrollment.course_overview.display_name,
                    'value': text_type(enrollment.course_id)
                }
            )

    return financial_aid_courses


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


@ensure_csrf_cookie
@cache_if_anonymous()
def schools(request):
    return render_to_response("courseware/schools.html")


@ensure_csrf_cookie
@cache_if_anonymous()
def schools_make_filter(request):
    with connections['default'].cursor() as cur:
        query = '''
            select detail_name, detail_code, detail_ename
            from code_detail
            where group_code = '041'
            and use_yn = 'Y'
            and delete_yn = 'N';
        '''.format()

        print query
        cur.execute(query)
        rows = cur.fetchall()
        print rows

    year_list = []
    current_year = int(datetime.now().year)
    for year in range(2015, current_year+1):
        year_list.append(year)

    print 'current_year = ', current_year

    search_filter = {
        'org_type': rows,
        'year_list': year_list,
        'lang': request.LANGUAGE_CODE
    }

    return JsonResponse({'result': search_filter})


@ensure_csrf_cookie
@cache_if_anonymous()
def schools_make_item(request):
    f_year_filter = request.POST.get('f_year_filter')
    f_org_filter = request.POST.get('f_org_filter')
    f_name_filter = request.POST.get('f_name_filter')
    lang = request.LANGUAGE_CODE

    if f_year_filter == '':
        f_year_filter = 'A'
    if f_org_filter == '':
        f_org_filter = 'A'

    print "f_year_filter = ", f_year_filter
    print "f_org_filter = ", f_org_filter
    print "f_name_filter = ", f_name_filter
    print "lang = ", lang

    search_query = ''
    if f_year_filter != 'A':
        search_query += "and start_year = '{f_year_filter}' ".format(f_year_filter=f_year_filter)
    if f_org_filter != 'A':
        search_query += "and raw_org_type = '{f_org_filter}' ".format(f_org_filter=f_org_filter)
    if f_name_filter != '':
        search_query += "and univ_name like '%{f_name_filter}%' or univ_name_e like '%{f_name_filter}%' ".format(f_name_filter=f_name_filter)

    with connections['default'].cursor() as cur:
        query = '''
            select *
            from (
                select 
                    org_id,
                    a.start_year,
                    case
                    when org_intro is null
                    then 'N'
                    else 'Y'
                    end check_intro,
                    b.detail_name as univ_name,
                    b.detail_ename as univ_name_e,
                    ifnull((SELECT save_path FROM tb_attach WHERE use_yn = 1 AND id = a.logo_img), 'null1') logo_img,
                    ifnull((SELECT save_path FROM tb_attach WHERE use_yn = 1 AND id = a.logo_img_e), 'null2') logo_img_e,
                    IF(org_phone is null or org_phone = '', '-', org_phone) org_phone,
                    c.detail_name as org_type,
                    c.detail_ename as org_type_e,
                    org_type as raw_org_type
                from tb_org a
                JOIN code_detail b 
                ON a.org_id = b.detail_code
                AND b.group_code = '003'
                JOIN code_detail c
                ON a.org_type = c.detail_code
                AND c.group_code = '041'
                where a.use_yn = '1'
            ) w
            where start_year != ''
            and start_year is not null
            {search_query}
            order by start_year;
        '''.format(search_query=search_query)

        print query
        cur.execute(query)
        rows = dictfetchall(cur)
        print rows

    return JsonResponse({'result': rows, 'lang': lang})


@ensure_csrf_cookie
@cache_if_anonymous()
def haewoondaex(request, org):
    lang = request.LANGUAGE_CODE
    user = request.user

    f1 = None if user.is_staff else {'enrollment_start__isnull': False, 'enrollment_start__lte': datetime.now()}
    log.info(f1)
    courses_list = get_courses(user, org=org, filter_=f1)

    course_discovery_meanings = getattr(settings, 'COURSE_DISCOVERY_MEANINGS', False)

    with connections['default'].cursor() as cur:
        lang_subtitle = 'intro_subtitle' if lang == 'ko-kr' else 'intro_subtitle_e'
        lang_top = 'top_img' if lang == 'ko-kr' else 'top_img_e'
        lang_org_name = 'c.detail_name' if lang == 'ko-kr' else 'c.detail_ename'
        query = '''
            SELECT org_id,
                   ifnull(b.save_path, '') top_img,
                   ifnull(d.save_path, '') intro_subtitle,
                   homepage,
                   youtube,
                   facebook,
                   kakaostory,
                   naverblog,
                   instagram,
                   ifnull(intro_mov, ''),
                   {lang_org_name}
              FROM tb_org a
                   LEFT JOIN
                   (SELECT id, save_path
                      FROM tb_attach
                     WHERE use_yn = TRUE) b
                      ON (case when '{lang}' = 'ko-kr' then a.top_img else ifnull(a.top_img_e, a.top_img) end) = b.id
                   LEFT JOIN
                   (SELECT id, save_path
                      FROM tb_attach
                     WHERE     use_yn = TRUE) d
                      ON (case when '{lang}' = 'ko-kr' then a.intro_subtitle else ifnull(a.intro_subtitle_e, a.intro_subtitle) end) = d.id
                   JOIN code_detail c ON a.org_id = c.detail_code AND group_code = '003'
             WHERE org_id = '{org}' AND a.use_yn = TRUE;
        '''.format(lang=lang, lang_org_name=lang_org_name, org=org)

        print query
        cur.execute(query)
        org_data = cur.fetchone()

        org_dict = dict()
        org_dict['org_id'] = org_data[0]
        org_dict['top_img'] = org_data[1]
        org_dict['intro_subtitle'] = org_data[2]
        org_dict['homepage'] = org_data[3]
        org_dict['youtube'] = org_data[4]
        org_dict['facebook'] = org_data[5]
        org_dict['kakaostory'] = org_data[6]
        org_dict['naverblog'] = org_data[7]
        org_dict['instagram'] = org_data[8]
        org_dict['intro_mov'] = org_data[9]
        org_dict['org_name'] = org_data[10]

    return render_to_response(
        "courseware/univ_intro_base.html",
        {'courses': courses_list, 'course_discovery_meanings': course_discovery_meanings,
         'org_dict': org_dict}
    )


def school_view(request, org):
    lang = request.LANGUAGE_CODE
    with connections['default'].cursor() as cur:
        lang_intro = 'org_intro' if lang == 'ko-kr' else 'org_intro_e'
        query = '''
                    SELECT {lang_intro}
                      FROM tb_org a
                     WHERE org_id = '{org}' AND delete_yn = FALSE AND use_yn = TRUE;
                '''.format(lang_intro=lang_intro, org=org)

        print query

        cur.execute(query)
        intro_data = cur.fetchone()

        return JsonResponse({'org_intro': intro_data})


@login_required
@require_POST
def course_review(request):
    return render_to_response("courseware/course_review.html")


def course_review_add(request):
    user_id = request.POST.get('user_id')
    course_id = request.POST.get('course_id')
    review = request.POST.get('review')
    point = request.POST.get("star")

    lock = 0

    if request.is_ajax():

        with connections['default'].cursor() as cur:
            query = """
                select id
                from course_review
                where course_id='{course_id}'and user_id='{user_id}'
            """.format(user_id=user_id, course_id=course_id)
            cur.execute(query)
            check = cur.fetchall()

            if check != ():
                return JsonResponse({"data": "false"})

            else:
                with connections['default'].cursor() as cur:
                    query = """
                        insert into edxapp.course_review(content,
                                                        point,
                                                        user_id,
                                                        course_id)
                        values('{review}',
                                '{point}',
                                '{user_id}',
                                '{course_id}')
                    """.format(user_id=user_id, course_id=course_id, point=point, review=review)
                    cur.execute(query)

                return JsonResponse({"data": "success"})


def course_review_del(request):
    course_id = request.POST.get('course_id')
    id = request.POST.get('id')
    user_id = request.POST.get('user_id')

    if request.is_ajax():
        with connections['default'].cursor() as cur:
            query = """
                delete from course_review
                where id='{id}'
            """.format(id=id)
            cur.execute(query)
        with connections['default'].cursor() as cur:
            query = """
                delete from course_review_user
                where review_seq='{id}'
            """.format(id=id)
            cur.execute(query)

    return JsonResponse({"data": "success"})


def course_review_gb(request):
    review_id = request.POST.get('review_id')
    user_id = request.POST.get('user_id')
    gb = request.POST.get('gb')
    review_seq = request.POST.get('review_seq')

    if request.is_ajax():

        with connections['default'].cursor() as cur:
            query = """
                select good_bad
                from course_review_user
                where review_id='{review_id}' and user_id = '{user_id}';
            """.format(review_id=review_id, user_id=user_id)
            cur.execute(query)
            check = cur.fetchall()

            if check == ():
                with connections['default'].cursor() as cur:
                    query = """
                        insert into edxapp.course_review_user(review_id,
                                                        user_id,
                                                        good_bad,
                                                        review_seq)
                        values('{review_id}',
                                '{user_id}',
                                '{gb}',
                                '{review_seq}')
                    """.format(review_id=review_id, gb=gb, user_id=user_id, review_seq=review_seq)
                    cur.execute(query)

                    print " insert ok"
                return JsonResponse({"data": "success"})

            elif check[0][0] == gb:
                with connections['default'].cursor() as cur:
                    query = """
                        delete from edxapp.course_review_user
                        where review_id='{review_id}' and user_id = '{user_id}';
                    """.format(review_id=review_id, user_id=user_id)
                    cur.execute(query)
                    print " delete ok"
                return JsonResponse({"data": "delete"})

            elif check[0][0] != gb:
                print " ok"
                return JsonResponse({"data": "false"})


@ensure_csrf_cookie
@cache_if_anonymous()
def agreement(request):
    if _("Agree") == "Agree":
        return render_to_response(
            "courseware/agreement_en.html"
        )
    else:
        return render_to_response(
            "courseware/agreement.html"
        )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy(request):
    if _("Agree") == "Agree":
        return render_to_response(
            "courseware/privacy_en.html"
        )
    else:
        return render_to_response(
            "courseware/privacy.html"
        )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy_old1(request):
    return render_to_response(
        "courseware/privacy_old1.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy_old2(request):
    return render_to_response(
        "courseware/privacy_old2.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy_old3(request):
    return render_to_response(
        "courseware/privacy_old3.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy_old3(request):
    return render_to_response(
        "courseware/privacy_old3.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy_old4(request):
    return render_to_response(
        "courseware/privacy_old4.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy_old5(request):
    return render_to_response(
        "courseware/privacy_old5.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def privacy_old7(request):
    return render_to_response(
        "courseware/privacy_old7.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def copyright(request):
    return render_to_response(
        "courseware/copyright.html"
    )


@ensure_csrf_cookie
@cache_if_anonymous()
def cert_check(request):
    return render_to_response("courseware/cert_check.html")


def cert_check_id(request):
    uuid = request.POST['uuid']

    with connections['default'].cursor() as cur:
        sql = '''
            select concat('/certificates/user/', user_id,'/course/', course_id) certUrl 
            from certificates_generatedcertificate 
            where verify_uuid = '{uuid}'
        '''.format(uuid=uuid)
        cur.execute(sql)
        rows = cur.fetchall()

    if len(rows) == 0:
        with connections['default'].cursor() as cur:
            sql = '''
                select date_format(change_date_kst, '%Y-%m-%d %H:%i:%s')
                from certificates_generatedcertificate_trigger
                where verify_uuid = '{uuid}'
                order by change_date_kst desc
                limit 1
            '''.format(uuid=uuid)
            print('-------------------------------')
            print(sql)
            print('-------------------------------')
            cur.execute(sql)
            history = cur.fetchall()
            if len(history) == 0:
                return JsonResponse({'result': 404})
            else:
                change_date_kst = history[0][0]
                return JsonResponse({'result': 200, 'change_date_kst': change_date_kst})
    else:
        url = rows[0][0]
        return JsonResponse({'result': 200, 'url': url})


def save_search_term(request):
    term = request.POST.get('term')
    status = request.POST.get('status')
    count = request.POST.get('count')
    tmp = request.POST.get('tmp')

    # print '----------', status
    # aaa =urllib.unquote(status)
    # print type(aaa)
    # bbb = aaa.encode("utf-8")
    # # print unicode(aaa, "UTF-8")
    # print bbb.encode("utf-8")
    # print bbb.decode("utf-8")
    # print urllib.unquote(status)
    # print urllib.unquote(status).encode('utf8')
    # print urllib.unquote(status).decode('utf8')
    # print urllib.quote(status)
    # print urllib.quote(status).encode('utf8')
    # print urllib.quote(status).decode('utf8')
    # print urllib.unquote(urllib.unquote(status))
    # print status
    # print term

    # print 'tmptmp',tmp

    try:
        if tmp == 'o':
            location = 'header'
        else:
            location = 'discovery'
    except:
        location = 'bug'
    user = request.user

    with connections['default'].cursor() as cur:
        sql = '''
            INSERT INTO tb_search_result(search_word,search_from,search_count,regist_id)
            VALUES('{term}','{location}','{count}','{user}')
        '''.format(term=term, user=user.id, count=count, location=location)
        cur.execute(sql)

    return JsonResponse({'return': 'ok'})


def blue_ribbon_year(request):
    with connections['default'].cursor() as cur:
        sql = '''
           select course_id, ribbon_year from course_overview_addinfo where ribbon_yn  ='Y'
        '''
        cur.execute(sql)
        rows = cur.fetchall()

    data = dict()
    for row in rows:
        try:
            data[row[0]] = row[1]
        except:
            pass

    return JsonResponse(data)


def recognition(request):
    org_info = request.POST.get('org')
    student_no = request.POST.get('student_no')
    email = request.POST.get('email')
    course_id = request.POST.get('course_id')
    user = request.user.id
    org_info = org_info.split(',')
    try:
        with connections['default'].cursor() as cur:
            sql = '''
                  INSERT INTO tb_enroll_addinfo(course_id, org, org_name,org_type,student_no, email, regist_id) 
                  VALUES ('{course_id}','{org}','{org_name}','{org_type}','{student_no}','{email}','{regist_id}');
    
               '''.format(course_id=course_id, org=org_info[0], org_name=org_info[1], org_type=org_info[2],
                          student_no=student_no, email=email, regist_id=user)
            cur.execute(sql)
            return JsonResponse({"return": "success"})
    except:
        return JsonResponse({"return": "fail"})
