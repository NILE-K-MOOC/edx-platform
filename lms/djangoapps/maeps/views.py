# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.template.loader import render_to_string, get_template
from django.views.decorators.csrf import csrf_exempt
import base64
import os
import time
from . import mapreprocessor
from . import MaFpsCommon
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt

@ensure_csrf_cookie
def test(request):
    print 'Test!@!!@!#@!##!@#!#@!'

    return '3'

def MaSample(request):
    # strHtmlData = render_to_string('markany/sampleh.html')
    # strEncodeHtmlData = str(strHtmlData.encode("utf-8"))
    context = {
        'strName': '김동화',
        'strJuminNo': '880808-1234567',
    }

    strHtmlData = render_to_string('markany/sampleh.html', context)
    strEncodeHtmlData = str(strHtmlData.encode("utf-8"))

    response = MaFpsTail(request, strEncodeHtmlData, len(strEncodeHtmlData))
    return response


def MaFpsTail(request, strHtmlData, iHtmlDataSize):
    strRetCode = ''
    iRetCode = 0

    strAddData = ''
    strAMetaData = ''
    iAMetaDataSize = 0

    ma_cookie_data = ''

    (strRetCode, strAMetaData) = mapreprocessor.strMaPrestreamWmByte(MaFpsCommon.strMAServerIP,
                                                                     MaFpsCommon.iMAServerPort, strHtmlData,
                                                                     iHtmlDataSize, MaFpsCommon.iCellBlockCount,
                                                                     MaFpsCommon.iCellBlockRow)
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
    iNotSessionInCookie = 0

    if not request.session.session_key:
        request.session.save()
        iNotSessionInCookie = 1

    strSID = 'ytvamqjoiyr1h36spotbgtitc4po5hhc'
    print 'strSID=========='
    print strSID

    if iNotSessionInCookie == 1:
        ma_cookie_data = ma_cookie_data + "sessionid=" + strSID + ";"

    strBase64Cookie = base64.standard_b64encode(ma_cookie_data)

    pversion = "NONE"
    iCurrent = 0
    iSession = 0
    iSessionCheck = 0

    pversion = request.session.get('productversion', 'NONE')

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
    # print "MaSetInstall"
    # strParam = request.GET.get("param", "NONE")
    strParam = '1|0ht3t1vxoh42drg66xa2gt95b0ru9feo|4j1r8yquk25x|IjQ2Y2Q1MDdjYmM1NzgwNGRkYzdiODFlM2U5OGIzOTYyYTc3NWNlMTQ5NzEyOTBmNDZiYzNmZTMzNmI5MDMyZWUi:1eg3sQ:i534c9NZUsEwQp9JIEdKCjt_lwM'

    # print "MaSetInstall " + strParam
    # safetyFileNameChek
    if strParam != "NONE":
        iFindIndex = strParam.find(MaFpsCommon.strSignature)
        if iFindIndex >= 0:
            request.session['productversion'] = strParam
            request.session.modified = True

    return HttpResponse("who are you")


def MaSessionCheck(request):
    strParamPversion = request.session.get('productversion', 'NONE')
    strDownURL = request.session.get('strDownURL', 'NONE')
    strCookie = '1|0ht3t1vxoh42drg66xa2gt95b0ru9feo|4j1r8yquk25x|IjQ2Y2Q1MDdjYmM1NzgwNGRkYzdiODFlM2U5OGIzOTYyYTc3NWNlMTQ5NzEyOTBmNDZiYzNmZTMzNmI5MDMyZWUi:1eg3sQ:i534c9NZUsEwQp9JIEdKCjt_lwM'

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
        strSID = 'ytvamqjoiyr1h36spotbgtitc4po5hhc'
        print 'strSID=========='
        print strSID

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
        'strParamCookie': '1|0ht3t1vxoh42drg66xa2gt95b0ru9feo|4j1r8yquk25x|IjQ2Y2Q1MDdjYmM1NzgwNGRkYzdiODFlM2U5OGIzOTYyYTc3NWNlMTQ5NzEyOTBmNDZiYzNmZTMzNmI5MDMyZWUi:1eg3sQ:i534c9NZUsEwQp9JIEdKCjt_lwM',
        'strParamPversion': strParamPversion,
        'strParamDownURL': strParamDownURL,
        'strPVersion': MaFpsCommon.strPVersion,
        'strApp': MaFpsCommon.strApp,
        'iQuickSet': MaFpsCommon.iQuickSet,
    }

    return HttpResponse(template.render(context, request))


@csrf_exempt
def Mafndown(request):
    # String requestFileNameAndPath = request.getParameter("fn");
    # String requestFileServerIp = request.getParameter("fs");
    # String requestDatFile = request.getParameter("prtdat");
    strFileName = ''
    strParamFileName = request.POST.get("fn", "NONE")
    filePath = MaFpsCommon.strDownFolder
    strSID = 'ytvamqjoiyr1h36spotbgtitc4po5hhc'
    print 'strSID=========='
    print strSID

    # print "strParamFileName : " + strParamFileName
    strParamFileName = mapreprocessor.strSafetyFileNameCheck(strParamFileName)

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
    MaFpsCommon.MaSetVariable(request)

    template = loader.get_template('markany/MaInstallPage.html')
    context = {
        'strWebHome': MaFpsCommon.strWebHome,
        'strJsWebHome': MaFpsCommon.strJsWebHome,
    }

    return HttpResponse(template.render(context, request))


def MaGetSession(request):
    strParamPversion = request.session.get('productversion', 'NONE')
    strDownURL = request.session.get('strDownURL', 'NONE')
    strCookie = '1|0ht3t1vxoh42drg66xa2gt95b0ru9feo|4j1r8yquk25x|IjQ2Y2Q1MDdjYmM1NzgwNGRkYzdiODFlM2U5OGIzOTYyYTc3NWNlMTQ5NzEyOTBmNDZiYzNmZTMzNmI5MDMyZWUi:1eg3sQ:i534c9NZUsEwQp9JIEdKCjt_lwM'

    print request.session.session_key
    print "strParamPversion : " + strParamPversion
    print "strDownURL : " + strDownURL
    print "strCookie : " + strCookie

    return HttpResponse("Result")


def MaMakeCookie(request):
    response = HttpResponse()
    response.set_cookie('1|0ht3t1vxoh42drg66xa2gt95b0ru9feo|4j1r8yquk25x|IjQ2Y2Q1MDdjYmM1NzgwNGRkYzdiODFlM2U5OGIzOTYyYTc3NWNlMTQ5NzEyOTBmNDZiYzNmZTMzNmI5MDMyZWUi:1eg3sQ:i534c9NZUsEwQp9JIEdKCjt_lwM')

    request.session['productversion'] = 'MARKANYEPS25124'
    request.session.modified = True

    return response
