# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import time
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from openedx.core.djangoapps.safe_sessions.middleware import SafeCookieData
from . import MaFpsCommon
from . import mapreprocessor
from xmodule.modulestore.django import modulestore
from certificates.api import get_active_web_certificate
from opaque_keys.edx.keys import CourseKey
import MySQLdb as mdb
from django.conf import settings
from django.http import HttpResponse, JsonResponse


@csrf_exempt
def servey_check(request):
    survey_code = request.POST.get('survey_code')
    course_id = request.POST.get('course_id')
    user_id = request.POST.get('user_id')
    con = mdb.connect(settings.DATABASES.get('default').get('HOST'),
                      settings.DATABASES.get('default').get('USER'),
                      settings.DATABASES.get('default').get('PASSWORD'),
                      settings.DATABASES.get('default').get('NAME'),
                      charset='utf8')

    cur = con.cursor()
    query = """
            SELECT detail_code
              FROM code_detail
             WHERE group_code = 999;
            """
    cur.execute(query)
    servey_check_code = cur.fetchall()

    check_flag = 'false'
    if (survey_code.strip() == servey_check_code[0][0].strip()):
        query = """
            INSERT INTO survey_check(course_id, regist_id, regist_date)
            VALUES ('{0}', '{1}', now());
            """.format(course_id, user_id)
        cur.execute(query)
        print 'insert query ========='
        print query
        print 'insert query ========='
        con.commit()

        check_flag = 'true'
    else:
        check_flag = 'false'

    return JsonResponse({'return': check_flag})


@csrf_exempt
def certificate_print(request):
    print_index_css = '''
            <style>
            body {
                width: 100%!important;
                height: 100%!important;
                margin: 0!important;
                padding: 0!important;
                background-color: #ddd!important;
                font-family:'malgun gothic', 맑은 고딕 !important;
            }
            h1, h2, h3, h4, h5, .hd-1, .hd-2, .accomplishment-rendering .accomplishment-statement-lead, .hd-3, .hd-4, .hd-5, .hd-6{
                line-height: inherit !important;
            }
            h1, h2, h3, h4, h5 {
                
            }
            h6 {
                font-size: 12px!important;
                margin-bottom: 2px!important;
                margin-top: 0px!important;
                font-weight: normal!important;
            }
            * {
                box-sizing: border-box!important;
                -moz-box-sizing: border-box!important;
            }
            ul{
                border-left: 3px solid #333!important;
                padding-left: 15px!important;
                font-size:14px!important;
            }
            ul li{
                list-style:none!important;
            }
            .paper {
                width: 230mm;
                min-height: 297mm;
                padding: 6.5mm!important;
                margin: 10mm auto!important;
                background: #fff!important;
                box-shadow: 0 0 5px rgba(0, 0, 0, 0.1)!important;
                position:relative!important;
            }
            ul, .list-bulleted{
                margin-left: 0px !important;
            }
            .content {
                padding: 25px!important;
                border: 4px solid #6c6f73!important;
                height: 90%!important;
                width: 100%!important;
                position:relative!important;
            }
            @page {
                size: A4!important;
                margin: 0!important;
            }
            @media print {
                html, body {
                    width: 100%!important;
                    height: 100%!important;
                    background: #fff!important;
                }
                .page {
                    margin: 0;
                    border: initial;
                    border-radius: initial;
                    width: initial;
                    min-height: initial;
                    box-shadow: initial;
                    background: initial;
                    page-break-after: always;
                }
            }
            .ribbon{
                display: inline-block!important;
                position: absolute!important;
                right: 110px!important;
                z-index: 10!important;
                top: 0px!important;
            }
            h5{margin:0!important;}
            .t-center{
                display:inline-block!important;
                margin-left: 20px!important;
                width:160px!important;
                float: left!important;
            }
            .t-center_empty {
                width: 0px !important;
                margin: 0px !important;
            }
            .t-sign{
                margin-bottom: 5px;
                padding-bottom: 5px;
                border-bottom: 1px solid #333;
            }
            .t-center:first-child{
                margin-left:3px;
            }
            .t-center h5{
                text-align:center!important;
                font-size:11px!important;
            }
            .ce-bg{
                background:url(${static_url}/static/images/certi_bg2.png) no-repeat!important;
                width: 643px!important;
                height: 232px!important;
                display: inline-block!important;
                position: absolute!important;
                top: 393px!important;
                left: 100px!important;
            }
            .ce-t-gray{
                color:#959595!important;
                font-size:15px!important;
            }
            .content .k_h1 {
                font-size:50px!important;
                margin-bottom: 46.5px!important;
                margin-top: 36.5px!important;
            }
            .content .e_h1 {
                font-size:43px!important;
                margin-bottom: 55px!important;
                margin-top: 45px!important;
            }
            .content h2 {
                font-size:20px!important;
            }
            .ce-txt-second {
                margin-top: 0px!important;
                font-size: 20px!important;
            }
            .ce-center-txt1{
                text-align: center!important;
                margin: 0 auto!important;
                margin-bottom: 20px!important;
                margin-top: -10px!important;
            }
            .sign-area{
                display:inline-block!important;
                width:100%!important;
                margin-bottom: -80px;
            }
            .sign-area-depth1, .sign-area-depth2, .sign-area-depth0{
                display:block!important;
                height:70px!important;
                width: 100%!important;
                float: left!important;
                margin-top: 10px;
            }
            .sign-area-depth2{
                margin-bottom: 10px;
            }
            .sign-none{
                display:inline-block!important;
                text-indent:-9999px!important;
                overflow:hidden!important;
            }
            .ce-logo-area{
                display:inline-block!important;
                width:100%!important;
            }
            .ce-logo1{
                float:right!important;
                font-size: 25px!important;
            }
            .ce-logo2{
                float:left!important;
                margin-top: 21px!important;
            }
            #k_box1{
                visibility: visibility;
                margin-bottom: 0px!important;
            }
            #e_box1{
                visibility: visibility;
                margin-bottom: 0px!important;
            }
            .t-sign {
                height: 34px!important;
                width: 160px!important;
            }
            .ce-logo1 {
                height: 60px!important;
                width: auto!important;
                margin-top: 20px!important;
            }
            .check_img {
                height: 20px!important;
                width: 14px!important;
            }
            .certifi_index {
                font-size:14px!important;
            }
            .e_name_text {
                margin-top: 0px!important;
            }
            .helloworld{
              margin-top: -15px;
              margin-bottom: 20px;
              font-size: 20px;
              color: #8a8585;
            }
            '''
    language_flag = request.POST.get('language_flag')
    multisite = request.POST.get('multisite')

    logo_eng = request.POST.get('logo_eng')
    logo_kor = request.POST.get('logo_kor')

    print "meaps / logo_eng -> ", logo_eng
    print "meaps / logo_kor -> ", logo_kor

    checkbox1 = request.POST.get('checkbox1')
    checkbox2 = request.POST.get('checkbox2')
    checkbox3 = request.POST.get('checkbox3')
    checkbox4 = request.POST.get('checkbox4')
    static_url = request.POST.get('static_url')

    print "meaps / static_url -> ", static_url

    certificate_id_number = request.POST.get('certificate_id_number')
    created_date = request.POST.get('created_date')
    nice_check_flag = request.POST.get('nice_check_flag')
    accomplishment_copy_name = request.POST.get('accomplishment_copy_name')
    user_name = request.POST.get('user_name')
    birth_date = request.POST.get('birth_date')
    accomplishment_course_title = request.POST.get('accomplishment_course_title')
    course_id = request.POST.get('course_id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    Play_h = request.POST.get('Play_h')
    Play_m = request.POST.get('Play_m')
    course_week = request.POST.get('course_week')
    course_effort_h = request.POST.get('course_effort_h')
    course_effort_m = request.POST.get('course_effort_m')
    grade = request.POST.get('grade')
    certificate_date_issued2 = request.POST.get('certificate_date_issued2')
    certificate_date_issued = request.POST.get('certificate_date_issued')

    print "multisite -> ", multisite

    logo_eng_full_path = static_url + logo_eng
    logo_kor_full_path = static_url + logo_kor

    print "logo_eng_full_path -> ", logo_eng_full_path
    print "logo_kor_full_path -> ", logo_kor_full_path

    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)
    preview_mode = None
    certificate_data = get_active_web_certificate(course, preview_mode)

    signatories_exists = False

    if certificate_data and 'signatories' in certificate_data:
        signatories = certificate_data['signatories']

        for signatory in signatories:
            # 서명인의 입력된 이름을 확인하여 이름이 존재하면 break
            if signatory['name']:
                signatories_exists = True
                break

    classfy_k = request.POST.get('classfy_k')
    classfy_e = request.POST.get('classfy_e')
    logo_index = request.POST.get('logo_index')
    org_name_k = request.POST.get('org_name_k')
    org_name_e = request.POST.get('org_name_e')
    e_name = request.POST.get('e_name')

    print_index_css = print_index_css.replace('${static_url}', static_url)

    print_index = ''
    f = open("/edx/app/edxapp/edx-platform/lms/templates/certificates/_accomplishment-rendering_kmooc_N_print.html",
             'r')
    while True:
        certificate_index = f.readline()
        if not certificate_index: break
        print_index += str(certificate_index)
    f.close()

    print_index_flag = print_index.split('<!-- language_flag -->')

    if language_flag == 'K':
        print_index = print_index_flag[0]
        if multisite != '':
            print_index_css += '''
                        .ce-center-txt2{
                            text-align:center!important;
                            margin-bottom: 35px!important;
                            font-size: 20px;
                        }
                        </style>
                        '''
            print_index = print_index.replace('${multisite}', multisite)
        else:
            print_index_css += '''
            .ce-center-txt2{
                text-align:center!important;
                margin-bottom: 80px!important;
                font-size: 20px;
            }
            </style>
            '''
            print_index = print_index.replace('${multisite}', '')
        if (checkbox3 == 'true'):
            print_index = print_index.replace('${k_box3}', '<li id="k_box3" >총 주차 : ${course_week} 주</li>')
        else:
            print_index = print_index.replace('${k_box3}', '')
        if (checkbox4 == 'true'):
            print_index = print_index.replace('${k_box4}',
                                              '<li id="k_box4" >학습인정시간 : ${course_effort_h}시간 ${course_effort_m}분</li>')
        else:
            print_index = print_index.replace('${k_box4}', '')
        if (checkbox2 == 'true'):
            print_index = print_index.replace('${k_box2}', '<li id="k_box2" >총 동영상시간 : ${Play_h}시간 ${Play_m}분</li>')
        else:
            print_index = print_index.replace('${k_box2}', '')

        if (checkbox1 == 'true'):
            print_index = print_index.replace('${k_box1}', '''
            <h5 class="ce-t-gray">성적</h5>
            <h4 class="ce-txt-second">${grade}</h4>
            ''')
            print_index_css = print_index_css.replace('visibility: hidden;', 'visibility: visibility;')
        else:
            print_index = print_index.replace('${k_box1}', '''
            <h5 class="ce-t-gray">성적</h5>
            <h4 class="ce-txt-second">${grade}</h4>
            ''')
            print_index_css = print_index_css.replace('visibility: visibility;', 'visibility: hidden;')

        # 마크애니 / 한글로고
        print_index = print_index.replace('${logo_area}', '<img class="ce-logo1" src="' + logo_kor_full_path + '" alt="${org_name_k}">')

        """
        if (os.path.isfile('/edx/var/edxapp/staticfiles/images/univ/logo01_' + logo_index + '.png')):
            print_index = print_index.replace('${logo_area}',
                                              '<img class="ce-logo1" src="${static_url}/static/images/univ/logo01_${logo_index}.png" alt="${org_name_k}">')
        else:
            print_index = print_index.replace('${logo_area}', '<b><p class="ce-logo1">' + org_name_k + '</p></b>')
        """

    elif language_flag == 'E':
        print_index = print_index_flag[1]
        if multisite != '':
            print_index = print_index.replace('${multisite}', multisite)
        else:
            print_index_css += '''
            </style>
            '''
            print_index = print_index.replace('${multisite}', '')
        if (checkbox3 == 'true'):
            print_index = print_index.replace('${e_box3}',
                                              '<li id="e_box3">Total no. of weeks : ${course_week} weeks</li>')
        else:
            print_index = print_index.replace('${e_box3}', '')

        if (checkbox4 == 'true'):
            print_index = print_index.replace('${e_box4}',
                                              '<li id="e_box4">Accredited learning time : ${course_effort_h} hours ${course_effort_m} minutes</li>')
        else:
            print_index = print_index.replace('${e_box4}', '')
        if (checkbox2 == 'true'):
            print_index = print_index.replace('${e_box2}',
                                              '<li id="e_box2">Total hours of video instruction : ${Play_h} hours ${Play_m} minutes</li>')
        else:
            print_index = print_index.replace('${e_box2}', '')
        if (checkbox1 == 'true'):
            print_index = print_index.replace('${e_box1}', '''
            <h5 class="ce-t-gray">SCORE</h5>
            <h4 class="ce-txt-second">${grade}</h4>
            ''')
            print_index_css = print_index_css.replace('visibility: hidden;', 'visibility: visibility;')
        else:
            print_index = print_index.replace('${e_box1}', '''
            <h5 class="ce-t-gray">SCORE</h5>
            <h4 class="ce-txt-second">${grade}</h4>
            ''')
            print_index_css = print_index_css.replace('visibility: visibility;', 'visibility: hidden;')

        # 마크애니 / 영문로고
        print_index = print_index.replace('${logo_area}', '<img class="ce-logo1" src="' + logo_eng_full_path + '" alt="${org_name_k}">')
        """
        if (os.path.isfile('/edx/var/edxapp/staticfiles/images/univ_e/logo01_' + logo_index + '_e.png')):
            print_index = print_index.replace('${logo_area}',
                                              '<img class="ce-logo1" src="${static_url}/static/images/univ_e/logo01_${logo_index}_e.png" alt="${org_name_e}">')
        else:
            print_index = print_index.replace('${logo_area}', '<b><p class="ce-logo1">' + org_name_e + '</p></b>')
        """

    print_index = print_index.replace('${certificate_id_number}', certificate_id_number)
    print_index = print_index.replace('${created_date}', created_date)

    # 본인인증 여부에 따라 성명 표시의 내용이 달라짐
    # 인증 X : 0, 인증 O : 1

    if nice_check_flag == '0':
        if (language_flag == 'K'):
            print_index = print_index.replace('${nice_check_flag}',
                                              '<h4 class="ce-txt-second"><p class="e_name_text">${accomplishment_copy_name}</p></h4>')
        else:
            if (e_name == ''):
                print_index = print_index.replace('${nice_check_flag}',
                                                  '<h4 class="ce-txt-second"><p class="e_name_text">${user_name}(Born in ${birth_date}) <span class="certifi_index">( <img class="check_img" src="${static_url}/static/images/correct-icon.png"> ID confirmed)</span></p></h4>')
            else:
                print_index = print_index.replace('${nice_check_flag}',
                                                  '<h4 class="ce-txt-second"><p class="e_name_text">${e_name}</p></h4>')

        print_index = print_index.replace('${nice_check_flag2}',
                                          '<h2 class="ce-center-txt1">This is to certify that ${accomplishment_copy_name}<br>successfully completed the course.</h2>')
    else:
        if (language_flag == 'K'):
            print_index = print_index.replace('${nice_check_flag}',
                                              '<h4 class="ce-txt-second"><p class="e_name_text">${user_name}(${birth_date}) <span class="certifi_index">( <img class="check_img" src="${static_url}/static/images/correct-icon.png"> 본인인증됨)</span></p></h4>')
        else:
            if (e_name == ''):
                print_index = print_index.replace('${nice_check_flag}',
                                                  '<h4 class="ce-txt-second"><p class="e_name_text">${user_name}(Born in ${birth_date}) <span class="certifi_index">( <img class="check_img" src="${static_url}/static/images/correct-icon.png"> ID confirmed)</span></p></h4>')
                print_index = print_index.replace('${nice_check_flag2}',
                                                  '<h2 class="ce-center-txt1">This is to certify that ${user_name}<br>successfully completed the course.</h2>')
            else:
                print_index = print_index.replace('${nice_check_flag}',
                                                  '<h4 class="ce-txt-second"><p class="e_name_text">${e_name}</p></h4>')
                print_index = print_index.replace('${nice_check_flag2}',
                                                  '<h2 class="ce-center-txt1">This is to certify that ${e_name}<br>successfully completed the course.</h2>')

    print_index = print_index.replace('${accomplishment_copy_name}', accomplishment_copy_name)
    print_index = print_index.replace('${user_name}', user_name)
    print_index = print_index.replace('${birth_date}', birth_date)
    accomplishment_course_title = accomplishment_course_title.split('!@#')
    print_index = print_index.replace('${accomplishment_course_title[0]}', accomplishment_course_title[0])
    print_index = print_index.replace('${accomplishment_course_title[1]}', accomplishment_course_title[1])
    print_index = print_index.replace('${course_id}', course_id)
    start_date_index = start_date.split(' ')
    print_index = print_index.replace('${start_date_index[0]}', start_date_index[0])
    print_index = print_index.replace('${start_date_index[1]}', start_date_index[1])
    print_index = print_index.replace('${start_date_index[2]}', start_date_index[2])
    end_date_index = end_date.split(' ')
    print_index = print_index.replace('${end_date_index[0]}', end_date_index[0])
    print_index = print_index.replace('${end_date_index[1]}', end_date_index[1])
    print_index = print_index.replace('${end_date_index[2]}', end_date_index[2])
    print_index = print_index.replace('${Play_h}', Play_h)
    print_index = print_index.replace('${Play_m}', Play_m)
    print_index = print_index.replace('${course_week}', course_week)
    print_index = print_index.replace('${course_effort_h}', course_effort_h)
    print_index = print_index.replace('${course_effort_m}', course_effort_m)
    print_index = print_index.replace('${grade}', grade)
    print_index = print_index.replace('${certificate_date_issued2}', certificate_date_issued2)
    print_index = print_index.replace('${certificate_date_issued}', certificate_date_issued)
    print_index = print_index.replace('${e_name}', e_name)

    certificate_data_index = ''

    # 서명인 정보가 없을 경우 영역만 할당하고 내용을 비움
    if signatories_exists:
        if certificate_data:
            certificate_data_index += '<div class="sign-area-depth2">'
            cnt = 0
            for i in range(0, 10):
                cnt = cnt + 1
                if i < 10 - len(certificate_data.get('signatories', [])):
                    certificate_data_index += '''
                    <div class="t-center_empty">
                        <h5></h5>
                        <h5></h5>
                        <h5></h5>
                        <h5></h5>
                    </div>
                    '''
                    if cnt == 5:
                        certificate_data_index += '''
                        </div>
                        <div class="sign-area-depth1">
                        '''
                elif i >= 10 - len(certificate_data.get('signatories', [])):
                    if cnt == 5:
                        certificate_data_index += '''
                        </div>
                        <div class="sign-area-depth1">
                        '''
                    elif cnt == 9:
                        certificate_data_index += '''
                        </div>
                        <div class="sign-area-depth0">
                        '''
                    signatory_index = len(certificate_data.get('signatories', [])) - (10 - i)
                    signatory = certificate_data.get('signatories', [])[signatory_index]
                    teacher = signatory['name']
                    if teacher.find('(') == -1:
                        teacher = teacher + '(' + teacher
                    teacher = teacher.split('(')
                    title_k = signatory['title']
                    if signatory['title'].find('(') == -1:
                        title_k = title_k + '(' + title_k
                    title_k = title_k.split('(')
                    organization_k = signatory['organization']
                    if organization_k.find('(') == -1:
                        organization_k = organization_k + '(' + organization_k
                    organization_k = organization_k.split('(')
                    if (language_flag == 'K'):
                        certificate_data_index += '''
                        <div class="t-center">
                            <img class="t-sign" src="${static_url}${signatory['signature_image_path']}" alt="">
                            <h5>${teacher[0]} ${title_k[0]}</h5>
                            <h5>${organization_k[0]}</h5>
                        </div>
                        '''
                    if (language_flag == 'E'):
                        certificate_data_index += '''
                        <div class="t-center">
                            <img class="t-sign" src="${static_url}${signatory['signature_image_path']}" alt="">
                            <h5>${teacher[1]} ${title_k[1]}</h5>
                            <h5>${organization_k[1]}</h5>
                        </div>
                        '''
                    certificate_data_index = certificate_data_index.replace("${signatory['signature_image_path']}",
                                                                            signatory['signature_image_path'])
                    certificate_data_index = certificate_data_index.replace('${teacher[0]}', teacher[0])
                    certificate_data_index = certificate_data_index.replace('${teacher[1]}', teacher[1].replace(')', ''))
                    certificate_data_index = certificate_data_index.replace('${title_k[0]}', title_k[0].replace(')', ''))
                    certificate_data_index = certificate_data_index.replace('${title_k[1]}', title_k[1].replace(')', ''))
                    certificate_data_index = certificate_data_index.replace('${organization_k[0]}', organization_k[0])
                    certificate_data_index = certificate_data_index.replace('${organization_k[1]}',
                                                                            organization_k[1].replace(')', ''))
                    certificate_data_index = certificate_data_index.replace('${classfy_k}', classfy_k)
                    certificate_data_index = certificate_data_index.replace('${classfy_e}', classfy_e)
            certificate_data_index += '</div>'
    else:
        certificate_data_index += '<div class="sign-area-depth2"></div><div class="sign-area-depth1"></div>'

    print_index = print_index.replace('${certificate_data_index}', certificate_data_index)
    print_index = print_index.replace('${logo_index}', logo_index)
    print_index = print_index.replace('${org_name_k}', org_name_k)
    print_index = print_index.replace('${org_name_e}', org_name_e)

    print_index = print_index.replace('${static_url}', static_url)
    strHtmlData = print_index_css
    strHtmlData += '''
            <HTML>
            <HEAD>
            <TITLE>KMOOC 이수증</TITLE>
            <META http-equiv=Content-Type content="text/html; charset=utf-8">
            <META content="MSHTML 6.00.2800.1458" name=GENERATOR>
            </HEAD>
            <BODY text=#000000 bgColor=#ffffff leftMargin=0 topMargin=0 marginheight="0" marginwidth="0">
            {print_index}
            </BODY>
            </HTML>
    '''.format(print_index=print_index)
    if (strHtmlData.find('"k_box1"') == -1 and strHtmlData.find('"e_box1"') == -1):
        strHtmlData = strHtmlData.replace('</blockquote>', '</blockquote><div id="k_box1"></div>')
    strEncodeHtmlData = str(strHtmlData.encode("utf-8"))

    print 'strEncodeHtmlData ---------------------------------------------- s'
    print strEncodeHtmlData
    print 'strEncodeHtmlData ---------------------------------------------- e'

    response = MaFpsTail(request, strEncodeHtmlData, len(strEncodeHtmlData))
    return response


@csrf_exempt
def series_print(request):
    print "### call series_print"
    print_index = request.POST.get('print_index')

    strHtmlData = '''
        <HTML>
            <HEAD>
                <TITLE>KMOOC 시리즈강좌</TITLE>
                <META http-equiv=Content-Type content="text/html; charset=utf-8">
                <META content="MSHTML 6.00.2800.1458" name=GENERATOR>
            </HEAD>
                <BODY text=#000000 bgColor=#ffffff leftMargin=0 topMargin=0 marginheight="0" marginwidth="0">
                {print_index}
            </BODY>
        </HTML>
    '''.format(print_index=print_index)
    strHtmlData = strHtmlData.replace('<script src="//code.jquery.com/jquery-1.11.3.min.js"></script>', '')

    print 'strHtmlData ---------------------------------------------- s (series)'
    print strHtmlData
    print 'strHtmlData ---------------------------------------------- e (series)'

    strEncodeHtmlData = str(strHtmlData.encode("utf-8"))

    response = MaFpsTail(request, strEncodeHtmlData, len(strEncodeHtmlData))
    return response


@csrf_exempt
def index(request):
    MaFpsCommon.MaSetVariable(request)

    template = loader.get_template('markany/index.html')
    context = {
        'strWebHome': MaFpsCommon.strWebHome,
        'strJsWebHome': MaFpsCommon.strJsWebHome,
    }

    return HttpResponse(template.render(context, request))


@csrf_exempt
def MaSample(request):
    context = {
        'strName': '김동화',
        'strJuminNo': '880808-1234567',
    }

    strHtmlData = render_to_string('markany/sampleh.html', context)

    print 'strHtmlData ---------------------------------------------- s'
    print strHtmlData
    print 'strHtmlData ---------------------------------------------- e'

    strEncodeHtmlData = str(strHtmlData.encode("utf-8"))

    response = MaFpsTail(request, strEncodeHtmlData, len(strEncodeHtmlData))
    return response


def MaFpsTail(request, strHtmlData, iHtmlDataSize):
    # print 'session key:', request.session.session_key, '[3]'
    strRetCode = ''
    iRetCode = 0

    strAddData = ''
    strAMetaData = ''
    iAMetaDataSize = 0

    ma_cookie_data = ''

    print "MaFpsCommon.strMAServerIP -> ", MaFpsCommon.strMAServerIP
    print "MaFpsCommon.iMAServerPort -> ", MaFpsCommon.iMAServerPort

    (strRetCode, strAMetaData) = mapreprocessor.strMaPrestreamWmByte(MaFpsCommon.strMAServerIP,
                                                                     MaFpsCommon.iMAServerPort, strHtmlData,
                                                                     iHtmlDataSize, MaFpsCommon.iCellBlockCount,
                                                                     MaFpsCommon.iCellBlockRow)

    print "strRetCode -> ", strRetCode
    print "mapreprocessor.ISUCCESS -> ", mapreprocessor.ISUCCESS

    import logging
    logging.info('---------------------------')
    logging.info('strRetCode -> ' + str(strRetCode))
    logging.info('---------------------------')

    if strRetCode != mapreprocessor.ISUCCESS:
        iRetCode = int(strRetCode)
        if (iRetCode == 1001) or (iRetCode == 10001):
            strErrorMessage = "Error code : " + strRetCode + " 마크애니 데몬프로세스를 구동해주세요."
        elif (iRetCode == 70007):
            strErrorMessage = "Error code : " + strRetCode + " 바코드 사이즈가 작습니다."

        return HttpResponse(strErrorMessage)

    iAMetaDataSize = len(strAMetaData)

    # strUserAgent = request.META
    strUserAgent = request.META.get('HTTP_USER_AGENT')
    MaFpsCommon.MaSetVariable(request)
    # print("strDomain : " + MaFpsCommon.strDomain )
    # print("tototoday : " + MaFpsCommon.tototoday)
    # print("PRINTERUPDATE : " + MaFpsCommon.PRINTERUPDATE )
    # PRINTERUPDATE = base64.encodestring(strPrtDatDownURL)

    browserinfo = mapreprocessor.ma_getBrowserInfo(strUserAgent)
    iRetOsCheck = browserinfo[0]
    browsername = browserinfo[1]
    browserversion = browserinfo[2]

    ma_cookie_data_temp = mapreprocessor.ma_parse_cookie(request.COOKIES)

    if iRetOsCheck == 1:
        ma_cookie_data = "Cookie: " + ma_cookie_data_temp;

    strVersion = ''
    strSID = ''

    strUserIdFromSession = ''

    '''
    iNotSessionInCookie = 0
    '''
    from openedx.core.djangoapps.safe_sessions.middleware import SafeSessionMiddleware

    print 'request.COOKIES ----------------------------------------------------------- s'
    print request.COOKIES
    print 'request.COOKIES ----------------------------------------------------------- e'

    if not request.session.session_key:
        request.session.save()
        strUserIdFromSession = get_random_string()
    else:
        strUserIdFromSession = SafeSessionMiddleware.get_user_id_from_session(request)

    strSID = request.session.session_key

    safe_cookie_data = SafeCookieData.create(strSID, strUserIdFromSession)
    serialized_value = unicode(safe_cookie_data)

    ma_cookie_data = ma_cookie_data + "sessionid=" + serialized_value + ";"
    # print "ma_cookie_data"
    # print ma_cookie_data

    # if iNotSessionInCookie == 1:
    strBase64Cookie = base64.standard_b64encode(ma_cookie_data)

    pversion = "NONE"
    iCurrent = 0
    iSession = 0
    iSessionCheck = 0

    pversion = request.session.get('productversion', 'NONE')
    # print pversion

    if pversion != "NONE":
        strVersion = pversion.replace(MaFpsCommon.strSignature, "")
        iCurrent = MaFpsCommon.strPVersion
        iSession = strVersion
        if iSession >= iCurrent:
            iSessionCheck = 1

    if iRetCode == 0:
        if iRetOsCheck <= 4:
            # Windows OS
            strAddData += "#META_SIZE=" + str(iAMetaDataSize)
            strAddData += "#CPPARAM=" + MaFpsCommon.strCPParam
            strAddData += "#CPSUBPARAM=" + MaFpsCommon.strCPSubParam
            strAddData += "#PRTIP=" + MaFpsCommon.strServerName
            strAddData += "#PRTPORT=" + str(MaFpsCommon.iServerPort)
            strAddData += "#PRTPARAM=" + MaFpsCommon.strPrintParam
            strAddData += "#PRTURL=" + MaFpsCommon.strPrintURL
            strAddData += "#DOCTYPE=1";
            strAddData += "#PRTTYPE=0";
            strAddData += "#PSSTRING=" + MaFpsCommon.PSSTRING
            strAddData += "#PSSTRING2=" + MaFpsCommon.PSSTRING2
            strAddData += "#FAQURL=" + MaFpsCommon.FAQURL
            strAddData += "#WMPARAM=" + MaFpsCommon.WMPARAM
            strAddData += "#PRINTERDAT=" + MaFpsCommon.strDataFileName
            strAddData += "#PRINTERVER=" + MaFpsCommon.PRINTERVER
            strAddData += "#PRINTERUPDATE=" + MaFpsCommon.PRINTERUPDATE
            strAddData += "#CHARSET=" + MaFpsCommon.CHARSET
            strAddData += "#VIRTUAL=" + MaFpsCommon.VIRTUAL  # allow virtual
            strAddData += "#LANGUAGE=" + MaFpsCommon.LANGUAGE  # set lang
            strAddData += "#PAGEMARGIN=" + MaFpsCommon.PAGEMARGIN  # PAGEMARGIN L^T^R^B
            strAddData += "#PRINTCNT=" + MaFpsCommon.strPrintCount  # set printcount
            strAddData += "#STNODATA=" + MaFpsCommon.STNODATA  # Nodata -> Print
            strAddData += "#BUCLOSE=" + MaFpsCommon.BUCLOSE  # add close button
            strAddData += "#WINDOWSIZE=" + MaFpsCommon.WINDOWSIZE  # window size land^port
            strAddData += "#SHRINKTOFIT=" + MaFpsCommon.SHRINKTOFIT  # auto shrink print
            strAddData += "#FIXEDSIZE=" + MaFpsCommon.FIXEDSIZE  # adjust window size
            strAddData += "#PRTPROTOCOL=" + MaFpsCommon.strPrtProtocol  # prt protocol
            strAddData += "#PRTAFTEREXIT=" + MaFpsCommon.PRTAFTEREXIT  # after print close
            strAddData += "#NO2DBARCODE=" + MaFpsCommon.NO2DBARCODE;  # print no barcode
            strAddData += "#VIEWPAGE=" + MaFpsCommon.VIEWPAGE;  # ViewPage option
            strAddData += "#ZOOMINCONTENT =" + MaFpsCommon.ZOOMINCONTENT  # ViewPage option
            strAddData += "#HIDECD =" + MaFpsCommon.strHIDECD;  # hidden copydetector
            strAddData += "#PRINTTEXT=1";
            strAddData += "#PRINTCOPIES=" + MaFpsCommon.strPrintCount;

            if MaFpsCommon.CBFDIRECTORY != "":
                strAddData += "#CBFDIRECTORY =" + base64.standard_b64encode(MaFpsCommon.CBFDIRECTORY)  # CBFDIRECTORY
            if MaFpsCommon.CBFPRPOCESS != "":
                strAddData += "#CBFPRPOCESS =" + base64.standard_b64encode(MaFpsCommon.CBFPRPOCESS)  # CBFPRPOCESS

            strAddData = strAddData.replace("\\n", "\n");

    # print strAddData
    if (iRetOsCheck == 1) or (iRetOsCheck == 2):
        if len(strSID) > 128:
            strPath = strSID[:128] + MaFpsCommon.tototoday + ".matmp"
        else:
            strPath = strSID + MaFpsCommon.tototoday + ".matmp"

        strPath = strPath.replace(":", "c")

        filePath = MaFpsCommon.strDownFolder + "/" + strPath
        strDownURL = MaFpsCommon.strDownURL + MaFpsCommon.tototoday
        if MaFpsCommon.iUseNas == 1:
            fResult = open(filePath, 'wb')
            fResult.write(strAMetaData + strAddData)
            fResult.close()

        request.session['strDownURL'] = strDownURL
        request.session['strCookie'] = ma_cookie_data
        request.session.modified = True

    # print "strDownURL : " + strDownURL
    # print "strSessionURL : " + MaFpsCommon.strSessionURL

    strBase64DownURL = base64.standard_b64encode(strDownURL)
    strBase64SessionURL = base64.standard_b64encode(MaFpsCommon.strSessionURL)

    LaunchRegistAppCommand = ""
    if MaFpsCommon.iQuickSet == 1:
        LaunchRegistAppCommand = "quickurl"
    elif MaFpsCommon.iQuickSet == 0 or MaFpsCommon.iQuickSet == 2:
        if iSessionCheck == 0:
            LaunchRegistAppCommand = "registapp"
        else:
            LaunchRegistAppCommand = "sockmeta"

    template = loader.get_template('markany/MaFpsTail.html')
    context = {
        'strWebHome': MaFpsCommon.strWebHome,
        'strJsWebHome': MaFpsCommon.strJsWebHome,
        'strPyHome': MaFpsCommon.strPyHome,
        'strBase64Cookie': strBase64Cookie,
        'strSessionCheck': MaFpsCommon.strSessionCheck,
        'strBase64DownURL': strBase64DownURL,
        'strBase64SessionURL': strBase64SessionURL,
        'strSudongInstallURL': MaFpsCommon.strSudongInstallURL,
        'strApp': MaFpsCommon.strApp,
        'strIePopupURL': MaFpsCommon.strIePopupURL,
        'iVersion': MaFpsCommon.strPVersion,
        'iQuickSet': MaFpsCommon.iQuickSet,
        'iRetOsCheck': iRetOsCheck,
        'pversion': pversion,
        'iSessionCheck': iSessionCheck,
        'strImagePath': MaFpsCommon.strImagePath,
        'LaunchRegistAppCommand': LaunchRegistAppCommand,
    }

    return HttpResponse(template.render(context, request))


def MaIePopup(request):
    # print 'session key:', request.session.session_key, '[4]'
    # print "MaIePopup"
    strParamSessionURL = request.GET.get("sessionurl")
    # print strParamSessionURL

    MaFpsCommon.MaSetVariable(request)

    template = loader.get_template('markany/MaIePopup.html')
    context = {
        'strJsWebHome': MaFpsCommon.strJsWebHome,
        'strParamSessionURL': strParamSessionURL,
    }

    return HttpResponse(template.render(context, request))


@csrf_exempt
def MaSetInstall(request):
    '''
    print 'MaSetInstall META check s'
    print request.META
    print 'MaSetInstall META check e'
    print 'session key:', request.session.session_key, '[5]'
    '''
    # print "MaSetInstall"
    # strParam = request.GET.get("param", "NONE")
    strParam = request.POST.get("param", "NONE")

    # print "MaSetInstall " + strParam
    # safetyFileNameChek
    if strParam != "NONE":
        iFindIndex = strParam.find(MaFpsCommon.strSignature)
        if iFindIndex >= 0:
            request.session['productversion'] = strParam
            request.session.modified = True

    return HttpResponse("who are you")


def MaSessionCheck(request):
    # print 'session key:', request.session.session_key, '[5]'
    strParamPversion = request.session.get('productversion', 'NONE')
    strDownURL = request.session.get('strDownURL', 'NONE')
    strCookie = request.session.get('strCookie', 'NONE')

    # print "strParamPversion : " + strParamPversion
    # print "strDownURL : " + strDownURL
    # print "strCookie : " + strCookie
    strParamDownURL = base64.standard_b64encode(strDownURL)
    strParamCookie = base64.standard_b64encode(strCookie)

    # print strParamDownURL
    # print strParamCookie
    iTotal = 20
    iCnt = 0
    bValidVersion = False

    while True:
        strParamPversion = request.session.get('productversion', 'NONE')
        # print "productversion : " + strParamPversion
        if strParamPversion != "NONE":
            strVersion = strParamPversion.replace(MaFpsCommon.strSignature, "")
            iCurrent = MaFpsCommon.strPVersion
            iSession = strVersion
            if iSession >= iCurrent:
                bValidVersion = True

        if bValidVersion:
            break

        iCnt = iCnt + 1

        if iTotal <= iCnt:
            break

        time.sleep(0.5)

    if not (bValidVersion):
        result = strDownURL.split("fn=")
        filePath = MaFpsCommon.strDownFolder
        strSID = request.session.session_key

        # safetyFileNameCheck...
        # security check
        if len(strSID) > 128:
            strFileName = strSID[:128] + result[1] + ".matmp"
        else:
            strFileName = strSID + result[1] + ".matmp"

        strFileName = strFileName.replace(":", "c")
        strFullFileName = filePath + "/" + strFileName

        if os.path.exists(filePath) and os.path.isfile(strFullFileName):
            os.remove(strFullFileName)

        return HttpResponseRedirect(MaFpsCommon.strSudongInstallURL)

    template = loader.get_template('markany/MaSessionCheck.html')
    context = {
        'strImagePath': MaFpsCommon.strImagePath,
        'strJsWebHome': MaFpsCommon.strJsWebHome,
        'strSudongInstallURL': MaFpsCommon.strSudongInstallURL,
        'strParamCookie': strParamCookie,
        'strParamPversion': strParamPversion,
        'strParamDownURL': strParamDownURL,
        'strPVersion': MaFpsCommon.strPVersion,
        'strApp': MaFpsCommon.strApp,
        'iQuickSet': MaFpsCommon.iQuickSet,
    }

    return HttpResponse(template.render(context, request))


@csrf_exempt
def Mafndown(request):
    # print 'session key:', request.session.session_key, '[6]'
    # String requestFileNameAndPath = request.getParameter("fn");
    # String requestFileServerIp = request.getParameter("fs");
    # String requestDatFile = request.getParameter("prtdat");
    strFileName = ''
    strParamFileName = request.POST.get("fn", "NONE")
    filePath = MaFpsCommon.strDownFolder
    strSID = request.session.session_key

    # print "strParamFileName : " + strParamFileName
    strParamFileName = mapreprocessor.strSafetyFileNameCheck(strParamFileName)

    print 'strSID check ------------------------>', strSID

    if strParamFileName == "NONE":
        print 'Error'
    else:
        # safetyFileNameCheck...
        # security check
        if len(strSID) > 128:
            strFileName = strSID[:128] + strParamFileName + ".matmp"
        else:
            strFileName = strSID + strParamFileName + ".matmp"

        strFileName = strFileName.replace(":", "c")

    strFullFileName = filePath + "/" + strFileName

    if os.path.exists(filePath) and os.path.isfile(strFullFileName):
        with open(strFullFileName, 'rb') as fp:
            response = HttpResponse(fp.read())
            # response = FileResponse(open(strFullFileName, 'rb'))

        content_type = 'application/octet-stream'
        response['Content-Type'] = content_type
        response['Content-Length'] = str(os.stat(strFullFileName).st_size)
        response['Content-Disposition'] = 'attachment; fileName=' + strFileName

        os.remove(strFullFileName)

    return response


def MaInstallPage(request):
    # print 'session key:', request.session.session_key, '[7]'
    MaFpsCommon.MaSetVariable(request)

    template = loader.get_template('markany/MaInstallPage.html')
    context = {
        'strWebHome': MaFpsCommon.strWebHome,
        'strJsWebHome': MaFpsCommon.strJsWebHome,
    }

    return HttpResponse(template.render(context, request))


def MaGetSession(request):
    print 'session key:', request.session.session_key, '[8]'
    strParamPversion = request.session.get('productversion', 'NONE')
    strDownURL = request.session.get('strDownURL', 'NONE')
    strCookie = request.session.get('strCookie', 'NONE')

    print request.session.session_key
    print "strParamPversion : " + strParamPversion
    print "strDownURL : " + strDownURL
    print "strCookie : " + strCookie

    return HttpResponse("Result")


def MaMakeCookie(request):
    print 'session key:', request.session.session_key, '[9]'
    response = HttpResponse()
    response.set_cookie('test_cookie', 'value#1')
    response.set_cookie('test_donghwa', 'value#2')
    response.set_cookie('test-babo', 'value#3')

    request.session['productversion'] = 'MARKANYEPS25124'
    request.session.modified = True

    return response
