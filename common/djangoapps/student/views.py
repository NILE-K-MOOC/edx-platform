# -*- coding: utf-8 -*-
"""
Student Views
"""
import datetime
from django.utils.timezone import UTC as UTC2
import logging
import uuid
import json
import warnings
from collections import defaultdict
from urlparse import urljoin, urlsplit, parse_qs, urlunsplit
from django.views.generic import TemplateView
from pytz import UTC
from requests import HTTPError
from ipware.ip import get_ip
import edx_oauth2_provider
from django.conf import settings
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset_confirm
from django.contrib import messages
from django.core.context_processors import csrf
from django.core import mail
from django.core.urlresolvers import reverse, NoReverseMatch, reverse_lazy
from django.core.validators import validate_email, ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError, Http404
from django.shortcuts import redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ungettext
from django.utils.http import base36_to_int, urlsafe_base64_encode, urlencode
from django.utils.translation import ugettext as _, get_language
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.template.response import TemplateResponse
from provider.oauth2.models import Client
from ratelimitbackend.exceptions import RateLimitException
from social.apps.django_app import utils as social_utils
from social.backends import oauth as social_oauth
from social.exceptions import AuthException, AuthAlreadyAssociated
from edxmako.shortcuts import render_to_response, render_to_string
from course_modes.models import CourseMode
from shoppingcart.api import order_history
from student.models import (
    Registration, UserProfile,
    PendingEmailChange, CourseEnrollment, CourseEnrollmentAttribute, unique_id_for_user,
    CourseEnrollmentAllowed, UserStanding, LoginFailures,
    create_comments_service_user, PasswordHistory, UserSignupSource,
    DashboardConfiguration, LinkedInAddToProfileConfiguration, ManualEnrollmentAudit, ALLOWEDTOENROLL_TO_ENROLLED,
    LogoutViewConfiguration)
from student.forms import AccountCreationForm, PasswordResetFormNoActive, get_registration_extension_form
from lms.djangoapps.commerce.utils import EcommerceService  # pylint: disable=import-error
from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification  # pylint: disable=import-error
from bulk_email.models import Optout, BulkEmailFlag  # pylint: disable=import-error
from certificates.models import CertificateStatuses, certificate_status_for_student
from certificates.api import (  # pylint: disable=import-error
    get_certificate_url,
    has_html_certificates_enabled,
)
from xmodule.modulestore.django import modulestore
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys.edx.locator import CourseLocator
from collections import namedtuple
from courseware.courses import get_courses, sort_by_announcement, sort_by_start_date  # pylint: disable=import-error
from courseware.access import has_access
from django_comment_common.models import Role
from external_auth.models import ExternalAuthMap
import external_auth.views
from external_auth.login_and_register import (
    login as external_auth_login,
    register as external_auth_register
)
from lang_pref import LANGUAGE_KEY
import track.views
import dogstats_wrapper as dog_stats_api
from util.db import outer_atomic
from util.json_request import JsonResponse
from util.bad_request_rate_limiter import BadRequestRateLimiter
from util.milestones_helpers import (
    get_pre_requisite_courses_not_completed,
)
from util.password_policy_validators import validate_password_strength
import third_party_auth
from third_party_auth import pipeline, provider
from student.helpers import (
    check_verify_status_by_course,
    auth_pipeline_urls, get_next_url_for_login_page,
    DISABLE_UNENROLL_CERT_STATES,
)
from student.cookies import set_logged_in_cookies, delete_logged_in_cookies
from student.models import anonymous_id_for_user, UserAttribute, EnrollStatusChange
from shoppingcart.models import DonationConfiguration, CourseRegistrationCode
from embargo import api as embargo_api
import analytics
from eventtracking import tracker
# Note that this lives in LMS, so this dependency should be refactored.
from notification_prefs.views import enable_notifications
from openedx.core.djangoapps.credit.email_utils import get_credit_provider_display_names, make_providers_strings
from openedx.core.djangoapps.user_api.preferences import api as preferences_api
from openedx.core.djangoapps.programs.utils import get_programs_for_dashboard, get_display_category
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.theming import helpers as theming_helpers
import re
from django.core.serializers.json import DjangoJSONEncoder
import traceback
from courseware import grades
from courseware.courses import (
    get_courses,
    get_course_with_access,
    sort_by_announcement,
    sort_by_start_date,
)
from django.views.decorators.cache import cache_control
from util.views import ensure_valid_course_key
from pymongo import MongoClient
import MySQLdb as mdb
from django.db import connections
from django.db.models import Q
import sys

log = logging.getLogger("edx.student")
AUDIT_LOG = logging.getLogger("audit")
ReverifyInfo = namedtuple('ReverifyInfo',
                          'course_id course_name course_number date status display')  # pylint: disable=invalid-name
SETTING_CHANGE_INITIATED = 'edx.user.settings.change_initiated'
# Used as the name of the user attribute for tracking affiliate registrations
REGISTRATION_AFFILIATE_ID = 'registration_affiliate_id'
# used to announce a registration
REGISTER_USER = Signal(providing_args=["user", "profile"])


# Disable this warning because it doesn't make sense to completely refactor tests to appease Pylint
# pylint: disable=logging-format-interpolation
# pylint: disable=logging-format-interpolation


def csrf_token(context):
    """A csrf token that can be included in a form."""
    token = context.get('csrf_token', '')
    if token == 'NOTPROVIDED':
        return ''
    return (u'<div style="display:none"><input type="hidden"'
            ' name="csrfmiddlewaretoken" value="%s" /></div>' % (token))


def common_course_status(startDt, endDt):
    # input
    # case - 1
    # startDt = 2016-12-19 00:00:00
    # endDt   = 2017-02-10 23:00:00
    # nowDt   = 2017-11-10 00:11:28

    # case - 2
    # startDt = 2016-12-19 00:00:00+00:00
    # endDt   = 2017-02-10 23:00:00+00:00
    # nowDt   = 2017-11-10 00:11:28

    # import
    from datetime import datetime
    from django.utils.timezone import UTC as UTC2

    startDt = startDt.strftime("%Y-%m-%d-%H-%m-%S")
    startDt = startDt.split('-')
    startDt = datetime(int(startDt[0]), int(startDt[1]), int(startDt[2]), int(startDt[3]), int(startDt[4]),
                       int(startDt[5]))

    endDt = endDt.strftime("%Y-%m-%d-%H-%m-%S")
    endDt = endDt.split('-')
    endDt = datetime(int(endDt[0]), int(endDt[1]), int(endDt[2]), int(endDt[3]), int(endDt[4]), int(endDt[5]))

    # making nowDt
    nowDt = datetime.now(UTC2()).strftime("%Y-%m-%d-%H-%m-%S")
    nowDt = nowDt.split('-')
    nowDt = datetime(int(nowDt[0]), int(nowDt[1]), int(nowDt[2]), int(nowDt[3]), int(nowDt[4]), int(nowDt[5]))

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


# -------------------- multi site -------------------- #
def multisite_index(request, extra_context=None, user=AnonymousUser()):
    if extra_context is None:
        extra_context = {}
    user = request.user

    # import
    from xmodule.modulestore.django import modulestore
    from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

    # session check
    site_code = request.session.get('org')

    # multisite - get site code query
    with connections['default'].cursor() as cur:
        query = """
            SELECT site_id
            FROM   edxapp.multisite
            WHERE  site_code = '{0}'
        """.format(site_code)
        cur.execute(query)
        result_table = cur.fetchall()
    try:
        site_id = result_table[0][0]
    except BaseException:
        site_id = None
        course_list = []

    if site_id != None:

        # list init
        course_list = []
        module_store = modulestore()

        # get search data
        if request.GET.get('search_query') != None:

            search_name = str(request.GET.get('search_query'))

            # multisite - get site id query
            with connections['default'].cursor() as cur:
                query = """
                    SELECT mc.course_id, coc.display_name
                    FROM   edxapp.multisite_course AS mc
                    JOIN     edxapp.course_overviews_courseoverview AS coc
                    ON mc.course_id = coc.id
                    WHERE  site_id = {0}
                    AND coc.display_name like '%{1}%'
                """.format(site_id, search_name)
                cur.execute(query)
                result_table = cur.fetchall()

            for item in result_table:
                ci = item[0]
                ci = ci.split(':')
                data_ci = ci[1]
                data_ci = data_ci.split('+')
                c_org = data_ci[0]
                c_course = data_ci[1]
                c_name = data_ci[2]
                multi_course_id = module_store.make_course_key(c_org, c_course, c_name)
                course_overviews = CourseOverview.objects.get(id=multi_course_id)
                course_list.append(course_overviews)

            # multisite - make course status
            for c in course_list:
                c.status = common_course_status(c.start, c.end)

            context = {'courses': course_list}

        # base logic
        else:
            # multisite - get site id query
            with connections['default'].cursor() as cur:
                query = """
                    SELECT course_id
                    FROM   edxapp.multisite_course
                    WHERE  site_id = '{0}';
                """.format(site_id)
                cur.execute(query)
                result_table = cur.fetchall()

            for item in result_table:
                ci = item[0]
                ci = ci.split(':')
                data_ci = ci[1]
                data_ci = data_ci.split('+')
                c_org = data_ci[0]
                c_course = data_ci[1]
                c_name = data_ci[2]
                multi_course_id = module_store.make_course_key(c_org, c_course, c_name)
                course_overviews = CourseOverview.objects.get(id=multi_course_id)
                course_list.append(course_overviews)

            # multisite - make course status
            for c in course_list:
                status = common_course_status(c.start, c.end)
                c.status = status

            """
            for c in course_list:
                if c.start is None or c.start == '' or c.end is None or c.end == '':
                    c.status = 'none'
                elif datetime.datetime.now(UTC2()) < c.start:
                    c.status = 'ready'
                elif c.start <= datetime.datetime.now(UTC2()) <= c.end:
                    c.status = 'ing'
                elif c.end < datetime.datetime.now(UTC2()):
                    c.status = 'end'
                else:
                    c.status = 'none'
            """

            context = {'courses': course_list}

    context['homepage_overlay_html'] = configuration_helpers.get_value('homepage_overlay_html')
    context['show_partners'] = configuration_helpers.get_value('show_partners', True)
    context['show_homepage_promo_video'] = configuration_helpers.get_value('show_homepage_promo_video', False)
    youtube_video_id = configuration_helpers.get_value('homepage_promo_video_youtube_id', "your-youtube-id")
    context['homepage_promo_video_youtube_id'] = youtube_video_id
    context['courses_list'] = theming_helpers.get_template_path('courses_list.html')
    context['boards_list'] = theming_helpers.get_template_path('boards_list.html')

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')

    total_list = []
    cur = con.cursor()
    query = """
            (  SELECT board_id,
                 CASE
                     WHEN head_title = 'noti_n' THEN '[공지]'
                     WHEN head_title = 'advert_n' THEN '[공고]'
                     WHEN head_title = 'guide_n' THEN '[안내]'
                     WHEN head_title = 'event_n' THEN '[이벤트]'
                     WHEN head_title = 'etc_n' THEN '[기타]'
                     ELSE ''
                 END
                     head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     ''
                FROM tb_board
               WHERE section = 'N'
               and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)
        union all
            (  SELECT board_id,
                 CASE
                     WHEN head_title = 'k_news_k' THEN '[K-MOOC소식]'
                     WHEN head_title = 'report_k' THEN '[보도자료]'
                     WHEN head_title = 'u_news_k' THEN '[대학뉴스]'
                     WHEN head_title = 'support_k' THEN '[서포터즈이야기]'
                     WHEN head_title = 'n_new_k' THEN '[NILE소식]'
                     WHEN head_title = 'etc_k' THEN '[기타]'
                     ELSE ''
                 END
                     head_title,
                     subject,
                     mid(substr(content, instr(content, 'src="') + 5), 1, instr(substr(content, instr(content, 'src="') + 5), '"') - 1 ),
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     ''
                FROM tb_board
               WHERE section = 'K'
               and use_yn = 'Y'
            ORDER BY mod_date DESC
                limit 4)
        union all
            (  SELECT board_id,
                 CASE
                     WHEN head_title = 'publi_r' THEN '[홍보자료]'
                     WHEN head_title = 'data_r' THEN '[자료집]'
                     WHEN head_title = 'repo_r' THEN '[보고서]'
                     WHEN head_title = 'etc_r' THEN '[기타]'
                     ELSE ''
                 END
                     head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     ''
                FROM tb_board
               WHERE section = 'R'
               and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)
        union all
            (  SELECT board_id,
                 CASE
                      WHEN head_title = 'kmooc_f' THEN '[K-MOOC]'
                      WHEN head_title = 'regist_f ' THEN '[회원가입]'
                      WHEN head_title = 'login_f ' THEN '[로그인/계정]'
                      WHEN head_title = 'enroll_f ' THEN '[수강신청/취소]'
                      WHEN head_title = 'course_f ' THEN '[강좌수강]'
                      WHEN head_title = 'certi_f  ' THEN '[성적/이수증]'
                      WHEN head_title = 'tech_f ' THEN '[기술적문제]'
                      ELSE ''
                   END
                      head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     head_title
                FROM tb_board
               WHERE section = 'F'
                 and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)
        union all
            (  SELECT board_id,
                     '' head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     head_title
                FROM tb_board
               WHERE section = 'M'
                 and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)

    """

    index_list = []
    cur.execute(query)
    row = cur.fetchall()
    for i in row:
        value_list = []
        value_list.append(i[0])
        value_list.append(i[1])
        value_list.append(i[2])
        s = i[3]
        text = re.sub('<[^>]*>', '', s)
        text = re.sub('&nbsp;', '', text)
        text = re.sub('/manage/home/static/upload/', '/static/file_upload/', text)
        text1 = re.sub('/home/project/management/home/static/upload/', '', text)
        # text1 = re.sub('/manage/home/static/excel/notice_file/', '', text)
        text = re.sub('/home/project/management/home/static/upload/', '/static/file_upload/', text)
        # text = re.sub('/manage/home/static/excel/notice_file/', '/static/file_upload/', text)
        value_list.append(text[0:200])
        value_list.append(i[4])
        value_list.append(i[5])
        value_list.append(i[6])
        value_list.append(text1)
        index_list.append(value_list)

    context['index_list'] = index_list
    context.update(extra_context)

    print context

    return render_to_response('multisite_index.html', context)


# -------------------- multi site -------------------- #

# NOTE: This view is not linked to directly--it is called from
# branding/views.py:index(), which is cached for anonymous users.
# This means that it should always return the same thing for anon
# users. (in particular, no switching based on query params allowed)
def index(request, extra_context=None, user=AnonymousUser()):
    """
    Render the edX main page.

    extra_context is used to allow immediate display of certain modal windows, eg signup,
    as used by external_auth.
    """

    if extra_context is None:
        extra_context = {}

    user = request.user

    # courses = get_courses(user)
    # filter test ::: filter_={'start__lte': datetime.datetime.now(), 'org':'edX'}

    f1 = None if user.is_staff else {'enrollment_start__isnull': False, 'start__gt': datetime.datetime.now(),
                                     'enrollment_start__lte': datetime.datetime.now()}
    log.info(f1)
    courses1 = get_courses(user, filter_=f1)

    f2 = {'enrollment_start__isnull': False} if user.is_staff else {'enrollment_start__isnull': False,
                                                                    'start__lte': datetime.datetime.now(),
                                                                    'enrollment_start__lte': datetime.datetime.now()}
    log.info(f2)
    courses2 = get_courses(user, filter_=f2)

    # print 'get course test ------------------------------------------------------- e'

    # if configuration_helpers.get_value(
    #         "ENABLE_COURSE_SORTING_BY_START_DATE",
    #         settings.FEATURES["ENABLE_COURSE_SORTING_BY_START_DATE"],
    # ):
    #     courses = sort_by_start_date(courses)
    # else:
    #     courses = sort_by_announcement(courses)

    # 사용자가 스태프 이면 강좌 목록 제한이 없도록 한다..
    if user and user.is_staff:
        pass
    else:
        if courses1 and len(courses1) > 4:
            courses1 = courses1[:4]

    if user and user.is_staff:
        courses = courses1
    else:
        courses = courses1 + courses2
    courses = [c for c in courses if not c.has_ended()]
    log.info(u'len(courses) ::: %s', len(courses))

    if user and user.is_staff:
        pass
    else:
        courses = courses[:8]

    context = {'courses': courses}

    context['homepage_overlay_html'] = configuration_helpers.get_value('homepage_overlay_html')

    # This appears to be an unused context parameter, at least for the master templates...
    context['show_partners'] = configuration_helpers.get_value('show_partners', True)

    # TO DISPLAY A YOUTUBE WELCOME VIDEO
    # 1) Change False to True
    context['show_homepage_promo_video'] = configuration_helpers.get_value('show_homepage_promo_video', False)

    # 2) Add your video's YouTube ID (11 chars, eg "123456789xX"), or specify via site configuration
    # Note: This value should be moved into a configuration setting and plumbed-through to the
    # context via the site configuration workflow, versus living here
    youtube_video_id = configuration_helpers.get_value('homepage_promo_video_youtube_id', "your-youtube-id")
    context['homepage_promo_video_youtube_id'] = youtube_video_id

    # allow for theme override of the courses list
    context['courses_list'] = theming_helpers.get_template_path('courses_list.html')

    # allow for theme override of the boards list
    context['boards_list'] = theming_helpers.get_template_path('boards_list.html')

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    total_list = []
    cur = con.cursor()
    query = """
            (  SELECT board_id,
                 CASE
                     WHEN head_title = 'noti_n' THEN '[공지]'
                     WHEN head_title = 'advert_n' THEN '[공고]'
                     WHEN head_title = 'guide_n' THEN '[안내]'
                     WHEN head_title = 'event_n' THEN '[이벤트]'
                     WHEN head_title = 'etc_n' THEN '[기타]'
                     ELSE ''
                 END
                     head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     ''
                FROM tb_board
               WHERE section = 'N'
               and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)
        union all
            (  SELECT board_id,
                 CASE
                     WHEN head_title = 'k_news_k' THEN '[K-MOOC소식]'
                     WHEN head_title = 'report_k' THEN '[보도자료]'
                     WHEN head_title = 'u_news_k' THEN '[대학뉴스]'
                     WHEN head_title = 'support_k' THEN '[서포터즈이야기]'
                     WHEN head_title = 'n_new_k' THEN '[NILE소식]'
                     WHEN head_title = 'etc_k' THEN '[기타]'
                     ELSE ''
                 END
                     head_title,
                     subject,
                     mid(substr(content, instr(content, 'src="') + 5), 1, instr(substr(content, instr(content, 'src="') + 5), '"') - 1 ),
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     ''
                FROM tb_board
               WHERE section = 'K'
               and use_yn = 'Y'
            ORDER BY mod_date DESC
                limit 4)
        union all
            (  SELECT board_id,
                 CASE
                     WHEN head_title = 'publi_r' THEN '[홍보자료]'
                     WHEN head_title = 'data_r' THEN '[자료집]'
                     WHEN head_title = 'repo_r' THEN '[보고서]'
                     WHEN head_title = 'etc_r' THEN '[기타]'
                     ELSE ''
                 END
                     head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     ''
                FROM tb_board
               WHERE section = 'R'
               and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)
        union all
            (  SELECT board_id,
                 CASE
                      WHEN head_title = 'kmooc_f' THEN '[K-MOOC]'
                      WHEN head_title = 'regist_f ' THEN '[회원가입]'
                      WHEN head_title = 'login_f ' THEN '[로그인/계정]'
                      WHEN head_title = 'enroll_f ' THEN '[수강신청/취소]'
                      WHEN head_title = 'course_f ' THEN '[강좌수강]'
                      WHEN head_title = 'certi_f  ' THEN '[성적/이수증]'
                      WHEN head_title = 'tech_f ' THEN '[기술적문제]'
                      ELSE ''
                   END
                      head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     head_title
                FROM tb_board
               WHERE section = 'F'
                 and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)
        union all
            (  SELECT board_id,
                     '' head_title,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     section,
                     head_title
                FROM tb_board
               WHERE section = 'M'
                 and use_yn = 'Y'
            ORDER BY mod_date DESC
               limit 4)
    """

    index_list = []
    cur.execute(query)
    row = cur.fetchall()
    for i in row:
        value_list = []
        value_list.append(i[0])
        value_list.append(i[1])
        value_list.append(i[2])
        s = i[3]
        text = re.sub('<[^>]*>', '', s)
        text = re.sub('&nbsp;', '', text)
        text = re.sub('/manage/home/static/upload/', '/static/file_upload/', text)
        text1 = re.sub('/home/project/management/home/static/upload/', '', text)
        # text1 = re.sub('/manage/home/static/excel/notice_file/', '', text)
        text = re.sub('/home/project/management/home/static/upload/', '/static/file_upload/', text)
        # text = re.sub('/manage/home/static/excel/notice_file/', '/static/file_upload/', text)
        value_list.append(text[0:200])
        value_list.append(i[4])
        value_list.append(i[5])
        value_list.append(i[6])
        value_list.append(text1)
        index_list.append(value_list)

    context['index_list'] = index_list

    cur = con.cursor()
    query = """
        SELECT popup_id,
               template,
               popup_type,
               title,
               contents,
               link_url,
               link_target,
               CASE
                  WHEN hidden_day = '1' THEN '1일간 열지 않음'
                  WHEN hidden_day = '7' THEN '7일간 열지 않음'
                  WHEN hidden_day = '0' THEN '다시 열지 않음'
               END
               hidden_day,
               width,
               height,
               CASE
                  WHEN hidden_day = '1' THEN '1'
                  WHEN hidden_day = '7' THEN '7'
                  WHEN hidden_day = '0' THEN '999999'
               END
               hidden_day
          FROM popup
         WHERE use_yn = 'Y' and adddate(now(), INTERVAL 9 HOUR) between STR_TO_DATE(concat(start_date, start_time), '%Y%m%d%H%i') and STR_TO_DATE(concat(end_date, end_time), '%Y%m%d%H%i')
        """

    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    popup_index = ""
    for index in row:
        if (index[1] == '0'):
            if (index[2] == "H"):
                print('indexH.html')
                f = open("/edx/app/edxapp/edx-platform/common/static/popup_index/indexH.html", 'r')
                while True:
                    line = f.readline()
                    if not line: break
                    popup_index += str(line)
                    popup_index = popup_index.replace("#_id", str(index[0]))
                    popup_index = popup_index.replace("#_title", str(index[3]))
                    popup_index = popup_index.replace("#_contents", str(index[4]))
                    popup_index = popup_index.replace("#_link_url", str(index[5]))
                    popup_index = popup_index.replace("#_link_target", str(index[6]))
                    popup_index = popup_index.replace("#_hidden_day", str(index[7]))
                    popup_index = popup_index.replace("#_width", str(index[8]))
                    popup_index = popup_index.replace("#_height", str(index[9] - 28))
                    popup_index = popup_index.replace("#_hidden", str(index[10]))
                f.close()
            elif (index[2] == "I"):
                print('indexI.html')
                cur = con.cursor()
                query = """
                    SELECT popup_id,
                           title,
                           contents,
                           link_url,
                           CASE
                              WHEN link_target = 'B' THEN 'blank'
                              WHEN link_target = 'S' THEN 'self'
                           END
                           link_target,
                           CASE
                              WHEN hidden_day = '1' THEN '1일간 열지 않음'
                              WHEN hidden_day = '7' THEN '7일간 열지 않음'
                              WHEN hidden_day = '0' THEN '다시 열지 않음'
                           END
                           hidden_day,
                           popup_type,
                           attatch_file_name,
                           width,
                           height,
                           image_map,
                           CASE
                              WHEN hidden_day = '1' THEN '1'
                              WHEN hidden_day = '7' THEN '7'
                              WHEN hidden_day = '0' THEN '999999'
                           END
                           hidden_day
                      FROM popup
                      JOIN tb_board_attach ON tb_board_attach.attatch_id = popup.image_file
                     WHERE popup_id = {0};
                    """.format(index[0])
                cur.execute(query)
                row = cur.fetchall()
                cur.close()
                map_list = []
                for p in row:
                    image_map = p[10]
                    im_arr = image_map.split('/')
                    map_list.append(list(p + (im_arr,)))
                for index in map_list:
                    f = open("/edx/app/edxapp/edx-platform/common/static/popup_index/indexI.html", 'r')
                    while True:
                        line = f.readline()
                        if not line: break
                        popup_index += str(line)
                        popup_index = popup_index.replace("#_id", str(index[0]))
                        popup_index = popup_index.replace("#_title", str(index[1]))
                        popup_index = popup_index.replace("#_contents", str(index[2]))
                        popup_index = popup_index.replace("#_link_url", str(index[3]))
                        popup_index = popup_index.replace("#_link_target", str(index[4]))
                        popup_index = popup_index.replace("#_hidden_day", str(index[5]))
                        popup_index = popup_index.replace("#_attatch_file_name", str(index[7]))
                        popup_index = popup_index.replace("#_width", str(index[8]))
                        popup_index = popup_index.replace("#_height", str(index[9]))
                        popup_index = popup_index.replace("#_img_width", str(index[9]))
                        popup_index = popup_index.replace("#_img_height", str(index[9] - 27))
                        popup_index = popup_index.replace("#_hidden", str(index[11]))
                        if (len(index[12]) == 1):
                            map_str = """
                                    <area shape="rect" coords="0,0,{0},{1}" alt="IM" target="_{2}" href="{3}">
                                    """.format(str(index[8]), str(index[9]), str(index[4]), str(index[3]))
                            popup_index = popup_index.replace("#_not_exist", map_str)
                            popup_index = popup_index.replace("#_exist", "")
                        else:
                            map_str = ""
                            for map in index[12]:
                                map_str += """
                                    <area shape="rect" coords="{0}" alt="IM" target="_{1}" href="{2}">
                                    """.format(str(map), str(index[4]), str(index[3]))
                            popup_index = popup_index.replace("#_not_exist", "")
                            popup_index = popup_index.replace("#_exist", map_str)
                    f.close()


        elif (index[1] == '1'):
            print('index1.html')
            f = open("/edx/app/edxapp/edx-platform/common/static/popup_index/index1.html", 'r')
            while True:
                line = f.readline()
                if not line: break
                popup_index += str(line)
                popup_index = popup_index.replace("#_id", str(index[0]))
                popup_index = popup_index.replace("#_title", str(index[3]))
                popup_index = popup_index.replace("#_contents", str(index[4]))
                popup_index = popup_index.replace("#_link_url", str(index[5]))
                popup_index = popup_index.replace("#_link_target", str(index[6]))
                popup_index = popup_index.replace("#_hidden_day", str(index[7]))
                popup_index = popup_index.replace("#_width", str(index[8]))
                popup_index = popup_index.replace("#_height", str(index[9] - 83))
                popup_index = popup_index.replace("#bg_top", str(int(index[9]) - 125))
                popup_index = popup_index.replace("#_hidden", str(index[10]))
            f.close()
        elif (index[1] == '2'):
            print('index2.html')
            f = open("/edx/app/edxapp/edx-platform/common/static/popup_index/index2.html", 'r')
            while True:
                line = f.readline()
                if not line: break
                popup_index += str(line)
                popup_index = popup_index.replace("#_id", str(index[0]))
                popup_index = popup_index.replace("#_title", str(index[3]))
                popup_index = popup_index.replace("#_contents", str(index[4]))
                popup_index = popup_index.replace("#_link_url", str(index[5]))
                popup_index = popup_index.replace("#_link_target", str(index[6]))
                popup_index = popup_index.replace("#_hidden_day", str(index[7]))
                popup_index = popup_index.replace("#_width", str(index[8]))
                popup_index = popup_index.replace("#_height", str(index[9] - 131))
                popup_index = popup_index.replace("#_hidden", str(index[10]))
            f.close()
        elif (index[1] == '3'):
            f = open("/edx/app/edxapp/edx-platform/common/static/popup_index/index3.html", 'r')
            while True:
                line = f.readline()
                if not line: break
                popup_index += str(line)
                popup_index = popup_index.replace("#_id", str(index[0]))
                popup_index = popup_index.replace("#_title", str(index[3]))
                popup_index = popup_index.replace("#_contents", str(index[4]))
                popup_index = popup_index.replace("#_link_url", str(index[5]))
                popup_index = popup_index.replace("#_link_target", str(index[6]))
                popup_index = popup_index.replace("#_hidden_day", str(index[7]))
                popup_index = popup_index.replace("#_width", str(index[8]))
                popup_index = popup_index.replace("#_height", str(index[9] - 149))
                popup_index = popup_index.replace("#_hidden", str(index[10]))
            f.close()

    cur = con.cursor()
    query = """
        SELECT max(popup_id) FROM popup;
        """
    cur.execute(query)
    max_pop = cur.fetchall()
    cur.close()


    extra_context['popup_index'] = popup_index
    # Insert additional context for use in the template
    context.update(extra_context)
    extra_context['max_pop'] = str(max_pop[0][0])
    context.update(extra_context)

    return render_to_response('index.html', context)


def process_survey_link(survey_link, user):
    """
    If {UNIQUE_ID} appears in the link, replace it with a unique id for the user.
    Currently, this is sha1(user.username).  Otherwise, return survey_link.
    """
    return survey_link.format(UNIQUE_ID=unique_id_for_user(user))


def cert_info(user, course_overview, course_mode):
    """
    Get the certificate info needed to render the dashboard section for the given
    student and course.

    Arguments:
        user (User): A user.
        course_overview (CourseOverview): A course.
        course_mode (str): The enrollment mode (honor, verified, audit, etc.)

    Returns:
        dict: Empty dict if certificates are disabled or hidden, or a dictionary with keys:
            'status': one of 'generating', 'ready', 'notpassing', 'processing', 'restricted'
            'show_download_url': bool
            'download_url': url, only present if show_download_url is True
            'show_disabled_download_button': bool -- true if state is 'generating'
            'show_survey_button': bool
            'survey_url': url, only if show_survey_button is True
            'grade': if status is not 'processing'
            'can_unenroll': if status allows for unenrollment
    """
    if not course_overview.may_certify():
        return {}
    return _cert_info(
        user,
        course_overview,
        certificate_status_for_student(user, course_overview.id),
        course_mode
    )


def reverification_info(statuses):
    """
    Returns reverification-related information for *all* of user's enrollments whose
    reverification status is in statuses.

    Args:
        statuses (list): a list of reverification statuses we want information for
            example: ["must_reverify", "denied"]

    Returns:
        dictionary of lists: dictionary with one key per status, e.g.
            dict["must_reverify"] = []
            dict["must_reverify"] = [some information]
    """
    reverifications = defaultdict(list)

    # Sort the data by the reverification_end_date
    for status in statuses:
        if reverifications[status]:
            reverifications[status].sort(key=lambda x: x.date)
    return reverifications


def get_course_enrollments(user, org_to_include, orgs_to_exclude, status=None):
    """
    Given a user, return a filtered set of his or her course enrollments.

    Arguments:
        user (User): the user in question.
        org_to_include (str): If not None, ONLY courses of this org will be returned.
        orgs_to_exclude (list[str]): If org_to_include is not None, this
            argument is ignored. Else, courses of this org will be excluded.

    Returns:
        generator[CourseEnrollment]: a sequence of enrollments to be displayed
        on the user's dashboard.
    """
    if not status:
        enrollments = CourseEnrollment.enrollments_for_user_ing(user)
    elif status == 'end':
        enrollments = CourseEnrollment.enrollments_for_user_end(user)
    elif status == 'interest':
        enrollments = CourseEnrollment.enrollments_for_user_interest(user)
    else:
        enrollments = CourseEnrollment.enrollments_for_user_ing(user)

    for enrollment in enrollments:
        enrollment.is_enrolled = CourseEnrollment.is_enrolled(user, enrollment.course_id)
        # If the course is missing or broken, log an error and skip it.
        course_overview = enrollment.course_overview
        if not course_overview:
            log.error(
                "User %s enrolled in broken or non-existent course %s",
                user.username,
                enrollment.course_id
            )
            continue
        else:
            pass

        # Filter out anything that is not attributed to the current ORG.
        if org_to_include and course_overview.location.org != org_to_include:
            continue

        # Conversely, filter out any enrollments with courses attributed to current ORG.
        elif course_overview.location.org in orgs_to_exclude:
            continue

        # Else, include the enrollment.
        else:
            yield enrollment


def _cert_info(user, course_overview, cert_status, course_mode):  # pylint: disable=unused-argument
    """
    Implements the logic for cert_info -- split out for testing.

    Arguments:
        user (User): A user.
        course_overview (CourseOverview): A course.
        course_mode (str): The enrollment mode (honor, verified, audit, etc.)
    """
    # simplify the status for the template using this lookup table
    template_state = {
        CertificateStatuses.generating: 'generating',
        CertificateStatuses.downloadable: 'ready',
        CertificateStatuses.notpassing: 'notpassing',
        CertificateStatuses.restricted: 'restricted',
        CertificateStatuses.auditing: 'auditing',
        CertificateStatuses.audit_passing: 'auditing',
        CertificateStatuses.audit_notpassing: 'auditing',
        CertificateStatuses.unverified: 'unverified',
    }

    default_status = 'processing'

    default_info = {
        'status': default_status,
        'show_disabled_download_button': False,
        'show_download_url': False,
        'show_survey_button': False,
        'can_unenroll': True,
    }

    if cert_status is None:
        return default_info

    is_hidden_status = cert_status['status'] in ('unavailable', 'processing', 'generating', 'notpassing', 'auditing')

    if course_overview.certificates_display_behavior == 'early_no_info' and is_hidden_status:
        return {}

    status = template_state.get(cert_status['status'], default_status)

    status_dict = {
        'status': status,
        'show_download_url': status == 'ready',
        'show_disabled_download_button': status == 'generating',
        'mode': cert_status.get('mode', None),
        'linked_in_url': None,
        'can_unenroll': status not in DISABLE_UNENROLL_CERT_STATES,
    }

    if (status in ('generating', 'ready', 'notpassing', 'restricted', 'auditing', 'unverified') and
                course_overview.end_of_course_survey_url is not None):
        status_dict.update({
            'show_survey_button': True,
            'survey_url': process_survey_link(course_overview.end_of_course_survey_url, user)})
    else:
        status_dict['show_survey_button'] = False

    if status == 'ready':
        # showing the certificate web view button if certificate is ready state and feature flags are enabled.
        if has_html_certificates_enabled(course_overview.id, course_overview):
            if course_overview.has_any_active_web_certificate:
                status_dict.update({
                    'show_cert_web_view': True,
                    'cert_web_view_url': get_certificate_url(course_id=course_overview.id, uuid=cert_status['uuid'])
                })
            else:
                # don't show download certificate button if we don't have an active certificate for course
                status_dict['show_download_url'] = False
        elif 'download_url' not in cert_status:
            log.warning(
                u"User %s has a downloadable cert for %s, but no download url",
                user.username,
                course_overview.id
            )
            return default_info
        else:
            status_dict['download_url'] = cert_status['download_url']

            # If enabled, show the LinkedIn "add to profile" button
            # Clicking this button sends the user to LinkedIn where they
            # can add the certificate information to their profile.
            linkedin_config = LinkedInAddToProfileConfiguration.current()

            # posting certificates to LinkedIn is not currently
            # supported in White Labels
            if linkedin_config.enabled and not theming_helpers.is_request_in_themed_site():
                status_dict['linked_in_url'] = linkedin_config.add_to_profile_url(
                    course_overview.id,
                    course_overview.display_name,
                    cert_status.get('mode'),
                    cert_status['download_url']
                )

    if status in ('generating', 'ready', 'notpassing', 'restricted', 'auditing', 'unverified'):
        if 'grade' not in cert_status:
            # Note: as of 11/20/2012, we know there are students in this state-- cs169.1x,
            # who need to be regraded (we weren't tracking 'notpassing' at first).
            # We can add a log.warning here once we think it shouldn't happen.
            return default_info
        else:
            status_dict['grade'] = cert_status['grade']

    # 이수강좌의 경우 강좌에 `survey`가 있는지와 완료 했는지 여부를 확인
    try:

        if status == 'ready':
            log.info('survey or poll count check start.')

            arr = str(course_overview)[10:].split('+')

            org = arr[0]
            course = arr[1]
            run = arr[2]
            checklist = list()
            survey_list = list()

            client = MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'),
                                 settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port'))
            db = client.edxapp

            log.info('org: {0}, course: {1}, run: {2}'.format(str(org), str(course), str(run)))

            cursor = db.modulestore.active_versions.find({'org': org, 'course': course}).sort("edited_on", 1)
            order_course = {}
            course_cnt = 1

            for document in cursor:
                print document.get('run')
                order_course[document.get('run')] = course_cnt
                course_cnt += 1

            print 'order_course[run]:', order_course[run]
            if order_course[run] == 1:
                pass
            else:
                print 'return because rerun course..'
                return status_dict

            cursor = db.modulestore.active_versions.find({'org': org, 'course': course, 'run': run})

            pb = ''
            for document in cursor:
                pb = document.get('versions').get('published-branch')
            cursor.close()

            if pb:
                cursor = db.modulestore.structures.find({'_id': pb})
                for document in cursor:
                    blocks = document.get('blocks')
                cursor.close()
                client.close()

                check_cnt = 0

                chapters = dict()
                sequentials = dict()
                verticals = dict()

                for block in blocks:

                    if block.get('block_type') == 'chapter':
                        chapters[block.get('block_id')] = [id for type, id in block.get('fields')['children']]
                    elif block.get('block_type') == 'sequential':
                        sequentials[block.get('block_id')] = [id for type, id in block.get('fields')['children']]
                    elif block.get('block_type') == 'vertical':
                        verticals[block.get('block_id')] = [id for type, id in block.get('fields')['children']]

                    if block.get('block_type') == 'course':
                        end = block.get('fields')['end']
                        # print 'end:', end

                    elif block.get('block_type') == 'vertical':
                        global visible_to_staff_only

                        if 'visible_to_staff_only' in block.get('fields'):
                            visible_to_staff_only = block.get('fields')['visible_to_staff_only']
                        else:
                            visible_to_staff_only = False

                        if visible_to_staff_only is True:
                            continue

                        childrens = block.get('fields')['children']
                        for children in childrens:
                            if children[0] == 'survey':
                                check_cnt += 1
                                survey_list.append(children[1])

                                checklist.append("'" + children[1] + "'")

                if not end or end.strftime("%Y%m%d") < '20161231':
                    log.info('before 20161201 course.. return..')
                    return status_dict

                if check_cnt > 0:
                    with connections['default'].cursor() as cur:
                        query = """
                            SELECT SUBSTRING_INDEX(module_id, '@', -1)                    module_id,
                                   if(instr(state, 'submissions_count') > 0, TRUE, FALSE) is_done
                              FROM courseware_studentmodule
                             WHERE     student_id = '{0}'
                                   AND course_id = '{1}'
                                   AND module_type IN ('survey');
                        """.format(str(user.id), str(course_overview))
                        print 'query:', query

                        cur.execute(query)
                        rows = cur.fetchall()

                    status_dict['survey'] = 'complete'

                    for survey in survey_list:
                        if rows:
                            result = [row[1] for row in rows if row[0] == survey and row[1] == 1]
                            cnt = len(result)
                        else:
                            cnt = 0

                        if cnt == 0:
                            status_dict['survey'] = 'incomplete'
                            v_key = [key for key in verticals.keys() if survey in verticals[key]][0]
                            s_key = [key for key in sequentials.keys() if v_key in sequentials[key]][0]
                            c_key = [key for key in chapters.keys() if s_key in chapters[key]][0]

                            # verticals_keys = verticals.keys()
                            #
                            # for key in verticals_keys:
                            #     if survey in verticals[key]:
                            #         v_key = key
                            #
                            # sequentials_keys = sequentials.keys()
                            #
                            # for key in sequentials_keys:
                            #     if v_key in sequentials[key]:
                            #         s_key = key
                            #
                            # chapters_keys = chapters.keys()
                            #
                            # for key in chapters_keys:
                            #     if s_key in chapters[key]:
                            #         c_key = key

                            status_dict['survey_url'] = '/courses/{0}/courseware/{1}/{2}'.format(str(course_overview),
                                                                                                 c_key, s_key)
                            break
    except Exception as e:
        traceback.print_exc()
        log.error(e)

    return status_dict


@ensure_csrf_cookie
def signin_user(request):
    """Deprecated. To be replaced by :class:`student_account.views.login_and_registration_form`."""
    external_auth_response = external_auth_login(request)
    if external_auth_response is not None:
        return external_auth_response
    # Determine the URL to redirect to following login:
    redirect_to = get_next_url_for_login_page(request)
    if request.user.is_authenticated():
        return redirect(redirect_to)

    third_party_auth_error = None
    for msg in messages.get_messages(request):
        if msg.extra_tags.split()[0] == "social-auth":
            # msg may or may not be translated. Try translating [again] in case we are able to:
            third_party_auth_error = _(unicode(msg))  # pylint: disable=translation-of-non-string
            break

    context = {
        'login_redirect_url': redirect_to,  # This gets added to the query string of the "Sign In" button in the header
        # Bool injected into JS to submit form if we're inside a running third-
        # party auth pipeline; distinct from the actual instance of the running
        # pipeline, if any.
        'pipeline_running': 'true' if pipeline.running(request) else 'false',
        'pipeline_url': auth_pipeline_urls(pipeline.AUTH_ENTRY_LOGIN, redirect_url=redirect_to),
        'platform_name': configuration_helpers.get_value(
            'platform_name',
            settings.PLATFORM_NAME
        ),
        'third_party_auth_error': third_party_auth_error
    }

    return render_to_response('login.html', context)


@ensure_csrf_cookie
def register_user(request, extra_context=None):
    """Deprecated. To be replaced by :class:`student_account.views.login_and_registration_form`."""
    # Determine the URL to redirect to following login:
    redirect_to = get_next_url_for_login_page(request)
    if request.user.is_authenticated():
        return redirect(redirect_to)

    external_auth_response = external_auth_register(request)
    if external_auth_response is not None:
        return external_auth_response

    context = {
        'login_redirect_url': redirect_to,  # This gets added to the query string of the "Sign In" button in the header
        'email': '',
        'name': '',
        'running_pipeline': None,
        'pipeline_urls': auth_pipeline_urls(pipeline.AUTH_ENTRY_REGISTER, redirect_url=redirect_to),
        'platform_name': configuration_helpers.get_value(
            'platform_name',
            settings.PLATFORM_NAME
        ),
        'selected_provider': '',
        'username': '',
    }

    if extra_context is not None:
        context.update(extra_context)

    if context.get("extauth_domain", '').startswith(external_auth.views.SHIBBOLETH_DOMAIN_PREFIX):
        return render_to_response('register-shib.html', context)

    # If third-party auth is enabled, prepopulate the form with data from the
    # selected provider.
    if third_party_auth.is_enabled() and pipeline.running(request):
        running_pipeline = pipeline.get(request)
        current_provider = provider.Registry.get_from_pipeline(running_pipeline)
        if current_provider is not None:
            overrides = current_provider.get_register_form_data(running_pipeline.get('kwargs'))
            overrides['running_pipeline'] = running_pipeline
            overrides['selected_provider'] = current_provider.name
            context.update(overrides)

    return render_to_response('register.html', context)


def complete_course_mode_info(course_id, enrollment, modes=None):
    """
    We would like to compute some more information from the given course modes
    and the user's current enrollment

    Returns the given information:
        - whether to show the course upsell information
        - numbers of days until they can't upsell anymore
    """
    if modes is None:
        modes = CourseMode.modes_for_course_dict(course_id)

    mode_info = {'show_upsell': False, 'days_for_upsell': None}
    # we want to know if the user is already enrolled as verified or credit and
    # if verified is an option.
    if CourseMode.VERIFIED in modes and enrollment.mode in CourseMode.UPSELL_TO_VERIFIED_MODES:
        mode_info['show_upsell'] = True
        mode_info['verified_sku'] = modes['verified'].sku
        mode_info['verified_bulk_sku'] = modes['verified'].bulk_sku
        # if there is an expiration date, find out how long from now it is
        if modes['verified'].expiration_datetime:
            today = datetime.datetime.now(UTC).date()
            mode_info['days_for_upsell'] = (modes['verified'].expiration_datetime.date() - today).days

    return mode_info


def is_course_blocked(request, redeemed_registration_codes, course_key):
    """Checking either registration is blocked or not ."""
    blocked = False
    for redeemed_registration in redeemed_registration_codes:
        # registration codes may be generated via Bulk Purchase Scenario
        # we have to check only for the invoice generated registration codes
        # that their invoice is valid or not
        if redeemed_registration.invoice_item:
            if not redeemed_registration.invoice_item.invoice.is_valid:
                blocked = True
                # disabling email notifications for unpaid registration courses
                Optout.objects.get_or_create(user=request.user, course_id=course_key)
                log.info(
                    u"User %s (%s) opted out of receiving emails from course %s",
                    request.user.username,
                    request.user.email,
                    course_key,
                )
                track.views.server_track(
                    request,
                    "change-email1-settings",
                    {"receive_emails": "no", "course": course_key.to_deprecated_string()},
                    page='dashboard',
                )
                break

    return blocked


@transaction.non_atomic_requests
@login_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@ensure_valid_course_key
@ensure_csrf_cookie
def dashboard(request):
    user = request.user

    platform_name = configuration_helpers.get_value("platform_name", settings.PLATFORM_NAME)

    # we want to filter and only show enrollments for courses within
    # the 'ORG' defined in configuration.
    course_org_filter = configuration_helpers.get_value('course_org_filter')

    # Let's filter out any courses in an "org" that has been declared to be
    # in a configuration
    org_filter_out_set = configuration_helpers.get_all_orgs()

    # remove our current org from the "filter out" list, if applicable
    if course_org_filter:
        org_filter_out_set.remove(course_org_filter)

    # Build our (course, enrollment) list for the user, but ignore any courses that no
    # longer exist (because the course IDs have changed). Still, we don't delete those
    # enrollments, because it could have been a data push snafu.

    # 개강예정, 진행중, 종료 로 구분하여 대시보드 로딩 속도를 개선한다.
    if request.is_ajax():
        status = request.POST.get('status')
        print 'status:', status

        course_enrollments = list(get_course_enrollments(user, course_org_filter, org_filter_out_set, status))
    else:
        course_enrollments = list(get_course_enrollments(user, course_org_filter, org_filter_out_set))

    # Retrieve the course modes for each course
    enrolled_course_ids = [enrollment.course_id for enrollment in course_enrollments]
    __, unexpired_course_modes = CourseMode.all_and_unexpired_modes_for_courses(enrolled_course_ids)
    course_modes_by_course = {
        course_id: {
            mode.slug: mode
            for mode in modes
            }
        for course_id, modes in unexpired_course_modes.iteritems()
        }

    # Check to see if the student has recently enrolled in a course.
    # If so, display a notification message confirming the enrollment.
    enrollment_message = _create_recent_enrollment_message(
        course_enrollments, course_modes_by_course
    )

    course_optouts = Optout.objects.filter(user=user).values_list('course_id', flat=True)

    message = ""
    if not user.is_active:
        message = render_to_string(
            'registration/activate_account_notice.html',
            {'email': user.email, 'platform_name': platform_name}
        )

    # Global staff can see what courses errored on their dashboard
    staff_access = False
    errored_courses = {}
    if has_access(user, 'staff', 'global'):
        # Show any courses that errored on load
        staff_access = True
        errored_courses = modulestore().get_errored_courses()

    show_courseware_links_for = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if has_access(request.user, 'load', enrollment.course_overview)
        and has_access(request.user, 'view_courseware_with_prerequisites', enrollment.course_overview)
    )

    # Get any programs associated with courses being displayed.
    # This is passed along in the template context to allow rendering of
    # program-related information on the dashboard.
    course_programs = _get_course_programs(user, [enrollment.course_id for enrollment in course_enrollments])

    # Construct a dictionary of course mode information
    # used to render the course list.  We re-use the course modes dict
    # we loaded earlier to avoid hitting the database.
    course_mode_info = {
        enrollment.course_id: complete_course_mode_info(
            enrollment.course_id, enrollment,
            modes=course_modes_by_course[enrollment.course_id]
        )
        for enrollment in course_enrollments
        }

    # Determine the per-course verification status
    # This is a dictionary in which the keys are course locators
    # and the values are one of:
    #
    # VERIFY_STATUS_NEED_TO_VERIFY
    # VERIFY_STATUS_SUBMITTED
    # VERIFY_STATUS_APPROVED
    # VERIFY_STATUS_MISSED_DEADLINE
    #
    # Each of which correspond to a particular message to display
    # next to the course on the dashboard.
    #
    # If a course is not included in this dictionary,
    # there is no verification messaging to display.

    verify_status_by_course = check_verify_status_by_course(user, course_enrollments)
    cert_statuses = {
        enrollment.course_id: cert_info(request.user, enrollment.course_overview, enrollment.mode)
        for enrollment in course_enrollments
        }

    # sort the enrollment pairs by the enrollment date
    # course_enrollments.sort(key=lambda x: x.created, reverse=True)
    print 'cert_statuses:'
    print cert_statuses

    course_type1 = []
    course_type2 = []
    course_type3 = []
    course_type4 = []

    # 수정필요. https://github.com/kmoocdev2/edx-platform/commit/8da64778a4c8e758c5a9b012624c39846f100084#diff-55b798ee23a7fde8d1103408afcd0f16

    for c in course_enrollments:
        # 이수증 생성 여부: c.course.has_any_active_web_certificate

        print c.course.id, c.course.display_name, c.course.has_any_active_web_certificate

        if c.course.start and c.course.end and c.course.start > c.course.end:
            continue

        elif c.course.start and c.course.start > datetime.datetime.now(UTC):
            c.status = 'ready'
            course_type1.append(c)

        elif c.course.start and c.course.end and c.course.start <= datetime.datetime.now(
                UTC) <= c.course.end and datetime.datetime.now(UTC) <= c.course.enrollment_end:
            c.status = 'ing(ing)'
            course_type2.append(c)

        elif c.course.start and c.course.end and c.course.start <= datetime.datetime.now(
                UTC) <= c.course.end and datetime.datetime.now(UTC) <= c.course.enrollment_end:
            c.status = 'ing(end)'
            course_type2.append(c)

        elif c.course.has_ended():
            c.status = 'end'
            course_type3.append(c)

        else:
            c.status = 'none'
            course_type4.append(c)

    course_type1.sort(key=lambda x: x.created, reverse=True)
    course_type2.sort(key=lambda x: x.created, reverse=True)
    # course_type3.sort(key=lambda x: x.created, reverse=True)
    # course_type4.sort(key=lambda x: x.created, reverse=True)

    print 'course 1:'
    print course_type1
    print 'course 2:'
    print course_type2
    print 'course 3:'
    print course_type3
    print 'course 4:'
    print course_type4

    course_enrollments = course_type1 + course_type2 + course_type3 + course_type4

    print 'check step 1 s'
    for c in course_enrollments:
        print c.course.id, c.course.display_name
    print 'check step 1 e'

    show_email_settings_for = frozenset(
        enrollment.course_id for enrollment in course_enrollments if (
            BulkEmailFlag.feature_enabled(enrollment.course_id)
        )
    )

    # Verification Attempts
    # Used to generate the "you must reverify for course x" banner
    verification_status, verification_msg = SoftwareSecurePhotoVerification.user_status(user)

    # Gets data for midcourse reverifications, if any are necessary or have failed
    statuses = ["approved", "denied", "pending", "must_reverify"]
    reverifications = reverification_info(statuses)

    show_refund_option_for = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if enrollment.refundable()
    )

    block_courses = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if is_course_blocked(
            request,
            CourseRegistrationCode.objects.filter(
                course_id=enrollment.course_id,
                registrationcoderedemption__redeemed_by=request.user
            ),
            enrollment.course_id
        )
    )

    enrolled_courses_either_paid = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if enrollment.is_paid_course()
    )

    # If there are *any* denied reverifications that have not been toggled off,
    # we'll display the banner
    denied_banner = any(item.display for item in reverifications["denied"])

    # Populate the Order History for the side-bar.
    order_history_list = order_history(user, course_org_filter=course_org_filter, org_filter_out_set=org_filter_out_set)

    # get list of courses having pre-requisites yet to be completed
    courses_having_prerequisites = frozenset(
        enrollment.course_id for enrollment in course_enrollments
        if enrollment.course_overview.pre_requisite_courses
    )
    courses_requirements_not_met = get_pre_requisite_courses_not_completed(user, courses_having_prerequisites)

    if 'notlive' in request.GET:
        redirect_message = _("The course you are looking for does not start until {date}.").format(
            date=request.GET['notlive']
        )
    elif 'course_closed' in request.GET:
        redirect_message = _("The course you are looking for is closed for enrollment as of {date}.").format(
            date=request.GET['course_closed']
        )
    else:
        redirect_message = ''

    percents = {}

    # add course progress
    for dashboard_index, enrollment in enumerate(course_enrollments):
        course_id = str(enrollment.course_id)
        # if not enrollment.course_overview.has_started():
        #     percents[course_id] = None
        #     continue

        percents[course_id] = None

        # course = get_course_with_access(user, 'load', enrollment.course_id, depth=None, check_if_enrolled=True)
        # grade_summary = grades.grade(user, course, course_structure=None)
        # percents[course_id] = str(int(float(grade_summary['percent']) * 100))

    # cur = con.cursor()
    # query = """
    #     SELECT course_id
    #       FROM interest_course
    #       WHERE use_yn = 'Y' AND user_id = '""" + str(user.id) + """'
    #     """
    # print ('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
    # cur.execute(query)
    # rows = cur.fetchall()
    # cur.close()
    # interest_list = []
    # if (len(rows) > 0):
    #     for p in rows:
    #         interest_list.append(list(p)[0])
    # print interest_list

    final_list = []

    sys.setdefaultencoding('utf-8')
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    for c in course_enrollments:
        cur = con.cursor()
        query = """
            SELECT DATE_FORMAT(max(modified), "최종수강일 - %Y년%m월%d일"), course_id
              FROM courseware_studentmodule
             WHERE student_id = '{0}' AND course_id = '{1}';
        """.format(user.id, c.course.id)
        cur.execute(query)
        final_day = cur.fetchall()
        final_list.append(list(final_day[0]))
        cur.close()

    print ('final_list =====================')
    print type(final_list)
    print (final_list)

    status = request.POST.get('status')
    context = {
        'percents': percents,
        'enrollment_message': enrollment_message,
        'redirect_message': redirect_message,
        'course_enrollments': course_enrollments,
        'course_optouts': course_optouts,
        'message': message,
        'staff_access': staff_access,
        'errored_courses': errored_courses,
        'show_courseware_links_for': show_courseware_links_for,
        'all_course_modes': course_mode_info,
        'cert_statuses': cert_statuses,
        'credit_statuses': _credit_statuses(user, course_enrollments),
        'show_email_settings_for': show_email_settings_for,
        'reverifications': reverifications,
        'verification_status': verification_status,
        'verification_status_by_course': verify_status_by_course,
        'verification_msg': verification_msg,
        'show_refund_option_for': show_refund_option_for,
        'block_courses': block_courses,
        'denied_banner': denied_banner,
        'billing_email': settings.PAYMENT_SUPPORT_EMAIL,
        'user': user,
        'logout_url': reverse('logout'),
        'platform_name': platform_name,
        'enrolled_courses_either_paid': enrolled_courses_either_paid,
        'provider_states': [],
        'order_history_list': order_history_list,
        'courses_requirements_not_met': courses_requirements_not_met,
        'nav_hidden': True,
        'course_programs': course_programs,
        'disable_courseware_js': True,
        'show_program_listing': ProgramsApiConfig.current().show_program_listing,
        'status_flag': status,
        'final_list': final_list,
    }

    ecommerce_service = EcommerceService()
    if ecommerce_service.is_enabled(request.user):
        context.update({
            'use_ecommerce_payment_flow': True,
            'ecommerce_payment_page': ecommerce_service.payment_page_url(),
        })

    if request.is_ajax():
        return render_to_response('dashboard_ajax.html', context)

    return render_to_response('dashboard.html', context)


def _create_recent_enrollment_message(course_enrollments, course_modes):  # pylint: disable=invalid-name
    """
    Builds a recent course enrollment message.

    Constructs a new message template based on any recent course enrollments
    for the student.

    Args:
        course_enrollments (list[CourseEnrollment]): a list of course enrollments.
        course_modes (dict): Mapping of course ID's to course mode dictionaries.

    Returns:
        A string representing the HTML message output from the message template.
        None if there are no recently enrolled courses.

    """
    recently_enrolled_courses = _get_recently_enrolled_courses(course_enrollments)

    if recently_enrolled_courses:
        enroll_messages = [
            {
                "course_id": enrollment.course_overview.id,
                "course_name": enrollment.course_overview.display_name,
                "allow_donation": _allow_donation(course_modes, enrollment.course_overview.id, enrollment)
            }
            for enrollment in recently_enrolled_courses
            ]

        platform_name = configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME)

        return render_to_string(
            'enrollment/course_enrollment_message.html',
            {'course_enrollment_messages': enroll_messages, 'platform_name': platform_name}
        )


def _get_recently_enrolled_courses(course_enrollments):
    """
    Given a list of enrollments, filter out all but recent enrollments.

    Args:
        course_enrollments (list[CourseEnrollment]): A list of course enrollments.

    Returns:
        list[CourseEnrollment]: A list of recent course enrollments.
    """
    seconds = DashboardConfiguration.current().recent_enrollment_time_delta
    time_delta = (datetime.datetime.now(UTC) - datetime.timedelta(seconds=seconds))
    return [
        enrollment for enrollment in course_enrollments
        # If the enrollment has no created date, we are explicitly excluding the course
        # from the list of recent enrollments.
        if enrollment.is_active and enrollment.created > time_delta
        ]


def _allow_donation(course_modes, course_id, enrollment):
    """Determines if the dashboard will request donations for the given course.

    Check if donations are configured for the platform, and if the current course is accepting donations.

    Args:
        course_modes (dict): Mapping of course ID's to course mode dictionaries.
        course_id (str): The unique identifier for the course.
        enrollment(CourseEnrollment): The enrollment object in which the user is enrolled

    Returns:
        True if the course is allowing donations.

    """
    donations_enabled = DonationConfiguration.current().enabled
    return (
        donations_enabled and
        enrollment.mode in course_modes[course_id] and
        course_modes[course_id][enrollment.mode].min_price == 0
    )


def _update_email_opt_in(request, org):
    """Helper function used to hit the profile API if email opt-in is enabled."""

    email_opt_in = request.POST.get('email_opt_in')
    if email_opt_in is not None:
        email_opt_in_boolean = email_opt_in == 'true'
        preferences_api.update_email_opt_in(request.user, org, email_opt_in_boolean)


def _credit_statuses(user, course_enrollments):
    """
    Retrieve the status for credit courses.

    A credit course is a course for which a user can purchased
    college credit.  The current flow is:

    1. User becomes eligible for credit (submits verifications, passes the course, etc.)
    2. User purchases credit from a particular credit provider.
    3. User requests credit from the provider, usually creating an account on the provider's site.
    4. The credit provider notifies us whether the user's request for credit has been accepted or rejected.

    The dashboard is responsible for communicating the user's state in this flow.

    Arguments:
        user (User): The currently logged-in user.
        course_enrollments (list[CourseEnrollment]): List of enrollments for the
            user.

    Returns: dict

    The returned dictionary has keys that are `CourseKey`s and values that
    are dictionaries with:

        * eligible (bool): True if the user is eligible for credit in this course.
        * deadline (datetime): The deadline for purchasing and requesting credit for this course.
        * purchased (bool): Whether the user has purchased credit for this course.
        * provider_name (string): The display name of the credit provider.
        * provider_status_url (string): A URL the user can visit to check on their credit request status.
        * request_status (string): Either "pending", "approved", or "rejected"
        * error (bool): If true, an unexpected error occurred when retrieving the credit status,
            so the user should contact the support team.

    Example:
    {
        CourseKey.from_string("edX/DemoX/Demo_Course"): {
            "course_key": "edX/DemoX/Demo_Course",
            "eligible": True,
            "deadline": 2015-11-23 00:00:00 UTC,
            "purchased": True,
            "provider_name": "Hogwarts",
            "provider_status_url": "http://example.com/status",
            "request_status": "pending",
            "error": False
        }
    }

    """
    from openedx.core.djangoapps.credit import api as credit_api

    # Feature flag off
    if not settings.FEATURES.get("ENABLE_CREDIT_ELIGIBILITY"):
        return {}

    request_status_by_course = {
        request["course_key"]: request["status"]
        for request in credit_api.get_credit_requests_for_user(user.username)
        }

    credit_enrollments = {
        enrollment.course_id: enrollment
        for enrollment in course_enrollments
        if enrollment.mode == "credit"
        }

    # When a user purchases credit in a course, the user's enrollment
    # mode is set to "credit" and an enrollment attribute is set
    # with the ID of the credit provider.  We retrieve *all* such attributes
    # here to minimize the number of database queries.
    purchased_credit_providers = {
        attribute.enrollment.course_id: attribute.value
        for attribute in CourseEnrollmentAttribute.objects.filter(
        namespace="credit",
        name="provider_id",
        enrollment__in=credit_enrollments.values()
    ).select_related("enrollment")
        }

    provider_info_by_id = {
        provider["id"]: provider
        for provider in credit_api.get_credit_providers()
        }

    statuses = {}
    for eligibility in credit_api.get_eligibilities_for_user(user.username):
        course_key = CourseKey.from_string(unicode(eligibility["course_key"]))
        providers_names = get_credit_provider_display_names(course_key)
        status = {
            "course_key": unicode(course_key),
            "eligible": True,
            "deadline": eligibility["deadline"],
            "purchased": course_key in credit_enrollments,
            "provider_name": make_providers_strings(providers_names),
            "provider_status_url": None,
            "provider_id": None,
            "request_status": request_status_by_course.get(course_key),
            "error": False,
        }

        # If the user has purchased credit, then include information about the credit
        # provider from which the user purchased credit.
        # We retrieve the provider's ID from the an "enrollment attribute" set on the user's
        # enrollment when the user's order for credit is fulfilled by the E-Commerce service.
        if status["purchased"]:
            provider_id = purchased_credit_providers.get(course_key)
            if provider_id is None:
                status["error"] = True
                log.error(
                    u"Could not find credit provider associated with credit enrollment "
                    u"for user %s in course %s.  The user will not be able to see his or her "
                    u"credit request status on the student dashboard.  This attribute should "
                    u"have been set when the user purchased credit in the course.",
                    user.id, course_key
                )
            else:
                provider_info = provider_info_by_id.get(provider_id, {})
                status["provider_name"] = provider_info.get("display_name")
                status["provider_status_url"] = provider_info.get("status_url")
                status["provider_id"] = provider_id

        statuses[course_key] = status

    return statuses


@transaction.non_atomic_requests
@require_POST
@outer_atomic(read_committed=True)
def change_enrollment(request, check_access=True):
    """
    Modify the enrollment status for the logged-in user.

    The request parameter must be a POST request (other methods return 405)
    that specifies course_id and enrollment_action parameters. If course_id or
    enrollment_action is not specified, if course_id is not valid, if
    enrollment_action is something other than "enroll" or "unenroll", if
    enrollment_action is "enroll" and enrollment is closed for the course, or
    if enrollment_action is "unenroll" and the user is not enrolled in the
    course, a 400 error will be returned. If the user is not logged in, 403
    will be returned; it is important that only this case return 403 so the
    front end can redirect the user to a registration or login page when this
    happens. This function should only be called from an AJAX request, so
    the error messages in the responses should never actually be user-visible.

    Args:
        request (`Request`): The Django request object

    Keyword Args:
        check_access (boolean): If True, we check that an accessible course actually
            exists for the given course_key before we enroll the student.
            The default is set to False to avoid breaking legacy code or
            code with non-standard flows (ex. beta tester invitations), but
            for any standard enrollment flow you probably want this to be True.

    Returns:
        Response

    """
    # Get the user
    user = request.user

    # Ensure the user is authenticated
    if not user.is_authenticated():
        return HttpResponseForbidden()

    # Ensure we received a course_id
    action = request.POST.get("enrollment_action")
    if 'course_id' not in request.POST:
        return HttpResponseBadRequest(_("Course id not specified"))

    try:
        course_id = SlashSeparatedCourseKey.from_deprecated_string(request.POST.get("course_id"))
    except InvalidKeyError:
        log.warning(
            u"User %s tried to %s with invalid course id: %s",
            user.username,
            action,
            request.POST.get("course_id"),
        )
        return HttpResponseBadRequest(_("Invalid course id"))

    if action == "enroll":
        # Make sure the course exists
        # We don't do this check on unenroll, or a bad course id can't be unenrolled from
        if not modulestore().has_course(course_id):
            log.warning(
                u"User %s tried to enroll in non-existent course %s",
                user.username,
                course_id
            )
            return HttpResponseBadRequest(_("Course id is invalid"))

        # Record the user's email opt-in preference
        if settings.FEATURES.get('ENABLE_MKTG_EMAIL_OPT_IN'):
            _update_email_opt_in(request, course_id.org)

        available_modes = CourseMode.modes_for_course_dict(course_id)

        # Check whether the user is blocked from enrolling in this course
        # This can occur if the user's IP is on a global blacklist
        # or if the user is enrolling in a country in which the course
        # is not available.
        redirect_url = embargo_api.redirect_if_blocked(
            course_id, user=user, ip_address=get_ip(request),
            url=request.path
        )
        if redirect_url:
            return HttpResponse(redirect_url)

        # Check that auto enrollment is allowed for this course
        # (= the course is NOT behind a paywall)
        if CourseMode.can_auto_enroll(course_id):
            # Enroll the user using the default mode (audit)
            # We're assuming that users of the course enrollment table
            # will NOT try to look up the course enrollment model
            # by its slug.  If they do, it's possible (based on the state of the database)
            # for no such model to exist, even though we've set the enrollment type
            # to "audit".
            try:
                enroll_mode = CourseMode.auto_enroll_mode(course_id, available_modes)
                if enroll_mode:
                    enrollment = CourseEnrollment.enroll(user, course_id, check_access=check_access, mode=enroll_mode)
                    enrollment.send_signal(EnrollStatusChange.enroll)
            except Exception:  # pylint: disable=broad-except
                return HttpResponseBadRequest(_("Could not enroll"))

        # If we have more than one course mode or professional ed is enabled,
        # then send the user to the choose your track page.
        # (In the case of no-id-professional/professional ed, this will redirect to a page that
        # funnels users directly into the verification / payment flow)
        if CourseMode.has_verified_mode(available_modes) or CourseMode.has_professional_mode(available_modes):
            return HttpResponse(
                reverse("course_modes_choose", kwargs={'course_id': unicode(course_id)})
            )

        # Otherwise, there is only one mode available (the default)
        return HttpResponse()
    elif action == "unenroll":
        enrollment = CourseEnrollment.get_enrollment(user, course_id)
        if not enrollment:
            return HttpResponseBadRequest(_("You are not enrolled in this course"))

        certificate_info = cert_info(user, enrollment.course_overview, enrollment.mode)
        if certificate_info.get('status') in DISABLE_UNENROLL_CERT_STATES:
            return HttpResponseBadRequest(_("Your certificate prevents you from unenrolling from this course"))

        CourseEnrollment.unenroll(user, course_id)
        return HttpResponse()
    else:
        return HttpResponseBadRequest(_("Enrollment action is invalid"))


# Need different levels of logging
@ensure_csrf_cookie
def login_user(request, error=""):  # pylint: disable=too-many-statements,unused-argument
    """AJAX request to log in the user."""

    backend_name = None
    email = None
    password = None
    redirect_url = None
    response = None
    running_pipeline = None
    third_party_auth_requested = third_party_auth.is_enabled() and pipeline.running(request)
    third_party_auth_successful = False
    trumped_by_first_party_auth = bool(request.POST.get('email')) or bool(request.POST.get('password'))
    user = None
    platform_name = configuration_helpers.get_value("platform_name", settings.PLATFORM_NAME)

    if third_party_auth_requested and not trumped_by_first_party_auth:
        # The user has already authenticated via third-party auth and has not
        # asked to do first party auth by supplying a username or password. We
        # now want to put them through the same logging and cookie calculation
        # logic as with first-party auth.
        running_pipeline = pipeline.get(request)
        username = running_pipeline['kwargs'].get('username')
        backend_name = running_pipeline['backend']
        third_party_uid = running_pipeline['kwargs']['uid']
        requested_provider = provider.Registry.get_from_pipeline(running_pipeline)

        try:
            user = pipeline.get_authenticated_user(requested_provider, username, third_party_uid)
            third_party_auth_successful = True
        except User.DoesNotExist:
            AUDIT_LOG.warning(
                u"Login failed - user with username {username} has no social auth "
                "with backend_name {backend_name}".format(
                    username=username, backend_name=backend_name)
            )
            message = _(
                "You've successfully logged into your {provider_name} account, "
                "but this account isn't linked with an {platform_name} account yet."
            ).format(
                platform_name=platform_name,
                provider_name=requested_provider.name,
            )
            message += "<br/><br/>"
            message += _(
                "Use your {platform_name} username and password to log into {platform_name} below, "
                "and then link your {platform_name} account with {provider_name} from your dashboard."
            ).format(
                platform_name=platform_name,
                provider_name=requested_provider.name,
            )
            message += "<br/><br/>"
            message += _(
                "If you don't have an {platform_name} account yet, "
                "click <strong>Register</strong> at the top of the page."
            ).format(
                platform_name=platform_name
            )

            return HttpResponse(message, content_type="text/plain", status=403)

    else:

        if 'email' not in request.POST or 'password' not in request.POST:
            return JsonResponse({
                "success": False,
                # TODO: User error message
                "value": _('There was an error receiving your login information. Please email us.'),
            })  # TODO: this should be status code 400

        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
            cur = con.cursor()
            query = '''
              SELECT email, dormant_mail_cd, dormant_yn
                FROM auth_user
              where email= %s
            '''
            cur.execute(query, [email])
            row = cur.fetchone()

            context = {
                'active_account_url': '/active_account/%s' % email
            }

            print 'context:', context

            if row[2] != None and row[2] == 'Y':
                return render_to_response("drmt_login.html", context)

        except User.DoesNotExist:
            if settings.FEATURES['SQUELCH_PII_IN_LOGS']:
                AUDIT_LOG.warning(u"Login failed - Unknown user email")
            else:
                AUDIT_LOG.warning(u"Login failed - Unknown user email: {0}".format(email))

    # check if the user has a linked shibboleth account, if so, redirect the user to shib-login
    # This behavior is pretty much like what gmail does for shibboleth.  Try entering some @stanford.edu
    # address into the Gmail login.
    if settings.FEATURES.get('AUTH_USE_SHIB') and user:
        try:
            eamap = ExternalAuthMap.objects.get(user=user)
            if eamap.external_domain.startswith(external_auth.views.SHIBBOLETH_DOMAIN_PREFIX):
                return JsonResponse({
                    "success": False,
                    "redirect": reverse('shib-login'),
                })  # TODO: this should be status code 301  # pylint: disable=fixme
        except ExternalAuthMap.DoesNotExist:
            # This is actually the common case, logging in user without external linked login
            AUDIT_LOG.info(u"User %s w/o external auth attempting login", user)

    # see if account has been locked out due to excessive login failures
    user_found_by_email_lookup = user
    if user_found_by_email_lookup and LoginFailures.is_feature_enabled():
        if LoginFailures.is_user_locked_out(user_found_by_email_lookup):
            lockout_message = _('This account has been temporarily locked due '
                                'to excessive login failures. Try again later.')
            return JsonResponse({
                "success": False,
                "value": lockout_message,
            })  # TODO: this should be status code 429  # pylint: disable=fixme

    # see if the user must reset his/her password due to any policy settings
    if user_found_by_email_lookup and PasswordHistory.should_user_reset_password_now(user_found_by_email_lookup):
        return JsonResponse({
            "success": False,
            "value": _('Your password has expired due to password policy on this account. You must '
                       'reset your password before you can log in again. Please click the '
                       '"Forgot Password" link on this page to reset your password before logging in again.'),
        })  # TODO: this should be status code 403  # pylint: disable=fixme

    # if the user doesn't exist, we want to set the username to an invalid
    # username so that authentication is guaranteed to fail and we can take
    # advantage of the ratelimited backend
    username = user.username if user else ""

    if not third_party_auth_successful:
        try:
            user = authenticate(username=username, password=password, request=request)
        # this occurs when there are too many attempts from the same IP address
        except RateLimitException:
            return JsonResponse({
                "success": False,
                "value": _('Too many failed login attempts. Try again later.'),
            })  # TODO: this should be status code 429  # pylint: disable=fixme

    if user is None:
        # tick the failed login counters if the user exists in the database
        if user_found_by_email_lookup and LoginFailures.is_feature_enabled():
            LoginFailures.increment_lockout_counter(user_found_by_email_lookup)

        # if we didn't find this username earlier, the account for this email
        # doesn't exist, and doesn't have a corresponding password
        if username != "":
            if settings.FEATURES['SQUELCH_PII_IN_LOGS']:
                loggable_id = user_found_by_email_lookup.id if user_found_by_email_lookup else "<unknown>"
                AUDIT_LOG.warning(u"Login failed - password for user.id: {0} is invalid".format(loggable_id))
            else:
                AUDIT_LOG.warning(u"Login failed - password for {0} is invalid".format(email))
        return JsonResponse({
            "success": False,
            "value": _('Email or password is incorrect.'),
        })  # TODO: this should be status code 400  # pylint: disable=fixme

    # successful login, clear failed login attempts counters, if applicable
    if LoginFailures.is_feature_enabled():
        LoginFailures.clear_lockout_counter(user)

    # Track the user's sign in
    if hasattr(settings, 'LMS_SEGMENT_KEY') and settings.LMS_SEGMENT_KEY:
        tracking_context = tracker.get_tracker().resolve_context()
        analytics.identify(
            user.id,
            {
                'email': email,
                'username': username
            },
            {
                # Disable MailChimp because we don't want to update the user's email
                # and username in MailChimp on every page load. We only need to capture
                # this data on registration/activation.
                'MailChimp': False
            }
        )

        analytics.track(
            user.id,
            "edx.bi.user.account.authenticated",
            {
                'category': "conversion",
                'label': request.POST.get('course_id'),
                'provider': None
            },
            context={
                'ip': tracking_context.get('ip'),
                'Google Analytics': {
                    'clientId': tracking_context.get('client_id')
                }
            }
        )

    if user is not None and user.is_active:
        try:
            # We do not log here, because we have a handler registered
            # to perform logging on successful logins.
            login(request, user)
            if request.POST.get('remember') == 'true':
                request.session['ISREMEMBER'] = True
                request.session.set_expiry(604800)
                log.debug("Setting user session to never expire")
            else:
                request.session.set_expiry(0)
        except Exception as exc:  # pylint: disable=broad-except
            AUDIT_LOG.critical("Login failed - Could not create session. Is memcached running?")
            log.critical("Login failed - Could not create session. Is memcached running?")
            log.exception(exc)
            raise

        redirect_url = None  # The AJAX method calling should know the default destination upon success
        if third_party_auth_successful:
            redirect_url = pipeline.get_complete_url(backend_name)
        response = JsonResponse({
            "success": True,
            "redirect_url": redirect_url,
        })

        # Ensure that the external marketing site can
        # detect that the user is logged in.
        return set_logged_in_cookies(request, response, user)

    if settings.FEATURES['SQUELCH_PII_IN_LOGS']:
        AUDIT_LOG.warning(u"Login failed - Account not active for user.id: {0}, resending activation".format(user.id))
    else:
        AUDIT_LOG.warning(u"Login failed - Account not active for user {0}, resending activation".format(username))

    reactivation_email_for_user(user)
    not_activated_msg = _("Before you sign in, you need to activate your account. We have sent you an "
                          "email message with instructions for activating your account.")
    return JsonResponse({
        "success": False,
        "value": not_activated_msg,
    })  # TODO: this should be status code 400  # pylint: disable=fixme


@csrf_exempt
@require_POST
@social_utils.strategy("social:complete")
def login_oauth_token(request, backend):
    """
    Authenticate the client using an OAuth access token by using the token to
    retrieve information from a third party and matching that information to an
    existing user.
    """
    warnings.warn("Please use AccessTokenExchangeView instead.", DeprecationWarning)

    backend = request.backend
    if isinstance(backend, social_oauth.BaseOAuth1) or isinstance(backend, social_oauth.BaseOAuth2):
        if "access_token" in request.POST:
            # Tell third party auth pipeline that this is an API call
            request.session[pipeline.AUTH_ENTRY_KEY] = pipeline.AUTH_ENTRY_LOGIN_API
            user = None
            try:
                user = backend.do_auth(request.POST["access_token"])
            except (HTTPError, AuthException):
                pass
            # do_auth can return a non-User object if it fails
            if user and isinstance(user, User):
                login(request, user)
                return JsonResponse(status=204)
            else:
                # Ensure user does not re-enter the pipeline
                request.social_strategy.clean_partial_pipeline()
                return JsonResponse({"error": "invalid_token"}, status=401)
        else:
            return JsonResponse({"error": "invalid_request"}, status=400)
    raise Http404


@require_GET
@login_required
@ensure_csrf_cookie
def manage_user_standing(request):
    """
    Renders the view used to manage user standing. Also displays a table
    of user accounts that have been disabled and who disabled them.
    """
    if not request.user.is_staff:
        raise Http404
    all_disabled_accounts = UserStanding.objects.filter(
        account_status=UserStanding.ACCOUNT_DISABLED
    )

    all_disabled_users = [standing.user for standing in all_disabled_accounts]

    headers = ['username', 'account_changed_by']
    rows = []
    for user in all_disabled_users:
        row = [user.username, user.standing.changed_by]
        rows.append(row)

    context = {'headers': headers, 'rows': rows}

    return render_to_response("manage_user_standing.html", context)


@require_POST
@login_required
@ensure_csrf_cookie
def disable_account_ajax(request):
    """
    Ajax call to change user standing. Endpoint of the form
    in manage_user_standing.html
    """
    if not request.user.is_staff:
        raise Http404
    username = request.POST.get('username')
    context = {}
    if username is None or username.strip() == '':
        context['message'] = _('Please enter a username')
        return JsonResponse(context, status=400)

    account_action = request.POST.get('account_action')
    if account_action is None:
        context['message'] = _('Please choose an option')
        return JsonResponse(context, status=400)

    username = username.strip()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        context['message'] = _("User with username {} does not exist").format(username)
        return JsonResponse(context, status=400)
    else:
        user_account, _success = UserStanding.objects.get_or_create(
            user=user, defaults={'changed_by': request.user},
        )
        if account_action == 'disable':
            user_account.account_status = UserStanding.ACCOUNT_DISABLED
            context['message'] = _("Successfully disabled {}'s account").format(username)
            log.info(u"%s disabled %s's account", request.user, username)
        elif account_action == 'reenable':
            user_account.account_status = UserStanding.ACCOUNT_ENABLED
            context['message'] = _("Successfully reenabled {}'s account").format(username)
            log.info(u"%s reenabled %s's account", request.user, username)
        else:
            context['message'] = _("Unexpected account status")
            return JsonResponse(context, status=400)
        user_account.changed_by = request.user
        user_account.standing_last_changed_at = datetime.datetime.now(UTC)
        user_account.save()

    return JsonResponse(context)


@login_required
@ensure_csrf_cookie
def change_setting(request):
    """JSON call to change a profile setting: Right now, location"""
    # TODO (vshnayder): location is no longer used
    u_prof = UserProfile.objects.get(user=request.user)  # request.user.profile_cache
    if 'location' in request.POST:
        u_prof.location = request.POST['location']
    u_prof.save()

    return JsonResponse({
        "success": True,
        "location": u_prof.location,
    })


class AccountValidationError(Exception):
    def __init__(self, message, field):
        super(AccountValidationError, self).__init__(message)
        self.field = field


@receiver(post_save, sender=User)
def user_signup_handler(sender, **kwargs):  # pylint: disable=unused-argument
    """
    handler that saves the user Signup Source
    when the user is created
    """
    if 'created' in kwargs and kwargs['created']:
        site = configuration_helpers.get_value('SITE_NAME')
        if site:
            user_signup_source = UserSignupSource(user=kwargs['instance'], site=site)
            user_signup_source.save()
            log.info(u'user {} originated from a white labeled "Microsite"'.format(kwargs['instance'].id))


def _do_create_account(form, custom_form=None):
    """
    Given cleaned post variables, create the User and UserProfile objects, as well as the
    registration for this user.

    Returns a tuple (User, UserProfile, Registration).

    Note: this function is also used for creating test users.
    """
    errors = {}
    errors.update(form.errors)
    if custom_form:
        errors.update(custom_form.errors)

    if errors:
        raise ValidationError(errors)

    user = User(
        username=form.cleaned_data["username"],
        email=form.cleaned_data["email"],
        is_active=False
    )
    user.set_password(form.cleaned_data["password"])
    registration = Registration()

    # TODO: Rearrange so that if part of the process fails, the whole process fails.
    # Right now, we can have e.g. no registration e-mail sent out and a zombie account
    try:
        with transaction.atomic():
            user.save()
            if custom_form:
                custom_model = custom_form.save(commit=False)
                custom_model.user = user
                custom_model.save()
    except IntegrityError:
        # Figure out the cause of the integrity error
        if len(User.objects.filter(username=user.username)) > 0:
            raise AccountValidationError(
                _("An account with the Public Username '{username}' already exists.").format(username=user.username),
                field="username"
            )
        elif len(User.objects.filter(email=user.email)) > 0:
            raise AccountValidationError(
                _("An account with the Email '{email}' already exists.").format(email=user.email),
                field="email"
            )
        else:
            raise

    # add this account creation to password history
    # NOTE, this will be a NOP unless the feature has been turned on in configuration
    password_history_entry = PasswordHistory()
    password_history_entry.create(user)

    registration.register(user)

    profile_fields = [
        "name", "level_of_education", "gender", "mailing_address", "city", "country", "goals",
        "year_of_birth"
    ]
    profile = UserProfile(
        user=user,
        **{key: form.cleaned_data.get(key) for key in profile_fields}
    )
    extended_profile = form.cleaned_extended_profile
    if extended_profile:
        profile.meta = json.dumps(extended_profile)
    try:
        profile.save()
    except Exception:  # pylint: disable=broad-except
        log.exception("UserProfile creation failed for user {id}.".format(id=user.id))
        raise

    return (user, profile, registration)


def create_account_with_params(request, params):
    """
    Given a request and a dict of parameters (which may or may not have come
    from the request), create an account for the requesting user, including
    creating a comments service user object and sending an activation email.
    This also takes external/third-party auth into account, updates that as
    necessary, and authenticates the user for the request's session.

    Does not return anything.

    Raises AccountValidationError if an account with the username or email
    specified by params already exists, or ValidationError if any of the given
    parameters is invalid for any other reason.

    Issues with this code:
    * It is not transactional. If there is a failure part-way, an incomplete
      account will be created and left in the database.
    * Third-party auth passwords are not verified. There is a comment that
      they are unused, but it would be helpful to have a sanity check that
      they are sane.
    * It is over 300 lines long (!) and includes disprate functionality, from
      registration e-mails to all sorts of other things. It should be broken
      up into semantically meaningful functions.
    * The user-facing text is rather unfriendly (e.g. "Username must be a
      minimum of two characters long" rather than "Please use a username of
      at least two characters").
    """
    # Copy params so we can modify it; we can't just do dict(params) because if
    # params is request.POST, that results in a dict containing lists of values
    params = dict(params.items())

    # allow to define custom set of required/optional/hidden fields via configuration
    extra_fields = configuration_helpers.get_value(
        'REGISTRATION_EXTRA_FIELDS',
        getattr(settings, 'REGISTRATION_EXTRA_FIELDS', {})
    )

    # Boolean of whether a 3rd party auth provider and credentials were provided in
    # the API so the newly created account can link with the 3rd party account.
    #
    # Note: this is orthogonal to the 3rd party authentication pipeline that occurs
    # when the account is created via the browser and redirect URLs.
    should_link_with_social_auth = third_party_auth.is_enabled() and 'provider' in params

    # 정책적으로 수정이 필요함.
    # if should_link_with_social_auth or (third_party_auth.is_enabled() and pipeline.running(request)):
    #     params["password"] = pipeline.make_random_password()

    # if doing signup for an external authorization, then get email, password, name from the eamap
    # don't use the ones from the form, since the user could have hacked those
    # unless originally we didn't get a valid email or name from the external auth
    # TODO: We do not check whether these values meet all necessary criteria, such as email length
    do_external_auth = 'ExternalAuthMap' in request.session
    if do_external_auth:
        eamap = request.session['ExternalAuthMap']
        try:
            validate_email(eamap.external_email)
            params["email"] = eamap.external_email
        except ValidationError:
            pass
        if eamap.external_name.strip() != '':
            params["name"] = eamap.external_name
        params["password"] = eamap.internal_password
        log.debug(u'In create_account with external_auth: user = %s, email=%s', params["name"], params["email"])

    extended_profile_fields = configuration_helpers.get_value('extended_profile_fields', [])
    enforce_password_policy = (
        settings.FEATURES.get("ENFORCE_PASSWORD_POLICY", False) and
        not do_external_auth
    )
    # Can't have terms of service for certain SHIB users, like at Stanford
    registration_fields = getattr(settings, 'REGISTRATION_EXTRA_FIELDS', {})
    tos_required = (
                       registration_fields.get('terms_of_service') != 'hidden' or
                       registration_fields.get('honor_code') != 'hidden'
                   ) and (
                       not settings.FEATURES.get("AUTH_USE_SHIB") or
                       not settings.FEATURES.get("SHIB_DISABLE_TOS") or
                       not do_external_auth or
                       not eamap.external_domain.startswith(
                           external_auth.views.SHIBBOLETH_DOMAIN_PREFIX
                       )
                   )

    form = AccountCreationForm(
        data=params,
        extra_fields=extra_fields,
        extended_profile_fields=extended_profile_fields,
        enforce_username_neq_password=True,
        enforce_password_policy=enforce_password_policy,
        tos_required=tos_required,
    )
    custom_form = get_registration_extension_form(data=params)

    # Perform operations within a transaction that are critical to account creation
    with transaction.atomic():
        # first, create the account
        (user, profile, registration) = _do_create_account(form, custom_form)

        # next, link the account with social auth, if provided via the API.
        # (If the user is using the normal register page, the social auth pipeline does the linking, not this code)
        if should_link_with_social_auth:
            backend_name = params['provider']
            request.social_strategy = social_utils.load_strategy(request)
            redirect_uri = reverse('social:complete', args=(backend_name,))
            request.backend = social_utils.load_backend(request.social_strategy, backend_name, redirect_uri)
            social_access_token = params.get('access_token')
            if not social_access_token:
                raise ValidationError({
                    'access_token': [
                        _("An access_token is required when passing value ({}) for provider.").format(
                            params['provider']
                        )
                    ]
                })
            request.session[pipeline.AUTH_ENTRY_KEY] = pipeline.AUTH_ENTRY_REGISTER_API
            pipeline_user = None
            error_message = ""
            try:
                pipeline_user = request.backend.do_auth(social_access_token, user=user)
            except AuthAlreadyAssociated:
                error_message = _("The provided access_token is already associated with another user.")
            except (HTTPError, AuthException):
                error_message = _("The provided access_token is not valid.")
            if not pipeline_user or not isinstance(pipeline_user, User):
                # Ensure user does not re-enter the pipeline
                request.social_strategy.clean_partial_pipeline()
                raise ValidationError({'access_token': [error_message]})

    # Perform operations that are non-critical parts of account creation
    preferences_api.set_user_preference(user, LANGUAGE_KEY, get_language())

    if settings.FEATURES.get('ENABLE_DISCUSSION_EMAIL_DIGEST'):
        try:
            enable_notifications(user)
        except Exception:  # pylint: disable=broad-except
            log.exception("Enable discussion notifications failed for user {id}.".format(id=user.id))

    dog_stats_api.increment("common.student.account_created")

    # If the user is registering via 3rd party auth, track which provider they use
    third_party_provider = None
    running_pipeline = None
    if third_party_auth.is_enabled() and pipeline.running(request):
        running_pipeline = pipeline.get(request)
        third_party_provider = provider.Registry.get_from_pipeline(running_pipeline)

    # Track the user's registration
    if hasattr(settings, 'LMS_SEGMENT_KEY') and settings.LMS_SEGMENT_KEY:
        tracking_context = tracker.get_tracker().resolve_context()
        identity_args = [
            user.id,  # pylint: disable=no-member
            {
                'email': user.email,
                'username': user.username,
                'name': profile.name,
                # Mailchimp requires the age & yearOfBirth to be integers, we send a sane integer default if falsey.
                'age': profile.age or -1,
                'yearOfBirth': profile.year_of_birth or datetime.datetime.now(UTC).year,
                'education': profile.level_of_education_display,
                'address': profile.mailing_address,
                'gender': profile.gender_display,
                'country': unicode(profile.country),
            }
        ]

        if hasattr(settings, 'MAILCHIMP_NEW_USER_LIST_ID'):
            identity_args.append({
                "MailChimp": {
                    "listId": settings.MAILCHIMP_NEW_USER_LIST_ID
                }
            })

        analytics.identify(*identity_args)

        analytics.track(
            user.id,
            "edx.bi.user.account.registered",
            {
                'category': 'conversion',
                'label': params.get('course_id'),
                'provider': third_party_provider.name if third_party_provider else None
            },
            context={
                'ip': tracking_context.get('ip'),
                'Google Analytics': {
                    'clientId': tracking_context.get('client_id')
                }
            }
        )

    # Announce registration
    REGISTER_USER.send(sender=None, user=user, profile=profile)

    create_comments_service_user(user)

    # Don't send email if we are:
    #
    # 1. Doing load testing.
    # 2. Random user generation for other forms of testing.
    # 3. External auth bypassing activation.
    # 4. Have the platform configured to not require e-mail activation.
    # 5. Registering a new user using a trusted third party provider (with skip_email_verification=True)
    #
    # Note that this feature is only tested as a flag set one way or
    # the other for *new* systems. we need to be careful about
    # changing settings on a running system to make sure no users are
    # left in an inconsistent state (or doing a migration if they are).
    send_email = (
        not settings.FEATURES.get('SKIP_EMAIL_VALIDATION', None) and
        not settings.FEATURES.get('AUTOMATIC_AUTH_FOR_TESTING') and
        not (do_external_auth and settings.FEATURES.get('BYPASS_ACTIVATION_EMAIL_FOR_EXTAUTH')) and
        not (
            third_party_provider and third_party_provider.skip_email_verification and
            user.email == running_pipeline['kwargs'].get('details', {}).get('email')
        )
    )
    if send_email:
        context = {
            'name': profile.name,
            'key': registration.activation_key,
        }

        # composes activation email
        subject = render_to_string('emails/activation_email_subject.txt', context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('emails/activation_email.txt', context)

        from_address = configuration_helpers.get_value(
            'email_from_address',
            settings.DEFAULT_FROM_EMAIL
        )
        try:
            if settings.FEATURES.get('REROUTE_ACTIVATION_EMAIL'):
                dest_addr = settings.FEATURES['REROUTE_ACTIVATION_EMAIL']
                message = ("Activation for %s (%s): %s\n" % (user, user.email, profile.name) +
                           '-' * 80 + '\n\n' + message)
                mail.send_mail(subject, message, from_address, [dest_addr], fail_silently=False)
            else:
                user.email_user(subject, message, from_address)
        except Exception:  # pylint: disable=broad-except
            log.error(u'Unable to send activation email to user from "%s"', from_address, exc_info=True)
    else:
        registration.activate()
        _enroll_user_in_pending_courses(user)  # Enroll student in any pending courses

    # Immediately after a user creates an account, we log them in. They are only
    # logged in until they close the browser. They can't log in again until they click
    # the activation link from the email.
    new_user = authenticate(username=user.username, password=params['password'])
    login(request, new_user)
    request.session.set_expiry(0)

    _record_registration_attribution(request, new_user)

    # TODO: there is no error checking here to see that the user actually logged in successfully,
    # and is not yet an active user.
    if new_user is not None:
        AUDIT_LOG.info(u"Login success on new account creation - {0}".format(new_user.username))

    if do_external_auth:
        eamap.user = new_user
        eamap.dtsignup = datetime.datetime.now(UTC)
        eamap.save()
        AUDIT_LOG.info(u"User registered with external_auth %s", new_user.username)
        AUDIT_LOG.info(u'Updated ExternalAuthMap for %s to be %s', new_user.username, eamap)

        if settings.FEATURES.get('BYPASS_ACTIVATION_EMAIL_FOR_EXTAUTH'):
            log.info('bypassing activation email')
            new_user.is_active = True
            new_user.save()
            AUDIT_LOG.info(u"Login activated on extauth account - {0} ({1})".format(new_user.username, new_user.email))

    return new_user


def _enroll_user_in_pending_courses(student):
    """
    Enroll student in any pending courses he/she may have.
    """
    ceas = CourseEnrollmentAllowed.objects.filter(email=student.email)
    for cea in ceas:
        if cea.auto_enroll:
            enrollment = CourseEnrollment.enroll(student, cea.course_id)
            manual_enrollment_audit = ManualEnrollmentAudit.get_manual_enrollment_by_email(student.email)
            if manual_enrollment_audit is not None:
                # get the enrolled by user and reason from the ManualEnrollmentAudit table.
                # then create a new ManualEnrollmentAudit table entry for the same email
                # different transition state.
                ManualEnrollmentAudit.create_manual_enrollment_audit(
                    manual_enrollment_audit.enrolled_by, student.email, ALLOWEDTOENROLL_TO_ENROLLED,
                    manual_enrollment_audit.reason, enrollment
                )


def _record_registration_attribution(request, user):
    """
    Attribute this user's registration to the referring affiliate, if
    applicable.
    """
    affiliate_id = request.COOKIES.get(settings.AFFILIATE_COOKIE_NAME)
    if user is not None and affiliate_id is not None:
        UserAttribute.set_user_attribute(user, REGISTRATION_AFFILIATE_ID, affiliate_id)


@csrf_exempt
def active_account(request, email):
    user = User.objects.get(email=email)

    with connections['default'].cursor() as cur:
        query = """
            UPDATE auth_user a
                   INNER JOIN drmt_auth_user b ON b.dormant_yn = 'Y' AND a.id = b.id
               SET a.username = b.username,
                   a.first_name = b.first_name,
                   a.last_name = b.last_name,
                   a.email = b.email,
                   a.password = b.password,
                   a.dormant_yn = 'N'
             WHERE a.id = %s;
        """

        cur.execute(query, [user.id])

        query = """
            UPDATE auth_userprofile a
                   INNER JOIN drmt_auth_userprofile b
                      ON b.dormant_yn = 'Y' AND a.id = b.id
               SET a.name = b.name,
                   a.language = b.language,
                   a.location = b.location,
                   a.meta = b.meta,
                   a.gender = b.gender,
                   a.mailing_address = b.mailing_address,
                   a.year_of_birth = b.year_of_birth,
                   a.level_of_education = b.level_of_education,
                   a.goals = b.goals,
                   a.country = b.country,
                   a.city = b.city,
                   a.bio = b.bio
             WHERE a.id = %s;
        """

        cur.execute(query, [user.id])

        query = """
            UPDATE drmt_auth_user
               SET dormant_yn = 'N'
             WHERE dormant_yn = 'Y' AND id = %s;
        """
        cur.execute(query, [user.id])

        query = """
            UPDATE drmt_auth_userprofile
               SET dormant_yn = 'N'
             WHERE dormant_yn = 'Y' AND id = %s;
        """
        cur.execute(query, [user.id])

    return redirect('/login')


@csrf_exempt
def create_account(request, post_override=None):
    """
    JSON call to create new edX account.
    Used by form in signup_modal.html, which is included into navigation.html
    """
    warnings.warn("Please use RegistrationView instead.", DeprecationWarning)

    try:
        user = create_account_with_params(request, post_override or request.POST)
    except AccountValidationError as exc:
        return JsonResponse({'success': False, 'value': exc.message, 'field': exc.field}, status=400)
    except ValidationError as exc:
        field, error_list = next(exc.message_dict.iteritems())
        return JsonResponse(
            {
                "success": False,
                "field": field,
                "value": error_list[0],
            },
            status=400
        )

    redirect_url = None  # The AJAX method calling should know the default destination upon success

    # Resume the third-party-auth pipeline if necessary.
    if third_party_auth.is_enabled() and pipeline.running(request):
        running_pipeline = pipeline.get(request)
        redirect_url = pipeline.get_complete_url(running_pipeline['backend'])

    response = JsonResponse({
        'success': True,
        'redirect_url': redirect_url,
    })
    set_logged_in_cookies(request, response, user)
    return response


def auto_auth(request):
    """
    Create or configure a user account, then log in as that user.

    Enabled only when
    settings.FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] is true.

    Accepts the following querystring parameters:
    * `username`, `email`, and `password` for the user account
    * `full_name` for the user profile (the user's full name; defaults to the username)
    * `staff`: Set to "true" to make the user global staff.
    * `course_id`: Enroll the student in the course with `course_id`
    * `roles`: Comma-separated list of roles to grant the student in the course with `course_id`
    * `no_login`: Define this to create the user but not login
    * `redirect`: Set to "true" will redirect to the `redirect_to` value if set, or
        course home page if course_id is defined, otherwise it will redirect to dashboard
    * `redirect_to`: will redirect to to this url
    If username, email, or password are not provided, use
    randomly generated credentials.
    """

    # Generate a unique name to use if none provided
    unique_name = uuid.uuid4().hex[0:30]

    # Use the params from the request, otherwise use these defaults
    username = request.GET.get('username', unique_name)
    password = request.GET.get('password', unique_name)
    email = request.GET.get('email', unique_name + "@example.com")
    full_name = request.GET.get('full_name', username)
    is_staff = request.GET.get('staff', None)
    is_superuser = request.GET.get('superuser', None)
    course_id = request.GET.get('course_id', None)
    redirect_to = request.GET.get('redirect_to', None)

    # mode has to be one of 'honor'/'professional'/'verified'/'audit'/'no-id-professional'/'credit'
    enrollment_mode = request.GET.get('enrollment_mode', 'honor')

    course_key = None
    if course_id:
        course_key = CourseLocator.from_string(course_id)
    role_names = [v.strip() for v in request.GET.get('roles', '').split(',') if v.strip()]
    redirect_when_done = request.GET.get('redirect', '').lower() == 'true' or redirect_to
    login_when_done = 'no_login' not in request.GET

    form = AccountCreationForm(
        data={
            'username': username,
            'email': email,
            'password': password,
            'name': full_name,
        },
        tos_required=False
    )

    # Attempt to create the account.
    # If successful, this will return a tuple containing
    # the new user object.
    try:
        user, profile, reg = _do_create_account(form)
    except (AccountValidationError, ValidationError):
        # Attempt to retrieve the existing user.
        user = User.objects.get(username=username)
        user.email = email
        user.set_password(password)
        user.save()
        profile = UserProfile.objects.get(user=user)
        reg = Registration.objects.get(user=user)

    # Set the user's global staff bit
    if is_staff is not None:
        user.is_staff = (is_staff == "true")
        user.save()

    if is_superuser is not None:
        user.is_superuser = (is_superuser == "true")
        user.save()

    # Activate the user
    reg.activate()
    reg.save()

    # ensure parental consent threshold is met
    year = datetime.date.today().year
    age_limit = settings.PARENTAL_CONSENT_AGE_LIMIT
    profile.year_of_birth = (year - age_limit) - 1
    profile.save()

    # Enroll the user in a course
    if course_key is not None:
        CourseEnrollment.enroll(user, course_key, mode=enrollment_mode)

    # Apply the roles
    for role_name in role_names:
        role = Role.objects.get(name=role_name, course_id=course_key)
        user.roles.add(role)

    # Log in as the user
    if login_when_done:
        user = authenticate(username=username, password=password)
        login(request, user)

    create_comments_service_user(user)

    # Provide the user with a valid CSRF token
    # then return a 200 response unless redirect is true
    if redirect_when_done:
        # Redirect to specific page if specified
        if redirect_to:
            redirect_url = redirect_to
        # Redirect to course info page if course_id is known
        elif course_id:
            try:
                # redirect to course info page in LMS
                redirect_url = reverse(
                    'info',
                    kwargs={'course_id': course_id}
                )
            except NoReverseMatch:
                # redirect to course outline page in Studio
                redirect_url = reverse(
                    'course_handler',
                    kwargs={'course_key_string': course_id}
                )
        else:
            try:
                # redirect to dashboard for LMS
                redirect_url = reverse('dashboard')
            except NoReverseMatch:
                # redirect to home for Studio
                redirect_url = reverse('home')

        return redirect(redirect_url)
    elif request.META.get('HTTP_ACCEPT') == 'application/json':
        response = JsonResponse({
            'created_status': u"Logged in" if login_when_done else "Created",
            'username': username,
            'email': email,
            'password': password,
            'user_id': user.id,  # pylint: disable=no-member
            'anonymous_id': anonymous_id_for_user(user, None),
        })
    else:
        success_msg = u"{} user {} ({}) with password {} and user_id {}".format(
            u"Logged in" if login_when_done else "Created",
            username, email, password, user.id  # pylint: disable=no-member
        )
        response = HttpResponse(success_msg)
    response.set_cookie('csrftoken', csrf(request)['csrf_token'])
    return response


@ensure_csrf_cookie
def activate_account(request, key):
    """When link in activation e-mail is clicked"""
    regs = Registration.objects.filter(activation_key=key)
    if len(regs) == 1:
        user_logged_in = request.user.is_authenticated()
        already_active = True
        if not regs[0].user.is_active:
            regs[0].activate()
            already_active = False

        # Enroll student in any pending courses he/she may have if auto_enroll flag is set
        _enroll_user_in_pending_courses(regs[0].user)

        resp = render_to_response(
            "registration/activation_complete.html",
            {
                'user_logged_in': user_logged_in,
                'already_active': already_active
            }
        )
        return resp
    if len(regs) == 0:
        return render_to_response(
            "registration/activation_invalid.html",
            {'csrf': csrf(request)['csrf_token']}
        )
    return HttpResponseServerError(_("Unknown error. Please e-mail us to let us know how it happened."))


@csrf_exempt
@require_POST
def password_reset(request):
    """ Attempts to send a password reset e-mail. """
    # Add some rate limiting here by re-using the RateLimitMixin as a helper class
    limiter = BadRequestRateLimiter()
    if limiter.is_rate_limit_exceeded(request):
        AUDIT_LOG.warning("Rate limit exceeded in password_reset")
        return HttpResponseForbidden()

    form = PasswordResetFormNoActive(request.POST)
    if form.is_valid():
        form.save(use_https=request.is_secure(),
                  from_email=configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL),
                  request=request,
                  domain_override=request.get_host())
        # When password change is complete, a "edx.user.settings.changed" event will be emitted.
        # But because changing the password is multi-step, we also emit an event here so that we can
        # track where the request was initiated.
        tracker.emit(
            SETTING_CHANGE_INITIATED,
            {
                "setting": "password",
                "old": None,
                "new": None,
                "user_id": request.user.id,
            }
        )
    else:
        # bad user? tick the rate limiter counter
        AUDIT_LOG.info("Bad password_reset user passed in.")
        limiter.tick_bad_request_counter(request)

    return JsonResponse({
        'success': True,
        'value': render_to_string('registration/password_reset_done.html', {}),
    })


def uidb36_to_uidb64(uidb36):
    """
    Needed to support old password reset URLs that use base36-encoded user IDs
    https://github.com/django/django/commit/1184d077893ff1bc947e45b00a4d565f3df81776#diff-c571286052438b2e3190f8db8331a92bR231
    Args:
        uidb36: base36-encoded user ID

    Returns: base64-encoded user ID. Otherwise returns a dummy, invalid ID
    """
    try:
        uidb64 = force_text(urlsafe_base64_encode(force_bytes(base36_to_int(uidb36))))
    except ValueError:
        uidb64 = '1'  # dummy invalid ID (incorrect padding for base64)
    return uidb64


def validate_password(user, password):
    """
    Tie in password policy enforcement as an optional level of
    security protection

    Args:
        user: the user object whose password we're checking.
        password: the user's proposed new password.

    Returns:
        is_valid_password: a boolean indicating if the new password
            passes the validation.
        err_msg: an error message if there's a violation of one of the password
            checks. Otherwise, `None`.
    """
    err_msg = None

    if settings.FEATURES.get('ENFORCE_PASSWORD_POLICY', False):
        try:
            validate_password_strength(password)
        except ValidationError as err:
            err_msg = _('Password: ') + '; '.join(err.messages)

    # also, check the password reuse policy
    if not PasswordHistory.is_allowable_password_reuse(user, password):
        if user.is_staff:
            num_distinct = settings.ADVANCED_SECURITY_CONFIG['MIN_DIFFERENT_STAFF_PASSWORDS_BEFORE_REUSE']
        else:
            num_distinct = settings.ADVANCED_SECURITY_CONFIG['MIN_DIFFERENT_STUDENT_PASSWORDS_BEFORE_REUSE']
        # Because of how ngettext is, splitting the following into shorter lines would be ugly.
        # pylint: disable=line-too-long
        err_msg = ungettext(
            "You are re-using a password that you have used recently. You must have {num} distinct password before reusing a previous password.",
            "You are re-using a password that you have used recently. You must have {num} distinct passwords before reusing a previous password.",
            num_distinct
        ).format(num=num_distinct)

    # also, check to see if passwords are getting reset too frequent
    if PasswordHistory.is_password_reset_too_soon(user):
        num_days = settings.ADVANCED_SECURITY_CONFIG['MIN_TIME_IN_DAYS_BETWEEN_ALLOWED_RESETS']
        # Because of how ngettext is, splitting the following into shorter lines would be ugly.
        # pylint: disable=line-too-long
        err_msg = ungettext(
            "You are resetting passwords too frequently. Due to security policies, {num} day must elapse between password resets.",
            "You are resetting passwords too frequently. Due to security policies, {num} days must elapse between password resets.",
            num_days
        ).format(num=num_days)

    is_password_valid = err_msg is None

    return is_password_valid, err_msg


def password_reset_confirm_wrapper(request, uidb36=None, token=None):
    """
    A wrapper around django.contrib.auth.views.password_reset_confirm.
    Needed because we want to set the user as active at this step.
    We also optionally do some additional password policy checks.
    """
    # convert old-style base36-encoded user id to base64
    uidb64 = uidb36_to_uidb64(uidb36)
    platform_name = {
        "platform_name": configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME)
    }
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        # if there's any error getting a user, just let django's
        # password_reset_confirm function handle it.
        return password_reset_confirm(
            request, uidb64=uidb64, token=token, extra_context=platform_name
        )

    if request.method == 'POST':
        password = request.POST['new_password1']
        is_password_valid, password_err_msg = validate_password(user, password)
        if not is_password_valid:
            # We have a password reset attempt which violates some security
            # policy. Use the existing Django template to communicate that
            # back to the user.
            context = {
                'validlink': False,
                'form': None,
                'title': _('Password reset unsuccessful'),
                'err_msg': password_err_msg,
            }
            context.update(platform_name)
            return TemplateResponse(
                request, 'registration/password_reset_confirm.html', context
            )

        # remember what the old password hash is before we call down
        old_password_hash = user.password

        response = password_reset_confirm(
            request, uidb64=uidb64, token=token, extra_context=platform_name
        )

        # get the updated user
        updated_user = User.objects.get(id=uid_int)

        # did the password hash change, if so record it in the PasswordHistory
        if updated_user.password != old_password_hash:
            entry = PasswordHistory()
            entry.create(updated_user)

    else:
        response = password_reset_confirm(
            request, uidb64=uidb64, token=token, extra_context=platform_name
        )

        response_was_successful = response.context_data.get('validlink')
        if response_was_successful and not user.is_active:
            user.is_active = True
            user.save()

    return response


def reactivation_email_for_user(user):
    try:
        reg = Registration.objects.get(user=user)
    except Registration.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": _('No inactive user with this e-mail exists'),
        })  # TODO: this should be status code 400  # pylint: disable=fixme

    context = {
        'name': user.profile.name,
        'key': reg.activation_key,
    }

    subject = render_to_string('emails/activation_email_subject.txt', context)
    subject = ''.join(subject.splitlines())
    message = render_to_string('emails/activation_email.txt', context)

    try:
        user.email_user(subject, message, configuration_helpers.get_value(
            'email_from_address',
            settings.DEFAULT_FROM_EMAIL,
        ))
    except Exception:  # pylint: disable=broad-except
        log.error(
            u'Unable to send reactivation email from "%s"',
            configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL),
            exc_info=True
        )
        return JsonResponse({
            "success": False,
            "error": _('Unable to send reactivation email')
        })  # TODO: this should be status code 500  # pylint: disable=fixme

    return JsonResponse({"success": True})


def validate_new_email(user, new_email):
    """
    Given a new email for a user, does some basic verification of the new address If any issues are encountered
    with verification a ValueError will be thrown.
    """
    try:
        validate_email(new_email)
    except ValidationError:
        raise ValueError(_('Valid e-mail address required.'))

    if new_email == user.email:
        raise ValueError(_('Old email is the same as the new email.'))

    if User.objects.filter(email=new_email).count() != 0:
        raise ValueError(_('An account with this e-mail already exists.'))


def do_email_change_request(user, new_email, activation_key=None):
    """
    Given a new email for a user, does some basic verification of the new address and sends an activation message
    to the new address. If any issues are encountered with verification or sending the message, a ValueError will
    be thrown.
    """
    pec_list = PendingEmailChange.objects.filter(user=user)
    if len(pec_list) == 0:
        pec = PendingEmailChange()
        pec.user = user
    else:
        pec = pec_list[0]

    # if activation_key is not passing as an argument, generate a random key
    if not activation_key:
        activation_key = uuid.uuid4().hex

    pec.new_email = new_email
    pec.activation_key = activation_key
    pec.save()

    context = {
        'key': pec.activation_key,
        'old_email': user.email,
        'new_email': pec.new_email
    }

    subject = render_to_string('emails/email_change_subject.txt', context)
    subject = ''.join(subject.splitlines())

    message = render_to_string('emails/email_change.txt', context)

    from_address = configuration_helpers.get_value(
        'email_from_address',
        settings.DEFAULT_FROM_EMAIL
    )
    try:
        mail.send_mail(subject, message, from_address, [pec.new_email])
    except Exception:  # pylint: disable=broad-except
        log.error(u'Unable to send email activation link to user from "%s"', from_address, exc_info=True)
        raise ValueError(_('Unable to send email activation link. Please try again later.'))

    # When the email address change is complete, a "edx.user.settings.changed" event will be emitted.
    # But because changing the email address is multi-step, we also emit an event here so that we can
    # track where the request was initiated.
    tracker.emit(
        SETTING_CHANGE_INITIATED,
        {
            "setting": "email",
            "old": context['old_email'],
            "new": context['new_email'],
            "user_id": user.id,
        }
    )


@ensure_csrf_cookie
def confirm_email_change(request, key):  # pylint: disable=unused-argument
    """
    User requested a new e-mail. This is called when the activation
    link is clicked. We confirm with the old e-mail, and update
    """
    with transaction.atomic():
        try:
            pec = PendingEmailChange.objects.get(activation_key=key)
        except PendingEmailChange.DoesNotExist:
            response = render_to_response("invalid_email_key.html", {})
            transaction.set_rollback(True)
            return response

        user = pec.user
        address_context = {
            'old_email': user.email,
            'new_email': pec.new_email
        }

        if len(User.objects.filter(email=pec.new_email)) != 0:
            response = render_to_response("email_exists.html", {})
            transaction.set_rollback(True)
            return response

        subject = render_to_string('emails/email_change_subject.txt', address_context)
        subject = ''.join(subject.splitlines())
        message = render_to_string('emails/confirm_email_change.txt', address_context)
        u_prof = UserProfile.objects.get(user=user)
        meta = u_prof.get_meta()
        if 'old_emails' not in meta:
            meta['old_emails'] = []
        meta['old_emails'].append([user.email, datetime.datetime.now(UTC).isoformat()])
        u_prof.set_meta(meta)
        u_prof.save()
        # Send it to the old email...
        try:
            user.email_user(
                subject,
                message,
                configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL)
            )
        except Exception:  # pylint: disable=broad-except
            log.warning('Unable to send confirmation email to old address', exc_info=True)
            response = render_to_response("email_change_failed.html", {'email': user.email})
            transaction.set_rollback(True)
            return response

        user.email = pec.new_email
        user.save()
        pec.delete()
        # And send it to the new email...
        try:
            user.email_user(
                subject,
                message,
                configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL)
            )
        except Exception:  # pylint: disable=broad-except
            log.warning('Unable to send confirmation email to new address', exc_info=True)
            response = render_to_response("email_change_failed.html", {'email': pec.new_email})
            transaction.set_rollback(True)
            return response

        response = render_to_response("email_change_successful.html", address_context)
        return response


@require_POST
@login_required
@ensure_csrf_cookie
def change_email_settings(request):
    """Modify logged-in user's setting for receiving emails from a course."""
    user = request.user

    course_id = request.POST.get("course_id")
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    receive_emails = request.POST.get("receive_emails")
    if receive_emails:
        optout_object = Optout.objects.filter(user=user, course_id=course_key)
        if optout_object:
            optout_object.delete()
        log.info(
            u"User %s (%s) opted in to receive emails from course %s",
            user.username,
            user.email,
            course_id,
        )
        track.views.server_track(
            request,
            "change-email-settings",
            {"receive_emails": "yes", "course": course_id},
            page='dashboard',
        )
    else:
        Optout.objects.get_or_create(user=user, course_id=course_key)
        log.info(
            u"User %s (%s) opted out of receiving emails from course %s",
            user.username,
            user.email,
            course_id,
        )
        track.views.server_track(
            request,
            "change-email-settings",
            {"receive_emails": "no", "course": course_id},
            page='dashboard',
        )

    return JsonResponse({"success": True})


def _get_course_programs(user, user_enrolled_courses):  # pylint: disable=invalid-name
    """Build a dictionary of program data required for display on the student dashboard.

    Given a user and an iterable of course keys, find all programs relevant to the
    user and return them in a dictionary keyed by course key.

    Arguments:
        user (User): The user to authenticate as when requesting programs.
        user_enrolled_courses (list): List of course keys representing the courses in which
            the given user has active enrollments.

    Returns:
        dict, containing programs keyed by course.
    """
    course_programs = get_programs_for_dashboard(user, user_enrolled_courses)
    programs_data = {}

    for course_key, programs in course_programs.viewitems():
        for program in programs:
            if program.get('status') == 'active' and program.get('category') == 'xseries':
                try:
                    programs_for_course = programs_data.setdefault(course_key, {})
                    programs_for_course.setdefault('course_program_list', []).append({
                        'course_count': len(program['course_codes']),
                        'display_name': program['name'],
                        'program_id': program['id'],
                        'program_marketing_url': urljoin(
                            settings.MKTG_URLS.get('ROOT'),
                            'xseries' + '/{}'
                        ).format(program['marketing_slug'])
                    })
                    programs_for_course['category'] = program.get('category')
                    programs_for_course['display_category'] = get_display_category(program)
                except KeyError:
                    log.warning('Program structure is invalid, skipping display: %r', program)

    return programs_data


class LogoutView(TemplateView):
    """
    Logs out user and redirects.

    The template should load iframes to log the user out of OpenID Connect services.
    See http://openid.net/specs/openid-connect-logout-1_0.html.
    """
    oauth_client_ids = []
    template_name = 'logout.html'

    # Keep track of the page to which the user should ultimately be redirected.
    target = reverse_lazy('cas-logout') if settings.FEATURES.get('AUTH_USE_CAS') else '/'

    def dispatch(self, request, *args, **kwargs):  # pylint: disable=missing-docstring
        # We do not log here, because we have a handler registered to perform logging on successful logouts.
        request.is_from_logout = True

        # Get the list of authorized clients before we clear the session.
        self.oauth_client_ids = request.session.get(edx_oauth2_provider.constants.AUTHORIZED_CLIENTS_SESSION_KEY, [])

        logout(request)

        # If we don't need to deal with OIDC logouts, just redirect the user.
        if LogoutViewConfiguration.current().enabled and self.oauth_client_ids:
            response = super(LogoutView, self).dispatch(request, *args, **kwargs)
        else:
            response = redirect(self.target)

        # Clear the cookie used by the edx.org marketing site
        delete_logged_in_cookies(response)

        return response

    def _build_logout_url(self, url):
        """
        Builds a logout URL with the `no_redirect` query string parameter.

        Args:
            url (str): IDA logout URL

        Returns:
            str
        """
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)
        query_params['no_redirect'] = 1
        new_query_string = urlencode(query_params, doseq=True)
        return urlunsplit((scheme, netloc, path, new_query_string, fragment))

    def get_context_data(self, **kwargs):
        context = super(LogoutView, self).get_context_data(**kwargs)

        # Create a list of URIs that must be called to log the user out of all of the IDAs.
        uris = Client.objects.filter(client_id__in=self.oauth_client_ids,
                                     logout_uri__isnull=False).values_list('logout_uri', flat=True)

        referrer = self.request.META.get('HTTP_REFERER', '').strip('/')
        logout_uris = []

        for uri in uris:
            if not referrer or (referrer and not uri.startswith(referrer)):
                logout_uris.append(self._build_logout_url(uri))

        context.update({
            'target': self.target,
            'logout_uris': logout_uris,
        })

        return context


@login_required
def getUserIdBySocialInfo(request):
    try:
        socialId = request.POST.get("socialId")
        con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                          settings.DATABASES.get('default').get('USER'),
                          settings.DATABASES.get('default').get('PASSWORD'),
                          settings.DATABASES.get('default').get('NAME'),
                          charset='utf8')
        cur = con.cursor()
        query = """
            SELECT uid
              FROM social_auth_usersocialauth
             WHERE id = {0};
        """.format(socialId)
        cur.execute(query)
        uid = cur.fetchone()[0];

        print 'userId = ', uid
        return JsonResponse(
            {
                "success": True,
                "uid": uid,
            },
            status=200
        )
    except Exception as e:
        print e
        return JsonResponse(
            {
                "success": False,
            },
            status=500
        )
    finally:
        cur.close()
        con.close()


@login_required
def deleteOauth2Tokens(request):
    uid = request.POST.get("uid")
    print 'deleteOauth2Tokens userId:', uid
    try:
        con = mdb.connect(settings.DATABASES.get('default').get('HOST'), 'nileprovider', 'nileprovider', 'oauth',
                          charset='utf8')
        cur = con.cursor()
        query = """
            DELETE FROM oauth2_provider_refreshtoken
                  USING oauth2_provider_refreshtoken
                        INNER JOIN auth_user
                           ON oauth2_provider_refreshtoken.user_id = auth_user.id
                  WHERE auth_user.username = '{0}';
                  """.format(uid)
        cur.execute(query)

        print 'query1 >>'
        print query

        con.commit()

        query = """
            DELETE FROM oauth2_provider_accesstoken
                  USING oauth2_provider_accesstoken
                        INNER JOIN auth_user
                           ON oauth2_provider_accesstoken.user_id = auth_user.id
                  WHERE auth_user.username = '{0}';
                  """.format(uid)
        cur.execute(query)
        con.commit()

        print 'query2 >>'
        print query

        return JsonResponse(
            {
                "success": True,
            },
            status=200
        )
    except Exception as e:
        print e
        return JsonResponse(
            {
                "success": False,
            },
            status=500
        )
    finally:
        cur.close()
        con.close()
