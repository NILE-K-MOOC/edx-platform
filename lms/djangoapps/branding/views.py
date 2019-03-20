#-*- coding: utf-8 -*-
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

import pymongo
from pymongo import MongoClient
from bson import ObjectId

log = logging.getLogger(__name__)


def common_course_status(startDt, endDt):

    #input
    # startDt = 2016-12-19 00:00:00
    # endDt   = 2017-02-10 23:00:00
    # nowDt   = 2017-11-10 00:11:28

    #import
    from datetime import datetime

    #making nowDt
    nowDt = datetime.now().strftime("%Y-%m-%d-%H-%m-%S")
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
    # conn = pymysql.connect(host='docker.for.mac.localhost',
    #                        user='edxapp001',
    #                        password='password',
    #                        db='edxapp',
    #                        charset='utf8')
    conn = connections['default'].cursor()

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

    err_cnt = 0
    # making data (insert)
    for item in slist:
        #mongo
        client = MongoClient('docker.for.mac.localhost', 27017)
        db = client["edxapp"]
        cursor = db.modulestore.active_versions.find_one({'org': item[11], 'course': item[12], 'run': item[13]})

        print "org -> ", item[11]
        print "course -> ", item[12]
        print "run -> ", item[13]

        try:
            pb = cursor.get('versions').get('published-branch')
        except BaseException:
            err_cnt += 1
            continue
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

        print "item[14] -> ", item[14]

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
    for n in range(0, len(slist)-err_cnt):
        item = '{' + '"course_id":' + '"' + str(course_id_list[n])  + '"' +  ',' + '"display_name":'  + '"' +  unicode(display_name_list[n])  + '"' +  ',' + '"univ_name":'  + '"' +  unicode(univ_name_list[n])  + '"' +  ',' + '"start_time":'  + '"' +  str(start_time_list[n])  + '"' +  ',' + '"end_time":'  + '"' +  str(end_time_list[n])  + '"' +  ',' + '"enroll_start":'  + '"' +  str(enroll_start_list[n])  + '"' +  ',' + '"enroll_end":'  + '"' +  str(enroll_end_list[n])  + '"' +  ',' + '"created":'  + '"' +  str(created_list[n])  + '"' +  ',' + '"modified":'  + '"' +  str(modified_list[n])  + '"' +  ',' + '"video":'  + '"' +  str(video_list[n])  + '"' +  ',' + '"img":'  + '"' +  str(img_list[n])  + '"' +  ',' + '"org":'  + '"' +  str(org_list[n])  + '"' +  ',' + '"course":'  + '"' +  str(course_list[n])  + '"' +  ',' + '"run":'  + '"' +  str(run_list[n])  + '"' +  ',' + '"e0":'  + '"' +  str(e0_list[n])  + '"' +  ',' + '"e1":'  + '"' +  str(e1_list[n])  + '"' +  ',' + '"e2":'  + '"' +  str(e2_list[n])  + '"' +  ',' + '"et":'  + '"' +  str(et_list[n])  + '"' +  ',' + '"course_status":'  + '"' +  str(course_status_list[n])  + '"' +  ',' + '"classfy":'  + '"' +  str(classfy_list[n])  + '"' +  ',' + '"middle_classfy":'  + '"' +  str(middle_classfy_list[n])  + '"' +  ',' + '"cert_date":'  + '"' +  str(cert_date_list[n])  + '"' +  ',' + '"teacher_name":'  + '"' +  str(teacher_name_list[n])  + '"' +  '}'
        if n == 0:
            item = "[" + item + ","
        elif n == len(slist)-1:
            item = item + "," + '{"total_cnt":"' + str(len(slist)) + '"}' + ']'
        else:
            item = item + ','
        json_list.append(item)

    return HttpResponse(json_list)


#==================================================================================================> login 오버라이딩 시작
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

def multisite_error(request):
    context = {}

    error = request.GET.get('error')

    print "error -> ", error

    if error == 'error001':
        context['info'] = '유효하지않은 org(기관번호) 입니다.'
    if error == 'error002':
        context['info'] = 'in_url(접근URL)과 out_url(등록URL)이 일치하지 않습니다.'
    if error == 'error003':
        context['info'] = '암호화 데이터를 복호화하는데 실패하였습니다.'
    if error == 'error004':
        context['info'] = '복호화 데이터 파싱에 실패하였습니다.'
    if error == 'error005':
        context['info'] = '호출시간이 만료되었습니다'
    if error == 'error006':
        context['info'] = '접속한 org(기관번호)와 복호화된 orgid(기관번호)가 일치하지 않습니다.'
    if error == 'error007':
        context['info'] = '기관연계 되지 않은 사번입니다.'

    return render_to_response("multisite_error.html", context)

def multisite_index(request, org):

    print "org -> ", org
    print "------------------------------------"

    # 멀티사이트에 온 것을 환영합니다
    request.session['multisite_mode'] = 1
    request.session['multisite_org'] = org

    print "request.session['multisite_mode'] -> ", request.session['multisite_mode']
    print "request.session['multisite_org'] -> ", request.session['multisite_org']
    print "------------------------------------"

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
        SELECT login_type, site_url, Encryption_key
        FROM multisite
        where site_code = '{0}'
        '''.format(org)
        cur.execute(sql)
        rows = cur.fetchall()
        try:
            login_type = rows[0][0]
            out_url = rows[0][1]
            key = rows[0][2]
        except BaseException:
            return redirect('/multisite_error?error=error001')

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
    in_url = in_url.replace('http://',"")
    in_url = in_url.replace('www.',"")
    out_url = out_url.replace('http://', "")
    out_url = out_url.replace('www.',"")

    # DEBUG
    print 'in_url -> ', in_url
    print 'out_url -> ', out_url
    print "------------------------------------"

    # 접근URL 과 등록URL 비교
    if out_url == 'passkey':
        pass
    else:
        if in_url.find(out_url) == -1:
            return redirect('/multisite_error?error=error002')

    # 파라미터 방식
    if login_type == 'P':
        # 암호화 데이터 (get, post 구분 없음)
        if request.GET.get('encStr') or request.POST.get('encStr'):
            if request.GET.get('encStr'):
                encStr = request.GET.get('encStr')
            elif request.POST.get('encStr'):
                encStr = request.POST.get('encStr')

        # DEBUG
        encStr = 'HMSFfWYS/NSUE93/Ra7TfEWuBhTPy9XZiHJoeD+QV+mMVgEEb9ezJ4OyYuDlwuNG'
        print 'encStr -> ', encStr

        # 암호화 데이터 복호화
        encStr = encStr.replace(' ', '+')

        try:
            raw_data = decrypt(key, key, encStr)
            raw_data = raw_data.split('&')
        except BaseException:
            return redirect('/multisite_error?error=error003')

        # DEBUG
        print 'raw_data -> ', raw_data
        print "------------------------------------"

        # 복호화 데이터 파싱
        try:
            calltime = raw_data[0].split('=')[1]
            userid = raw_data[1].split('=')[1]
            orgid = raw_data[2].split('=')[1]
        except BaseException:
            return redirect('/multisite_error?error=error004')

        # DEBUG
        print 'calltime -> ', calltime
        print 'userid -> ', userid
        print 'orgid -> ', orgid
        print "------------------------------------"

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
        print 'java_calltime -> ', java_calltime
        print 'python_calltime -> ', python_calltime
        print "------------------------------------"

        # 호출시간 만료 체크
        #if java_calltime + timedelta(seconds=180) < python_calltime:
        #    return redirect('/multisite_error?error=error005')

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

        print 'len(rows) -> ', len(rows)

        # 기관연계 된 회원이라면 SSO 로그인
        if len(rows) != 0:
            user = User.objects.get(pk=rows[0][0])
            user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
            login(request, user)

            if zero_mode == 0:
                request.session['multisite_zero'] = 1
                return redirect('/')
        # 아니라면 에러페이지 리다이렉트
        else:
            request.session['multisite_userid'] = userid
            return redirect('/login')

    # Oauth 방식
    elif  login_type == 'O':
        pass

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

@csrf_exempt
def get_org_value(request):

    org = request.POST.get('org')
    user_id = request.user.id

    print "### org -> ", org

    with connections['default'].cursor() as cur:
        sql = '''
            select b.org_user_id
            from multisite a
            join multisite_member b
            on a.site_id = b.site_id
            where site_name = '{org}'
            and b.user_id = '{user_id}';
        '''.format(org=org, user_id=user_id)

        print sql
        cur.execute(sql)
        org_user_id = cur.fetchall()[0][0]

    return JsonResponse({'result':org_user_id})


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

    # 패키지 강좌 목록 조회
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
            # 패키지 강좌 이수 개수
            sql1 = '''
                select sum(result)
                from (
                select x.org, x.display_number_with_default, case when y.status is not null then sum(1) when y.status is null then sum(0) end as result
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
                and b.status = 'downloadable'
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

            # 패키지 강좌 진행 개수
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
                      and end > now()
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

            # 패키지 강좌 총 개수
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
        tmp_dict['is_noing'] = is_total - (is_ing + is_cert)
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
# @cache_if_anonymous() <- 캐시는 개발자의 적이다. 사용자가 피해를 보더라도 개발자는 살자
def index(request):
    """
    Redirects to main page -- info page if user authenticated, or marketing if not
    """

    # 멀티사이트 인덱스에서 더럽혀진 영혼을 정화하는 구간입니다.
    # 치유의 빛이 흐릿하게 빛나며 더럽혀진 영혼이 정화됩니다.
    if 'multisite_mode' in request.session:
        del request.session['multisite_mode']

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
