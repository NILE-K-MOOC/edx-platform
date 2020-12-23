// ------------------------------------------------------------------
var appName = "maepagesafer";
var arrPort = new Array(15396, 25396, 35396); // 포트 정보
var MarkanySignature = "MARKANYEPS";
var sessionKey = "JSESSIONID";
var src_url = "./jsp/Sample.jsp";

// ------------------------------------------------------------------

function addZero(x, n) {
    while (x.toString().length < n) {
        x = "0" + x;
    }
    return x;
}

var match = navigator.userAgent.match(/(CrOS\ \w+|Windows\ NT|Mac\ OS\ X|Linux)\ ([\d\._]+)?/);
var os = (match || [])[1] || "Unknown";
var osVersion = (match || [])[2] || "Unknown";

var MyTimer2;

function sleep(delay) {
    var start = new Date().getTime();
    while (new Date().getTime() < start + delay) ;
}

function getInstallPage() {
    return vstrSudongInstallURL;
}


function get_browser() {
    var ua = navigator.userAgent, tem,
        M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if (/trident/i.test(M[1])) {
        tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
        return 'MSIE';
    }
    if (M[1] === 'Chrome') {
        tem = ua.match(/\bOPR\/(\d+)/)
        if (tem != null) {
            return 'Opera';
        }
    }
    M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
    if ((tem = ua.match(/version\/(\d+)/i)) != null) {
        M.splice(1, 1, tem[1]);
    }
    return M[0];
}

function get_browser_version() {
    var ua = navigator.userAgent, tem,
        M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];

    if (/trident/i.test(M[1])) {
        tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
        return tem[1];
    }
    if (M[1] === 'Chrome') {
        tem = ua.match(/\bOPR\/(\d+)/)
        if (tem != null) {
            return tem[1];
        }
    }
    M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
    if ((tem = ua.match(/version\/(\d+)/i)) != null) {
        M.splice(1, 1, tem[1]);
    }
    return M[1];
}


function setWebStorage(cName, cValue) {
    window.localStorage[cName] = cValue;
}

function getWebStorage(cName) {
    return (window.localStorage[cName]);
}

function delWebStorage(cName) {
    window.localStorage[cName] = '';
}

function setCookie(cName, cValue, cDay) {
    var expire = new Date();
    expire.setDate(expire.getDate() + cDay);
    cookies = cName + '=' + escape(cValue) + '; path=/ ';
    if (typeof cDay != 'undefined')
        cookies += ';expires=' + expire.toGMTString() + ';';
    document.cookie = cookies;
}

function getCookie(cName) {
    cName = cName + '=';
    var cookieData = document.cookie;
    var start = cookieData.indexOf(cName);
    var cValue = '';
    if (start != -1) {
        start += cName.length;
        var end = cookieData.indexOf(';', start);
        if (end == -1) end = cookieData.length;
        cValue = cookieData.substring(start, end);
    }
    return unescape(cValue);
}


function IsMarkanySafeBrowsing() {
    if (navigator.userAgent.indexOf("MarkAnySafeBrowser") >= 0) {
        return true;
    }
    return false;
}


function AutoRefresh(str) {
    var MyTimer = setInterval(function () {
        var cookie = getCookie(str)
        if (cookie >= iVersion) {
            window.location = 'http://www.markany.com/';
        }
    }, 1000);
}

var StopMyTimer = function () {
    clearInterval(MyTimer);
}

var iCnt = 0;
var iCnt2 = 0;
var iCheckCnt = 0;
var iMaxCnt = 1000;
var iInstCheckCnt = 0;

function checkProduct(str) {
    if (str.length < MarkanySignature.length)
        return false;

    if (str.substring(0, MarkanySignature.length) === MarkanySignature)
        return true;
    else
        return false;
}

function checkVersion(str) {
    var arrValue = str.split(';');
    if (arrValue.length >= 1) {
        return parseInt(arrValue[1]) - iVersion;
    }
    return -1;
}

function checkVersionCookie(str) {
    var arrValue = str.split('#');
    if (arrValue.length >= 1) {
        return parseInt(arrValue[1]) - iVersion;
    }
    return -1;
}

function checkVersionSession(str) {
    var version = str.substring(MarkanySignature.length, MarkanySignature.length + 5);
    if (version.length >= 1) {
        return parseInt(version) - iVersion;
    }
    return -1;
}

function isWow64() {
    if (navigator.userAgent.indexOf("WOW64") != -1 || navigator.userAgent.indexOf("Win64") != -1) {
        return true;
    } else {
        return false;
    }
}

function messageDataSend() {
    document.body.innerHTML = '';
    document.write('<html xmlns="http://www.w3.org/1999/xhtml">');
    document.write('<head>');
    document.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />');
    document.write('<title>E-Certification</title></head>');
    document.write('<body>');
    document.write('</body></html>');
    document.oncontextmenu = document.body.oncontextmenu = function () {
        return false;
    }
    //window close
    if (os == 'Windows NT' && get_browser() === 'Firefox') {
        var win = window.open('about:blank', '_self');
        win.close();
    } else if (get_browser() === 'Chrome') {
        window.open('', '_self');
        window.close();
    } else {
        window.open('about:blank', '_self').close();
    }
}

var _KeyStr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';

function base64_encode(input) {
    var output = '', chr1, chr2, chr3, enc1, enc2, enc3, enc4, i = 0;

    function _keyStrCharAt() {
        var ar = arguments, i, ov = '';
        for (i = 0; i < ar.length; i++) ov += _KeyStr.charAt(ar[i]);
        return ov;
    }

    function _utf8_encode(string) {
        string = string.replace(/\r\n/g, '\n');
        var utftext = '', c;
        for (var n = 0; n < string.length; n++) {
            var c = string.charCodeAt(n);
            if (c < 128)
                utftext += String.fromCharCode(c);
            else if ((c > 127) && (c < 2048))
                utftext += String.fromCharCode((c >> 6) | 192, (c & 63) | 128);
            else
                utftext += String.fromCharCode((c >> 12) | 224, ((c >> 6) & 63) | 128, (c & 63) | 128);
        }
        return utftext;
    }

    input = _utf8_encode(input);
    while (i < input.length) {
        chr1 = input.charCodeAt(i++);
        chr2 = input.charCodeAt(i++);
        chr3 = input.charCodeAt(i++);
        enc1 = chr1 >> 2;
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
        enc4 = chr3 & 63;
        if (isNaN(chr2)) enc3 = enc4 = 64;
        else if (isNaN(chr3)) enc4 = 64;
        output += _keyStrCharAt(enc1, enc2, enc3, enc4);
    }
    return output;
}

function leadingZeros(n, digits) {
    var zero = '';
    n = n.toString();

    if (n.length < digits) {
        for (i = 0; i < digits - n.length; i++)
            zero += '0';
    }
    return zero + n;
}


function getAdams() {
    var d = new Date();
    var s =
        leadingZeros(d.getFullYear(), 4) +
        leadingZeros(d.getMonth() + 1, 2) +
        leadingZeros(d.getDate(), 2) +
        leadingZeros(d.getHours(), 2) +
        leadingZeros(d.getMinutes(), 2) +
        leadingZeros(d.getSeconds(), 2);
    return s;
}


function makeQuickURL() {
    return vstrSDownURL + "@" + vstrSCookie + "@" + base64_encode(getAdams()) + "@" + vstrSSessionURL;

}

function makeMetaURL() {

    var metaUrl = ""; //base64_encode(vstrDownURL) + "@" + base64_encode(vSession) + "@" + base64_encode(getAdams());
    metaUrl = vstrSDownURL + "@" + vstrSCookie + "@" + base64_encode(getAdams());
    return metaUrl;
}

function makeInstallURL() {
    var installUrl = ""; // = base64_encode(vstrSessionURL) + "@" + base64_encode(vSession) + "@" + base64_encode(getAdams());
    installUrl = vstrSSessionURL + "@" + vstrSCookie + "@" + base64_encode(getAdams());
    return installUrl;
}

function isInstall(appGUID) {
    if (os == 'Windows NT' && get_browser() === 'MSIE') {
        MyTimer2 = setInterval(function () {
            var cookie = getCookie(MarkanySignature);
            validProduct = checkProduct(cookie);
            validVer = checkVersionCookie(cookie) >= 0 ? true : false;

            if (validProduct == true && validVer == true) {
                if (MarkanySignature === "MARKANYEPS") {
                    clearInterval(MyTimer2);
                    document.location = src_url;
                } else if (MarkanySignature === "MARKANYWEBDRM") {
                }
            }
        }, 1000);
    }
    return true;
}

var checkcustomurl = false;
var newWindow;

function checksessionurl() {
    if (newWindow == null) {
        alert('팝업 항상 허용을 선택해 주십시오.');
    } else {
        newWindow.close();
        document.location = vstrSessionCheck;
    }
}

function checksessionurl2() {
    document.location = vstrSessionCheck;
}

function LaunchAppImplement(src) {
    var strBrowser = get_browser();
    if (os === 'Linux' && strBrowser === 'Opera') {
        window.location = src;
    } else {
        try {
            var ifrm = document.createElement("iframe");
            ifrm.src = src;
            ifrm.style.display = "none";
            document.body.appendChild(ifrm);
        } catch (err) {
            console.log(err)
        }
    }
}

var sendmetadata = false;

function stopCheck() {
    if (!sendmetadata)
        document.location = getInstallPage();
}


function LaunchApp(appGUID, param) {
    // --------------------------------------------------------------
    // WebSocket 가능 여부 체크
    // --------------------------------------------------------------	
    if (os === 'Windows NT' && get_browser() === 'Chrome' && get_browser_version() < 19) {
        alert('Chrome 19 이상 버전에서 지원 가능합니다.');
        var win = parent.window.open('', 'popWinC', '');
        win.close();
        return false;
    }
    if (os === 'Windows NT' && get_browser() === 'Firefox' && get_browser_version() < 18) {
        alert('Firefox 18 이상 버전에서 지원 가능합니다.');
        var win = parent.window.open('', 'popWinC', '');
        win.close();
        return false;
    }
    if (os === 'Windows NT' && get_browser() === 'Safari') {
        alert('Safari8 이상 버전에서 지원 가능합니다.');
        var win = parent.window.open('', 'popWinC', '');
        win.close();
        return false;
    }
    if (os === 'Windows NT' && get_browser() === 'Opera' && get_browser_version() < 15) {
        alert('Opera 15 이상 버전에서 지원 가능합니다.');
        var win = parent.window.open('', 'popWinC', '');
        win.close();
        return false;
    }

    var validVer = false;
    var validProduct = false;

    if (MarkanySignature === "MARKANYEPS") {
        validProduct = checkProduct(vpversion);
        validVer = checkVersionSession(vpversion) >= 0 ? true : false;

        if (validProduct == true && validVer == true) {
            var makeurl = makeMetaURL();
            LaunchAppImplement(appGUID + "://?urlmeta" + makeurl);
            setTimeout(function () {
                messageDataSend()
            }, 5000);
        } else
            document.location = getInstallPage();
    }

    return true;
}

function openIEPopup(src, popurl) {
    var myForm = document.createElement('FORM');
    var my_tb = document.createElement('INPUT');
    my_tb.type = 'HIDDEN';
    my_tb.name = 'sessionurl';
    my_tb.value = src;
    myForm.appendChild(my_tb);
    myForm.action = popurl;
    myForm.method = "post";
    myForm.target = "newWindow";
    //myForm.sessionurl = src;
    //setCookie("sessionurl", src, 999);
    var v_Bars = 'directories=no, location=no, menubar=no, status=no,titlebar=no,toolbar=no';
    var v_Options = 'scrollbars=yes,resizable=no,Height=10,Width=10,left=' + window.screenLeft + ',top=' + window.screenTop + ',visible=false,alwaysLowered=yes';
    newWindow = window.open("", "newWindow", v_Bars + ',' + v_Options);
    document.body.appendChild(myForm);
    myForm.submit();
}

function LaunchAppImplementRegist(src, popurl) {
    var strBrowser = get_browser();

    if (strBrowser === 'MSIE')// && get_browser_version() < 9)
    {
        if (get_browser_version() > 10) {
            setWebStorage("sessionurl", src);
            var v_Bars = 'directories=no, location=no, menubar=no, status=no,titlebar=no,toolbar=no';
            var v_Options = 'scrollbars=yes,resizable=no,Height=10,Width=10,left=' + window.screenLeft + ',top=' + window.screenTop + ',visible=false,alwaysLowered=yes';
            newWindow = window.open(popurl, "newWindow", v_Bars + ',' + v_Options);
        } else {
            openIEPopup(src, popurl);
        }
        setTimeout(function () {
            checksessionurl()
        }, 2000);
    } else if (os === 'Linux' && strBrowser === 'Opera') {
        window.location = src;
    } else {
        try {
            var ifrm = document.createElement("iframe");
            ifrm.src = src;
            ifrm.style.display = "none";
            document.body.appendChild(ifrm);
            if (strBrowser === 'Edge' || strBrowser === 'Chrome') {
                //if(strBrowser === 'Edge'){
                //alert("test");
                setTimeout(function () {
                    checksessionurl2();
                }, 2000);
            }
        } catch (err) {
            console.log(err)
        }
        if (os === 'Windows NT' && strBrowser === 'Firefox')
            setTimeout(function () {
                checksessionurl2()
            }, 2000);
    }
}

function LaunchAppImplementRegistCheck(src, popurl) {
    var strBrowser = get_browser();
    if (strBrowser === 'MSIE')// && get_browser_version() < 9)
    {
        if (get_browser_version() > 10) {
            setWebStorage("sessionurl", src);
            var v_Bars = 'directories=no, location=no, menubar=no, status=no,titlebar=no,toolbar=no';
            var v_Options = 'scrollbars=yes,resizable=no,Height=10,Width=10,left=' + window.screenLeft + ',top=' + window.screenTop + ',visible=false,alwaysLowered=yes';
            newWindow = window.open(popurl, "newWindow", v_Bars + ',' + v_Options);
        } else {
            openIEPopup(src, popurl);
        }
        setTimeout(function () {
            checksessionurl()
        }, 2000);
    } else if (os === 'Linux' && strBrowser === 'Opera') {
        window.location = src;
    } else {
        try {
            var ifrm = document.createElement("iframe");
            ifrm.src = src;
            ifrm.style.display = "none";
            document.body.appendChild(ifrm);

        } catch (err) {
            console.log(err)
        }
        if (strBrowser === 'Firefox')
            setTimeout(function () {
                checksessionurl2()
            }, 2000);
    }
}


function LaunchRegistApp(appGUID, param, popurl) {
    var makeurl = makeInstallURL();
    if (param === "sockmeta") {
        LaunchApp(vstrApp, "sockmeta");
    } else if (param === "installcheck") {
        LaunchAppImplementRegistCheck(appGUID + "://?registapp" + makeurl, popurl);
    } else if (param === "quickurl") {
        makeurl = makeQuickURL();
        LaunchAppImplementRegist(appGUID + "://?quickurl" + makeurl, popurl);
    } else if (param === "registapp") {
        LaunchAppImplementRegist(appGUID + "://?registapp" + makeurl, popurl);
    }
}

// ksk
function GetParamData(appGUID) {

    var makeurl = makeMetaURL();
    return appGUID + "://?urlmeta" + makeurl;

}


//broker Start
var installCheckFunHandle;

showPopup = function () {
    var popUp = $("#popLayer");
    popUp.show();
    popUp.css("position", "absolute");
    popUp.css("top", "88px");
    popUp.css("left", "54px");
    $("body").css("background-color", "#565656");
    installCheckFunHandle = setInterval("maBrokerInit(maFun_InstallCheck, 'getVersion')", 1000);
}

function maFun_InstallCheck() {
    $("#progressbar img").css("display", "none");
    //설치체크가 완료되면 clearInterval()호출 후 뷰어호출 브로커 콜
    if (maOnlyInstallFlag == true) {
        clearInterval(installCheckFunHandle);
        //$("#ment").html("설치체크가 완료되었습니다.<br>안전한 증명서 확인 및 출력이 가능한 미리보기 화면이 실행됩니다.");

        maBrokerInit(maFun_execute, 'executeBinary')
    } else {
        $("#btn_maInstall").removeAttr("disabled");
        $("#ment").html("위변조 방지 솔루션의 설치 혹은 업데이트가 필요합니다.<br>아래의 다운로드 버튼을 눌러 다운로드 후 설치를 진행하세요.");
    }
}

function maFun_execute() {
    if (typeof (maResJsonData) != 'string') {
        var executeBinaryObj = maResJsonData["executeBinaryRet"];
        for (var execute_i = 0; execute_i < executeBinaryObj.length; execute_i++) {
            var fileName = executeBinaryObj[execute_i].name;
            var executeFalg = executeBinaryObj[execute_i].executeFlag;
            //실행 성공했으면 !
            if (executeFalg == "true") {
                $("#ment").html("설치체크가 완료되었습니다.<br>증명서 미리보기 화면과 출력이 가능한 뷰어가 실행되며 잠시 후 팝업창이 자동으로 종료됩니다.");
                setTimeout(function () {
                    closePopLayer();
                    closeWindow();
                }, 3000);
            } else {
                $("#ment").html("뷰어 실행에 실패하였습니다.<br>관리자에게 문의해주시기 바랍니다.");
            }
        }
    }
}

function closePopLayer() {
    $("#popLayer").css("display", "none")
    $("body").css("background-color", "#FFF");

    $("#ment").html("증명서의 안전한 출력을 위해 보안 프로그램의 설치체크 여부를 확인 중입니다.");
    $("#btn_maInstall").attr("disabled");
}

function closeWindow() {
    try {
        window.close();
    } catch (e) {
        var win = parent.window.open('', 'popWinC', '');
        win.close();
    }
}

//broker End


