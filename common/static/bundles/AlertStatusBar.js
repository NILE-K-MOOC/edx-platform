(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([85],{

/***/ "./lms/static/js/accessible_components/StatusBarAlert.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "StatusAlertRenderer", function() { return StatusAlertRenderer; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react_dom__ = __webpack_require__("./node_modules/react-dom/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react_dom___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_react_dom__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__ = __webpack_require__("./node_modules/@edx/paragon/static/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/*
Wrapper for React/Paragon accessible status bar
*/





var StatusAlertRenderer = function () {
  function StatusAlertRenderer(message, selector, afterselector) {
    var _this = this;

    _classCallCheck(this, StatusAlertRenderer);

    this.shiftFocus = this.shiftFocus.bind(this);
    var element = document.querySelector(selector);

    if (element) {
      /*
      These props match the defaults mostly in the paragon lib:
      https://github.com/edx/paragon/tree/master/src/StatusAlert
      but are made explicit in the case of a upstream change to defaults
      */
      __WEBPACK_IMPORTED_MODULE_1_react_dom___default.a.render(__WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["StatusAlert"], {
        alertType: 'warning',
        dismissible: true,
        open: true,
        dialog: message,
        dismissable: true,
        onClose: function onClose() {
          return _this.shiftFocus(afterselector);
        }
      }), document.querySelector(selector));
    }
  }

  _createClass(StatusAlertRenderer, [{
    key: 'shiftFocus',
    value: function shiftFocus(afterselector) {
      var afterelement = document.querySelector(afterselector);
      /*
      Optional generic function to shift 'next' focusable element for keyboard users
      */
      if (afterelement) {
        afterelement.focus();
      }
    }
  }]);

  return StatusAlertRenderer;
}();

/***/ })

},["./lms/static/js/accessible_components/StatusBarAlert.jsx"])));
//# sourceMappingURL=AlertStatusBar.js.map