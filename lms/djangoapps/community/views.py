#-*- coding: utf-8 -*-
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
import apscheduler.scheduler
from apscheduler.scheduler import Scheduler
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
import MySQLdb as mdb
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
import sys

reload(sys)
sys.setdefaultencoding('utf8')


@ensure_csrf_cookie
def comm_notice(request) :
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
    noti_list = []
    page = 1
    if request.is_ajax():
        data={}
        if request.GET['method'] == 'notice_list' :
            cur = con.cursor()
            if 'cur_page' in request.GET :
                page = request.GET['cur_page']
            query = """
                select
                    (select count(board_id)-(%s-1)*10 from tb_board where section ='N') no,
                    subject,
                    substring(reg_date,1,10) reg_datee,
                    (select ceil(count(board_id)/10) from tb_board where section='N') as total_page,
                    board_id
                from tb_board
                where section='N' and use_yn = 'Y'
            """ % (page)
            if 'cur_page' in request.GET :
                cur_page = request.GET['cur_page']
                if cur_page == '1' :
                    query += "order by reg_date desc " \
                             "limit 0,10"
                    cur.execute(query)
                else :
                    start_num = (int(cur_page)-1)*10
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
                notice = noti
                value_list.append(int(notice[0]))
                value_list.append(notice[1])
                value_list.append(notice[2])
                value_list.append(int(notice[3]))
                value_list.append(notice[4])
                noti_list.append(value_list)
            data = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'search_list' :
            cur = con.cursor()
            if 'cur_page' in request.GET :
                page = request.GET['cur_page']
            query = """
                select
                    (select count(board_id)-(%s-1)*10 from tb_board where section ='N') no,
                    subject,
                    substring(reg_date,1,10) reg_datee,
                    %s total_page,
                    board_id
                from tb_board
                where use_yn = 'Y'
            """ % (page, page)
            if 'search_con' in request.GET :
                title = request.GET['search_con']
                search = request.GET['search_search']
                print 'title == ',title
                if title == 'search_total':
                    query += "and subject like '%"+search+"%' or content like '%"+search+"%' and section='N' "
                else :
                    query += "and subject like '%"+search+"%' and section='N' "

            query += "order by reg_date desc "
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
    if request.is_ajax():
        data={}
        if request.GET['method'] == 'view' :
            cur = con.cursor()
            query = "select subject, content, SUBSTRING(reg_date,1,10) from tb_board where section = 'N' and board_id ="+board_id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            # 파일 이름 구하기
            cur = con.cursor()
            query = "select attatch_file_name from tb_board_attach where board_id = "+board_id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            print 'files == ',str(files)


            value_list.append(row[0][0])
            value_list.append(row[0][1])
            value_list.append(row[0][2])
            if files:
                value_list.append(files[0])
            # print 'value_list == ',value_list

            data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            print 'file_name == ', file_name
            data = json.dumps('/static/file_upload/'+ file_name, cls=DjangoJSONEncoder, ensure_ascii=False)


        return HttpResponse(data, 'application/json')

    context = {
        'id' : board_id
    }
    return render_to_response('community/comm_notice_view.html',context)


@ensure_csrf_cookie
def comm_faq(request) :
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
    if request.is_ajax() :
        if request.GET['method']  == 'faq_list' :
            faq_list = []
            head_title = request.GET['head_title']
            cur = con.cursor()
            query = "select subject, content, head_title from tb_board where section = 'F' and head_title = '"+head_title+"'"
            if 'search' in request.GET :
                search = request.GET['search']
                query += " and subject like '%"+search+"%'"
            cur.execute(query)
            row = cur.fetchall()
            # print str(row)
            # print query

            for f in row:
                value_list = []
                faq = f
                value_list.append(faq[0])
                value_list.append(faq[1])
                value_list.append(faq[2])
                faq_list.append(value_list)
            data = json.dumps(list(faq_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'application/json')
    return render_to_response('community/comm_faq.html')

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
        data={}
        if request.GET['method'] == 'data_list' :
            cur = con.cursor()
            if 'cur_page' in request.GET :
                page = request.GET['cur_page']
            query = """
                select
                    (select count(board_id)-(%s-1)*10 from tb_board where section ='R') no,
                    subject,
                    substring(reg_date,1,10) reg_datee,
                    (select ceil(count(board_id)/10) from tb_board where section='R') as total_page,
                    board_id
                from tb_board
                where section='R' and use_yn = 'Y'
            """ % (page)
            if 'cur_page' in request.GET :
                cur_page = request.GET['cur_page']
                if cur_page == '1' :
                    query += "order by reg_date desc " \
                             "limit 0,10"
                    cur.execute(query)
                else :
                    start_num = (int(cur_page)-1)*10
                    query += "order by reg_date desc " \
                             "limit %s,10" % (start_num)
                    cur.execute(query)
            else:
                query += "order by reg_date desc " \
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
                data_list.append(value_list)
            adata = json.dumps(list(data_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'search_list' :
            cur = con.cursor()
            page = ''
            if 'cur_page' in request.GET :
                page = request.GET['cur_page']
            query = """
                select
                    (select count(board_id)-(%s-1)*10 from tb_board where section ='R') no,
                    subject,
                    substring(reg_date,1,10) reg_datee,
                    %s total_page,
                    board_id
                from tb_board
                where use_yn = 'Y'
            """ % (page, page)
            if 'search_con' in request.GET :
                title = request.GET['search_con']
                search = request.GET['search_search']
                if title == 'search_total':
                    query += "and subject like '%"+search+"%' or content like '%"+search+"%' and section='R' "
                else :
                    query += "and subject like '%"+search+"%' and section='R' "

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
    if request.is_ajax():
        data={}
        if request.GET['method'] == 'view' :
            cur = con.cursor()
            query = "select subject, content, SUBSTRING(reg_date,1,10) from tb_board where section = 'R' and board_id ="+board_id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            # 파일 이름 구하기
            cur = con.cursor()
            query = "select attatch_file_name from tb_board_attach where board_id = "+board_id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            print 'files == ',files

            value_list.append(row[0][0])
            value_list.append(row[0][1])
            value_list.append(row[0][2])
            if files:
                value_list.append(files[0])


            data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            print 'file_name == ', file_name
            data = json.dumps('/static/file_upload/'+ file_name, cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'application/json')

    context = {
        'id' : board_id
    }
    return render_to_response('community/comm_repo_view.html',context)

@ensure_csrf_cookie
def comm_k_news(request) :
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                              settings.DATABASES.get('default').get('USER'),
                              settings.DATABASES.get('default').get('PASSWORD'),
                              settings.DATABASES.get('default').get('NAME'),
                              charset='utf8')
    k_news_list = []
    page = 1
    if request.is_ajax():
        data={}
        if request.GET['method'] == 'k_news_list' :
            cur = con.cursor()
            if 'cur_page' in request.GET :
                page = request.GET['cur_page']
            query = """
                select
                    (select count(board_id)-(%s-1)*10 from tb_board where section ='K') no,
                    subject,
                    substring(reg_date,1,10) reg_datee,
                    (select ceil(count(board_id)/10) from tb_board where section='K') as total_page,
                    board_id
                from tb_board
                where section='K' and use_yn = 'Y'
            """ % (page)
            if 'cur_page' in request.GET :
                cur_page = request.GET['cur_page']
                if cur_page == '1' :
                    query += "order by reg_date desc " \
                             "limit 0,10"
                    cur.execute(query)
                else :
                    start_num = (int(cur_page)-1)*10
                    query += "order by reg_date desc " \
                             "limit %s,10" % (start_num)
                    cur.execute(query)
            else:
                query += "order by reg_date desc " \
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
                k_news_list.append(value_list)
            data = json.dumps(list(k_news_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'search_list' :
            cur = con.cursor()
            if 'cur_page' in request.GET :
                page = request.GET['cur_page']
            query = """
                select
                    (select count(board_id)-(%s-1)*10 from tb_board where section ='K') no,
                    subject,
                    substring(reg_date,1,10) reg_datee,
                    %s total_page,
                    board_id
                from tb_board
                where use_yn = 'Y'
            """ % (page, page)
            if 'search_con' in request.GET :
                title = request.GET['search_con']
                search = request.GET['search_search']
                print 'title == ',title
                if title == 'search_total':
                    query += "and subject like '%"+search+"%' or content like '%"+search+"%' and section='K' "
                else :
                    query += "and subject like '%"+search+"%' and section='K' "

            query += "order by reg_date desc "
            print query
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
    if request.is_ajax():
        data={}
        if request.GET['method'] == 'view' :
            cur = con.cursor()
            query = "select subject, content, SUBSTRING(reg_date,1,10) from tb_board where section = 'K' and board_id ="+board_id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            # 파일 이름 구하기
            cur = con.cursor()
            query = "select attatch_file_name from tb_board_attach where board_id = "+board_id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            print 'files == ',files

            value_list.append(row[0][0])
            value_list.append(row[0][1])
            value_list.append(row[0][2])
            if files:
                value_list.append(files[0])


            data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            print 'file_name == ', file_name
            data = json.dumps('/static/file_upload/'+ file_name, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'application/json')

    context = {
        'id' : board_id
    }
    return render_to_response('community/comm_k_news_view.html',context)

class SMTPException(Exception):
    """Base class for all exceptions raised by this module."""
def test(request):
    email_list = []
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    cur = con.cursor()
    query = """
        SELECT email, dormant_mail_cd from auth_user
    """
    cur.execute(query)
    row = cur.fetchall()
    cur.close()

    for u in row:
        user = u
        if user[1] == '15' or user[1] == '30':
            email_list.append(user[0])
    # 이메일 전송
    from_address = configuration_helpers.get_value(
        'email_from_address',
        settings.DEFAULT_FROM_EMAIL
    )

    print 'email_list == ',email_list

    cur = con.cursor()
    for e in email_list:
        try:
            send_mail('테스트 이메일', '이메일 제대로 가나요', from_address, [e], fail_silently=False)
            query1 = "update auth_user set dormant_mail_cd = '0' where email = '"+e+"' "
            cur.execute(query1)
            cur.execute('commit')
            query1 = "insert into drmt_auth_user_process(email,success) values('"+e+"', '1')"
            cur.execute(query1)
            cur.execute('commit')
        except SMTPException:
            print 'fail sending email'
            cur = con.cursor()
            query1 = "insert into drmt_auth_user_process(email) values('"+e+"')"
            cur.execute(query1)
            cur.execute('commit')


    cur.close()
    return render_to_response('community/test.html')

