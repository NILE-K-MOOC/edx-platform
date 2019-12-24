# -*- coding: utf-8 -*-
import uuid
import json
import logging
import MySQLdb as mdb
import sys
import re
import os.path
import datetime
from django.conf import settings
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest)
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from edxmako.shortcuts import render_to_response
from util.json_request import JsonResponse
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
from django.db import models, connections
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import timedelta
from pytz import timezone
from django.db import connections
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser

import mimetypes
import urllib


def replace_all(string):
    string = string.replace('<', '&lt;');
    string = string.replace('>', '&gt;');
    string = string.replace('"', '&quot;');
    string = string.replace("'", "&#39;");
    return string


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


class TbAttach(models.Model):
    group_name = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.CharField(max_length=255, blank=True, null=True)
    real_name = models.CharField(max_length=255, blank=True, null=True)
    save_name = models.CharField(max_length=255, blank=True, null=True)
    ext = models.CharField(max_length=10, blank=True, null=True)
    real_size = models.IntegerField(blank=True, null=True)
    save_size = models.CharField(max_length=255, blank=True, null=True)
    save_path = models.CharField(max_length=255, blank=True, null=True)
    use_yn = models.IntegerField(default=True)
    regist_id = models.IntegerField(blank=True, null=True)
    regist_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    delete_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_attach'
        app_label = 'tb_attach'


class TbBoardAttach(models.Model):
    attatch_id = models.AutoField(primary_key=True)
    # board_id = models.ForeignKey('TbBoard', on_delete=models.CASCADE, related_name='attaches', null=True)
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
                comm_list = TbBoard.objects.filter(section=section, use_yn='Y').filter(
                    Q(subject__icontains=search_str)).order_by('odby', '-reg_date')
            else:
                comm_list = TbBoard.objects.filter(section=section, use_yn='Y').filter(
                    Q(subject__icontains=search_str) | Q(content__icontains=search_str)).order_by('odby', '-reg_date')
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
                    SELECT 
                        COUNT(id)
                    FROM
                        tb_attach
                    WHERE
                        group_id = {board_id} AND use_yn = 1;
                '''.format(board_id=board_data.board_id)
                cur.execute(query)
                cnt = cur.fetchone()[0]

                if cnt != 0:
                    board_dict['attach_file'] = 'Y'
                else:
                    board_dict['attach_file'] = 'N'

                board_list.append(board_dict)
                # print board_dict

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
def mobile_comm_list(request, section=None, curr_page=None):
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
                comm_list = TbBoard.objects.filter(section=section, use_yn='Y').filter(
                    Q(subject__icontains=search_str)).order_by('odby', '-reg_date')
            else:
                comm_list = TbBoard.objects.filter(section=section, use_yn='Y').filter(
                    Q(subject__icontains=search_str) | Q(content__icontains=search_str)).order_by('odby', '-reg_date')
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
                    SELECT 
                        COUNT(id)
                    FROM
                        tb_attach
                    WHERE
                        group_id = {board_id} AND use_yn = 1;
                '''.format(board_id=board_data.board_id)
                cur.execute(query)
                cnt = cur.fetchone()[0]

                if cnt != 0:
                    board_dict['attach_file'] = 'Y'
                else:
                    board_dict['attach_file'] = 'N'

                board_list.append(board_dict)
                # print board_dict

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

        return render_to_response('community/mobile_comm_list.html', context)


@ensure_csrf_cookie
def comm_view(request, section=None, curr_page=None, board_id=None):
    # print "board_id -> ", board_id

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

    # print "value -> ", rows[0][0]

    if rows[0][0] == 1:
        return render_to_response('community/comm_null.html', context)
    # 게시판 삭제 기능 유효성 체크 [e]

    if board_id is None:
        return redirect('/')

    board = TbBoard.objects.get(board_id=board_id)

    if board:
        # board.files = TbBoardAttach.objects.filter(del_yn='N', board_id=board_id)
        board.files = TbAttach.objects.filter(use_yn=True, group_id=board_id)

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

    # 20191008 관리자의 업로드 경로 변경건 반영
    board.content = board.content.replace('/home/ubuntu/project/management/static/file_upload/', '/static/file_upload/')
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
            comm_list = TbBoard.objects.filter(section='F', use_yn='Y').filter(
                Q(subject__icontains=search_str) | Q(content__icontains=search_str)).order_by('odby', '-reg_date')
        else:
            comm_list = TbBoard.objects.filter(section='F', head_title=head_title, use_yn='Y').order_by('odby',
                                                                                                        '-reg_date')

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
                SELECT save_path, real_name
                  FROM tb_attach
                 WHERE use_yn = TRUE AND id = {file_id};
            '''.format(file_id=file_id)

            cur.execute(query)
            attach_file = cur.fetchone()

        save_path = attach_file[0]
        file_name = attach_file[1]
        save_path = save_path.replace('/static/file_upload', '/staticfiles/file_upload') if attach_file[0] else ''
        real_path = '/edx/var/edxapp' + save_path

        # test
        # real_path = '/edx/app/edxapp/edx-platform/64f4225de45c4c0aaf4314d0c680c9f1'

    except Exception as e:
        print 'comm_file error --- s'
        print e
        print connections['default'].queries
        print 'comm_file error --- e'
        return HttpResponse("<script>alert('파일이 존재하지 않습니다.'); window.history.back();</script>")

    # filepath = file.attach_file_path.replace('/manage/home/static/upload/', '/edx/var/edxapp/staticfiles/file_upload/') if file.attach_file_path else '/edx/var/edxapp/staticfiles/file_upload/'
    # filename = file.attatch_file_name

    print "디렉토리", (os.getcwd())  # 현재 디렉토리의
    print 'file_path', os.path.dirname(os.path.realpath(__file__))
    # print "파일",(os.path.realpath(__file__))  # 파일
    # print "파일의 디렉토리",(os.path.dirname(os.path.realpath(__file__)))  # 파일이 위치한 디렉토리

    # if not file or not os.path.exists(filepath + filename):
    if not attach_file or not os.path.exists(real_path):
        print 'filepath  :', save_path
        return HttpResponse("<script>alert('파일이 존재하지 않습니다..'); window.history.back();</script>")

    # response = HttpResponse(open(real_path, 'rb'), content_type='application/force-download')

    if os.path.exists(real_path) and os.path.isfile(real_path):

        with open(real_path, 'rb') as fp:
            response = HttpResponse(fp.read())

        content_type, encoding = mimetypes.guess_type(file_name)

        if content_type is None:
            content_type = 'application/octet-stream'

        response['Content-Type'] = content_type
        response['Content-Length'] = str(os.stat(real_path).st_size)

        if encoding is not None:
            response['Content-Encoding'] = encoding

        if u'WebKit' in request.META.get('HTTP_USER_AGENT', u'Webkit'):
            filename_header = 'filename="%s"' % file_name.encode('utf-8')
        elif u'MSIE' in request.META.get('HTTP_USER_AGENT', u'MSIE'):
            filename_header = ''
        else:
            filename_header = 'filename*=UTF-8\'\' %s' % urllib.quote(file_name.encode('utf-8'))

        response['Content-Disposition'] = 'attachment; ' + filename_header

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
                'cb_f': '[학점은행제]',
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
                                          WHEN '""" + option + """' = 'cb_f ' THEN '학점은행제'
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


# cbkmooc 연계용 로그인 체크
def cb_login_check(request):
    log = logging.getLogger("edx.cb_kmooc")
    log.info("cb_kmooc login check")
    if request.user == AnonymousUser():
        return_user = False
    else:
        return_user = request.user.id
    return HttpResponse('edxlc("' + str(return_user) + '")')
