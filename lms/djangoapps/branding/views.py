# -*- coding: utf-8 -*-
"""Views for the branding app. """
import logging
import urllib
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseRedirect
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
# import pymysql
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import re
from datetime import datetime
from datetime import timedelta

log = logging.getLogger(__name__)

def common_course_status(startDt, endDt):

    #input
    # startDt = 2016-12-19 00:00:00
    # endDt   = 2017-02-10 23:00:00
    # nowDt   = 2017-11-10 00:11:28

    #import
    from datetime import datetime
    from django.utils.timezone import UTC as UTC2

    #making nowDt
    nowDt = datetime.now(UTC2()).strftime("%Y-%m-%d-%H-%m-%S")
    nowDt = nowDt.split('-')
    nowDt = datetime(int(nowDt[0]), int(nowDt[1]), int(nowDt[2]), int(nowDt[3]), int(nowDt[4]), int(nowDt[5]))

    #logic
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

    #return status
    return status


def course_api(request):

    #mysql
    conn = pymysql.connect(host='192.168.33.21',
                           user='hello',
                           password='0000',
                           db='edxapp',
                           charset='utf8')

    cur = conn.cursor()
    #with connections['default'].cursor() as cur:
    sql = '''
        SELECT coc.id,
               coc.display_name,
               coc.start,
               coc.end,
               coc.enrollment_start,
               coc.enrollment_end,
               coc.created,
               coc.modified,
               coc.course_video_url,
               coc.course_image_url,
               cd.detail_name,
               coc.org,
               coc.display_number_with_default  AS course,
               Substring_index(coc.id, '+', -1) AS RUN,
               coc.effort,
               c.cert_date,
               coa.teacher_name
        FROM   edxapp.course_overviews_courseoverview AS coc
               left outer join edxapp.code_detail AS cd
                      ON coc.org = cd.detail_code
               left outer join (
                    select course_id, min(created_date) as cert_date
                    from edxapp.certificates_generatedcertificate
                    group by course_id
               ) as c
                      ON coc.id = c.course_id
                left outer join edxapp.course_overview_addinfo as coa
                      ON coc.id = coa.course_id
    '''
    cur.execute(sql)
    slist = cur.fetchall()

    # init list
    course_id_list = []     #코스아이디
    display_name_list = []  #강좌명
    univ_name_list = []     #대학명
    start_time_list = []    #시작일
    end_time_list = []      #종강일
    enroll_start_list = []  #수강신청 시작일
    enroll_end_list = []    #수강신청 종료일
    created_list = []       #강좌생성 시간
    modified_list = []      #강좌수정 시간
    video_list = []         #강좌소개 비디오
    img_list = []           #강좌 썸네일 이미지
    org_list = []           #org 코드
    course_list = []        #course 코드
    run_list = []           #run 코드
    e0_list = []            #주간학습권장시간
    e1_list = []            #총주차
    e2_list = []            #동영상재생시간
    et_list = []            #총학습시간
    course_status_list = [] #강좌상태
    classfy_list = []       #대분류
    middle_classfy_list = []#중분류
    cert_date_list = []     #이수증 생성일
    teacher_name_list = []  #교수자 이름

    # making data (insert)
    for item in slist:
        #mongo
        client = MongoClient('192.168.33.21', 27017)
        db = client["edxapp"]
        cursor = db.modulestore.active_versions.find_one({'org': item[11], 'course': item[12], 'run': item[13]})
        pb = cursor.get('versions').get('published-branch')
        cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)})
        cursor_text = str(cursor)
        index = cursor_text.find('classfy')
        cl = cursor_text[index:index+50]
        index = cursor_text.find('middle_classfy')
        mcl = cursor_text[index:index+50]
        index_cl = cl.find("': u'")
        index_mcl = mcl.find("': u'")
        cls = cl[index_cl+5:index_cl+15]
        mcls = mcl[index_mcl+5:index_mcl+15]
        ha = cls.find("',")
        hb = mcls.find("',")
        if mcls.find("'},") != -1:
            hb = mcls.find("'},")
        clsf = cls[:ha]
        m_clsf = mcls[:hb]

        classfy_list.append(clsf)                               #대분류
        middle_classfy_list.append(m_clsf)                      #중분류
        course_id_list.append(item[0])                          #코스아이디
        display_name_list.append(item[1])                       #강좌명
        start_time_list.append(item[2])                         #시작일
        end_time_list.append(item[3])                           #종강일
        enroll_start_list.append(item[4])                       #수강신청 시작일
        enroll_end_list.append(item[5])                         #수강신청 종료일
        created_list.append(item[6])                            #강좌생성 시간
        modified_list.append(item[7])                           #강좌수정 시간
        video_list.append(item[8])                              #강좌소개 비디오
        img_list.append("http://www.kmooc.kr" + str(item[9]))   #강좌 썸네일 이미지
        univ_name_list.append(unicode(item[10]).strip())                         #대학명
        org_list.append(item[11])                               #org 코드
        course_list.append(item[12])                            #course 코드
        run_list.append(item[13])                               #run 코드

        if item[15] == None or item[15] == '':
            cert_date_list.append('null')
        else:
            cert_date_list.append(item[15])                     #이수증 생성일

        if item[16] == None or item[16] == '':
            teacher_name_list.append('null')
        else:
            teacher_name_list.append(item[16])                  #교수자 이름

        status = common_course_status(item[2], item[3])         #강좌상태
        course_status_list.append(status)
                                                                #주간학습권장시간
                                                                #총주차
                                                                #동영상재생시간
                                                                #총학습시간
        c2 = item[14].find('@')
        c3 = item[14].find('#')

        # @ 있고 # 있는 로직 ex) 11:11@7#11:11
        if c2 != -1 and c3 != -1:
            tmp = item[14].replace('@','#')
            tmp = tmp.split('#')
            e0_list.append(tmp[0])
            e1_list.append(tmp[1])
            e2_list.append(tmp[2])
            t = tmp[0].split(':')
            tt = ((int(t[0]) * 60) + int(t[1])) * int(tmp[1])
            th = tt/60
            tm = tt%60
            if len(str(th)) == 1:
                th = "0" + str(th)
            if len(str(tm)) == 1:
                tm = "0" + str(tm)
            total_time = str(th) + ":" + str(tm)
            et_list.append(total_time)

        # #만 있는 로직 ex) 11:11#11:11
        elif c3 != -1:
            tmp = item[14]
            tmp = tmp.split('#')
            e0_list.append(tmp[0])
            e1_list.append('null')
            e2_list.append(tmp[1])
            et_list.append('null')

        # @만 있는 로직 ex) 11:11@7
        elif c2 != -1:
            tmp = item[14]
            tmp = tmp.split('@')
            e0_list.append(tmp[0])
            e1_list.append(tmp[1])
            e2_list.append('null')
            t = tmp[0].split(':')
            tt = ((int(t[0]) * 60) + int(t[1])) * int(tmp[1])
            th = tt/60
            tm = tt%60
            if len(str(th)) == 1:
                th = "0" + str(th)
            if len(str(tm)) == 1:
                tm = "0" + str(tm)
            total_time = str(th) + ":" + str(tm)
            et_list.append(total_time)

        # @ 없고 # 없는 로직 ex) 11:11
        elif c2 == -1 and c3 == -1:
            e0_list.append(item[14])
            e1_list.append('null')
            e2_list.append('null')
            et_list.append('null')

        # 전부 없는 로직 ex)
        else:
            e0_list.append('null')
            e1_list.append('null')
            e2_list.append('null')
            et_list.append('null')

    json_list = []
    for n in range(0, len(slist) ):
        item = '{' + '"course_id":' + '"' + str(course_id_list[n])  + '"' +  ',' + '"display_name":'  + '"' +  unicode(display_name_list[n])  + '"' +  ',' + '"univ_name":'  + '"' +  unicode(univ_name_list[n])  + '"' +  ',' + '"start_time":'  + '"' +  str(start_time_list[n])  + '"' +  ',' + '"end_time":'  + '"' +  str(end_time_list[n])  + '"' +  ',' + '"enroll_start":'  + '"' +  str(enroll_start_list[n])  + '"' +  ',' + '"enroll_end":'  + '"' +  str(enroll_end_list[n])  + '"' +  ',' + '"created":'  + '"' +  str(created_list[n])  + '"' +  ',' + '"modified":'  + '"' +  str(modified_list[n])  + '"' +  ',' + '"video":'  + '"' +  str(video_list[n])  + '"' +  ',' + '"img":'  + '"' +  str(img_list[n])  + '"' +  ',' + '"org":'  + '"' +  str(org_list[n])  + '"' +  ',' + '"course":'  + '"' +  str(course_list[n])  + '"' +  ',' + '"run":'  + '"' +  str(run_list[n])  + '"' +  ',' + '"e0":'  + '"' +  str(e0_list[n])  + '"' +  ',' + '"e1":'  + '"' +  str(e1_list[n])  + '"' +  ',' + '"e2":'  + '"' +  str(e2_list[n])  + '"' +  ',' + '"et":'  + '"' +  str(et_list[n])  + '"' +  ',' + '"course_status":'  + '"' +  str(course_status_list[n])  + '"' +  ',' + '"classfy":'  + '"' +  str(classfy_list[n])  + '"' +  ',' + '"middle_classfy":'  + '"' +  str(middle_classfy_list[n])  + '"' +  ',' + '"cert_date":'  + '"' +  str(cert_date_list[n])  + '"' +  ',' + '"teacher_name":'  + '"' +  str(teacher_name_list[n])  + '"' +  '}'
        if n == 0:
            item = "[" + item + ","
        elif n == len(slist)-1:
            item = item + "," + '{"total_cnt":"' + str(len(slist)) + '"}' + ']'
        else:
            item = item + ','
        json_list.append(item)

    return HttpResponse(json_list)

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

#==================================================================================================> login 오버라이딩 시작
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.module_loading import import_string
from django.contrib.auth.signals import user_logged_in

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
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.AUTH_USER_MODEL
        )

def _get_user_session_key(request):
    # This value in the session is always serialized to a string, so we need
    # to convert it back to Python whenever we access it.
    return get_user_model()._meta.pk.to_python(request.session[SESSION_KEY])

def login(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
                session_auth_hash and
                not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
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
#==================================================================================================> login 오버라이딩 종료


#==================================================================================================> AES 복호화 함수 시작
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode
def decrypt(key, _iv, enc):
    BLOCK_SIZE = 16  # Bytes
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = b64decode(enc)
    iv = _iv
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc)).decode('utf8')
#==================================================================================================> AES 복호화 함수 종료


#==================================================================================================> 멀티사이트 시작
@ensure_csrf_cookie
def multisite_index(request, org):

    org = org.replace("/comm_list_json","") # <---- bugfix

    print "--------------------------> org s"
    print "org = ", org
    print request.session #u'gzc3na70yjpgc1wgga2xc96ns17q6enw'
    print "--------------------------> org e"

    print "---------------------> request.GET.get('pass')"
    if request.GET.get('pass'):
        print request.GET.get('pass')
    print "---------------------> request.GET.get('pass')"

    if 'status' not in request.session or request.session['status'] != 'success':
        request.session['status'] = None

    if 'status_org' in request.session and request.session['status_org'] != org:
        request.session['status'] = 'fail'

    print "=============================> xxx"
    print request.session['status']
    print "=============================> xxx"

    if 'social_auth_last_login_backend' in request.session:
        request.session['status'] = 'success'

    if request.session['status'] == None or request.session['status'] == 'fail':
        # 방식 구분 로직 ( 파라미터전송 / Oauth )
        with connections['default'].cursor() as cur:
            sql = '''
            SELECT login_type, site_url, Encryption_key
            FROM multisite
            where site_code = '{0}'
            '''.format(org)

            print sql

            cur.execute(sql)
            rows = cur.fetchall()
            login_type = rows[0][0]
            out_url = rows[0][1]
            key = rows[0][2]
            iv = rows[0][2]

        print "---------------------------------->s"
        print "login_type = ", login_type
        print "---------------------------------->e"

        # 공통 로직 (URL 체크)
        if 'HTTP_REFERER' in request.META:
            in_url = request.META['HTTP_REFERER']
        else:
            in_url = ''

        print "---------------------------------->s"
        print 'in_url (before) = ', in_url
        print "---------------------------------->e"

        in_url = in_url.replace('http://',"")
        in_url = in_url.replace('www.',"")

        out_url = out_url.replace('http://',"")
        out_url = out_url.replace('http://',"")

        print "---------------------------------->s"
        print 'in_url (after) = ', in_url
        print "---------------------------------->e"
        print "---------------------------------->s"
        print 'out_url (after) = ', out_url
        print "---------------------------------->e"

        if in_url != out_url:
            print "---------------------------------->s"
            request.session['status'] = 'fail'
            print "request.session['status'] = ", request.session['status']
            print "---------------------------------->e"

        # URL이 일치하면 타는 로직
        else:
            print "URL check 종료 ---------------------------->"

            # 파라미터 전송 타입
            if login_type == 'P':
                # 암호화 데이터 복호화 로직
                if request.GET.get('encStr'):
                    encStr = request.GET.get('encStr')

                    print "-------------------------------> encStr s"
                    print "encStr = ", encStr
                    print "-------------------------------> encStr e"

                    raw_data = decrypt(key, iv, encStr) #<--------------- 복호화 제대로 안됬을 때 예외 처리
                    raw_data = raw_data.split('&')

                    print "-------------------------------> encStr s"
                    print "raw_data = ", raw_data
                    print "-------------------------------> encStr e"

                    t1 = raw_data[0].split('=')
                    t2 = raw_data[1].split('=')
                    t3 = raw_data[2].split('=')
                    calltime = t1[1]
                    userid = t2[1]
                    orgid = t3[1]

                    calltime = str(calltime)

                    t_a = int(calltime[0:4])
                    t_b = int(calltime[4:6])
                    t_c = int(calltime[6:8])
                    t_d = int(calltime[8:10])
                    t_e = int(calltime[10:12])
                    t_f = int(calltime[12:14])

                    java_calltime = datetime(t_a, t_b, t_c, t_d, t_e, t_f)
                    python_calltime = datetime.utcnow() + timedelta(hours=9)

                    print "----------------------------- call time check s"
                    print "java_calltime = ",java_calltime
                    print "python_calltime = ",python_calltime
                    print "----------------------------- call time check e"

                    #(datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")

                    if java_calltime + timedelta(seconds=60) < python_calltime:
                        request.session['status'] = 'fail'
                        print "######################## fail logic - 1"
                        print " ---------------------------> status s inner time"
                        print request.session['status']
                        print " ---------------------------> status e inner time"

                    print "--------------------------->"
                    print "calltime ja = ", java_calltime
                    print "calltime py = ", python_calltime
                    print "calltime ja + 1 = ", java_calltime + timedelta(seconds=60)
                    print "userid = ", userid
                    print "orgid = ", orgid
                    print "--------------------------->"

                    if org != orgid:
                        request.session['status'] = 'fail'
                        print "######################## fail logic - 2"
                        print " ---------------------------> status s inner org"
                        print request.session['status']
                        print " ---------------------------> status e inner org"

                    if request.session['status'] != 'fail':
                        print "------------------------------------==========> success"
                        request.session['multisite_userid'] = userid
                        request.session['status'] = 'success'
                        request.session['status_org'] = org

                        with connections['default'].cursor() as cur:
                            sql = '''
                                SELECT user_id
                                FROM multisite_member as a
                                join multisite as b
                                on a.site_id = b.site_id
                                where site_code = '{0}'
                                and org_user_id = '{1}'
                            '''.format(org, userid)

                            print sql

                            cur.execute(sql)
                            rows = cur.fetchall()

                        print "----------------------------========> rows s"
                        print rows
                        print len(rows)
                        print "----------------------------========> rows e"

                        if len(rows) != 0:
                            from django.contrib.auth.models import User
                            user = User.objects.get(pk=rows[0][0])

                            print "********************************* s"
                            print user.pk
                            print "********************************* s"

                            user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
                            login(request, user)

                        print " ---------------------------> status s inner last"
                        print request.session['status']
                        print " ---------------------------> status e inner last"

            elif login_type == 'O':
                print "------------------> O"
                print "------------------> O"
                print "------------------> O"
                url = 'http://devstack.kr:8000/auth/login/google-plus/?auth_entry=login&next=%2Fmultisite%2F'+org+'%2F'
                return HttpResponseRedirect(url)

    # ----- i want data query ----- #
    with connections['default'].cursor() as cur:
        sql = '''
            SELECT logo_img, site_url
            FROM   edxapp.multisite
            WHERE  site_code = '{0}'
        '''.format(org)

        print sql

        cur.execute(sql)
        return_table = cur.fetchall()

    try:
        logo_img = return_table[0][0]
        site_url = return_table[0][1]

    except BaseException:
        org = 'kmooc'
        logo_img = ''
        site_url = ''
    # ----- i want data query ----- #

    # session up
    request.session['org'] = org
    request.session['logo_img'] = logo_img
    request.session['site_url'] = site_url

    # basic logic
    if request.user.is_authenticated():
        if configuration_helpers.get_value(
                'ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER',
                settings.FEATURES.get('ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER', True)):
            pass
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from external_auth.views import ssl_login
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
    if domain and 'edge.edx.org' in domain:
        return redirect(reverse("signin_user"))

    return student.views.multisite_index(request, user=request.user)
#==================================================================================================> 멀티사이트 종료


#==================================================================================================> 멀티사이트 테스트 시작
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode

def multisite_test(request, org=None):

    if 'HTTP_REFERER' in request.META:
        in_url = request.META['HTTP_REFERER']
    else:
        in_url = ''

    if not org:
        return redirect('/')

    key = '1234567890123456'
    iv = '1234567890123456'
    encStr = request.GET.get('encStr')

    if encStr:
        request.session['send_id'] = decrypt(key, iv, encStr)
        request.session['referer'] = in_url
        return redirect('/multisite_test2')
    else:
        return redirect('/')

def multisite_test2(request):
    if not 'send_id' in request.session or not 'referer' in request.session:
        return redirect('/')

    context = {
        'send_id': request.session['send_id'],
        'referer': request.session['referer']
    }
    return render_to_response("multisite_test.html", context)
#==================================================================================================> 멀티사이트 테스트 종료


@ensure_csrf_cookie
def index(request):
    '''
    Redirects to main page -- info page if user authenticated, or marketing if not
    '''

    request.session['org'] = 'kmooc'

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
