# -*- coding: utf-8 -*-
import logging
from util.json_request import JsonResponse
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from lms.envs import common as settings
from kakaocert import KakaocertService, KakaocertException, RequestVerifyAuth
import traceback
import datetime
import hashlib
from django.contrib.auth.hashers import make_password, check_password

log = logging.getLogger(__name__)

kakaocertService = KakaocertService(settings.LinkID, settings.SecretKey)

kakaocertService.IPRestrictOnOff = settings.IPRestrictOnOff

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


def kakao_auth_form(request):

    name = request.GET.get('name')
    phone = request.GET.get('phone')
    year = request.GET.get('year')
    gender = request.GET.get('name')

    try:
        # kakaoCert 이용기관코드, kakaoCert 파트너 사이트에서 확인
        clientCode = '021010000007'

        token_string = 'token_value'
        token_value = hashlib.sha256(token_string.encode())

        request.session['kakao_token'] = token_value.hexdigest()

        print token_value.hexdigest()

        # 본인인증 요청정보 객체
        requestObj = RequestVerifyAuth(

            # 고객센터 전화번호, 카카오톡 인증메시지 중 "고객센터" 항목에 표시
            CallCenterNum='1811-3118',

            # 인증요청 만료시간(초), 최대값 1000, 인증요청 만료시간(초) 내에 미인증시 만료 상태로 처리됨
            Expires_in=180,

            # 수신자 생년월일, 형식 : YYYYMMDD
            ReceiverBirthDay=year,

            # 수신자 휴대폰번호
            ReceiverHP=phone,

            # 수신자 성명
            ReceiverName=name,

            # 별칭코드, 이용기관이 생성한 별칭코드 (파트너 사이트에서 확인가능)
            # 카카오톡 인증메시지 중 "요청기관" 항목에 표시
            # 별칭코드 미 기재시 이용기관의 이용기관명이 "요청기관" 항목에 표시
            SubClientID='',

            # 인증요청 메시지 부가내용, 카카오톡 인증메시지 중 상단에 표시
            TMSMessage='K-MOOC 인증',

            # 인증요청 메시지 제목, 카카오톡 인증메시지 중 "요청구분" 항목에 표시
            TMSTitle='본인인증 요청',

            # 인증서 발급유형 선택
            # True : 휴대폰 본인인증만을 이용해 인증서 발급
            # False : 본인계좌 점유 인증을 이용해 인증서 발급
            # 카카오톡 인증메시지를 수신한 사용자가 카카오인증 비회원일 경우, 카카오인증 회원등록 절차를 거쳐 은행계좌 실명확인 절차를 밟은 다음 전자서명 가능
            isAllowSimpleRegistYN=True,

            # 수신자 실명확인 여부
            # True : 카카오페이가 본인인증을 통해 확보한 사용자 실명과 ReceiverName 값을 비교
            # False : 카카오페이가 본인인증을 통해 확보한 사용자 실명과 RecevierName 값을 비교하지 않음.
            isVerifyNameYN=True,

            # 전자서명할 토큰 원문
            Token=token_value.hexdigest(),

            # PayLoad, 이용기관이 생성한 payload(메모) 값
            PayLoad='memo info',
        )

        result = kakaocertService.requestVerifyAuth(clientCode, requestObj)

        return JsonResponse({'success': True, 'receiptId': result.receiptId})

    except KakaocertException as KE:
        print KE.code
        print KE.message

        return JsonResponse({'success': False})


def kakao_auth_confirm(request):

    print 'kakao_auth_confirm'

    try:
        clientCode = '021010000007'

        # 본인인증 요청시 반환받은 접수아이디
        receiptId = request.GET.get('receiptId')

        response = kakaocertService.getVerifyAuthState(clientCode, receiptId)

        # 인증을 하면 state = 1
        # 인증을 하지 않으면 state = 0
        # 시간이 만료 되었으면 state = 2
        return JsonResponse({'success': True, 'state': response.state})

    except KakaocertException as KE:

        print KE.code
        print KE.message

        return JsonResponse({'success': False})


def kakao_auth_certification(request):

    print 'kakao_auth_certification'

    try:
        clientCode = '021010000007'

        # 본인인증 요청시 반환받은 접수아이디
        receiptId = request.GET.get('receiptId')

        response = kakaocertService.verifyAuth(clientCode, receiptId)

        if request.session['kakao_token'] == response.signedData:

            request.session['kakao_name'] = request.GET.get('name')
            request.session['kakao_gender'] = request.GET.get('gender')
            request.session['is_kakao'] = 'Y'
            request.session['kakao_phone'] = request.GET.get('phone')
            request.session['kakao_year'] = request.GET.get('year')

            print 'kakao_debug -----------------> s'
            print request.session['kakao_name']
            print request.session['kakao_gender']
            print request.session['kakao_phone']
            print 'kakao_debug -----------------> e'

            print 'kakao_auth_certification success'

            return JsonResponse({'success': True})
        else:

            print 'kakao_auth_certification fail'
            return JsonResponse({'success': False})

    except KakaocertException as KE:

        print KE.code
        print KE.message

        print 'kakao_auth_certification fail'

        return JsonResponse({'success': False})


def kakao_auth_account_update(request):

    print 'kakao_auth_update'

    try:
        name = request.session['kakao_name'] if 'kakao_name' in request.session else ''
        phone = request.session['kakao_phone'] if 'kakao_phone' in request.session else ''
        gender = request.session['kakao_gender'] if 'kakao_gender' in request.session else ''
        is_kakao = request.session['is_kakao'] if 'is_kakao' in request.session else 'N'
        year = request.session['kakao_year'] if 'kakao_year' in request.session else ''

        if 'kakao_name' in request.session:
            del request.session['kakao_name']

        if 'kakao_phone' in request.session:
            del request.session['kakao_phone']

        if 'kakao_gender' in request.session:
            del request.session['kakao_gender']

        if 'is_kakao' in request.session:
            del request.session['is_kakao']

        if 'kakao_year' in request.session:
            del request.session['kakao_year']

        if gender == '1' or gender == '3':
            gender = 'm'
        elif gender == '2' or gender == '4':
            gender = 'f'

        phone = make_password(phone)

        print phone

        with connections['default'].cursor() as cur:
            query = """
                UPDATE tb_auth_user_addinfo 
                SET 
                    phone = '{phone}',
                    gender = '{gender}',
                    name = '{name}',
                    is_kakao = '{is_kakao}',
                    modify_date = '{modify_date}'
                WHERE
                    user_id = '{user_id}'
            """.format(
                phone=phone,
                gender=gender,
                name=name,
                is_kakao=is_kakao,
                modify_date=datetime.datetime.now(),
                user_id=request.user.id
            )

            print 'update tb_auth_user_addinfo query check ---------------------- s'
            print query
            print 'update tb_auth_user_addinfo query check ---------------------- e'

            cur.execute(query)

        with connections['default'].cursor() as cur:
            query = """
                UPDATE auth_userprofile 
                SET 
                    gender = '{gender}',
                    name = '{name}',
                    year_of_birth = '{year}'
                WHERE
                    user_id = '{user_id}'
            """.format(
                gender=gender,
                name=name,
                year=year,
                modify_date=datetime.datetime.now(),
                user_id=request.user.id
            )

            print 'update tb_auth_user_addinfo query check ---------------------- s'
            print query
            print 'update tb_auth_user_addinfo query check ---------------------- e'

            cur.execute(query)

        return JsonResponse({'success': True})

    except Exception as e:
        print traceback.print_exc(e)

        return JsonResponse({'success': False})