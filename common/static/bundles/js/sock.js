(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([83],{

/***/ "./cms/static/js/sock.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "toggleSock", function() { return toggleSock; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_domReady__ = __webpack_require__("./common/static/js/vendor/domReady.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_domReady___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_domReady__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_jquery__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_jquery_smoothScroll__ = __webpack_require__("./common/static/js/vendor/jquery.smooth-scroll.min.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_jquery_smoothScroll___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_jquery_smoothScroll__);




'use strict';

var toggleSock = function toggleSock(e) {
    e.preventDefault();

    var $btnShowSockLabel = __WEBPACK_IMPORTED_MODULE_1_jquery__(this).find('.copy-show');
    var $btnHideSockLabel = __WEBPACK_IMPORTED_MODULE_1_jquery__(this).find('.copy-hide');
    var $sock = __WEBPACK_IMPORTED_MODULE_1_jquery__('.wrapper-sock');
    var $sockContent = $sock.find('.wrapper-inner');

    if ($sock.hasClass('is-shown')) {
        $sock.removeClass('is-shown');
        $sockContent.hide('fast');
        $btnHideSockLabel.removeClass('is-shown').addClass('is-hidden');
        $btnShowSockLabel.removeClass('is-hidden').addClass('is-shown');
    } else {
        $sock.addClass('is-shown');
        $sockContent.show('fast');
        $btnHideSockLabel.removeClass('is-hidden').addClass('is-shown');
        $btnShowSockLabel.removeClass('is-shown').addClass('is-hidden');
    }

    __WEBPACK_IMPORTED_MODULE_1_jquery__["smoothScroll"]({
        offset: -200,
        easing: 'swing',
        speed: 1000,
        scrollElement: null,
        scrollTarget: $sock
    });
};

__WEBPACK_IMPORTED_MODULE_0_domReady__(function () {
    // toggling footer additional support
    __WEBPACK_IMPORTED_MODULE_1_jquery__('.cta-show-sock').bind('click', toggleSock);
});



/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ })

},["./cms/static/js/sock.js"])));
//# sourceMappingURL=sock.js.map