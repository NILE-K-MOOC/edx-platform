(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([82],{

/***/ "./lms/static/js/student_account/components/PasswordResetConfirmation.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "PasswordResetConfirmation", function() { return PasswordResetConfirmation; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_whatwg_fetch__ = __webpack_require__("./node_modules/whatwg-fetch/fetch.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_whatwg_fetch___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_whatwg_fetch__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__edx_paragon_static__ = __webpack_require__("./node_modules/@edx/paragon/static/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__edx_paragon_static___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3__edx_paragon_static__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__PasswordResetInput__ = __webpack_require__("./lms/static/js/student_account/components/PasswordResetInput.jsx");
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/* globals gettext */









// NOTE: Use static paragon with this because some internal classes (StatusAlert at least)
// conflict with some standard LMS ones ('alert' at least). This means that you need to do
// something like the following on any templates that use this class:
//
// <link type='text/css' rel='stylesheet' href='${STATIC_URL}paragon/static/paragon.min.css'>
//

var PasswordResetConfirmation = function (_React$Component) {
  _inherits(PasswordResetConfirmation, _React$Component);

  function PasswordResetConfirmation(props) {
    _classCallCheck(this, PasswordResetConfirmation);

    var _this = _possibleConstructorReturn(this, (PasswordResetConfirmation.__proto__ || Object.getPrototypeOf(PasswordResetConfirmation)).call(this, props));

    _this.state = {
      password: '',
      passwordConfirmation: '',
      showMatchError: false,
      isValid: true,
      validationMessage: ''
    };
    _this.onBlurPassword1 = _this.onBlurPassword1.bind(_this);
    _this.onBlurPassword2 = _this.onBlurPassword2.bind(_this);
    return _this;
  }

  _createClass(PasswordResetConfirmation, [{
    key: 'onBlurPassword1',
    value: function onBlurPassword1(password) {
      this.updatePasswordState(password, this.state.passwordConfirmation);
      this.validatePassword(password);
    }
  }, {
    key: 'onBlurPassword2',
    value: function onBlurPassword2(passwordConfirmation) {
      this.updatePasswordState(this.state.password, passwordConfirmation);
    }
  }, {
    key: 'updatePasswordState',
    value: function updatePasswordState(password, passwordConfirmation) {
      this.setState({
        password: password,
        passwordConfirmation: passwordConfirmation,
        showMatchError: !!password && !!passwordConfirmation && password !== passwordConfirmation
      });
    }
  }, {
    key: 'validatePassword',
    value: function validatePassword(password) {
      var _this2 = this;

      fetch('/api/user/v1/validation/registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          password: password
        })
      }).then(function (res) {
        return res.json();
      }).then(function (response) {
        var validationMessage = '';
        // Be careful about grabbing this message, since we could have received an HTTP error or the
        // endpoint didn't give us what we expect. We only care if we get a clear error message.
        if (response.validation_decisions && response.validation_decisions.password) {
          validationMessage = response.validation_decisions.password;
        }
        _this2.setState({
          isValid: !validationMessage,
          validationMessage: validationMessage
        });
      });
    }
  }, {
    key: 'render',
    value: function render() {
      return __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(
        'section',
        { id: 'password-reset-confirm-anchor', className: 'form-type' },
        __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(
          'div',
          { id: 'password-reset-confirm-form', className: 'form-wrapper', 'aria-live': 'polite' },
          __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_3__edx_paragon_static__["StatusAlert"], {
            alertType: 'danger',
            dismissible: false,
            open: !!this.props.errorMessage,
            dialog: this.props.errorMessage
          }),
          __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(
            'form',
            { id: 'passwordreset-form', method: 'post', action: '' },
            __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(
              'h2',
              { className: 'section-title lines' },
              __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(
                'span',
                { className: 'text' },
                gettext('Reset Your Password')
              )
            ),
            __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(
              'p',
              { className: 'action-label', id: 'new_password_help_text' },
              gettext('Enter and confirm your new password.')
            ),
            __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_4__PasswordResetInput__["a" /* default */], {
              name: 'new_password1',
              describedBy: 'new_password_help_text',
              label: gettext('New Password'),
              onBlur: this.onBlurPassword1,
              isValid: this.state.isValid,
              validationMessage: this.state.validationMessage
            }),
            __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_4__PasswordResetInput__["a" /* default */], {
              name: 'new_password2',
              describedBy: 'new_password_help_text',
              label: gettext('Confirm Password'),
              onBlur: this.onBlurPassword2,
              isValid: !this.state.showMatchError,
              validationMessage: gettext('Passwords do not match.')
            }),
            __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement('input', {
              type: 'hidden',
              id: 'csrf_token',
              name: 'csrfmiddlewaretoken',
              value: this.props.csrfToken
            }),
            __WEBPACK_IMPORTED_MODULE_2_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_3__edx_paragon_static__["Button"], {
              type: 'submit',
              className: ['action', 'action-primary', 'action-update', 'js-reset'],
              label: gettext('Reset My Password')
            })
          )
        )
      );
    }
  }]);

  return PasswordResetConfirmation;
}(__WEBPACK_IMPORTED_MODULE_2_react___default.a.Component);

PasswordResetConfirmation.propTypes = {
  csrfToken: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  errorMessage: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string
};

PasswordResetConfirmation.defaultProps = {
  errorMessage: ''
};

 // eslint-disable-line import/prefer-default-export

/***/ }),

/***/ "./lms/static/js/student_account/components/PasswordResetInput.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__ = __webpack_require__("./node_modules/@edx/paragon/static/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__);
var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

/* globals gettext */






function PasswordResetInput(props) {
  return __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
    'div',
    { className: 'form-field' },
    __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["InputText"], _extends({
      id: props.name,
      type: 'password',
      themes: ['danger'],
      dangerIconDescription: gettext('Error: '),
      required: true
    }, props))
  );
}

PasswordResetInput.propTypes = {
  name: __WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.string.isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (PasswordResetInput);

/***/ })

},["./lms/static/js/student_account/components/PasswordResetConfirmation.jsx"])));
//# sourceMappingURL=PasswordResetConfirmation.js.map