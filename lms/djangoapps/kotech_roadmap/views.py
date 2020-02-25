# -*- coding: utf-8 -*-
import uuid
import json
import logging
import sys
import re
import datetime
from django.conf import settings
from django.http import ( HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest )
from django.shortcuts import redirect
from edxmako.shortcuts import render_to_response
from util.json_request import JsonResponse
from django.db import models, connections
from django.db import connections
from django.views.decorators.csrf import csrf_exempt


def roadmap(request):

    context = {}
    return render_to_response('kotech_roadmap/roadmap.html', context)


def roadmap_view(request, id):

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