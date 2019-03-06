(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([86],{

/***/ "./common/static/js/src/ReactRenderer.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ReactRenderer", function() { return ReactRenderer; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react_dom__ = __webpack_require__("./node_modules/react-dom/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react_dom___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_react_dom__);
var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }




var ReactRendererException = function (_Error) {
  _inherits(ReactRendererException, _Error);

  function ReactRendererException(message) {
    _classCallCheck(this, ReactRendererException);

    var _this = _possibleConstructorReturn(this, (ReactRendererException.__proto__ || Object.getPrototypeOf(ReactRendererException)).call(this, 'ReactRendererException: ' + message));

    Error.captureStackTrace(_this, ReactRendererException);
    return _this;
  }

  return ReactRendererException;
}(Error);

var ReactRenderer = function () {
  function ReactRenderer(_ref) {
    var component = _ref.component,
        selector = _ref.selector,
        componentName = _ref.componentName,
        _ref$props = _ref.props,
        props = _ref$props === undefined ? {} : _ref$props;

    _classCallCheck(this, ReactRenderer);

    _extends(this, {
      component: component,
      selector: selector,
      componentName: componentName,
      props: props
    });
    this.handleArgumentErrors();
    this.targetElement = this.getTargetElement();
    this.renderComponent();
  }

  _createClass(ReactRenderer, [{
    key: 'handleArgumentErrors',
    value: function handleArgumentErrors() {
      if (this.component === null) {
        throw new ReactRendererException('Component ' + this.componentName + ' is not defined. Make sure you\'re ' + ('using a non-default export statement for the ' + this.componentName + ' ') + ('class, that ' + this.componentName + ' has an entry point defined ') + 'within the \'entry\' section of webpack.common.config.js, and that the ' + 'entry point is pointing at the correct file path.');
      }
      if (!(this.props instanceof Object && this.props.constructor === Object)) {
        var propsType = _typeof(this.props);
        if (Array.isArray(this.props)) {
          propsType = 'array';
        } else if (this.props === null) {
          propsType = 'null';
        }
        throw new ReactRendererException('Invalid props passed to component ' + this.componentName + '. Expected ' + ('an object, but received a ' + propsType + '.'));
      }
    }
  }, {
    key: 'getTargetElement',
    value: function getTargetElement() {
      var elementList = document.querySelectorAll(this.selector);
      if (elementList.length !== 1) {
        throw new ReactRendererException('Expected 1 element match for selector "' + this.selector + '" ' + ('but received ' + elementList.length + ' matches.'));
      } else {
        return elementList[0];
      }
    }
  }, {
    key: 'renderComponent',
    value: function renderComponent() {
      __WEBPACK_IMPORTED_MODULE_1_react_dom___default.a.render(__WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(this.component, this.props, null), this.targetElement);
    }
  }]);

  return ReactRenderer;
}();

/***/ })

},["./common/static/js/src/ReactRenderer.jsx"])));
//# sourceMappingURL=ReactRenderer.js.map