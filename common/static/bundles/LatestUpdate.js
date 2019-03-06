(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([76],{

/***/ "./openedx/features/course_experience/static/course_experience/js/LatestUpdate.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "LatestUpdate", function() { return LatestUpdate; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery_cookie__ = __webpack_require__("./common/static/js/vendor/jquery.cookie.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery_cookie___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_jquery_cookie__);
function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/* globals $ */


var LatestUpdate = // eslint-disable-line import/prefer-default-export

function LatestUpdate(options) {
  _classCallCheck(this, LatestUpdate);

  if ($.cookie('update-message') === 'hide') {
    $(options.messageContainer).hide();
  }
  $(options.dismissButton).click(function () {
    $.cookie('update-message', 'hide', { expires: 1 });
    $(options.messageContainer).hide();
  });
};
/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ })

},["./openedx/features/course_experience/static/course_experience/js/LatestUpdate.js"])));
//# sourceMappingURL=LatestUpdate.js.map