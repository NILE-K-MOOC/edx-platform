#!/usr/bin/python
# -*- coding: utf8 -*-

from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest, HttpResponseRedirect,
    JsonResponse
)
from edxmako.shortcuts import render_to_response
from django.shortcuts import render

import urllib,urllib2, sys
import requests, json
from django.shortcuts import redirect

login_url = "http://oauthdev.lge.com:8080/login"
get_info_url = "http://oauthdev.lge.com:8080/"
get_code_url = "http://oauthdev.lge.com:8080/oauth/authorize"
auth_url = "http://oauthdev.lge.com:8080/oauth/token"
token_url = "http://oauthdev.lge.com:8080/"
check_token_url = "http://oauthdev.lge.com:8080/oauth/check_token"
token_header = "Authorization: Bearer "

#edx set
redirect_uri = "http://edxlmsdev.lge.com/login_process"
cookie_domain = ".lge.com"

# http://lge.nedx.kr/login?jsessionid=oauth-test&jsessionid=oauth-test
def login_test(request):

    ''' 1. 런닝넷의 토큰 ID를 가져올 '''
    lnetid = request.COOKIES.get("LNETID")
    
    if lnetid:
        ''' 2. 런닝넷 로그인 쿠키 체크햐여 LNETID가 없으면, 런닝넷에 로그인이 안되어 있는 것으로 판단함. '''
        res_code, res_dict, _ = call(get_info_url, {})

        if res_code is not None:
            if res_code == 401:
                res_code2, res_dict2, cookie = call(login_url, {"jsessionid": lnetid, "key": "3q5e7a8d9f4q5as65f4g7"})
                ''' 아래의 페이지는 별도 구성해야 함. '''

                res = render_to_response('login_test/index.html')
                res.set_cookie('LGSESSIONID', cookie['LGSESSIONID']) ### 3. oAuth 서비스와 연동을 위하여 해당 세션을 구움
                res.set_cookie('OAuthInfo', cookie['LGSESSIONID']) #### 4. 사용자 상세 프로파일 조회를 위하여
                return res
                
            elif res_code == 200:
                '''
                로그인이 계속 되고 있는 상태로 SSO의 세션이 유지되고 있는 상태이다.
                프로파일 정보가 json으로 넘어온다.
                '''
                return json.dumps(red_dict2)
            
            else:
                
                '''
                500 등의 코드가 옮.
                '''
                html_msg = """
                <html>
                <body>
                <p><h2>OAuth 서버를 체크해주세요.<h2></p>
                <p><h3>응답코드: """ + str(res_code) +"""</h3></p>
                <p><a href="javascript:history.go(-1);">뒤로가기</a>
                </body>
                </html>
                """

                return HttpResponse(html_msg)
                
    else:

        html_msg = """
        <html>
        <body>
        <p><h2>LNETID가 없습니다.<h2></p>
        <p><a href="javascript:history.go(-1);">뒤로가기</a>
        </body>
        </html>
        """

        return HttpResponse(html_msg)
        '''
        런닝넷에 로그인이 되어 있지 않은 상태이다.
        런닝넷으로 리다이렉트
        '''
        

def login_check(request):

    ''' 5. OAuth 연동을 위한 코드 방행을 함(OAuth의 토큰 연동을 위한 OAuth 유니크 키를 발급함.) '''

    lnetid = request.COOKIES.get("LNETID")

    res_code, res_dict, _ = call(get_info_url, {})

    if res_code is not None:
        if res_code == 401:
            res_code2, res_dict2, cookie = call(login_url, {"jsessionid": lnetid, "key": "3q5e7a8d9f4q5as65f4g7"})
            if(res_dict2['status'] == 'OK'):
                try:
                    param = {
                        "client_id": "mme",
                        "response_type": "code",
                        "client_secret": "lge",
                        "redirect_uri": redirect_uri
                    }
                    param_url = get_code_url+'?'+urllib.urlencode(param)
                    res = redirect(param_url)
                    res.set_cookie(key="LGSESSIONID", value=cookie['LGSESSIONID'], domain=cookie_domain)

                    return res

                except Exception as e:
                    print e
                    sys.exit(1)
            else:
                print 'HttpResponse Error'
    return HttpResponse('Response Fail')
    
def login_process(request):

    ''' 6.  login_check에서 코드를 발급하면 OAuth 서버가 본 method로 자동 리다이렉트 함.'''
    oauth_code = request.GET['code'] ##### OAuth에서 발급한 유니크 코드


    if oauth_code:
        if request.COOKIES:

            ''' 7. 발급된 코드를 기반으로 토큰키를 발행함. 아래의 파라미터는 모두 필수 파라미터임.
            ** 주의) redirect_uri는 login_check 에 등록된 리다이렉트 URL과 같아야만 됨.
            '''
            token_request_param = {
                    "code": oauth_code,
                    "client_id": "mme",
                    "client_secret": "lge",
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
            }
            res_code3, res_dict3, cookies = call(auth_url, token_request_param, 'post', {"LGSESSIONID": request.COOKIES.get('LGSESSIONID')})
        if res_code3 == 200:
            for key, val in res_dict3.items():
                request.session[key] = val
            # return redirect('/login_complete')

            #token값 조회
            '''
            8. 발행된 토큰 정보를 가져옮.
            ** 실제 로그인 토큰이 만들어진 상태임.
            ** user_name이 엘지 사번임!!!. 해당 번호를 가지고 회원 맵핑을 해서 EDX로그인을 해야함.
            '''
            res_code4, res_dict4, _ = call(check_token_url + '?token=' + res_dict3['access_token'])

            '''
            추가 정보 조회.
            위의 8에서 맵핑을 완료하였을경우, 아래의 코드는 필요없음.
            런닝넷의 사용자 프로파일 정보를 조회하여 EDX에 가져오는 코드임.
            '''
            #상세 정보 조회
            user_code, user_info = get_profile_info({"LGSESSIONID": request.COOKIES.get('OAuthInfoifres'), 'LNETID': request.COOKIES.get('LNETID')})

            return JsonResponse({'token_info':res_dict3, 'token_check': res_dict4, 'user_info': user_info})

            #return HttpResponse(request.session['access_token'])

        elif res_code3 == 400:

            '''
            토큰을 받은 후 새로고침등을 하였을때 토큰 정보를 조회함.
            *** 해당 코드는 샘플용임. 위의 8에서 edx 회원 맵핑이 안되었을시에 아래의 코드와 EDX의 사용자정보를 맵핑하여 처리할 수 있음.
            '''
            #OAuth Token
            access_token = request.session.get('access_token')
            # OAuth를 갱신할시 사용하는 token
            refresh_token = request.session.get('refresh_token')

            #token값 조회
            res_code4, res_dict4, _ = call(check_token_url + '?token=' + access_token)

            #상세 정보 조회
            user_code, user_info = get_profile_info({"LGSESSIONID": request.COOKIES.get('OAuthInfo'), 'LNETID': request.COOKIES.get('LNETID')})

            return JsonResponse({'tocken_check': res_dict4, 'user_info': user_info, "LGSESSIONID": request.COOKIES.get('LGSESSIONID'), 'LNETID': request.COOKIES.get('LNETID')})



        else:
            
            html_msg = """
            <html>
            <body>
            <p><h2>OAuth 서버를 체크해주세요.<h2></p>
            <p><h3>응답코드: """ + str(res_code3) +"""</h3></p>
            <p><a href="javascript:history.go(-1);">뒤로가기</a>
            </body>
            </html>
            """

            return HttpResponse(html_msg)
            #return 'BadRequest'

    # return render_to_response('login_test/pass_to_login.html')
    return redirect('/')

# def login_complete(request):
#     _, get_user_info, _ = call(get_info_url,{})
#     print 'session == ', request.session['access_token']
#     print 'get_user_info == ', get_user_info
#     return render_to_response('login_test/pass_to_login.html')

def call(url,param={},method='get',cookies={}):
    
    if method == 'get':
        print 'get'
        response = requests.get(
            url=url,
            params=param,
            headers={
                "Authorization": "",
                "Content-Type": "application/json",
            },
            cookies = cookies
        )
    else:
        print 'post'
        response = requests.post(
            url=url,
            params=param,
            headers={
                "Authorization": "",
                "Content-Type": "application/json",
            },
            cookies = cookies
        )

    return response.status_code, json.loads(response.content), response.cookies

def get_profile_info(cookies_info):

    response = requests.get(
        url=get_info_url,
        headers={
            "Authorization": "",
            "Content-Type": "application/json",
        },
        cookies = cookies_info
    )
    return response.status_code, json.loads(response.content)




