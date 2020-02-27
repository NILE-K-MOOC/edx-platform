# -*- coding: utf-8 -*-
import uuid
import json
import logging
import sys
import re
from datetime import datetime
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

log = logging.getLogger(__name__)


def roadmap(request):

    context = {}
    return render_to_response('kotech_roadmap/roadmap.html', context)


def roadmap_view(request, id):
    if request.is_ajax():
        course_data = request.GET.get('data')
        if course_data.find('+') != -1:
            org = course_data.split('+')[0]
            course = course_data.split('+')[1]
            not_date = datetime(2030, 01, 01, tzinfo=utc)
            new_course = CourseOverview.objects.filter(org=org, display_number_with_default=course,
                                                       catalog_visivility='both')\
                .exclude(start=not_date).order_by('-start').first()

            try:
                url = 'http://' + settings.LMS_BASE + '/courses/' + unicode(new_course.id) + '/about'
            except AttributeError as e:
                log.error(e)
                return JsonResponse({'error': '공개된 강좌가 없습니다.'})
        else:
            url = 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'

        return JsonResponse({'url': url})

    title = ''
    if id == 'a01':
        title = '컴퓨터공학 전공자'
    elif id == 'b01':
        title = '공학, 자연과학 전공자'
    elif id == 'c01':
        title = '인문, 사회과학을 비롯한 다양한 학문 전공자'
    elif id == 'd01':
        title = '자율주행 분야 (AI+X)'
    elif id == 'd02':
        title = '로보틱스 분야 (AI+X)'
    elif id == 'd03':
        title = '의료 및 헬스케어 분야 (AI+X)'
    elif id == 'd04':
        title = '인지과학 분야 (AI+X)'
    elif id == 'd05':
        title = '걍제학 분야 (AI+X)'
    elif id == 'f01':
        title = '호기심 차원에서 인공지능(AI)를 공부하려는 일반인'
    elif id == 'e01':
        title = '기업에 인공지능(AI) 기술 적용을 결정할 수 있는 경영인'

    context = {}
    context['id'] = id
    context['title'] = title
    return render_to_response('kotech_roadmap/roadmap_view.html', context)
