(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([13,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74],{

/***/ "./cms/static/js/factories/edit_tabs.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (immutable) */ __webpack_exports__["default"] = EditTabsFactory;
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "EditTabsFactory", function() { return EditTabsFactory; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_js_models_explicit_url__ = __webpack_require__("./cms/static/js/models/explicit_url.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_js_models_explicit_url___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_js_models_explicit_url__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_views_tabs__ = __webpack_require__("./cms/static/js/views/tabs.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_views_tabs___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_js_views_tabs__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_xmodule__ = __webpack_require__("./cms/djangoapps/pipeline_js/js/xmodule.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_xmodule___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_xmodule__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__base__ = __webpack_require__("./cms/static/js/factories/base.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__base___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3__base__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_cms_js_main__ = __webpack_require__("./cms/static/cms/js/main.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_cms_js_main___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_cms_js_main__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_xblock_cms_runtime_v1__ = __webpack_require__("./cms/static/cms/js/xblock/cms.runtime.v1.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_xblock_cms_runtime_v1___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_5_xblock_cms_runtime_v1__);







'use strict';
function EditTabsFactory(courseLocation, explicitUrl) {
    __WEBPACK_IMPORTED_MODULE_2_xmodule__["done"](function () {
        var model = new __WEBPACK_IMPORTED_MODULE_0_js_models_explicit_url__({
            id: courseLocation,
            explicit_url: explicitUrl
        }),
            editView;

        editView = new __WEBPACK_IMPORTED_MODULE_1_js_views_tabs__({
            el: $('.tab-list'),
            model: model,
            mast: $('.wrapper-mast')
        });
    });
};


/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ "./cms/static/js/models/explicit_url.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * A model that simply allows the update URL to be passed
 * in as an argument.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2)], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone) {
    return Backbone.Model.extend({
        defaults: {
            explicit_url: ''
        },
        url: function url() {
            return this.get('explicit_url');
        }
    });
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/models/module_info.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__("./cms/static/js/utils/module.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, ModuleUtils) {
    var ModuleInfo = Backbone.Model.extend({
        urlRoot: ModuleUtils.urlRoot,

        defaults: {
            id: null,
            data: null,
            metadata: null,
            children: null
        }
    });
    return ModuleInfo;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/module_edit.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;(function () {
    'use strict';

    var __hasProp = {}.hasOwnProperty,
        __extends = function __extends(child, parent) {
        var key;
        for (key in parent) {
            if (__hasProp.call(parent, key)) {
                child[key] = parent[key];
            }
        }
        function Ctor() {
            this.constructor = child;
        }
        Ctor.prototype = parent.prototype;
        child.prototype = new Ctor();
        child.__super__ = parent.prototype;
        return child;
    };

    !(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./common/static/common/js/xblock/runtime.v1.js"), __webpack_require__("./cms/static/js/views/xblock.js"), __webpack_require__("./cms/static/js/views/modals/edit_xblock.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, gettext, XBlock, XBlockView, EditXBlockModal) {
        var ModuleEdit = function (_super) {
            __extends(ModuleEdit, _super);

            function ModuleEdit() {
                return ModuleEdit.__super__.constructor.apply(this, arguments);
            }

            ModuleEdit.prototype.tagName = 'li';

            ModuleEdit.prototype.className = 'component';

            ModuleEdit.prototype.editorMode = 'editor-mode';

            ModuleEdit.prototype.events = {
                'click .edit-button': 'clickEditButton',
                'click .delete-button': 'onDelete'
            };

            ModuleEdit.prototype.initialize = function () {
                this.onDelete = this.options.onDelete;
                return this.render();
            };

            ModuleEdit.prototype.loadDisplay = function () {
                var xblockElement;
                xblockElement = this.$el.find('.xblock-student_view');
                if (xblockElement.length > 0) {
                    return XBlock.initializeBlock(xblockElement);
                }
            };

            ModuleEdit.prototype.createItem = function (parent, payload, callback) {
                var _this = this;
                if (_.isNull(callback)) {
                    callback = function callback() {};
                }
                payload.parent_locator = parent;
                return $.postJSON(this.model.urlRoot + '/', payload, function (data) {
                    _this.model.set({
                        id: data.locator
                    });
                    _this.$el.data('locator', data.locator);
                    _this.$el.data('courseKey', data.courseKey);
                    return _this.render();
                }).success(callback);
            };

            ModuleEdit.prototype.loadView = function (viewName, target, callback) {
                var _this = this;
                if (this.model.id) {
                    return $.ajax({
                        url: '' + decodeURIComponent(this.model.url()) + '/' + viewName,
                        type: 'GET',
                        cache: false,
                        headers: {
                            Accept: 'application/json'
                        },
                        success: function success(fragment) {
                            return _this.renderXBlockFragment(fragment, target).done(callback);
                        }
                    });
                }
            };

            ModuleEdit.prototype.render = function () {
                var _this = this;
                return this.loadView('student_view', this.$el, function () {
                    _this.loadDisplay();
                    return _this.delegateEvents();
                });
            };

            ModuleEdit.prototype.clickEditButton = function (event) {
                var modal;
                event.preventDefault();
                modal = new EditXBlockModal();
                return modal.edit(this.$el, this.model, {
                    refresh: _.bind(this.render, this)
                });
            };

            return ModuleEdit;
        }(XBlockView);
        return ModuleEdit;
    }.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
}).call(this);

/***/ }),

/***/ "./cms/static/js/views/tabs.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/* globals analytics, course_location_analytics */

(function (analytics, course_location_analytics) {
    'use strict';

    var __hasProp = {}.hasOwnProperty,
        __extends = function __extends(child, parent) {
        var key;
        for (key in parent) {
            if (__hasProp.call(parent, key)) {
                child[key] = parent[key];
            }
        }
        function Ctor() {
            this.constructor = child;
        }
        Ctor.prototype = parent.prototype;
        child.prototype = new Ctor();
        child.__super__ = parent.prototype;
        return child;
    };

    !(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(1), __webpack_require__(0), __webpack_require__("./common/static/js/vendor/jquery-ui.min.js"), __webpack_require__(2), __webpack_require__("./common/static/common/js/components/views/feedback_prompt.js"), __webpack_require__("./common/static/common/js/components/views/feedback_notification.js"), __webpack_require__("./cms/static/js/views/module_edit.js"), __webpack_require__("./cms/static/js/models/module_info.js"), __webpack_require__("./cms/static/js/utils/module.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (_, $, ui, Backbone, PromptView, NotificationView, ModuleEditView, ModuleModel, ModuleUtils) {
        var TabsEdit;
        TabsEdit = function (_super) {
            __extends(TabsEdit, _super);

            function TabsEdit() {
                var self = this;
                this.deleteTab = function () {
                    return TabsEdit.prototype.deleteTab.apply(self, arguments);
                };
                this.addNewTab = function () {
                    return TabsEdit.prototype.addNewTab.apply(self, arguments);
                };
                this.tabMoved = function () {
                    return TabsEdit.prototype.tabMoved.apply(self, arguments);
                };
                this.toggleVisibilityOfTab = function () {
                    return TabsEdit.prototype.toggleVisibilityOfTab.apply(self, arguments);
                };
                this.initialize = function () {
                    return TabsEdit.prototype.initialize.apply(self, arguments);
                };
                return TabsEdit.__super__.constructor.apply(this, arguments);
            }

            TabsEdit.prototype.initialize = function (options) {
                var self = this;
                this.$('.component').each(function (idx, element) {
                    var model;
                    model = new ModuleModel({
                        id: $(element).data('locator')
                    });
                    return new ModuleEditView({
                        el: element,
                        onDelete: self.deleteTab,
                        model: model
                    });
                });
                this.options = _.extend({}, options);
                this.options.mast.find('.new-tab').on('click', this.addNewTab);
                $('.add-pages .new-tab').on('click', this.addNewTab);
                $('.toggle-checkbox').on('click', this.toggleVisibilityOfTab);
                return this.$('.course-nav-list').sortable({
                    handle: '.drag-handle',
                    update: this.tabMoved,
                    helper: 'clone',
                    opacity: '0.5',
                    placeholder: 'component-placeholder',
                    forcePlaceholderSize: true,
                    axis: 'y',
                    items: '> .is-movable'
                });
            };

            TabsEdit.prototype.toggleVisibilityOfTab = function (event) {
                var checkbox_element, saving, tab_element;
                checkbox_element = event.target;
                tab_element = $(checkbox_element).parents('.course-tab')[0];
                saving = new NotificationView.Mini({
                    title: gettext('Saving')
                });
                saving.show();
                return $.ajax({
                    type: 'POST',
                    url: this.model.url(),
                    data: JSON.stringify({
                        tab_id_locator: {
                            tab_id: $(tab_element).data('tab-id'),
                            tab_locator: $(tab_element).data('locator')
                        },
                        is_hidden: $(checkbox_element).is(':checked')
                    }),
                    contentType: 'application/json'
                }).success(function () {
                    return saving.hide();
                });
            };

            TabsEdit.prototype.tabMoved = function () {
                var saving, tabs;
                tabs = [];
                this.$('.course-tab').each(function (idx, element) {
                    return tabs.push({
                        tab_id: $(element).data('tab-id'),
                        tab_locator: $(element).data('locator')
                    });
                });
                analytics.track('Reordered Pages', {
                    course: course_location_analytics
                });
                saving = new NotificationView.Mini({
                    title: gettext('Saving')
                });
                saving.show();
                return $.ajax({
                    type: 'POST',
                    url: this.model.url(),
                    data: JSON.stringify({
                        tabs: tabs
                    }),
                    contentType: 'application/json'
                }).success(function () {
                    return saving.hide();
                });
            };

            TabsEdit.prototype.addNewTab = function (event) {
                var editor;
                event.preventDefault();
                editor = new ModuleEditView({
                    onDelete: this.deleteTab,
                    model: new ModuleModel()
                });
                $('.new-component-item').before(editor.$el);
                editor.$el.addClass('course-tab is-movable');
                editor.$el.addClass('new');
                setTimeout(function () {
                    return editor.$el.removeClass('new');
                }, 1000);
                $('html, body').animate({
                    scrollTop: $('.new-component-item').offset().top
                }, 500);
                editor.createItem(this.model.get('id'), {
                    category: 'static_tab'
                });
                return analytics.track('Added Page', {
                    course: course_location_analytics
                });
            };

            TabsEdit.prototype.deleteTab = function (event) {
                var confirm;
                confirm = new PromptView.Warning({
                    title: gettext('Delete Page Confirmation'),
                    message: gettext('Are you sure you want to delete this page? This action cannot be undone.'),
                    actions: {
                        primary: {
                            text: gettext('OK'),
                            click: function click(view) {
                                var $component, deleting;
                                view.hide();
                                $component = $(event.currentTarget).parents('.component');
                                analytics.track('Deleted Page', {
                                    course: course_location_analytics,
                                    id: $component.data('locator')
                                });
                                deleting = new NotificationView.Mini({
                                    title: gettext('Deleting')
                                });
                                deleting.show();
                                return $.ajax({
                                    type: 'DELETE',
                                    url: ModuleUtils.getUpdateUrl($component.data('locator'))
                                }).success(function () {
                                    $component.remove();
                                    return deleting.hide();
                                });
                            }
                        },
                        secondary: [{
                            text: gettext('Cancel'),
                            click: function click(view) {
                                return view.hide();
                            }
                        }]
                    }
                });
                return confirm.show();
            };

            return TabsEdit;
        }(Backbone.View);
        return TabsEdit;
    }.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
}).call(this, analytics, course_location_analytics);

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

/***/ }),

/***/ 4:
/***/ (function(module, exports) {

(function() { module.exports = window["URI"]; }());

/***/ })

},["./cms/static/js/factories/edit_tabs.js"])));
//# sourceMappingURL=edit_tabs.js.map