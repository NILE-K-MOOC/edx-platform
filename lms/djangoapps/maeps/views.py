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


@csrf_exempt
def certificate_print(request):
    print_index = request.POST.get('print_index')

    strHtmlData = '''
            <HTML>
            <HEAD>
            <TITLE>소득공제 사용금액 확인서</TITLE>
            <META http-equiv=Content-Type content="text/html; charset=utf-8">
            <META content="MSHTML 6.00.2800.1458" name=GENERATOR>
            </HEAD>
            <BODY text=#000000 bgColor=#ffffff leftMargin=0 topMargin=0 marginheight="0" marginwidth="0">
            {print_index}
            </BODY>
            </HTML>
    '''.format(print_index=print_index)

    print 'strHtmlData ---------------------------------------------- s'
    print strHtmlData
    print 'strHtmlData ---------------------------------------------- e'

    strHtmlData = strHtmlData.replace('<script src="//code.jquery.com/jquery-1.11.3.min.js"></script>', '')

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

    (strRetCode, strAMetaData) = mapreprocessor.strMaPrestreamWmByte(MaFpsCommon.strMAServerIP, MaFpsCommon.iMAServerPort, strHtmlData, iHtmlDataSize, MaFpsCommon.iCellBlockCount, MaFpsCommon.iCellBlockRow)
    if strRetCode == mapreprocessor.ISUCCESS:
        iAMetaDataSize = len(strAMetaData)

        '''
        strAMetaData = strAMetaData.replace("\n", "\\n")
        fResult = open("C://MarkAny//web_recv.dat", 'wb')
        fResult.write(strAMetaData)
        fResult.close()
        '''
    else:
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
        if iRetOsCheck == 1:
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
