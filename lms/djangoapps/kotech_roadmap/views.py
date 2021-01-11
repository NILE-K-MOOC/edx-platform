# -*- coding: utf-8 -*-
import uuid
import json
import logging
import sys
import re
from datetime import datetime, date
from pytz import utc
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest
from django.shortcuts import redirect
from edxmako.shortcuts import render_to_response
from util.json_request import JsonResponse
from django.db import models, connections
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from courseware.models import CourseOverview
from .models import *
import MySQLdb as mdb

log = logging.getLogger(__name__)


def about_org(request):
    context = {}
    return render_to_response('kotech_roadmap/about_org.html', context)


def about_st(request):
    context = {}
    if request.LANGUAGE_CODE == 'ko-kr':
        return render_to_response('kotech_roadmap/about_st.html', context)
    else:
        return render_to_response('kotech_roadmap/about_st_en.html', context)


def about_intro(request):
    context = {}
    if request.LANGUAGE_CODE == 'ko-kr':
        return render_to_response('kotech_roadmap/about_intro.html', context)
    else:
        return render_to_response('kotech_roadmap/about_intro_en.html', context)


def roadmap(request):

    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')
    cur = con.cursor()

    # group_name 이 존재 하는 리스트
    ai_group_list = list(TbAi.objects.values().filter(group_name__isnull=False))

    # group_name 이 null 인 애들
    query = """
                SELECT 
                    concat(@rn:=@rn + 1) rn,
                    id,
                    target,
                    basic_knowledge,
                    purpose_of_course
                FROM
                    tb_ai AS a
                        JOIN
                    (SELECT @rn:=0) rn
                WHERE
                    group_name IS NULL AND use_yn = 'Y';
                """.format()
    cur.execute(query)
    ai_not_group_list = dictfetchall(cur)

    index = len(ai_not_group_list)

    # group_list_name 뽑기
    query = """
                SELECT 
                    *, CONCAT(@rn:=@rn + 1) rn
                FROM
                    (SELECT 
                        id, target, basic_knowledge, purpose_of_course, group_name
                    FROM
                        tb_ai
                    WHERE
                        group_name IS NOT NULL AND use_yn = 'Y'
                    GROUP BY group_name) t1
                        JOIN
                    (SELECT @rn:={index}) rn;
            """.format(index=index)
    cur.execute(query)
    ai_group_name_list = dictfetchall(cur)

    cur.close()

    context = {
        'ai_not_group_list': ai_not_group_list,
        'ai_group_list': ai_group_list,
        'ai_group_name_list': ai_group_name_list
    }

    return render_to_response('kotech_roadmap/roadmap.html', context)


def roadmap_view(request, id):
    if request.is_ajax():
        course_data = request.GET.get('data')
        print course_data
        if course_data.find('http') == -1:
            org = course_data.split('+')[0]
            course = course_data.split('+')[1]
            not_date = datetime(2030, 01, 01, tzinfo=utc)
            new_course = CourseOverview.objects.filter(org=org, display_number_with_default=course,
                                                       catalog_visibility='both') \
                .exclude(start=not_date).order_by('-start').first()

            try:
                # url = 'http://' + settings.ENV_TOKENS.get('LMS_BASE') + '/courses/' + unicode(new_course.id) + '/about'
                url = request.scheme + '://' + request.META['HTTP_HOST'] + '/courses/' + unicode(new_course.id) + '/about'
            except AttributeError as e:
                log.error(e)
                return JsonResponse({'error': '공개된 강좌가 없습니다.'})
        else:
            url = course_data

        return JsonResponse({'display_name': new_course.display_name, 'org_name': new_course.org, 'url': url})

    node_list = list(TbAiNode.objects.values().filter(ai_id=id, use_yn='Y').all())
    edge_list = list(TbAiEdge.objects.values().filter(ai_id=id, use_yn='Y').all())

    # title = ''
    # if id == 'a01':
    #     title = '컴퓨터공학 전공자'
    # elif id == 'b01':
    #     title = '공학, 자연과학 전공자'
    # elif id == 'c01':
    #     title = '인문, 사회과학을 비롯한 다양한 학문 전공자'
    # elif id == 'd01':
    #     title = '자율주행 분야 (AI+X)'
    # elif id == 'd02':
    #     title = '로보틱스 분야 (AI+X)'
    # elif id == 'd03':
    #     title = '의료 및 헬스케어 분야 (AI+X)'
    # elif id == 'd04':
    #     title = '인지과학 분야 (AI+X)'
    # elif id == 'd05':
    #     title = '경제학 분야 (AI+X)'
    # elif id == 'f01':
    #     title = '호기심 차원에서 인공지능(AI)를 공부하려는 일반인'
    # elif id == 'e01':
    #     title = '기업에 인공지능(AI) 기술 적용을 결정할 수 있는 경영인'
    print "----------edge_list----------"
    print edge_list
    print "----------edge_list----------"
    print "----------node_list----------"
    print node_list
    print "----------node_list----------"

    for edge in edge_list:

        edge['color'] = dict()

        edge['from'] = edge['from_node']
        edge['to'] = edge['to_node']
        edge['color']['opacity'] = edge['opacity']

        edge['regist_date'] = json_serial(edge['regist_date'])

    # for node in node_list:
    #     node['link'] = dict()
    #
    #     link_dict_list = list(TbAiLink.objects.values().filter(ai_id=id, node_id=node['id']))
    #
    #     link_list_data = list()
    #     for link in link_dict_list:
    #         link_list = list()
    #
    #         if link['link_type'] == 'Y':
    #             link_list.append(link['title'])
    #             link_list.append(link['url'])
    #
    #             link_list_data.append(link_list)
    #
    #             node['link'] = link_list_data
    #         else:
    #             node['link'] = link['url']
    #
    #     node['regist_date'] = json_serial(node['regist_date'])

    for node in node_list:
        node['link'] = dict()

        link_dict_list = list(TbAiLink.objects.values().filter(ai_id=id, node_id=node['id'], use_yn='Y'))

        link_list_data = list()
        for link in link_dict_list:
            link_list = list()

            link_list.append(link['title'])
            link_list.append(link['url'])

            link_list_data.append(link_list)

            node['link'] = link_list_data

        node['regist_date'] = json_serial(node['regist_date'])

    node = json.dumps(node_list)
    edge = json.dumps(edge_list)

    context = {}
    context['id'] = id
    context['nodes'] = node
    context['edges'] = edge

    return render_to_response('kotech_roadmap/roadmap_view.html', context)


def roadmap_download(request):
    response = HttpResponse(open('lms/static/images/kotech_roadmap/roadmap_all.jpg', 'rb'),
                            content_type="image/jpeg")
    response['Content-Disposition'] = "attachment; filename=전체 AI 이수체계도.jpg"

    return response


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError("Type %s not serializable" % type(obj))