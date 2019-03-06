(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([80],{

/***/ "./openedx/features/course_experience/static/course_experience/js/CourseOutline.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CourseOutline", function() { return CourseOutline; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_edx_ui_toolkit_js_utils_constants__ = __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/constants.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_edx_ui_toolkit_js_utils_constants___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_edx_ui_toolkit_js_utils_constants__);
function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/* globals Logger */



// @TODO: Figure out how to make webpack handle default exports when libraryTarget: 'window'
var CourseOutline = // eslint-disable-line import/prefer-default-export
function CourseOutline() {
  _classCallCheck(this, CourseOutline);

  var focusable = [].concat(_toConsumableArray(document.querySelectorAll('.outline-item.focusable')));

  focusable.forEach(function (el) {
    return el.addEventListener('keydown', function (event) {
      var index = focusable.indexOf(event.target);

      switch (event.key) {// eslint-disable-line default-case
        case __WEBPACK_IMPORTED_MODULE_0_edx_ui_toolkit_js_utils_constants__["keys"].down:
          event.preventDefault();
          focusable[Math.min(index + 1, focusable.length - 1)].focus();
          break;
        case __WEBPACK_IMPORTED_MODULE_0_edx_ui_toolkit_js_utils_constants__["keys"].up:
          // @TODO: Get these from the UI Toolkit
          event.preventDefault();
          focusable[Math.max(index - 1, 0)].focus();
          break;
      }
    });
  });

  [].concat(_toConsumableArray(document.querySelectorAll('a:not([href^="#"])'))).forEach(function (link) {
    return link.addEventListener('click', function (event) {
      Logger.log('edx.ui.lms.link_clicked', {
        current_url: window.location.href,
        target_url: event.currentTarget.href
      });
    });
  });

  function expandSection(sectionToggleButton) {
    var $toggleButtonChevron = $(sectionToggleButton).children('.fa-chevron-right');
    var $contentPanel = $(document.getElementById(sectionToggleButton.getAttribute('aria-controls')));

    $contentPanel.slideDown();
    $contentPanel.removeClass('is-hidden');
    $toggleButtonChevron.addClass('fa-rotate-90');
    sectionToggleButton.setAttribute('aria-expanded', 'true');
  }

  function collapseSection(sectionToggleButton) {
    var $toggleButtonChevron = $(sectionToggleButton).children('.fa-chevron-right');
    var $contentPanel = $(document.getElementById(sectionToggleButton.getAttribute('aria-controls')));

    $contentPanel.slideUp();
    $contentPanel.addClass('is-hidden');
    $toggleButtonChevron.removeClass('fa-rotate-90');
    sectionToggleButton.setAttribute('aria-expanded', 'false');
  }

  [].concat(_toConsumableArray(document.querySelectorAll('.accordion'))).forEach(function (accordion) {
    var sections = Array.prototype.slice.call(accordion.querySelectorAll('.accordion-trigger'));

    sections.forEach(function (section) {
      return section.addEventListener('click', function (event) {
        var sectionToggleButton = event.currentTarget;
        if (sectionToggleButton.classList.contains('accordion-trigger')) {
          var isExpanded = sectionToggleButton.getAttribute('aria-expanded') === 'true';
          if (!isExpanded) {
            expandSection(sectionToggleButton);
          } else if (isExpanded) {
            collapseSection(sectionToggleButton);
          }
          event.stopImmediatePropagation();
        }
      });
    });
  });

  var toggleAllButton = document.querySelector('#expand-collapse-outline-all-button');
  var toggleAllSpan = document.querySelector('#expand-collapse-outline-all-span');
  var extraPaddingClass = 'expand-collapse-outline-all-extra-padding';
  toggleAllButton.addEventListener('click', function (event) {
    var toggleAllExpanded = toggleAllButton.getAttribute('aria-expanded') === 'true';
    var sectionAction = void 0;
    if (toggleAllExpanded) {
      toggleAllButton.setAttribute('aria-expanded', 'false');
      sectionAction = collapseSection;
      toggleAllSpan.classList.add(extraPaddingClass);
      toggleAllSpan.innerText = 'Expand All';
    } else {
      toggleAllButton.setAttribute('aria-expanded', 'true');
      sectionAction = expandSection;
      toggleAllSpan.classList.remove(extraPaddingClass);
      toggleAllSpan.innerText = 'Collapse All';
    }
    var sections = Array.prototype.slice.call(document.querySelectorAll('.accordion-trigger'));
    sections.forEach(function (sectionToggleButton) {
      sectionAction(sectionToggleButton);
    });
    event.stopImmediatePropagation();
  });
};
/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ })

},["./openedx/features/course_experience/static/course_experience/js/CourseOutline.js"])));
//# sourceMappingURL=CourseOutline.js.map