(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([15],{

/***/ "./lms/djangoapps/support/static/support/jsx/errors_list.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/* global gettext */
/* eslint react/no-array-index-key: 0 */




var ShowErrors = function (_React$Component) {
  _inherits(ShowErrors, _React$Component);

  function ShowErrors() {
    _classCallCheck(this, ShowErrors);

    return _possibleConstructorReturn(this, (ShowErrors.__proto__ || Object.getPrototypeOf(ShowErrors)).apply(this, arguments));
  }

  _createClass(ShowErrors, [{
    key: 'render',
    value: function render() {
      if (this.props.errorList.length > 0) {
        window.scrollTo(0, 0);
      }
      return this.props.errorList.length > 0 && __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'alert alert-danger', role: 'alert' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'strong',
            null,
            gettext('Please fix the following errors:')
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'ul',
            null,
            this.props.errorList.map(function (error) {
              return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                'li',
                null,
                error
              );
            })
          )
        )
      );
    }
  }]);

  return ShowErrors;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

ShowErrors.propTypes = {
  errorList: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.arrayOf(__WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.object).isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (ShowErrors);

/***/ }),

/***/ "./lms/djangoapps/support/static/support/jsx/file_upload.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function($) {/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__upload_progress__ = __webpack_require__("./lms/djangoapps/support/static/support/jsx/upload_progress.jsx");
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/* global gettext */
/* eslint one-var: ["error", "always"] */






var FileUpload = function (_React$Component) {
  _inherits(FileUpload, _React$Component);

  function FileUpload(props) {
    _classCallCheck(this, FileUpload);

    var _this = _possibleConstructorReturn(this, (FileUpload.__proto__ || Object.getPrototypeOf(FileUpload)).call(this, props));

    _this.uploadFile = _this.uploadFile.bind(_this);
    _this.removeFile = _this.removeFile.bind(_this);
    _this.state = {
      fileList: [],
      fileInProgress: null
    };
    return _this;
  }

  _createClass(FileUpload, [{
    key: 'removeFile',
    value: function removeFile(e) {
      e.preventDefault();
      var fileToken = e.target.id,
          $this = this,
          url = this.props.zendeskApiHost + '/api/v2/uploads/' + fileToken + '.json',
          request = new XMLHttpRequest();

      request.open('DELETE', url, true);
      request.setRequestHeader('Authorization', 'Bearer ' + this.props.accessToken);
      request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

      request.send();

      request.onreadystatechange = function removeFile() {
        if (request.readyState === 4 && request.status === 204) {
          $this.setState({
            fileList: $this.state.fileList.filter(function (file) {
              return file.fileToken !== fileToken;
            })
          });
        }
      };
    }
  }, {
    key: 'uploadFile',
    value: function uploadFile(e) {
      var url = this.props.zendeskApiHost + '/api/v2/uploads.json?filename=',
          fileReader = new FileReader(),
          request = new XMLHttpRequest(),
          errorList = [],
          $this = this,
          file = e.target.files[0],
          maxFileSize = 5000000,
          // 5mb is max limit
      allowedFileTypes = ['gif', 'png', 'jpg', 'jpeg', 'pdf'];

      // remove file from input and upload it to zendesk after validation
      $(e.target).val('');

      if (file.size > maxFileSize) {
        errorList.push(gettext('Files that you upload must be smaller than 5MB in size.'));
      } else if ($.inArray(file.name.split('.').pop().toLowerCase(), allowedFileTypes) === -1) {
        errorList.push(gettext('Files that you upload must be PDFs or image files in .gif, .jpg, .jpeg, or .png format.'));
      }

      this.props.setErrorState(errorList);
      if (errorList.length > 0) {
        return;
      }

      request.open('POST', url + file.name, true);
      request.setRequestHeader('Authorization', 'Bearer ' + this.props.accessToken);
      request.setRequestHeader('Content-Type', 'application/binary');

      fileReader.readAsArrayBuffer(file);

      fileReader.onloadend = function success() {
        $this.setState({
          fileInProgress: file.name,
          currentRequest: request
        });
        request.send(fileReader.result);
      };

      request.upload.onprogress = function renderProgress(event) {
        if (event.lengthComputable) {
          var percentComplete = event.loaded / event.total * 100;
          $('.progress-bar-striped').css({ width: percentComplete + '%' });
        }
      };

      request.onreadystatechange = function success() {
        if (request.readyState === 4 && request.status === 201) {
          var uploadedFile = {
            fileName: file.name,
            fileToken: JSON.parse(request.response).upload.token
          };

          $this.setState({
            fileList: $this.state.fileList.concat(uploadedFile),
            fileInProgress: null
          });
        }
      };

      request.onerror = function error() {
        $this.setState({
          fileInProgress: null,
          errorList: [gettext('Something went wrong. Please try again later.')]
        });
      };

      request.onabort = function abortUpload() {
        $this.setState({
          fileInProgress: null
        });
      };
    }
  }, {
    key: 'render',
    value: function render() {
      var _this2 = this;

      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'file-container' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'row' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'div',
            { className: 'col-sm-12' },
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'div',
              { className: 'form-group' },
              __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                'label',
                { htmlFor: 'attachment' },
                gettext('Add Attachment'),
                __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                  'span',
                  null,
                  ' ',
                  gettext('(Optional)')
                )
              ),
              __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('input', {
                id: 'attachment',
                className: 'file file-loading',
                type: 'file',
                accept: '.pdf, .jpeg, .png, .jpg, .gif',
                onChange: this.uploadFile
              })
            )
          )
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'progress-container' },
          this.state.fileInProgress && __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_2__upload_progress__["a" /* default */], {
            fileName: this.state.fileInProgress,
            request: this.state.currentRequest
          })
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'uploaded-files' },
          this.state.fileList.map(function (file) {
            return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'div',
              { key: file.fileToken, className: 'row' },
              __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                'div',
                { className: 'col-sm-12' },
                __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                  'span',
                  { className: 'file-name' },
                  file.fileName
                ),
                __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                  'span',
                  { className: 'file-action remove-upload' },
                  __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                    'button',
                    { className: 'btn btn-link', id: file.fileToken, onClick: _this2.removeFile },
                    gettext('Remove file')
                  )
                )
              )
            );
          })
        )
      );
    }
  }]);

  return FileUpload;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

FileUpload.propTypes = {
  setErrorState: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.func.isRequired,
  zendeskApiHost: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  accessToken: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired
};
/* unused harmony default export */ var _unused_webpack_default_export = (FileUpload);
/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ "./lms/djangoapps/support/static/support/jsx/logged_in_user.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils__ = __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__file_upload__ = __webpack_require__("./lms/djangoapps/support/static/support/jsx/file_upload.jsx");
/* global gettext */








function LoggedInUser(_ref) {
  var userInformation = _ref.userInformation,
      setErrorState = _ref.setErrorState,
      zendeskApiHost = _ref.zendeskApiHost,
      submitForm = _ref.submitForm;

  var courseElement = void 0;
  if (userInformation.enrollments) {
    courseElement = __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      null,
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'label',
        { className: 'label-course', htmlFor: 'course' },
        gettext('Course Name')
      ),
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'select',
        { className: 'form-control select-course', id: 'course', defaultValue: userInformation.course_id },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'option',
          { key: 'select-course', value: '' },
          '--------'
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'option',
          { key: 'not-course-specific', value: 'Not specific to a course' },
          gettext('Not specific to a course')
        ),
        userInformation.enrollments.map(function (enrollment) {
          return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'option',
            { key: enrollment.course_id, value: enrollment.course_id },
            enrollment.course_name
          );
        })
      )
    );
  } else {
    courseElement = __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      null,
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'label',
        { htmlFor: 'course' },
        gettext('Course Name')
      ),
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('input', { type: 'text', className: 'form-control', id: 'course' })
    );
  }

  return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
    'div',
    null,
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        {
          className: 'col-sm-12 user-info',
          'data-username': userInformation.username,
          'data-email': userInformation.email
        },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'p',
          null,
          __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('What can we help you with, {username}?'), { username: userInformation.username })
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'form-group' },
          courseElement
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'form-group' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'label',
            { htmlFor: 'subject' },
            gettext('Subject')
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('input', { type: 'text', className: 'form-control', id: 'subject' })
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'form-group' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'label',
            { htmlFor: 'message' },
            gettext('Details')
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'p',
            {
              className: 'message-desc'
            },
            gettext('The more you tell us, the more quickly and helpfully we can respond!')
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('textarea', {
            'aria-describedby': 'message',
            className: 'form-control',
            rows: '7',
            id: 'message'
          })
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'button',
          {
            className: 'btn btn-primary btn-submit',
            onClick: submitForm
          },
          gettext('Submit')
        )
      )
    )
  );
}

LoggedInUser.propTypes = {
  setErrorState: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.func.isRequired,
  submitForm: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.func.isRequired,
  userInformation: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.arrayOf(__WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.object).isRequired,
  submitFormUrl: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (LoggedInUser);

/***/ }),

/***/ "./lms/djangoapps/support/static/support/jsx/logged_out_user.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils__ = __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils__);
/* global gettext */






function LoggedOutUser(_ref) {
  var platformName = _ref.platformName,
      loginQuery = _ref.loginQuery,
      supportEmail = _ref.supportEmail;

  return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
    'div',
    null,
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'p',
          null,
          __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('Sign in to {platform} so we can help you better.'), { platform: platformName })
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'a',
          { href: '/login' + loginQuery, className: 'btn btn-primary btn-signin' },
          gettext('Sign in')
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'a',
          { className: 'create-account', href: '/register' + loginQuery },
          __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(
          // FIXME: not all platforms start with a vowel
          gettext('Create an {platform} account'), { platform: platformName })
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'p',
          { className: 'create-account-note' },
          __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('If you are unable to access your account contact us via email using {email}.'), { email: supportEmail })
        )
      )
    )
  );
}

LoggedOutUser.propTypes = {
  platformName: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  loginQuery: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  supportEmail: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (LoggedOutUser);

/***/ }),

/***/ "./lms/djangoapps/support/static/support/jsx/single_support_form.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SingleSupportForm", function() { return SingleSupportForm; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react_dom__ = __webpack_require__("./node_modules/react-dom/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react_dom___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_react_dom__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils__ = __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__errors_list__ = __webpack_require__("./lms/djangoapps/support/static/support/jsx/errors_list.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__logged_in_user__ = __webpack_require__("./lms/djangoapps/support/static/support/jsx/logged_in_user.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__logged_out_user__ = __webpack_require__("./lms/djangoapps/support/static/support/jsx/logged_out_user.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__success__ = __webpack_require__("./lms/djangoapps/support/static/support/jsx/success.jsx");
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/* global gettext */
/* eslint one-var: ["error", "always"] */
/* eslint no-alert: "error" */












var RenderForm = function (_React$Component) {
  _inherits(RenderForm, _React$Component);

  function RenderForm(props) {
    _classCallCheck(this, RenderForm);

    var _this = _possibleConstructorReturn(this, (RenderForm.__proto__ || Object.getPrototypeOf(RenderForm)).call(this, props));

    _this.state = {
      currentRequest: null,
      errorList: [],
      success: false
    };
    _this.submitForm = _this.submitForm.bind(_this);
    _this.setErrorState = _this.setErrorState.bind(_this);
    return _this;
  }

  _createClass(RenderForm, [{
    key: 'setErrorState',
    value: function setErrorState(errors) {
      this.setState({
        errorList: errors
      });
    }
  }, {
    key: 'submitForm',
    value: function submitForm() {
      var url = this.props.context.submitFormUrl,
          $userInfo = $('.user-info'),
          request = new XMLHttpRequest(),
          $course = $('#course'),
          data = {
        subject: $('#subject').val(),
        comment: {
          body: $('#message').val()
        },
        tags: this.props.context.tags
      },
          errors = [];

      var course = void 0;
      this.clearErrors();

      data.requester = {
        email: $userInfo.data('email'),
        name: $userInfo.data('username')
      };

      course = $course.find(':selected').val();
      if (!course) {
        course = $course.val();
      }
      if (!course) {
        $('#course').closest('.form-group').addClass('has-error');
        errors.push(gettext('Select a course or select "Not specific to a course" for your support request.'));
      }
      data.custom_fields = [{
        id: this.props.context.customFields.course_id,
        value: course
      }];

      if (this.validateData(data, errors)) {
        request.open('POST', url, true);
        request.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
        request.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));

        request.send(JSON.stringify(data));

        request.onreadystatechange = function success() {
          if (request.readyState === 4 && request.status === 201) {
            this.setState({
              success: true
            });
          }
        }.bind(this);

        request.onerror = function error() {
          this.setErrorState([gettext('Something went wrong. Please try again later.')]);
        }.bind(this);
      }
    }
  }, {
    key: 'clearErrors',
    value: function clearErrors() {
      this.setErrorState([]);
      $('.form-group').removeClass('has-error');
    }
  }, {
    key: 'validateData',
    value: function validateData(data, errors) {
      if (!data.subject) {
        errors.push(gettext('Enter a subject for your support request.'));
        $('#subject').closest('.form-group').addClass('has-error');
      }
      if (!data.comment.body) {
        errors.push(gettext('Enter some details for your support request.'));
        $('#message').closest('.form-group').addClass('has-error');
      }

      if (!errors.length) {
        return true;
      }

      this.setErrorState(errors);
      return false;
    }
  }, {
    key: 'renderSuccess',
    value: function renderSuccess() {
      return __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_7__success__["a" /* default */], {
        platformName: this.props.context.platformName,
        homepageUrl: this.props.context.homepageUrl,
        dashboardUrl: this.props.context.dashboardUrl,
        isLoggedIn: this.props.context.user !== undefined
      });
    }
  }, {
    key: 'renderSupportForm',
    value: function renderSupportForm() {
      var userElement = void 0;
      if (this.props.context.user) {
        userElement = __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_5__logged_in_user__["a" /* default */], {
          userInformation: this.props.context.user,
          submitFormUrl: this.props.context.submitFormUrl,
          setErrorState: this.setErrorState,
          submitForm: this.submitForm
        });
      } else {
        userElement = __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_6__logged_out_user__["a" /* default */], {
          platformName: this.props.context.platformName,
          loginQuery: this.props.context.loginQuery,
          supportEmail: this.props.context.supportEmail
        });
      }

      return __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
        'div',
        { className: 'contact-us-wrapper' },
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'div',
          { className: 'row' },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'div',
            { className: 'col-sm-12' },
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'h2',
              null,
              gettext('Contact Us')
            )
          )
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'div',
          { className: 'row form-errors' },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_4__errors_list__["a" /* default */], { errorList: this.state.errorList })
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'div',
          { className: 'row' },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'div',
            { className: 'col-sm-12' },
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'p',
              null,
              gettext('Find answers to the top questions asked by learners.')
            )
          )
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'div',
          { className: 'row' },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'div',
            { className: 'col-sm-12' },
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'a',
              {
                href: this.props.context.marketingUrl,
                className: 'btn btn-secondary help-button'
              },
              __WEBPACK_IMPORTED_MODULE_3_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('Search the {platform} Help Center'), { platform: this.props.context.platformName })
            )
          )
        ),
        userElement
      );
    }
  }, {
    key: 'render',
    value: function render() {
      if (this.state.success) {
        return this.renderSuccess();
      }

      return this.renderSupportForm();
    }
  }]);

  return RenderForm;
}(__WEBPACK_IMPORTED_MODULE_1_react___default.a.Component);

RenderForm.propTypes = {
  context: __WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.arrayOf(__WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.object).isRequired
};

var SingleSupportForm = function SingleSupportForm(context) {
  _classCallCheck(this, SingleSupportForm);

  __WEBPACK_IMPORTED_MODULE_2_react_dom___default.a.render(__WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(RenderForm, { context: context }), document.getElementById('root'));
};
/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ "./lms/djangoapps/support/static/support/jsx/success.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils__ = __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils__);
/* global gettext */
/* eslint one-var: ["error", "always"] */






function Success(_ref) {
  var platformName = _ref.platformName,
      homepageUrl = _ref.homepageUrl,
      dashboardUrl = _ref.dashboardUrl,
      isLoggedIn = _ref.isLoggedIn;

  var btnText = void 0,
      btnUrl = void 0;
  if (isLoggedIn) {
    btnText = gettext('Go to my Dashboard');
    btnUrl = dashboardUrl;
  } else {
    btnText = __WEBPACK_IMPORTED_MODULE_2_edx_ui_toolkit_js_utils_string_utils___default.a.interpolate(gettext('Go to {platform} Home'), { platform: platformName });
    btnUrl = homepageUrl;
  }
  return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
    'div',
    { className: 'contact-us-wrapper' },
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'h2',
          null,
          gettext('Contact Us')
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'p',
          null,
          gettext('Thank you for submitting a request! We will contact you within 24 hours.')
        )
      )
    ),
    __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
      'div',
      { className: 'row' },
      __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'col-sm-12' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'a',
          {
            href: btnUrl,
            className: 'btn btn-secondary help-button'
          },
          btnText
        )
      )
    )
  );
}

Success.propTypes = {
  platformName: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  dashboardUrl: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  homepageUrl: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  isLoggedIn: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.bool.isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (Success);

/***/ }),

/***/ "./lms/djangoapps/support/static/support/jsx/upload_progress.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_prop_types__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/* global gettext */




var ShowProgress = function (_React$Component) {
  _inherits(ShowProgress, _React$Component);

  function ShowProgress(props) {
    _classCallCheck(this, ShowProgress);

    var _this = _possibleConstructorReturn(this, (ShowProgress.__proto__ || Object.getPrototypeOf(ShowProgress)).call(this, props));

    _this.abortRequest = _this.abortRequest.bind(_this);
    return _this;
  }

  _createClass(ShowProgress, [{
    key: 'abortRequest',
    value: function abortRequest(e) {
      e.preventDefault();
      this.props.request.abort();
    }
  }, {
    key: 'render',
    value: function render() {
      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'row' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'col-sm-12' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'div',
            { className: 'form-group' },
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'span',
              { className: 'file-name' },
              this.props.fileName
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'span',
              { className: 'file-action abort-upload' },
              __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
                'button',
                { className: 'btn btn-link', onClick: this.abortRequest },
                gettext('Cancel upload')
              )
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'div',
              { className: 'progress' },
              __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('div', { className: 'progress-bar progress-bar-striped zero-width', role: 'progressbar' })
            )
          )
        )
      );
    }
  }]);

  return ShowProgress;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

ShowProgress.propTypes = {
  fileName: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.string.isRequired,
  request: __WEBPACK_IMPORTED_MODULE_1_prop_types___default.a.objectOf(XMLHttpRequest).isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (ShowProgress);

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ })

},["./lms/djangoapps/support/static/support/jsx/single_support_form.jsx"])));
//# sourceMappingURL=SingleSupportForm.js.map