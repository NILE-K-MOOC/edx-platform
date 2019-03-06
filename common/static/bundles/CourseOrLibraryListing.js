(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([87],{

/***/ "./cms/static/js/features_jsx/studio/CourseOrLibraryListing.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (immutable) */ __webpack_exports__["CourseOrLibraryListing"] = CourseOrLibraryListing;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react_dom__ = __webpack_require__("./node_modules/react-dom/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react_dom___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_react_dom__);
/* global gettext */
/* eslint react/no-array-index-key: 0 */





function CourseOrLibraryListing(props) {
  var allowReruns = props.allowReruns;
  var linkClass = props.linkClass;
  var idBase = props.idBase;

  return __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
    'ul',
    { className: 'list-courses' },
    props.items.map(function (item, i) {
      return __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
        'li',
        { key: i, className: 'course-item', 'data-course-key': item.course_key },
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'a',
          { className: linkClass, href: item.url },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'h3',
            { className: 'course-title', id: 'title-' + idBase + '-' + i },
            item.display_name
          ),
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'div',
            { className: 'course-metadata' },
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'span',
              { className: 'course-org metadata-item' },
              __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
                'span',
                { className: 'label' },
                gettext('Organization:')
              ),
              __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
                'span',
                { className: 'value' },
                item.org
              )
            ),
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'span',
              { className: 'course-num metadata-item' },
              __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
                'span',
                { className: 'label' },
                gettext('Course Number:')
              ),
              __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
                'span',
                { className: 'value' },
                item.number
              )
            ),
            item.run && __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'span',
              { className: 'course-run metadata-item' },
              __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
                'span',
                { className: 'label' },
                gettext('Course Run:')
              ),
              __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
                'span',
                { className: 'value' },
                item.run
              )
            ),
            item.can_edit === false && __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'span',
              { className: 'extra-metadata' },
              gettext('(Read-only)')
            )
          )
        ),
        item.lms_link && item.rerun_link && __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'ul',
          { className: 'item-actions course-actions' },
          allowReruns && __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'li',
            { className: 'action action-rerun' },
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'a',
              {
                href: item.rerun_link,
                className: 'button rerun-button',
                'aria-labelledby': 're-run-' + idBase + '-' + i + ' title-' + idBase + '-' + i,
                id: 're-run-' + idBase + '-' + i
              },
              gettext('Re-run Course')
            )
          ),
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'li',
            { className: 'action action-view' },
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
              'a',
              {
                href: item.lms_link,
                rel: 'external',
                className: 'button view-button',
                'aria-labelledby': 'view-live-' + idBase + '-' + i + ' title-' + idBase + '-' + i,
                id: 'view-live-' + idBase + '-' + i
              },
              gettext('View Live')
            )
          )
        )
      );
    })
  );
}

CourseOrLibraryListing.propTypes = {
  allowReruns: __WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.bool.isRequired,
  idBase: __WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.string.isRequired,
  items: __WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.arrayOf(__WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.object).isRequired,
  linkClass: __WEBPACK_IMPORTED_MODULE_0_prop_types___default.a.string.isRequired
};

/***/ })

},["./cms/static/js/features_jsx/studio/CourseOrLibraryListing.jsx"])));
//# sourceMappingURL=CourseOrLibraryListing.js.map