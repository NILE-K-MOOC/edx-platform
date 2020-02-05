# -*- coding: utf-8 -*-
"""
Student Views
"""

import datetime
import json
import logging
import uuid
import warnings
from collections import namedtuple

import analytics
import dogstats_wrapper as dog_stats_api
from bulk_email.models import Optout
from courseware.courses import get_courses, sort_by_announcement, sort_by_start_date
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth.views import password_reset_confirm
from django.core import mail
from django.urls import reverse
from django.core.validators import ValidationError, validate_email
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.context_processors import csrf
from django.template.response import TemplateResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import base36_to_int, urlsafe_base64_encode
from django.utils.translation import get_language, ungettext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from eventtracking import tracker
from ipware.ip import get_ip
# Note that this lives in LMS, so this dependency should be refactored.
from notification_prefs.views import enable_notifications
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from pytz import UTC
from requests import HTTPError
from six import text_type, iteritems
from social_core.exceptions import AuthAlreadyAssociated, AuthException
from social_django import utils as social_utils
from xmodule.modulestore.django import modulestore

import openedx.core.djangoapps.external_auth.views
import third_party_auth
import track.views
from course_modes.models import CourseMode
from edxmako.shortcuts import render_to_response, render_to_string
from entitlements.models import CourseEntitlement
from openedx.core.djangoapps import monitoring_utils
from openedx.core.djangoapps.catalog.utils import (
    get_programs_with_type,
)
from openedx.core.djangoapps.embargo import api as embargo_api
from openedx.core.djangoapps.external_auth.login_and_register import register as external_auth_register
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.theming import helpers as theming_helpers
from openedx.core.djangoapps.user_api import accounts as accounts_settings
from openedx.core.djangoapps.user_api.accounts.utils import generate_password
from openedx.core.djangoapps.user_api.models import UserRetirementRequest
from openedx.core.djangoapps.user_api.preferences import api as preferences_api
from openedx.core.djangoapps.user_api.config.waffle import PREVENT_AUTH_USER_WRITES, SYSTEM_MAINTENANCE_MSG, waffle
from openedx.core.djangolib.markup import HTML, Text
from student.cookies import set_logged_in_cookies
from student.forms import AccountCreationForm, PasswordResetFormNoActive, get_registration_extension_form
from student.helpers import (
    DISABLE_UNENROLL_CERT_STATES,
    AccountValidationError,
    auth_pipeline_urls,
    authenticate_new_user,
    cert_info,
    create_or_set_user_attribute_created_on_site,
    destroy_oauth_tokens,
    do_create_account,
    generate_activation_email_context,
    get_next_url_for_login_page
)
from student.models import (
    CourseEnrollment,
    PasswordHistory,
    PendingEmailChange,
    Registration,
    RegistrationCookieConfiguration,
    UserAttribute,
    UserProfile,
    UserSignupSource,
    UserStanding,
    create_comments_service_user,
    email_exists_or_retired,
)
from student.signals import REFUND_ORDER
from student.tasks import send_activation_email
from student.text_me_the_app import TextMeTheAppFragmentView
from third_party_auth import pipeline, provider
from third_party_auth.saml import SAP_SUCCESSFACTORS_SAML_KEY
from util.bad_request_rate_limiter import BadRequestRateLimiter
from util.db import outer_atomic
from util.json_request import JsonResponse
from util.password_policy_validators import SecurityPolicyError, validate_password
import MySQLdb as mdb
from django.db import connections
from random import shuffle
import re
import os
from copy import deepcopy
import time

log = logging.getLogger("edx.student")

AUDIT_LOG = logging.getLogger("audit")
ReverifyInfo = namedtuple(
    'ReverifyInfo',
    'course_id course_name course_number date status display'
)
SETTING_CHANGE_INITIATED = 'edx.user.settings.change_initiated'
# Used as the name of the user attribute for tracking affiliate registrations
REGISTRATION_AFFILIATE_ID = 'registration_affiliate_id'
REGISTRATION_UTM_PARAMETERS = {
    'utm_source': 'registration_utm_source',
    'utm_medium': 'registration_utm_medium',
    'utm_campaign': 'registration_utm_campaign',
    'utm_term': 'registration_utm_term',
    'utm_content': 'registration_utm_content',
}
REGISTRATION_UTM_CREATED_AT = 'registration_utm_created_at'
# used to announce a registration
REGISTER_USER = Signal(providing_args=["user", "registration"])


def csrf_token(context):
    """
    A csrf token that can be included in a form.
    """
    token = context.get('csrf_token', '')
    if token == 'NOTPROVIDED':
        return ''
    return (u'<div style="display:none"><input type="hidden"'
            ' name="csrfmiddlewaretoken" value="{}" /></div>'.format(token))


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

    startDt = startDt.strftime("%Y-%m-%d-%H-%m-%S")
    startDt = startDt.split('-')
    startDt = datetime(int(startDt[0]), int(startDt[1]), int(startDt[2]), int(startDt[3]), int(startDt[4]),
                       int(startDt[5]))

    if endDt != None or endDt == '':
        endDt = endDt.strftime("%Y-%m-%d-%H-%m-%S")
        endDt = endDt.split('-')
        endDt = datetime(int(endDt[0]), int(endDt[1]), int(endDt[2]), int(endDt[3]), int(endDt[4]), int(endDt[5]))

    # making nowDt
    nowDt = datetime.now().strftime("%Y-%m-%d-%H-%m-%S")
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


from bson import ObjectId
from pymongo import MongoClient
from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from courseware.models import CodeDetail


@csrf_exempt
def multisite_index(request, extra_context=None, user=AnonymousUser()):
    context = {}
    if extra_context is None:
        extra_context = {}

    # site_code 획득
    site_code = request.session.get('multisite_org')

    # 기관명 목록
    org_names = CodeDetail.objects.filter(group_code='003', use_yn='Y', delete_yn='N')
    org_dict = {org.detail_code: {'org_kname': org.detail_name, 'org_ename': org.detail_ename} for org in org_names}

    # DEBUG
    print "site_code -> ", site_code

    # multisite - get site code query
    with connections['default'].cursor() as cur:
        query = '''
                SELECT site_id
                FROM   edxapp.multisite
                WHERE  site_code = '{0}'
            '''.format(site_code)
        cur.execute(query)
        rows = cur.fetchall()
    try:
        site_id = rows[0][0]
    except BaseException:
        return redirect('/multisite_error?error=error001')

    if site_id != None:

        course_list = []
        module_store = modulestore()

        with connections['default'].cursor() as cur:
            query = '''
                SELECT 
                    course_id, audit_yn, ribbon_yn, ifnull(teacher_name, '') teacher_name
                FROM
                    (SELECT 
                        a.course_id,
                            c.audit_yn,
                            IFNULL(c.ribbon_yn, 'N') AS ribbon_yn,
                            IFNULL(CASE
                                        WHEN INSTR(c.teacher_name, ',') = 0 THEN c.teacher_name
                                        ELSE CONCAT(SUBSTRING_INDEX(c.teacher_name, ',', 1),
                                                ' 외 ',
                                                LENGTH(c.teacher_name) - LENGTH(REPLACE(c.teacher_name, ',', '')),
                                                '명')
                                    END, '') AS teacher_name,
                            CASE
                                WHEN NOW() BETWEEN ADDDATE(enrollment_start, INTERVAL 9 HOUR) AND ADDDATE(enrollment_end, INTERVAL 9 HOUR) THEN 1
                                WHEN NOW() BETWEEN ADDDATE(start, INTERVAL 9 HOUR) AND ADDDATE(end, INTERVAL 9 HOUR) THEN 2
                                WHEN
                                    ADDDATE(end, INTERVAL 9 HOUR) < NOW()
                                        AND c.audit_yn = 'Y'
                                THEN
                                    3
                                ELSE 4
                            END AS order1,
                            id,
                            org,
                            display_number_with_default,
                            created,
                            display_name,
                            start,
                            end,
                            enrollment_start,
                            enrollment_end
                    FROM
                        multisite_course a
                    JOIN (SELECT 
                        *
                    FROM
                        course_overviews_courseoverview
                    WHERE
                        LOWER(id) NOT LIKE '%demo%'
                            AND LOWER(id) NOT LIKE '%nile%'
                            AND LOWER(id) NOT LIKE '%test%') b ON b.id = a.course_id
                    JOIN course_overview_addinfo c ON a.course_id = c.course_id
                    WHERE 1=1
                        and start < date('2030/01/01') 
                        and site_id = '{site_id}'
                    ORDER BY created DESC) mc
                GROUP BY org , display_number_with_default
                ORDER BY order1 , enrollment_start DESC , start DESC , enrollment_end DESC , end DESC , display_name;
            '''.format(site_id=site_id)

            cur.execute(query)
            result_table = cur.fetchall()

            #print "result_table -> ", result_table
            #print "====================================> 강좌 상태값 연산 시작"

            # catalog_visibility 가 none 이면 출력 대상에서 제외하는 로직이나 현재는 미사용
            client = MongoClient(settings.DATABASES.get('default').get('HOST'), 27017)

            for item in result_table:
                course_lock = 0
                ci = item[0]
                ci = ci.split(':')
                data_ci = ci[1]
                data_ci = data_ci.split('+')
                c_org = data_ci[0]
                c_course = data_ci[1]
                c_name = data_ci[2]

                db = client["edxapp"]
                cursor = db.modulestore.active_versions.find_one({'org': c_org, 'course': c_course, 'run': c_name})
                pb = cursor.get('versions').get('published-branch')
                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)})

                blocks = cursor.get('blocks')
                for block in blocks:
                    if block.get('block_type') and block.get('block_id'):
                        if block.get('block_type') == 'course' and block.get('block_id') == 'course':
                            if block.get('fields').get('catalog_visibility'):
                                if block.get('fields').get('catalog_visibility') == 'none':
                                    course_lock = 1

                if course_lock == 0:
                    multi_course_id = module_store.make_course_key(c_org, c_course, c_name)
                    course_overviews = CourseOverview.objects.get(id=multi_course_id)

                    course_overviews.audit_yn = item[1]
                    course_overviews.ribbon_yn = item[2]
                    course_overviews.teacher_name = item[3]

                    # 강좌별 기관명 추가
                    course_overviews.org_kname = org_dict[course_overviews.org]['org_kname'] \
                        if course_overviews.org in org_dict else course_overviews.display_org_with_default
                    course_overviews.org_ename = org_dict[course_overviews.org]['org_ename'] \
                        if course_overviews.org in org_dict else course_overviews.display_org_with_default

                    course_list.append(course_overviews)

            # 강좌에 상태 값 부여
            for c in course_list:
                status = common_course_status(c.start, c.end)
                c.status = status

            context = {'courses': course_list}

    # multisite popup
    context['popup_list'] = popup_contents(site_code)

    with connections['default'].cursor() as cur:
        query = """
                SELECT max(popup_id) FROM popup;
                """
        cur.execute(query)
        max_pop = cur.fetchone()

    context['max_pop'] = max_pop[0]
    context['popup_base'] = theming_helpers.get_template_path('popup_base.html')
    context['popup_image_base'] = theming_helpers.get_template_path('popup_image_base.html')

    context['homepage_overlay_html'] = configuration_helpers.get_value('homepage_overlay_html')
    context['show_partners'] = configuration_helpers.get_value('show_partners', True)
    context['show_homepage_promo_video'] = configuration_helpers.get_value('show_homepage_promo_video', False)
    context['homepage_course_max'] = configuration_helpers.get_value(
        'HOMEPAGE_COURSE_MAX', settings.HOMEPAGE_COURSE_MAX
    )
    youtube_video_id = configuration_helpers.get_value('homepage_promo_video_youtube_id', "your-youtube-id")
    context['homepage_promo_video_youtube_id'] = youtube_video_id
    context['courses_list'] = theming_helpers.get_template_path('multisite_courses_list.html')
    context.update(extra_context)
    context['programs_list'] = get_programs_with_type(request.site, include_hidden=False)
    return render_to_response('multisite_index.html', context)


# NOTE: This view is not linked to directly--it is called from
# branding/views.py:index(), which is cached for anonymous users.
# This means that it should always return the same thing for anon
# users. (in particular, no switching based on query params allowed)
def index(request, extra_context=None, user=AnonymousUser()):
    """
    Render the edX main page.

    extra_context is used to allow immediate display of certain modal windows, eg signup,
    as used by external_auth.

    ! 수정시 mobile_index도 함께 수정
    """

    start = time.time()

    if extra_context is None:
        extra_context = {}

    user = request.user

    # courses = get_courses(user)
    # filter test ::: filter_={'start__lte': datetime.datetime.now(), 'org':'edX'}
    with connections['default'].cursor() as cur:
        query = '''
            SELECT course_division, course_id
              FROM tb_main_course;
        '''
        cur.execute(query)
        main_course = cur.fetchall()
        new_course = [CourseKey.from_string(course[1]) for course in main_course if course[0] == 'N']
        pop_course = [CourseKey.from_string(course[1]) for course in main_course if course[0] == 'P']
        today_course = [CourseKey.from_string(course[1]) for course in main_course if course[0] == 'T']

    f1 = {'id__in': new_course}
    log.debug('***** def index time check1.1.1 [%s]' % format(time.time() - start, ".6f"))

    f2 = {'id__in': pop_course}
    log.debug('***** def index time check1.1.2 [%s]' % format(time.time() - start, ".6f"))

    f3 = {'id__in': today_course}
    log.debug('***** def index time check1.1.3 [%s]' % format(time.time() - start, ".6f"))

    new_courses = index_courses(user, f1)
    pop_courses = index_courses(user, f2)
    today_courses = index_courses(user, f3)

    log.info(u'len(new_courses) ::: %s', len(new_courses))
    log.info(u'len(pop_courses) ::: %s', len(pop_courses))
    log.info(u'len(today_courses) ::: %s', len(today_courses))

    context = {'new_courses': new_courses, 'pop_courses': pop_courses, 'today_courses': today_courses}

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

    context['popup_base'] = theming_helpers.get_template_path('popup_base.html')
    context['popup_image_base'] = theming_helpers.get_template_path('popup_image_base.html')

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
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
                         SUBSTRING(reg_date, 1, 11) reg_date,
                         section,
                         '',
                         odby
                    FROM tb_board
                   WHERE section = 'N'
                   and use_yn = 'Y'
                   and odby > 0
                ORDER BY odby DESC, reg_date DESC
                   limit 5)
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
                         SUBSTRING(reg_date, 1, 11) reg_date,
                         section,
                         '',
                         odby
                    FROM tb_board
                   WHERE section = 'K'
                   and use_yn = 'Y'
                   and odby > 0
                ORDER BY odby DESC, reg_date DESC
                    limit 5)
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
                         SUBSTRING(reg_date, 1, 11) reg_date,
                         section,
                         '',
                         odby
                    FROM tb_board
                   WHERE section = 'R'
                   and use_yn = 'Y'
                   and odby > 0
                ORDER BY odby DESC, reg_date DESC
                   limit 5)
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
                          WHEN head_title = 'mobile_f ' THEN '[모바일앱]'
                          ELSE ''
                       END
                          head_title,
                         subject,
                         SUBSTRING(reg_date, 1, 11) reg_date,
                         section,
                         head_title,
                         odby
                    FROM tb_board
                   WHERE section = 'F'
                     and use_yn = 'Y'
                     and odby > 0
                ORDER BY odby DESC, reg_date DESC
                   limit 5)
            union all
                (  SELECT board_id,
                         head_title,
                         subject,
                         SUBSTRING(reg_date, 1, 11) reg_date,
                         section,
                         head_title,
                         odby
                    FROM tb_board
                   WHERE section = 'M'
                     and use_yn = 'Y'
                     and odby > 0
                ORDER BY odby DESC, reg_date DESC
                   limit 5)
            ORDER BY odby DESC, reg_date DESC;
        """

    index_list = []
    cur.execute(query)
    row = cur.fetchall()
    if len(row) <= 0:
        with connections['default'].cursor() as cur:
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
                             SUBSTRING(reg_date, 1, 11) reg_date,
                             section,
                             '',
                             odby
                        FROM tb_board
                       WHERE section = 'N'
                       and use_yn = 'Y'
                    ORDER BY odby DESC, reg_date DESC
                       limit 5)
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
                             SUBSTRING(reg_date, 1, 11) reg_date,
                             section,
                             '',
                             odby
                        FROM tb_board
                       WHERE section = 'K'
                       and use_yn = 'Y'
                    ORDER BY odby DESC, reg_date DESC
                        limit 5)
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
                             SUBSTRING(reg_date, 1, 11) reg_date,
                             section,
                             '',
                             odby
                        FROM tb_board
                       WHERE section = 'R'
                       and use_yn = 'Y'
                    ORDER BY odby DESC, reg_date DESC
                       limit 5)
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
                              WHEN head_title = 'mobile_f ' THEN '[모바일앱]'
                              ELSE ''
                           END
                              head_title,
                             subject,
                             SUBSTRING(reg_date, 1, 11) reg_date,
                             section,
                             head_title,
                             odby
                        FROM tb_board
                       WHERE section = 'F'
                         and use_yn = 'Y'
                    ORDER BY odby DESC, reg_date DESC
                       limit 5)
                union all
                    (  SELECT board_id,
                             '' head_title,
                             subject,
                             SUBSTRING(reg_date, 1, 11) reg_date,
                             section,
                             head_title,
                             odby
                        FROM tb_board
                       WHERE section = 'M'
                         and use_yn = 'Y'
                    ORDER BY odby DESC, reg_date DESC
                       limit 5)
                ORDER BY odby DESC, reg_date DESC;
                    """
            cur.execute(query)
            row = cur.fetchall()

    comm_section = {
        'N': '공지사항 더보기',
        'K': 'K-MOOC 뉴스 더보기',
        'R': '자료실 더보기',
        'F': 'FAQ 더보기',
        'M': '모바일 더보기'
    }

    for i in row:
        comm_dict = dict()
        comm_dict['board_id'] = i[0]
        comm_dict['head_title'] = i[1]
        comm_dict['subject'] = i[2]
        comm_dict['section'] = i[4]
        comm_dict['faq_section'] = i[5]
        comm_dict['category'] = comm_section[i[4]]

        index_list.append(comm_dict)

    context['index_list'] = index_list

    cur = con.cursor()
    query = """
            SELECT max(popup_id) FROM popup;
            """
    cur.execute(query)
    max_pop = cur.fetchall()
    cur.close()

    # popup zone s --------------------------------------------------
    popupzone_query = """
              SELECT seq,
                     title,
                     ifnull(save_path, '')
                        image_file,
                     link_url,
                     link_target
                FROM popupzone a LEFT JOIN tb_attach b ON a.image_file = b.id
               WHERE date_format(adddate(now(), INTERVAL 9 HOUR), '%Y%m%d%H:%i') 
                   BETWEEN concat(start_date, ifnull(start_time,'00:00'))
                    AND concat(end_date, ifnull(end_time, '00:00'))
            ORDER BY end_date ASC, start_date ASC;
        """
    cur = con.cursor()
    cur.execute(popupzone_query)
    popzone = cur.fetchall()

    popzone_list = list()
    for idx, zone in enumerate(popzone):
        popzone_dict = dict()
        popzone_dict['title'] = zone[1]
        image_idx = zone[2].find('/static')
        if image_idx == -1:
            popzone_dict['image_file'] = '/static/images/blank.png'
        else:
            popzone_dict['image_file'] = zone[2][image_idx:]
        popzone_dict['link_url'] = zone[3]
        popzone_dict['link_target'] = zone[4]

        popzone_list.append(popzone_dict)

    # popup zone e ----------------------------------------------------

    context['popup_list'] = popup_contents()
    context['index_submenu'] = index_submenu()
    # Insert additional context for use in the template
    context.update(extra_context)
    extra_context['max_pop'] = str(max_pop[0][0])
    extra_context['popzone_list'] = popzone_list
    context.update(extra_context)

    limit_length = 140 if request.LANGUAGE_CODE == 'ko-kr' else 110

    with connections['default'].cursor() as cur:
        query = '''
              SELECT detail_code, {d_name}
                FROM code_detail a
                     JOIN course_overview_addinfo b ON a.detail_code = b.middle_classfy
                     JOIN course_overviews_courseoverview c ON b.course_id = c.id
               WHERE     group_code = '002'
                     AND c.catalog_visibility = 'both'
                     AND adddate(c.enrollment_start, INTERVAL 9 HOUR) <= now()
            GROUP BY middle_classfy
            ORDER BY order_no;
        '''.format(d_name='detail_name' if request.LANGUAGE_CODE == 'ko-kr' else 'detail_Ename')
        cur.execute(query)
        m_classfy_list = list(cur.fetchall())
        random_classfy = deepcopy(m_classfy_list)

        shuffle(random_classfy)
        len_check = ''
        for sh_idx, s_classfy in enumerate(random_classfy):
            if len(len_check + str(s_classfy[1])) <= limit_length:
                len_check += str(s_classfy[1])
            else:
                break
        tmp = set([shu[0] for shu in random_classfy[:sh_idx]])
        middle_list = [mid for mid in m_classfy_list if mid[0] not in tmp]
        context['middle_list'] = middle_list
        context['random_classfy'] = random_classfy[:sh_idx]
    return render_to_response('index.html', context)


# index submenu 2개 조회
def index_submenu():
    with connections['default'].cursor() as cur:
        query = '''
              SELECT ifnull(detail_name, 'K-MOOC소개'), ifnull(detail_desc, '/about')
                FROM code_detail
               WHERE group_code = '040' AND use_yn = 'Y' AND delete_yn = 'N'
            ORDER BY order_no
               LIMIT 2;
        '''
        cur.execute(query)
        m_data = cur.fetchall()
        m_dict = dict()
        m_dict['subm_title_1'] = m_data[0][0]
        m_dict['subm_link_1'] = m_data[0][1]
        m_dict['subm_title_2'] = m_data[1][0]
        m_dict['subm_link_2'] = m_data[1][1]
    return m_dict


def index_courses(user, filter_=None):
    courses = get_courses(user, filter_=filter_)

    # 랜덤 출력을위해 shuffle 사용
    shuffle(courses)

    # audit_yn 값이 없으면 html 랜더시 오류, courses
    # audit_yn 값이 없는 강좌만 조회시 courses 가 None 이면 iterator 오류이므로 기본값을 셋팅
    for c in courses:
        if not hasattr(c, 'audit_yn'):
            c.audit_yn = 'N'

    return courses


def popup_contents(site_code=None):
    with connections['default'].cursor() as cur:
        multi_query = """
            JOIN multisite c
            ON a.site_id = c.site_id
            AND site_code = "{site_code}"
            AND c.delete_yn = "N"
        """.format(site_code=site_code) if site_code is not None else ''

        query = '''
            SELECT popup_id,
                   popup_type,
                   link_type,
                   title,
                   contents,
                   save_path,
                   ifnull(link_url, '#') link_url,
                   link_target,
                   width,
                   height,
                   hidden_day,
                   a.site_id
              FROM popup a LEFT JOIN tb_attach b ON a.image_file = b.id AND b.use_yn = 1
              {multi_query}
             WHERE     a.use_yn = 'Y'
                   AND a.delete_yn != 'Y'
                   AND date_format(adddate(now(), INTERVAL 9 HOUR), '%Y%m%d%H:%i') 
                   BETWEEN concat(start_date, ifnull(start_time,'00:00'))
                    AND concat(end_date, ifnull(end_time, '00:00')) ;
        '''.format(multi_query=multi_query)
        cur.execute(query)
        pop_data = cur.fetchall()
        pop_list = list()
        for pop in pop_data:
            pop_dict = dict()
            pop_dict['pop_id'] = pop[0]
            pop_dict['popup_type'] = pop[1]
            pop_dict['link_type'] = pop[2]
            pop_dict['pop_title'] = pop[3]
            pop_dict['pop_contents'] = pop[4]
            pop_dict['img_path'] = pop[5]
            pop_dict['link_url'] = pop[6] if pop[6] != '' else '#'
            pop_dict['link_target'] = '_blank' if pop[7] == 'B' else '_self'
            pop_dict['pop_width'] = pop[8]
            pop_dict['pop_height'] = pop[9]
            pop_dict['pop_hidden_day'] = [pop[10], pop[10] + '일간 열지 않음' if pop[10] != '0' else '다시는 열지 않음']
            pop_dict['site_id'] = pop[11]

            pop_list.append(pop_dict)
    return pop_list


@ensure_csrf_cookie
def register_user(request, extra_context=None):
    """
    Deprecated. To be replaced by :class:`student_account.views.login_and_registration_form`.
    """
    # Determine the URL to redirect to following login:
    redirect_to = get_next_url_for_login_page(request)
    if request.user.is_authenticated:
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

    if context.get("extauth_domain", '').startswith(
            openedx.core.djangoapps.external_auth.views.SHIBBOLETH_DOMAIN_PREFIX
    ):
        print 'here is register-shib'
        return render_to_response('register-shib.html', context)

    # If third-party auth is enabled, prepopulate the form with data from the
    # selected provider.
    if third_party_auth.is_enabled() and pipeline.running(request):
        print 'here is third_party_auth'
        running_pipeline = pipeline.get(request)
        current_provider = provider.Registry.get_from_pipeline(running_pipeline)
        if current_provider is not None:
            overrides = current_provider.get_register_form_data(running_pipeline.get('kwargs'))
            overrides['running_pipeline'] = running_pipeline
            overrides['selected_provider'] = current_provider.name
            context.update(overrides)
    print 'here is register'
    return render_to_response('register.html', context)


def compose_and_send_activation_email(user, profile, user_registration=None):
    """
    Construct all the required params and send the activation email
    through celery task

    Arguments:
        user: current logged-in user
        profile: profile object of the current logged-in user
        user_registration: registration of the current logged-in user
    """
    dest_addr = user.email
    if user_registration is None:
        user_registration = Registration.objects.get(user=user)
    context = generate_activation_email_context(user, user_registration)
    subject = render_to_string('emails/activation_email_subject.txt', context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message_for_activation = render_to_string('emails/activation_email.txt', context)
    from_address = configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL)
    from_address = configuration_helpers.get_value('ACTIVATION_EMAIL_FROM_ADDRESS', from_address)
    if settings.FEATURES.get('REROUTE_ACTIVATION_EMAIL'):
        dest_addr = settings.FEATURES['REROUTE_ACTIVATION_EMAIL']
        message_for_activation = ("Activation for %s (%s): %s\n" % (user, user.email, profile.name) +
                                  '-' * 80 + '\n\n' + message_for_activation)
    send_activation_email.delay(subject, message_for_activation, from_address, dest_addr)


@login_required
def course_run_refund_status(request, course_id):
    """
    Get Refundable status for a course.

    Arguments:
        request: The request object.
        course_id (str): The unique identifier for the course.

    Returns:
        Json response.

    """

    try:
        course_key = CourseKey.from_string(course_id)
        course_enrollment = CourseEnrollment.get_enrollment(request.user, course_key)

    except InvalidKeyError:
        logging.exception("The course key used to get refund status caused InvalidKeyError during look up.")

        return JsonResponse({'course_refundable_status': ''}, status=406)

    refundable_status = course_enrollment.refundable()
    logging.info("Course refund status for course {0} is {1}".format(course_id, refundable_status))

    return JsonResponse({'course_refundable_status': refundable_status}, status=200)


def _update_email_opt_in(request, org):
    """
    Helper function used to hit the profile API if email opt-in is enabled.
    """

    email_opt_in = request.POST.get('email_opt_in')
    if email_opt_in is not None:
        email_opt_in_boolean = email_opt_in == 'true'
        preferences_api.update_email_opt_in(request.user, org, email_opt_in_boolean)


@transaction.non_atomic_requests
@require_POST
@outer_atomic(read_committed=True)
def enrollment_verifi(request):
    course_id = request.POST.get('course_id')
    user_id = request.POST.get('user_id')

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')

    cur = con.cursor()
    query = """
            INSERT INTO student_courseenrollment(user_id,
                                                 course_id,
                                                 created,
                                                 is_active,
                                                 mode)
                 VALUES ('{0}',
                         '{1}',
                         now(),
                         TRUE,
                         'audit')
       """.format(user_id, course_id)
    cur.execute(query)
    con.commit()

    return HttpResponse()


@transaction.non_atomic_requests
@require_POST
@outer_atomic(read_committed=True)
def change_enrollment(request, check_access=True):
    """
    Modify the enrollment status for the logged-in user.

    TODO: This is lms specific and does not belong in common code.

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
    if not user.is_authenticated:
        return HttpResponseForbidden()

    # Ensure we received a course_id
    action = request.POST.get("enrollment_action")
    if 'course_id' not in request.POST:
        return HttpResponseBadRequest(_("Course id not specified"))

    try:
        course_id = CourseKey.from_string(request.POST.get("course_id"))
    except InvalidKeyError:
        log.warning(
            u"User %s tried to %s with invalid course id: %s",
            user.username,
            action,
            request.POST.get("course_id"),
        )
        return HttpResponseBadRequest(_("Invalid course id"))

    # Allow us to monitor performance of this transaction on a per-course basis since we often roll-out features
    # on a per-course basis.
    monitoring_utils.set_custom_metric('course_id', text_type(course_id))

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

        if CourseEntitlement.check_for_existing_entitlement_and_enroll(user=user, course_run_key=course_id):
            return HttpResponse(reverse('courseware', args=[unicode(course_id)]))

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
                    CourseEnrollment.enroll(user, course_id, check_access=check_access, mode=enroll_mode)
            except Exception:  # pylint: disable=broad-except
                return HttpResponseBadRequest(_("Could not enroll"))

        # If we have more than one course mode or professional ed is enabled,
        # then send the user to the choose your track page.
        # (In the case of no-id-professional/professional ed, this will redirect to a page that
        # funnels users directly into the verification / payment flow)
        if CourseMode.has_verified_mode(available_modes) or CourseMode.has_professional_mode(available_modes):
            return HttpResponse(
                reverse("course_modes_choose", kwargs={'course_id': text_type(course_id)})
            )

        # Otherwise, there is only one mode available (the default)
        return HttpResponse()
    elif action == "unenroll":
        enrollment = CourseEnrollment.get_enrollment(user, course_id)
        if not enrollment:
            return HttpResponseBadRequest(_("You are not enrolled in this course"))

        certificate_info = cert_info(user, enrollment.course_overview)
        if certificate_info.get('status') in DISABLE_UNENROLL_CERT_STATES:
            return HttpResponseBadRequest(_("Your certificate prevents you from unenrolling from this course"))

        CourseEnrollment.unenroll(user, course_id)
        REFUND_ORDER.send(sender=None, course_enrollment=enrollment)
        return HttpResponse()
    else:
        return HttpResponseBadRequest(_("Enrollment action is invalid"))


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
    """
    JSON call to change a profile setting: Right now, location
    """
    # TODO (vshnayder): location is no longer used
    u_prof = UserProfile.objects.get(user=request.user)  # request.user.profile_cache
    if 'location' in request.POST:
        u_prof.location = request.POST['location']
    u_prof.save()

    return JsonResponse({
        "success": True,
        "location": u_prof.location,
    })


@receiver(post_save, sender=User)
def user_signup_handler(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Handler that saves the user Signup Source when the user is created
    """
    if 'created' in kwargs and kwargs['created']:
        site = configuration_helpers.get_value('SITE_NAME')
        if site:
            user_signup_source = UserSignupSource(user=kwargs['instance'], site=site)
            user_signup_source.save()
            log.info(u'user {} originated from a white labeled "Microsite"'.format(kwargs['instance'].id))


@transaction.non_atomic_requests
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
    * It is non-transactional except where explicitly wrapped in atomic to
      alleviate deadlocks and improve performance. This means failures at
      different places in registration can leave users in inconsistent
      states.
    * Third-party auth passwords are not verified. There is a comment that
      they are unused, but it would be helpful to have a sanity check that
      they are sane.
    * The user-facing text is rather unfriendly (e.g. "Username must be a
      minimum of two characters long" rather than "Please use a username of
      at least two characters").
    * Duplicate email raises a ValidationError (rather than the expected
      AccountValidationError). Duplicate username returns an inconsistent
      user message (i.e. "An account with the Public Username '{username}'
      already exists." rather than "It looks like {username} belongs to an
      existing account. Try again with a different username.") The two checks
      occur at different places in the code; as a result, registering with
      both a duplicate username and email raises only a ValidationError for
      email only.
    """
    # Copy params so we can modify it; we can't just do dict(params) because if
    # params is request.POST, that results in a dict containing lists of values
    params = dict(params.items())

    # allow to define custom set of required/optional/hidden fields via configuration
    extra_fields = configuration_helpers.get_value(
        'REGISTRATION_EXTRA_FIELDS',
        getattr(settings, 'REGISTRATION_EXTRA_FIELDS', {})
    )
    # registration via third party (Google, Facebook) using mobile application
    # doesn't use social auth pipeline (no redirect uri(s) etc involved).
    # In this case all related info (required for account linking)
    # is sent in params.
    # `third_party_auth_credentials_in_api` essentially means 'request
    # is made from mobile application'
    third_party_auth_credentials_in_api = 'provider' in params

    is_third_party_auth_enabled = third_party_auth.is_enabled()

    # pipeline 에서 비밀번호를 파라미터로 쓰는 내용을 하드 코딩필요
    # params 에 password2 가 있다면 있는 내용을 사용함

    if is_third_party_auth_enabled and (pipeline.running(request) or third_party_auth_credentials_in_api) and ('password2' not in params or params['password2'] == ''):
        params["password"] = generate_password()

    # in case user is registering via third party (Google, Facebook) and pipeline has expired, show appropriate
    # error message
    if is_third_party_auth_enabled and ('social_auth_provider' in params and not pipeline.running(request)):
        raise ValidationError(
            {'session_expired': [
                _(u"Registration using {provider} has timed out.").format(
                    provider=params.get('social_auth_provider'))
            ]}
        )

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
        if len(eamap.external_name.strip()) >= accounts_settings.NAME_MIN_LENGTH:
            params["name"] = eamap.external_name
        params["password"] = eamap.internal_password
        log.debug(u'In create_account with external_auth: user = %s, email=%s', params["name"], params["email"])

    extended_profile_fields = configuration_helpers.get_value('extended_profile_fields', [])
    enforce_password_policy = not do_external_auth
    # Can't have terms of service for certain SHIB users, like at Stanford
    registration_fields = getattr(settings, 'REGISTRATION_EXTRA_FIELDS', {})
    tos_required = (
                           registration_fields.get('terms_of_service') != 'hidden' or
                           registration_fields.get('honor_code') != 'hidden'
                   ) and (
                           not settings.FEATURES.get("AUTH_USE_SHIB") or
                           not settings.FEATURES.get("SHIB_DISABLE_TOS") or
                           not do_external_auth or
                           not eamap.external_domain.startswith(openedx.core.djangoapps.external_auth.views.SHIBBOLETH_DOMAIN_PREFIX)
                   )

    form = AccountCreationForm(
        data=params,
        extra_fields=extra_fields,
        extended_profile_fields=extended_profile_fields,
        enforce_password_policy=enforce_password_policy,
        tos_required=tos_required,
    )
    custom_form = get_registration_extension_form(data=params)

    third_party_provider = None
    running_pipeline = None
    new_user = None

    # Perform operations within a transaction that are critical to account creation
    with outer_atomic(read_committed=True):
        # first, create the account
        (user, profile, registration) = do_create_account(form, custom_form)

        # If a 3rd party auth provider and credentials were provided in the API, link the account with social auth
        # (If the user is using the normal register page, the social auth pipeline does the linking, not this code)

        # Note: this is orthogonal to the 3rd party authentication pipeline that occurs
        # when the account is created via the browser and redirect URLs.

        if is_third_party_auth_enabled and third_party_auth_credentials_in_api:
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
                request.social_strategy.clean_partial_pipeline(social_access_token)
                raise ValidationError({'access_token': [error_message]})

        # If the user is registering via 3rd party auth, track which provider they use
        if is_third_party_auth_enabled and pipeline.running(request):
            running_pipeline = pipeline.get(request)
            third_party_provider = provider.Registry.get_from_pipeline(running_pipeline)

        new_user = authenticate_new_user(request, user.username, params['password'])
        django_login(request, new_user)
        request.session.set_expiry(0)

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
                AUDIT_LOG.info(
                    u"Login activated on extauth account - {0} ({1})".format(new_user.username, new_user.email))

    # Check if system is configured to skip activation email for the current user.
    skip_email = skip_activation_email(
        user, do_external_auth, running_pipeline, third_party_provider,
    )

    if skip_email:
        registration.activate()
    else:
        compose_and_send_activation_email(user, profile, registration)

    # Perform operations that are non-critical parts of account creation
    create_or_set_user_attribute_created_on_site(user, request.site)

    preferences_api.set_user_preference(user, LANGUAGE_KEY, get_language())

    if settings.FEATURES.get('ENABLE_DISCUSSION_EMAIL_DIGEST'):
        try:
            enable_notifications(user)
        except Exception:  # pylint: disable=broad-except
            log.exception("Enable discussion notifications failed for user {id}.".format(id=user.id))

    dog_stats_api.increment("common.student.account_created")

    # Track the user's registration
    if hasattr(settings, 'LMS_SEGMENT_KEY') and settings.LMS_SEGMENT_KEY:
        tracking_context = tracker.get_tracker().resolve_context()
        identity_args = [
            user.id,
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
                'country': text_type(profile.country),
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
    REGISTER_USER.send(sender=None, user=user, registration=registration)

    create_comments_service_user(user)

    try:
        record_registration_attributions(request, new_user)
    # Don't prevent a user from registering due to attribution errors.
    except Exception:  # pylint: disable=broad-except
        log.exception('Error while attributing cookies to user registration.')

    # TODO: there is no error checking here to see that the user actually logged in successfully,
    # and is not yet an active user.
    if new_user is not None:
        AUDIT_LOG.info(u"Login success on new account creation - {0}".format(new_user.username))

    return new_user


def skip_activation_email(user, do_external_auth, running_pipeline, third_party_provider):
    """
    Return `True` if activation email should be skipped.

    Skip email if we are:
        1. Doing load testing.
        2. Random user generation for other forms of testing.
        3. External auth bypassing activation.
        4. Have the platform configured to not require e-mail activation.
        5. Registering a new user using a trusted third party provider (with skip_email_verification=True)

    Note that this feature is only tested as a flag set one way or
    the other for *new* systems. we need to be careful about
    changing settings on a running system to make sure no users are
    left in an inconsistent state (or doing a migration if they are).

    Arguments:
        user (User): Django User object for the current user.
        do_external_auth (bool): True if external authentication is in progress.
        running_pipeline (dict): Dictionary containing user and pipeline data for third party authentication.
        third_party_provider (ProviderConfig): An instance of third party provider configuration.

    Returns:
        (bool): `True` if account activation email should be skipped, `False` if account activation email should be
            sent.
    """
    sso_pipeline_email = running_pipeline and running_pipeline['kwargs'].get('details', {}).get('email')

    # Email is valid if the SAML assertion email matches the user account email or
    # no email was provided in the SAML assertion. Some IdP's use a callback
    # to retrieve additional user account information (including email) after the
    # initial account creation.
    valid_email = (
            sso_pipeline_email == user.email or (
            sso_pipeline_email is None and
            third_party_provider and
            getattr(third_party_provider, "identity_provider_type", None) == SAP_SUCCESSFACTORS_SAML_KEY
    )
    )

    # log the cases where skip activation email flag is set, but email validity check fails
    if third_party_provider and third_party_provider.skip_email_verification and not valid_email:
        log.info(
            '[skip_email_verification=True][user=%s][pipeline-email=%s][identity_provider=%s][provider_type=%s] '
            'Account activation email sent as user\'s system email differs from SSO email.',
            user.email,
            sso_pipeline_email,
            getattr(third_party_provider, "provider_id", None),
            getattr(third_party_provider, "identity_provider_type", None)
        )

    return (
            settings.FEATURES.get('SKIP_EMAIL_VALIDATION', None) or
            settings.FEATURES.get('AUTOMATIC_AUTH_FOR_TESTING') or
            (settings.FEATURES.get('BYPASS_ACTIVATION_EMAIL_FOR_EXTAUTH') and do_external_auth) or
            (third_party_provider and third_party_provider.skip_email_verification and valid_email)
    )


def record_affiliate_registration_attribution(request, user):
    """
    Attribute this user's registration to the referring affiliate, if
    applicable.
    """
    affiliate_id = request.COOKIES.get(settings.AFFILIATE_COOKIE_NAME)
    if user and affiliate_id:
        UserAttribute.set_user_attribute(user, REGISTRATION_AFFILIATE_ID, affiliate_id)


def record_utm_registration_attribution(request, user):
    """
    Attribute this user's registration to the latest UTM referrer, if
    applicable.
    """
    utm_cookie_name = RegistrationCookieConfiguration.current().utm_cookie_name
    utm_cookie = request.COOKIES.get(utm_cookie_name)
    if user and utm_cookie:
        utm = json.loads(utm_cookie)
        for utm_parameter_name in REGISTRATION_UTM_PARAMETERS:
            utm_parameter = utm.get(utm_parameter_name)
            if utm_parameter:
                UserAttribute.set_user_attribute(
                    user,
                    REGISTRATION_UTM_PARAMETERS.get(utm_parameter_name),
                    utm_parameter
                )
        created_at_unixtime = utm.get('created_at')
        if created_at_unixtime:
            # We divide by 1000 here because the javascript timestamp generated is in milliseconds not seconds.
            # PYTHON: time.time()      => 1475590280.823698
            # JS: new Date().getTime() => 1475590280823
            created_at_datetime = datetime.datetime.fromtimestamp(int(created_at_unixtime) / float(1000), tz=UTC)
            UserAttribute.set_user_attribute(
                user,
                REGISTRATION_UTM_CREATED_AT,
                created_at_datetime
            )


def record_registration_attributions(request, user):
    """
    Attribute this user's registration based on referrer cookies.
    """
    record_affiliate_registration_attribution(request, user)
    record_utm_registration_attribution(request, user)


@csrf_exempt
@transaction.non_atomic_requests
def create_account(request, post_override=None):
    """
    JSON call to create new edX account.
    Used by form in signup_modal.html, which is included into header.html
    """
    # Check if ALLOW_PUBLIC_ACCOUNT_CREATION flag turned off to restrict user account creation
    if not configuration_helpers.get_value(
            'ALLOW_PUBLIC_ACCOUNT_CREATION',
            settings.FEATURES.get('ALLOW_PUBLIC_ACCOUNT_CREATION', True)
    ):
        return HttpResponseForbidden(_("Account creation not allowed."))

    if waffle().is_enabled(PREVENT_AUTH_USER_WRITES):
        return HttpResponseForbidden(SYSTEM_MAINTENANCE_MSG)

    warnings.warn("Please use RegistrationView instead.", DeprecationWarning)

    try:
        user = create_account_with_params(request, post_override or request.POST)
    except AccountValidationError as exc:
        return JsonResponse({'success': False, 'value': text_type(exc), 'field': exc.field}, status=400)
    except ValidationError as exc:
        field, error_list = next(iteritems(exc.message_dict))
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


@ensure_csrf_cookie
def activate_account(request, key):
    """
    When link in activation e-mail is clicked
    """
    # If request is in Studio call the appropriate view
    if theming_helpers.get_project_root_name().lower() == u'cms':
        return activate_account_studio(request, key)

    try:
        registration = Registration.objects.get(activation_key=key)
    except (Registration.DoesNotExist, Registration.MultipleObjectsReturned):
        messages.error(
            request,
            HTML(_(
                '{html_start}Your account could not be activated{html_end}'
                'Something went wrong, please <a href="{support_url}">contact support</a> to resolve this issue.'
            )).format(
                support_url=configuration_helpers.get_value('SUPPORT_SITE_LINK', settings.SUPPORT_SITE_LINK),
                html_start=HTML('<p class="message-title">'),
                html_end=HTML('</p>'),
            ),
            extra_tags='account-activation aa-icon'
        )
    else:
        if registration.user.is_active:
            messages.info(
                request,
                HTML(_('{html_start}This account has already been activated.{html_end}')).format(
                    html_start=HTML('<p class="message-title">'),
                    html_end=HTML('</p>'),
                ),
                extra_tags='account-activation aa-icon',
            )
        elif waffle().is_enabled(PREVENT_AUTH_USER_WRITES):
            messages.error(
                request,
                HTML(u'{html_start}{message}{html_end}').format(
                    message=Text(SYSTEM_MAINTENANCE_MSG),
                    html_start=HTML('<p class="message-title">'),
                    html_end=HTML('</p>'),
                ),
                extra_tags='account-activation aa-icon',
            )
        else:
            registration.activate()
            # Success message for logged in users.
            message = _('{html_start}Success{html_end} You have activated your account.')

            if not request.user.is_authenticated:
                # Success message for logged out users
                message = _(
                    '{html_start}Success! You have activated your account.{html_end}'
                    'You will now receive email updates and alerts from us related to'
                    ' the courses you are enrolled in. Sign In to continue.'
                )

            # Add message for later use.
            messages.success(
                request,
                HTML(message).format(
                    html_start=HTML('<p class="message-title">'),
                    html_end=HTML('</p>'),
                ),
                extra_tags='account-activation aa-icon',
            )

    return redirect('dashboard')


@ensure_csrf_cookie
def activate_account_studio(request, key):
    """
    When link in activation e-mail is clicked and the link belongs to studio.
    """
    try:
        registration = Registration.objects.get(activation_key=key)
    except (Registration.DoesNotExist, Registration.MultipleObjectsReturned):
        return render_to_response(
            "registration/activation_invalid.html",
            {'csrf': csrf(request)['csrf_token']}
        )
    else:
        user_logged_in = request.user.is_authenticated
        already_active = True
        if not registration.user.is_active:
            if waffle().is_enabled(PREVENT_AUTH_USER_WRITES):
                return render_to_response('registration/activation_invalid.html',
                                          {'csrf': csrf(request)['csrf_token']})
            registration.activate()
            already_active = False

        return render_to_response(
            "registration/activation_complete.html",
            {
                'user_logged_in': user_logged_in,
                'already_active': already_active
            }
        )


@csrf_exempt
@require_POST
def password_reset(request):
    """
    Attempts to send a password reset e-mail.
    """
    # Add some rate limiting here by re-using the RateLimitMixin as a helper class
    limiter = BadRequestRateLimiter()
    if limiter.is_rate_limit_exceeded(request):
        AUDIT_LOG.warning("Rate limit exceeded in password_reset")
        return HttpResponseForbidden()

    form = PasswordResetFormNoActive(request.POST)
    if form.is_valid():
        form.save(use_https=request.is_secure(),
                  from_email=configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL),
                  request=request)
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
        destroy_oauth_tokens(request.user)
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

    if UserRetirementRequest.has_user_requested_retirement(user):
        # Refuse to reset the password of any user that has requested retirement.
        context = {
            'validlink': True,
            'form': None,
            'title': _('Password reset unsuccessful'),
            'err_msg': _('Error in resetting your password.'),
        }
        context.update(platform_name)
        return TemplateResponse(
            request, 'registration/password_reset_confirm.html', context
        )

    if waffle().is_enabled(PREVENT_AUTH_USER_WRITES):
        context = {
            'validlink': False,
            'form': None,
            'title': _('Password reset unsuccessful'),
            'err_msg': SYSTEM_MAINTENANCE_MSG,
        }
        context.update(platform_name)
        return TemplateResponse(
            request, 'registration/password_reset_confirm.html', context
        )

    if request.method == 'POST':
        password = request.POST['new_password1']

        try:
            validate_password(password, user=user)
        except ValidationError as err:
            # We have a password reset attempt which violates some security
            # policy, or any other validation. Use the existing Django template to communicate that
            # back to the user.
            context = {
                'validlink': True,
                'form': None,
                'title': _('Password reset unsuccessful'),
                'err_msg': err.message,
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

        # If password reset was unsuccessful a template response is returned (status_code 200).
        # Check if form is invalid then show an error to the user.
        # Note if password reset was successful we get response redirect (status_code 302).
        if response.status_code == 200:
            form_valid = response.context_data['form'].is_valid() if response.context_data['form'] else False
            if not form_valid:
                log.warning(
                    u'Unable to reset password for user [%s] because form is not valid. '
                    u'A possible cause is that the user had an invalid reset token',
                    user.username,
                )
                response.context_data['err_msg'] = _('Error in resetting your password. Please try again.')
                return response

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

    if email_exists_or_retired(new_email):
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
    except Exception:
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
    if waffle().is_enabled(PREVENT_AUTH_USER_WRITES):
        return render_to_response('email_change_failed.html', {'err_msg': SYSTEM_MAINTENANCE_MSG})

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
    """
    Modify logged-in user's setting for receiving emails from a course.
    """
    user = request.user

    course_id = request.POST.get("course_id")
    course_key = CourseKey.from_string(course_id)
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


@ensure_csrf_cookie
def text_me_the_app(request):
    """
    Text me the app view.
    """
    text_me_fragment = TextMeTheAppFragmentView().render_to_fragment(request)
    context = {
        'nav_hidden': True,
        'show_dashboard_tabs': True,
        'show_program_listing': ProgramsApiConfig.is_enabled(),
        'fragment': text_me_fragment
    }

    return render_to_response('text-me-the-app.html', context)


@csrf_exempt
def guide_download(request):
    """
    guide_flag
        1: K-MOOC 학습인정시간 기준(`18.9.개정).pdf(저장 파일명: total_study_time.pdf)
        2: 2018 강좌안내서 국문.pdf(저장 파일명: guide_ko.pdf)
        3: 2018 강좌안내서 영문.pdf(저장 파일명: guide_en.pdf)
    """
    guide_flag = request.GET.get('guide') if request.GET.get('guide') else ''

    if guide_flag == '1':
        file_name = 'total_study_time.pdf'
        down_name = 'K-MOOC 학습인정시간 기준(`18.9.개정).pdf'
    elif guide_flag == '2':
        file_name = '2018_guide_ko.pdf'
        down_name = '2018 강좌안내서 국문.pdf'
    else:
        file_name = '2018_guide_en.pdf'
        down_name = '2018 강좌안내서 영문.pdf'

    if os.path.exists('/edx/var/edxapp/staticfiles/file_upload/' + file_name):
        response = HttpResponse(open('/edx/var/edxapp/staticfiles/file_upload/' + file_name, 'rb'), content_type='application/force-download')

        response['Content-Disposition'] = 'attachment; filename=%s' % str(down_name)
        return response
    else:
        raise IOError(down_name + '파일을 찾을 수 없습니다.')
