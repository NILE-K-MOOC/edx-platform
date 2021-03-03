# -*- coding: utf-8 -*-
import logging
import urllib
import json
import datetime
import uuid
import urllib2
from pytz import timezone
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
from third_party_auth.decorators import xframe_allow_whitelisted
import requests
from django.contrib import messages


log = logging.getLogger(__name__)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
    ]

def cb_course_list(request):

    cb_course_cert = ''

    if 'cb_course_cert' in request.session:
        cb_course_cert = request.session['cb_course_cert']
        del request.session['cb_course_cert']

    context = {
        'user_id': request.user.id,
        'username': request.user.username,
        'cb_course_cert': cb_course_cert
    }

    return render_to_response('community/cb_course_list.html', context)


def cb_print(request, course_id):

    # url 직접 입력 후 접근 시 발생하는 버그 수정
    # 정상 "7"
    # 비정상 "7/images/bg.png"
    course_id = course_id.replace("/images/bg.png", "")

    # 1. 사용자 아이디 로드 및 이수증 고유번호 생성
    user_id = request.user.id

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "course_id -> ", course_id
    print "user_id -> ", user_id
    print "--------------------------------------------"

    # 2. 로그인 유효성 검증
    if user_id == None:
        return redirect('/login')

    # 3. 이름, 생년월일, 본인인증여부, 본인인증데이터 불러오기
    with connections['default'].cursor() as cur:
        query = '''
            select b.name, b.year_of_birth, 
            case 
            when c.id is null
            then 'N'
            when c.id is not null
            then 'Y'
            end as nice, plain_data
            from auth_user a
            join auth_userprofile b
            on a.id = b.user_id
            left join auth_user_nicecheck c
            on a.id = c.user_Id
            where a.id = '{user_id}';
        '''.format(user_id=user_id)
        cur.execute(query)
        user_data = cur.fetchall()

    try:
        user_name = user_data[0][0]   # 'kim hangil'
        user_birth = user_data[0][1]  # '1990'
        user_nice = user_data[0][2]   # 'N' or 'Y'
    except BaseException as err:
        print "user data parsing error detail : ", err
        return redirect('/dashboard')

    if user_nice == 'N':
        with connections['default'].cursor() as cur:
            query = '''
                SELECT 
                    user_id, name, is_kakao, date_of_birth
                FROM
                    tb_auth_user_addinfo
                WHERE
                    user_id = '{user_id}';
            '''.format(user_id=user_id)
            cur.execute(query)
            user_kakao_data = cur.fetchone()

        is_kakao = user_kakao_data[2]

        if is_kakao == 'Y':
            user_name = user_kakao_data[1]
            user_birth = user_kakao_data[3]

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "user_name -> ", user_name
    print "user_birth-> ", user_birth
    print "user_nice -> ", user_nice
    print "--------------------------------------------"

    # 본인인증이 되어있다면 본인인증데이터 불러오기
    if user_nice == 'Y':
        try:
            pd = user_data[0][3]
            pd = json.loads(pd)
            user_name = urllib2.unquote(str(pd['UTF8_NAME'])).decode('utf8')
            pd = pd['BIRTHDATE']
            pd = pd[0:4] + '.' + pd[4:6] + '.' + pd[6:8]
            user_birth = pd
        except BaseException as err:
            print "user data parsing error (2) detail : ", err
            return redirect('/dashboard')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "user_name -> ", user_name
    print "user_birth-> ", user_birth
    print "--------------------------------------------"

    # 4. 이수증 출력일시 날짜 포맷 변경
    # ex) 2019.11.27 16:34:38
    kst = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m.%d %H:%M:%S')
    # ex) 2019.11.27
    kst_short = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m.%d')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "kst -> ", kst
    print "kst_short -> ", kst_short
    print "--------------------------------------------"

    # 5. 강좌 전체 정보
    with connections['default'].cursor() as cur:
        query = '''
            SELECT 
                display_name,
                professor_name,
                org,
                weeks,
                credit,
                DATE_FORMAT(start, '%Y-%m-%d') AS start,
                DATE_FORMAT(end, '%Y-%m-%d') AS end,
                org_image
            FROM
                cb_course
            WHERE
                course_id = '{course_id}';
        '''.format(course_id=course_id)
        cur.execute(query)
        course_data = cur.fetchall()

    print query

    if len(course_data) == 0:

        request.session['cb_course_cert'] = 'Y'
        print "course_data is 0"
        return redirect('/cb_course_list')
    else:
        course_data = course_data[0]

    context = {}
    context['user_name'] = user_name
    context['user_birth'] = str(user_birth) + '.'
    context['user_nice'] = user_nice
    context['user_kakao'] = is_kakao
    context['kst'] = kst
    context['display_name'] = course_data[0]
    context['professor_name'] = course_data[1]
    context['org'] = course_data[2]
    context['weeks'] = course_data[3]
    context['credit'] = course_data[4]
    context['start'] = course_data[5]
    context['end'] = course_data[6]
    context['org_image'] = course_data[7]

    date_format = str(datetime.datetime.now()).split(" ")[0]
    now_date = date_format.replace("-", ".")

    context['regist_date'] = now_date

    return render_to_response('community/cb_print.html', context)


def cb_course(request):

    user_id = request.user.id
    username = request.user.username

    print "--------------------------"
    print "user_id = ", user_id
    print "user_id = ", user_id
    print "--------------------------"

    try:
        r = requests.post('https://cb.kmooc.kr/api/v1/external/certificates', data={'user_id': username, 'uid': user_id})
        return JsonResponse({'result': r.json()})
    except:
        return JsonResponse({'result': 'fail'})

    # with connections['default'].cursor() as cur:
    #     query = '''
    #         select  x.course_id,
    #                 y.display_name,
    #                 y.course_image,
    #                 y.professor_name,
    #                 y.org,
    #                 y.major_category,
    #                 y.weeks,
    #                 y.credit,
    #                 Date_format(y.start, '%y.%m.%d. ') as start,
    #                 Date_format(y.end, '%y.%m.%d. ') as end,
    #                 x.attendance,
    #                 x.score
    #         from cb_course_enroll x
    #         join cb_course y
    #         on x.course_id = y.course_id
    #         where user_id = '{user_id}'
    #         and x.delete_yn = 'N';
    #     '''.format(user_id=user_id)
    #     cur.execute(query)
    #     rows = dictfetchall(cur)
    #
    # print "--------------------------"
    # print "rows = ", rows
    # print "--------------------------"




def common_course_status(startDt, endDt):
    # input
    # startDt = 2016-12-19 00:00:00
    # endDt   = 2017-02-10 23:00:00
    # nowDt   = 2017-11-10 00:11:28

    # import
    from datetime import datetime

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


def course_api(request):
    # mysql
    cur = connections['default'].cursor()

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
               coa.teacher_name,
               coa.classfy,
               coa.middle_classfy
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

    item_list = list()

    # making data (insert)
    for item in slist:
        """
        course_id
        display_name
        univ_name
        start_time
        end_time
        enroll_start
        enroll_end
        created
        modified
        video
        img
        org
        course
        run
        effort
        e0 권장학습시간
        e1 주차
        e2 학습인정시간
        et 동영상 재생시간
        classfy
        middle_classfy
        cert_date
        teacher_name
        """

        item_dict = dict()

        item_dict['course_id'] = item[0]
        item_dict['display_name'] = item[1]
        item_dict['univ_name'] = unicode(item[10]).strip()
        item_dict['start_time'] = str(item[2]) if item[2] is not None and item[2] != '' else None
        item_dict['end_time'] = str(item[3]) if item[3] is not None and item[3] != '' else None
        item_dict['enroll_start'] = str(item[4]) if item[4] is not None and item[4] != '' else None
        item_dict['enroll_end'] = str(item[5]) if item[5] is not None and item[5] != '' else None
        item_dict['created'] = str(item[6]) if item[6] is not None and item[6] != '' else None
        item_dict['modified'] = str(item[7]) if item[7] is not None and item[7] != '' else None
        item_dict['video'] = item[8]
        item_dict['img'] = 'http://www.kmooc.kr' + item[9]
        item_dict['org'] = item[11]
        item_dict['course'] = item[12]
        item_dict['run'] = item[13]
        item_dict['effort'] = item[14]

        effort_dict = effort_make_available(item[14] if item[14] is not None else '00:00@00#00:00$00:00')

        item_dict['e0'] = effort_dict['w_time']  # 권장학습시간
        item_dict['e1'] = effort_dict['week']  # 주차
        item_dict['e2'] = effort_dict['l_time']  # 학습인정시간
        item_dict['et'] = effort_dict['v_time']  # 동영상 재생시간
        item_dict['classfy'] = item[17]
        item_dict['middle_classfy'] = item[18]
        item_dict['cert_date'] = str(item[15]) if item[15] is not None and item[15] != '' else None
        item_dict['teacher_name'] = item[16] if item[16] != '' else ''

        item_list.append(item_dict)

        # api 항목에 없어서 현재 사용 X
        status = common_course_status(item[2], item[3])  # 강좌상태

    result = {
        'results': item_list,
        'total_cnt': len(slist)
    }

    item_json = json.dumps(result, ensure_ascii=False, encoding='utf-8')

    return HttpResponse(item_json)
