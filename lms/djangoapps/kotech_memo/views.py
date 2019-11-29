# -*- coding: utf-8 -*-
import uuid
import json
import logging
import sys
import re
import MySQLdb as mdb
import os.path
import datetime
from django.conf import settings
from django.http import ( HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest )
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
            for item in del_list:
                Memo.objects.filter(memo_id=item).delete()
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
                    comm_list = Memo.objects.filter(receive_id=user_id).filter(Q(title__contains=search_str)).order_by(
                        '-regist_date')
                else:
                    comm_list = Memo.objects.filter(receive_id=user_id).filter(
                        Q(title__contains=search_str) | Q(contents__contains=search_str)).order_by('-regist_date')
            else:
                comm_list = Memo.objects.filter(receive_id=user_id).order_by('-regist_date')

            try:
                p = Paginator(comm_list, page_size)
            except BaseException as err:
                print "Paginator error detail : ", err
                return JsonResponse({"result": 500})
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

                query2 = '''
                      SELECT title,
                             contents,
                             memo_gubun,
                             date_format(ifnull(modify_date, regist_date), '%m.%d') memo_date,
                             memo_id
                        FROM memo
                       WHERE read_date IS NULL AND receive_id = {user_id}
                    ORDER BY memo_id DESC
                       LIMIT 0, 10;
                '''.format(user_id=user_id)

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

            return JsonResponse({"cnt": cnt, "memo_list": memo_list})