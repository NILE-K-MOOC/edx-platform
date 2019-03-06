(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([21,31,86],{

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

/***/ }),

/***/ "./lms/static/js/student_account/AccountsClient.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return deactivate; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_whatwg_fetch__ = __webpack_require__("./node_modules/whatwg-fetch/fetch.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_whatwg_fetch___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_whatwg_fetch__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_cookie__ = __webpack_require__("./node_modules/js-cookie/src/js.cookie.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_cookie___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_js_cookie__);



var deactivate = function deactivate(password) {
  return fetch('/api/user/v1/accounts/deactivate_logout/', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'X-CSRFToken': __WEBPACK_IMPORTED_MODULE_1_js_cookie___default.a.get('csrftoken')
    },
    // URLSearchParams + polyfill doesn't work in IE11
    body: 'password=' + encodeURIComponent(password)
  }).then(function (response) {
    if (response.ok) {
      return response;
    }

    throw new Error(response);
  });
};



/***/ }),

/***/ "./lms/static/js/student_account/StudentAccountDeletionInitializer.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_ReactRenderer__ = __webpack_require__("./common/static/js/src/ReactRenderer.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__components_StudentAccountDeletion__ = __webpack_require__("./lms/static/js/student_account/components/StudentAccountDeletion.jsx");
/* eslint-disable no-new */



var maxWait = 60000;
var interval = 50;
var accountDeletionWrapperId = 'account-deletion-container';
var currentWait = 0;

var wrapperRendered = setInterval(function () {
  var wrapper = document.getElementById(accountDeletionWrapperId);

  if (wrapper) {
    clearInterval(wrapperRendered);
    new __WEBPACK_IMPORTED_MODULE_0_ReactRenderer__["ReactRenderer"]({
      component: __WEBPACK_IMPORTED_MODULE_1__components_StudentAccountDeletion__["StudentAccountDeletion"],
      selector: '#' + accountDeletionWrapperId,
      componentName: 'StudentAccountDeletion',
      props: { socialAccountLinks: window.auth, isActive: window.isActive }
    });
  }

  currentWait += interval;

  if (currentWait >= maxWait) {
    clearInterval(wrapperRendered);
  }
}, interval);

/***/ }),

/***/ "./lms/static/js/student_account/components/StudentAccountDeletion.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "StudentAccountDeletion", function() { return StudentAccountDeletion; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__ = __webpack_require__("./node_modules/@edx/paragon/static/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils__ = __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__StudentAccountDeletionModal__ = __webpack_require__("./lms/static/js/student_account/components/StudentAccountDeletionModal.jsx");
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/* globals gettext */
/* eslint-disable react/no-danger, import/prefer-default-export */






var StudentAccountDeletion = function (_React$Component) {
  _inherits(StudentAccountDeletion, _React$Component);

  function StudentAccountDeletion(props) {
    _classCallCheck(this, StudentAccountDeletion);

    var _this = _possibleConstructorReturn(this, (StudentAccountDeletion.__proto__ || Object.getPrototypeOf(StudentAccountDeletion)).call(this, props));

    _this.closeDeletionModal = _this.closeDeletionModal.bind(_this);
    _this.loadDeletionModal = _this.loadDeletionModal.bind(_this);
    _this.state = {
      deletionModalOpen: false,
      isActive: props.isActive,
      socialAuthConnected: _this.getConnectedSocialAuth()
    };
    return _this;
  }

  _createClass(StudentAccountDeletion, [{
    key: 'getConnectedSocialAuth',
    value: function getConnectedSocialAuth() {
      var socialAccountLinks = this.props.socialAccountLinks;

      if (socialAccountLinks && socialAccountLinks.providers) {
        return socialAccountLinks.providers.reduce(function (acc, value) {
          return acc || value.connected;
        }, false);
      }

      return false;
    }
  }, {
    key: 'closeDeletionModal',
    value: function closeDeletionModal() {
      this.setState({ deletionModalOpen: false });
      this.modalTrigger.focus();
    }
  }, {
    key: 'loadDeletionModal',
    value: function loadDeletionModal() {
      this.setState({ deletionModalOpen: true });
    }
  }, {
    key: 'render',
    value: function render() {
      var _this2 = this;

      var _state = this.state,
          deletionModalOpen = _state.deletionModalOpen,
          socialAuthConnected = _state.socialAuthConnected,
          isActive = _state.isActive;

      var loseAccessText = __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('You may also lose access to verified certificates and other program credentials like MicroMasters certificates. If you want to make a copy of these for your records before proceeding with deletion, follow the instructions for {htmlStart}printing or downloading a certificate{htmlEnd}.'), {
        htmlStart: '<a href="https://edx.readthedocs.io/projects/edx-guide-for-students/en/latest/SFD_certificates.html#printing-a-certificate" target="_blank">',
        htmlEnd: '</a>'
      });

      var showError = socialAuthConnected || !isActive;

      var socialAuthError = __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('Before proceeding, please {htmlStart}unlink all social media accounts{htmlEnd}.'), {
        htmlStart: '<a href="https://support.edx.org/hc/en-us/articles/207206067" target="_blank">',
        htmlEnd: '</a>'
      });

      var activationError = __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('Before proceeding, please {htmlStart}activate your account{htmlEnd}.'), {
        htmlStart: '<a href="https://support.edx.org/hc/en-us/articles/115000940568-How-do-I-activate-my-account-" target="_blank">',
        htmlEnd: '</a>'
      });

      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'account-deletion-details' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'p',
          { className: 'account-settings-header-subtitle' },
          gettext('We’re sorry to see you go!')
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'p',
          { className: 'account-settings-header-subtitle' },
          gettext('Please note: Deletion of your account and personal data is permanent and cannot be undone. EdX will not be able to recover your account or the data that is deleted.')
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'p',
          { className: 'account-settings-header-subtitle' },
          gettext('Once your account is deleted, you cannot use it to take courses on the edX app, edx.org, or any other site hosted by edX. This includes access to edx.org from your employer’s or university’s system and access to private sites offered by MIT Open Learning, Wharton Executive Education, and Harvard Medical School.')
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('p', {
          className: 'account-settings-header-subtitle',
          dangerouslySetInnerHTML: { __html: loseAccessText }
        }),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["Button"], {
          id: 'delete-account-btn',
          className: ['btn-outline-primary'],
          disabled: showError,
          label: gettext('Delete My Account'),
          inputRef: function inputRef(input) {
            _this2.modalTrigger = input;
          },
          onClick: this.loadDeletionModal
        }),
        showError && __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["StatusAlert"], {
          dialog: __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'div',
            { className: 'modal-alert' },
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'div',
              { className: 'icon-wrapper' },
              __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["Icon"], { id: 'delete-confirmation-body-error-icon', className: ['fa', 'fa-exclamation-circle'] })
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'div',
              { className: 'alert-content' },
              socialAuthConnected && isActive && __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('p', { dangerouslySetInnerHTML: { __html: socialAuthError } }),
              !isActive && __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('p', { dangerouslySetInnerHTML: { __html: activationError } })
            )
          ),
          alertType: 'danger',
          dismissible: false,
          open: true
        }),
        deletionModalOpen && __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_4__StudentAccountDeletionModal__["a" /* default */], { onClose: this.closeDeletionModal })
      );
    }
  }]);

  return StudentAccountDeletion;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

StudentAccountDeletion.propTypes = {
  isActive: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.bool.isRequired,
  socialAccountLinks: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.shape({
    providers: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.arrayOf(__WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.object)
  }).isRequired
};

/***/ }),

/***/ "./lms/static/js/student_account/components/StudentAccountDeletionModal.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__ = __webpack_require__("./node_modules/@edx/paragon/static/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__edx_paragon_static___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils__ = __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__AccountsClient__ = __webpack_require__("./lms/static/js/student_account/AccountsClient.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__removeLoggedInCookies__ = __webpack_require__("./lms/static/js/student_account/components/removeLoggedInCookies.js");
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/* globals gettext */
/* eslint-disable react/no-danger */








var StudentAccountDeletionConfirmationModal = function (_React$Component) {
  _inherits(StudentAccountDeletionConfirmationModal, _React$Component);

  function StudentAccountDeletionConfirmationModal(props) {
    _classCallCheck(this, StudentAccountDeletionConfirmationModal);

    var _this = _possibleConstructorReturn(this, (StudentAccountDeletionConfirmationModal.__proto__ || Object.getPrototypeOf(StudentAccountDeletionConfirmationModal)).call(this, props));

    _this.deleteAccount = _this.deleteAccount.bind(_this);
    _this.handlePasswordInputChange = _this.handlePasswordInputChange.bind(_this);
    _this.passwordFieldValidation = _this.passwordFieldValidation.bind(_this);
    _this.handleConfirmationModalClose = _this.handleConfirmationModalClose.bind(_this);
    _this.state = {
      password: '',
      passwordSubmitted: false,
      passwordValid: true,
      validationMessage: '',
      validationErrorDetails: '',
      accountQueuedForDeletion: false,
      responseError: false
    };
    return _this;
  }

  _createClass(StudentAccountDeletionConfirmationModal, [{
    key: 'handleConfirmationModalClose',
    value: function handleConfirmationModalClose() {
      this.props.onClose();

      __webpack_require__.i(__WEBPACK_IMPORTED_MODULE_5__removeLoggedInCookies__["a" /* default */])();
      window.location.href = 'https://www.edx.org';
    }
  }, {
    key: 'deleteAccount',
    value: function deleteAccount() {
      var _this2 = this;

      return this.setState({ passwordSubmitted: true }, function () {
        return __webpack_require__.i(__WEBPACK_IMPORTED_MODULE_4__AccountsClient__["a" /* deactivate */])(_this2.state.password).then(function () {
          return _this2.setState({
            accountQueuedForDeletion: true,
            responseError: false,
            passwordSubmitted: false,
            validationMessage: '',
            validationErrorDetails: ''
          });
        }).catch(function (error) {
          return _this2.failedSubmission(error);
        });
      });
    }
  }, {
    key: 'failedSubmission',
    value: function failedSubmission(error) {
      var status = error.status;

      var title = status === 403 ? gettext('Password is incorrect') : gettext('Unable to delete account');
      var body = status === 403 ? gettext('Please re-enter your password.') : gettext('Sorry, there was an error trying to process your request. Please try again later.');

      this.setState({
        passwordSubmitted: false,
        responseError: true,
        passwordValid: false,
        validationMessage: title,
        validationErrorDetails: body
      });
    }
  }, {
    key: 'handlePasswordInputChange',
    value: function handlePasswordInputChange(value) {
      this.setState({ password: value });
    }
  }, {
    key: 'passwordFieldValidation',
    value: function passwordFieldValidation(value) {
      var feedback = { passwordValid: true };

      if (value.length < 1) {
        feedback = {
          passwordValid: false,
          validationMessage: gettext('A Password is required'),
          validationErrorDetails: ''
        };
      }

      this.setState(feedback);
    }
  }, {
    key: 'renderConfirmationModal',
    value: function renderConfirmationModal() {
      var _state = this.state,
          passwordValid = _state.passwordValid,
          password = _state.password,
          passwordSubmitted = _state.passwordSubmitted,
          responseError = _state.responseError,
          validationErrorDetails = _state.validationErrorDetails,
          validationMessage = _state.validationMessage;
      var onClose = this.props.onClose;

      var loseAccessText = __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('You may also lose access to verified certificates and other program credentials like MicroMasters certificates. If you want to make a copy of these for your records before proceeding with deletion, follow the instructions for {htmlStart}printing or downloading a certificate{htmlEnd}.'), {
        htmlStart: '<a href="https://edx.readthedocs.io/projects/edx-guide-for-students/en/latest/SFD_certificates.html#printing-a-certificate" target="_blank">',
        htmlEnd: '</a>'
      });

      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'delete-confirmation-wrapper' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["Modal"], {
          title: gettext('Are you sure?'),
          renderHeaderCloseButton: false,
          onClose: onClose,
          'aria-live': 'polite',
          open: true,
          body: __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'div',
            null,
            responseError && __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["StatusAlert"], {
              dialog: __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                'div',
                { className: 'modal-alert' },
                __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                  'div',
                  { className: 'icon-wrapper' },
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["Icon"], { id: 'delete-confirmation-body-error-icon', className: ['fa', 'fa-exclamation-circle'] })
                ),
                __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                  'div',
                  { className: 'alert-content' },
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                    'h3',
                    { className: 'alert-title' },
                    validationMessage
                  ),
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                    'p',
                    null,
                    validationErrorDetails
                  )
                )
              ),
              alertType: 'danger',
              dismissible: false,
              open: true
            }),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["StatusAlert"], {
              dialog: __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                'div',
                { className: 'modal-alert' },
                __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                  'div',
                  { className: 'icon-wrapper' },
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["Icon"], { id: 'delete-confirmation-body-warning-icon', className: ['fa', 'fa-exclamation-triangle'] })
                ),
                __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                  'div',
                  { className: 'alert-content' },
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                    'h3',
                    { className: 'alert-title' },
                    gettext('You have selected “Delete my account.” Deletion of your account and personal data is permanent and cannot be undone. EdX will not be able to recover your account or the data that is deleted.')
                  ),
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                    'p',
                    null,
                    gettext('If you proceed, you will be unable to use this account to take courses on the edX app, edx.org, or any other site hosted by edX. This includes access to edx.org from your employer’s or university’s system and access to private sites offered by MIT Open Learning, Wharton Executive Education, and Harvard Medical School.')
                  ),
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('p', { dangerouslySetInnerHTML: { __html: loseAccessText } })
                )
              ),
              dismissible: false,
              open: true
            }),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'p',
              { className: 'next-steps' },
              gettext('If you still wish to continue and delete your account, please enter your account password:')
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["InputText"], {
              name: 'confirm-password',
              label: 'Password',
              type: 'password',
              className: ['confirm-password-input'],
              onBlur: this.passwordFieldValidation,
              isValid: passwordValid,
              validationMessage: validationMessage,
              onChange: this.handlePasswordInputChange,
              autoComplete: 'new-password',
              themes: ['danger']
            })
          ),
          closeText: gettext('Cancel'),
          buttons: [__WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["Button"], {
            label: gettext('Yes, Delete'),
            onClick: this.deleteAccount,
            disabled: password.length === 0 || passwordSubmitted
          })]
        })
      );
    }
  }, {
    key: 'renderSuccessModal',
    value: function renderSuccessModal() {
      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'delete-success-wrapper' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__edx_paragon_static__["Modal"], {
          title: gettext('We\'re sorry to see you go! Your account will be deleted shortly.'),
          renderHeaderCloseButton: false,
          body: gettext('Account deletion, including removal from email lists, may take a few weeks to fully process through our system. If you want to opt-out of emails before then, please unsubscribe from the footer of any email.'),
          onClose: this.handleConfirmationModalClose,
          'aria-live': 'polite',
          open: true
        })
      );
    }
  }, {
    key: 'render',
    value: function render() {
      var accountQueuedForDeletion = this.state.accountQueuedForDeletion;


      return accountQueuedForDeletion ? this.renderSuccessModal() : this.renderConfirmationModal();
    }
  }]);

  return StudentAccountDeletionConfirmationModal;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

StudentAccountDeletionConfirmationModal.propTypes = {
  onClose: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.func
};

StudentAccountDeletionConfirmationModal.defaultProps = {
  onClose: function onClose() {}
};

/* harmony default export */ __webpack_exports__["a"] = (StudentAccountDeletionConfirmationModal);

/***/ }),

/***/ "./lms/static/js/student_account/components/removeLoggedInCookies.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_js_cookie__ = __webpack_require__("./node_modules/js-cookie/src/js.cookie.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_js_cookie___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_js_cookie__);


var removeLoggedInCookies = function removeLoggedInCookies() {
  var hostname = window.location.hostname;
  var isLocalhost = hostname.indexOf('localhost') >= 0;
  var isStage = hostname.indexOf('stage') >= 0;

  var domain = '.edx.org';
  if (isLocalhost) {
    domain = 'localhost';
  } else if (isStage) {
    domain = '.stage.edx.org';
  }

  __WEBPACK_IMPORTED_MODULE_0_js_cookie___default.a.remove('edxloggedin', { domain: domain });

  if (isLocalhost) {
    // localhost doesn't have prefixes
    __WEBPACK_IMPORTED_MODULE_0_js_cookie___default.a.remove('csrftoken', { domain: domain });
    __WEBPACK_IMPORTED_MODULE_0_js_cookie___default.a.remove('edx-user-info', { domain: domain });
  } else {
    // does not take sandboxes into account
    var prefix = isStage ? 'stage' : 'prod';
    // both stage and prod csrf tokens are set to .edx.org
    __WEBPACK_IMPORTED_MODULE_0_js_cookie___default.a.remove(prefix + '-edx-csrftoken', { domain: '.edx.org' });
    __WEBPACK_IMPORTED_MODULE_0_js_cookie___default.a.remove(prefix + '-edx-user-info', { domain: domain });
  }
};

/* harmony default export */ __webpack_exports__["a"] = (removeLoggedInCookies);

/***/ })

},["./lms/static/js/student_account/StudentAccountDeletionInitializer.js"])));
//# sourceMappingURL=StudentAccountDeletionInitializer.js.map