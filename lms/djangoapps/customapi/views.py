from django.shortcuts import render
from customapi.models import AuthUser, CoursewareStudentmodule
from django.http import HttpResponse, JsonResponse
from django.core import serializers

from datetime import datetime, timedelta

#from urllib import parse

import logging
log = logging.getLogger(__name__)

#import os
#from urllib import parse

def getServerInfo(request):

#    diskInfo  = os.statvfs('/')

#    used      = diskInfo.f_bsize * (diskInfo.f_blocks - diskInfo.f_bavail)
#    free      = diskInfo.f_bsize * diskInfo.f_bavail
#    total     = diskInfo.f_bsize * diskInfo.f_blocks
    #if not request.user.is_staff or not request.user.is_superuser:
    #json_val = json.dumps(dict1)
    #    raise Http404
    #UserList = AuthUser.objects.filter(is_active=1)
    context = {}
    context['allUserCount'] = AuthUser.objects.count()
    context['loginUserCount'] = AuthUser.objects.filter(last_login__isnull=False).count()
#    context['loginUserCountForWeek'] = AuthUser.objects.filter(last_login__isnull=False).exclude(last_login__gt=datetime.now() - tim$
    context['loginUserCountForWeek'] = AuthUser.objects.filter(last_login__isnull=False).filter(last_login__gt=datetime.now() - timedelta(days=7)).count()

    import psutil
    import math

    obj_Disk = psutil.disk_usage('/')

    log.info(math.ceil(obj_Disk.total / (1024.0 ** 3)))
    log.info(math.ceil(obj_Disk.used / (1024.0 ** 3)))
    log.info(math.ceil(obj_Disk.free / (1024.0 ** 3)))
    log.info(math.ceil(obj_Disk.percent))

    context['totalDisk'] = math.ceil(obj_Disk.total / (1024.0 ** 3))
    context['usedDisk'] = math.ceil(obj_Disk.used / (1024.0 ** 3))
    context['freeDisk'] = math.ceil(obj_Disk.free / (1024.0 ** 3))
    context['usedDisk'] = math.ceil(obj_Disk.percent)
    return JsonResponse(context, safe=False)

def getUserList(request):
    #if not request.user.is_staff or not request.user.is_superuser:
    #json_val = json.dumps(dict1)
    #    raise Http404
    #UserList = AuthUser.objects.filter(is_active=1)
    context = {}
    context['allUserCount'] = AuthUser.objects.count()
    context['loginUserCount'] = AuthUser.objects.filter(last_login__isnull=False).count()
    context['loginUserCountForWeek'] = AuthUser.objects.filter(last_login__isnull=False).exclude(last_login__gt=datetime.now() - timedelta(days=7)).count()

    return JsonResponse(context, safe=False)

    #UserListForJson = serializers.serialize('json', UserList)
    #return HttpResponse(UserListForJson, content_type="text/json-comment-filtered")
    #jsonData = json.dumps(keywordList)

    #return JsonResponse(jsonData, safe=False)

def getVideoList(request):
    #if not request.user.is_staff or not request.user.is_superuser:
    #json_val = json.dumps(dict1)
    #    raise Http404
    import logging
    log = logging.getLogger(__name__)

    studentId = request.GET.get('studentId', 0)
    courseId = request.GET.get('courseId', '')

    #courseId = 'courseId%3dcourse-v1:edX%2bDemoX%2bDemo_Course'

    log.info(studentId)
    log.info(courseId)

    #videoList = CoursewareStudentmodule.objects.filter(course_id__contains=courseId)
    courseId  =  courseId.replace(' ', '+')

    log.info(courseId)

    videoList = CoursewareStudentmodule.objects.filter(course_id=courseId, student_id=studentId, module_type='video')

    videoListForJson = serializers.serialize('json', videoList)
    log.info(videoListForJson)
    return HttpResponse(videoListForJson, content_type="text/json-comment-filtered")

    #context = {}
    #context['allUserCount'] = AuthUser.objects.count()
    #context['loginUserCount'] = AuthUser.objects.filter(last_login__isnull=False).count()
    #context['loginUserCountForWeek'] = AuthUser.objects.filter(last_login__isnull=False).exclude(last_login__gt=datetime.now() - timedelta(days=7)).count()

#    return JsonResponse(context, safe=False)
def getCourseStructure(request):
    import logging
    from openedx.core.djangoapps.content.course_structures.api.v0.api import course_structure as structure
    from opaque_keys.edx.keys import CourseKey
    import json
    course_key = CourseKey.from_string(request.GET.get('key'))
    st = structure(course_key)
    dt = json.dumps(st, ensure_ascii=False)
    return HttpResponse(dt, content_type="text/json-comment-filtered")








# Create your views here.
