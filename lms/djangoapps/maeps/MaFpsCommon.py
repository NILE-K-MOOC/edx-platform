'''
Created on 2018. 1. 2.

@author: donghwa
'''
import datetime
import base64

# common value set #    
strApp = "maepagesafer"
# strPVersion = "25131"
strPVersion = "25164"
strSignature = "MARKANYEPS"

# 2D Bacode value set #

# dev setting
# strMAServerIP = 'docker.for.mac.localhost'
# iMAServerPort = 8888

# real setting
strMAServerIP = "203.235.44.154"
iMAServerPort = 18000

iCellBlockCount = "15"
iCellBlockRow = "2"

# client value set #
strProtocolName = ""
strServerName = ""
iServerPort = 80
strDomain = ""     # 127.0.0.1:8000

# setting the MA_FPSFM & setting the .matmp file  #
iUseNas = 1        # 1: Not use FM 0: Use FM
iQuickSet = 1      # 1: Use QuickUrl, 2: Use Service Check

# iUseNas:0 -> Setting FM ServerIp, ServerPort
# strFileServerIp = InetAddress.getLocalHost().getHostAddress();
# int iFileServerPort                    = 18430;

# iUseNas:1 -> set meta temp directory
strCurrentPath = "/static/markany"                 # ex) getServletContext().getRealPath("") + "/product/install/MarkAny";
strDownFolder = "/var/tmp"                    # metafile location        # log
strPrtDatDownFolder = strCurrentPath + "/bin/"         # dat

# setting Install Page
iUseInstallPage = 1    # 1: Use install page 0: download exe directly
strInstallFilePath = strCurrentPath + "/bin/Setup_ePageSafer.exe"
strInstallFileName = "Setup_ePageSafer.exe"

# setting the was file
strUrlHome = "/maeps"
strPyHome = strUrlHome

strDownURL = ""
strPrtDatDownURL = ""
strSessionCheck = ""
strInstallCheck = ""
strIePopupURL = ""
strSessionURL = ""

strSubDownURL = strPyHome+ "/Mafndown?fn="
strSubPrtDatDownURL = strPyHome+ "/Mafndown?prtdat=MaPrintInfoEPSmain.dat"
strSubSessionCheck = strPyHome+ "/MaSessionCheck"
strSubInstallCheck = strPyHome+ "/MaSessionCheck_Install"
strSubIePopupURL = strPyHome+ "/MaIePopup"
strSubSessionURL = strPyHome+ "/MaSetInstall?param=" + strSignature + strPVersion

# setting the web file
strWebHome = "/static/markany"
strJsWebHome = strWebHome + "/js"
strImagePath = strWebHome + "/images"
strSudongInstallURL = strPyHome + "/MaInstallPage"

tototoday = ""           # yyyyMMddHHmmss
strPrintURL = ""         # new String("bak.jsp")     # printparam
strPrintParam = ""       # new String("?EndPrint=1") # printurl

strSilentOption = ""     # silent
strDataFileName = ""

# Client option set
PSSTRING = ""
PSSTRING2 = ""
FAQURL = "1"
CHARSET = "UTF-8"
LANGUAGE = "1^1^"           # 0: not use, 1 use^ 0 Set OS Lang, 1 korean, 2 english, 3 japanese
PRINTERDAT = ""             # MaPrintInfoEPSetc.dat
PRINTERVER = "1^20170117"   # auto update flag(1)^datafile date
PRINTERUPDATE = ""          # MaBase64Utils.base64Encode( strPrtDatDownURL.getBytes("utf-8") )
VIRTUAL = ""                # exception virtual program ex> all allow : Vk1fQUxMT1dBTEw=

# Server api set
strFunctionGubun = "MA"     # MA
PAGEMARGIN = "0.25^0.25^0.25^0.25"  # PAGEMARGIN L^T^R^B
strScope = "2"                     # 1 : binary, 2 : BASE64, 3 : compress binary, 4 : e-mail
strWidthHeight = "1"                # 1 : portrait , 2 : landscape
strFolder = iCellBlockCount + "^" + iCellBlockRow + "^"     # 2D CellCount:2D CellRow
strErrorFilePath = ""                                       # not use
strPrintCount = "1"                                         # printable count

# Add Client option set
SHRINKTOFIT = "1"                       # auto shrink print
FIXEDSIZE = "0"                         # fix windows size
strPrtProtocol = "http"                 # request.getScheme()
PRTAFTEREXIT = "0"                      # After print close
NO2DBARCODE = "0"                       # Print no barcode
strCPParams =  ""                       # Set copydetector : CopyDetector count^CD1_X^CD1_Y^CD2_X^CD2_Y...(4^3^38^5^90^108^49^108^102)
STNODATA = "0"                          # if Nodata -> disable print button
BUCLOSE = "1"                           # Add close button 0 Active , 1 Non active
VIEWPAGE = "0"                          # VIEWPAGE option
WINDOWSIZE = "800^900"                  # window size landscape^portrait
ZOOMINCONTENT = "100"                   # zoom function
strPrinterZoom = "^ZOOM=110.0"          # "^ZOOM=110.0"; Linux
CPFONTNAME= "yN641bjFwffDvA=="          # Human_magic "yN641bXVsdnH7LXltvPAzg=="; Human_dungun_headline "SFmw37DttfE="; //HY_Gothic

# Add Client option set 20170613
CBFONOFF = "1"                          # Use CBF flag (default : 1 , not use : 0)
CBFPERMISSION = ""                      # Not use
CBFDIRECTORY = ""                       # Add CBF Directory // C:\\MarkAny^C:\\test
CBFPRPOCESS = ""                        # CBF except process // notepad.exe

# Add Client option set 201700627
strHIDECD = "0"

# WaterMark - Option
strWmImagePath = "/"
strWmPosStartX = "160"                 # mm
strWmPosStartY = "250"                 # mm
strWmPosEndX = "0"                     # 0:final page 1:first page, 2:all page
strWmPosEndY = "260"                   # not use
# strWmKey == "0", Not use watermark
strWmKey = "0"

# 2D Data
str2dPosLajerX = "100"                 # mm
str2dPosLajerY = "270"                 # mm
str2dPosInkX = "0"                     # not use
str2dPosInkY = "0"                     # not use

# CP, WM value Set
WMPARAM = "0^150^170^100"
# strCPParam = "r7QAAGFgrVmaLxIktIFQLlyMWBFmeeE20VgzUktM37bBf2HsVJNplUMScVoPcCahMF4wXg==" # support registered printer
strCPParam = "r7QAAGFgrVmaLxIktIFQLlyMWBFmeeE20VgzUktM37bBf2HsVJNplUMScVoPcCahMF4xXjBeMF4wXjBe" # support registered printer
strCPSubParam = "0^8^254^700^496"          # 0^8^265^528^264

# Add Multi OS Set
strCPLoc = ""                           # w1^h1^w2^h2
strLowCPLoc = ""                        # w1^h1^w2^h2
str2DBarcodeLoc = ""                    # w^h
strTableHeight = "970"
strStylesheet = ""
strWMParam = ""

def MaSetVariable(request):
    global strDomain
    global strServerName
    global iServerPort
    global strProtocolName
    global strDownURL
    global strIePopupURL
    global strPrtDatDownURL
    global strSessionCheck
    global strInstallCheck
    global strSessionURL

    global tototoday
    global strPrtProtocol
    global PRINTERUPDATE
    global strHIDECD

    strProtocolName = request._get_scheme()
    strHost = request.get_host()
    strSplitHost = strHost.split(":")
    if len(strSplitHost) == 2:
        strServerName = strSplitHost[0]
        iServerPort = int(strSplitHost[1])
    else:
        strServerName = strSplitHost[0]
        iServerPort = 80

    strDomain = strProtocolName + "://" + strHost
    strDownURL = strDomain + strSubDownURL
    strPrtDatDownURL = strDomain + strSubPrtDatDownURL
    strSessionCheck = strDomain + strSubSessionCheck
    strInstallCheck = strDomain + strSubInstallCheck
    strIePopupURL = strDomain + strSubIePopupURL
    strSessionURL = strDomain + strSubSessionURL

    now = datetime.datetime.now()
    tototoday = now.strftime("%Y%m%d%H%M%S")

    strPrtProtocol = strProtocolName

    PRINTERUPDATE = base64.standard_b64encode(strPrtDatDownURL)

    if strFunctionGubun == "OM":
        strHIDECD = "1"

