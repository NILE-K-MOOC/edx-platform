# -*- coding: utf-8 -*-

import json
import logging
import datetime
from util.json_request import JsonResponse
from edxmako.shortcuts import render_to_response
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db import models, connections


@login_required
def course_satisfaction_survey(request):

    # url encoding 에 의해 course_id 의 '+' 가 필터링되어 파라미터로 넘어옴
    # cert_id 는 이수증 페이지로 리다이렉트하기 위해 사용됨

    # "이수증보기" 및 "강좌 만족도 설문" 클릭 시 넘어오는 공통 파라미터
    cert_id = request.GET['cert_id']        # /certificates/8d1bd287992a436f9ad55c226620b9d3
    course_id = request.GET['course_id']    # course-v1:KangwonK fasd as
    course_id = course_id.replace(" ", "+") # course-v1:KangwonK+fasd+as
    user_id = request.user.id               # 4

    # "강좌 만족도 설문" 클릭 시 넘어오는 독립 파라미터
    # flag = '1' ... 강좌 진행 중 만족도 설문
    # flag = '2' ... 강좌 종료 후 만족도 설문
    # view_yn = 'true' ... 만족도 설문 수정 불가능
    # view_yn = 'false' ... 만족도 설문 수정 가능
    flag = request.GET.get('flag')          # 2
    view_yn = request.GET.get('view')       # true

    if cert_id is not None and cert_id != '/dashboard' and flag is None:
        flag = '2'

    # debug
    print "cert_id -> ", cert_id
    print "course_id -> ", course_id
    print "user_id -> ", user_id
    print "flag -> ", flag
    print "view_yn -> ", view_yn

    if flag == '1' or (flag == '2' and view_yn == 'true'):
        cert_id = ''
        with connections['default'].cursor() as cur:
            query = '''
                SELECT count(*)
                FROM survey_result 
                WHERE course_id = '{course_id}' 
                AND regist_id = {user_id}
                AND survey_gubun = '1';
            '''.format(course_id=course_id, user_id=user_id)
            cur.execute(query)
            survey_cnt = cur.fetchone()[0]

            query = '''
                SELECT display_name
                FROM course_overviews_courseoverview
                WHERE id = '{course_id}'
            '''.format(course_id=course_id)
            cur.execute(query)
            display_name = cur.fetchone()[0]

        if view_yn == 'true':
            data_flag = 'disable'
        elif survey_cnt == 0:
            data_flag = 'insert'
        else:
            data_flag = 'update'
    else:
        cert_id = cert_id.split('/certificates/')
        cert_id = cert_id[1]

        with connections['default'].cursor() as cur:
            query = '''
                select display_name
                from course_overviews_courseoverview
                where id = '{course_id}';
            '''.format(course_id=course_id)
            cur.execute(query)
            display_name = cur.fetchall()[0][0]

            query = '''
                select course_id, min(created_date)
                from certificates_generatedcertificate
                where course_id ='{course_id}'
                group by course_id;
            '''.format(course_id=course_id)
            cur.execute(query)
            rows = cur.fetchall()

            base_time = datetime.datetime(2018, 7, 11, 00, 00, 00)

            if base_time > rows[0][1]:
                return redirect('/certificates/' + cert_id)

            query = '''
                select course_id, regist_id
                from survey_result
                where course_id= '{course_id}' and regist_id='{regist_id}' and survey_gubun = '2'
            '''.format(course_id=course_id, regist_id=user_id)
            cur.execute(query)
            rows = cur.fetchall()

            if len(rows) != 0:
                return redirect('/certificates/' + cert_id)

            query = '''
                SELECT count(*)
                FROM survey_result 
                WHERE course_id = '{course_id}' 
                AND regist_id = {user_id}
                AND survey_gubun = '1';
            '''.format(course_id=course_id, user_id=user_id)
            cur.execute(query)
            survey_cnt = cur.fetchone()[0]

            if survey_cnt == 0:
                data_flag = 'insert'
            else:
                data_flag = 'update'

    context = {}
    context['course_id'] = course_id
    context['user_id'] = user_id
    context['survey_gubun'] = flag
    context['cert_id'] = cert_id
    context['display_name'] = display_name
    context['data_flag'] = data_flag
    return render_to_response("kotech_survey/cert_survey.html", context)


@login_required
def api_course_satisfaction_survey(request):
    if request.is_ajax() and request.POST:
        Q1 = request.POST.get('Q1')
        Q2 = request.POST.get('Q2')
        Q3 = request.POST.get('Q3')
        Q4 = request.POST.get('Q4')
        Q5 = request.POST.get('Q5')
        Q6 = request.POST.get('Q6')
        Q7 = request.POST.get('Q7')
        Q8 = request.POST.get('Q8')
        Q9 = request.POST.get('Q9')
        Q10 = request.POST.get('Q10')
        user_id = request.user.id
        course_id = request.POST.get('course_id')
        survey_gubun = request.POST.get('survey_gubun')
        upsert = request.POST.get('upsert')
        s_seq = request.POST.get('s_seq')

        c_id = course_id.split('course-v1:')[1]
        org = c_id.split('+')[0]
        course = c_id.split('+')[1]

        if upsert == 'insert':
            query = '''
                  INSERT INTO edxapp.survey_result
                              (course_id,
                              question_01,
                              question_02,
                              question_03,
                              question_04,
                              question_05,
                              question_06,
                              question_07,
                              question_08,
                              question_09,
                              question_10,
                              regist_id,
                              org,
                              display_number_with_default,
                              survey_gubun)
                  VALUES ('{course_id}','{q01}','{q02}','{q03}','{q04}','{q05}','{q06}','{q07}','{q08}',
                  '{q09}','{q10}','{regist_id}',
                  '{org}', '{course}', '{survey_gubun}')
            '''.format(course_id=course_id, q01=Q1, q02=Q2, q03=Q3, q04=Q4, q05=Q5,
                       q06=Q6, q07=Q7, q08=Q8, q09=Q9, q10=Q10, regist_id=user_id,
                       org=org, course=course, survey_gubun=survey_gubun)

        else:
            query = '''
                UPDATE survey_result 
                SET 
                    question_01 = '{q01}',
                    question_02 = '{q02}',
                    question_03 = '{q03}',
                    question_04 = '{q04}',
                    question_05 = '{q05}',
                    question_06 = '{q06}',
                    question_07 = '{q07}',
                    question_08 = '{q08}',
                    question_09 = '{q09}',
                    question_10 = '{q10}',
                    org = '{org}',
                    display_number_with_default = '{course}',
                    survey_gubun = '{survey_gubun}',
                    regist_date = NOW()
                WHERE
                    seq = {seq} AND course_id = '{course_id}'
                        AND regist_id = '{user_id}';
            '''.format(q01=Q1, q02=Q2, q03=Q3, q04=Q4, q05=Q5, q06=Q6, q07=Q7, q08=Q8, q09=Q9, q10=Q10,
                       org=org, course=course, survey_gubun=survey_gubun, seq=s_seq, course_id=course_id, user_id=user_id)

        with connections['default'].cursor() as cur:
            cur.execute(query)
            cur.execute('commit')

        return JsonResponse({"return": "success", "next": survey_gubun})

    elif request.is_ajax() and request.GET:  # 설문 결과가 있는 경우 해당 데이터 보냄
        course_id = request.GET.get('course_id')
        user_id = request.user.id
        r_status = request.GET.get('r_status')
        with connections['default'].cursor() as cur:
            query = '''
                SELECT 
                    seq,
                    course_id,
                    question_01,
                    question_02,
                    question_03,
                    question_04,
                    question_05,
                    question_06,
                    question_07,
                    question_08,
                    question_09,
                    question_10,
                    display_name
                FROM
                    survey_result a
                  JOIN
                    course_overviews_courseoverview b ON a.course_id = b.id
                WHERE
                    course_id = '{course_id}' AND regist_id = {user_id} AND survey_gubun = '{r_status}';
                '''.format(course_id=course_id, user_id=user_id, r_status=r_status)
            cur.execute(query)
            survey_data = cur.fetchall()

        s_dict = dict()
        for s in survey_data:
            s_dict['seq'] = s[0]
            s_dict['q1'] = s[2]
            s_dict['q2'] = s[3]
            s_dict['q3'] = s[4]
            s_dict['q4'] = s[5]
            s_dict['q5'] = s[6]
            s_dict['q6'] = s[7]
            s_dict['q7'] = s[8]
            s_dict['q8'] = s[9]
            s_dict['q9'] = s[10]
            s_dict['q10'] = s[11]

        return JsonResponse({'result': s_dict})