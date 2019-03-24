# -*- coding: utf-8 -*-
""" Views for a student's account information. """

import uuid
import json
from django.conf import settings
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest
)
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from edxmako.shortcuts import render_to_response
from util.json_request import JsonResponse
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
import MySQLdb as mdb
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
import sys
import re
from django.db import models, connections
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.db.models import Q
import os.path
import datetime
from datetime import timedelta
from pytz import timezone
from django.db import connections
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

reload(sys)
sys.setdefaultencoding('utf8')


# ---------- 2017.11.15 ahn jin yong ---------- #
@ensure_csrf_cookie
def memo(request):
    # 1. 로그인 체크 로직
    if not request.user.is_authenticated():
        return redirect('/')

    # 2. ajax 로직
    if request.is_ajax():

        # 2.1 메모 동기화 로직
        if request.POST.get('sync_memo'):
            user_id = request.POST.get('user_id')
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT Count(memo_id)
                    FROM   edxapp.memo
                    WHERE  receive_id = {0}
                           AND read_date IS NULL;
                '''.format(user_id)
                cur.execute(query)
                rows = cur.fetchall()
                try:
                    cnt = rows[0][0]
                except BaseException:
                    cnt = 0

            return JsonResponse({"cnt": cnt})

        # 2.2 메모 내부 삭제 클릭 시 로직
        if request.POST.get('delete_flag'):
            user_id = request.POST.get('user_id')
            board_id = request.POST.get('board_id')
            with connections['default'].cursor() as cur:
                query = '''
                    DELETE FROM edxapp.memo
                    WHERE  memo_id = {0}
                           AND receive_id = {1}
                '''.format(board_id, user_id)
                cur.execute(query)
            return JsonResponse({"return": "success"})

        # 2.3 검색 클릭 시 로직
        if request.POST.get('method') == 'search':
            search_data = request.POST.get('search_data')
            user_id = request.POST.get('user_id')
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT REPLACE(@rn := @rn - 1, .0, '')               AS index_num,
                           CASE
                             WHEN memo_gubun = 1 THEN '단체메일발송'
                           end                                           AS memo_gubun,
                           CONCAT(memo_id, '$xcode$', title)             AS title,
                           Date_format(regist_date, '%Y-%m-%d %H:%m:%s') AS regist_date,
                           CASE
                             WHEN Date_format(read_date, '%Y-%m-%d %H:%m:%s') IS NULL THEN ''
                             ELSE Date_format(read_date, '%Y-%m-%d %H:%m:%s')
                           end                                           AS read_date
                    FROM   edxapp.memo,
                           (SELECT @rn := Count(*) + 1
                            FROM   edxapp.memo
                            WHERE  receive_id = {0}
                            AND    title like '%{1}%' ) AS tmp
                    WHERE  receive_id = {0}
                    AND    title like '%{1}%'
                    ORDER  BY regist_date DESC
                '''.format(user_id, search_data)
                cur.execute(query)
                rows = cur.fetchall()
                if len(rows) < 11:
                    return_list = []
                    for n in range(0, len(rows)):
                        return_list.append(rows[n])
                elif len(rows) != 0:
                    return_list = []
                    for n in range(0, 10):
                        return_list.append(rows[n])
                elif len(rows) == 0:
                    return_list = []
            return JsonResponse({"data": return_list})

        # 2.3 메모 외부 삭제 클릭 시 로직
        elif request.POST.get('method') == 'delete':
            last_num = request.POST.get('last_num')
            if last_num == '':
                last_num = 0

            print "-----------------------> reqeust post get"
            print "last_num = {}".format(last_num)
            print "-----------------------> reqeust post get"

            del_id = request.POST.get('del_id')
            user_id = request.POST.get('user_id')
            search_data = request.POST.get('search_data')
            with connections['default'].cursor() as cur:
                query = '''
                    delete from edxapp.memo
                    where memo_id = {0} and receive_id = {1};
                '''.format(del_id, user_id)
                cur.execute(query)
                print "----------------> query"
                print query
                print "----------------> query"
            with connections['default'].cursor() as cur:
                # 2.3.1 검색 하지 않은 상태의 삭제
                if (search_data) == None:
                    query = '''
                        SELECT REPLACE(@rn := @rn - 1, .0, '')               AS index_num,
                               CASE
                                 WHEN memo_gubun = 1 THEN '단체메일발송'
                               end                                           AS memo_gubun,
                               CONCAT(memo_id, '$xcode$', title)             AS title,
                               Date_format(regist_date, '%Y-%m-%d %H:%m:%s') AS regist_date,
                               CASE
                                 WHEN Date_format(read_date, '%Y-%m-%d %H:%m:%s') IS NULL THEN ''
                                 ELSE Date_format(read_date, '%Y-%m-%d %H:%m:%s')
                               end                                           AS read_date
                        FROM   edxapp.memo,
                               (SELECT @rn := Count(*) + 1
                                FROM   edxapp.memo
                                WHERE  receive_id = {0}) AS tmp
                        WHERE  receive_id = {0}
                        ORDER  BY regist_date DESC
                    '''.format(user_id)
                # 2.3.1 검색 한 이후 상태의 삭제
                elif (search_data) != None:
                    query = '''
                        SELECT REPLACE(@rn := @rn - 1, .0, '')               AS index_num,
                               CASE
                                 WHEN memo_gubun = 1 THEN '단체메일발송'
                               end                                           AS memo_gubun,
                               CONCAT(memo_id, '$xcode$', title)             AS title,
                               Date_format(regist_date, '%Y-%m-%d %H:%m:%s') AS regist_date,
                               CASE
                                 WHEN Date_format(read_date, '%Y-%m-%d %H:%m:%s') IS NULL THEN ''
                                 ELSE Date_format(read_date, '%Y-%m-%d %H:%m:%s')
                               end                                           AS read_date
                        FROM   edxapp.memo,
                               (SELECT @rn := Count(*) + 1
                                FROM   edxapp.memo
                                WHERE  receive_id = {0}
                                AND    title like '%{1}%' ) AS tmp
                        WHERE  receive_id = {0}
                        AND    title like '%{1}%'
                        ORDER  BY regist_date DESC
                    '''.format(user_id, search_data)
                cur.execute(query)
                rows = cur.fetchall()
                plus_list = []

            for i in rows:
                try:
                    if int(last_num) > int(i[0]):
                        plus_list.append(i)
                except BaseException:
                    print "error"
                    return JsonResponse({"return": "success"})

            print "###################################"
            print plus_list
            print len(plus_list)
            print "###################################"

            if len(plus_list) == 0:
                return JsonResponse({"return": "success"})

            return JsonResponse({"return": "success", "plus": plus_list[0]})

        # 2.4 페이징 숫자 클릭시 로직
        elif request.POST.get('click_page'):
            user_id = request.POST.get('user_id')
            click_page = request.POST.get('click_page')
            search_data = request.POST.get('search_data')
            click_page = int(click_page)
            with connections['default'].cursor() as cur:
                # 2.4.1 검색 하지 않은 상태의 조회
                if (search_data) == None:
                    query = '''
                        SELECT REPLACE(@rn := @rn - 1, .0, '')               AS index_num,
                               CASE
                                 WHEN memo_gubun = 1 THEN '단체메일발송'
                               end                                           AS memo_gubun,
                               CONCAT(memo_id, '$xcode$', title)             AS title,
                               Date_format(regist_date, '%Y-%m-%d %H:%m:%s') AS regist_date,
                               CASE
                                 WHEN Date_format(read_date, '%Y-%m-%d %H:%m:%s') IS NULL THEN ''
                                 ELSE Date_format(read_date, '%Y-%m-%d %H:%m:%s')
                               end                                           AS read_date
                        FROM   edxapp.memo,
                               (SELECT @rn := Count(*) + 1
                                FROM   edxapp.memo
                                WHERE  receive_id = {0}) AS tmp
                        WHERE  receive_id = {0}
                        ORDER  BY regist_date DESC
                    '''.format(user_id)
                # 2.4.2 검색 한 이후 상태의 조회
                elif (search_data) != None:
                    query = '''
                        SELECT REPLACE(@rn := @rn - 1, .0, '')               AS index_num,
                               CASE
                                 WHEN memo_gubun = 1 THEN '단체메일발송'
                               end                                           AS memo_gubun,
                               CONCAT(memo_id, '$xcode$', title)             AS title,
                               Date_format(regist_date, '%Y-%m-%d %H:%m:%s') AS regist_date,
                               CASE
                                 WHEN Date_format(read_date, '%Y-%m-%d %H:%m:%s') IS NULL THEN ''
                                 ELSE Date_format(read_date, '%Y-%m-%d %H:%m:%s')
                               end                                           AS read_date
                        FROM   edxapp.memo,
                               (SELECT @rn := Count(*) + 1
                                FROM   edxapp.memo
                                WHERE  receive_id = {0}
                                AND    title like '%{1}%' ) AS tmp
                        WHERE  receive_id = {0}
                        AND    title like '%{1}%'
                        ORDER  BY regist_date DESC
                    '''.format(user_id, search_data)
                cur.execute(query)
                rows = cur.fetchall()
                total = len(rows)
                end = 10 * click_page
                start = end - 10
                stop = 0
                if end > total:
                    end = total
                    start = end - (end % 10)
                    click_page = (start / 10) + 1
                    stop = (total / 10) + 1
                return_list = []
                for n in range(start, end):
                    return_list.append(rows[n])
                    print rows[n]
            return JsonResponse({"data": return_list, "click_page": click_page, "page_stop": stop})

        # 2.5 첫 조회 (리스트에 10개 출력)
        elif request.POST.get('method') == 'notice_list':
            user_id = request.POST.get('user_id')
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT REPLACE(@rn := @rn - 1, .0, '')               AS index_num,
                           CASE
                             WHEN memo_gubun = 1 THEN '단체메일발송'
                           end                                           AS memo_gubun,
                           CONCAT(memo_id, '$xcode$', title)             AS title,
                           Date_format(regist_date, '%Y-%m-%d %H:%m:%s') AS regist_date,
                           CASE
                             WHEN Date_format(read_date, '%Y-%m-%d %H:%m:%s') IS NULL THEN ''
                             ELSE Date_format(read_date, '%Y-%m-%d %H:%m:%s')
                           end                                           AS read_date
                    FROM   edxapp.memo,
                           (SELECT @rn := Count(*) + 1
                            FROM   edxapp.memo
                            WHERE  receive_id = {0}) AS tmp
                    WHERE  receive_id = {0}
                    ORDER  BY regist_date DESC
                '''.format(user_id)
                cur.execute(query)
                rows = cur.fetchall()
                return_list = []
                if len(rows) < 10:
                    for n in range(0, len(rows)):
                        return_list.append(rows[n])
                else:
                    for n in range(0, 10):
                        return_list.append(rows[n])
            return JsonResponse({"data": return_list})

    # 2.1 메모 동기화 로직
    user_email = request.user.email
    with connections['default'].cursor() as cur:
        query = '''
            SELECT count(memo_id)
            FROM   edxapp.memo
			where receive_id in (
                select id
                from edxapp.auth_user
                where email = '{}'
			)
        '''.format(user_email)
        print "query ------------------->"
        print query
        print "query ------------------->"
        cur.execute(query)
        rows = cur.fetchall()
        print "total ------------------->"
        total_size = rows[0][0]
        print "total ------------------->"

    context = {}
    context['total_size'] = total_size
    # 일반 렌더링 리턴
    return render_to_response('community/memo.html', context)


@ensure_csrf_cookie
def memo_view(request, board_id):
    # 1. 미권한 조회 방지 프로텍터 로직
    try:
        user_id = request.user.id
    except BaseException:
        user_id = 0
    with connections['default'].cursor() as cur:
        query = '''
            SELECT memo_id
            FROM   edxapp.memo
            WHERE  memo_id = {0}
                   AND receive_id = {1}
        '''.format(board_id, user_id)
        cur.execute(query)
        rows = cur.fetchall()
        secure_lock = len(rows)  # secure_lock = 0 (권한없음) / secure_lock = 1 (권한있음)
    if secure_lock == 0:
        return JsonResponse({"return": "secure"})

    # 2. 조회 이후 조회시간 업데이트 로직
    with connections['default'].cursor() as cur:
        query = '''
            UPDATE edxapp.memo
            SET    read_date = Now()
            WHERE  memo_id = {0}
        '''.format(board_id)
        cur.execute(query)

    # 3. 조회에 의한 데이터 리턴 로직(메인)
    with connections['default'].cursor() as cur:
        query = '''
            SELECT title,
                   contents,
                   Date_format(regist_date, '%Y-%m-%d %H:%m:%s') as regist_date,
                   Date_format(read_date, '%Y-%m-%d %H:%m:%s') as read_date
            FROM   edxapp.memo
            WHERE  memo_id = {0};
        '''.format(board_id)
        cur.execute(query)
        rows = cur.fetchall()
    title = rows[0][0]
    content = rows[0][1]
    regist_date = rows[0][2]
    read_date = rows[0][3]
    context = {}
    context['title'] = title
    context['content'] = content
    context['board_id'] = board_id
    context['regist_date'] = regist_date
    context['read_date'] = read_date
    return render_to_response('community/memo_view.html', context)


# ---------- 2017.11.15 ahn jin yong ---------- #

def series(request):
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
               b.attach_file_path,
               b.attatch_file_name,
               attatch_file_ext,
               c.detail_name,
               ifnull(a.short_description, '')
            FROM series as a
            LEFT JOIN tb_board_attach AS b
                ON a.sumnail_file_id = b.attatch_id
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


import urllib2
def series_print(request, id):

    # 사용자 아이디 로드 및 이수증 고유번호 생성
    user_id = request.user.id
    cert_uuid = str(uuid.uuid4()).replace('-', '')

    # DEBUG
    print "--------------------------------------------"
    print "user_id -> ", user_id
    print "cert_uuid -> ", cert_uuid
    print "--------------------------------------------"

    # 묶음강좌 중 마지막 이수일 로드
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
        print query
        cur.execute(query)
        cert_date = cur.fetchall()[0][0]

    # 마지막 이수일 포매팅
    cert_date = (cert_date + datetime.timedelta(hours=+9)).strftime('%Y.%m.%d')

    # DEBUG
    print 'cert_date -> ', cert_date
    print "--------------------------------------------"

    # 묶음강좌 이수증 고유번호가 있는지 확인
    with connections['default'].cursor() as cur:
        query = '''
            select count(certificated_id)
            from series_student
            where series_seq = '{id}'
            and user_id = '{user_id}';
        '''.format(user_id=user_id, id=id)
        cur.execute(query)
        check = cur.fetchall()[0][0]

    # DEBUG
    print "check -> ", check
    print "--------------------------------------------"

    # 묶음강좌 이수증 고유번호가 없다면 고유번호 업데이트
    if check == 0:
        with connections['default'].cursor() as cur:
            query = '''
                update series_student
                set pass_yn = 'Y'
                , certificated_id = '{cert_uuid}'
                , certificated_date = now()
                where series_seq = '{id}'
                and user_id = '{user_id}';
            '''.format(user_id=user_id, id=id, cert_uuid=cert_uuid)
            print query
            cur.execute(query)

    # 묶음강좌 이수증 고유번호가 있다면 고유번호 로드
    else:
        with connections['default'].cursor() as cur:
            query = '''
                select certificated_id, certificated_date
                from series_student
                where series_seq = '{id}'
                and user_id = '{user_id}';
            '''.format(user_id=user_id, id=id)
            print query
            cur.execute(query)
            check = cur.fetchall()
        cert_uuid = check[0][0]

    # DEBUG
    print "--------------------------------------------"
    print "cert_uuid -> ", cert_uuid
    print "--------------------------------------------"

    # 이름 / 생년월일 / 본인인증
    with connections['default'].cursor() as cur:
        query = '''
            select username, b.year_of_birth, 
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
            where a.id = '13';
        '''.format(user_id=user_id)
        cur.execute(query)
        row1 = cur.fetchall()

    user_name = row1[0][0]
    user_birth = row1[0][1]
    user_nice = row1[0][2]

    # DEBUG
    print "before user_name -> ", user_name
    print "before user_birth -> ", user_birth
    print "user_nice -> ", user_nice
    print "--------------------------------------------"

    # 본인인증이 되어있다면 본인인증 데이터 로드
    if user_nice == 'Y':
        pd = row1[0][3]
        pd = json.loads(pd)

        user_name = urllib2.unquote(str(pd['UTF8_NAME'])).decode('utf8')

        pd = pd['BIRTHDATE']
        pd = pd[0:4] + '.' + pd[4:6] + '.' + pd[6:8]
        user_birth = pd

    # DEBUG
    print "after user_name -> ", user_name
    print "after user_birth -> ", user_birth
    print "--------------------------------------------"

    # 이수증 출력일시 포매팅
    kst = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m.%d %H:%M:%S')
    kst_short = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m.%d')

    # DEBUG
    print "kst -> ", kst
    print "kst_short -> ", kst_short
    print "--------------------------------------------"

    # 묶음강좌명 / 강좌명
    with connections['default'].cursor() as cur:
        query = '''
            select a.series_name, b.course_name
            from series a
            join series_course b
            on a.series_seq = b.series_seq
            where a.series_seq = '{id}';
            '''.format(id=id)
        cur.execute(query)
        row2 = cur.fetchall()

    try:
        package_name = row2[0][0]
        package_cousre = row2
    except BaseException:
        return JsonResponse({"error": "There is no course in the package course."})

    print "package_name -> ", package_name
    print "package_cousre -> ", package_cousre
    print "--------------------------------------------"

    # 짧은소개 / 기관
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
        row3 = cur.fetchall()

    short_description = row3[0][0]
    org = row3[0][1]

    print "short_description -> ", short_description
    print "org -> ", org
    print "--------------------------------------------"

    # 교수자 사인 (기관)
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

    admin_sign_list = []
    for n in range(0,8):
        try:
            admin_sign_list.append(admin_sign[n][0])
        except BaseException:
            pass

    print "admin_sign_list -> ", admin_sign_list

    # 사인 (대표기관)
    with connections['default'].cursor() as cur:
        query = '''
            select org
            from series
            where series_seq = '{id}';
        '''.format(id=id)
        cur.execute(query)
        row4 = cur.fetchall()

    main_sign = row4[0][0]
    print "main_sign -> ", main_sign

    # 사인 (기관)
    with connections['default'].cursor() as cur:
        query = '''
            select distinct(org)
            from series_course
            where series_seq = '{id}';
        '''.format(id=id)
        cur.execute(query)
        row5= cur.fetchall()

    sub_sign = row5
    print "sub_sign -> ", sub_sign

    sign_list = []
    sign_list.append(main_sign)
    for n in range(0, 3):
        sign_list.append(sub_sign[n][0])

    print "sign_list -> ", sign_list

    sign_path_list = []
    with connections['default'].cursor() as cur:
        for sign in sign_list:
            query = '''
              select save_path
              from tb_attach
              where group_name = 'top_img'
              and group_id = '{sign}';
            '''.format(sign=sign)
            cur.execute(query)
            sign_path = cur.fetchall()
            try:
                sign_path = sign_path[0][0]
            except BaseException:
                sign_path = ''

            sign_path_list.append(sign_path)

    print "sign_path_list -> ", sign_path_list

    # 강좌 리스
    with connections['default'].cursor() as cur:
        query = '''
            select y.display_name, y.start, y.end, z.created_date, effort
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
        tmp['display_name'] = r4[0]
        tmp['start'] = (r4[1] + datetime.timedelta(hours=+9)).strftime('%Y.%m.%d')
        tmp['end'] = (r4[2] + datetime.timedelta(hours=+9)).strftime('%Y.%m.%d')

        ccc = r4[3] + datetime.timedelta(hours=+9)
        ccc = ccc.strftime('%Y.%m.%d %H:%M:%S')
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
        print('e2 -> ', e2)
        print('e3 -> ', e3)
        print('e4 -> ', e4)

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

    print "e3_tmp_front -> ", e3_tmp_front
    print "e3_tmp_back -> ", e3_tmp_back
    print "e3_tmp_back/60 -> ", e3_tmp_back/60
    print "e3_tmp_back%60 -> ", e3_tmp_back%60

    e3_front = e3_tmp_front + e3_tmp_back/60
    e3_back = e3_tmp_back%60

    e3_total = str(e3_front) + '시간 ' + str(e3_back) + '분'

    print "e4_tmp_front -> ", e4_tmp_front
    print "e4_tmp_back -> ", e4_tmp_back
    print "e4_tmp_back/60 -> ", e4_tmp_back/60
    print "e4_tmp_back%60 -> ", e4_tmp_back%60

    e4_front = e4_tmp_front + e4_tmp_back / 60
    e4_back = e4_tmp_back % 60

    e4_total = str(e4_front) + '시간 ' + str(e4_back) + '분'

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

    print "org -> ", org
    print "org -> ", org
    print "org -> ", org

    context = {}
    context['user_name'] = user_name
    context['user_birth'] = user_birth + '.'
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
    context['sign_path_list'] = sign_path_list
    context['admin_sign_list'] = admin_sign_list
    context['org_list'] = org_list

    return render_to_response('community/series_print.html', context)

class TbBoard(models.Model):
    board_id = models.AutoField(primary_key=True)
    head_title = models.CharField(max_length=50, blank=True, null=True)
    subject = models.TextField()
    content = models.TextField(blank=True, null=True)
    reg_date = models.DateTimeField()
    mod_date = models.DateTimeField()
    # section
    # N : notice, F: faq, K: k-mooc news, R: reference
    section = models.CharField(max_length=10)
    use_yn = models.CharField(max_length=1)
    odby = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_board'
        app_label = 'tb_board'

class TbBoardAttach(models.Model):
    attatch_id = models.AutoField(primary_key=True)
    #board_id = models.ForeignKey('TbBoard', on_delete=models.CASCADE, related_name='attaches', null=True)
    board_id = models.IntegerField(11)
    attach_file_path = models.CharField(max_length=255)
    attatch_file_name = models.CharField(max_length=255)
    attach_org_name = models.CharField(max_length=255, blank=True, null=True)
    attatch_file_ext = models.CharField(max_length=50, blank=True, null=True)
    attatch_file_size = models.CharField(max_length=50, blank=True, null=True)
    attach_gubun = models.CharField(max_length=20, blank=True, null=True)
    del_yn = models.CharField(max_length=1)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_board_attach'
        app_label = 'tb_board_attach'

class Memo(models.Model):
    memo_id = models.AutoField(primary_key=True)  # memo_id int(11) primary key auto_increment
    receive_id = models.IntegerField(blank=True, null=True)  # receive_id int(11)
    title = models.CharField(max_length=300)  # title varchar(300) not null
    contents = models.CharField(max_length=20000, blank=True, null=True)  # contents varchar(20000)
    memo_gubun = models.CharField(max_length=20, blank=True, null=True)  # memo_gubun varchar(20)
    read_date = models.DateTimeField(blank=True, null=True)  # read_date datetime
    regist_id = models.IntegerField(blank=True, null=True)  # regist_id int(11)
    regist_date = models.DateTimeField(blank=True, null=True)  # regist_date datetime
    modify_date = models.DateTimeField(blank=True, null=True)  # modify_date datetime

    class Meta:
        managed = False
        db_table = 'memo'
        app_label = 'memo'

@ensure_csrf_cookie
def memo(request):
    user_id = request.user.id

    if request.is_ajax():
        if request.POST.get('del_list'):
            del_list = request.POST.get('del_list')
            del_list = del_list.split('+')
            del_list.pop()

            print "-----------------------> del_list s"
            print "del_list = ", del_list
            print "-----------------------> del_list e"

            for item in del_list:
                Memo.objects.filter(memo_id=item).delete()
                print "-------------### del"
                print "item = ", item
                print "-------------### del"
            return JsonResponse({'a': 'b'})

        else:
            page_size = request.POST.get('page_size')
            curr_page = request.POST.get('curr_page')
            search_con = request.POST.get('search_con')
            search_str = request.POST.get('search_str')

            print "---------------------- DEBUG s"
            print "page_size = ", page_size
            print "curr_page = ", curr_page
            print "search_con = ", search_con
            print "search_str = ", search_str
            print "user_id = ", user_id
            print "---------------------- DEBUG e"

            if search_str:
                print 'search_con:', search_con
                print 'search_str:', search_str

                if search_con == 'title':
                    print "---------------------->1"
                    comm_list = Memo.objects.filter(receive_id=user_id).filter(Q(title__contains=search_str)).order_by('-regist_date')
                else:
                    print "---------------------->2"
                    comm_list = Memo.objects.filter(receive_id=user_id).filter(Q(title__contains=search_str) | Q(contents__contains=search_str)).order_by('-regist_date')
            else:
                print "---------------------->3"
                comm_list = Memo.objects.filter(receive_id=user_id).order_by('-regist_date')

            p = Paginator(comm_list, page_size)
            total_cnt = p.count
            all_pages = p.num_pages
            curr_data = p.page(curr_page)

            print "---------------------- DEBUG s"
            print "total_cnt = ", total_cnt
            print "all_pages = ", all_pages
            print "curr_data = ", curr_data
            print "---------------------- DEBUG e"

            context = {
                'total_cnt': total_cnt,
                'all_pages': all_pages,
                'curr_data': [model_to_dict(o) for o in curr_data.object_list],
            }

            return JsonResponse(context)
    else:
        pass

        context = {
            'page_title': 'Notification'
        }

        return render_to_response('community/comm_memo.html', context)


@ensure_csrf_cookie
def memo_view(request, memo_id=None):
    if memo_id is None:
        return redirect('/')

    Memo.objects.filter(memo_id=memo_id).update(read_date=datetime.datetime.now() + datetime.timedelta(hours=+9))
    memo = Memo.objects.get(memo_id=memo_id)

    if memo:
        memo.files = Memo.objects.filter(memo_id=memo_id)

    context = {
        'page_title': 'Notification',
        'memo': memo
    }

    return render_to_response('community/comm_memo_view.html', context)


# 메모 동기화 로직
@csrf_exempt
def memo_sync(request):
    if request.is_ajax():
        if request.POST.get('sync_memo'):
            user_id = request.POST.get('user_id')
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT Count(memo_id)
                    FROM   edxapp.memo
                    WHERE  receive_id = {0}
                           AND read_date IS NULL;
                '''.format(user_id)
                cur.execute(query)
                rows = cur.fetchall()
                try:
                    cnt = rows[0][0]
                except BaseException:
                    cnt = 0

                query2 = """
                      SELECT title,
                             contents,
                             memo_gubun,
                             date_format(ifnull(modify_date, regist_date), '%m.%d') memo_date,
                             memo_id
                        FROM memo
                       WHERE read_date IS NULL AND receive_id = {user_id}
                    ORDER BY memo_id DESC
                       LIMIT 0, 10;
                """.format(user_id=user_id)

                cur.execute(query2)
                memo_data = cur.fetchall()
                memo_list = []
                for memo in memo_data:
                    memo_row = dict()
                    memo_row['title'] = memo[0]
                    memo_row['contents'] = memo[1]
                    memo_row['memo_gubun'] = memo[2]
                    memo_row['memo_date'] = memo[3]
                    memo_row['memo_id'] = memo[4]

                    memo_list.append(memo_row)

                # print query2

            return JsonResponse({"cnt": cnt, "memo_list": memo_list})


@ensure_csrf_cookie
def comm_list(request, section=None, curr_page=None):
    if request.is_ajax():

        print "--------------------------> comm_list"

        page_size = request.POST.get('page_size')
        curr_page = request.POST.get('curr_page')
        search_con = request.POST.get('search_con')
        search_str = request.POST.get('search_str')

        if search_str != '':
            request.session['search_str'] = search_str

        if search_str == '' and 'search_str' in request.session:
            search_str = request.session['search_str']
            del request.session['search_str']

        print "--------------------> search_str [s]"
        print "search_str = ", search_str
        if 'search_str' in request.session:
            print "request.session['search_str'] = ", request.session['search_str']
        print "--------------------> search_str [e]"

        if search_str:
            if search_con == 'title':
                comm_list = TbBoard.objects.filter(section=section, use_yn='Y').filter(Q(subject__icontains=search_str)).order_by('odby', '-reg_date')
            else:
                comm_list = TbBoard.objects.filter(section=section, use_yn='Y').filter(Q(subject__icontains=search_str) | Q(content__icontains=search_str)).order_by('odby', '-reg_date')
        else:
            comm_list = TbBoard.objects.filter(section=section, use_yn='Y').order_by('-odby', '-reg_date')
        p = Paginator(comm_list, page_size)
        total_cnt = p.count
        all_pages = p.num_pages
        curr_data = p.page(curr_page)

        with connections['default'].cursor() as cur:
            board_list = list()
            for board_data in curr_data.object_list:
                board_dict = dict()
                board_dict['board_id'] = board_data.board_id
                board_dict['content'] = board_data.content
                board_dict['head_title'] = board_data.head_title
                board_dict['mod_date'] = board_data.mod_date
                board_dict['odby'] = board_data.odby
                board_dict['reg_date'] = board_data.reg_date
                board_dict['section'] = board_data.section
                board_dict['subject'] = board_data.subject
                board_dict['use_yn'] = board_data.use_yn

                query = '''
                    SELECT count(attatch_id)
                      FROM tb_board_attach
                     WHERE board_id = {board_id} AND del_yn = 'N';
                '''.format(board_id=board_data.board_id)
                cur.execute(query)
                cnt = cur.fetchone()[0]

                if cnt != 0:
                    board_dict['attach_file'] = 'Y'
                else:
                    board_dict['attach_file'] = 'N'

                board_list.append(board_dict)

            context = {
                'total_cnt': total_cnt,
                'all_pages': all_pages,
                'curr_data': board_list,
            }

        return JsonResponse(context)
    else:
        if section == 'N':
            page_title = '공지사항'
        elif section == 'K':
            page_title = 'K-MOOC 뉴스'
        elif section == 'R':
            page_title = '자료실'
        else:
            return None

        context = {
            'page_title': page_title,
            'curr_page': curr_page,
        }

        return render_to_response('community/comm_list.html', context)


@ensure_csrf_cookie
def comm_view(request, section=None, curr_page=None, board_id=None):

    #print "board_id -> ", board_id

    if section == 'N':
        page_title = '공지사항'
    elif section == 'K':
        page_title = 'K-MOOC 뉴스'
    elif section == 'R':
        page_title = '자료실'
    else:
        return None

    context = {
        'page_title': page_title
    }

    # 게시판 삭제 기능 유효성 체크 [s]
    with connections['default'].cursor() as cur:
        query = '''
            select count(board_id)
            FROM tb_board
            where board_id = '{board_id}'
            and use_yn = 'D'
        '''.format(board_id=board_id)
        cur.execute(query)
        rows = cur.fetchall()

    #print "value -> ", rows[0][0]

    if rows[0][0] == 1:
        return render_to_response('community/comm_null.html', context)
    # 게시판 삭제 기능 유효성 체크 [e]

    if board_id is None:
        return redirect('/')

    board = TbBoard.objects.get(board_id=board_id)

    if board:
        board.files = TbBoardAttach.objects.filter(del_yn='N', board_id=board_id)

    section = board.section

    if section == 'N':
        page_title = '공지사항'
    elif section == 'K':
        page_title = 'K-MOOC 뉴스'
    elif section == 'R':
        page_title = '자료실'
    else:
        return None

    # 관리자에서 업로드한 경로와 실서버에서 가져오는 경로를 replace 시켜주어야함
    board.content = board.content.replace('/manage/home/static/upload/', '/static/file_upload/')

    # local test
    board.content = board.content.replace('/home/project/management/home/static/upload/', '/static/file_upload/')
    context = {
        'page_title': page_title,
        'board': board,
        # 'comm_list_url': reverse('file_check', kwargs={'section': section, 'curr_page': curr_page})
        'comm_list_url': reverse('comm_list', kwargs={'section': section, 'curr_page': curr_page})
    }

    return render_to_response('community/comm_view.html', context)


@ensure_csrf_cookie
def comm_tabs(request, head_title=None):
    if request.is_ajax():

        print "----------------------------->"

        search_str = request.POST.get('search_str')
        head_title = request.POST.get('head_title')

        if head_title == 'total_f' and not search_str:
            comm_list = TbBoard.objects.filter(section='F', use_yn='Y').order_by('odby', '-reg_date')
        # elif head_title == 'total_f' and search_str:
        #     comm_list = TbBoard.objects.filter(section='F', use_yn='Y').filter(Q(subject__icontains=search_str) | Q(content__icontains=search_str)).order_by('odby', '-reg_date')
        elif search_str:
            comm_list = TbBoard.objects.filter(section='F', use_yn='Y').filter(Q(subject__icontains=search_str) | Q(content__icontains=search_str)).order_by('odby', '-reg_date')
        else:
            comm_list = TbBoard.objects.filter(section='F', head_title=head_title, use_yn='Y').order_by('odby', '-reg_date')

        return JsonResponse([model_to_dict(o) for o in comm_list])
    else:
        if not head_title:
            head_title = 'kmooc_f'

        comm_list = TbBoard.objects.filter(section='F', head_title=head_title, use_yn='Y').order_by('odby', '-reg_date')

        context = {
            'data': comm_list,
            'head_title': head_title
        }

        return render_to_response('community/comm_tabs.html', context)


@ensure_csrf_cookie
def comm_file(request, file_id=None):
    try:
        with connections['default'].cursor() as cur:
            query = '''
                SELECT save_path, save_name
                  FROM tb_attach
                 WHERE use_yn = TRUE AND id = {file_id};
            '''.format(file_id=file_id)

            cur.execute(query)
            attach_file = cur.fetchone()

        # file = TbBoardAttach.objects.filter(del_yn='N').get(pk=file_id)
    except Exception as e:
        print 'comm_file error --- s'
        print e
        print connections['default'].queries
        print 'comm_file error --- e'
        return HttpResponse("<script>alert('파일이 존재하지 않습니다.'); window.history.back();</script>")

    # filepath = file.attach_file_path.replace('/manage/home/static/upload/', '/edx/var/edxapp/staticfiles/file_upload/') if file.attach_file_path else '/edx/var/edxapp/staticfiles/file_upload/'
    save_path = attach_file[0]

    file_name = attach_file[1]
    save_path = save_path.replace('/static/file_upload', '/staticfiles/file_upload') if attach_file[0] else ''
    real_path = '/edx/var/edxapp' + save_path
    # filename = file.attatch_file_name

    print "디렉토리",(os.getcwd())  # 현재 디렉토리의
    print 'file_path,,', os.path.dirname(os.path.realpath(__file__))
    #print "파일",(os.path.realpath(__file__))  # 파일
    #print "파일의 디렉토리",(os.path.dirname(os.path.realpath(__file__)))  # 파일이 위치한 디렉토리

    # if not file or not os.path.exists(filepath + filename):
    if not attach_file or not os.path.exists(real_path):
        print 'filepath  :', save_path
        return HttpResponse("<script>alert('파일이 존재하지 않습니다 .'); window.history.back();</script>")

    response = HttpResponse(open(real_path, 'rb'), content_type='application/force-download')

    response['Content-Disposition'] = 'attachment; filename=%s' % str(file_name)
    return response


def comm_notice(request):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    noti_list = []
    page = 1
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'notice_list':
            cur = con.cursor()
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'N' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           (SELECT ceil(count(board_id) / 10)
                              FROM tb_board
                             WHERE section = 'N' AND use_yn = 'Y')
                              AS total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'noti_n' THEN '공지'
                              WHEN head_title = 'advert_n' THEN '공고'
                              WHEN head_title = 'guide_n' THEN '안내'
                              WHEN head_title = 'event_n' THEN '이벤트'
                              WHEN head_title = 'etc_n' THEN '기타'
                              ELSE ''
                           END
                              head_title
                    FROM tb_board
                    WHERE section = 'N' AND use_yn = 'Y'
            """ % (page)

            if 'cur_page' in request.GET:
                cur_page = request.GET['cur_page']
                if cur_page == '1':
                    query += "order by odby desc, reg_date desc " \
                             "limit 0,10"
                    cur.execute(query)
                else:
                    start_num = (int(cur_page) - 1) * 10
                    query += "order by odby desc, reg_date desc " \
                             "limit %s,10" % (start_num)
                    cur.execute(query)
            else:
                query += "order by odby desc, reg_date desc " \
                         "limit 0,10"
                cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for noti in row:
                value_list = []
                notice = noti
                value_list.append(int(notice[0]))
                value_list.append(notice[1])
                value_list.append(notice[2])
                value_list.append(int(notice[3]))
                value_list.append(notice[4])
                value_list.append(notice[5])
                if notice[6] == None or notice[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + notice[6] + '] ')

                noti_list.append(value_list)
            data = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'search_list':
            cur = con.cursor()
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'N' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           %s                          total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'noti_n' THEN '공지'
                              WHEN head_title = 'advert_n' THEN '공고'
                              WHEN head_title = 'guide_n' THEN '안내'
                              WHEN head_title = 'event_n' THEN '이벤트'
                              WHEN head_title = 'etc_n' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'N' and use_yn = 'Y'
            """ % (page, page)
            logging.info("############# - second")

            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                # print 'title == ',title
                if title == 'search_total':
                    query += "and (subject like '%" + search + "%' or content like '%" + search + "%') and section='N' "
                else:
                    query += "and subject like '%" + search + "%' and section='N' "

            query += "order by reg_date desc "
            # print 'query == ', query
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for noti in row:
                value_list = []
                notice = noti
                value_list.append(int(notice[0]))
                value_list.append(notice[1])
                value_list.append(notice[2])
                value_list.append(int(notice[3]))
                value_list.append(notice[4])
                value_list.append(notice[5])
                if notice[6] == None or notice[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + notice[6] + '] ')
                noti_list.append(value_list)
            data = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(list(data), 'application/json')

    return render_to_response('community/comm_notice.html')


@ensure_csrf_cookie
def comm_notice_view(request, board_id):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    value_list = []
    board_id = board_id.replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("/", "&#x2F;") \
        .replace("&", "&#38;") \
        .replace("#", "&#35;") \
        .replace("\'", "&#x27;") \
        .replace("\"", "&#qout;")
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'view':
            cur = con.cursor()
            query = """
                    SELECT subject,
                           content,
                           SUBSTRING(reg_date, 1, 10),
                           SUBSTRING(mod_date, 1, 10),
                           CASE
                              WHEN head_title = 'noti_n' THEN '공지'
                              WHEN head_title = 'advert_n' THEN '공고'
                              WHEN head_title = 'guide_n' THEN '안내'
                              WHEN head_title = 'event_n' THEN '이벤트'
                              WHEN head_title = 'etc_n' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'N' AND board_id =
            """ + board_id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            # ----- 파일 이름 구하기 query ----- #
            cur = con.cursor()
            query = '''
                SELECT attatch_file_name 
                FROM   tb_board_attach 
                WHERE  attatch_file_name <> 'None' 
                AND    board_id = {0}
                AND    del_yn = 'N'
            '''.format(board_id)
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # ----- 파일 이름 구하기 query ----- #

            value_list.append(row[0][0])
            value_list.append(row[0][1])
            value_list.append(row[0][2])
            value_list.append(row[0][3])
            if row[0][4] == None or row[0][4] == '':
                value_list.append('')
            else:
                value_list.append('[' + row[0][4] + '] ')

            if files:
                value_list.append(files)

            # print 'value_list == ',value_list

            data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            # print 'file_name == ', file_name
            data = json.dumps('/static/file_upload/' + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'application/json')

    context = {
        'id': board_id
    }
    return render_to_response('community/comm_notice_view.html', context)


@ensure_csrf_cookie
def comm_faq(request, head_title):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    if request.is_ajax():
        if request.GET['method'] == 'faq_list':
            faq_list = []
            head_title = request.GET['head_title']
            cur = con.cursor()
            query = """SELECT subject,
                               content,
                               CASE
                                  WHEN head_title = 'kmooc_f' THEN 'K-MOOC'
                                  WHEN head_title = 'regist_f ' THEN '회원가입'
                                  WHEN head_title = 'login_f ' THEN '로그인/계정'
                                  WHEN head_title = 'enroll_f ' THEN '수강신청/취소'
                                  WHEN head_title = 'course_f ' THEN '강좌수강'
                                  WHEN head_title = 'certi_f  ' THEN '성적/이수증'
                                  WHEN head_title = 'tech_f ' THEN '기술적문제'
                                  WHEN head_title = 'mobile_f ' THEN '모바일문제'
                                  ELSE ''
                               END
                                  head_title
                          FROM tb_board
                         WHERE section = 'F' AND use_yn = 'Y' AND head_title = '""" + head_title + "'"""
            if 'search' in request.GET:
                search = request.GET['search']
                query += " and subject like '%" + search + "%'"
            cur.execute(query)
            row = cur.fetchall()
            print str(row)
            print query
            head_title = head_title.replace("<", "&lt;") \
                .replace(">", "&gt;") \
                .replace("/", "&#x2F;") \
                .replace("&", "&#38;") \
                .replace("#", "&#35;") \
                .replace("\'", "&#x27;") \
                .replace("\"", "&#qout;")

            for f in row:
                value_list = []
                faq = f
                value_list.append(faq[0])
                value_list.append(faq[1])
                value_list.append(faq[2])
                faq_list.append(value_list)
            data = json.dumps(list(faq_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'application/json')
    # print 'head_title ==', head_title
    context = {
        'head_title': head_title
    }
    return render_to_response('community/comm_faq.html', context)


def comm_faqrequest(request, head_title=None):
    if request.is_ajax():
        data = json.dumps('fail')
        if request.GET['method'] == 'request':
            con = connections['default']
            email = request.GET['email']
            request_con = request.GET['request_con']
            option = request.GET['option']
            save_email = ''
            # print 'option == ', option
            head_dict = {
                'kmooc_f': '[K-MOOC]',
                'regist_f': '[회원가입]',
                'login_f': '[로그인/계정]',
                'enroll_f': '[수강신청/취소]',
                'course_f': '[강좌수강]',
                'certi_f': '[성적/이수증]',
                'tech_f': '[기술적문제]',
                'mobile_f': '[모바일문제]',
            }
            email_title = head_dict[option] + ' ' + email + '님의 문의 내용입니다.'
            # 이메일 전송

            from_address = configuration_helpers.get_value(
                'email_from_address',
                settings.DEFAULT_FROM_EMAIL
            )

            email = replace_all(email)

            option = replace_all(option)
            email_title = replace_all(email_title)
            request_con = replace_all(request_con)
            from_address = replace_all(from_address)

            if option == 'kmooc_f':
                # send_mail(email+'님의 문의 내용입니다.', request_con, 보내는 사람, ['받는사람'])
                send_mail(email_title, request_con, from_address, ['kmooc@nile.or.kr'])
                save_email = 'kmooc@nile.or.kr'
            else:
                send_mail(email_title, request_con, from_address, ['info_kmooc@nile.or.kr'])
                save_email = 'info_kmooc@nile.or.kr'
            # 문의내용 저장

            save_email = replace_all(save_email)

            cur = con.cursor()
            query = """
                    INSERT INTO faq_request(student_email,
                                response_email,
                                question,
                                head_title)
                            VALUES (
                                      '""" + email + """',
                                      '""" + save_email + """',
                                      '""" + request_con + """',
                                      (CASE
                                          WHEN '""" + option + """' = 'kmooc_f' THEN 'K-MOOC'
                                          WHEN '""" + option + """' = 'regist_f ' THEN '회원가입'
                                          WHEN '""" + option + """' = 'login_f ' THEN '로그인/계정'
                                          WHEN '""" + option + """' = 'enroll_f ' THEN '수강신청/취소'
                                          WHEN '""" + option + """' = 'course_f ' THEN '강좌수강'
                                          WHEN '""" + option + """' = 'certi_f  ' THEN '성적/이수증'
                                          WHEN '""" + option + """' = 'tech_f ' THEN '기술적문제'
                                          WHEN '""" + option + """' = 'mobile_f ' THEN '모바일문제'
                                          ELSE ''
                                       END));
            """
            # print 'query == ',query
            cur.execute(query)
            cur.execute('commit')
            cur.close()
            data = json.dumps('success')
        return HttpResponse(data, 'application/json')

    return render_to_response('community/comm_faqrequest.html', {'head_title': head_title})


def replace_all(string):
    string = string.replace('<', '&lt;');
    string = string.replace('>', '&gt;');
    string = string.replace('"', '&quot;');
    string = string.replace("'", "&#39;");
    return string


@ensure_csrf_cookie
def comm_repository(request):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    data_list = []
    page = 1
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'data_list':
            cur = con.cursor()
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'R' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           (SELECT ceil(count(board_id) / 10)
                              FROM tb_board
                             WHERE section = 'R' AND use_yn = 'Y')
                              AS total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'publi_r' THEN '홍보자료'
                              WHEN head_title = 'data_r' THEN '자료집'
                              WHEN head_title = 'repo_r' THEN '보고서'
                              WHEN head_title = 'etc_r' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'R' AND use_yn = 'Y'
            """ % (page)
            if 'cur_page' in request.GET:
                cur_page = request.GET['cur_page']
                if cur_page == '1':
                    query += "order by odby desc, reg_date desc " \
                             "limit 0,10"
                    cur.execute(query)
                else:
                    start_num = (int(cur_page) - 1) * 10
                    query += "order by odby desc, reg_date desc " \
                             "limit %s,10" % (start_num)
                    cur.execute(query)
            else:
                query += "order by odby desc, reg_date desc " \
                         "limit 0,10"
                cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for d in row:
                value_list = []
                data = d
                value_list.append(int(data[0]))
                value_list.append(data[1])
                value_list.append(data[2])
                value_list.append(int(data[3]))
                value_list.append(data[4])
                value_list.append(data[5])
                if data[6] == None or data[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + data[6] + '] ')
                data_list.append(value_list)
            adata = json.dumps(list(data_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'search_list':
            cur = con.cursor()
            page = ''
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'R' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           %s                          total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'publi_r' THEN '홍보'
                              WHEN head_title = 'course_r' THEN '강좌안내'
                              WHEN head_title = 'event_r' THEN '행사'
                              WHEN head_title = 'etc_r' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'R' and use_yn = 'Y'
            """ % (page, page)
            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                if title == 'search_total':
                    query += "and (subject like '%" + search + "%' or content like '%" + search + "%') and section='R' "
                else:
                    query += "and subject like '%" + search + "%' and section='R' "

            query += "order by reg_date desc "
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for d in row:
                value_list = []
                data = d
                value_list.append(int(data[0]))
                value_list.append(data[1])
                value_list.append(data[2])
                value_list.append(int(data[3]))
                value_list.append(data[4])
                value_list.append(data[5])
                if data[6] == None or data[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + data[6] + '] ')
                data_list.append(value_list)
            adata = json.dumps(list(data_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(list(adata), 'application/json')
    return render_to_response('community/comm_repository.html')


@ensure_csrf_cookie
def comm_repo_view(request, board_id):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    value_list = []
    board_id = board_id.replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("/", "&#x2F;") \
        .replace("&", "&#38;") \
        .replace("#", "&#35;") \
        .replace("\'", "&#x27;") \
        .replace("\"", "&#qout;")
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'view':
            cur = con.cursor()
            query = """
                    SELECT subject,
                           content,
                           SUBSTRING(reg_date, 1, 10),
                           CASE
                              WHEN head_title = 'publi_r' THEN '홍보'
                              WHEN head_title = 'course_r' THEN '강좌안내'
                              WHEN head_title = 'event_r' THEN '행사'
                              WHEN head_title = 'etc_r' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'R' AND board_id = """ + board_id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            # ----- 파일 이름 구하기 query ----- #
            cur = con.cursor()
            query = '''
                SELECT attatch_file_name 
                FROM   tb_board_attach 
                WHERE  attatch_file_name <> 'None' 
                AND    board_id = {0}
                AND    del_yn = 'N'
            '''.format(board_id)
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # ----- 파일 이름 구하기 query ----- #

            value_list.append(row[0][0])
            value_list.append(row[0][1])
            value_list.append(row[0][2])
            if row[0][3] == None or row[0][3] == '':
                value_list.append('')
            else:
                value_list.append('[' + row[0][3] + '] ')

            if files:
                value_list.append(files)

            data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            # print 'file_name == ', file_name
            data = json.dumps('/static/file_upload/' + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'application/json')

    context = {
        'id': board_id
    }
    return render_to_response('community/comm_repo_view.html', context)


@ensure_csrf_cookie
def comm_mobile(request):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    noti_list = []
    page = 1
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'mobile_list':
            cur = con.cursor()
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'M' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           (SELECT ceil(count(board_id) / 10)
                              FROM tb_board
                             WHERE section = 'M' AND use_yn = 'Y')
                              AS total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'noti_n' THEN '공지'
                              WHEN head_title = 'advert_n' THEN '공고'
                              WHEN head_title = 'guide_n' THEN '안내'
                              WHEN head_title = 'event_n' THEN '이벤트'
                              WHEN head_title = 'etc_n' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'M' AND use_yn = 'Y'
            """ % (page)
            if 'cur_page' in request.GET:
                cur_page = request.GET['cur_page']
                if cur_page == '1':
                    query += "order by reg_date desc " \
                             "limit 0,10"
                    cur.execute(query)
                else:
                    start_num = (int(cur_page) - 1) * 10
                    query += "order by reg_date desc " \
                             "limit %s,10" % (start_num)
                    cur.execute(query)
            else:
                query += "order by reg_date desc " \
                         "limit 0,10"
                cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for noti in row:
                value_list = []
                mobile = noti
                value_list.append(int(mobile[0]))
                value_list.append(mobile[1])
                value_list.append(mobile[2])
                value_list.append(int(mobile[3]))
                value_list.append(mobile[4])
                value_list.append(mobile[5])
                if mobile[6] == None or mobile[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + mobile[6] + '] ')

                noti_list.append(value_list)
            data = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'search_list':
            cur = con.cursor()
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'M' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           %s                          total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'noti_n' THEN '공지'
                              WHEN head_title = 'advert_n' THEN '공고'
                              WHEN head_title = 'guide_n' THEN '안내'
                              WHEN head_title = 'event_n' THEN '이벤트'
                              WHEN head_title = 'etc_n' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'M' and use_yn = 'Y'
            """ % (page, page)
            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                # print 'title == ',title
                if title == 'search_total':
                    query += "and (subject like '%" + search + "%' or content like '%" + search + "%') and section='M' "
                else:
                    query += "and subject like '%" + search + "%' and section='M' "

            query += "order by reg_date desc "
            # print 'query == ', query
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for noti in row:
                value_list = []
                mobile = noti
                value_list.append(int(mobile[0]))
                value_list.append(mobile[1])
                value_list.append(mobile[2])
                value_list.append(int(mobile[3]))
                value_list.append(mobile[4])
                value_list.append(mobile[5])
                if mobile[6] == None or mobile[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + mobile[6] + '] ')
                noti_list.append(value_list)
            data = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(list(data), 'application/json')

    return render_to_response('community/comm_mobile.html')


@ensure_csrf_cookie
def comm_mobile_view(request, board_id):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    value_list = []
    board_id = board_id.replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("/", "&#x2F;") \
        .replace("&", "&#38;") \
        .replace("#", "&#35;") \
        .replace("\'", "&#x27;") \
        .replace("\"", "&#qout;")
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'view':
            cur = con.cursor()
            query = """
                    SELECT subject,
                           content,
                           SUBSTRING(reg_date, 1, 10),
                           SUBSTRING(mod_date, 1, 10),
                           '모바일' head_title
                      FROM tb_board
                     WHERE section = 'M' AND board_id =
            """ + board_id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            # ----- 파일 이름 구하기 query ----- #
            cur = con.cursor()
            query = '''
                SELECT attatch_file_name 
                FROM   tb_board_attach 
                WHERE  attatch_file_name <> 'None' 
                AND    board_id = {0}
                AND    del_yn = 'N'
            '''.format(board_id)
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # ----- 파일 이름 구하기 query ----- #

            value_list.append(row[0][0])
            value_list.append(row[0][1])
            value_list.append(row[0][2])
            value_list.append(row[0][3])
            if row[0][4] == None or row[0][4] == '':
                value_list.append('')
            else:
                value_list.append('[' + row[0][4] + '] ')

            if files:
                value_list.append(files)

            # print 'value_list == ',value_list

            data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            # print 'file_name == ', file_name
            data = json.dumps('/static/file_upload/' + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'application/json')

    context = {
        'id': board_id
    }
    return render_to_response('community/comm_mobile_view.html', context)


@ensure_csrf_cookie
def comm_k_news(request):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    k_news_list = []
    page = 1
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'k_news_list':
            cur = con.cursor()
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'K' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           (SELECT ceil(count(board_id) / 10)
                              FROM tb_board
                             WHERE section = 'K' AND use_yn = 'Y')
                              AS total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'k_news_k' THEN 'K-MOOC소식'
                              WHEN head_title = 'report_k' THEN '보도자료'
                              WHEN head_title = 'u_news_k' THEN '대학뉴스'
                              WHEN head_title = 'support_k' THEN '서포터즈이야기'
                              WHEN head_title = 'n_new_k' THEN 'NILE소식'
                              WHEN head_title = 'etc_k' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'K' AND use_yn = 'Y'
            """ % (page)
            if 'cur_page' in request.GET:
                cur_page = request.GET['cur_page']
                if cur_page == '1':
                    query += "order by odby desc, reg_date desc " \
                             "limit 0,10"
                    cur.execute(query)
                else:
                    start_num = (int(cur_page) - 1) * 10
                    query += "order by odby desc, reg_date desc " \
                             "limit %s,10" % (start_num)
                    cur.execute(query)
            else:
                query += "order by odby desc, reg_date desc " \
                         "limit 0,10"
                cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for k in row:
                value_list = []
                k_news = k
                value_list.append(int(k_news[0]))
                value_list.append(k_news[1])
                value_list.append(k_news[2])
                value_list.append(int(k_news[3]))
                value_list.append(k_news[4])
                value_list.append(k_news[5])
                if k_news[6] == None or k_news[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + k_news[6] + '] ')

                k_news_list.append(value_list)
            data = json.dumps(list(k_news_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'search_list':
            cur = con.cursor()
            if 'cur_page' in request.GET:
                page = request.GET['cur_page']
            query = """
                    SELECT (SELECT count(board_id) - (%s - 1) * 10
                              FROM tb_board
                             WHERE section = 'K' AND use_yn = 'Y')
                              no,
                           subject,
                           substring(reg_date, 1, 10) reg_datee,
                           %s                          total_page,
                           board_id,
                           CASE
                              WHEN reg_date BETWEEN now() - INTERVAL 7 DAY AND now() THEN '1'
                              ELSE '0'
                           END
                              flag,
                           CASE
                              WHEN head_title = 'k_news_k' THEN 'K-MOOC소식'
                              WHEN head_title = 'report_k' THEN '보도자료'
                              WHEN head_title = 'u_news_k' THEN '대학뉴스'
                              WHEN head_title = 'support_k' THEN '서포터즈이야기'
                              WHEN head_title = 'n_new_k' THEN 'NILE소식'
                              WHEN head_title = 'etc_k' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE use_yn = 'Y'
            """ % (page, page)
            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                # print 'title == ',title
                if title == 'search_total':
                    query += "and (subject like '%" + search + "%' or content like '%" + search + "%') and section='K' "
                else:
                    query += "and subject like '%" + search + "%' and section='K' "

            query += "order by reg_date desc "
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            for k in row:
                value_list = []
                k_news = k
                value_list.append(int(k_news[0]))
                value_list.append(k_news[1])
                value_list.append(k_news[2])
                value_list.append(int(k_news[3]))
                value_list.append(k_news[4])
                value_list.append(k_news[5])
                if k_news[6] == None or k_news[6] == '':
                    value_list.append('')
                else:
                    value_list.append('[' + k_news[6] + '] ')
                k_news_list.append(value_list)
            data = json.dumps(list(k_news_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(list(data), 'application/json')
    return render_to_response('community/comm_k_news.html')


def comm_k_news_view(request, board_id):
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    value_list = []
    board_id = board_id.replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("/", "&#x2F;") \
        .replace("&", "&#38;") \
        .replace("#", "&#35;") \
        .replace("\'", "&#x27;") \
        .replace("\"", "&#qout;")
    if request.is_ajax():
        data = {}
        if request.GET['method'] == 'view':
            cur = con.cursor()
            query = """
                    SELECT subject,
                           content,
                           SUBSTRING(reg_date, 1, 10),
                           CASE
                              WHEN head_title = 'k_news_k' THEN 'K-MOOC소식'
                              WHEN head_title = 'report_k' THEN '보도자료'
                              WHEN head_title = 'u_news_k' THEN '대학뉴스'
                              WHEN head_title = 'support_k' THEN '서포터즈이야기'
                              WHEN head_title = 'n_new_k' THEN 'NILE소식'
                              WHEN head_title = 'etc_k' THEN '기타'
                              ELSE ''
                           END
                              head_title
                      FROM tb_board
                     WHERE section = 'K' AND board_id = """ + board_id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            # ----- 파일 이름 구하기 query ----- #
            cur = con.cursor()
            query = '''
                SELECT attatch_file_name 
                FROM   tb_board_attach 
                WHERE  attatch_file_name <> 'None' 
                AND    board_id = {0}
                AND    del_yn = 'N'
            '''.format(board_id)
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # ----- 파일 이름 구하기 query ----- #

            value_list.append(row[0][0])
            value_list.append(row[0][1])
            value_list.append(row[0][2])
            if row[0][3] == None or row[0][3] == '':
                value_list.append('')
            else:
                value_list.append('[' + row[0][3] + '] ')

            if files:
                value_list.append(files)

            data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            # print 'file_name == ', file_name
            data = json.dumps('/static/file_upload/' + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'application/json')

    context = {
        'id': board_id
    }
    return render_to_response('community/comm_k_news_view.html', context)


class SMTPException(Exception):
    """Base class for all exceptions raised by this module."""


# 휴면계정 이메일 발송 쿼리
# def test(request):
#     email_list = []
#     con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
#                       settings.DATABASES.get('default').get('USER'),
#                       settings.DATABASES.get('default').get('PASSWORD'),
#                       settings.DATABASES.get('default').get('NAME'),
#                       charset='utf8')
#     cur = con.cursor()
#     query = """
#         SELECT email, dormant_mail_cd from auth_user
#     """
#     cur.execute(query)
#     row = cur.fetchall()
#     cur.close()
#
#     for u in row:
#         user = u
#         if user[1] == '15' or user[1] == '30':
#             email_list.append(user[0])
#     # 이메일 전송
#     from_address = configuration_helpers.get_value(
#         'email_from_address',
#         settings.DEFAULT_FROM_EMAIL
#     )
#
#     print 'email_list == ',email_list
#
#     cur = con.cursor()
#     for e in email_list:
#         try:
#             send_mail('테스트 이메일', '이메일 제대로 가나요', from_address, [e], fail_silently=False)
#             query1 = "update auth_user set dormant_mail_cd = '0' where email = '"+e+"' "
#             cur.execute(query1)
#             cur.execute('commit')
#             query1 = "insert into drmt_auth_user_process(email,success) values('"+e+"', '1')"
#             cur.execute(query1)
#             cur.execute('commit')
#         except SMTPException:
#             print 'fail sending email'
#             cur = con.cursor()
#             query1 = "insert into drmt_auth_user_process(email) values('"+e+"')"
#             cur.execute(query1)
#             cur.execute('commit')
#
#
#     cur.close()
#     return render_to_response('community/test.html')


def comm_list_json(request):
    con = connections['default']
    if request.is_ajax:
        total_list = []
        data = json.dumps('ready')
        cur = con.cursor()
        query = """
              SELECT *
                FROM (SELECT board_id,
                             CASE
                                WHEN section = 'N' THEN '[공지사항]'
                                WHEN section = 'F' THEN '[Q&A]'
                                WHEN section = 'K' THEN '[K-MOOC 뉴스]'
                                WHEN section = 'R' THEN '[자료실]'
                                WHEN section = 'M' THEN '[모바일]'
                                ELSE ''
                             END
                                head_title,
                             subject,
                             content,
                             mod_date,
                             section,
                             CASE
                                WHEN section = 'N' THEN 1
                                WHEN section = 'F' THEN 4
                                WHEN section = 'K' THEN 2
                                WHEN section = 'R' THEN 3
                                WHEN section = 'M' THEN 5
                                ELSE ''
                             END
                                odby,
                             head_title AS `s`,
                             reg_date
                        FROM ((  SELECT board_id,
                                        head_title,
                                        subject,
                                        content,
                                        date_format(mod_date, '%Y/%m/%d') mod_date,
                                        section,
                                        head_title                    s,
                                        date_format(reg_date, '%Y/%m/%d') reg_date
                                   FROM tb_board
                                  WHERE use_yn = 'Y' AND section = 'N'
                               ORDER BY reg_date DESC, board_id DESC
                                  LIMIT 1)
                              UNION ALL
                              (  SELECT board_id,
                                        head_title,
                                        subject,
                                        content,
                                        date_format(mod_date, '%Y/%m/%d') mod_date,
                                        section,
                                        head_title                    s,
                                        date_format(reg_date, '%Y/%m/%d') reg_date
                                   FROM tb_board
                                  WHERE use_yn = 'Y' AND section = 'K'
                               ORDER BY reg_date DESC, board_id DESC
                                  LIMIT 1)
                              UNION ALL
                              (  SELECT board_id,
                                        head_title,
                                        subject,
                                        content,
                                        date_format(mod_date, '%Y/%m/%d') mod_date,
                                        section,
                                        head_title                    s,
                                        date_format(reg_date, '%Y/%m/%d') reg_date
                                   FROM tb_board
                                  WHERE use_yn = 'Y' AND section = 'R'
                               ORDER BY reg_date DESC, board_id DESC
                                  LIMIT 1)
                              UNION ALL
                              (  SELECT board_id,
                                        head_title,
                                        subject,
                                        content,
                                        date_format(mod_date, '%Y/%m/%d') mod_date,
                                        section,
                                        head_title                    s,
                                        date_format(reg_date, '%Y/%m/%d') reg_date
                                   FROM tb_board
                                  WHERE use_yn = 'Y' AND section = 'F'
                               ORDER BY reg_date DESC, board_id DESC
                                  LIMIT 1)) dt1) dt2
            ORDER BY odby
        """
        cur.execute(query)
        row = cur.fetchall()

        for t in row:
            value_list = []
            value_list.append(t[0])
            value_list.append(t[1])
            value_list.append(t[2])
            s = t[3]
            text = re.sub('<[^>]*>', '', s)
            text = re.sub('&nbsp;', '', text)
            value_list.append(text)
            value_list.append(t[8])
            value_list.append(t[5])
            value_list.append(t[7])
            total_list.append(value_list)
        data = json.dumps(list(total_list), cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(data, 'application/json')

# ---------- 2018.06.22 Jo Ho Young ---------- #

def cert_survey(request):
    print "survey_chk"
    if request.is_ajax():

        Q1 = request.POST.get('Q1')
        Q2 = request.POST.get('Q2')
        Q3 = request.POST.get('Q3')
        Q4 = request.POST.get('Q4')
        Q5 = request.POST.get('Q5')
        user_id = request.POST.get('user_id')
        course_id = request.POST.get('course_id')
        #print "Q1-------->",Q1
        #print "Q2-------->",Q2
        #print "Q3-------->",Q3
        #print "Q4-------->",Q4
        #print "Q5-------->",Q5
        #print "user_id-------->",user_id
        #print "course_id-------->",course_id

        with connections['default'].cursor() as cur:
            query = '''
                  INSERT INTO edxapp.survey_result
                              (course_id,
                              question_01,
                              question_02,
                              question_03,
                              question_04,
                              question_05,
                              regist_id)
                  VALUES ('{course_id}','{question_01}','{question_02}','{question_03}','{question_04}','{question_05}','{regist_id}')
            '''.format(course_id=course_id,question_01=Q1,question_02=Q2,question_03=Q3,question_04=Q4,question_05=Q5,regist_id=user_id)

            #print "query ===============",query
            cur.execute(query)

        return JsonResponse({"return": "success","course_id":course_id,"question_01":Q1,"question_02":Q2,"question_03":Q3,'question_04':Q4,'question_05':Q5,'regist_id':user_id})

    hello = request.GET['hello']
    print "hello", hello
    course_id = request.GET['course_id']
    user_id = request.GET['user_id']
    course_id2 = request.GET['course_id']
    #print "before = ", hello

    hello = hello.split('/certificates/')
    hello = hello[1]
    course_id = course_id
    user_id=user_id

    print "course_id = ",course_id

    course_id2 = course_id2.replace(" ", "+")

    with connections['default'].cursor() as cur:
        query = '''
                select display_name
                from course_overviews_courseoverview
                where id = '{course_id}';
            '''.format(course_id=course_id2)
        cur.execute(query)
        display_name = cur.fetchall()

    # print "course_id2", course_id2
    # print "display_name = ",display_name

    with connections['default'].cursor() as cur:
        query = '''
                select course_id,min(created_date)
                from certificates_generatedcertificate
                where course_id ='{course_id}'
                group by course_id;
            '''.format(course_id=course_id2)
        cur.execute(query)
        rows = cur.fetchall()

    from django.utils import timezone
    base_time = datetime.datetime(2018, 7, 11, 00, 00, 00)

    # print "gggg---g",base_time
    # print "rows---",rows[0][1]
    # print "user_id = ",user_id
    # print "certificates = ", hello
    # 2018-11-16 05:15:19.093068

    if base_time > rows[0][1]:
        print "trus"
        return redirect('/certificates/'+hello)

    else:
        print "false"
        pass



    with connections['default'].cursor() as cur:
        query = '''
                select course_id, regist_id
                from survey_result
                where course_id= '{course_id}' and regist_id='{regist_id}'
            '''.format(course_id=course_id2,regist_id=user_id)
        cur.execute(query)
        rows = cur.fetchall()

    #print "설문 검증 쿼리====>",query

    if len(rows) !=0 :
        return redirect('/certificates/'+hello)

    context={}
    context['hello']=hello
    context['course_id']=course_id
    context['user_id']=user_id
    context['display_name']= display_name[0][0]

    return render_to_response("community/cert_survey.html",context)

# def dormant_mail(request):
#     email_list = []
#     con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
#                       settings.DATABASES.get('default').get('USER'),
#                       settings.DATABASES.get('default').get('PASSWORD'),
#                       settings.DATABASES.get('default').get('NAME'),
#                       charset='utf8')
#     cur = con.cursor()
#     query = """
#         SELECT email, dormant_mail_cd from auth_user
#     """
#     cur.execute(query)
#     row = cur.fetchall()
#     cur.close()
#
#     for u in row:
#         user = u
#         if user[1] == '15' or user[1] == '30':
#             email_list.append(user[0])
#     # 이메일 전송
#     from_address = configuration_helpers.get_value(
#         'email_from_address',
#         settings.DEFAULT_FROM_EMAIL
#     )
#
#     print 'email_list == ',email_list
#
#     cur = con.cursor()
#     for e in email_list:
#         try:
#             send_mail('테스트 이메일', '이메일 제대로 가나요', from_address, [e], fail_silently=False)
#             query1 = "update auth_user set dormant_mail_cd = '0' where email = '"+e+"' "
#             cur.execute(query1)
#             cur.execute('commit')
#             query1 = "insert into drmt_auth_user_process(email,success) values('"+e+"', '1')"
#             cur.execute(query1)
#             cur.execute('commit')
#         except SMTPException:
#             print 'fail sending email'
#             cur = con.cursor()
#             query1 = "insert into drmt_auth_user_process(email) values('"+e+"')"
#             cur.execute(query1)
#             cur.execute('commit')
#
#
#     cur.close()
#     print 'done'
