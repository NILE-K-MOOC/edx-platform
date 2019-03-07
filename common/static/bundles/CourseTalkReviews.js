(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([78],{

/***/ "./openedx/features/course_experience/static/course_experience/js/CourseTalkReviews.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CourseTalkReviews", function() { return CourseTalkReviews; });
function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
  Enable users to switch between viewing and writing CourseTalk reviews.
 */

var CourseTalkReviews = // eslint-disable-line import/prefer-default-export
function CourseTalkReviews(options) {
  _classCallCheck(this, CourseTalkReviews);

  var $courseTalkToggleReadWriteReviews = $(options.toggleButton);

  var toReadBtnText = 'View Reviews';
  var toWriteBtnText = 'Write a Review';

  // Initialize page to the read reviews view
  self.currentSrc = options.readSrc;
  $.getScript(options.readSrc, function () {
    // eslint-disable-line func-names
    $('iframe').load(function () {
      $(options.loadIcon).hide();
    });
  });
  $courseTalkToggleReadWriteReviews.text(toWriteBtnText);

  $courseTalkToggleReadWriteReviews.on('click', function () {
    var switchToReadView = self.currentSrc === options.writeSrc;
    // Cache js file for future button clicks
    $.ajaxSetup({ cache: true });

    // Show the loading icon
    $(options.loadIcon).show();

    // Update toggle button text
    var newBtnText = switchToReadView ? toWriteBtnText : toReadBtnText;
    $courseTalkToggleReadWriteReviews.text(newBtnText);

    // Toggle the new coursetalk script object
    self.currentSrc = switchToReadView ? options.readSrc : options.writeSrc;
    $.getScript(self.currentSrc, function () {
      // eslint-disable-line func-names
      $('iframe').load(function () {
        $(options.loadIcon).hide();
      });
    });
  });
};
/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ })

},["./openedx/features/course_experience/static/course_experience/js/CourseTalkReviews.js"])));
//# sourceMappingURL=CourseTalkReviews.js.map