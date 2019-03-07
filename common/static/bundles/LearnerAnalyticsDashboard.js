(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([20],{

/***/ "./lms/static/js/learner_analytics_dashboard/CircleChart.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames__ = __webpack_require__("./node_modules/classnames/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_classnames__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_prop_types__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }





var size = 100;
var radCircumference = Math.PI * 2;
var center = size / 2;
var radius = center - 1; // padding to prevent clipping

// Based on https://github.com/brigade/react-simple-pie-chart

var CircleChart = function (_React$Component) {
  _inherits(CircleChart, _React$Component);

  function CircleChart(props) {
    _classCallCheck(this, CircleChart);

    var _this = _possibleConstructorReturn(this, (CircleChart.__proto__ || Object.getPrototypeOf(CircleChart)).call(this, props));

    _this.getCenter = _this.getCenter.bind(_this);
    _this.getSlices = _this.getSlices.bind(_this);
    return _this;
  }

  _createClass(CircleChart, [{
    key: 'getCenter',
    value: function getCenter() {
      var _props = this.props,
          centerHole = _props.centerHole,
          sliceBorder = _props.sliceBorder;

      if (centerHole) {
        var _size = center / 2;
        return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('circle', { cx: center, cy: center, r: _size, fill: sliceBorder.strokeColor });
      }
    }
  }, {
    key: 'getSlices',
    value: function getSlices(slices, sliceBorder) {
      var total = slices.reduce(function (totalValue, _ref) {
        var value = _ref.value;
        return totalValue + value;
      }, 0);
      var strokeColor = sliceBorder.strokeColor,
          strokeWidth = sliceBorder.strokeWidth;


      var radSegment = 0;
      var lastX = radius;
      var lastY = 0;

      // Reverse a copy of the array so order start at 12 o'clock
      return slices.slice(0).reverse().map(function (_ref2, index) {
        var value = _ref2.value,
            sliceIndex = _ref2.sliceIndex;

        // Should we just draw a circle?
        if (value === total) {
          return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('circle', { r: radius,
            cx: center,
            cy: center,
            className: 'slice-1',
            key: index });
        }

        if (value === 0) {
          return;
        }

        var valuePercentage = value / total;

        // Should the arc go the long way round?
        var longArc = valuePercentage <= 0.5 ? 0 : 1;

        radSegment += valuePercentage * radCircumference;
        var nextX = Math.cos(radSegment) * radius;
        var nextY = Math.sin(radSegment) * radius;

        /**
         * d is a string that describes the path of the slice.
         * The weirdly placed minus signs [eg, (-(lastY))] are due to the fact
         * that our calculations are for a graph with positive Y values going up,
         * but on the screen positive Y values go down.
         */
        var d = ['M ' + center + ',' + center, 'l ' + lastX + ',' + -lastY, 'a' + radius + ',' + radius, '0', longArc + ',0', nextX - lastX + ',' + -(nextY - lastY), 'z'].join(' ');

        lastX = nextX;
        lastY = nextY;

        return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('path', { d: d,
          className: 'slice-' + sliceIndex,
          key: index,
          stroke: strokeColor,
          strokeWidth: strokeWidth });
      });
    }
  }, {
    key: 'render',
    value: function render() {
      var _props2 = this.props,
          slices = _props2.slices,
          sliceBorder = _props2.sliceBorder;


      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'svg',
        { viewBox: '0 0 ' + size + ' ' + size },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'g',
          { transform: 'rotate(-90 ' + center + ' ' + center + ')' },
          this.getSlices(slices, sliceBorder)
        ),
        this.getCenter()
      );
    }
  }]);

  return CircleChart;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

CircleChart.defaultProps = {
  sliceBorder: {
    strokeColor: '#fff',
    strokeWidth: 0
  }
};

CircleChart.propTypes = {
  slices: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.array.isRequired,
  centerHole: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.bool,
  sliceBorder: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.object
};

/* harmony default export */ __webpack_exports__["a"] = (CircleChart);

/***/ }),

/***/ "./lms/static/js/learner_analytics_dashboard/CircleChartLegend.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames__ = __webpack_require__("./node_modules/classnames/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_classnames__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_prop_types__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }





var CircleChartLegend = function (_React$Component) {
  _inherits(CircleChartLegend, _React$Component);

  function CircleChartLegend(props) {
    _classCallCheck(this, CircleChartLegend);

    return _possibleConstructorReturn(this, (CircleChartLegend.__proto__ || Object.getPrototypeOf(CircleChartLegend)).call(this, props));
  }

  _createClass(CircleChartLegend, [{
    key: 'getList',
    value: function getList() {
      var _this2 = this;

      var data = this.props.data;


      return data.map(function (_ref, index) {
        var value = _ref.value,
            label = _ref.label,
            sliceIndex = _ref.sliceIndex;

        var swatchClass = 'swatch-' + sliceIndex;
        return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'li',
          { className: 'legend-item', key: index },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('div', { className: __WEBPACK_IMPORTED_MODULE_1_classnames___default()('color-swatch', swatchClass),
            'aria-hidden': 'true' }),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'span',
            { className: 'label' },
            label
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'span',
            { className: 'percentage' },
            _this2.getPercentage(value)
          )
        );
      });
    }
  }, {
    key: 'getPercentage',
    value: function getPercentage(value) {
      var num = value * 100;

      return num + '%';
    }
  }, {
    key: 'renderList',
    value: function renderList() {
      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'ul',
        { className: 'legend-list' },
        this.getList()
      );
    }
  }, {
    key: 'render',
    value: function render() {
      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'legend' },
        this.renderList()
      );
    }
  }]);

  return CircleChartLegend;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

CircleChartLegend.propTypes = {
  data: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.array.isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (CircleChartLegend);

/***/ }),

/***/ "./lms/static/js/learner_analytics_dashboard/Discussions.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames__ = __webpack_require__("./node_modules/classnames/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_classnames__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_prop_types__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }





var Discussions = function (_React$Component) {
  _inherits(Discussions, _React$Component);

  function Discussions(props) {
    _classCallCheck(this, Discussions);

    return _possibleConstructorReturn(this, (Discussions.__proto__ || Object.getPrototypeOf(Discussions)).call(this, props));
  }

  _createClass(Discussions, [{
    key: 'getComparisons',
    value: function getComparisons() {
      var experiments = window.experimentVariables || {};
      var _props = this.props,
          content_authored = _props.content_authored,
          profileImages = _props.profileImages;

      var content_average = experiments.learnerAnalyticsDiscussionAverage || 4;
      var average_percent = 1;
      var authored_percent = 0;

      if (content_average > content_authored) {
        average_percent = 1;
        authored_percent = content_authored / content_average;
      } else {
        authored_percent = 1;
        average_percent = content_average / content_authored;
      }

      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'chart-wrapper' },
        this.getCountChart(content_authored, authored_percent, 'You', profileImages.medium),
        this.getCountChart(content_average, average_percent, 'Average graduate')
      );
    }
  }, {
    key: 'getCountChart',
    value: function getCountChart(count, percent, label) {
      var img = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : false;

      var percentWidth;
      if (percent === 0) {
        percentWidth = '2px';
      } else {
        percentWidth = 'calc((100% - 40px) * ' + percent + ')';
      }
      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'count-chart' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('div', { className: __WEBPACK_IMPORTED_MODULE_1_classnames___default()('chart-icon', { 'fa fa-graduation-cap': !img }),
          style: { backgroundImage: !!img ? 'url(' + img + ')' : 'none' },
          'aria-hidden': 'true' }),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'chart-label' },
          label
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'chart-display' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('div', { className: 'chart-bar',
            'aria-hidden': 'true',
            style: { width: '' + percentWidth } }),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'span',
            { className: 'user-count' },
            count
          )
        )
      );
    }
  }, {
    key: 'render',
    value: function render() {
      var _props2 = this.props,
          content_authored = _props2.content_authored,
          thread_votes = _props2.thread_votes;


      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'discussions-wrapper' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'h2',
          { className: 'group-heading' },
          'Discussions'
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'comparison-charts' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'h3',
            { className: 'section-heading' },
            'Posts, comments, and replies'
          ),
          this.getComparisons()
        ),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'div',
          { className: 'post-counts' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'div',
            { className: 'votes-wrapper' },
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement('span', { className: 'fa fa-plus-square-o count-icon', 'aria-hidden': 'true' }),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'span',
              { className: 'user-count' },
              thread_votes
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'p',
              { className: 'label' },
              'Votes on your posts, comments, and replies'
            )
          )
        )
      );
    }
  }]);

  return Discussions;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

Discussions.propTypes = {
  content_authored: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.number.isRequired,
  thread_votes: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.number.isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (Discussions);

/***/ }),

/***/ "./lms/static/js/learner_analytics_dashboard/DueDates.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames__ = __webpack_require__("./node_modules/classnames/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_classnames__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_prop_types__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }





var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

var DueDates = function (_React$Component) {
  _inherits(DueDates, _React$Component);

  function DueDates(props) {
    _classCallCheck(this, DueDates);

    return _possibleConstructorReturn(this, (DueDates.__proto__ || Object.getPrototypeOf(DueDates)).call(this, props));
  }

  _createClass(DueDates, [{
    key: 'getDate',
    value: function getDate(str) {
      var date = new Date(str);
      var day = days[date.getDay()];
      var month = months[date.getMonth()];
      var number = date.getDate();
      var year = date.getFullYear();

      return day + ' ' + month + ' ' + number + ', ' + year;
    }
  }, {
    key: 'getLabel',
    value: function getLabel(type) {
      var assignmentCounts = this.props.assignmentCounts;

      if (assignmentCounts[type] < 2) {
        return type;
      } else {
        this.renderLabels[type] += 1;
        return type + ' ' + this.renderLabels[type];
      }
    }
  }, {
    key: 'getList',
    value: function getList() {
      var _this2 = this;

      var _props = this.props,
          dates = _props.dates,
          assignmentCounts = _props.assignmentCounts;

      this.renderLabels = this.initLabelTracker(assignmentCounts);

      return dates.sort(function (a, b) {
        return new Date(a.due) > new Date(b.due);
      }).map(function (_ref, index) {
        var format = _ref.format,
            due = _ref.due;

        return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'li',
          { className: 'date-item', key: index },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'div',
            { className: 'label' },
            _this2.getLabel(format)
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'div',
            { className: 'data' },
            _this2.getDate(due)
          )
        );
      });
    }
  }, {
    key: 'initLabelTracker',
    value: function initLabelTracker(list) {
      var labels = Object.keys(list);

      return labels.reduce(function (accumulator, key) {
        accumulator[key] = 0;
        return accumulator;
      }, {});
    }
  }, {
    key: 'renderList',
    value: function renderList() {
      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'ul',
        { className: 'date-list' },
        this.getList()
      );
    }
  }, {
    key: 'render',
    value: function render() {
      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'div',
        { className: 'due-dates' },
        this.renderList()
      );
    }
  }]);

  return DueDates;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

DueDates.propTypes = {
  dates: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.array.isRequired
};

/* unused harmony default export */ var _unused_webpack_default_export = (DueDates);

/***/ }),

/***/ "./lms/static/js/learner_analytics_dashboard/GradeTable.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames__ = __webpack_require__("./node_modules/classnames/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_classnames___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_classnames__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_prop_types__);
var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }




var exGrades = [{
  "assignment_type": "Exam",
  "total_possible": 6.0,
  "total_earned": 3.0
}, {
  "assignment_type": "Homework",
  "total_possible": 5.0
}, {
  "assignment_type": "Homework",
  "total_possible": 11.0,
  "total_earned": 0.0
}];

var GradeTable = function (_React$Component) {
  _inherits(GradeTable, _React$Component);

  function GradeTable(props) {
    _classCallCheck(this, GradeTable);

    return _possibleConstructorReturn(this, (GradeTable.__proto__ || Object.getPrototypeOf(GradeTable)).call(this, props));
  }

  _createClass(GradeTable, [{
    key: 'getTableGroup',
    value: function getTableGroup(type, groupIndex) {
      var grades = this.props.grades;

      var groupData = grades.filter(function (value) {
        if (value['assignment_type'] === type) {
          return value;
        }
      });
      var multipleAssignments = groupData.length > 1;

      var rows = groupData.map(function (_ref, index) {
        var assignment_type = _ref.assignment_type,
            total_possible = _ref.total_possible,
            total_earned = _ref.total_earned,
            passing_grade = _ref.passing_grade;

        var label = multipleAssignments ? assignment_type + ' ' + (index + 1) : assignment_type;
        return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'tr',
          { key: index },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'td',
            null,
            label
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'td',
            null,
            passing_grade,
            '/',
            total_possible
          ),
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'td',
            null,
            total_earned,
            '/',
            total_possible
          )
        );
      });

      return rows.length ? __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'tbody',
        { className: 'type-group', key: groupIndex },
        rows
      ) : false;
    }
  }, {
    key: 'render',
    value: function render() {
      var _this2 = this;

      var _props = this.props,
          assignmentTypes = _props.assignmentTypes,
          passingGrade = _props.passingGrade,
          percentGrade = _props.percentGrade;

      return __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
        'table',
        { className: 'table grade-table' },
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'thead',
          { className: 'table-head' },
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'tr',
            null,
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'th',
              null,
              'Assignment'
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'th',
              null,
              'Passing'
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'th',
              null,
              'You'
            )
          )
        ),
        assignmentTypes.map(function (type, index) {
          return _this2.getTableGroup(type, index);
        }),
        __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
          'tfoot',
          null,
          __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
            'tr',
            { className: 'totals' },
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'td',
              { className: 'footer-label' },
              'Total'
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'td',
              null,
              passingGrade,
              '%'
            ),
            __WEBPACK_IMPORTED_MODULE_0_react___default.a.createElement(
              'td',
              null,
              '*',
              percentGrade,
              '%'
            )
          )
        )
      );
    }
  }]);

  return GradeTable;
}(__WEBPACK_IMPORTED_MODULE_0_react___default.a.Component);

;

GradeTable.propTypes = {
  assignmentTypes: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.array.isRequired,
  grades: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.array.isRequired,
  passingGrade: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.number.isRequired,
  percentGrade: __WEBPACK_IMPORTED_MODULE_2_prop_types___default.a.number.isRequired
};

/* harmony default export */ __webpack_exports__["a"] = (GradeTable);

/***/ }),

/***/ "./lms/static/js/learner_analytics_dashboard/LearnerAnalyticsDashboard.jsx":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (immutable) */ __webpack_exports__["LearnerAnalyticsDashboard"] = LearnerAnalyticsDashboard;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types__ = __webpack_require__("./node_modules/prop-types/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_prop_types___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_prop_types__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react__ = __webpack_require__("./node_modules/react/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_react___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_react__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react_dom__ = __webpack_require__("./node_modules/react-dom/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_react_dom___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_react_dom__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_classnames__ = __webpack_require__("./node_modules/classnames/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_classnames___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_classnames__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__CircleChart__ = __webpack_require__("./lms/static/js/learner_analytics_dashboard/CircleChart.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__CircleChartLegend__ = __webpack_require__("./lms/static/js/learner_analytics_dashboard/CircleChartLegend.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__GradeTable__ = __webpack_require__("./lms/static/js/learner_analytics_dashboard/GradeTable.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__DueDates__ = __webpack_require__("./lms/static/js/learner_analytics_dashboard/DueDates.jsx");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__Discussions__ = __webpack_require__("./lms/static/js/learner_analytics_dashboard/Discussions.jsx");
var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

/* global gettext */











function arrayToObject(array) {
  return array.reduce(function (accumulator, obj) {
    var key = Object.keys(obj)[0];
    accumulator[key] = obj[key];
    return accumulator;
  }, {});
}

function countByType(type, assignments) {
  var count = 0;
  assignments.map(function (_ref) {
    var format = _ref.format;

    if (format === type) {
      count += 1;
    }
  });
  return count;
}

function getActiveUserString(count) {
  var users = count === 1 ? 'User' : 'Users';
  return users + ' active in this course right now';
}

function getAssignmentCounts(types, assignments) {
  var countsArray = types.map(function (type) {
    return _defineProperty({}, type, countByType(type, assignments));
  });

  return arrayToObject(countsArray);
}

function getStreakIcons(count) {
  return Array.apply(null, { length: count }).map(function (e, i) {
    return __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement('span', { className: 'fa fa-trophy', 'aria-hidden': 'true', key: i });
  });
}

function getStreakEncouragement(count) {
  var action = count > 0 ? 'Maintain' : 'Start';

  return action + ' your active streak by';
}

function getStreakString(count) {
  var unit = count === 1 ? 'week' : 'weeks';
  return count > 0 ? 'Active ' + count + ' ' + unit + ' in a row' : false;
}

function LearnerAnalyticsDashboard(props) {
  var grading_policy = props.grading_policy,
      grades = props.grades,
      schedule = props.schedule,
      schedule_raw = props.schedule_raw,
      week_streak = props.week_streak,
      weekly_active_users = props.weekly_active_users,
      discussion_info = props.discussion_info,
      profile_images = props.profile_images,
      passing_grade = props.passing_grade,
      percent_grade = props.percent_grade;

  var gradeBreakdown = grading_policy.GRADER.map(function (_ref3, index) {
    var type = _ref3.type,
        weight = _ref3.weight;

    return {
      value: weight,
      label: type,
      sliceIndex: index + 1
    };
  });

  // Get a list of assignment types minus duplicates
  var assignments = gradeBreakdown.map(function (value) {
    return value['label'];
  });
  var assignmentTypes = [].concat(_toConsumableArray(new Set(assignments)));
  var assignmentCounts = getAssignmentCounts(assignmentTypes, schedule);

  console.log(schedule_raw);
  console.log(grades);

  return __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
    'div',
    { className: 'learner-analytics-wrapper' },
    __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
      'div',
      { className: 'main-block' },
      __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
        'div',
        { className: 'analytics-group' },
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'h2',
          { className: 'group-heading' },
          'Grading'
        ),
        gradeBreakdown && __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'h3',
          { className: 'section-heading' },
          'Weight'
        ),
        gradeBreakdown && __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'div',
          { className: 'grading-weight-wrapper' },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'div',
            { className: 'chart-wrapper' },
            __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_4__CircleChart__["a" /* default */], {
              slices: gradeBreakdown,
              centerHole: true,
              sliceBorder: {
                strokeColor: '#f5f5f5',
                strokeWidth: 2
              }
            })
          ),
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_5__CircleChartLegend__["a" /* default */], { data: gradeBreakdown })
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'h3',
          { className: 'section-heading' },
          'Graded Assignments'
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'div',
          { className: 'graded-assessments-wrapper' },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_6__GradeTable__["a" /* default */], { assignmentTypes: assignmentTypes,
            grades: grades,
            passingGrade: passing_grade,
            percentGrade: percent_grade }),
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'div',
            { className: 'footnote' },
            '* Your current grade is calculated based on all assignments, including those you have not yet completed.'
          )
        )
      ),
      __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
        'div',
        { className: 'analytics-group' },
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(__WEBPACK_IMPORTED_MODULE_8__Discussions__["a" /* default */], _extends({}, discussion_info, { profileImages: profile_images }))
      )
    ),
    __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
      'div',
      { className: 'analytics-group sidebar week-streak' },
      __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
        'h2',
        { className: 'group-heading' },
        'Timing'
      ),
      __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
        'div',
        { className: 'week-streak-wrapper' },
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'h3',
          { className: 'section-heading' },
          'Week streak'
        ),
        week_streak > 0 && __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'div',
          { className: 'streak-icon-wrapper', 'aria-hidden': 'true' },
          getStreakIcons(week_streak)
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'p',
          null,
          getStreakString(week_streak)
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'p',
          { className: 'streak-encouragement' },
          getStreakEncouragement(week_streak)
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'ul',
          { className: 'streak-criteria' },
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'li',
            null,
            'Answering problems'
          ),
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'li',
            null,
            'Participating in discussions'
          ),
          __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
            'li',
            null,
            'Watching course videos'
          )
        )
      ),
      __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
        'div',
        { className: 'active-users-wrapper' },
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement('span', { className: 'fa fa-user count-icon', 'aria-hidden': 'true' }),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'span',
          { className: 'user-count' },
          weekly_active_users.toLocaleString('en', { useGrouping: true })
        ),
        __WEBPACK_IMPORTED_MODULE_1_react___default.a.createElement(
          'p',
          { className: 'label' },
          getActiveUserString(weekly_active_users)
        )
      )
    )
  );
}

/***/ })

},["./lms/static/js/learner_analytics_dashboard/LearnerAnalyticsDashboard.jsx"])));
//# sourceMappingURL=LearnerAnalyticsDashboard.js.map