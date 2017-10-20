# -*- coding: utf-8 -*-
""" Views for a student's account information. """

import logging
import json
import urlparse
from datetime import datetime
import logging
import json
import urlparse
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, resolve
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest
)
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django_countries import countries
from edxmako.shortcuts import render_to_response
import pytz
from commerce.models import CommerceConfiguration
from external_auth.login_and_register import (
    login as external_auth_login,
    register as external_auth_register
)
from lang_pref.api import released_languages, all_languages
from openedx.core.djangoapps.commerce.utils import ecommerce_api_client
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.theming.helpers import is_request_in_themed_site
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api.accounts.api import request_password_change
from openedx.core.djangoapps.user_api.errors import UserNotFound
from openedx.core.lib.time_zone_utils import TIME_ZONE_CHOICES
from openedx.core.lib.edx_api_utils import get_edx_api_data
from student.models import UserProfile
from student.views import (
    signin_user as old_login_view,
    register_user as old_register_view
)
from student.helpers import get_next_url_for_login_page
import third_party_auth
from third_party_auth import pipeline
from third_party_auth.decorators import xframe_allow_whitelisted
from util.bad_request_rate_limiter import BadRequestRateLimiter
from util.date_utils import strftime_localized
import commands
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from student.views import register_user
from django.contrib.auth import authenticate
from util.json_request import JsonResponse
import time
import thread
import logging
import logging.handlers
from datetime import datetime
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
import MySQLdb as mdb
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
import sys
import re
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
import datetime

reload(sys)
sys.setdefaultencoding('utf8')


@ensure_csrf_cookie
def comm_notice(request):
    logging.info("############# - start")
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
            # 파일 이름 구하기
            cur = con.cursor()
            query = "select attatch_file_name from tb_board_attach where attatch_file_name <> 'None' and  board_id = " + board_id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # print 'files == ',str(files)

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


def comm_faqrequest(request):
    if request.is_ajax():
        data = json.dumps('fail')
        if request.GET['method'] == 'request':
            con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
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

            if option == 'kmooc_f':
                # send_mail(email+'님의 문의 내용입니다.', request_con, 보내는 사람, ['받는사람'])
                send_mail(email_title, request_con, from_address, ['kmooc@nile.or.kr'])
                save_email = 'kmooc@nile.or.kr'
            else:
                send_mail(email_title, request_con, from_address, ['info_kmooc@nile.or.kr'])
                save_email = 'info_kmooc@nile.or.kr'
            # 문의내용 저장

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

    return render_to_response('community/comm_faqrequest.html')


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
            # 파일 이름 구하기
            cur = con.cursor()
            query = "select attatch_file_name from tb_board_attach where attatch_file_name <> 'None' and board_id = " + board_id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # print 'files == ',files

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
            # 파일 이름 구하기
            cur = con.cursor()
            query = "select attatch_file_name from tb_board_attach where attatch_file_name <> 'None' and  board_id = " + board_id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # print 'files == ',str(files)

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
            # 파일 이름 구하기
            cur = con.cursor()
            query = "select attatch_file_name from tb_board_attach where attatch_file_name <> 'None' and board_id = " + board_id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # print 'files == ',files

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
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    if request.is_ajax:
        total_list = []
        data = json.dumps('ready')
        cur = con.cursor()
        query = """
              SELECT c.*
                FROM (SELECT a.board_id,
                             CASE
                                WHEN a.section = 'N' THEN '[공지사항]'
                                WHEN a.section = 'F' THEN '[Q&A]'
                                WHEN a.section = 'K' THEN '[K-MOOC 뉴스]'
                                WHEN a.section = 'R' THEN '[자료실]'
                                WHEN a.section = 'M' THEN '[모바일]'
                                ELSE ''
                             END
                                head_title,
                             a.subject,
                             a.content,
                             substr(a.mod_date, 1, 11) mod_date,
                             a.section,
                             CASE
                                WHEN a.section = 'N' THEN 1
                                WHEN a.section = 'F' THEN 4
                                WHEN a.section = 'K' THEN 2
                                WHEN a.section = 'R' THEN 3
                                WHEN a.section = 'M' THEN 5
                                ELSE ''
                             END
                                odby,
                             head_title              s,
                             substr(a.reg_date, 1, 11) reg_date
                        FROM tb_board a
                             INNER JOIN (  SELECT section, max(mod_date) mod_date
                                             FROM tb_board
                                            WHERE use_yn = 'Y'
                                         GROUP BY section) b
                                ON (a.section = b.section AND a.mod_date = b.mod_date)) c
            ORDER BY c.odby;
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
