'''
Created on 2018. 1. 2.

@author: donghwa
'''
import Cookie
import socket
import struct

import os

ISUCCESS = "00000"
IFAILED = "10000"

E_PARAMETER = "90001"
E_CONNECT_SOCKET = "10001"
E_WRITE_SOCKET = "10015"
E_READ_SOCKET = "10016"
E_SOCKET = "10014"
E_PACKET = "10017"

E_ORG_FILE_OPEN = "10021"
E_ORG_FILE_READ = "10022"
E_RESULT_FILE_WRITE = "10023"

E_PACKET_HEADER = "10030";
E_PACKET_HEADER_TRIM = "10031";
E_SAVE_BMP = "90005";

PACKET_SIZE = 4096
MAX_FILE_READ_SIZE = 4096


def strMaPrestreamWmByteInFile(strServerIp, iServerPort, strHtmlFilePath, iCellBlockCount, iCellBlockRow):
    strMetaData = ""
    strTmpRecvSocketData = ""
    strRecvSocketHeader = ""
    iRecvSocketHeaderSize = 0

    # socket
    sock = None
    server_address = (strServerIp, iServerPort)
    iStartRecvData = 0

    # file io
    fOrgHtmlFile = None

    # packet signature
    PrestreamHtml_GetHtmlReq_Sig = 0x310
    PrestreamHtml_GetHtmlRep_Sig = 0x3400

    # fixed data
    strFunctionFlag = "MA"  # Fix data
    strScope = "2"  # 1 : binary, 2 : BASE64, 3 : compress binary, 4 : e-mail
    strWidthHeight = "1"  # 1 : portrait, 2 : landscape
    strFolder = str(iCellBlockCount) + "^" + str(iCellBlockRow) + "^"
    strPrintCount = "5"  # Printable count
    strMethod = "0"
    strWmFlag = "0"

    if os.path.isfile(strHtmlFilePath):
        iHtmlFileSize = os.path.getsize(strHtmlFilePath)
        strHtmlFileSize = str(iHtmlFileSize).rjust(10, '0')
    else:
        return (E_ORG_FILE_OPEN, "0")

    # int(string)
    packer = struct.Struct('>L4scc2s128s16sc3939x')  # total = 4096
    values = (PrestreamHtml_GetHtmlReq_Sig, \
              strFunctionFlag, \
              strScope, \
              strWidthHeight, \
              strPrintCount, \
              strFolder, \
              strHtmlFileSize, \
              strWmFlag)

    packed_data = packer.pack(*values)

    # for debug
    # with open('C://MarkAny/packet.dat', 'wb') as f:
    #    f.write(packed_data)
    # f.close()

    # socket initialize
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        sock = None
        return (E_SOCKET, "0")

    # socket connect
    try:
        sock.connect(server_address)
    except socket.error as msg:
        sock.close()
        sock = None
        return (E_CONNECT_SOCKET, "0")

    # socket send header
    try:
        sock.sendall(packed_data)
    except socket.error as msg:
        sock.close()
        sock = None
        return (E_WRITE_SOCKET, "0")

    # socket send data
    try:
        fOrgHtmlFile = open(strHtmlFilePath, 'rb')
    except:
        return (E_ORG_FILE_OPEN, "0")

    try:
        strFileReadData = fOrgHtmlFile.read(MAX_FILE_READ_SIZE)
        while (strFileReadData):
            try:
                sock.send(strFileReadData)
            except socket.error as msg:
                sock.close
                sock = None
                fOrgHtmlFile.close()
                return E_WRITE_SOCKET

            try:
                strFileReadData = fOrgHtmlFile.read(MAX_FILE_READ_SIZE)
            except IOError as err:
                fOrgHtmlFile.close()
                return (E_ORG_FILE_READ, "0")
    except IOError as err:
        fOrgHtmlFile.close()
        return (E_ORG_FILE_READ, "0")

    fOrgHtmlFile.close()

    while True:
        try:
            strSockRecvData = sock.recv(PACKET_SIZE)
            # print "strSockRecvDataSize = ", len(strSockRecvData)

            if iRecvSocketHeaderSize != -1:
                iRecvSocketHeaderSize += len(strSockRecvData)
                strTmpRecvSocketData += strSockRecvData

        except socket.error as msg:
            sock.close()
            sock = None
            return (E_READ_SOCKET, "0")

        if iRecvSocketHeaderSize >= PACKET_SIZE:
            if iRecvSocketHeaderSize > PACKET_SIZE:
                strRecvSocketHeader = strTmpRecvSocketData[:PACKET_SIZE]
                strSockRecvData = strTmpRecvSocketData[PACKET_SIZE:]
                strMetaData += strSockRecvData
            else:
                strRecvSocketHeader = strTmpRecvSocketData

            unpacker = struct.Struct('>L5s10s4077x')
            unpacked_data = unpacker.unpack(str(strRecvSocketHeader))

            if unpacked_data[0] != PrestreamHtml_GetHtmlRep_Sig:
                sock.close()
                sock = None
                return (E_PACKET_HEADER, "0")

            iRecvSocketHeaderSize = -1
            # print unpacked_data[0]
            # print unpacked_data[1]
            # print unpacked_data[2]
        elif iRecvSocketHeaderSize == -1:
            strMetaData += strSockRecvData

        if not strSockRecvData:
            break;

    sock.close()

    # print iHtmlFileSize
    # print strFolder
    # print strHtmlFileSize

    return (ISUCCESS, strMetaData)


def strMaPrestreamWmByte(strServerIp, iServerPort, strHtmlData, iHtmlDataSize, iCellBlockCount, iCellBlockRow):
    strMetaData = ""
    strTmpRecvSocketData = ""
    strRecvSocketHeader = ""
    iRecvSocketHeaderSize = 0

    # socket
    sock = None
    server_address = (strServerIp, iServerPort)
    iStartRecvData = 0

    # packet signature
    PrestreamHtml_GetHtmlReq_Sig = 0x310
    PrestreamHtml_GetHtmlRep_Sig = 0x3400

    # fixed data
    strFunctionFlag = "MA"  # Fix data
    strScope = "2"  # 1 : binary, 2 : BASE64, 3 : compress binary, 4 : e-mail
    strWidthHeight = "1"  # 1 : portrait, 2 : landscape
    strFolder = str(iCellBlockCount) + "^" + str(iCellBlockRow) + "^"
    strPrintCount = "5"  # Printable count
    strMethod = "0"
    strWmFlag = "0"

    strHtmlFileSize = str(iHtmlDataSize).rjust(10, '0')

    # int(string)
    packer = struct.Struct('>L4scc2s128s16sc3939x')  # total = 4096
    values = (PrestreamHtml_GetHtmlReq_Sig, \
              strFunctionFlag, \
              strScope, \
              strWidthHeight, \
              strPrintCount, \
              strFolder, \
              strHtmlFileSize, \
              strWmFlag)

    packed_data = packer.pack(*values)

    # socket initialize
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        sock = None
        return (E_SOCKET, "0")

    # socket connect
    try:
        sock.connect(server_address)
    except socket.error as msg:
        sock.close()
        sock = None
        return (E_CONNECT_SOCKET, "0")

    # socket send header
    try:
        sock.sendall(packed_data)
    except socket.error as msg:
        sock.close()
        sock = None
        return (E_WRITE_SOCKET, "0")

    # socket send data
    try:
        sock.sendall(strHtmlData)
    except socket.error as msg:
        sock.close
        sock = None
        return E_WRITE_SOCKET

    while True:
        # print "receive data...."
        try:
            strSockRecvData = sock.recv(PACKET_SIZE)
            # print "strSockRecvDataSize = ", len(strSockRecvData)

            if iRecvSocketHeaderSize != -1:
                iRecvSocketHeaderSize += len(strSockRecvData)
                strTmpRecvSocketData += strSockRecvData

        except socket.error as msg:
            sock.close()
            sock = None
            return (E_READ_SOCKET, "0")

        if iRecvSocketHeaderSize >= PACKET_SIZE:
            if iRecvSocketHeaderSize > PACKET_SIZE:
                strRecvSocketHeader = strTmpRecvSocketData[:PACKET_SIZE]
                strSockRecvData = strTmpRecvSocketData[PACKET_SIZE:]
                strMetaData += strSockRecvData
            else:
                strRecvSocketHeader = strTmpRecvSocketData

            unpacker = struct.Struct('>L5s10s4077x')
            unpacked_data = unpacker.unpack(str(strRecvSocketHeader))

            if unpacked_data[0] != PrestreamHtml_GetHtmlRep_Sig:
                sock.close()
                sock = None
                return (E_PACKET_HEADER, "0")

            iRecvSocketHeaderSize = -1
            # print unpacked_data[0]
            # print unpacked_data[1]
            # print unpacked_data[2]
        elif iRecvSocketHeaderSize == -1:
            strMetaData += strSockRecvData

        if not strSockRecvData:
            break;

    sock.close()

    # print iHtmlFileSize
    # print strFolder
    # print strHtmlFileSize

    return (ISUCCESS, strMetaData)


def ma_getBrowserInfo(strUserAgent):
    otherBrowsers = ["Firefox", "Opera", "OPR", "Chrome", "Safari"]
    ioscheck = 0
    browsername = ""
    browserversion = ""

    # browserInfoArr[] = new String[2];
    # iIndex = strUserAgent.find("Macintosh")
    if strUserAgent.find("Windows") > 0:
        ioscheck = 1
    elif strUserAgent.find("Macintosh") or strUserAgent.find("Linux"):
        ioscheck = 2
    else:
        ioscheck = 3

    if (strUserAgent.find("MSIE") < 0) and (strUserAgent.find("Trident") < 0):
        for otherBrowser in otherBrowsers:
            if strUserAgent.find(otherBrowser) >= 0:
                browsername = otherBrowser
                break

        subString = strUserAgent[strUserAgent.find(browsername):]
        browserinfo1 = subString.split()
        browserinfo = browserinfo1[0].split("/")

        browsername = browserinfo[0]
        browserversion = browserinfo[1]

        if browsername.find("OPR") >= 0:
            browsername = "Opera"
    else:
        if strUserAgent.find("MSIE") >= 0:
            tempStr = strUserAgent[strUserAgent.find("MSIE"):]
            browserversion = tempStr[4, tempStr.find(";")]
        elif strUserAgent.find("Trident") >= 0:
            tempStr = strUserAgent[strUserAgent.find("Trident"):]
            tempStr = tempStr[7:tempStr.find(";")]
            if tempStr.find("7") >= 0:
                browserversion = "11"
            else:
                browserversion = "0"

        browsername = "IE"

    return (ioscheck, browsername, browserversion)


def ma_parse_cookie(cookie):
    ma_cookie_data = ''

    if cookie == '':
        return {}
    if not isinstance(cookie, Cookie.BaseCookie):
        try:
            c = Cookie.SimpleCookie()
            c.load(cookie)
        except Cookie.CookieError:
            return {}
    else:
        c = cookie
    cookiedict = {}
    for key in c.keys():
        if key != "sessionid":
            if key == "edx-user-info":
                ma_value = c.get(key).value.replace(',', '\\054');
                ma_value = ma_value.replace('"', '\\"');
                ma_value = '"' + ma_value + '"'
                ma_cookie_data = ma_cookie_data + key + "=" + ma_value + "; "
            else:
                ma_cookie_data = ma_cookie_data + key + "=" + c.get(key).value + ";"
                # ma_cookie_data = ma_cookie_data + key + "=" + c.get(key).value + ";"
    return ma_cookie_data
    # expected_html = render_to_string('home.html', request=request)


def strSafetyFileNameCheck(filePath):
    filePath = filePath.replace("/", "")
    filePath = filePath.replace("\\\\", "");
    filePath = filePath.replace("\\..", "");
    filePath = filePath.replace("&", "");

    # XSS Script
    filePath = filePath.replace("<", "& lt;").replace(">", "& gt;");
    filePath = filePath.replace("\\(", "& #40;").replace("\\)", "& #41;");
    filePath = filePath.replace("'", "& #39;");
    filePath = filePath.replace("eval\\((.*)\\)", "");
    filePath = filePath.replace("[\\\"\\\'][\\s]*javascript:(.*)[\\\"\\\']", "\"\"");
    filePath = filePath.replace("script", "");
    filePath = filePath.replace("\r", "");
    filePath = filePath.replace("\n", "");

    return filePath


'''
strHtmlFilePath = 'E://Workspace_oxygen//PythonTestPrj//sample.html'
(strRetCode, strRetData) = strMaPrestreamWmByte(strHtmlFilePath, 16, 1)

if strRetCode == ISUCCESS:
    strRetData = strRetData.replace("\n", "\\n")
    fResult = open("C://MarkAny//recv.dat", 'wb')
    fResult.write(strRetData)
    fResult.close()

print strRetCode
'''

# strUserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko"
# strUserAgent = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
'''
strUserAgent = "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"

browserinfo = ma_getBrowserInfo(strUserAgent)

print browserinfo[0]
print browserinfo[1]
print browserinfo[2]

text = "/bbb/aaa/test"
encoded_text = base64.encodestring(text)
print encoded_text

decoded_text = base64.decodestring(encoded_text)
print decoded_text
'''