(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([23,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74],{

/***/ "./cms/static/js/factories/login.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (immutable) */ __webpack_exports__["default"] = LoginFactory;
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "LoginFactory", function() { return LoginFactory; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery_cookie__ = __webpack_require__("./common/static/js/vendor/jquery.cookie.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery_cookie___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_jquery_cookie__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_utility__ = __webpack_require__("./common/static/js/src/utility.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_utility___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_utility__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_common_js_components_utils_view_utils__ = __webpack_require__("./common/static/common/js/components/utils/view_utils.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_common_js_components_utils_view_utils___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_common_js_components_utils_view_utils__);







function LoginFactory(homepageURL) {
    function postJSON(url, data, callback) {
        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            data: data,
            success: callback
        });
    }

    // Clear the login error message when credentials are edited
    $('input#email').on('input', function () {
        $('#login_error').removeClass('is-shown');
    });

    $('input#password').on('input', function () {
        $('#login_error').removeClass('is-shown');
    });

    $('form#login_form').submit(function (event) {
        event.preventDefault();
        var $submitButton = $('#submit'),
            deferred = new $.Deferred(),
            promise = deferred.promise();
        __WEBPACK_IMPORTED_MODULE_2_common_js_components_utils_view_utils___default.a.disableElementWhileRunning($submitButton, function () {
            return promise;
        });
        var submit_data = $('#login_form').serialize();

        postJSON('/login_post', submit_data, function (json) {
            if (json.success) {
                var next = /next=([^&]*)/g.exec(decodeURIComponent(window.location.search));
                if (next && next.length > 1 && !isExternal(next[1])) {
                    __WEBPACK_IMPORTED_MODULE_2_common_js_components_utils_view_utils___default.a.redirect(next[1]);
                } else {
                    __WEBPACK_IMPORTED_MODULE_2_common_js_components_utils_view_utils___default.a.redirect(homepageURL);
                }
            } else if ($('#login_error').length === 0) {
                $('#login_form').prepend('<div id="login_error" class="message message-status error">' + json.value + '</span></div>');
                $('#login_error').addClass('is-shown');
                deferred.resolve();
            } else {
                $('#login_error').stop().addClass('is-shown').html(json.value);
                deferred.resolve();
            }
        });
    });
};


/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ }),

/***/ 1:
/***/ (function(module, exports) {

(function() { module.exports = window["_"]; }());

/***/ }),

/***/ 2:
/***/ (function(module, exports) {

(function() { module.exports = window["Backbone"]; }());

/***/ }),

/***/ 3:
/***/ (function(module, exports) {

(function() { module.exports = window["gettext"]; }());

/***/ })

},["./cms/static/js/factories/login.js"])));
//# sourceMappingURL=login.js.map