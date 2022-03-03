var maFunType = "";
var maCallBackFun;
var maResJsonData = new Object();
var maOnlyInstallFlag = false;
var maBrokerCommand = "";
var maStrError;
var maRepeatCheckflag = false;
var maTimeOutCheck_s = 2;
var maBrokerAddOptJson = new Object();
maBrokerAddOptJson.getVersion = new Object();
maBrokerAddOptJson.getVersion.addDot = 0;

function addZero(x, n) {
  while (x.toString().length < n) {
    x = "0" + x;
  }
  return x;
}

function MDBG(valueName, value, caller) {
  var callerFun = arguments.callee.caller;

  if (caller) {
    callerFun = callerFun.caller;
  }

  var pat = /^function\s+([a-zA-Z0-9_]+)\s*\(/i;
  pat.exec(callerFun);
  var func = new Object();
  func.name = RegExp.$1;
  var d = new Date();
  var h = addZero(d.getHours(), 2);
  var m = addZero(d.getMinutes(), 2);
  var s = addZero(d.getSeconds(), 2);
  var ms = addZero(d.getMilliseconds(), 3);
  var currentTime = h + ":" + m + ":" + s;
  var funNameArr = [];
  var maxFunNameLength = 20;
  var blankCount = maxFunNameLength - func.name.length;

  for (var funnamei = 0; funnamei < func.name.length; funnamei++) {
    funNameArr.push(func.name.charAt(funnamei));
  }

  for (var maxFunName = 0; maxFunName < blankCount; maxFunName++) {
    funNameArr.push(" ");
  }

  var callFunName = funNameArr.join("");
  var valueNameArr = [];
  var maxValueNameLength = 25;
  blankCount = maxValueNameLength - valueName.length;

  for (var valuenamei = 0; valuenamei < valueName.length; valuenamei++) {
    valueNameArr.push(valueName.charAt(valuenamei));
  }

  for (var maxValuenamei = 0; maxValuenamei < blankCount; maxValuenamei++) {
    valueNameArr.push(" ");
  }

  var valueName1 = valueNameArr.join("");
  var valueName2 = "## |" + currentTime + "| " + callFunName + "() :: " + valueName1;
  if (window.console == undefined) console = {
    log: function () {}
  };
  console.log(valueName2, value);
}

var MaBase64 = {
  _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
  encode: function (input) {
    var output = "";
    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
    var i = 0;
    input = MaBase64._utf8_encode(input);

    while (i < input.length) {
      chr1 = input.charCodeAt(i++);
      chr2 = input.charCodeAt(i++);
      chr3 = input.charCodeAt(i++);
      enc1 = chr1 >> 2;
      enc2 = (chr1 & 3) << 4 | chr2 >> 4;
      enc3 = (chr2 & 15) << 2 | chr3 >> 6;
      enc4 = chr3 & 63;

      if (isNaN(chr2)) {
        enc3 = enc4 = 64;
      } else if (isNaN(chr3)) {
        enc4 = 64;
      }

      output = output + this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) + this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);
    }

    return output;
  },
  decode: function (input) {
    var output = "";
    var chr1, chr2, chr3;
    var enc1, enc2, enc3, enc4;
    var i = 0;
    input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

    while (i < input.length) {
      enc1 = this._keyStr.indexOf(input.charAt(i++));
      enc2 = this._keyStr.indexOf(input.charAt(i++));
      enc3 = this._keyStr.indexOf(input.charAt(i++));
      enc4 = this._keyStr.indexOf(input.charAt(i++));
      chr1 = enc1 << 2 | enc2 >> 4;
      chr2 = (enc2 & 15) << 4 | enc3 >> 2;
      chr3 = (enc3 & 3) << 6 | enc4;
      output = output + String.fromCharCode(chr1);

      if (enc3 != 64) {
        output = output + String.fromCharCode(chr2);
      }

      if (enc4 != 64) {
        output = output + String.fromCharCode(chr3);
      }
    }

    output = MaBase64._utf8_decode(output);
    return output;
  },
  _utf8_encode: function (string) {
    string = string.replace(/\r\n/g, "\n");
    var utftext = "";

    for (var n = 0; n < string.length; n++) {
      var c = string.charCodeAt(n);

      if (c < 128) {
        utftext += String.fromCharCode(c);
      } else if (c > 127 && c < 2048) {
        utftext += String.fromCharCode(c >> 6 | 192);
        utftext += String.fromCharCode(c & 63 | 128);
      } else {
        utftext += String.fromCharCode(c >> 12 | 224);
        utftext += String.fromCharCode(c >> 6 & 63 | 128);
        utftext += String.fromCharCode(c & 63 | 128);
      }
    }

    return utftext;
  },
  _utf8_decode: function (utftext) {
    var string = "";
    var i = 0;
    var c = c1 = c2 = 0;

    while (i < utftext.length) {
      c = utftext.charCodeAt(i);

      if (c < 128) {
        string += String.fromCharCode(c);
        i++;
      } else if (c > 191 && c < 224) {
        c2 = utftext.charCodeAt(i + 1);
        string += String.fromCharCode((c & 31) << 6 | c2 & 63);
        i += 2;
      } else {
        c2 = utftext.charCodeAt(i + 1);
        c3 = utftext.charCodeAt(i + 2);
        string += String.fromCharCode((c & 15) << 12 | (c2 & 63) << 6 | c3 & 63);
        i += 3;
      }
    }

    return string;
  }
};
ua = navigator.userAgent;
uaOs = ua.match(/(CrOS\ \w+|Windows\ NT|Mac\ OS\ X|Linux)\ ([\d\._]+)?/);
uaBrowser = ua.match(/(opera|chrome|safari|firefox|msie|trident|edge(?=\/))\/?\s*(\d+)/i) || [];

function getOsName() {
  return uaOs[1] || "Unknown";
}

function getOsVersion() {
  return uaOs[2] || "Unknown";
}

function getOsBit() {
  var osBit = "";
  M = ua.match(/\(.*(Windows|Linux).*(WOW64|Win64|i686|x86_64).*?\)/i) || [];

  if (ua.indexOf("Macintosh") > 0) {
    osBit = "64";
  } else if (M[2] != null) {
    if (M[2].indexOf("64") > 0) {
      osBit = "64";
    } else {
      osBit = "32";
    }
  } else {
    osBit = "32";
  }

  return osBit;
}

function getBrowserName() {
  var tem;

  if (/trident/i.test(uaBrowser[1])) {
    tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
    return "MSIE";
  }

  if (uaBrowser[1] === "Chrome") {
    tem = ua.match(/\bOPR\/(\d+)/);

    if (tem != null) {
      return "Opera";
    }

    tem = ua.match(/\bEdge\/(\d+)/);

    if (tem != null) {
      return "Edge";
    }
  }

  return uaBrowser[1];
}

function getBrowserVersion() {
  var tem;

  if (/trident/i.test(uaBrowser[0])) {
    return "11";
  }

  if (uaBrowser[1] === "Chrome") {
    tem = ua.match(/\bOPR\/(\d+)/);

    if (tem != null) {
      return tem[1];
    }

    tem = ua.match(/\bEdge\/(\d+)/);

    if (tem != null) {
      return tem[1];
    }
  }

  return uaBrowser[2];
}

function getBrowserBit() {
  var bsBit = "";
  M = ua.match(/ \(.*(Windows|Linux).*(x64|x86_64).*?\)/) || [];

  if (M[2] != null) {
    if (M[2].indexOf("64") > 0) {
      bsBit = "64";
    }
  } else {
    bsBit = "32";
  }

  return bsBit;
}

userInfo = new Object();
userInfo.osName = getOsName();
userInfo.osVersion = getOsVersion();
userInfo.osBit = getOsBit();
userInfo.bsName = getBrowserName();
userInfo.bsVersion = getBrowserVersion();
userInfo.bsBit = getBrowserBit();
MDBG("userInfo", userInfo);

function maBrokerInit(callbackFun, commandType, repeatCheckflag) {
  maFunType = commandType;
  maCallBackFun = callbackFun;
  maRepeatCheckflag = repeatCheckflag;

  if (commandType == "getVersion") {
    maBrokerCommand = craeteBoekerCommand(chkFileArray);
  } else if (commandType == "executeBinary") {
    maBrokerCommand = craeteBoekerCommand(executeBinaryArray);
  } else if (commandType == "getClientInfo") {
    maBrokerCommand = craeteBoekerCommand(clientInfo);
  } else if (commandType == "getPrintInfo") {
    maTimeOutCheck_s = 60;
    maBrokerCommand = craeteBoekerCommand(printInfo);
  } else if (commandType == "updatePrinterDAT") {
    maBrokerCommand = craeteBoekerCommand(updatePrinterDATArray);
    maTimeOutCheck_s = 60;
  }

  //@CHECK
  if( window.WebSocket ){
    maBroker_wss(maBrokerCommand)
	/*
	if(get_browser() === 'Chrome' || get_browser() === 'Edge'){
		maBroker_wss(maBrokerCommand)
	}
	*/
  }else{
    maBroker(maBrokerCommand);
  }
 
  return;
}

function maBroker_wss(bokerCommand){
  var local_host = "127.0.0.1";
  var current_port = 19877;
  var wssBrokerURL =" wss://"+local_host + ":" + current_port;

  var d = new Date();
  var h = addZero(d.getHours(), 2);
  var m = addZero(d.getMinutes(), 2);
  var s = addZero(d.getSeconds(), 2);
  var ms = addZero(d.getMilliseconds(), 3);
  var currentTime = h + "" + m + "" + s + "" + ms;
  var brokerParam = "[MAEPS]" + MaBase64.encode(bokerCommand) + "[MAEPSEOF]";
  brokerParam = "GET /?brokerCommand=" + brokerParam + "&Type=json&t=" + currentTime + "&callback=maCbBrokerResFun";

  var ws = new WebSocket(wssBrokerURL);
  ws.onopen = function() {
    MDBG("onopen", "called");
    ws.send(brokerParam);
  };
  ws.onmessage = function(event) {
    console.log("onmessage", event);
    eval(event.data);
    ws.close();
  };
  ws.onerror = function(e) {
    maBrokerController(null, null, e);
    reConnectionMaBroker(1);
    // if (maRepeatCheckflag === true) {
    //   setTimeout(function(){
    //     maBroker_wss(maBrokerCommand);
    //   }, 1000);
    // }

  };
  ws.onclose = function() {
    MDBG("onclose", "called");
  };
}


function reConnectionMaBroker(reConnectionTime_s) {
  setTimeout(function () {
    if( window.WebSocket ){
      maBroker_wss(maBrokerCommand)
    }else{
      maBroker(maBrokerCommand);
    }
  }, reConnectionTime_s * 1000);
}

function maBroker(bokerCommand) {
  var brokerServerURI = getBrokerServerURI();
  var d = new Date();
  var h = addZero(d.getHours(), 2);
  var m = addZero(d.getMinutes(), 2);
  var s = addZero(d.getSeconds(), 2);
  var ms = addZero(d.getMilliseconds(), 3);
  var currentTime = h + "" + m + "" + s + "" + ms;
  var brokerParam = "[MAEPS]" + MaBase64.encode(bokerCommand) + "[MAEPSEOF]";
  var brokerServerURL = brokerServerURI + "/?brokerCommand=" + brokerParam + "&Type=json&t=" + currentTime;
  var broker = jQuery.ajax({
    url: brokerServerURL,
    dataType: "jsonp",
    cache: false,
    jsonpCallback: "maCbBrokerResFun",
    timeout: maTimeOutCheck_s * 1000,
    success: function (data, status, err) {},
    error: function (data, status, err) {
      var maErrString = "";
      maBrokerController(null, status, err);

      if (maRepeatCheckflag === true) {
        reConnectionMaBroker(1);
      }
    }
  });
  MDBG("broker", broker);
}

function maCbBrokerResFun(data) {
  MDBG("", "called");
  maBrokerController(data, null, null);
}

function getBrokerServerURI() {
  var maurl;
  if (window.location.protocol === "https:") maurl = "https://127.0.0.1:19876";else maurl = "http://127.0.0.1:19875";
  return maurl;
}

function maSetFileInstallFlag(checkFileRetJson) {
  var fileVersionJsonData = checkFileRetJson["fileVerRet"];
  var versionCheckType = maBrokerAddOptJson.getVersion.addDot;

  for (var chkFile_i = 0; chkFile_i < chkFileArray.length; chkFile_i++) {
    var fileName = fileVersionJsonData[chkFile_i].name;
    var fileVersion = fileVersionJsonData[chkFile_i].version;
    var defineVersion = chkFileArray[chkFile_i][0];

    if (fileVersion == -1000) {
      fileVersionJsonData[chkFile_i].installFlag = false;
    } else if (versionCheckType == 0) {
      if (fileVersion - defineVersion >= 0) {
        fileVersionJsonData[chkFile_i].installFlag = true;
      } else {
        fileVersionJsonData[chkFile_i].installFlag = false;
      }
    } else {
      var fileVersionArr = fileVersion.split(".");
      var defineVersionArr = defineVersion.split(".");
      var checkCount = 1;

      for (var fileVer_i = 0; fileVer_i < fileVersionArr.length; fileVer_i++) {
        var versionDifference = fileVersionArr[fileVer_i] - defineVersionArr[fileVer_i];

        if (versionDifference > 0) {
          fileVersionJsonData[chkFile_i].installFlag = true;
          break;
        } else if (versionDifference == 0) {
          checkCount++;

          if (checkCount == 4) {
            fileVersionJsonData[chkFile_i].installFlag = true;
          }
        } else {
          fileVersionJsonData[chkFile_i].installFlag = false;
          break;
        }
      }
    }

    MDBG(chkFile_i + "_" + fileName, "defineVersion = " + defineVersion + " || installVersion = " + fileVersion + " || installFlag = " + fileVersionJsonData[chkFile_i].installFlag);
  }

  return fileVersionJsonData;
}

function craeteBoekerCommand(brokerParam) {
  var brokerReqJsonData = new Object();
  brokerReqJsonData.funType = maFunType;

  if (maFunType == "getVersion") {
    brokerReqJsonData.chkFileInfo = new Array();

    for (var obj_i = 0; obj_i < brokerParam.length; obj_i++) {
      var checkFile = new Object();
      checkFile.csidl = brokerParam[obj_i][1];
      checkFile.name = brokerParam[obj_i][2];
      checkFile.addPath = brokerParam[obj_i][3];
      brokerReqJsonData.chkFileInfo[obj_i] = checkFile;
    }
  } else if (maFunType == "executeBinary") {
    brokerReqJsonData.executeBinaryInfo = new Array();

    for (var obj_i = 0; obj_i < brokerParam.length; obj_i++) {
      var executeBinary = new Object();
      executeBinary.parameter = brokerParam[obj_i][0];
      executeBinary.csidl = brokerParam[obj_i][1];
      executeBinary.name = brokerParam[obj_i][2];
      executeBinary.addPath = brokerParam[obj_i][3];
      brokerReqJsonData.executeBinaryInfo[obj_i] = executeBinary;
    }
  } else if (maFunType == "getClientInfo") {
    brokerReqJsonData.clientInfo = new Object();
    brokerReqJsonData.clientInfo = brokerParam;
  } else if (maFunType == "getPrintInfo") {
    brokerReqJsonData.printInfo = new Array();

    for (var obj_i = 0; obj_i < brokerParam.length; obj_i++) {
      var getPrintInfo = new Object();
      getPrintInfo.parameter = brokerParam[0];
      getPrintInfo.csidl = brokerParam[1];
      getPrintInfo.name = brokerParam[2];
      getPrintInfo.addPath = brokerParam[3];
      getPrintInfo.supportRange = brokerParam[4];
    }

    brokerReqJsonData.printInfo = getPrintInfo;
  } else if (maFunType == "updatePrinterDAT") {
    brokerReqJsonData.printerDATurl = brokerParam[0];
    brokerReqJsonData.printerDATversion = brokerParam[1];
    brokerReqJsonData.printerDATcookie = brokerParam[2];
    brokerReqJsonData.printerDAThash = brokerParam[3];
    brokerReqJsonData.csidl = brokerParam[4];
    brokerReqJsonData.addPath = brokerParam[5];
  }

  brokerReqJsonData.addOpt = maBrokerAddOptJson[maFunType] != undefined ? maBrokerAddOptJson[maFunType] : "";
  return JSON.stringify(brokerReqJsonData);
}

function maBrokerController(data, status, err) {
  MDBG("", "start");
  MDBG("status", status);
  MDBG("data", data);
  MDBG("err", err);

  if (typeof data == "number") {
    return maCallBackFun(maSetBrokerErr(data));
  } else if (!data) {
    return maCallBackFun(maSetBrokerErr(-9000));
  }

  if (maFunType == "getVersion") {
    maResJsonData = maSetFileInstallFlag(data);
    maGetOnlyInstallFlag();

    if (maOnlyInstallFlag === false && maRepeatCheckflag === true) {
      reConnectionMaBroker(1);
    }
  } else {
    maResJsonData = data;
  }

  MDBG("", "end");
  return maCallBackFun(maResJsonData);
}

function maSetBrokerErr(err) {
  switch (err) {
    case -2001:
      maStrError = "요청 데이터가 없습니다.";
      break;

    case -2002:
      maStrError = "시그니처를 찾을 수 없습니다.";
      break;

    case -2003:
      maStrError = "명령어 형태가 올바르지 않습니다.";
      break;

    case -9000:
      maStrError = "MaEPSBroker.exe 모듈의 설치 혹은 업데이트가 필요합니다.";
      makeNotInstallBrokerJson();
      break;

    case 0:
      maStrError = "버전 체크 중 오류가 발생 하였습니다.";
      makeNotInstallBrokerJson();
      break;

    case 99999:
      maStrError = "요청 데이터가 올바르지 않습니다.";
      break;

    default:
      if (err - 30000 < 0) {
        maStrError = "MaEPSBroker.exe 모듈의 설치 혹은 업데이트가 필요합니다.";
      } else {
        maStrError = "버전 체크 중 오류가 발생 하였습니다.";
      }

      break;
  }

  return maStrError;
}

function maGetOnlyInstallFlag() {
  for (var chkFile_i = 0; chkFile_i < maResJsonData.length; chkFile_i++) {
    var chkFileInstallFlag = maResJsonData[chkFile_i].installFlag;

    if (chkFileInstallFlag == false) {
      maOnlyInstallFlag = false;
      break;
    } else {
      maOnlyInstallFlag = true;
    }
  }

  MDBG("maOnlyInstallFlag", maOnlyInstallFlag);
}

function makeNotInstallBrokerJson() {
  maResJsonData = new Array();
  var brokerObj = new Object();
  brokerObj.name = "MaEPSBroker.exe";
  brokerObj.version = "-1000";
  brokerObj.installFlag = false;
  maResJsonData[0] = brokerObj;
}