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


@csrf_exempt
def get_org_value(request):
    org = request.POST.get('org')
    user_id = request.user.id

    with connections['default'].cursor() as cur:
        sql = '''
            select b.org_user_id
            from multisite a
            join multisite_member b
            on a.site_id = b.site_id
            where site_name = '{org}'
            and b.user_id = '{user_id}';
        '''.format(org=org, user_id=user_id)

        print sql
        cur.execute(sql)
        try:
            org_user_id = cur.fetchall()[0][0]
        except BaseException:
            org_user_id = 'social'

    return JsonResponse({'result': org_user_id})


@csrf_exempt
def sidebar(request):
    with connections['default'].cursor() as cur:
        sql = '''
            select a.title,a.url,b.save_path,
                case 
                    when a.open = 'Y'  then '_blank'
                    when a.open = 'N' then '_self'
                end as open 
            from tb_sidebar a 
            join tb_attach b on a.icon_url = b.id  
            where a.use_yn = 'Y' 
            order by order_by asc
        '''
        cur.execute(sql)
        data = cur.fetchall()

    return JsonResponse({'data': data})
