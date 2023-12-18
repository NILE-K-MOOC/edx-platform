# -*- coding: utf-8 -*-
import logging
import urllib
import traceback
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

# ==================================================================================================> login 오버라이딩 시작
from datetime import datetime
from datetime import timedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.module_loading import import_string
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'


def load_backend(path):
    return import_string(path)()


def _get_backends(return_tuples=False):
    backends = []
    for backend_path in settings.AUTHENTICATION_BACKENDS:
        backend = load_backend(backend_path)
        backends.append((backend, backend_path) if return_tuples else backend)
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does '
            'AUTHENTICATION_BACKENDS contain anything?'
        )
    return backends


def get_backends():
    return _get_backends(return_tuples=False)


def get_user_model():
    try:
        return django_apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.AUTH_USER_MODEL
        )


def _get_user_session_key(request):
    return get_user_model()._meta.pk.to_python(request.session[SESSION_KEY])


def login(request, user, backend=None):
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
                session_auth_hash and
                not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


# ==================================================================================================> login 오버라이딩 종료


# ==================================================================================================> AES 복호화 함수 시작
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode


def decrypt(key, _iv, enc):
    enc = enc.replace(' ', '+')
    BLOCK_SIZE = 16  # Bytes
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = b64decode(enc)
    iv = _iv
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc)).decode('utf8')


# ==================================================================================================> AES 복호화 함수 종료


@csrf_exempt
def multisite_error(request):
    context = {}

    error = request.GET.get('error')

    print "error -> ", error
    context['header'] = '디버깅 페이지'
    if error == 'error001':
        context['header'] = '등록되어 있지 않은 기관번호입니다.'
        context['info'] = '기관담당자에게 정확한 URL을 문의해주세요'
    if error == 'error002':
        context['info'] = 'in_url(접근URL)과 out_url(등록URL)이 일치하지 않습니다.'
    if error == 'error003':
        return redirect('signin_user')
    if error == 'error004':
        context['info'] = '복호화 데이터 파싱에 실패하였습니다.'
    if error == 'error005':
        context['info'] = '호출시간이 만료되었습니다'
    if error == 'error006':
        context['info'] = '접속한 org(기관번호)와 복호화된 orgid(기관번호)가 일치하지 않습니다.'
    if error == 'error007':
        context['info'] = '기관연계 되지 않은 사번입니다.'

    return render_to_response("multisite_error.html", context)


# ==================================================================================================> 배너 시작
@csrf_exempt
def banner(request):
    return render_to_response("banner.html")


@csrf_exempt
def studentsync(request):
    import requests, xlsxwriter
    try:
        import cStringIO as StringIO
    except ImportError:
        import StringIO
    context = {}
    newinsertdata = []
    searchcourseid = request.GET.get('courseid')
    datastatus = request.GET.get('datastatus')

    if searchcourseid:
        context['courseid'] = searchcourseid
        context['state'] = "true"
        url="https://lms.kmooc.kr/local/coursemos/courseid.php?courseid="+str(searchcourseid)+"&requestfrom=oldkmooc"
        header = ''
        data='{"courseid":str(searchcourseid)}'
        response = requests.post(url, headers=header, data=data)
        if response:
            success = response.json().get("success")

        if success == "success":
            course_new_id = response.json().get("data")
        else:
            course_new_id = ""
        response.close

        print "course_new_id====>",course_new_id

        url = "https://lms.kmooc.kr/local/coursemos/enrol.php?courseid="+str(course_new_id)
        header = ''
        data='{"courseid":str(course_new_id)}'
        response = requests.post(url, headers=header, data=data)
        newkmoocdata = ""
        if response:
            newkmoocdata = response.json().get("data")
        else:
            newkmoocdata = ""
        response.close

        if newkmoocdata:
            now = datetime.now()
            file_output = StringIO.StringIO()
            n_date = now.strftime('%Y%m%d')
            workbook = xlsxwriter.Workbook(file_output)
            worksheet = workbook.add_worksheet('수강등록')
            format_dict = {'align': 'center', 'valign': 'vcenter', 'bold': 'true', 'border': 1}
            header_format = workbook.add_format(format_dict)
            format_dict.pop('bold')
            cell_format = workbook.add_format(format_dict)

            worksheet.write('A2', "USER ID",cell_format)
            worksheet.write('B2', "USER NAME", cell_format)
            worksheet.write('C2', "USER EMAIL", cell_format)
            worksheet.set_column('A:A', 8)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 70)
            worksheet.merge_range('A1:C1', str(searchcourseid).decode('utf-8'), header_format)
            cnt = 2
            ecnt = 3
            for newdata in newkmoocdata:
                try:
                    with connections['default'].cursor() as cur:
                        sql = '''
                            SELECT count(*) FROM student_courseenrollment WHERE user_id = '{userid}' and course_id = '{courseid}'                              
                           '''.format(
                            userid=str(unicode(newdata.get('user_kmooc_edx_id'))),
                            courseid=str(unicode(newdata.get('kmooc_edx_id')))
                        )
                        # print "first sql ===> ",sql
                        cur.execute(sql)
                        memchk = cur.fetchall()[0][0]
                        if memchk == 0:
                            if datastatus == "insert":
                                if str(unicode(newdata.get('kmooc_edx_id'))) == "5":
                                    mode = "honor"
                                elif str(unicode(newdata.get('kmooc_edx_id'))) == "10":
                                    mode = "audit"

                                try:
                                    with connections['default'].cursor() as incur:
                                        query = """
                                            INSERT INTO edxapp.student_courseenrollment
                                                        (user_id,
                                                         course_id,
                                                         created,
                                                         is_active,
                                                         mode
                                                         )
                                            VALUES      ('{0}',
                                                         '{1}',
                                                         now(),
                                                         '1',
                                                         'honor')
                                        """.format(str(unicode(newdata.get('user_kmooc_edx_id'))), str(unicode(newdata.get('kmooc_edx_id'))))
                                        # print "query====>",query
                                        incur.execute(query)
                                    cnt = cnt + 1
                                    worksheet.write('A' + str(cnt), str(unicode(newdata.get('user_kmooc_edx_id'))).decode('utf-8'), cell_format)
                                    worksheet.write('B' + str(cnt), str(unicode(newdata.get('username'))).decode('utf-8'), cell_format)
                                    worksheet.write('C' + str(cnt), str(unicode(newdata.get('email'))).decode('utf-8'), cell_format)
                                except Exception as err:
                                    if ecnt == 3:
                                        worksheet2 = workbook.add_worksheet('없는회원')
                                        worksheet2.merge_range('A1:C1', str(searchcourseid).decode('utf-8'),header_format)
                                        worksheet2.write('A2', "USER ID", cell_format)
                                        worksheet2.write('B2', "USER NAME", cell_format)
                                        worksheet2.write('C2', "USER EMAIL", cell_format)
                                        worksheet2.set_column('A:A', 8)
                                        worksheet2.set_column('B:B', 25)
                                        worksheet2.set_column('C:C', 70)

                                    worksheet2.write('A' + str(ecnt), str(unicode(newdata.get('user_kmooc_edx_id'))).decode('utf-8'), cell_format)
                                    worksheet2.write('B' + str(ecnt), str(unicode(newdata.get('username'))).decode('utf-8'), cell_format)
                                    worksheet2.write('C' + str(ecnt), str(unicode(newdata.get('email'))).decode('utf-8'), cell_format)
                                    ecnt = ecnt + 1
                                    print err
                            newinsertdata.append({
                                'id': str(unicode(newdata.get('user_kmooc_edx_id'))),
                                'username': str(unicode(newdata.get('username'))),
                                'email': str(unicode(newdata.get('email')))
                            })
                except Exception as e:
                    print e

            # print "context data====>",context['data']
            workbook.close()
            context['data'] = newinsertdata
    else:
        context['state'] = "false"
        context['courseid'] = "";
        context['data'] = ""

    if datastatus == "insert":
        file_output.seek(0)
        response = HttpResponse(file_output.read(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename="+str(searchcourseid)+"_" + n_date + ".xlsx"
        return response
    else:
        return render_to_response("studentsync_list.html", context)



@csrf_exempt
def kmoochumanfree(request):
    import requests, unicodedata, time, json
    searchdate = request.GET.get("sdate")
    status = request.GET.get("status")
    url = "https://lms.kmooc.kr/local/coursemos/dormant_cancel.php?date={0}".format(searchdate)
    header = ''
    data = ''
    response = requests.get(url, headers=header, data=data)
    if response:
        newkmoocdata = response.json().get("data")
    else:
        newkmoocdata = ""

    context = {};
    context['date'] = searchdate
    if newkmoocdata:
        newinsertdata = []
        lossinsertdata = []
        for newdata in newkmoocdata:
            listupdatecheck = "true"
            userid = newkmoocdata.get(newdata).get("kmooc_edx_id")
            with connections['default'].cursor() as cur:
                query = """
                    SELECT COUNT(*) as cnt FROM auth_user
                     WHERE id = {0} and email like '%delete.com'
                """.format(userid)
                cur.execute(query)
                memcheck = cur.fetchall()[0][0]
                if memcheck:
                    if status == "sync":
                        print "newdata['kmooc_edx_id']======>",userid
                        try:
                            query = """
                                UPDATE auth_user a
                                       INNER JOIN drmt_auth_user b ON b.dormant_yn = 'Y' AND a.id = b.id
                                   SET a.username = b.username,
                                       a.first_name = b.first_name,
                                       a.last_name = b.last_name,
                                       a.email = b.email,
                                       a.password = b.password,
                                       a.dormant_yn = 'N'
                                 WHERE a.id = '{0}'
                            """.format(userid)
                            cur.execute(query)
                        except BaseException:
                            lossinsertdata.append({
                                'status': 'auth_user',
                                'id': userid,
                                'username': str(newkmoocdata.get(newdata).get("firstname")),
                                'email': str(newkmoocdata.get(newdata).get("email"))
                            })
                            listupdatecheck = "false"

                        try:
                            query = """
                                UPDATE auth_userprofile a
                                       INNER JOIN drmt_auth_userprofile b
                                          ON b.dormant_yn = 'Y' AND a.id = b.id
                                   SET a.name = b.name,
                                       a.language = b.language,
                                       a.location = b.location,
                                       a.meta = b.meta,
                                       a.gender = b.gender,
                                       a.mailing_address = b.mailing_address,
                                       a.year_of_birth = b.year_of_birth,
                                       a.level_of_education = b.level_of_education,
                                       a.goals = b.goals,
                                       a.country = b.country,
                                       a.city = b.city,
                                       a.bio = b.bio
                                 WHERE a.id = '{0}'
                            """.format(userid)
                            cur.execute(query)
                        except BaseException:
                            lossinsertdata.append({
                                'status': 'auth_userprofile',
                                'id': userid,
                                'username': str(newkmoocdata.get(newdata).get("firstname")),
                                'email': str(newkmoocdata.get(newdata).get("email"))
                            })
                            listupdatecheck = "false"

                        try:
                            query = """
                                UPDATE drmt_auth_user
                                   SET dormant_yn = 'N'
                                 WHERE dormant_yn = 'Y' AND id = '{0}';
                            """.format(userid)
                            cur.execute(query)
                        except BaseException:
                            lossinsertdata.append({
                                'status': 'drmt_auth_user',
                                'id': userid,
                                'username': str(newkmoocdata.get(newdata).get("firstname")),
                                'email': str(newkmoocdata.get(newdata).get("email"))
                            })
                            listupdatecheck = "false"

                        try:
                            query = """
                                UPDATE drmt_auth_userprofile
                                   SET dormant_yn = 'N'
                                 WHERE dormant_yn = 'Y' AND id = '{0}';
                            """.format(userid)
                            cur.execute(query)
                        except BaseException:
                            lossinsertdata.append({
                                'status': 'drmt_auth_userprofile',
                                'id': userid,
                                'username': str(newkmoocdata.get(newdata).get("firstname")),
                                'email': str(newkmoocdata.get(newdata).get("email"))
                            })
                            listupdatecheck = "false"

                        if listupdatecheck == "true":
                            newinsertdata.append({
                                'id': userid,
                                'username': str(newkmoocdata.get(newdata).get("firstname")),
                                'email': str(newkmoocdata.get(newdata).get("email"))
                            })
                    else:
                        newinsertdata.append({
                            'id': userid,
                            'username': str(newkmoocdata.get(newdata).get("firstname")),
                            'email': str(newkmoocdata.get(newdata).get("email"))
                        })

    context['data'] = newinsertdata
    context['lossdata'] = lossinsertdata
    return JsonResponse(context)

@csrf_exempt
def kmoocmemactive(request):
    context = ""
    if "id" in request.GET:
        userid = request.GET.get("id")
        with connections['default'].cursor() as cur:
            try:
                query = """
                    UPDATE auth_user a
                           INNER JOIN drmt_auth_user b ON b.dormant_yn = 'Y' AND a.id = b.id
                       SET a.username = b.username,
                           a.first_name = b.first_name,
                           a.last_name = b.last_name,
                           a.email = b.email,
                           a.password = b.password,
                           a.dormant_yn = 'N'
                     WHERE a.id = {0}
                """.format(str(unicode(userid)))
                cur.execute(query)
            except BaseException:
                context = "false"

            try:
                query = """
                    UPDATE auth_userprofile a
                           INNER JOIN drmt_auth_userprofile b
                              ON b.dormant_yn = 'Y' AND a.id = b.id
                       SET a.name = b.name,
                           a.language = b.language,
                           a.location = b.location,
                           a.meta = b.meta,
                           a.gender = b.gender,
                           a.mailing_address = b.mailing_address,
                           a.year_of_birth = b.year_of_birth,
                           a.level_of_education = b.level_of_education,
                           a.goals = b.goals,
                           a.country = b.country,
                           a.city = b.city,
                           a.bio = b.bio
                     WHERE a.id = {0}
                """.format(str(unicode(userid)))
                cur.execute(query)
            except BaseException:
                context = "false"

            try:
                query = """
                    UPDATE drmt_auth_user
                       SET dormant_yn = 'N'
                     WHERE dormant_yn = 'Y' AND id = {0};기
                """.format(str(unicode(userid)))
                cur.execute(query)
            except BaseException:
                context = "false"

            try:
                query = """
                    UPDATE drmt_auth_userprofile
                       SET dormant_yn = 'N'
                     WHERE dormant_yn = 'Y' AND id = {0};
                """.format(str(unicode(userid)))
                cur.execute(query)
            except BaseException:
                context = "false"

        context = {'result': 'true'}
        return JsonResponse(context)
    else:
        context = {'result': 'false'}
        return JsonResponse(context)

@csrf_exempt
def kmoocmempassch(request):
    if "id" in request.POST:
        userid = request.POST.get("id")
        if "userpwd" in request.POST:
            if "pbkdf2_sha256$" in request.POST.get("userpwd"):
                userpwd = request.POST.get("userpwd")
                with connections['default'].cursor() as cur:
                    query = """
                        UPDATE auth_user 
                           SET password = '{1}'
                         WHERE id = '{0}'
                    """.format(str(unicode(userid)),userpwd)
                    cur.execute(query)
                context = {'result': 'true'}
            else:
                context = {'result': 'false'}
        else:
            context = {'result': 'false'}
        return JsonResponse(context)
    else:
        context = {'result': 'false'}
        return JsonResponse(context)

def blankpage(request):
    return render_to_response("blanksync.html")

def privacy(request):
    return render_to_response("privacy.html")

@csrf_exempt
def sericeo(request):
    return render_to_response("sericeo.html")


@csrf_exempt
def sericeo_ubion(request):
    return render_to_response("sericeo_ubion.html")


def invitation_banner_old1(request):
    return render_to_response("invitation-banner2back.html")


def invitation_banner(request):
    return render_to_response("invitation-banner2.html")


def invitation_banner_udemy(request):
    return render_to_response("invitation-banner-udemy.html")


def prev_coursera_course(request):
    return render_to_response("banner3.html")


def coursera_course(request):
    return render_to_response("banner4.html")

def coursera_course_ubion(request):
    return render_to_response("banner5.html")

def matchup(request):
    return render_to_response("matchup_update.html")


def matchup_info(request):
    return render_to_response("matchup_info.html")


def matchup_course(request):
    return render_to_response("matchup_course.html")

from django.contrib.auth.decorators import login_required
from .forms import InvitationForm
from django.shortcuts import render
from .models import Invitation
from django.contrib import messages

@login_required
def invitation_confirm(request):
    # org = request.POST.get('org')
    if request.method == 'POST':
        # 폼 이니셜 값 user_id 할당
        updated_request = request.POST.copy()
        updated_request.update({'user_id': request.user.id})
        form = InvitationForm(updated_request)

        # 중복 참여 alert
        model = Invitation()
        model.phone = request.POST.get('phone')
        model.email = request.POST.get('email')
        # phone_exist = Invitation.objects.filter(phone=model.phone).exists()
        # email_exist = Invitation.objects.filter(email=model.email).exists()
        # if phone_exist or email_exist:
        #     duplicate_user = True
        #     context = {
        #         'duplicate_user': duplicate_user,
        #     }
        #     return render_to_response("invitation-banner2.html", context)

        # 폼 유효성 체크
        if form.is_valid():
            # user_id 저장
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.save()
            messages.success(request, '이벤트에 참여해 주셔서 감사합니다 :)')

            success = True
            context = {
                'success': success,
            }
            return render_to_response("invitation-banner2.html", context)
            # if org == 'coursera':
            #     return render_to_response("invitation-banner2.html", context)
            # elif org == 'udemy':
            #     return render_to_response("invitation-banner-udemy.html", context)
        else:
            print form.errors
            # HTML 형식 alert 불가 #<ul class="errorlist"><li>phone<ul class="errorlist"><li>Invitation with this Phone already exists.</li></ul></li><li>email<ul class="errorlist"><li>Invitation with this Email already exists.</li></ul></li></ul>
            print('form error')
            fail = True
            context = {
                'fail': fail,
            }
            return render_to_response("invitation-banner2.html", context)

            # return render_to_response("invitation-banner2.html")
            # redirect 줄 추가해주지 않으면 아래 render로 가서 깨진 html 이 나옴
            # return redirect('/invitation-banner')        #original
            # return render_to_response("banner-error.html")
    # GET 요청이면 제출용 빈 폼을 생성
    else:
        form = InvitationForm()
    return render(request, 'invitation-banner2.html', {'form': form})  # original

# Udemy ----------------------------------------------------------------------------------------
@login_required
def invitation_confirm_udemy(request):
    if request.method == 'POST':
        # 폼 이니셜 값 user_id 할당
        updated_request = request.POST.copy()
        updated_request.update({'user_id': request.user.id})
        form = InvitationForm(updated_request)

        # 폼 유효성 체크
        if form.is_valid():
            # user_id 저장
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.save()
            success = True
            context = {
                'success': success,
            }
            return render_to_response("invitation-banner-udemy.html", context)

        else:
            print form.errors
            # HTML 형식 alert 불가 #<ul class="errorlist"><li>phone<ul class="errorlist"><li>Invitation with this Phone already exists.</li></ul></li><li>email<ul class="errorlist"><li>Invitation with this Email already exists.</li></ul></li></ul>
            print('form error')
            fail = True
            context = {
                'fail': fail,
            }
            return render_to_response("invitation-banner-udemy.html", context)
    # GET 요청이면 제출용 빈 폼을 생성
    else:
        form = InvitationForm()
    return render(request, 'invitation-banner-udemy.html', {'form': form})
# ==================================================================================================> coursera, udemy end


@csrf_exempt
def multisite_index(request, org):
    # 중앙교육연수원의 추가 정보 입력을 위한 변수
    addinfo = None

    log.info("multisite check multistie_success [%s]" % "multistie_success" in request.session)

    if 'multistie_success' in request.session:
        if request.session['multistie_success'] == 1 and request.user.is_authenticated and 'multisite_org' in request.session:
            return student.views.management.multisite_index(request, user=request.user)

    # 로그인 상태라면 로그아웃 처리

    if request.user and request.user.is_authenticated:
        from django.contrib.auth import logout
        logout(request)

    # 멀티사이트에 온 것을 환영합니다
    request.session['multisite_mode'] = 1
    request.session['multisite_org'] = org

    log.info("multisite check request.session['multisite_mode'] -> %s" % request.session['multisite_mode'])
    log.info("multisite check request.session['multisite_org'] -> %s" % request.session['multisite_org'])

    # 강좌 개수 확인
    with connections['default'].cursor() as cur:
        sql = '''
        select count(*)
        from multisite_course a
        join multisite b
        on a.site_id = b.site_id
        where b.site_code = '{0}';
        '''.format(org)
        cur.execute(sql)
        zero_mode = cur.fetchall()[0][0]

    # zero_mode = 0 # TEST

    # 로그인타입 / 등록URL / 암호화키 획득
    with connections['default'].cursor() as cur:
        sql = '''
        SELECT login_type, site_url, Encryption_key, ifnull(b.save_path, '/static/images/no_images_large.png') save_path
        FROM multisite a
        left join tb_attach b
        on a.logo_img = b.id
        where site_code = '{0}'
        '''.format(org)
        cur.execute(sql)
        rows = cur.fetchall()
        try:
            login_type = rows[0][0]
            out_url = rows[0][1]
            key = rows[0][2]
            save_path = rows[0][3]
        except BaseException as err:
            log.info('multisite check err [%s]' % traceback.format_exc(err))
            return redirect('/multisite_error?error=error001')

    request.session['save_path'] = save_path
    # DEBUG
    print "login_type -> ", login_type
    print "out_url -> ", out_url
    print "key -> ", key
    print "------------------------------------"

    # 접근URL 및 등록URL 획득
    if 'HTTP_REFERER' in request.META:
        in_url = request.META['HTTP_REFERER']
    else:
        in_url = ''
    in_url = in_url.replace('http://', "")
    in_url = in_url.replace('www.', "")
    out_url = out_url.replace('http://', "")
    out_url = out_url.replace('www.', "")

    # DEBUG
    log.info('multisite check in_url -> %s' % in_url)
    log.info('multisite check out_url -> %s' % out_url)
    print "------------------------------------"

    # 접근URL 과 등록URL 비교
    if out_url == 'passkey':
        pass
    elif out_url == 'passurl':
        pass
    elif out_url == 'passparam':
        pass
    elif out_url == 'debug':
        request.session['multistie_success'] = 1
        user = User.objects.get(email='staff@example.com')
        user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
        login(request, user)
        login_type = 'debug'
    else:
        if in_url.find(out_url) == -1:
            # return redirect('/multisite_error?error=error002')
            pass

    # 파라미터 방식
    log.info('multisite check login_type [%s]' % login_type)

    if login_type == 'P':
        # 암호화 데이터 (get, post 구분 없음)
        if request.GET.get('encStr') or request.POST.get('encStr'):
            if request.GET.get('encStr'):
                encStr = request.GET.get('encStr')
            elif request.POST.get('encStr'):
                encStr = request.POST.get('encStr')
        else:
            encStr = None

        log.info('multisite check encStr [%s]' % encStr)

        # encStr 이 있는 경우 세션에 지정
        if encStr:
            request.session['multisite_encStr'] = encStr

        # DEBUG
        # encStr = 'HMSFfWYS/NSUE93/Ra7TfEWuBhTPy9XZiHJoeD+QV+mMVgEEb9ezJ4OyYuDlwuNG'

        if request.user.is_staff:
            return student.views.management.multisite_index(request, user=request.user)

        if out_url == 'passparam' and encStr == None:
            request.session['multisite_mode'] = 2
            return redirect('/login')
        elif (out_url == 'passparam' and encStr != None) or (out_url != 'passparam'):
            # 암호화 데이터 복호화

            try:
                encStr = encStr.replace(' ', '+')

            except BaseException as err:
                log.info('multisite check err1 [%s]' % traceback.format_exc(err))
                return redirect('/multisite_error?error=error003')

            try:
                # url decode 처리
                encStr = urllib.unquote(encStr)

                raw_data = decrypt(key, key, encStr)
                qs = raw_data
                raw_data = raw_data.split('&')

                # addinfo 파라미터가 있는지 체크
                params = parse_qs(qs)

                if 'addinfo' in params:
                    addinfo = params['addinfo'][0]

            except BaseException as err:
                log.info('multisite check err2 [%s]' % traceback.format_exc(err))
                return redirect('/multisite_error?error=error003')
            except Exception as e:
                log.info('multisite check err3 [%s]' % traceback.format_exc(e))

            # DEBUG
            print 'raw_data -> ', raw_data
            print "------------------------------------"

            # 복호화 데이터 파싱
            try:
                calltime = raw_data[0].split('=')[1]
                userid = raw_data[1].split('=')[1]
                orgid = raw_data[2].split('=')[1]

                # 중앙교육 연수원의 경우 addinfo 파라미터를 추가적으로 보내고, 해당 내용은 multisite_member 테이블에 추가정보로 입력한다.
                if len(raw_data) > 3:
                    pass

            except BaseException as err:
                log.info('multisite check err4 [%s]' % traceback.format_exc(err))
                return redirect('/multisite_error?error=error004')

            # DEBUG
            log.info('multisite check calltime [%s] userid [%s] orgid [%s]' % (calltime, userid, orgid))

            # 호출시간 파싱
            calltime = str(calltime)
            year = int(calltime[0:4])
            mon = int(calltime[4:6])
            day = int(calltime[6:8])
            hour = int(calltime[8:10])
            min = int(calltime[10:12])
            sec = int(calltime[12:14])
            java_calltime = datetime(year, mon, day, hour, min, sec)
            python_calltime = datetime.utcnow() + timedelta(hours=9)

            # DEBUG
            log.info('multisite check java_calltime -> %s' % java_calltime)
            log.info('multisite check python_calltime -> %s' % python_calltime)

            # 호출시간 만료 체크
            if java_calltime + timedelta(seconds=180) < python_calltime:
                return redirect('/multisite_error?error=error005')

            # 복호화 기관코드와 접속 기관코드 비교
            if org != orgid:
                return redirect('/multisite_error?error=error006')

            # 기관연계 된 회원인지 확인
            with connections['default'].cursor() as cur:
                sql = '''
                       SELECT user_id
                       FROM multisite_member as a
                       join multisite as b
                       on a.site_id = b.site_id
                       where site_code = '{0}'
                       and org_user_id = '{1}'
                   '''.format(org, userid)

                cur.execute(sql)
                rows = cur.fetchall()

            log.info('multisite check len(rows) -> %s' % len(rows))

            # 기관연계 된 회원이라면 SSO 로그인
            if len(rows) != 0:
                request.session['multistie_success'] = 1
                user = User.objects.get(pk=rows[0][0])
                user.backend = 'ratelimitbackend.backends.RateLimitModelBackend'
                login(request, user)

                # addinfo 가 있다면 DB 저장
                if addinfo and len(addinfo) > 0:
                    try:
                        with connections['default'].cursor() as cur:
                            sql = '''
                                UPDATE multisite_member a
                                        JOIN
                                    multisite b ON a.site_id = b.site_id 
                                SET 
                                    a.addinfo = '{addinfo}'
                                WHERE
                                    b.site_code = '{org}' AND a.org_user_id = '{userid}'                               
                               '''.format(
                                addinfo=addinfo,
                                org=org,
                                userid=userid
                            )
                            cur.execute(sql)
                    except Exception as e:
                        print e

                # test code
                log.info('multisite check zero_mode [%s]' % zero_mode)

                # if zero_mode == 0:
                #     request.session['multisite_zero'] = 1
                #     return redirect('/')

            # 아니라면 에러페이지 리다이렉트
            else:
                log.info('multisite check set multisite_userid [%s]' % userid)

                request.session['multistie_success'] = 1
                request.session['multisite_userid'] = userid
                if addinfo:
                    request.session['multisite_addinfo'] = addinfo

                return redirect('/login')

    # Oauth 방식
    elif login_type == 'O':
        url = 'https://www.kmooc.kr/auth/login/' + str(org) + '/?auth_entry=login&next=%2Forg%2F' + str(org)
        log.info("multisite check url -> %s" % url)
        if not request.user.is_authenticated:
            request.session['multisite_mode'] = 0
            return redirect(url)

    # basic logic
    if request.user.is_authenticated:
        if configuration_helpers.get_value(
                'ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER',
                settings.FEATURES.get('ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER', True)):
            pass
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from openedx.core.djangoapps.external_auth.views import ssl_login
        if not request.GET.get('next'):
            req_new = request.GET.copy()
            req_new['next'] = reverse('dashboard')
            request.GET = req_new
        return ssl_login(request)
    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )
    if enable_mktg_site:
        marketing_urls = configuration_helpers.get_value(
            'MKTG_URLS',
            settings.MKTG_URLS
        )
        return redirect(marketing_urls.get('ROOT'))
    domain = request.META.get('HTTP_HOST')
    if domain and 'edge.edx.org' in domain:
        return redirect(reverse("signin_user"))

    return student.views.management.multisite_index(request, user=request.user)


def multi_index_count(request, org):
    with connections['default'].cursor() as cur:
        query = '''
                SELECT site_id, course_select_type
                FROM   edxapp.multisite
                WHERE  site_code = '{0}'
            '''.format(org)
        cur.execute(query)
        rows = cur.fetchall()
    try:
        site_id = rows[0][0]
        search_word = request.POST.get('search_word')
    except BaseException:
        return redirect('/multisite_error?error=error001')

    with connections['default'].cursor() as cur:
        query = '''
                        SELECT
                            a.id course_id
                            , b.audit_yn
                            , b.ribbon_yn
                            , CASE WHEN INSTR(b.teacher_name, ',') = 0 
                                   THEN b.teacher_name
                                ELSE CONCAT(SUBSTRING_INDEX(b.teacher_name, ',', 1), ' 외 ', LENGTH(b.teacher_name) - LENGTH(REPLACE(b.teacher_name, ',', '')), '명')
                              END teacher_name
                            , START
                            ,
                        END
                        FROM
                            course_overviews_courseoverview a
                        , course_overview_addinfo b
                        , multisite_course c
                        WHERE
                            a.id = b.course_id
                        AND b.course_id = c.course_id
                        AND START < date('2030/01/01')
                        AND c.site_id = '{site_id}'
                        AND LOWER(id) NOT LIKE '%demo%'
                        AND LOWER(id) NOT LIKE '%nile%'
                        AND LOWER(id) NOT LIKE '%test%'
                        AND a.enrollment_start < now()
                        AND a.catalog_visibility != 'none'
                        -- AND now() BETWEEN a.START AND a.END
                        AND a.display_name like '%{search_word}%'
                        ORDER BY
                            enrollment_start DESC
                        , `START` DESC
                        , enrollment_end DESC
                        , `END` DESC
                        , display_name
                    '''.format(site_id=site_id, search_word=search_word)

        cur.execute(query)
        result_table = cur.fetchall()

    return JsonResponse({'a': len(result_table)})


def get_multisite_list(request):
    user_id = request.POST.get('user_id')

    with connections['default'].cursor() as cur:
        sql = '''
            SELECT site_code, org_user_id, site_name
            FROM multisite_member AS a
            JOIN multisite AS b
            ON a.site_id = b.site_id
            WHERE user_id = {user_id}
        '''.format(user_id=user_id)

        print sql

        cur.execute(sql)
        rows = cur.fetchall()

    if len(rows) == 0:
        return JsonResponse({'return': 'zero'})

    print "------------------------> hello s"
    print "user_id = ", user_id
    print "------------------------> hello e"

    return JsonResponse({'return': rows})


def get_org_list(request):
    with connections['default'].cursor() as cur:
        query = """
            SELECT detail_code, detail_name
              FROM code_detail
             WHERE group_code = 003
             AND USE_YN = 'Y'
             ORDER BY detail_name;
        """
        cur.execute(query)
        org_index = cur.fetchall()
        org_list = list(org_index)
        org_count = len(org_list)

    return JsonResponse({'result': org_list, 'count': org_count})


def delete_multisite_account(request):
    user_id = request.POST.get('user_id')
    org = request.POST.get('org')

    with connections['default'].cursor() as cur:
        sql = '''
            delete a
            from multisite_member as a
            join multisite as b
            on a.site_id = b.site_id
            where b.site_code = '{org}' and a.user_id = '{user_id}'
        '''.format(org=org, user_id=user_id)

        print sql

        cur.execute(sql)

    return JsonResponse({'return': 'success'})


@ensure_csrf_cookie
@transaction.non_atomic_requests
@cache_if_anonymous()
def index(request):
    """
    Redirects to main page -- info page if user authenticated, or marketing if not
    수정시 mobile_index도 함께 수정해야함
    """

    # 멀티사이트 이용중 홈페이지로 이동했을경우 session 을 클리어
    if 'multisite_org' in request.session:
        log.info('multisite check clear request.session ------------------------ s')
        for key in request.session.keys():
            if str(key).startswith('multisite'):
                log.info('multisite check delete session key: [%s]' % key)
                del request.session[key]
        log.info('multisite check clear request.session ------------------------ e')

    if request.user.is_authenticated:
        # Only redirect to dashboard if user has
        # courses in his/her dashboard. Otherwise UX is a bit cryptic.
        # In this case, we want to have the user stay on a course catalog
        # page to make it easier to browse for courses (and register)
        if configuration_helpers.get_value(
                'ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER',
                settings.FEATURES.get('ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER', True)):
            pass
            # return redirect(reverse('dashboard'))

    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from openedx.core.djangoapps.external_auth.views import ssl_login
        # Set next URL to dashboard if it isn't set to avoid
        # caching a redirect to / that causes a redirect loop on logout
        if not request.GET.get('next'):
            req_new = request.GET.copy()
            req_new['next'] = reverse('dashboard')
            request.GET = req_new
        return ssl_login(request)

    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        marketing_urls = configuration_helpers.get_value(
            'MKTG_URLS',
            settings.MKTG_URLS
        )
        return redirect(marketing_urls.get('ROOT'))

    domain = request.META.get('HTTP_HOST')

    # keep specialized logic for Edge until we can migrate over Edge to fully use
    # configuration.
    if domain and 'edge.edx.org' in domain:
        return redirect(reverse("signin_user"))

    #  we do not expect this case to be reached in cases where
    #  marketing and edge are enabled
    return student.views.management.index(request, user=request.user)


@ensure_csrf_cookie
@transaction.non_atomic_requests
@cache_if_anonymous()
def mobile_index(request):
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from openedx.core.djangoapps.external_auth.views import ssl_login
        # Set next URL to dashboard if it isn't set to avoid
        # caching a redirect to / that causes a redirect loop on logout
        if not request.GET.get('next'):
            req_new = request.GET.copy()
            req_new['next'] = reverse('dashboard')
            request.GET = req_new
        return ssl_login(request)

    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        marketing_urls = configuration_helpers.get_value(
            'MKTG_URLS',
            settings.MKTG_URLS
        )
        return redirect(marketing_urls.get('ROOT'))

    #  we do not expect this case to be reached in cases where
    #  marketing and edge are enabled
    return student.views.management.mobile_index(request, user=request.user)


@ensure_csrf_cookie
# @cache_if_anonymous()
def courses(request):
    """
    Render the "find courses" page. If the marketing site is enabled, redirect
    to that. Otherwise, if subdomain branding is on, this is the university
    profile page. Otherwise, it's the edX courseware.views.views.courses page
    수정시 mobile_courses도 함께 수정
    """
    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        return redirect(marketing_link('COURSES'), permanent=True)

    if not settings.FEATURES.get('COURSES_ARE_BROWSABLE'):
        raise Http404

    #  we do not expect this case to be reached in cases where
    #  marketing is enabled or the courses are not browsable
    return courseware.views.views.courses(request)


@ensure_csrf_cookie
# @cache_if_anonymous()
def mobile_courses(request):
    """
    Render the "find courses" page. If the marketing site is enabled, redirect
    to that. Otherwise, if subdomain branding is on, this is the university
    profile page. Otherwise, it's the edX courseware.views.views.courses page
    """

    # search_query 여부에따라 강좌 검색과 모바일 메인 페이지 분기
    search_query = request.GET.get('search_query')
    if search_query is None:
        return mobile_index(request)

    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )

    if enable_mktg_site:
        return redirect(marketing_link('COURSES'), permanent=True)

    if not settings.FEATURES.get('COURSES_ARE_BROWSABLE'):
        raise Http404

    #  we do not expect this case to be reached in cases where
    #  marketing is enabled or the courses are not browsable
    return courseware.views.views.mobile_courses(request)


def _footer_static_url(request, name):
    """Construct an absolute URL to a static asset. """
    return request.build_absolute_uri(staticfiles_storage.url(name))


def _footer_css_urls(request, package_name):
    """Construct absolute URLs to CSS assets in a package. """
    # We need this to work both in local development and in production.
    # Unfortunately, in local development we don't run the full asset pipeline,
    # so fully processed output files may not exist.
    # For this reason, we use the *css package* name(s), rather than the static file name
    # to identify the CSS file name(s) to include in the footer.
    # We then construct an absolute URI so that external sites (such as the marketing site)
    # can locate the assets.
    package = settings.PIPELINE_CSS.get(package_name, {})
    paths = [package['output_filename']] if not settings.DEBUG else package['source_filenames']
    return [
        _footer_static_url(request, path)
        for path in paths
    ]


def _render_footer_html(request, show_openedx_logo, include_dependencies, include_language_selector):
    """Render the footer as HTML.

    Arguments:
        show_openedx_logo (bool): If True, include the OpenEdX logo in the rendered HTML.
        include_dependencies (bool): If True, include JavaScript and CSS dependencies.
        include_language_selector (bool): If True, include a language selector with all supported languages.

    Returns: unicode

    """
    bidi = 'rtl' if translation.get_language_bidi() else 'ltr'
    css_name = settings.FOOTER_CSS['openedx'][bidi]

    context = {
        'hide_openedx_link': not show_openedx_logo,
        'footer_js_url': _footer_static_url(request, 'js/footer-edx.js'),
        'footer_css_urls': _footer_css_urls(request, css_name),
        'bidi': bidi,
        'include_dependencies': include_dependencies,
        'include_language_selector': include_language_selector
    }

    return render_to_response("footer.html", context)


@cache_control(must_revalidate=True, max_age=settings.FOOTER_BROWSER_CACHE_MAX_AGE)
def footer(request):
    """Retrieve the branded footer.

    This end-point provides information about the site footer,
    allowing for consistent display of the footer across other sites
    (for example, on the marketing site and blog).

    It can be used in one of two ways:
    1) A client renders the footer from a JSON description.
    2) A browser loads an HTML representation of the footer
        and injects it into the DOM.  The HTML includes
        CSS and JavaScript links.

    In case (2), we assume that the following dependencies
    are included on the page:
    a) JQuery (same version as used in edx-platform)
    b) font-awesome (same version as used in edx-platform)
    c) Open Sans web fonts

    Example: Retrieving the footer as JSON

        GET /api/branding/v1/footer
        Accepts: application/json

        {
            "navigation_links": [
                {
                  "url": "http://example.com/about",
                  "name": "about",
                  "title": "About"
                },
                # ...
            ],
            "social_links": [
                {
                    "url": "http://example.com/social",
                    "name": "facebook",
                    "icon-class": "fa-facebook-square",
                    "title": "Facebook",
                    "action": "Sign up on Facebook!"
                },
                # ...
            ],
            "mobile_links": [
                {
                    "url": "http://example.com/android",
                    "name": "google",
                    "image": "http://example.com/google.png",
                    "title": "Google"
                },
                # ...
            ],
            "legal_links": [
                {
                    "url": "http://example.com/terms-of-service.html",
                    "name": "terms_of_service",
                    "title': "Terms of Service"
                },
                # ...
            ],
            "openedx_link": {
                "url": "http://open.edx.org",
                "title": "Powered by Open edX",
                "image": "http://example.com/openedx.png"
            },
            "logo_image": "http://example.com/static/images/logo.png",
            "copyright": "EdX, Open edX and their respective logos are trademarks or registered trademarks of edX Inc."
        }


    Example: Retrieving the footer as HTML

        GET /api/branding/v1/footer
        Accepts: text/html


    Example: Including the footer with the "Powered by Open edX" logo

        GET /api/branding/v1/footer?show-openedx-logo=1
        Accepts: text/html


    Example: Retrieving the footer in a particular language

        GET /api/branding/v1/footer?language=en
        Accepts: text/html


    Example: Retrieving the footer with a language selector

        GET /api/branding/v1/footer?include-language-selector=1
        Accepts: text/html


    Example: Retrieving the footer with all JS and CSS dependencies (for testing)

        GET /api/branding/v1/footer?include-dependencies=1
        Accepts: text/html

    """
    if not branding_api.is_enabled():
        raise Http404

    # Use the content type to decide what representation to serve
    accepts = request.META.get('HTTP_ACCEPT', '*/*')

    # Show the OpenEdX logo in the footer
    show_openedx_logo = bool(request.GET.get('show-openedx-logo', False))

    # Include JS and CSS dependencies
    # This is useful for testing the end-point directly.
    include_dependencies = bool(request.GET.get('include-dependencies', False))

    # Override the language if necessary
    language = request.GET.get('language', translation.get_language())
    try:
        language = get_supported_language_variant(language)
    except LookupError:
        language = settings.LANGUAGE_CODE

    # Include a language selector
    include_language_selector = request.GET.get('include-language-selector', '') == '1'

    # Render the footer information based on the extension
    if 'text/html' in accepts or '*/*' in accepts:
        cache_params = {
            'language': language,
            'show_openedx_logo': show_openedx_logo,
            'include_dependencies': include_dependencies
        }
        if include_language_selector:
            cache_params['language_selector_options'] = ','.join(sorted([lang.code for lang in released_languages()]))
        cache_key = u"branding.footer.{params}.html".format(params=urllib.urlencode(cache_params))

        content = cache.get(cache_key)
        if content is None:
            with translation.override(language):
                content = _render_footer_html(
                    request, show_openedx_logo, include_dependencies, include_language_selector
                )
                cache.set(cache_key, content, settings.FOOTER_CACHE_TIMEOUT)
        return HttpResponse(content, status=200, content_type="text/html; charset=utf-8")

    elif 'application/json' in accepts:
        cache_key = u"branding.footer.{params}.json".format(
            params=urllib.urlencode({
                'language': language,
                'is_secure': request.is_secure(),
            })
        )
        footer_dict = cache.get(cache_key)
        if footer_dict is None:
            with translation.override(language):
                footer_dict = branding_api.get_footer(is_secure=request.is_secure())
                cache.set(cache_key, footer_dict, settings.FOOTER_CACHE_TIMEOUT)
        return JsonResponse(footer_dict, 200, content_type="application/json; charset=utf-8")

    else:
        return HttpResponse(status=406)





@login_required
@ensure_csrf_cookie
def vodfile_move_one(request):
    from os.path import exists
    import math
    import MySQLdb as mdb
    import time
    coursetmp = []
    if "courseid" in request.GET:
        courseid = request.GET.get("courseid","")
        courseidtmp = courseid.replace(" ","+")
        print "courseid===>",courseidtmp
        coursetmp.append(courseidtmp)
        print "coursetmp===>",coursetmp
    else:
        # coursetmp.append("course-v1:EwhaK+EW36387K+2015-04")
        # coursetmp.append("course-v1:EwhaK+EW10771K+2015-03")
        # coursetmp.append("course-v1:EwhaK+EW10164K+2015-01")
        # coursetmp.append("course-v1:SKKUk+SKKU_BUS3033.01K+2016_SKKU01")
        # coursetmp.append("course-v1:SMUCk+SMUC01k+2017_T1")
        # coursetmp.append("course-v1:SMUCk+SMUC02k+2017_T2")
        # coursetmp.append("course-v1:UOUk+UOU101.02k+U101B.1")
        # coursetmp.append("course-v1:SKKUk+SKKU_GEDH042.01K+2016_SKKU04")
        # coursetmp.append("course-v1:KonYangK+ACE.KY002+KY2016A02")
        # coursetmp.append("course-v1:KNUk+CORE.KNUk01+2016_S1")
        # coursetmp.append("course-v1:SKKUk+SKKU_GEDH043.O1K+2017_T1_0")
        # coursetmp.append("course-v1:EwhaK+EW22126K+2017_F11")
        # coursetmp.append("course-v1:DGUk+DGUk_004k+DGU_004k_2017_9_4")
        # coursetmp.append("course-v1:DGUk+DGUk_005k+DGU_005k_2017_9_5")
        # coursetmp.append("course-v1:KHUk+KH304+2017_KH304")
        # coursetmp.append("course-v1:KHUk+FD_KH305+2017_KH305")
        # coursetmp.append("course-v1:KHUk+FD_KH306+2017_KH306")
        # coursetmp.append("course-v1:SKKUk+FD_SKKU_GEDH061.O1K+2017_T1_0")
        # coursetmp.append("course-v1:SKKUk+FD_SKKU_GEDH062_O1K+2017_T1_0")
        # coursetmp.append("course-v1:PTUk+SF_PMOOC01k+2017_T2")
        # coursetmp.append("course-v1:KonkukK+PRIME_konkuk_P001+2017_1")
        # coursetmp.append("course-v1:DonggukK+ACE_FA_DGU02k+2017_T1")
        # coursetmp.append("course-v1:EwhaK+CORE_EW16001C+2017_F09")
        # coursetmp.append("course-v1:DGUk+DGU_006k+DGU_006k_2018_9_6")
        # coursetmp.append("course-v1:DGUk+DGU-007k+DGU-007k_2018_9_7")
        # coursetmp.append("course-v1:DGUk+DGU_008k+DGU_008k_2018_9_8")
        # coursetmp.append("course-v1:DGUk+DGU_009k+DGU_009k_2018_9_9")
        # coursetmp.append("course-v1:SMUk+SMU2018_02+2018_2_T2")
        # coursetmp.append("course-v1:SOGANGk+SOGANG06K+2018_T3")
        # coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc05K+2018_2")
        # coursetmp.append("course-v1:HYUk+CORE_HYUKMOOC2018-2k+2018_C2")
        # coursetmp.append("course-v1:DKUK+MOOC_DKUK0006+2019_T2")
        # coursetmp.append("course-v1:DKUK+MOOC_DKUK0008+2019_T2")
        # coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc09K+2019_T2")
        # coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc10K+2019_T2")
        # coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc11K+2019_T2")
        # coursetmp.append("course-v1:DongdukK+DDU04+2019_T2")
        # coursetmp.append("course-v1:SSUk+SSMOOC14K+2019_T2")
        # coursetmp.append("course-v1:INU+INU004+2019_L2")
        # coursetmp.append("course-v1:AYUk+AYUk_EM_01+2019_T2")
        # coursetmp.append("course-v1:CNUk+MOE_CNU10+2019_2_10")
        # coursetmp.append("course-v1:DKUK+MOOC_DKUK0017+2019_T2")
        # coursetmp.append("course-v1:HYUk+IV_HYUKMOOC2019-1k+2019_C1")
        # coursetmp.append("course-v1:XuetangX+XuetangX_01+2020_T1")
        # coursetmp.append("course-v1:XuetangX+XuetangX_02+2020_T1")
        # coursetmp.append("course-v1:XuetangX+XuetangX_03+2020_T1")
        # coursetmp.append("course-v1:KSUk+KSUk_10+2020_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_11+2020_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_12+2020_T2")
        # coursetmp.append("course-v1:DGUk+DGU_011k+DGU_011k_2020_12_11")
        # coursetmp.append("course-v1:DGUk+DGU_012k+DGU_012k_2020_12_12")
        # coursetmp.append("course-v1:DHUk+DHUk07k+2020_T2")
        # coursetmp.append("course-v1:DHUk+DHUk08k+2020_T2")
        # coursetmp.append("course-v1:DHUk+DHUk09k+2020_T2")
        # coursetmp.append("course-v1:DHUk+DHUk10k+2020_T2")
        # coursetmp.append("course-v1:PNUk+PE_C01+2020_KM019")
        # coursetmp.append("course-v1:HonamUniv+HCTL01+2021_6")
        # coursetmp.append("course-v1:KHUk+KH502+2020_T2_1")
        # coursetmp.append("course-v1:DGUk+DGU_017k+DGU_017k_2020_12_17")
        # coursetmp.append("course-v1:DGUk+DGU_015k+DGU_015k_2020_12_15")
        # coursetmp.append("course-v1:KHUk+KH505+2020_T2_1")
        # coursetmp.append("course-v1:DGUk+DGU_016k+DGU_016k_2020_12_16")
        # coursetmp.append("course-v1:SKKUk+SKKU_47+2020_T1")
        # coursetmp.append("course-v1:SKKUk+SKKU_48+2020_T1")
        # coursetmp.append("course-v1:SKKUk+SKKU_49+2020_T1")
        # coursetmp.append("course-v1:KPU+KPU02+2020_T2")
        # coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc12K+2020_T2")
        # coursetmp.append("course-v1:EBS+EBS001+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS002+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS003+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS004+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS005+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS006+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS007+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS008+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS009+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS010+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS011+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS012+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS013+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS014+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS015+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS016+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS017+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS018+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS019+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS020+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS021+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS022+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS023+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS024+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS025+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS026+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS027+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS028+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS029+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS030+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS031+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS032+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS033+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS034+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS035+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS036+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS037+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS038+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS039+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS040+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS041+2021_T1")
        # coursetmp.append("course-v1:EBS+EBS042+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC001+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC002+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC003+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC004+2021_T1")
        # coursetmp.append("course-v1:JTBC+EBS005+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC006+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC007+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC008+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC009+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC010+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC011+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC015+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC012+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC013+2021_T1")
        # coursetmp.append("course-v1:JTBC+JTBC014+2021_T1")
        # coursetmp.append("course-v1:KSUk+KSUk_14+2021_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_15+2021_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_16+2021_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_17+2021_T2")
        # coursetmp.append("course-v1:DGUk+DGU_019k+DGU_018k_2021")
        # coursetmp.append("course-v1:DGUk+DGU_018k+DGU_018k_2021")
        # coursetmp.append("course-v1:DGUk+DGU_020k+DGU_020k_2021")
        # coursetmp.append("course-v1:DGUk+DGU_021k+DGU_021k_2021")
        # coursetmp.append("course-v1:DHUk+DHUk12k+2021_T2")
        # coursetmp.append("course-v1:DHUk+DHUk13k+2021_T2")
        # coursetmp.append("course-v1:DHUk+DHUk14k+2021_T2")
        # coursetmp.append("course-v1:PNUk+MS_C01+2021_N1")
        # coursetmp.append("course-v1:JJU+JJU04+2021_J04")
        # coursetmp.append("course-v1:AYUk+AYUK_IP_0+2021_T2_1")
        # coursetmp.append("course-v1:DSUk+UI.DSU01+2021_T2")
        # coursetmp.append("course-v1:DCU+DCU01+2021_1")
        # coursetmp.append("course-v1:XuetangX+THc2021+2022T1")
        # coursetmp.append("course-v1:EBS+EBS001+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS002+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS003+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS004+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS005+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS006+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS007+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS008+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS009+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS010+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS011+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS012+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS013+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS014+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS015+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS016+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS017+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS018+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS019+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS020+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS021+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS022+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS023+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS024+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS025+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS217+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS227+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS228+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS229+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS230+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS231+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS232+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS233+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS234+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS235+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS236+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS237+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS238+2022_T1")
        # coursetmp.append("course-v1:EBS+EBS240+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC001+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC002+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC003+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC004+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC005+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC006+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC007+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC008+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC009+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC010+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC011+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC012+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC013+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC014+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC015+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC016+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC017+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC018+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC019+2022_T1")
        # coursetmp.append("course-v1:JTBC+JTBC020+2022_T1")
        # coursetmp.append("course-v1:KSUk+KSUk_18+2022_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_19+2022_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_20+2022_T2")
        # coursetmp.append("course-v1:KSUk+KSUk_21+2022_T2")
        # coursetmp.append("course-v1:DHUk+DHU17k+2022_T2")
        # coursetmp.append("course-v1:DHUk+DHU18k+2022_T2")
        # coursetmp.append("course-v1:DHUk+DHU19k+2022_T2")
        # coursetmp.append("course-v1:DHUk+DHU20k+2022_T2")
        # coursetmp.append("course-v1:WHSUK+WHSUK_06+2022-T2-6")
        # coursetmp.append("course-v1:WHSUK+WHSUK_07+2022-T2-7")
        # coursetmp.append("course-v1:WHSUK+WHSUK_08+2022-T2-8")
        # coursetmp.append("course-v1:WHSUK+WHSUK_09+2022-T2-9")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_108+2022_1")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA001+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA002+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA003+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA004+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA005+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA006+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA007+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA008+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA009+2022_01")
        # coursetmp.append("course-v1:KAEP_INHA+KINHA010+2022_01")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU01+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU02+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU03+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU04+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU05+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU06+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU07+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU08+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU09+2022_T1")
        # coursetmp.append("course-v1:KAEP_KHU+KKHU10+2022_T1")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA001+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA002+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA003+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA004+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA005+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA006+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA007+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA008+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA009+2022_01")
        # coursetmp.append("course-v1:KAEP_KOREA+KKOREA010+2022_01")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_106+2022_1")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_104+2022_1")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_103+2022_1")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_102+2022_1")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_107+2022_1")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_109+2022_1")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_110+2022_1")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_105+2022_1")
        # coursetmp.append("course-v1:AYUk+AYUk_SP+2023_T1")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA101+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA102+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA103+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA104+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA105+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA106+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA107+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA108+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA109+2022_01")
        # coursetmp.append("course-v1:KEKA_SNU+KEKA110+2022_01")
        # coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_101+2022_1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP01+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP02+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP03+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP04+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP05+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP06+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP07+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP08+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP09+2022_T1")
        # coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP10+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP01+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP02+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP03+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP04+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP05+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP06+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP07+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP08+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP09+2022_T1")
        # coursetmp.append("course-v1:SOGANGKAEP+KAEP10+2022_T1")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH109+2023_A109")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH108+2023_A108")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH107+2023_A107")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH106+2023_A106")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH105+2023_A105")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH104+2023_A104")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH103+2023_A103")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH102+2023_A102")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH110+2023_A110")
        # coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH101+2023_A101")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP01+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP02+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP03+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP04+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP05+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP06+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP07+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP08+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP09+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP10+2022_T1")
        # coursetmp.append("course-v1:KAEP_SKKU+KAEP11+2022_T1")
        # coursetmp.append("course-v1:CKL_SNU+cklsnu08+2023_T1")
        # coursetmp.append("course-v1:CKL_SNU+cklsnu07+2023_T1")
        # coursetmp.append("course-v1:CKL_SNU+cklsnu06+2023_T1")
        # coursetmp.append("course-v1:CKL_SNU+cklsnu09+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu03+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu02+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu05+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu01+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu04+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu10+2023_T1")
        coursetmp.append("course-v1:SKKUk+SKKU_LAO2301+2023_T1")
        coursetmp.append("course-v1:SKKUk+SKKU_LAO2302+2023_T1")
        # coursetmp.append("course-v1:SunMoonK+SMKMOOC-05+2023_T2")
        # coursetmp.append("course-v1:DH+sdfsdfsdf+20230630")

        coursetmp2 = []
        coursetmp2.append("course-v1:SunMoonK+SMKMOOC-05+2023_T2")
        coursetmp2.append("course-v1:DH+sdfsdfsdf+20230630")

    chapter_list = []
    try:
        m_host = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host')
        m_port = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port')
        client = MongoClient(m_host, m_port)
        db = client.edxapp
        mdlcon = mdb.connect('192.168.1.245', 'openlms', 'dhvms@23gkrTmq', 'openlms', charset='utf8')
        #mdlcon = mdb.connect('118.67.152.82', 'root', 'anzmRoqkf@2022', 'edxapp', charset='utf8')

        mdlcur = mdlcon.cursor()
        for cblock in coursetmp:
            chapter_dict = {}
            # course_id = request.GET.get("course_id")
            # course_id = "course-v1:SunMoonK+SMKMOOC-05+2023_T2"
            course_id = cblock
            log.info("course_id ======> %s" % course_id)
            print "course_id=====>", course_id
            try:
                s_course_id = str(course_id).split('+')
                _course_id = s_course_id[-2]
                _run_id = s_course_id[-1]

                print "s_course_id====>", course_id
                print "_course_id====>", _course_id
                print "_run_id====>", _run_id

                structure_id = ObjectId(
                    db.modulestore.active_versions.find_one({'course': _course_id, 'run': _run_id}).get('versions').get('published-branch')
                )

                print "structure_id====>", structure_id
                if structure_id is not None:
                    blocks_list = db.modulestore.structures.find_one({'_id': structure_id}).get('blocks')
                    transcripts_data_list = []
                    for block in blocks_list:
                        chapter_dict[block.get('block_id')] = block

                    for block in blocks_list:
                        block_type = block.get('block_type')
                        if block_type == 'chapter':
                            for seq_id in block.get('fields').get('children'):
                                for ver_id in chapter_dict[seq_id[-1]].get('fields').get('children'):
                                    _is_exist_problem = False
                                    _is_exist_discussion = False
                                    for act_id in chapter_dict[ver_id[-1]].get('fields').get('children'):
                                        chapter_name = '-'  # 주차명
                                        chapter_sub_name = '-'  # 차시명
                                        activity_name = '-'  # 학습확동명
                                        activity_type = '-'  # 학습활동 종류
                                        video_url = '-'  # 동영상 URL
                                        video_range = ''  # 영상 재생시간
                                        transcripts = '-'  # 자막 여부

                                        activity_type = chapter_dict[act_id[-1]].get('block_type')
                                        if activity_type == 'video':
                                            edx_video_id = ''
                                            transcripts_list = []
                                            try:  # 자막 유무 mysql 에서 조회
                                                log.info("chapter_dict[act_id[-1]].get('fields')======> %s" % chapter_dict[act_id[-1]].get('fields').get('edx_video_id'))
                                                edx_video_id = chapter_dict[act_id[-1]].get('fields').get('edx_video_id')
                                                log.info("edx_video_id NONE ======> %s" % chapter_dict[act_id[-1]].get('fields'))
                                                if len(edx_video_id) > 0:
                                                    with connections['default'].cursor() as cur_video:
                                                        query = "SELECT b.language_code FROM  edxval_video AS a LEFT JOIN edxval_videotranscript AS b ON  a.id = b.video_id WHERE a.edx_video_id like '%{}%'".format(edx_video_id)
                                                        log.info('transcriptsmy query ===> %s' % query)
                                                        cur_video.execute(query)
                                                        video_rows = cur_video.fetchall()
                                                        transcripts_list = video_rows
                                            except:
                                                pass

                                            try:
                                                if len(transcripts_list) > 0:
                                                    for transcripts in transcripts_list:
                                                        if transcripts[0] not in transcripts_data_list:
                                                            log.info('transcriptsmy ===> %s' % transcripts[0])
                                                            print("transcriptsmy ===> ", transcripts[0])
                                                            transcripts_data_list.append(transcripts[0])
                                                else:
                                                    for transcripts in chapter_dict[act_id[-1]].get('fields').get('transcripts').values():
                                                        if transcripts not in transcripts_data_list:
                                                            log.info('transcriptsmongo===> %s' % transcripts)
                                                            transcripts_data_list.append(transcripts)
                                            except:
                                                pass

                                            # print("chapter_dict[act_id[-1]].get('fields')=====>",chapter_dict[act_id[-1]].get('fields'))
                                            chapter_name = block.get('fields').get('display_name')
                                            chapter_sub_name = chapter_dict[seq_id[-1]].get('fields').get('display_name')
                                            activity_name = chapter_dict[ver_id[-1]].get('fields').get('display_name')

                                            video_url = chapter_dict[act_id[-1]].get('fields').get('html5_sources')[0]
                                            edx_video_id = ''
                                            transcripts_list = []
                                            try:  # 자막 데이터 구성

                                                if len(transcripts_list) < 1:
                                                    transcripts_list = chapter_dict[act_id[-1]].get('fields').get('transcripts').keys()

                                                num = 0
                                                for transcript in transcripts_list:
                                                    language_code = transcript
                                                    # transcript_file = transcripts_script_list[num]
                                                    transcript_file = transcripts_data_list[num]
                                                    log.info('transcript_file===> %s' % transcript_file)
                                                    edx_video_id = chapter_dict[act_id[-1]].get('fields').get('edx_video_id')
                                                    block_id = chapter_dict[act_id[-1]].get('block_id')
                                                    # mdl_import_vod_meta
                                                    print("language_code======>",str(language_code))
                                                    query = "SELECT count(*) FROM mdl_import_vod_meta mivm JOIN mdl_import_script_meta mism WHERE mivm.url = '{0}' and mism.lang = '{1}';".format(video_url, str(language_code))
                                                    log.info('check_index111111 query ====> %s' % query)
                                                    mdlcur.execute(query)
                                                    check_index = mdlcur.fetchall()
                                                    log.info('check_index111111[0][0]====> %s' % check_index[0][0])
                                                    if (check_index[0][0] == 0):    # 정보가 없다면
                                                        #mdl_import_vod_meta_`2
                                                        query = "SELECT count(*) FROM mdl_import_vod_meta_2 mivm JOIN mdl_import_script_meta mism WHERE mivm.url = '{0}' and mism.lang = '{1}';".format(video_url, str(language_code))
                                                        mdlcur.execute(query)
                                                        check_index = mdlcur.fetchall()
                                                        log.info('check_index222222[0][0]====> %s' % check_index[0][0])
                                                        if (check_index[0][0] == 0):    # 정보가 없다면
                                                        # path_to_file = "/edx/var/edxapp/media/video-transcripts/{0}".format(transcript_file)
                                                        # log.info('path_to_file===> %s' % path_to_file)
                                                        # if exists(path_to_file):
                                                        #     chapter_list.append([chapter_name, chapter_sub_name, language_code,transcript_file, edx_video_id, video_url, block_id])
                                                        #     transcriptline = ""
                                                        #     f = open(path_to_file, 'r')
                                                        #     while True:
                                                        #         line = f.readline()
                                                        #         if not line: break
                                                        #         transcriptline = transcriptline + line
                                                        #
                                                        #     f.close()
                                                            transcriptline = ""

                                                            query = "INSERT INTO mdl_import_vod_meta_2(url,edx_video_id) VALUES ('{0}','{1}');".format(video_url,edx_video_id)
                                                            print "query1==>",query
                                                            log.info('query1===> %s' % query)
                                                            mdlcur.execute(query)
                                                            meta_id = mdlcur.lastrowid
                                                            mdlcur.execute('commit')
                                                            print "meta_id====>",meta_id
                                                            log.info('meta_id===> %s' % meta_id)

                                                            query = "INSERT INTO mdl_import_vod_meta_block_2(meta_id,block_id,block_name) VALUES ('{0}','{1}','{2}');".format(meta_id,block_id,'Video')
                                                            print "query2==>",query
                                                            log.info('query2===> %s' % query)
                                                            mdlcur.execute(query)
                                                            mdlcur.execute('commit')

                                                            uploaddate  = math.trunc(time.time())
                                                            query = "INSERT INTO mdl_import_script_meta_2(meta_id,lang,script,content,uploaddate) VALUES ('{0}','{1}','{2}','{3}','{4}');".format(meta_id,language_code,transcript_file,transcriptline,uploaddate)
                                                            # print "query3===>",query
                                                            log.info('query3===> %s' % query)
                                                            mdlcur.execute(query)
                                                            mdlcur.execute('commit')

                                                    num = num+1
                                            except:
                                                pass
            except Exception as e:
                pass

    except Exception as err:
        log.info('vodfile err [%s]' % traceback.format_exc(err))
        print('예외가 발생했습니다.', err)
        pass

    return JsonResponse(chapter_list)





@login_required
@ensure_csrf_cookie
def vodfile_move_one_nofile(request):
    from os.path import exists
    import math
    import MySQLdb as mdb
    import time
    coursetmp = []
    if "courseid" in request.GET:
        courseid = request.GET.get("courseid","")
        courseidtmp = courseid.replace(" ","+")
        print "courseid===>",courseidtmp
        coursetmp.append(courseidtmp)
        print "coursetmp===>",coursetmp
    else:
        coursetmp.append("course-v1:EwhaK+EW36387K+2015-04")
        coursetmp.append("course-v1:EwhaK+EW10771K+2015-03")
        coursetmp.append("course-v1:EwhaK+EW10164K+2015-01")
        coursetmp.append("course-v1:SKKUk+SKKU_BUS3033.01K+2016_SKKU01")
        coursetmp.append("course-v1:SMUCk+SMUC01k+2017_T1")
        coursetmp.append("course-v1:SMUCk+SMUC02k+2017_T2")
        coursetmp.append("course-v1:UOUk+UOU101.02k+U101B.1")
        coursetmp.append("course-v1:SKKUk+SKKU_GEDH042.01K+2016_SKKU04")
        coursetmp.append("course-v1:KonYangK+ACE.KY002+KY2016A02")
        coursetmp.append("course-v1:KNUk+CORE.KNUk01+2016_S1")
        coursetmp.append("course-v1:SKKUk+SKKU_GEDH043.O1K+2017_T1_0")
        coursetmp.append("course-v1:EwhaK+EW22126K+2017_F11")
        coursetmp.append("course-v1:DGUk+DGUk_004k+DGU_004k_2017_9_4")
        coursetmp.append("course-v1:DGUk+DGUk_005k+DGU_005k_2017_9_5")
        coursetmp.append("course-v1:KHUk+KH304+2017_KH304")
        coursetmp.append("course-v1:KHUk+FD_KH305+2017_KH305")
        coursetmp.append("course-v1:KHUk+FD_KH306+2017_KH306")
        coursetmp.append("course-v1:SKKUk+FD_SKKU_GEDH061.O1K+2017_T1_0")
        coursetmp.append("course-v1:SKKUk+FD_SKKU_GEDH062_O1K+2017_T1_0")
        coursetmp.append("course-v1:PTUk+SF_PMOOC01k+2017_T2")
        coursetmp.append("course-v1:KonkukK+PRIME_konkuk_P001+2017_1")
        coursetmp.append("course-v1:DonggukK+ACE_FA_DGU02k+2017_T1")
        coursetmp.append("course-v1:EwhaK+CORE_EW16001C+2017_F09")
        coursetmp.append("course-v1:DGUk+DGU_006k+DGU_006k_2018_9_6")
        coursetmp.append("course-v1:DGUk+DGU-007k+DGU-007k_2018_9_7")
        coursetmp.append("course-v1:DGUk+DGU_008k+DGU_008k_2018_9_8")
        coursetmp.append("course-v1:DGUk+DGU_009k+DGU_009k_2018_9_9")
        coursetmp.append("course-v1:SMUk+SMU2018_02+2018_2_T2")
        coursetmp.append("course-v1:SOGANGk+SOGANG06K+2018_T3")
        coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc05K+2018_2")
        coursetmp.append("course-v1:HYUk+CORE_HYUKMOOC2018-2k+2018_C2")
        coursetmp.append("course-v1:DKUK+MOOC_DKUK0006+2019_T2")
        coursetmp.append("course-v1:DKUK+MOOC_DKUK0008+2019_T2")
        coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc09K+2019_T2")
        coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc10K+2019_T2")
        coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc11K+2019_T2")
        coursetmp.append("course-v1:DongdukK+DDU04+2019_T2")
        coursetmp.append("course-v1:SSUk+SSMOOC14K+2019_T2")
        coursetmp.append("course-v1:INU+INU004+2019_L2")
        coursetmp.append("course-v1:AYUk+AYUk_EM_01+2019_T2")
        coursetmp.append("course-v1:CNUk+MOE_CNU10+2019_2_10")
        coursetmp.append("course-v1:DKUK+MOOC_DKUK0017+2019_T2")
        coursetmp.append("course-v1:HYUk+IV_HYUKMOOC2019-1k+2019_C1")
        coursetmp.append("course-v1:XuetangX+XuetangX_01+2020_T1")
        coursetmp.append("course-v1:XuetangX+XuetangX_02+2020_T1")
        coursetmp.append("course-v1:XuetangX+XuetangX_03+2020_T1")
        coursetmp.append("course-v1:KSUk+KSUk_10+2020_T2")
        coursetmp.append("course-v1:KSUk+KSUk_11+2020_T2")
        coursetmp.append("course-v1:KSUk+KSUk_12+2020_T2")
        coursetmp.append("course-v1:DGUk+DGU_011k+DGU_011k_2020_12_11")
        coursetmp.append("course-v1:DGUk+DGU_012k+DGU_012k_2020_12_12")
        coursetmp.append("course-v1:DHUk+DHUk07k+2020_T2")
        coursetmp.append("course-v1:DHUk+DHUk08k+2020_T2")
        coursetmp.append("course-v1:DHUk+DHUk09k+2020_T2")
        coursetmp.append("course-v1:DHUk+DHUk10k+2020_T2")
        coursetmp.append("course-v1:PNUk+PE_C01+2020_KM019")
        coursetmp.append("course-v1:HonamUniv+HCTL01+2021_6")
        coursetmp.append("course-v1:KHUk+KH502+2020_T2_1")
        coursetmp.append("course-v1:DGUk+DGU_017k+DGU_017k_2020_12_17")
        coursetmp.append("course-v1:DGUk+DGU_015k+DGU_015k_2020_12_15")
        coursetmp.append("course-v1:KHUk+KH505+2020_T2_1")
        coursetmp.append("course-v1:DGUk+DGU_016k+DGU_016k_2020_12_16")
        coursetmp.append("course-v1:SKKUk+SKKU_47+2020_T1")
        coursetmp.append("course-v1:SKKUk+SKKU_48+2020_T1")
        coursetmp.append("course-v1:SKKUk+SKKU_49+2020_T1")
        coursetmp.append("course-v1:KPU+KPU02+2020_T2")
        coursetmp.append("course-v1:SoongsilUnivK+soongsilmooc12K+2020_T2")
        coursetmp.append("course-v1:EBS+EBS001+2021_T1")
        coursetmp.append("course-v1:EBS+EBS002+2021_T1")
        coursetmp.append("course-v1:EBS+EBS003+2021_T1")
        coursetmp.append("course-v1:EBS+EBS004+2021_T1")
        coursetmp.append("course-v1:EBS+EBS005+2021_T1")
        coursetmp.append("course-v1:EBS+EBS006+2021_T1")
        coursetmp.append("course-v1:EBS+EBS007+2021_T1")
        coursetmp.append("course-v1:EBS+EBS008+2021_T1")
        coursetmp.append("course-v1:EBS+EBS009+2021_T1")
        coursetmp.append("course-v1:EBS+EBS010+2021_T1")
        coursetmp.append("course-v1:EBS+EBS011+2021_T1")
        coursetmp.append("course-v1:EBS+EBS012+2021_T1")
        coursetmp.append("course-v1:EBS+EBS013+2021_T1")
        coursetmp.append("course-v1:EBS+EBS014+2021_T1")
        coursetmp.append("course-v1:EBS+EBS015+2021_T1")
        coursetmp.append("course-v1:EBS+EBS016+2021_T1")
        coursetmp.append("course-v1:EBS+EBS017+2021_T1")
        coursetmp.append("course-v1:EBS+EBS018+2021_T1")
        coursetmp.append("course-v1:EBS+EBS019+2021_T1")
        coursetmp.append("course-v1:EBS+EBS020+2021_T1")
        coursetmp.append("course-v1:EBS+EBS021+2021_T1")
        coursetmp.append("course-v1:EBS+EBS022+2021_T1")
        coursetmp.append("course-v1:EBS+EBS023+2021_T1")
        coursetmp.append("course-v1:EBS+EBS024+2021_T1")
        coursetmp.append("course-v1:EBS+EBS025+2021_T1")
        coursetmp.append("course-v1:EBS+EBS026+2021_T1")
        coursetmp.append("course-v1:EBS+EBS027+2021_T1")
        coursetmp.append("course-v1:EBS+EBS028+2021_T1")
        coursetmp.append("course-v1:EBS+EBS029+2021_T1")
        coursetmp.append("course-v1:EBS+EBS030+2021_T1")
        coursetmp.append("course-v1:EBS+EBS031+2021_T1")
        coursetmp.append("course-v1:EBS+EBS032+2021_T1")
        coursetmp.append("course-v1:EBS+EBS033+2021_T1")
        coursetmp.append("course-v1:EBS+EBS034+2021_T1")
        coursetmp.append("course-v1:EBS+EBS035+2021_T1")
        coursetmp.append("course-v1:EBS+EBS036+2021_T1")
        coursetmp.append("course-v1:EBS+EBS037+2021_T1")
        coursetmp.append("course-v1:EBS+EBS038+2021_T1")
        coursetmp.append("course-v1:EBS+EBS039+2021_T1")
        coursetmp.append("course-v1:EBS+EBS040+2021_T1")
        coursetmp.append("course-v1:EBS+EBS041+2021_T1")
        coursetmp.append("course-v1:EBS+EBS042+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC001+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC002+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC003+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC004+2021_T1")
        coursetmp.append("course-v1:JTBC+EBS005+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC006+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC007+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC008+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC009+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC010+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC011+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC015+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC012+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC013+2021_T1")
        coursetmp.append("course-v1:JTBC+JTBC014+2021_T1")
        coursetmp.append("course-v1:KSUk+KSUk_14+2021_T2")
        coursetmp.append("course-v1:KSUk+KSUk_15+2021_T2")
        coursetmp.append("course-v1:KSUk+KSUk_16+2021_T2")
        coursetmp.append("course-v1:KSUk+KSUk_17+2021_T2")
        coursetmp.append("course-v1:DGUk+DGU_019k+DGU_018k_2021")
        coursetmp.append("course-v1:DGUk+DGU_018k+DGU_018k_2021")
        coursetmp.append("course-v1:DGUk+DGU_020k+DGU_020k_2021")
        coursetmp.append("course-v1:DGUk+DGU_021k+DGU_021k_2021")
        coursetmp.append("course-v1:DHUk+DHUk12k+2021_T2")
        coursetmp.append("course-v1:DHUk+DHUk13k+2021_T2")
        coursetmp.append("course-v1:DHUk+DHUk14k+2021_T2")
        coursetmp.append("course-v1:PNUk+MS_C01+2021_N1")
        coursetmp.append("course-v1:JJU+JJU04+2021_J04")
        coursetmp.append("course-v1:AYUk+AYUK_IP_0+2021_T2_1")
        coursetmp.append("course-v1:DSUk+UI.DSU01+2021_T2")
        coursetmp.append("course-v1:DCU+DCU01+2021_1")
        coursetmp.append("course-v1:XuetangX+THc2021+2022T1")
        coursetmp.append("course-v1:EBS+EBS001+2022_T1")
        coursetmp.append("course-v1:EBS+EBS002+2022_T1")
        coursetmp.append("course-v1:EBS+EBS003+2022_T1")
        coursetmp.append("course-v1:EBS+EBS004+2022_T1")
        coursetmp.append("course-v1:EBS+EBS005+2022_T1")
        coursetmp.append("course-v1:EBS+EBS006+2022_T1")
        coursetmp.append("course-v1:EBS+EBS007+2022_T1")
        coursetmp.append("course-v1:EBS+EBS008+2022_T1")
        coursetmp.append("course-v1:EBS+EBS009+2022_T1")
        coursetmp.append("course-v1:EBS+EBS010+2022_T1")
        coursetmp.append("course-v1:EBS+EBS011+2022_T1")
        coursetmp.append("course-v1:EBS+EBS012+2022_T1")
        coursetmp.append("course-v1:EBS+EBS013+2022_T1")
        coursetmp.append("course-v1:EBS+EBS014+2022_T1")
        coursetmp.append("course-v1:EBS+EBS015+2022_T1")
        coursetmp.append("course-v1:EBS+EBS016+2022_T1")
        coursetmp.append("course-v1:EBS+EBS017+2022_T1")
        coursetmp.append("course-v1:EBS+EBS018+2022_T1")
        coursetmp.append("course-v1:EBS+EBS019+2022_T1")
        coursetmp.append("course-v1:EBS+EBS020+2022_T1")
        coursetmp.append("course-v1:EBS+EBS021+2022_T1")
        coursetmp.append("course-v1:EBS+EBS022+2022_T1")
        coursetmp.append("course-v1:EBS+EBS023+2022_T1")
        coursetmp.append("course-v1:EBS+EBS024+2022_T1")
        coursetmp.append("course-v1:EBS+EBS025+2022_T1")
        coursetmp.append("course-v1:EBS+EBS217+2022_T1")
        coursetmp.append("course-v1:EBS+EBS227+2022_T1")
        coursetmp.append("course-v1:EBS+EBS228+2022_T1")
        coursetmp.append("course-v1:EBS+EBS229+2022_T1")
        coursetmp.append("course-v1:EBS+EBS230+2022_T1")
        coursetmp.append("course-v1:EBS+EBS231+2022_T1")
        coursetmp.append("course-v1:EBS+EBS232+2022_T1")
        coursetmp.append("course-v1:EBS+EBS233+2022_T1")
        coursetmp.append("course-v1:EBS+EBS234+2022_T1")
        coursetmp.append("course-v1:EBS+EBS235+2022_T1")
        coursetmp.append("course-v1:EBS+EBS236+2022_T1")
        coursetmp.append("course-v1:EBS+EBS237+2022_T1")
        coursetmp.append("course-v1:EBS+EBS238+2022_T1")
        coursetmp.append("course-v1:EBS+EBS240+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC001+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC002+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC003+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC004+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC005+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC006+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC007+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC008+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC009+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC010+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC011+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC012+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC013+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC014+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC015+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC016+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC017+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC018+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC019+2022_T1")
        coursetmp.append("course-v1:JTBC+JTBC020+2022_T1")
        coursetmp.append("course-v1:KSUk+KSUk_18+2022_T2")
        coursetmp.append("course-v1:KSUk+KSUk_19+2022_T2")
        coursetmp.append("course-v1:KSUk+KSUk_20+2022_T2")
        coursetmp.append("course-v1:KSUk+KSUk_21+2022_T2")
        coursetmp.append("course-v1:DHUk+DHU17k+2022_T2")
        coursetmp.append("course-v1:DHUk+DHU18k+2022_T2")
        coursetmp.append("course-v1:DHUk+DHU19k+2022_T2")
        coursetmp.append("course-v1:DHUk+DHU20k+2022_T2")
        coursetmp.append("course-v1:WHSUK+WHSUK_06+2022-T2-6")
        coursetmp.append("course-v1:WHSUK+WHSUK_07+2022-T2-7")
        coursetmp.append("course-v1:WHSUK+WHSUK_08+2022-T2-8")
        coursetmp.append("course-v1:WHSUK+WHSUK_09+2022-T2-9")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_108+2022_1")
        coursetmp.append("course-v1:KAEP_INHA+KINHA001+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA002+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA003+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA004+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA005+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA006+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA007+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA008+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA009+2022_01")
        coursetmp.append("course-v1:KAEP_INHA+KINHA010+2022_01")
        coursetmp.append("course-v1:KAEP_KHU+KKHU01+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU02+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU03+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU04+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU05+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU06+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU07+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU08+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU09+2022_T1")
        coursetmp.append("course-v1:KAEP_KHU+KKHU10+2022_T1")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA001+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA002+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA003+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA004+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA005+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA006+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA007+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA008+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA009+2022_01")
        coursetmp.append("course-v1:KAEP_KOREA+KKOREA010+2022_01")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_106+2022_1")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_104+2022_1")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_103+2022_1")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_102+2022_1")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_107+2022_1")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_109+2022_1")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_110+2022_1")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_105+2022_1")
        coursetmp.append("course-v1:AYUk+AYUk_SP+2023_T1")
        coursetmp.append("course-v1:KEKA_SNU+KEKA101+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA102+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA103+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA104+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA105+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA106+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA107+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA108+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA109+2022_01")
        coursetmp.append("course-v1:KEKA_SNU+KEKA110+2022_01")
        coursetmp.append("course-v1:KAEP_DONGGUK+KAEP_DONGGUK_101+2022_1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP01+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP02+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP03+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP04+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP05+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP06+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP07+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP08+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP09+2022_T1")
        coursetmp.append("course-v1:YonseiWK_KAEP+YonseiWK_KAEP10+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP01+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP02+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP03+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP04+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP05+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP06+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP07+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP08+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP09+2022_T1")
        coursetmp.append("course-v1:SOGANGKAEP+KAEP10+2022_T1")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH109+2023_A109")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH108+2023_A108")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH107+2023_A107")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH106+2023_A106")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH105+2023_A105")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH104+2023_A104")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH103+2023_A103")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH102+2023_A102")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH110+2023_A110")
        coursetmp.append("course-v1:KAEP_KOREA_CKH+KUKH101+2023_A101")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP01+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP02+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP03+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP04+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP05+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP06+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP07+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP08+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP09+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP10+2022_T1")
        coursetmp.append("course-v1:KAEP_SKKU+KAEP11+2022_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu08+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu07+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu06+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu09+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu03+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu02+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu05+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu01+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu04+2023_T1")
        coursetmp.append("course-v1:CKL_SNU+cklsnu10+2023_T1")
        coursetmp.append("course-v1:SKKUk+SKKU_LAO2301+2023_T1")
        coursetmp.append("course-v1:SKKUk+SKKU_LAO2302+2023_T1")
        # coursetmp.append("course-v1:SunMoonK+SMKMOOC-05+2023_T2")
        # coursetmp.append("course-v1:DH+sdfsdfsdf+20230630")

        coursetmp2 = []
        coursetmp2.append("course-v1:SunMoonK+SMKMOOC-05+2023_T2")
        coursetmp2.append("course-v1:DH+sdfsdfsdf+20230630")

    chapter_list = []
    try:
        m_host = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('host')
        m_port = settings.CONTENTSTORE.get('DOC_STORE_CONFIG').get('port')
        client = MongoClient(m_host, m_port)
        db = client.edxapp
        #mdlcon = mdb.connect('192.168.1.245', 'openlms', 'dhvms@23gkrTmq', 'openlms', charset='utf8')
        mdlcon = mdb.connect('118.67.152.82', 'root', 'anzmRoqkf@2022', 'edxapp', charset='utf8')

        mdlcur = mdlcon.cursor()
        for cblock in coursetmp:
            chapter_dict = {}
            # course_id = request.GET.get("course_id")
            # course_id = "course-v1:SunMoonK+SMKMOOC-05+2023_T2"
            course_id = cblock
            log.info("course_id ======> %s" % course_id)
            print "course_id=====>", course_id
            try:
                s_course_id = str(course_id).split('+')
                _course_id = s_course_id[-2]
                _run_id = s_course_id[-1]

                print "s_course_id====>", course_id
                print "_course_id====>", _course_id
                print "_run_id====>", _run_id

                structure_id = ObjectId(
                    db.modulestore.active_versions.find_one({'course': _course_id, 'run': _run_id}).get('versions').get('published-branch')
                )

                print "structure_id====>", structure_id
                if structure_id is not None:
                    blocks_list = db.modulestore.structures.find_one({'_id': structure_id}).get('blocks')
                    transcripts_data_list = []
                    for block in blocks_list:
                        chapter_dict[block.get('block_id')] = block

                    for block in blocks_list:
                        block_type = block.get('block_type')
                        if block_type == 'chapter':
                            for seq_id in block.get('fields').get('children'):
                                for ver_id in chapter_dict[seq_id[-1]].get('fields').get('children'):
                                    _is_exist_problem = False
                                    _is_exist_discussion = False
                                    for act_id in chapter_dict[ver_id[-1]].get('fields').get('children'):
                                        chapter_name = '-'  # 주차명
                                        chapter_sub_name = '-'  # 차시명
                                        activity_name = '-'  # 학습확동명
                                        activity_type = '-'  # 학습활동 종류
                                        video_url = '-'  # 동영상 URL
                                        video_range = ''  # 영상 재생시간
                                        transcripts = '-'  # 자막 여부

                                        activity_type = chapter_dict[act_id[-1]].get('block_type')
                                        if activity_type == 'video':
                                            edx_video_id = ''
                                            transcripts_list = []
                                            transcripts_videoid_list = []
                                            transcripts_lang_list = []
                                            transcripts_file_format_list = []
                                            try:
                                                log.info("chapter_dict[act_id[-1]].get('fields')======> %s" % chapter_dict[act_id[-1]].get('fields').get('edx_video_id'))
                                                edx_video_id = chapter_dict[act_id[-1]].get('fields').get('edx_video_id')
                                                log.info("edx_video_id NONE ======> %s" % chapter_dict[act_id[-1]].get('fields'))
                                                if len(edx_video_id) > 0:
                                                    with connections['default'].cursor() as cur_video:
                                                        query = "select transcript,language_code,video_id,file_format from edxval_videotranscript where video_id in (select video_id from edxval_coursevideo where course_id like '%{}%') and (language_code <> 'en' and language_code <> 'ko');".format(course_id)
                                                        log.info('transcriptsmy query ===> %s' % query)
                                                        cur_video.execute(query)
                                                        video_rows = cur_video.fetchall()
                                                        transcripts_list = video_rows
                                            except:
                                                pass

                                            try:
                                                if len(transcripts_list) > 0:
                                                    for transcripts in transcripts_list:
                                                        if transcripts[0] not in transcripts_data_list:
                                                            log.info('transcriptsmy ===> %s' % transcripts[0])
                                                            transcripts_data_list.append(transcripts[0])
                                                            transcripts_videoid_list.append(transcripts[2])
                                                            transcripts_lang_list.append(transcripts[1])
                                                            transcripts_file_format_list.append(transcripts[3])
                                                # else:
                                                #     for transcripts in chapter_dict[act_id[-1]].get('fields').get('transcripts').values():
                                                #         if transcripts not in transcripts_data_list:
                                                #             log.info('transcriptsmongo===> %s' % transcripts)
                                                #             transcripts_data_list.append(transcripts)
                                            except:
                                                pass

                                            # print("chapter_dict[act_id[-1]].get('fields')=====>",chapter_dict[act_id[-1]].get('fields'))
                                            chapter_name = block.get('fields').get('display_name')
                                            chapter_sub_name = chapter_dict[seq_id[-1]].get('fields').get('display_name')
                                            activity_name = chapter_dict[ver_id[-1]].get('fields').get('display_name')
                                            video_url = chapter_dict[act_id[-1]].get('fields').get('html5_sources')[0]
                                            edx_video_id = ''
                                            transcripts_list = []
                                            try:  # 자막 데이터 구성

                                                # if len(transcripts_list) < 1:
                                                #     transcripts_list = chapter_dict[act_id[-1]].get('fields').get('transcripts').keys()

                                                num = 0
                                                for transcript in transcripts_data_list:
                                                    language_code = transcripts_lang_list[num]
                                                    transcript_file = transcript
                                                    log.info('transcript_file===> %s' % transcript_file)
                                                    edx_video_id = transcripts_videoid_list[num]
                                                    block_id = chapter_dict[act_id[-1]].get('block_id')
                                                    # mdl_import_vod_meta
                                                    print("language_code======>",str(language_code))
                                                    query = "SELECT count(*) FROM mdl_import_vod_meta mivm JOIN mdl_import_script_meta mism ON mivm.id = mism.meta_id WHERE mivm.url = '{0}' and mism.lang = '{1}';".format(video_url, str(language_code))
                                                    log.info('check_index111111 query ====> %s' % query)
                                                    mdlcur.execute(query)
                                                    check_index = mdlcur.fetchall()
                                                    log.info('check_index111111[0][0]====> %s' % check_index[0][0])
                                                    if (check_index[0][0] == 0):    # 정보가 없다면
                                                        #mdl_import_vod_meta_`2
                                                        query = "SELECT count(*) FROM mdl_import_vod_meta_2 mivm JOIN mdl_import_script_meta mism ON mivm.id = mism.meta_id WHERE mivm.url = '{0}' and mism.lang = '{1}';".format(video_url, str(language_code))
                                                        mdlcur.execute(query)
                                                        check_index = mdlcur.fetchall()
                                                        log.info('check_index222222[0][0]====> %s' % check_index[0][0])
                                                        if (check_index[0][0] == 0):    # 정보가 없다면
                                                            path_to_file = "/edx/var/edxapp/media/video-transcripts/{0}".format(transcript_file)
                                                            log.info('path_to_file===> %s' % path_to_file)
                                                            if exists(path_to_file):
                                                                chapter_list.append([chapter_name, chapter_sub_name, language_code,transcript_file, edx_video_id, video_url, block_id])
                                                                transcriptline = ""
                                                                f = open(path_to_file, 'r')
                                                                while True:
                                                                    line = f.readline()
                                                                    if not line: break
                                                                    transcriptline = transcriptline + line

                                                                f.close()
                                                                if (transcripts_file_format_list=="sjson"):
                                                                    tmptranscript = generate_srt_from_sjson(transcriptline)
                                                                print("tmptranscript=======>",tmptranscript)

                                                                query = "INSERT INTO mdl_import_vod_meta_2(url,edx_video_id) VALUES ('{0}','{1}');".format(video_url,edx_video_id)
                                                                print "query1==>",query
                                                                log.info('query1===> %s' % query)
                                                                mdlcur.execute(query)
                                                                meta_id = mdlcur.lastrowid
                                                                mdlcur.execute('commit')
                                                                print "meta_id====>",meta_id
                                                                log.info('meta_id===> %s' % meta_id)

                                                                query = "INSERT INTO mdl_import_vod_meta_block_2(meta_id,block_id,block_name) VALUES ('{0}','{1}','{2}');".format(meta_id,block_id,'Video')
                                                                print "query2==>",query
                                                                log.info('query2===> %s' % query)
                                                                mdlcur.execute(query)
                                                                mdlcur.execute('commit')

                                                                uploaddate  = math.trunc(time.time())
                                                                query = "INSERT INTO mdl_import_script_meta_2(meta_id,lang,script,content,uploaddate) VALUES ('{0}','{1}','{2}','{3}','{4}');".format(meta_id,language_code,transcript_file,transcriptline,uploaddate)
                                                                print "query3===>",query
                                                                log.info('query3===> %s' % query)
                                                                mdlcur.execute(query)
                                                                mdlcur.execute('commit')

                                                    num = num+1
                                            except:
                                                pass
            except Exception as e:
                pass

    except Exception as err:
        log.info('vodfile err [%s]' % traceback.format_exc(err))
        print('예외가 발생했습니다.', err)
        pass

    return JsonResponse(chapter_list)


def generate_srt_from_sjson(sjson_subs):
    """
    Generate transcripts from sjson to SubRip (*.srt).

    Arguments:
        sjson_subs (dict): `sjson` subs.

    Returns:
        Subtitles in SRT format.
    """

    output = ''

    equal_len = len(sjson_subs['start']) == len(sjson_subs['end']) == len(sjson_subs['text'])
    if not equal_len:
        return output

    for i in range(len(sjson_subs['start'])):
        item = SubRipItem(
            index=i,
            start=SubRipTime(milliseconds=sjson_subs['start'][i]),
            end=SubRipTime(milliseconds=sjson_subs['end'][i]),
            text=sjson_subs['text'][i]
        )
        output += (unicode(item))
        output += '\n'
    return output
