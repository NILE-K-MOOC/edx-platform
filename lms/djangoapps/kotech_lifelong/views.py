# -*- coding: utf-8 -*-
import logging
import urllib
import json
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


log = logging.getLogger(__name__)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
    ]


def cb_course(request):

    user_id = request.user.id

    print "--------------------------"
    print "user_id = ", user_id
    print "--------------------------"

    with connections['default'].cursor() as cur:
        query = '''
            select  x.course_id, 
                    y.display_name, 
                    y.course_image,
                    y.professor_name, 
                    y.org,
                    y.major_category,
                    y.weeks,
                    y.credit,
                    Date_format(y.start, '%y.%m.%d. ') as start,
                    Date_format(y.end, '%y.%m.%d. ') as end,
                    x.attendance,
                    x.score
            from cb_course_enroll x
            join cb_course y
            on x.course_id = y.course_id
            where user_id = '{user_id}'
            and x.delete_yn = 'N';
        '''.format(user_id=user_id)
        cur.execute(query)
        rows = dictfetchall(cur)

    print "--------------------------"
    print "rows = ", rows
    print "--------------------------"

    return JsonResponse({'result': rows})


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
