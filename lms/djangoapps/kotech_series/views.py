# -*- coding: utf-8 -*-
import json
import pymongo
import logging
import urllib
import branding.api as branding_api
import courseware.views.views
import student.views.management
import uuid
import MySQLdb as mdb
import sys
import re
import os.path
import datetime
import urllib2

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from django.db import models, connections
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest
from django.shortcuts import redirect
from django.utils import translation
from django.utils.translation.trans_real import get_supported_language_variant
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from openedx.core.djangoapps.lang_pref.api import released_languages
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from student.views.dashboard import effort_make_available
from edxmako.shortcuts import marketing_link, render_to_response

from util.cache import cache_if_anonymous
from util.json_request import JsonResponse

from urlparse import urlparse, parse_qs

from pymongo import MongoClient
from bson import ObjectId

from datetime import timedelta
from pytz import timezone


def new_dashboard(request):
    user_id = request.user.id

    # 로그인 유효성 검증
    if user_id == None:
        return redirect('/login')

    # 패키지 강좌 목록 조회
    with connections['default'].cursor() as cur:
        sql = '''
            select y.series_seq, y.series_id, y.series_name, y.save_path, y.detail_name
            from series_student x
            join (
                select a.series_seq, a.series_id, a.series_name, b.save_path, b.ext, c.detail_name
                from series a
                left join tb_attach b
                on a.sumnail_file_id = id
                join code_detail c
                on a.org = c.detail_code
                where c.group_code = '003'
                and a.use_yn = 'Y'
            ) y
            on x.series_seq = y.series_seq
            where x.user_id = '{user_id}'
            and x.delete_yn = 'N';
        '''.format(user_id=user_id)

        print sql
        cur.execute(sql)
        temps = cur.fetchall()

    # 각 패키지 강좌에 대해 필요 정보 추출
    # 1. 패키지 강좌 이수 개수
    # 2. 패키지 강좌 진행 개수
    # 3. 패키지 강좌 총 개수
    # 4. 패키지 강좌 잔여 개수
    packages = []
    for temp in temps:
        tmp_dict = {}
        tmp_dict['series_seq'] = temp[0]
        tmp_dict['series_id'] = temp[1]
        tmp_dict['series_name'] = temp[2]
        save_path = temp[3]

        # 운영 서버 파일 서브 경로 변경
        try:
            save_path = save_path.replace('/static/upload/', '/static/file_upload/series/')
        except AttributeError:
            save_path = None

        tmp_dict['save_path'] = save_path
        tmp_dict['save_path'] = save_path
        tmp_dict['detail_name'] = temp[4]

        with connections['default'].cursor() as cur:
            # 패키지 강좌 이수 개수
            sql1 = '''
                select count(*) as cert_cnt
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
                    group by org, display_number_with_default
                ) y
                on x.org = y.org
                and x.display_number_with_default = y.display_number_with_default
                where y.org is not null;
            '''.format(series_seq=temp[0], user_id=user_id)

            print sql1
            cur.execute(sql1)
            try:
                is_cert = cur.fetchall()[0][0]
            except BaseException as err:
                print "is_cert parsing error detail : ", err
                is_cert = 0

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
                    '''.format(series_seq=temp[0], user_id=user_id)

            print sql2
            cur.execute(sql2)
            try:
                is_ing = cur.fetchall()[0][0]
            except BaseException as err:
                print "is_ing parsing error detail : ", err
                is_ing = 0

            # 패키지 강좌 총 개수
            sql3 = '''
                select count(*)
                from series_course
                where series_seq = '{series_seq}'
                  and delete_yn = 'N'
                ;
            '''.format(series_seq=temp[0], user_id=user_id)

            print sql3
            cur.execute(sql3)
            try:
                is_total = cur.fetchall()[0][0]
            except BaseException as err:
                print "is_total parsing error detail : ", err
                is_total = 0

        if is_cert == None:
            is_cert = 0
        if is_ing == None:
            is_ing = 0
        if is_total == None:
            is_total = 0

        # 개발 디버깅 로그
        print "--------------------------------------------"
        print "is_cert -> ", is_cert
        print "is_ing -> ", is_ing
        print "is_total -> ", is_total
        print "--------------------------------------------"

        tmp_dict['is_total'] = is_total             # 패키지 강좌 전체 수
        tmp_dict['is_cert'] = is_cert               # 패키지 강좌 이수강좌 수
        tmp_dict['is_ing'] = is_ing                 # 패키지 강좌 진행강좌 수
        tmp_dict['is_noing'] = is_total - is_cert   # 피키지 강좌 잔여강좌 수
        packages.append(tmp_dict)

    context = {}
    context['packages'] = packages
    return render_to_response("new_dashboard.html", context)


def series_print(request, id):

    # url 직접 입력 후 접근 시 발생하는 버그 수정
    # 정상 "7"
    # 비정상 "7/images/bg.png"
    id = id.replace("/images/bg.png", "")

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "id -> ", id
    print "--------------------------------------------"

    # 1. 사용자 아이디 로드 및 이수증 고유번호 생성
    user_id = request.user.id
    cert_uuid = str(uuid.uuid4()).replace('-', '')

    # 2. 로그인 유효성 검증
    if user_id == None:
        return redirect('/login')

    # 3. 묶음 강좌 이수증 백엔드 유효성 검증
    # 프론트엔드에서 유효성 검증을 우회하는 경우를 방지한 코드입니다
    # url에 묶음강좌 아이디 입력 후 들어오는 경우를 방지합니다
    # "이수 강좌 수"와 "전체 강좌수"를 백엔드에서 다시 한번 비교합니다
    with connections['default'].cursor() as cur:
        # 패키지 강좌 이수 개수
        sql1 = '''
            select count(*) as cert_cnt
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
                group by org, display_number_with_default
            ) y
            on x.org = y.org
            and x.display_number_with_default = y.display_number_with_default
            where y.org is not null;
        '''.format(series_seq=id, user_id=user_id)
        cur.execute(sql1)
        try:
            is_cert = cur.fetchall()[0][0]
        except BaseException as err:
            print "is_cert parsing error detail : ", err
            return redirect('/new_dashboard')

        # 패키지 강좌 전체 개수
        sql2 = '''
            select count(*)
            from series_course
            where series_seq = '{series_seq}';
        '''.format(series_seq=id, user_id=user_id)
        cur.execute(sql2)
        try:
            is_total = cur.fetchall()[0][0]
        except BaseException as err:
            print "is_total parsing error detail : ", err
            return redirect('/new_dashboard')

    if is_cert == is_total:
        pass
    else:
        return redirect('/new_dashboard')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "user_id -> ", user_id
    print "cert_uuid -> ", cert_uuid
    print "--------------------------------------------"

    # 4. 묶음강좌 중 마지막으로 이수증 발급한 날짜 불러오기
    with connections['default'].cursor() as cur:
        query = '''
            select max(z.created_date)
            from (
                select org, display_number_with_default
                from series_course
                where series_seq = '{id}'
            ) x
            join course_overviews_courseoverview y
            on x.org = y.org
            and x.display_number_with_default = y.display_number_with_default
            join (
                select course_id, created_date, 'Y' as cert
                from certificates_generatedcertificate
                where user_id = '{user_id}'
                and status = 'downloadable'
            ) z
            on y.id = z.course_id;
        '''.format(id=id, user_id=user_id)
        cur.execute(query)
        try:
            cert_date = cur.fetchall()[0][0]
            # 이수증 발급한 날짜 포맷 변경
            # 2019-03-20 14:11:11 -> 2019.03.20
            cert_date = (cert_date + datetime.timedelta(hours=+9)).strftime('%Y.%m.%d')
        except BaseException as err:
            print "cert_date parsing error detail : ", err
            return redirect('/new_dashboard')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print 'cert_date -> ', cert_date
    print "--------------------------------------------"

    # 5. 묶음강좌 이수증 고유번호가 있는지 확인
    with connections['default'].cursor() as cur:
        query = '''
            select count(certificated_id)
            from series_student
            where series_seq = '{id}'
            and user_id = '{user_id}';
        '''.format(user_id=user_id, id=id)
        cur.execute(query)
        try:
            check = cur.fetchall()[0][0]
        except BaseException as err:
            print "certificated_id check error detail : ", err
            return redirect('/new_dashboard')

        # 묶음강좌 이수증 고유번호가 없다면 고유번호 업데이트
        if check == 0:
            query = '''
                update series_student
                set pass_yn = 'Y'
                , certificated_id = '{cert_uuid}'
                , certificated_date = now()
                where series_seq = '{id}'
                and user_id = '{user_id}';
            '''.format(user_id=user_id, id=id, cert_uuid=cert_uuid)
            cur.execute(query)

        # 묶음강좌 이수증 고유번호 불러오기
        query = '''
            select certificated_id, certificated_date
            from series_student
            where series_seq = '{id}'
            and user_id = '{user_id}';
        '''.format(user_id=user_id, id=id)
        cur.execute(query)
        cert_uuid = cur.fetchall()
        try:
            cert_uuid = cert_uuid[0][0]
        except BaseException as err:
            print "cert_uuid load error detail : ", err
            return redirect('/new_dashboard')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "cert_uuid -> ", cert_uuid
    print "--------------------------------------------"

    # 6. 이름, 생년월일, 본인인증여부, 본인인증데이터 불러오기
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
        user_name = user_data[0][0]     # 'kim hangil'
        user_birth = user_data[0][1]    # '1990'
        user_nice = user_data[0][2]     # 'N' or 'Y'
    except BaseException as err:
        print "user data parsing error detail : ", err
        return redirect('/new_dashboard')

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
            return redirect('/new_dashboard')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "user_name -> ", user_name
    print "user_birth-> ", user_birth
    print "--------------------------------------------"

    # 7. 이수증 출력일시 날짜 포맷 변경
    # ex) 2019.11.27 16:34:38
    kst = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m.%d %H:%M:%S')
    # ex) 2019.11.27
    kst_short = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m.%d')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "kst -> ", kst
    print "kst_short -> ", kst_short
    print "--------------------------------------------"

    # 8. 묶음강좌명, 강좌명 불러오기
    with connections['default'].cursor() as cur:
        query = '''
            select a.series_name, b.course_name
            from series a
            join series_course b
            on a.series_seq = b.series_seq
            where a.series_seq = '{id}';
            '''.format(id=id)
        cur.execute(query)
        pack = cur.fetchall()

    try:
        package_name = pack[0][0]
        package_cousre = pack
    except BaseException as err:
        print "pack parsing error detail : ", err
        return redirect('/new_dashboard')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "package_name -> ", package_name
    print "package_cousre -> ", package_cousre
    print "--------------------------------------------"

    # 9. 짧은소개, 기관 불러오기
    with connections['default'].cursor() as cur:
        query = '''
            select a.short_description, b.detail_name
            from series a
            join code_detail b
            on a.org = b.detail_code
            where a.series_seq = '{id}'
            and b.group_code = '003';
                '''.format(id=id)
        cur.execute(query)
        course_info = cur.fetchall()

    try:
        short_description = course_info[0][0]
        org = course_info[0][1]
    except BaseException as err:
        print "course_info parsing error detail : ", err
        return redirect('/new_dashboard')

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "short_description -> ", short_description
    print "org -> ", org
    print "--------------------------------------------"

    # 10. 교수자 사인 경로 불러오기
    with connections['default'].cursor() as cur:
        query = '''
            select save_path
            from tb_attach
            where group_name = '/homepage/series'
            and group_id = '{id}';
            '''.format(id=id)
        print query
        cur.execute(query)
        admin_sign = cur.fetchall()

    # 교수자 사인을 8개 이상 등록하더라도 8개만 가져옴
    admin_sign_list = []
    for n in range(0, 8):
        try:
            pro_sign_path = admin_sign[n][0]
            # pro_sign_path = pro_sign_path.replace("file_upload", "dev") # 개발용 - 경로 스니핑
            admin_sign_list.append('http://kmooc.kr' + pro_sign_path)
        except BaseException as err:
            print "admin_sign err : ", err

    # 개발 디버깅 로그
    print "--------------------------------------------"
    for admin_sign in admin_sign_list:
        print "admin_sign -> ", admin_sign
    print "--------------------------------------------"

    # 11. 사인경로 획득을 위한 "대표기관" 코드 불러오기
    with connections['default'].cursor() as cur:
        query = '''
            select org
            from series
            where series_seq = '{id}';
        '''.format(id=id)
        cur.execute(query)
        try:
            main_sign = cur.fetchall()[0][0]
        except BaseException as err:
            print "main_sign err : ", err
            main_sign = ''


    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "main_sign -> ", main_sign
    print "--------------------------------------------"

    # 12. 사인경로 획득을 위한 "참여기관" 코드 불러오기
    """
    with connections['default'].cursor() as cur:
        query = '''
            select distinct(org)
            from series_course
            where series_seq = '{id}';
        '''.format(id=id)
        cur.execute(query)
        sub_sign = cur.fetchall()

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "sub_sign -> ", sub_sign
    print "--------------------------------------------"
    """

    # 13. "대표기관", "참여기관" 사인 통합
    sign_list = []
    sign_list.append(main_sign)
    """
    for n in range(0, 3):
        try:
            sign_list.append(sub_sign[n][0])
        except BaseException as err:
            print "sign_list err : ", err
    """

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "sign_list -> ", sign_list
    print "--------------------------------------------"

    # 14. 기관 이미지 경로 불러오기
    org_img_path_list = []
    with connections['default'].cursor() as cur:
        for sign in sign_list:
            query = '''
              select save_path
              from tb_attach
              where group_name = '/logo_img'
              and group_id = '{sign}';
            '''.format(sign=sign)
            cur.execute(query)
            org_img_path = cur.fetchall()
            try:
                org_img_path = org_img_path[0][0]
                # org_img_path = org_img_path.replace("upload", "dev") # 개발용 - 경로 스니핑
                org_img_path_list.append('http://kmooc.kr' + org_img_path)
            except BaseException as err:
                print "org_img_path err : ", err
                org_img_path = ''

    # 개발 디버깅 로그
    print "--------------------------------------------"
    for org_img_path in org_img_path_list:
        print "org_img_path -> ", org_img_path
    print "--------------------------------------------"

    # 15. 강좌 리스트 (분석 필요...하드코딩 쉣!)
    with connections['default'].cursor() as cur:
        query = '''
            select display_name, start, end, created_date, effort, org, display_number_with_default, teacher_name
            from (
                select y.org, y.display_number_with_default, y.display_name, y.start, y.end, z.created_date, effort, teacher_name
                from (
                    select org, display_number_with_default
                    from series_course
                    where series_seq = '{id}'
                ) x
                join (
                    select x.id, x.org, x.display_number_with_default, x.display_name, x.start, x.end, x.effort, y.teacher_name
                    from course_overviews_courseoverview x
                    join course_overview_addinfo y
                    on x.id = y.course_id
                    group by x.org, x.display_number_with_default
                ) y
                on x.org = y.org
                and x.display_number_with_default = y.display_number_with_default
                join (
                    select course_id, created_date, 'Y' as cert
                    from certificates_generatedcertificate
                    where user_id = '{user_id}'
                    and status = 'downloadable'
                    order by created_date desc
                ) z
                on y.id = z.course_id
            ) w 
            group by org, display_number_with_default;
        '''.format(id=id, user_id=user_id)
        cur.execute(query)
        row4 = cur.fetchall()

    e2_total = 0
    e3_tmp_front = 0
    e3_tmp_back = 0
    e4_tmp_front = 0
    e4_tmp_back = 0
    e3_total = None
    e4_total = None
    ppp_list = []
    for r4 in row4:
        tmp = {}
        teacher_name = r4[7]
        teacher_name_list = teacher_name.split(',')
        if len(teacher_name_list) > 1:
            teacher_name = teacher_name_list[0] + '외 ' + str(len(teacher_name_list)-1) + '명'
        else:
            teacher_name = teacher_name
        tmp['teacher_name'] = teacher_name
        tmp['display_name'] = r4[0]
        tmp['start'] = (r4[1] + datetime.timedelta(hours=+9)).strftime('%Y.%m.%d')
        tmp['end'] = (r4[2] + datetime.timedelta(hours=+9)).strftime('%Y.%m.%d')
        ccc = r4[3] + datetime.timedelta(hours=+9)
        # ccc = ccc.strftime('%Y.%m.%d %H:%M:%S')
        ccc = ccc.strftime('%Y.%m.%d')
        tmp['cert'] = ccc
        effort = r4[4]
        effort = effort.split('@')
        e1 = effort[0]
        effort = effort[1].split('#')
        e2 = effort[0]
        effort = effort[1].split('$')
        e3 = effort[0]
        e4 = effort[1]
        e2_total += int(e2)
        e3s = e3.split(':')
        e3_tmp_front += int(e3s[0])
        e3_tmp_back += int(e3s[1])
        e4s = e4.split(':')
        e4_tmp_front += int(e4s[0])
        e4_tmp_back += int(e4s[1])
        tmp['e1'] = e1
        tmp['e2'] = int(e2)
        e333 = e3.split(':')
        e3 = str(e333[0]) + '시간 ' + str(e333[1]) + '분'
        e444 = e4.split(':')
        e4 = str(e444[0]) + '시간 ' + str(e444[1]) + '분'
        tmp['e3'] = e3
        tmp['e4'] = e4
        ppp_list.append(tmp)
    e3_front = e3_tmp_front + e3_tmp_back / 60
    e3_back = e3_tmp_back % 60
    e3_total = str(e3_front) + '시간 ' + str(e3_back) + '분'
    e4_front = e4_tmp_front + e4_tmp_back / 60
    e4_back = e4_tmp_back % 60
    e4_total = str(e4_front) + '시간 ' + str(e4_back) + '분'

    # 16. 기관 연계 리스트
    with connections['default'].cursor() as cur:
        query = '''
            select site_name
            from multisite_member a
            join multisite b
            on a.site_id = b.site_id
            where user_id = '{user_id}';
        '''.format(user_id=user_id, id=id)
        cur.execute(query)
        org_list = cur.fetchall()

    # 개발 디버깅 로그
    print "--------------------------------------------"
    print "org_list -> ", org_list
    print "--------------------------------------------"

    # 개발 스니핑
    # org_img_path_list = ['http://www.kmooc.kr/static/file_upload/KoreaUnivK.png']

    context = {}
    context['user_name'] = user_name
    context['user_birth'] = str(user_birth) + '.'
    context['user_nice'] = user_nice
    context['kst'] = kst
    context['package_name'] = package_name
    context['package_cousre'] = package_cousre
    context['short_description'] = short_description
    context['main_org'] = org
    context['ppp_list'] = ppp_list
    context['e2_total'] = e2_total
    context['e3_total'] = e3_total
    context['e4_total'] = e4_total
    context['cert_uuid'] = cert_uuid
    context['cert_date'] = cert_date
    context['org_img_path_list'] = org_img_path_list
    context['admin_sign_list'] = admin_sign_list
    context['org_list'] = org_list
    return render_to_response('community/series_print.html', context)


def series(request):
    """
    수정시 mobile_series도 함께 수정 필요
    """
    with connections['default'].cursor() as cur:
        query = '''
            SELECT a.series_seq,
                   a.series_name,
                   ifnull(b.save_path, ''),
                   ifnull(c.detail_name, '-'),
                   ifnull(a.short_description, ''),
                   ifnull(a.org, ''),
                   ifnull(series_cnt, 0)
              FROM edxapp.series AS a
                   LEFT JOIN edxapp.tb_attach AS b
                      ON a.sumnail_file_id = b.id AND b.use_yn = TRUE
                   LEFT JOIN code_detail c
                      ON a.org = c.detail_code AND group_code = '003'
                   LEFT JOIN
                   (  SELECT count(series_course_id) series_cnt,
                             series_course_id,
                             series_seq
                        FROM series_course d
                       WHERE delete_yn = 'N'
                    GROUP BY d.series_seq) e
                      ON a.series_seq = e.series_seq
             WHERE a.use_yn = 'Y' AND a.delete_yn = 'N';
        '''
        cur.execute(query)
        rows = cur.fetchall()
        series_list = list()
    try:
        for row in rows:
            row_dict = dict()
            row_dict['series_seq'] = row[0]
            row_dict['series_name'] = row[1]
            row_dict['save_path'] = row[2]
            row_dict['detail_name'] = row[3]
            row_dict['short_description'] = row[4]
            row_dict['org'] = row[5]
            row_dict['series_cnt'] = row[6]
            row_dict['logo_path'] = ''
            series_list.append(row_dict)
    except Exception as e:
        print e

    context = {}
    context['series_list'] = series_list
    return render_to_response('community/series.html', context)


def mobile_series(request):
    with connections['default'].cursor() as cur:
        query = '''
            SELECT a.series_seq,
                   a.series_name,
                   ifnull(b.save_path, ''),
                   ifnull(c.detail_name, '-'),
                   ifnull(a.short_description, ''),
                   ifnull(a.org, ''),
                   ifnull(series_cnt, 0)
              FROM edxapp.series AS a
                   LEFT JOIN edxapp.tb_attach AS b
                      ON a.sumnail_file_id = b.id AND b.use_yn = TRUE
                   LEFT JOIN code_detail c
                      ON a.org = c.detail_code AND group_code = '003'
                   LEFT JOIN
                   (  SELECT count(series_course_id) series_cnt,
                             series_course_id,
                             series_seq
                        FROM series_course d
                       WHERE delete_yn = 'N'
                    GROUP BY d.series_seq) e
                      ON a.series_seq = e.series_seq
             WHERE a.use_yn = 'Y' AND a.delete_yn = 'N';
        '''
        cur.execute(query)
        rows = cur.fetchall()
        series_list = list()
    try:
        for row in rows:
            row_dict = dict()
            row_dict['series_seq'] = row[0]
            row_dict['series_name'] = row[1]
            row_dict['save_path'] = row[2]
            row_dict['detail_name'] = row[3]
            row_dict['short_description'] = row[4]
            row_dict['org'] = row[5]
            row_dict['series_cnt'] = row[6]
            row_dict['logo_path'] = ''
            series_list.append(row_dict)
    except Exception as e:
        print e

    context = {}
    context['series_list'] = series_list
    context['mobile_template'] = 'community/mobile_series'
    context['mobile_title'] = 'Series Course'
    context['series_base'] = settings.ENV_TOKENS.get('LMS_BASE') + '/series_view/'
    return render_to_response('mobile_main.html', context)


def series_about(request, id):
    with connections['default'].cursor() as cur:
        query = '''
            SELECT note
            FROM series
            WHERE series_seq = {id};
        '''.format(id=id)
        cur.execute(query)
        note = cur.fetchone()
        return JsonResponse({'note': str(note[0].encode("utf-8"))})


def series_view(request, id):
    user_id = request.user.id if request.user.id is not None else ''
    with connections['default'].cursor() as cur:
        query = '''
            SELECT a.series_name,
               a.series_id,
               a.note,
               ifnull(b.save_path, ''),
               c.detail_name,
               ifnull(a.short_description, '')
            FROM series as a
            LEFT JOIN tb_attach AS b
                ON a.sumnail_file_id = b.id
            LEFT JOIN code_detail c
                ON a.org = c.detail_code AND c.group_code = '003'
            WHERE  a.series_seq = {}
        '''.format(id)
        cur.execute(query)
        rows = cur.fetchall()
        main_list = rows[0]

    with connections['default'].cursor() as cur:
        query = '''
            SELECT IFNULL(effort, 0) effort
                  FROM (SELECT org,
                               display_number_with_default,
                               id,
                               effort,
                               start
                          FROM edxapp.course_overviews_courseoverview a) ab
                          JOIN
                           (  SELECT max(start) AS max_start, m1.org, display_number_with_default
                                FROM course_overviews_courseoverview m1
                            GROUP BY m1.org, m1.display_number_with_default) max
                              ON     ab.org = max.org
                                 AND ab.display_number_with_default =
                                     max.display_number_with_default
                                 AND ab.start = max.max_start
                 WHERE (ab.org, ab.display_number_with_default) IN
                          (SELECT org, display_number_with_default
                             FROM series_course
                            WHERE series_seq = {0} AND delete_yn = 'N');
        '''.format(id)
        cur.execute(query)
        effort = cur.fetchall()

        week_time = 0
        video_time = 0
        study_time = 0

        for e in effort:
            if e[0].find('@') != -1 and e[0].find('#') != -1:
                week = e[0].split('@')[1].split('#')[0]
            elif e[0].find('@') != -1 and e[0].find('#') == -1:
                week = e[0].split('@')[1]
            else:
                week = '0'
            w_time = int(week)
            study = e[0].split('$')[1] if e[0].find('$') != -1 else '0:0'
            s_time = (int(study.split(':')[0]) * 60) + int(study.split(':')[1])
            if e[0].find('#') != -1 and e[0].find('$') != -1:
                video = e[0].split('#')[1].split('$')[0]
            elif e[0].find('#') != -1 and e[0].find('$') == -1:
                video = e[0].split('#')[1]
            else:
                video = '0:0'
            v_time = (int(video.split(':')[0]) * 60) + int(video.split(':')[1])

            week_time += w_time
            study_time += s_time
            video_time += v_time

        week_total = str(week_time) + '주'
        study_total = str(study_time // 60) + '시간 ' + str(study_time % 60) + '분'
        video_total = str(video_time // 60) + '시간' + str(video_time % 60) + '분'

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

    with connections['default'].cursor() as cur:
        query = '''
            SELECT id,
                   course_image_url,
                   course_name,
                   v1.org,
                   ifnull(detail_name, v1.org) AS univ,
                   CASE
                      WHEN start > now()
                      THEN
                         concat(Date_format(start, '`%y.%m.%d. '), '개강예정')
                      WHEN start <= now() AND end > now()
                      THEN
                         concat(
                            '진행중',
                            Date_format(enrollment_end,
                                        '(`%y.%m.%d. 수강신청마감)'))
                      WHEN end <= now() AND audit_yn = 'N'
                      THEN
                         '종강됨'
                      WHEN end <= now() AND audit_yn = 'Y'
                      THEN
                         '종강됨(청강가능)'
                      ELSE
                         '-'
                   END AS course_status,
                   ifnull(effort, '00:00@0#00:00$00:00'),
                   ifnull(classfy, 'ETC') classfy,
                   ifnull(middle_classfy, 'ETC') middle_classfy,
                   v2.short_description,
                   ifnull(course_level, '') as course_level,
                   CASE
                     WHEN start > now()
                     THEN 'ready'
                     ELSE 'pass'
                   END AS status
              FROM edxapp.series_course AS v1
                   JOIN
                   (SELECT *
                      FROM (  SELECT id,
                                     @org := a.org AS org,
                                     display_number_with_default,
                                     start,
                                     end,
                                     enrollment_start,
                                     enrollment_end,
                                     course_image_url,
                                     CASE
                                        WHEN     a.org = @org
                                             AND a.display_number_with_default = @course
                                        THEN
                                           @rn := @rn + 1
                                        ELSE
                                           @rn := 1
                                     END AS rn,
                                     @course := a.display_number_with_default AS course,
                                     effort,
                                     c.classfy,
                                     c.middle_classfy,
                                     a.short_description,
                                     (SELECT detail_ename
                                        FROM code_detail
                                       WHERE     detail_code = c.course_level
                                             AND group_code = 007) AS course_level,
                                     c.audit_yn
                                FROM course_overviews_courseoverview a
                                     LEFT JOIN course_overview_addinfo c
                                        ON a.id = c.course_id,
                                     (SELECT @rn := 0, @org := '', @course := '') b
                               WHERE a.start < a.end
                            ORDER BY a.org, a.display_number_with_default, a.start DESC)
                           t1
                     WHERE rn = 1) AS v2
                      ON     v1.org = v2.org
                         AND v1.display_number_with_default =
                             v2.display_number_with_default
                   LEFT JOIN edxapp.code_detail AS d
                      ON v2.org = d.detail_code AND d.group_code = 003
             WHERE series_seq = {} AND v1.delete_yn = 'N';
        '''.format(id)
        cur.execute(query)
        rows = cur.fetchall()
        query_list = [list(row) for row in rows]

        sub_list = list()

        for row in query_list:
            effort_week = row[6].split('@')[1].split('#')[0] if row[6] and '@' in row[6] and '#' in row[6] else ''
            study_time = row[6].split('$')[1].split(':')[0] + "시간 " + row[6].split('$')[1].split(':')[
                1] + "분" if row[6] and '$' in row[6] else '-'
            learn_time = row[6].split('@')[0] if row[6] and '@' in row[6] else '0'
            course_video = '0'
            if row[6].find('#') != -1 and row[6].find('$') != -1:
                course_video = row[6].split('#')[1].split('$')[0]
            elif row[6].find('#') != -1 and row[6].find('$') == -1:
                course_video = row[6].split('#')[1]
            row.insert(len(row), effort_week)
            row.insert(len(row), study_time)
            row.insert(len(row), learn_time)
            row.insert(len(row), course_video)

            row[7] = classfy_dict[row[7]] if row[7] in classfy_dict or row[7] != 'ETC' else 'ETC'
            row[8] = middle_classfy_dict[row[8]] if row[8] in middle_classfy_dict or row[8] != 'ETC' else 'ETC'

            sub_dict = dict()
            sub_dict['id'] = row[0]
            sub_dict['course_image_url'] = row[1]
            sub_dict['course_name'] = row[2]
            sub_dict['org'] = row[3]
            sub_dict['univ'] = row[4]
            sub_dict['course_status'] = row[5]
            sub_dict['classfy'] = row[7]
            sub_dict['middle_classfy'] = row[8]
            sub_dict['short_description'] = row[9]
            sub_dict['course_level'] = row[10]
            sub_dict['status'] = row[11]
            sub_dict['effort_week'] = effort_week
            sub_dict['study_time'] = study_time
            sub_dict['learn_time'] = learn_time
            sub_dict['course_video'] = course_video
            sub_list.append(sub_dict)

    with connections['default'].cursor() as cur:
        query = '''
            SELECT count(series_student_seq), ifnull(pass_yn, 'N')
              FROM series_student
             WHERE series_seq = {series_seq} AND user_id = '{user_id}' AND delete_yn = 'N';
        '''.format(series_seq=id, user_id=user_id)
        print query
        cur.execute(query)
        series_active = cur.fetchone()
        series_status = dict()
        if series_active[0] == 0 and series_active[1] == 'N':
            series_status['msg'] = 'Series course enrollment'
            series_status['active'] = 'false'
        elif series_active[0] != 0 and series_active[1] == 'N':
            series_status['msg'] = 'Series course unenrollment'
            series_status['active'] = 'true'
        elif series_active[0] != 0 and series_active[1] == 'Y':
            series_status['msg'] = 'Series course complete'
            series_status['active'] = 'pass'

    context = {}
    context['id'] = id
    context['main_list'] = main_list
    context['sub_list'] = sub_list
    context['week_total'] = week_total
    context['study_total'] = study_total
    context['video_total'] = video_total
    context['series_status'] = series_status
    return render_to_response('community/series_view.html', context)


def series_enroll(request, id):
    user_id = request.user.id
    series_id = request.POST.get('series_id') if id == request.POST.get('series_id') else None
    return_msg = 'fail'
    if series_id is not None:
        with connections['default'].cursor() as cur:
            if request.POST.get('method') == 'enroll':
                query = '''
                    INSERT INTO series_student(series_seq,
                                               user_id,
                                               delete_yn,
                                               apply_date,
                                               pass_yn,
                                               regist_id,
                                               regist_date)
                         VALUES ({id},
                                 {user_id},
                                 'N',
                                 now(),
                                 'N',
                                 {user_id},
                                 now());
                '''.format(id=series_id, user_id=user_id)
            else:
                query = '''
                    UPDATE series_student
                       SET delete_yn = 'Y',
                           cancel_date = now(),
                           modify_id = {user_id},
                           modify_date = now()
                     WHERE     user_id = {user_id}
                           AND series_seq = {id}
                           AND delete_yn = 'N'
                           AND pass_yn = 'N';
                '''.format(id=series_id, user_id=user_id)

            print 'series_course insert/update s -------------------------'
            print query
            print 'series_course insert/update e -------------------------'

            cur.execute(query)
            cur.execute('commit')
            return_msg = 'success'

    return JsonResponse({'msg': return_msg})


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

    return JsonResponse({'result': 'success'})