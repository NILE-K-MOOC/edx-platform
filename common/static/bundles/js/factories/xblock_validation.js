(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([19,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74],{

/***/ "./cms/static/js/factories/xblock_validation.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (immutable) */ __webpack_exports__["default"] = XBlockValidationFactory;
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "XBlockValidationFactory", function() { return XBlockValidationFactory; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_js_views_xblock_validation__ = __webpack_require__("./cms/static/js/views/xblock_validation.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_js_views_xblock_validation___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_js_views_xblock_validation__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_models_xblock_validation__ = __webpack_require__("./cms/static/js/models/xblock_validation.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_models_xblock_validation___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_js_models_xblock_validation__);




'use strict';
function XBlockValidationFactory(validationMessages, hasEditingUrl, isRoot, isUnit, validationEle) {
    var model, response;

    if (hasEditingUrl && !isRoot) {
        validationMessages.showSummaryOnly = true;
    }
    response = validationMessages;
    response.isUnit = isUnit;

    model = new __WEBPACK_IMPORTED_MODULE_1_js_models_xblock_validation__(response, { parse: true });

    if (!model.get('empty')) {
        new __WEBPACK_IMPORTED_MODULE_0_js_views_xblock_validation__({ el: validationEle, model: model, root: isRoot }).render();
    }
};



/***/ }),

/***/ "./cms/static/js/models/xblock_validation.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__(3), __webpack_require__(1)], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, gettext, _) {
    /**
     * Model for xblock validation messages as displayed in Studio.
     */
    var XBlockValidationModel = Backbone.Model.extend({
        defaults: {
            summary: {},
            messages: [],
            empty: true,
            xblock_id: null
        },

        WARNING: 'warning',
        ERROR: 'error',
        NOT_CONFIGURED: 'not-configured',

        parse: function parse(response) {
            if (!response.empty) {
                var summary = 'summary' in response ? response.summary : {};
                var messages = 'messages' in response ? response.messages : [];
                if (!summary.text) {
                    if (response.isUnit) {
                        summary.text = gettext('This unit has validation issues.');
                    } else {
                        summary.text = gettext('This component has validation issues.');
                    }
                }
                if (!summary.type) {
                    summary.type = this.WARNING;
                    // Possible types are ERROR, WARNING, and NOT_CONFIGURED. NOT_CONFIGURED is treated as a warning.
                    _.find(messages, function (message) {
                        if (message.type === this.ERROR) {
                            summary.type = this.ERROR;
                            return true;
                        }
                        return false;
                    }, this);
                }
                response.summary = summary;
                if (response.showSummaryOnly) {
                    messages = [];
                }
                response.messages = messages;
            }

            return response;
        }
    });
    return XBlockValidationModel;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/xblock_validation.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__(3)], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, BaseView, gettext) {
    /**
     * View for xblock validation messages as displayed in Studio.
     */
    var XBlockValidationView = BaseView.extend({

        // Takes XBlockValidationModel as a model
        initialize: function initialize(options) {
            BaseView.prototype.initialize.call(this);
            this.template = this.loadTemplate('xblock-validation-messages');
            this.root = options.root;
        },

        render: function render() {
            this.$el.html(this.template({
                validation: this.model,
                additionalClasses: this.getAdditionalClasses(),
                getIcon: this.getIcon.bind(this),
                getDisplayName: this.getDisplayName.bind(this)
            }));
            return this;
        },

        /**
         * Returns the icon css class based on the message type.
         * @param messageType
         * @returns string representation of css class that will render the correct icon, or null if unknown type
         */
        getIcon: function getIcon(messageType) {
            if (messageType === this.model.ERROR) {
                return 'fa-exclamation-circle';
            } else if (messageType === this.model.WARNING || messageType === this.model.NOT_CONFIGURED) {
                return 'fa-exclamation-triangle';
            }
            return null;
        },

        /**
         * Returns a display name for a message (useful for screen readers), based on the message type.
         * @param messageType
         * @returns string display name (translated)
         */
        getDisplayName: function getDisplayName(messageType) {
            if (messageType === this.model.WARNING || messageType === this.model.NOT_CONFIGURED) {
                // Translators: This message will be added to the front of messages of type warning,
                // e.g. "Warning: this component has not been configured yet".
                return gettext('Warning');
            } else if (messageType === this.model.ERROR) {
                // Translators: This message will be added to the front of messages of type error,
                // e.g. "Error: required field is missing".
                return gettext('Error');
            }
            return null;
        },

        /**
         * Returns additional css classes that can be added to HTML containing the validation messages.
         * Useful for rendering NOT_CONFIGURED in a special way.
         *
         * @returns string of additional css classes (or empty string)
         */
        getAdditionalClasses: function getAdditionalClasses() {
            if (this.root && this.model.get('summary').type === this.model.NOT_CONFIGURED && this.model.get('messages').length === 0) {
                return 'no-container-content';
            }
            return '';
        }
    });

    return XBlockValidationView;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ }),

/***/ 1:
/***/ (function(module, exports) {

(function() { module.exports = window["_"]; }());

/***/ }),

/***/ 2:
/***/ (function(module, exports) {

(function() { module.exports = window["Backbone"]; }());

/***/ }),

/***/ 3:
/***/ (function(module, exports) {

(function() { module.exports = window["gettext"]; }());

/***/ })

},["./cms/static/js/factories/xblock_validation.js"])));
//# sourceMappingURL=xblock_validation.js.map