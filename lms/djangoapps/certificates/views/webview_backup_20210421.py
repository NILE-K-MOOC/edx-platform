# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
"""
Certificate HTML webview.
"""
import logging
import urllib
import json
import MySQLdb as mdb
import pytz
from pytz import timezone, utc
import urllib2
import commands
from datetime import datetime
from dateutil import tz
from uuid import uuid4
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.utils.encoding import smart_str
from django.utils import translation
from eventtracking import tracker
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from badges.events.course_complete import get_completion_badge
from badges.utils import badges_enabled
from lms.djangoapps.certificates.api import (
    emit_certificate_event,
    get_active_web_certificate,
    get_certificate_footer_context,
    get_certificate_header_context,
    get_certificate_template,
    get_certificate_url
)
from lms.djangoapps.certificates.models import (
    CertificateGenerationCourseSetting,
    CertificateHtmlViewConfiguration,
    CertificateSocialNetworks,
    CertificateStatuses,
    GeneratedCertificate
)
from courseware.access import has_access
from courseware.courses import get_course_by_id
from edxmako.shortcuts import render_to_response
from edxmako.template import Template
from openedx.core.djangoapps.catalog.utils import get_course_run_details
from openedx.core.djangoapps.lang_pref.api import get_closest_released_language
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.lib.courses import course_image_url
from openedx.core.djangoapps.certificates.api import display_date_for_certificate, certificates_viewable_for_course
from student.models import LinkedInAddToProfileConfiguration
from util import organizations_helpers as organization_api
from util.date_utils import strftime_localized
from util.views import handle_500
from django.conf import settings
from django.db import connections
from pymongo import MongoClient
from bson.objectid import ObjectId
from django.utils.translation import ugettext_lazy as _
import traceback

log = logging.getLogger(__name__)
_ = translation.ugettext

INVALID_CERTIFICATE_TEMPLATE_PATH = 'certificates/invalid.html'


def get_certificate_description(mode, certificate_type, platform_name):
    """
    :return certificate_type_description on the basis of current mode
    """
    certificate_type_description = None
    if mode == 'honor':
        # Translators:  This text describes the 'Honor' course certificate type.
        certificate_type_description = _("An {cert_type} certificate signifies that a "
                                         "learner has agreed to abide by the honor code established by {platform_name} "
                                         "and has completed all of the required tasks for this course under its "
                                         "guidelines.").format(cert_type=certificate_type,
                                                               platform_name=platform_name)
    elif mode == 'verified':
        # Translators:  This text describes the 'ID Verified' course certificate type, which is a higher level of
        # verification offered by edX.  This type of verification is useful for professional education/certifications
        certificate_type_description = _("A {cert_type} certificate signifies that a "
                                         "learner has agreed to abide by the honor code established by {platform_name} "
                                         "and has completed all of the required tasks for this course under its "
                                         "guidelines. A {cert_type} certificate also indicates that the "
                                         "identity of the learner has been checked and "
                                         "is valid.").format(cert_type=certificate_type,
                                                             platform_name=platform_name)
    elif mode == 'xseries':
        # Translators:  This text describes the 'XSeries' course certificate type.  An XSeries is a collection of
        # courses related to each other in a meaningful way, such as a specific topic or theme, or even an organization
        certificate_type_description = _("An {cert_type} certificate demonstrates a high level of "
                                         "achievement in a program of study, and includes verification of "
                                         "the student's identity.").format(cert_type=certificate_type)
    return certificate_type_description


def _update_certificate_context(context, course, user_certificate, platform_name):
    """
    Build up the certificate web view context using the provided values
    (Helper method to keep the view clean)
    """
    # Populate dynamic output values using the course/certificate data loaded above
    certificate_type = context.get('certificate_type')

    # Populate dynamic output values using the course/certificate data loaded above
    certificate_type = context.get('certificate_type')

    nice_sitecode = 'AD521'  # NICE로부터 부여받은 사이트 코드
    nice_sitepasswd = 'z0lWlstxnw0u'  # NICE로부터 부여받은 사이트 패스워드
    nice_cb_encode_path = '/edx/app/edxapp/edx-platform/CPClient'

    nice_authtype = ''  # 없으면 기본 선택화면, X: 공인인증서, M: 핸드폰, C: 카드
    nice_popgubun = 'N'  # Y : 취소버튼 있음 / N : 취소버튼 없음
    nice_customize = ''  # 없으면 기본 웹페이지 / Mobile : 모바일페이지
    nice_gender = ''  # 없으면 기본 선택화면, 0: 여자, 1: 남자
    nice_reqseq = 'REQ0000000001'  # 요청 번호, 이는 성공/실패후에 같은 값으로 되돌려주게 되므로
    # 업체에서 적절하게 변경하여 쓰거나, 아래와 같이 생성한다.
    lms_base = settings.ENV_TOKENS.get('LMS_BASE')
    # lms_base = 'dev.kr:18000'

    nice_returnurl = "http://{lms_base}/nicecheckplus".format(lms_base=lms_base)  # 성공시 이동될 URL
    # nice_returnurl = "http://localhost:8000/nicecheckplus".format(lms_base=lms_base)  # 성공시 이동될 URL
    nice_errorurl = "http://{lms_base}/nicecheckplus_error".format(lms_base=lms_base)  # 실패시 이동될 URL
    # nice_errorurl = "http://localhost:8000/nicecheckplus_error".format(lms_base=lms_base)  # 실패시 이동될 URL

    nice_returnMsg = ''

    plaindata = '7:REQ_SEQ{0}:{1}8:SITECODE{2}:{3}9:AUTH_TYPE{4}:{5}7:RTN_URL{6}:{7}7:ERR_URL{8}:{9}11:POPUP_GUBUN{10}:{11}9:CUSTOMIZE{12}:{13}6:GENDER{14}:{15}' \
        .format(len(nice_reqseq), nice_reqseq,
                len(nice_sitecode), nice_sitecode,
                len(nice_authtype), nice_authtype,
                len(nice_returnurl), nice_returnurl,
                len(nice_errorurl), nice_errorurl,
                len(nice_popgubun), nice_popgubun,
                len(nice_customize), nice_customize,
                len(nice_gender), nice_gender)

    nice_command = '{0} ENC {1} {2} {3}'.format(nice_cb_encode_path, nice_sitecode, nice_sitepasswd, plaindata)

    enc_data = commands.getoutput(nice_command)

    # 특수분야 직무 이수증 여부
    with connections['default'].cursor() as cur:
        query = '''
                select use_yn from special_institute 
                where course_id  = '{course_id}'
            '''.format(course_id=course.id)

        cur.execute(query)
        inst_yn = cur.fetchall()

    try:
        context['inst_yn'] = inst_yn[0][0]

    except Exception as e:
        print 'no special course ', e
        context['inst_yn'] = ''

    # 특수분야 직무 이수증 neis_id 여부
    with connections['default'].cursor() as cur:
        query = '''
            SELECT 
                addinfo
            FROM
                multisite_member
            WHERE
                user_id = '{user_id}' AND site_id = 7;
        '''.format(user_id=context['accomplishment_user_id'])
        cur.execute(query)
        multisite_member_addinfo = cur.fetchone()

    # 특수분야 직무 이수증 정보
    with connections['default'].cursor() as cur:
        query = '''
            SELECT 
                course_id,
                CONCAT(IF(quarter IN (1 , 2), 'a', 'b'),
                        LPAD(rn, 4, '0')) cert_num,
                appoint_num
            FROM
                (SELECT 
                    a.id course_id,
                        b.user_id,
                        QUARTER(ADDDATE(a.start, INTERVAL 9 HOUR)) quarter,
                        (@rn:=@rn + 1) rn,
                        c.appoint_num
                FROM
                    course_overviews_courseoverview a
                JOIN student_courseenrollment b ON a.id = b.course_id
                JOIN (SELECT @rn:=0) rn
                LEFT JOIN special_institute c ON a.id = c.course_id
                WHERE
                    a.id = '{course_id}'
                ORDER BY b.id) t1
            WHERE
                user_id = {user_id};
        '''.format(user_id=context['accomplishment_user_id'], course_id=course.id)
        cur.execute(query)
        multisite_cert_info = cur.fetchone()

    try:
        addinfo_json = json.loads(multisite_member_addinfo[0])

        context['instNm'] = addinfo_json.get('instNm', '미입력')
        context['neisId'] = addinfo_json.get('neisId', '미입력')
        context['mbrNm'] = addinfo_json.get('mbrNm', '미입력')
        mbrbirth = addinfo_json.get('mbrbirth')

        context['instqq'] = addinfo_json.get('instqq', '미입력')
        context['sosok'] = addinfo_json.get('sosok', '미입력')

        if mbrbirth:
            mbrbirth_format = datetime.strptime(mbrbirth, '%Y%m%d').date().strftime('%Y년 %m월 %d일')
            context['mbrbirth'] = mbrbirth_format
        else:
            context['mbrbirth'] = '미입력'

    except Exception as e:
        print traceback.print_exc(e)

    try:
        context['enroll_num'] = multisite_cert_info[1]
        context['appoint_num'] = multisite_cert_info[2]
    except:
        context['enroll_num'] = '-'
        context['appoint_num'] = '-'

    # {"instNm": "경기도교육청", "neisId": "J101389432", "mbrNm": "김하늘4", "mbrbirth": "20121234", "instqq": "직무"}

    with connections['default'].cursor() as cur:
        query = '''
            select site_code, site_name
            from multisite_member a
            join multisite b
            on a.site_id = b.site_id
            where a.user_id = '{user_id}'
            union
            select 'x' as site_code, provider as site_name
            from social_auth_usersocialauth
            where user_id = '{user_id}'
            and provider not in ('facebook', 'kakao', 'google-oauth2', 'google-plus', 'naver');
        '''.format(user_id=context['accomplishment_user_id'])
        cur.execute(query)
        multisite = cur.fetchall()

    print '------------------------------------'
    print 'user_id -> ', context['accomplishment_user_id']
    print 'multisite -> ', multisite
    print '------------------------------------'

    context['multisite'] = multisite

    context['enc_data'] = enc_data
    context['year'] = user_certificate.modified_date.year
    # Override the defaults with any mode-specific static values
    context['certificate_id_number'] = user_certificate.verify_uuid
    context['certificate_verify_url'] = "{prefix}{uuid}{suffix}".format(
        prefix=context.get('certificate_verify_url_prefix'),
        uuid=user_certificate.verify_uuid,
        suffix=context.get('certificate_verify_url_suffix')
    )

    # Translators:  The format of the date includes the full name of the month
    date = display_date_for_certificate(course, user_certificate)
    context['certificate_date_issued'] = _('{month}.{day}.{year}.').format(
        month=strftime_localized(date, "%m"),
        day=date.day,
        year=date.year
    )

    now_date_two = datetime.now(timezone('Asia/Seoul')).strftime('%m.%d.%Y')
    context['certificate_date_issued4'] = now_date_two

    now_date = datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m.%d')
    context['certificate_date_issued2'] = now_date

    now_date_special = datetime.now(timezone('Asia/Seoul')).strftime('%Y년 %m월 %d일')
    context['certificate_date_issued3'] = now_date_special

    # Translators:  This text represents the verification of the certificate
    context['document_meta_description'] = _('This is a valid {platform_name} certificate for {user_name}, '
                                             'who participated in {partner_short_name} {course_number}').format(
        platform_name=platform_name,
        user_name=context['accomplishment_copy_name'],
        partner_short_name=context['organization_short_name'],
        course_number=context['course_number']
    )

    # Translators:  This text is bound to the HTML 'title' element of the page and appears in the browser title bar
    context['document_title'] = _("{partner_short_name} {course_number} Certificate | {platform_name}").format(
        partner_short_name=context['organization_short_name'],
        course_number=context['course_number'],
        platform_name=platform_name
    )

    # Translators:  This text fragment appears after the student's name (displayed in a large font) on the certificate
    # screen.  The text describes the accomplishment represented by the certificate information displayed to the user
    context['accomplishment_copy_description_full'] = _("successfully completed, received a passing grade, and was "
                                                        "awarded this {platform_name} {certificate_type} "
                                                        "Certificate of Completion in ").format(
        platform_name=platform_name,
        certificate_type=context.get("certificate_type"))

    certificate_type_description = get_certificate_description(user_certificate.mode, certificate_type, platform_name)
    if certificate_type_description:
        context['certificate_type_description'] = certificate_type_description

    # Translators: This text describes the purpose (and therefore, value) of a course certificate
    context['certificate_info_description'] = _("{platform_name} acknowledges achievements through "
                                                "certificates, which are awarded for course activities "
                                                "that {platform_name} students complete.").format(
        platform_name=platform_name,
        tos_url=context.get('company_tos_url'),
        verified_cert_url=context.get('company_verified_certificate_url'))


def _update_context_with_basic_info(context, course_id, platform_name, configuration, user_id, preview_mode=None):
    """
    Updates context dictionary with basic info required before rendering simplest
    certificate templates.
    """
    # course_id = 'course-v1:CAUk+ACE_CAU01+2017_T2'

    context['platform_name'] = platform_name
    context['course_id'] = course_id
    context['course_id2'] = course_id.split('+')[1]
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')

    print "course_id -> ", course_id

    with connections['default'].cursor() as cur:
        query = '''
            select org
            from course_overviews_courseoverview
            where id = '{course_id}';
        '''.format(course_id=course_id)
        cur.execute(query)
        org = cur.fetchall()[0][0]

    with connections['default'].cursor() as cur:
        query = '''
            select save_path
            from tb_attach
            where id in (
                select logo_img_e
                from tb_org
                where org_id in (
                    select org
                    from course_overviews_courseoverview
                    where id = '{course_id}'
                )
            );
        '''.format(course_id=course_id)
        cur.execute(query)
        try:
            logo_eng = cur.fetchall()[0][0]
        except BaseException:
            logo_eng = ''

    print "logo_eng -> ", logo_eng

    with connections['default'].cursor() as cur:
        query = '''
            select save_path
            from tb_attach
            where id in (
                select logo_img
                from tb_org
                where org_id in (
                    select org
                    from course_overviews_courseoverview
                    where id = '{course_id}'
                )
            );
        '''.format(course_id=course_id)
        cur.execute(query)
        try:
            logo_kor = cur.fetchall()[0][0]
        except BaseException:
            logo_kor = ''

    print "logo_kor -> ", logo_kor

    context['logo_eng'] = logo_eng
    context['logo_kor'] = logo_kor

    cur = con.cursor()
    query = """
                SELECT plain_data
                  FROM auth_user_nicecheck
                 WHERE user_id = '{0}';
                 """.format(user_id)
    cur.execute(query)
    plain_data = cur.fetchall()

    query = """
                SELECT is_kakao, name, date_of_birth
                  FROM tb_auth_user_addinfo
                 WHERE user_id = '{0}';
             """.format(user_id)
    cur.execute(query)
    addinfo_data = cur.fetchone()
    cur.close()

    if len(plain_data) != 0:
        """
        nice_dict = ast.literal_eval(plain_data[0][0])
        user_name = nice_dict['UTF8_NAME']
        birth_date = nice_dict['BIRTHDATE']
        user_name = urllib.unquote(user_name).decode('utf8')
        context['user_name'] = user_name
        
        context['birth_date'] = birth_date[0:4]
        """

        pd = plain_data[0][0]
        pd = json.loads(pd)

        user_name = urllib2.unquote(str(pd['UTF8_NAME'])).decode('utf8')

        pd = pd['BIRTHDATE']
        pd = pd[0:4] + '.' + pd[4:6] + '.' + pd[6:8]
        user_birth = pd

        context['user_name'] = user_name
        context['birth_date'] = user_birth

    elif addinfo_data:
        if addinfo_data[0] == 'Y':
            context['user_name'] = addinfo_data[1]
            context['birth_date'] = addinfo_data[2][0:4] + '.' + addinfo_data[2][4:6] + '.' + addinfo_data[2][6:8]
        else:
            context['user_name'] = ''
            context['birth_date'] = ''

    else:
        context['user_name'] = ''
        context['birth_date'] = ''

    cur = con.cursor()
    query = """
                SELECT detail_name, detail_Ename
                  FROM code_detail
                 WHERE group_code = 003 AND detail_code = '{0}';
                 """.format(org)
    cur.execute(query)
    org_name = cur.fetchall()
    cur.close()

    if (len(org_name) == 0):
        context['org_name_k'] = org
        context['org_name_e'] = org
    else:
        context['org_name_k'] = org_name[0][0]
        context['org_name_e'] = org_name[0][1]

    # ----이수증 query--
    cur = con.cursor()
    query = """
                SELECT effort, date_format(start, '%Y %m %d'), date_format(end, '%Y %m %d'), datediff(end, start) date_diff FROM course_overviews_courseoverview where id = '{0}';
                """.format(course_id)
    cur.execute(query)
    row = cur.fetchone()
    cur.close()

    effort = row[0]
    start_date = row[1]
    end_date = row[2]
    date_diff = row[3]

    course_effort = effort.split('@')[0] if effort and '@' in effort else '-'
    course_week = effort.split('@')[1].split('#')[0] if effort and '@' in effort and '#' in effort else '-'

    if '$' in effort:
        course_video = effort.split('#')[1].split('$')[0] if effort and '#' in effort else '-'
    else:
        course_video = effort.split('#')[1] if effort and '#' in effort else '-'
    cert_effort = effort.split('$')[1] if effort and '$' in effort else None
    time = course_effort.split(':')

    context['course_week'] = course_week
    context['course_effort'] = course_effort

    if (course_effort == '-' or course_week == '-' or time[0] == '' or time[1] == ''):
        context['Learning_h'] = '-'
        context['Learning_m'] = '-'
    else:
        all_time = ((int(time[0]) * 60) + int(time[1])) * int(course_week)
        Learning_m = str(all_time % 60)
        if len(Learning_m) == 1:
            Learning_m = Learning_m + '0'
        context['Learning_h'] = str(all_time / 60)
        context['Learning_m'] = Learning_m
    if (course_video == '-'):
        context['Play_h'] = '-'
        context['Play_m'] = '-'
    else:
        Play_time = course_video.split(':')
        if (Play_time[0] == '' or Play_time[1] == ''):
            context['Play_h'] = '-'
            context['Play_m'] = '-'
        else:
            context['Play_h'] = Play_time[0]
            context['Play_m'] = Play_time[1]

    if (cert_effort is None):
        context['course_effort_h'] = '-'
        context['course_effort_m'] = '-'
    else:
        cert_effort_hh = cert_effort.split(':')[0]
        cert_effort_mm = cert_effort.split(':')[1]
        context['course_effort_h'] = cert_effort_hh
        context['course_effort_m'] = cert_effort_mm

    if preview_mode:
        grade = 100
        created_date = datetime.now().strftime('%Y.%m.%d %H:%M')
    else:
        cur = con.cursor()
        query = """
                    SELECT ifnull(grade, 0), date_format(now(), '%Y.%m.%d  %h:%i') FROM certificates_generatedcertificate where course_id = '{0}' and user_id = '{1}';
                    """.format(course_id, user_id)
        cur.execute(query)
        row = cur.fetchall()
        cur.close()

        try:
            grade = int(float(row[0][0]) * 100)
            created_date = row[0][1]
        except BaseException:
            grade = 100
            created_date = '2099-12-12 00:00:00'

    context['grade'] = str(grade)
    context['created_date'] = created_date
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['date_diff'] = date_diff

    static_url = "http://" + settings.ENV_TOKENS.get('LMS_BASE')
    # static_url = 'http://kmooc.kr'
    print "static_url -> ", static_url

    context['static_url'] = static_url

    course_index = course_id.split(':')
    course_index2 = course_index[1].split('+')

    course_org = course_index2[0]
    course_course = course_index2[1]
    course_run = course_index2[2]

    # client = MongoClient('127.0.0.1', 27017)

    # db = client.edxapp
    # cursors = db.modulestore.active_versions.find_one({"org": course_org, "course": course_course, "run": course_run})
    # pb = cursors.get('versions').get('published-branch')
    # certifi = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_type": "course"}}})
    # signatories = certifi.get('blocks')[0].get('fields').get('certificates').get('certificates')[0].get('signatories')[0]
    # teacher_name = signatories.get('name')
    # title = signatories.get('title')
    # organization = signatories.get('organization')
    # signature_image_path = signatories.get('signature_image_path')

    course_index = course_id.split(':')
    course_index = course_index[1].split('+')

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')

    cur = con.cursor()
    query = """
                SELECT count(*)
                  FROM auth_user_nicecheck
                 WHERE user_id = {0};
                """.format(user_id)
    cur.execute(query)
    nice_check_flag = cur.fetchall()

    query = """
            SELECT is_kakao, name, date_of_birth
              FROM tb_auth_user_addinfo
             WHERE user_id = '{0}';
            """.format(user_id)
    cur.execute(query)
    kakao_check_flag = cur.fetchone()

    query = """
                SELECT count(*)
                FROM survey_check
                where course_id = '{0}' and regist_id = {1};
                """.format(course_id, user_id)
    cur.execute(query)
    survey_check = cur.fetchall()
    cur.close()

    context['nice_check_flag'] = nice_check_flag[0][0]

    if kakao_check_flag:

        if kakao_check_flag[0]:
            context['kakao_check_flag'] = kakao_check_flag[0]
        else:
            context['kakao_check_flag'] = 'N'
    else:
        context['kakao_check_flag'] = 'N'

    context['survey_check'] = survey_check[0][0]
    context['user_id'] = user_id

    with connections['default'].cursor() as cur, MongoClient(settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host'),
                                                             settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get(
                                                                 'port')) as client:
        db = client.edxapp
        cursor = db.modulestore.active_versions.find_one(
            {'org': course_index[0], 'course': course_index[1], 'run': course_index[2]})
        pb = cursor.get('versions').get('published-branch')
        cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)})
        blocks = cursor.get('blocks')
        for block in blocks:
            block_type = block.get('block_type')

            if block_type == 'course':
                classfy = block.get('fields').get('classfy')
                if not classfy:
                    classfy = ''

    cur = con.cursor()
    query = """
                SELECT detail_name, detail_Ename
                  FROM code_detail
                 WHERE detail_code = '{0}';
                """.format(classfy)
    cur.execute(query)
    classfy_index = cur.fetchall()
    cur.close()

    if len(classfy_index) == 0:
        context['classfy_k'] = classfy
        context['classfy_e'] = classfy
    else:
        context['classfy_k'] = classfy_index[0][0]
        context['classfy_e'] = classfy_index[0][1]

    # Update the view context with the default ConfigurationModel settings
    context.update(configuration.get('default', {}))

    # Translators:  'All rights reserved' is a legal term used in copyrighting to protect published content
    reserved = _("All rights reserved")
    context['copyright_text'] = u'&copy; {year} {platform_name}. {reserved}.'.format(
        year=datetime.now(pytz.timezone(settings.TIME_ZONE)).year,
        platform_name=platform_name,
        reserved=reserved
    )

    # Translators:  This text is bound to the HTML 'title' element of the page and appears
    # in the browser title bar when a requested certificate is not found or recognized
    context['document_title'] = _("Invalid Certificate")

    context['company_tos_urltext'] = _("Terms of Service & Honor Code")

    # Translators: A 'Privacy Policy' is a legal document/statement describing a website's use of personal information
    context['company_privacy_urltext'] = _("Privacy Policy")

    # Translators: This line appears as a byline to a header image and describes the purpose of the page
    context['logo_subtitle'] = _("Certificate Validation")

    # Translators: Accomplishments describe the awards/certifications obtained by students on this platform
    context['accomplishment_copy_about'] = _('About {platform_name} Accomplishments').format(
        platform_name=platform_name
    )

    # Translators:  This line appears on the page just before the generation date for the certificate
    context['certificate_date_issued_title'] = _("Issued On:")

    # Translators:  The Certificate ID Number is an alphanumeric value unique to each individual certificate
    context['certificate_id_number_title'] = _('Certificate ID Number')

    context['certificate_info_title'] = _('About {platform_name} Certificates').format(
        platform_name=platform_name
    )

    context['certificate_verify_title'] = _("How {platform_name} Validates Student Certificates").format(
        platform_name=platform_name
    )

    # Translators:  This text describes the validation mechanism for a certificate file (known as GPG security)
    context['certificate_verify_description'] = _('Certificates issued by {platform_name} are signed by a gpg key so '
                                                  'that they can be validated independently by anyone with the '
                                                  '{platform_name} public key. For independent verification, '
                                                  '{platform_name} uses what is called a '
                                                  '"detached signature"&quot;".').format(platform_name=platform_name)

    context['certificate_verify_urltext'] = _("Validate this certificate for yourself")

    # Translators:  This text describes (at a high level) the mission and charter the edX platform and organization
    context['company_about_description'] = _("{platform_name} offers interactive online classes and MOOCs.").format(
        platform_name=platform_name)

    context['company_about_title'] = _("About {platform_name}").format(platform_name=platform_name)

    context['company_about_urltext'] = _("Learn more about {platform_name}").format(platform_name=platform_name)

    context['company_courselist_urltext'] = _("Learn with {platform_name}").format(platform_name=platform_name)

    context['company_careers_urltext'] = _("Work at {platform_name}").format(platform_name=platform_name)

    context['company_contact_urltext'] = _("Contact {platform_name}").format(platform_name=platform_name)

    # Translators:  This text appears near the top of the certficate and describes the guarantee provided by edX
    context['document_banner'] = _("{platform_name} acknowledges the following student accomplishment").format(
        platform_name=platform_name
    )


def _update_course_context(request, context, course, course_key, platform_name):
    """
    Updates context dictionary with course info.
    """
    context['full_course_image_url'] = request.build_absolute_uri(course_image_url(course))
    course_title_from_cert = context['certificate_data'].get('course_title', '')

    if course_title_from_cert == '':
        print "course.display_name -> ", course.display_name
        context['accomplishment_copy_course_name'] = course.display_name
        context['accomplishment_copy_course_name_incoding'] = course.display_name.decode('utf8')
    else:
        print "course_title_from_cert -> ", course_title_from_cert
        context['accomplishment_copy_course_name'] = course_title_from_cert
        context['accomplishment_copy_course_name_incoding'] = course_title_from_cert.decode('utf8')

    course_number = course.display_coursenumber if course.display_coursenumber else course.number
    context['course_number'] = course_number
    if context['organization_long_name']:
        # Translators:  This text represents the description of course
        context['accomplishment_copy_course_description'] = _('a course of study offered by {partner_short_name}, '
                                                              'an online learning initiative of '
                                                              '{partner_long_name}.').format(
            partner_short_name=context['organization_short_name'],
            partner_long_name=context['organization_long_name'],
            platform_name=platform_name)
    else:
        # Translators:  This text represents the description of course
        context['accomplishment_copy_course_description'] = _('a course of study offered by '
                                                              '{partner_short_name}.').format(
            partner_short_name=context['organization_short_name'],
            platform_name=platform_name)


def _update_social_context(request, context, course, user, user_certificate, platform_name):
    """
    Updates context dictionary with info required for social sharing.
    """
    share_settings = configuration_helpers.get_value("SOCIAL_SHARING_SETTINGS", settings.SOCIAL_SHARING_SETTINGS)
    context['facebook_share_enabled'] = share_settings.get('CERTIFICATE_FACEBOOK', False)
    context['facebook_app_id'] = configuration_helpers.get_value("FACEBOOK_APP_ID", settings.FACEBOOK_APP_ID)
    context['facebook_share_text'] = share_settings.get(
        'CERTIFICATE_FACEBOOK_TEXT',
        _("I completed the {course_title} course on {platform_name}.").format(
            course_title=context['accomplishment_copy_course_name'],
            platform_name=platform_name
        )
    )
    context['twitter_share_enabled'] = share_settings.get('CERTIFICATE_TWITTER', False)
    context['twitter_share_text'] = share_settings.get(
        'CERTIFICATE_TWITTER_TEXT',
        _("I completed a course at {platform_name}. Take a look at my certificate.").format(
            platform_name=platform_name
        )
    )

    share_url = request.build_absolute_uri(get_certificate_url(course_id=course.id, uuid=user_certificate.verify_uuid))
    context['share_url'] = share_url
    twitter_url = ''
    if context.get('twitter_share_enabled', False):
        twitter_url = 'https://twitter.com/intent/tweet?text={twitter_share_text}&url={share_url}'.format(
            twitter_share_text=smart_str(context['twitter_share_text']),
            share_url=urllib.quote_plus(smart_str(share_url))
        )
    context['twitter_url'] = twitter_url
    context['linked_in_url'] = None
    # If enabled, show the LinkedIn "add to profile" button
    # Clicking this button sends the user to LinkedIn where they
    # can add the certificate information to their profile.
    linkedin_config = LinkedInAddToProfileConfiguration.current()
    linkedin_share_enabled = share_settings.get('CERTIFICATE_LINKEDIN', linkedin_config.enabled)
    if linkedin_share_enabled:
        context['linked_in_url'] = linkedin_config.add_to_profile_url(
            course.id,
            course.display_name,
            user_certificate.mode,
            smart_str(share_url)
        )


def _update_context_with_user_info(context, user, user_certificate):
    """
    Updates context dictionary with user related info.
    """
    user_fullname = user.profile.name
    context['username'] = user.username
    context['course_mode'] = user_certificate.mode
    context['accomplishment_user_id'] = user.id
    context['accomplishment_copy_name'] = user_fullname
    print 'name!', user, '/', user.id, '/', user.profile, '/', user.profile.name, '/', user_fullname
    context['accomplishment_copy_username'] = user.username

    context['accomplishment_more_title'] = _("More Information About {user_name}'s Certificate:").format(
        user_name=user_fullname
    )
    # Translators: This line is displayed to a user who has completed a course and achieved a certification
    context['accomplishment_banner_opening'] = _("{fullname}, you earned a certificate!").format(
        fullname=user_fullname
    )

    # Translators: This line congratulates the user and instructs them to share their accomplishment on social networks
    context['accomplishment_banner_congrats'] = _("Congratulations! This page summarizes what "
                                                  "you accomplished. Show it off to family, friends, and colleagues "
                                                  "in your social and professional networks.")

    # Translators: This line leads the reader to understand more about the certificate that a student has been awarded
    context['accomplishment_copy_more_about'] = _("More about {fullname}'s accomplishment").format(
        fullname=user_fullname
    )


def _get_user_certificate(request, user, course_key, course, preview_mode=None):
    """
    Retrieves user's certificate from db. Creates one in case of preview mode.
    Returns None if there is no certificate generated for given user
    otherwise returns `GeneratedCertificate` instance.
    """
    user_certificate = None
    if preview_mode:
        # certificate is being previewed from studio
        if has_access(user, 'instructor', course) or has_access(user, 'staff', course):
            if course.certificate_available_date and not course.self_paced:
                modified_date = course.certificate_available_date
            else:
                modified_date = datetime.now().date()
            user_certificate = GeneratedCertificate(
                mode=preview_mode,
                verify_uuid=unicode(uuid4().hex),
                modified_date=modified_date
            )
    elif certificates_viewable_for_course(course):
        # certificate is being viewed by learner or public
        try:
            user_certificate = GeneratedCertificate.eligible_certificates.get(
                user=user,
                course_id=course_key,
                status=CertificateStatuses.downloadable
            )
        except GeneratedCertificate.DoesNotExist:
            pass

    return user_certificate


def _track_certificate_events(request, context, course, user, user_certificate):
    """
    Tracks web certificate view related events.
    """
    # Badge Request Event Tracking Logic
    course_key = course.location.course_key

    if 'evidence_visit' in request.GET:
        badge_class = get_completion_badge(course_key, user)
        if not badge_class:
            log.warning('Visit to evidence URL for badge, but badges not configured for course "%s"', course_key)
            badges = []
        else:
            badges = badge_class.get_for_user(user)
        if badges:
            # There should only ever be one of these.
            badge = badges[0]
            tracker.emit(
                'edx.badge.assertion.evidence_visited',
                {
                    'badge_name': badge.badge_class.display_name,
                    'badge_slug': badge.badge_class.slug,
                    'badge_generator': badge.backend,
                    'issuing_component': badge.badge_class.issuing_component,
                    'user_id': user.id,
                    'course_id': unicode(course_key),
                    'enrollment_mode': badge.badge_class.mode,
                    'assertion_id': badge.id,
                    'assertion_image_url': badge.image_url,
                    'assertion_json_url': badge.assertion_url,
                    'issuer': badge.data.get('issuer'),
                }
            )
        else:
            log.warn(
                "Could not find badge for %s on course %s.",
                user.id,
                course_key,
            )

    # track certificate evidence_visited event for analytics when certificate_user and accessing_user are different
    if request.user and request.user.id != user.id:
        emit_certificate_event('evidence_visited', user, unicode(course.id), course, {
            'certificate_id': user_certificate.verify_uuid,
            'enrollment_mode': user_certificate.mode,
            'social_network': CertificateSocialNetworks.linkedin
        })


def _update_configuration_context(context, configuration):
    """
    Site Configuration will need to be able to override any hard coded
    content that was put into the context in the
    _update_certificate_context() call above. For example the
    'company_about_description' talks about edX, which we most likely
    do not want to keep in configurations.
    So we need to re-apply any configuration/content that
    we are sourcing from the database. This is somewhat duplicative of
    the code at the beginning of this method, but we
    need the configuration at the top as some error code paths
    require that to be set up early on in the pipeline
    """

    config_key = configuration_helpers.get_value('domain_prefix')
    config = configuration.get("microsites", {})
    if config_key and config:
        context.update(config.get(config_key, {}))


def _update_badge_context(context, course, user):
    """
    Updates context with badge info.
    """
    badge = None
    if badges_enabled() and course.issue_badges:
        badges = get_completion_badge(course.location.course_key, user).get_for_user(user)
        if badges:
            badge = badges[0]
    context['badge'] = badge


def _update_organization_context(context, course):
    """
    Updates context with organization related info.
    """
    partner_long_name, organization_logo = None, None
    partner_short_name = course.display_organization if course.display_organization else course.org
    organizations = organization_api.get_course_organizations(course_id=course.id)
    if organizations:
        # TODO Need to add support for multiple organizations, Currently we are interested in the first one.
        organization = organizations[0]
        partner_long_name = organization.get('name', partner_long_name)
        partner_short_name = organization.get('short_name', partner_short_name)
        organization_logo = organization.get('logo', None)

    context['organization_long_name'] = partner_long_name
    context['organization_short_name'] = partner_short_name
    context['accomplishment_copy_course_org'] = partner_short_name
    context['organization_logo'] = organization_logo


def render_cert_by_uuid(request, certificate_uuid):
    """
    This public view generates an HTML representation of the specified certificate
    """
    try:
        certificate = GeneratedCertificate.eligible_certificates.get(
            verify_uuid=certificate_uuid,
            status=CertificateStatuses.downloadable
        )
        return render_html_view(request, certificate.user.id, unicode(certificate.course_id))
    except GeneratedCertificate.DoesNotExist:
        raise Http404


def render_cert_by_uuid_special(request, certificate_uuid):
    """
    create by 92hoy

    This public view generates an HTML representation of the specified certificate
    """
    try:
        certificate = GeneratedCertificate.eligible_certificates.get(
            verify_uuid=certificate_uuid,
            status=CertificateStatuses.downloadable
        )
        special = 'Y'
        return render_html_view(request, certificate.user.id, unicode(certificate.course_id), special)
    except GeneratedCertificate.DoesNotExist:
        raise Http404


@handle_500(
    template_path="certificates/server-error.html",
    test_func=lambda request: request.GET.get('preview', None)
)
def render_html_view(request, user_id, course_id, special=None):
    """
    modify by 92hoy
     - special : 특수분야 이수증 param

    This public view generates an HTML representation of the specified user and course
    If a certificate is not available, we display a "Sorry!" screen instead
    """
    try:
        user_id = int(user_id)
    except ValueError:
        raise Http404

    print 'speicalspeicalspeicalspeical', special
    preview_mode = request.GET.get('preview', None)
    platform_name = configuration_helpers.get_value("platform_name", settings.PLATFORM_NAME)
    configuration = CertificateHtmlViewConfiguration.get_config()

    # Kick the user back to the "Invalid" screen if the feature is disabled globally
    if not settings.FEATURES.get('CERTIFICATES_HTML_VIEW', False):
        return _render_invalid_certificate(course_id, platform_name, configuration, user_id, preview_mode)

    # Load the course and user objects
    try:
        course_key = CourseKey.from_string(course_id)
        user = User.objects.get(id=user_id)
        course = get_course_by_id(course_key)

    # For any course or user exceptions, kick the user back to the "Invalid" screen
    except (InvalidKeyError, User.DoesNotExist, Http404) as exception:
        error_str = (
            "Invalid cert: error finding course %s or user with id "
            "%d. Specific error: %s"
        )
        log.info(error_str, course_id, user_id, str(exception))
        return _render_invalid_certificate(course_id, platform_name, configuration, user_id, preview_mode)

    # Kick the user back to the "Invalid" screen if the feature is disabled for the course
    if not course.cert_html_view_enabled:
        log.info(
            "Invalid cert: HTML certificates disabled for %s. User id: %d",
            course_id,
            user_id,
        )
        return _render_invalid_certificate(course_id, platform_name, configuration, user_id, preview_mode)

    # Load user's certificate
    user_certificate = _get_user_certificate(request, user, course_key, course, preview_mode)
    if not user_certificate:
        log.info(
            "Invalid cert: User %d does not have eligible cert for %s.",
            user_id,
            course_id,
        )
        return _render_invalid_certificate(course_id, platform_name, configuration, user_id, preview_mode)

    # Get the active certificate configuration for this course
    # If we do not have an active certificate, we'll need to send the user to the "Invalid" screen
    # Passing in the 'preview' parameter, if specified, will return a configuration, if defined
    active_configuration = get_active_web_certificate(course, preview_mode)
    if active_configuration is None:
        log.info(
            "Invalid cert: course %s does not have an active configuration. User id: %d",
            course_id,
            user_id,
        )
        return _render_invalid_certificate(course_id, platform_name, configuration, user_id, preview_mode)

    # Get data from Discovery service that will be necessary for rendering this Certificate.
    catalog_data = _get_catalog_data_for_course(course_key)

    # Determine whether to use the standard or custom template to render the certificate.
    custom_template = None
    custom_template_language = None
    if settings.FEATURES.get('CUSTOM_CERTIFICATE_TEMPLATES_ENABLED', False):
        custom_template, custom_template_language = _get_custom_template_and_language(
            course.id,
            user_certificate.mode,
            catalog_data.pop('content_language', None)
        )

    # Determine the language that should be used to render the certificate.
    # For the standard certificate template, use the user language. For custom templates, use
    # the language associated with the template.
    user_language = translation.get_language()
    certificate_language = custom_template_language if custom_template else user_language

    # Generate the certificate context in the correct language, then render the template.
    with translation.override(certificate_language):
        context = {'user_language': user_language}

        _update_context_with_basic_info(context, course_id, platform_name, configuration, user_id, preview_mode)

        context['certificate_data'] = active_configuration

        # Append/Override the existing view context values with any mode-specific ConfigurationModel values
        context.update(configuration.get(user_certificate.mode, {}))

        # Append organization info
        _update_organization_context(context, course)

        # Append course info
        _update_course_context(request, context, course, course_key, platform_name)

        # Append course run info from discovery
        context.update(catalog_data)

        # Append user info
        _update_context_with_user_info(context, user, user_certificate)

        # Append social sharing info
        _update_social_context(request, context, course, user, user_certificate, platform_name)

        # Append/Override the existing view context values with certificate specific values
        _update_certificate_context(context, course, user_certificate, platform_name)

        # Append badge info
        _update_badge_context(context, course, user)

        # Append site configuration overrides
        _update_configuration_context(context, configuration)

        # Add certificate header/footer data to current context
        context.update(get_certificate_header_context(is_secure=request.is_secure()))
        context.update(get_certificate_footer_context())

        # Append/Override the existing view context values with any course-specific static values from Advanced Settings
        context.update(course.cert_html_view_overrides)

        # Track certificate view events
        _track_certificate_events(request, context, course, user, user_certificate)

        # Render the certificate
        return _render_valid_certificate(request, context, custom_template, special)


def _get_catalog_data_for_course(course_key):
    """
    Retrieve data from the Discovery service necessary for rendering a certificate for a specific course.
    """
    course_certificate_settings = CertificateGenerationCourseSetting.get(course_key)
    if not course_certificate_settings:
        return {}

    catalog_data = {}
    course_run_fields = []
    if course_certificate_settings.language_specific_templates_enabled:
        course_run_fields.append('content_language')
    if course_certificate_settings.include_hours_of_effort:
        course_run_fields.extend(['weeks_to_complete', 'max_effort'])

    if course_run_fields:
        course_run_data = get_course_run_details(course_key, course_run_fields)
        if course_run_data.get('weeks_to_complete') and course_run_data.get('max_effort'):
            try:
                weeks_to_complete = int(course_run_data['weeks_to_complete'])
                max_effort = int(course_run_data['max_effort'])
                catalog_data['hours_of_effort'] = weeks_to_complete * max_effort
            except ValueError:
                log.exception('Error occurred while parsing course run details')
        catalog_data['content_language'] = course_run_data.get('content_language')

    return catalog_data


def _get_custom_template_and_language(course_id, course_mode, course_language):
    """
    Return the custom certificate template, if any, that should be rendered for the provided course/mode/language
    combination, along with the language that should be used to render that template.
    """
    closest_released_language = get_closest_released_language(course_language) if course_language else None
    template = get_certificate_template(course_id, course_mode, closest_released_language)

    if template and template.language:
        return (template, closest_released_language)
    elif template:
        return (template, settings.LANGUAGE_CODE)
    else:
        return (None, None)


def _render_invalid_certificate(course_id, platform_name, configuration, user_id, preview_mode):
    context = {}
    _update_context_with_basic_info(context, course_id, platform_name, configuration, user_id, preview_mode)
    return render_to_response(INVALID_CERTIFICATE_TEMPLATE_PATH, context)


def _render_valid_certificate(request, context, custom_template=None, special=None):
    if custom_template:
        template = Template(
            custom_template.template,
            output_encoding='utf-8',
            input_encoding='utf-8',
            default_filters=['decode.utf8'],
            encoding_errors='replace',
        )
        context = RequestContext(request, context)
        # print 'context 1', context
        return HttpResponse(template.render(context))
    else:
        # print 'context 2', context
        # print 'special', special

        context['special'] = special
        return render_to_response("certificates/valid.html", context)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
