(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([75],{

/***/ "./openedx/features/course_experience/static/course_experience/js/WelcomeMessage.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "WelcomeMessage", function() { return WelcomeMessage; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery_cookie__ = __webpack_require__("./common/static/js/vendor/jquery.cookie.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery_cookie___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_jquery_cookie__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/* globals $ */


var WelcomeMessage = function () {
  _createClass(WelcomeMessage, null, [{
    key: 'dismissWelcomeMessage',
    // eslint-disable-line import/prefer-default-export

    value: function dismissWelcomeMessage(dismissUrl) {
      $.ajax({
        type: 'POST',
        url: dismissUrl,
        headers: {
          'X-CSRFToken': $.cookie('csrftoken')
        },
        success: function success() {
          $('.welcome-message').hide();
        }
      });
    }
  }]);

  function WelcomeMessage(options) {
    _classCallCheck(this, WelcomeMessage);

    // Dismiss the welcome message if the user clicks dismiss, or auto-dismiss if
    // the user doesn't click dismiss in 7 days from when it was first viewed.

    // Check to see if the welcome message has been displayed at all.
    if ($('.welcome-message').length > 0) {
      // If the welcome message has been viewed.
      if ($.cookie('welcome-message-viewed') === 'True') {
        // If the timer cookie no longer exists, dismiss the welcome message permanently.
        if ($.cookie('welcome-message-timer') !== 'True') {
          WelcomeMessage.dismissWelcomeMessage(options.dismissUrl);
        }
      } else {
        // Set both the viewed cookie and the timer cookie.
        $.cookie('welcome-message-viewed', 'True', { expires: 365 });
        $.cookie('welcome-message-timer', 'True', { expires: 7 });
      }
    }
    $('.dismiss-message button').click(function () {
      return WelcomeMessage.dismissWelcomeMessage(options.dismissUrl);
    });
  }

  return WelcomeMessage;
}();
/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ })

},["./openedx/features/course_experience/static/course_experience/js/WelcomeMessage.js"])));
//# sourceMappingURL=WelcomeMessage.js.map