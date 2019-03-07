(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([4,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74],{

/***/ "./cms/static/js/collections/component_template.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__("./cms/static/js/models/component_template.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, ComponentTemplate) {
    return Backbone.Collection.extend({
        model: ComponentTemplate
    });
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/factories/container.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (immutable) */ __webpack_exports__["default"] = ContainerFactory;
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ContainerFactory", function() { return ContainerFactory; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_underscore__ = __webpack_require__(1);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_underscore___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_underscore__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_js_models_xblock_container_info__ = __webpack_require__("./cms/static/js/models/xblock_container_info.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_js_models_xblock_container_info___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_js_models_xblock_container_info__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_js_views_pages_container__ = __webpack_require__("./cms/static/js/views/pages/container.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_js_views_pages_container___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_js_views_pages_container__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_js_collections_component_template__ = __webpack_require__("./cms/static/js/collections/component_template.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_js_collections_component_template___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_js_collections_component_template__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_xmodule__ = __webpack_require__("./cms/djangoapps/pipeline_js/js/xmodule.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_xmodule___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_5_xmodule__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__base__ = __webpack_require__("./cms/static/js/factories/base.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__base___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_6__base__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7_cms_js_main__ = __webpack_require__("./cms/static/cms/js/main.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7_cms_js_main___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_7_cms_js_main__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8_xblock_cms_runtime_v1__ = __webpack_require__("./cms/static/cms/js/xblock/cms.runtime.v1.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8_xblock_cms_runtime_v1___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_8_xblock_cms_runtime_v1__);










'use strict';
function ContainerFactory(componentTemplates, XBlockInfoJson, action, options) {
    var main_options = {
        el: __WEBPACK_IMPORTED_MODULE_0_jquery__('#content'),
        model: new __WEBPACK_IMPORTED_MODULE_2_js_models_xblock_container_info__(XBlockInfoJson, { parse: true }),
        action: action,
        templates: new __WEBPACK_IMPORTED_MODULE_4_js_collections_component_template__(componentTemplates, { parse: true })
    };

    __WEBPACK_IMPORTED_MODULE_5_xmodule__["done"](function () {
        var view = new __WEBPACK_IMPORTED_MODULE_3_js_views_pages_container__(__WEBPACK_IMPORTED_MODULE_1_underscore__["extend"](main_options, options));
        view.render();
    });
};



/***/ }),

/***/ "./cms/static/js/models/component_template.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Simple model for adding a component of a given type (for example, "video" or "html").
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2)], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone) {
    return Backbone.Model.extend({
        defaults: {
            type: '',
            // Each entry in the template array is an Object with the following keys:
            // display_name
            // category (may or may not match "type")
            // boilerplate_name (may be null)
            // is_common (only used for problems)
            templates: [],
            support_legend: {}
        },
        parse: function parse(response) {
            // Returns true only for templates that both have no boilerplate and are of
            // the overall type of the menu. This allows other component types to be added
            // and they will get sorted alphabetically rather than just at the top.
            // e.g. The ORA openassessment xblock is listed as an advanced problem.
            var isPrimaryBlankTemplate = function isPrimaryBlankTemplate(template) {
                return !template.boilerplate_name && template.category === response.type;
            };

            this.type = response.type;
            this.templates = response.templates;
            this.display_name = response.display_name;
            this.support_legend = response.support_legend;

            // Sort the templates.
            this.templates.sort(function (a, b) {
                // The blank problem for the current type goes first
                if (isPrimaryBlankTemplate(a)) {
                    return -1;
                } else if (isPrimaryBlankTemplate(b)) {
                    return 1;
                    // Hinted problems should be shown at the end
                } else if (a.hinted && !b.hinted) {
                    return 1;
                } else if (!a.hinted && b.hinted) {
                    return -1;
                } else if (a.display_name > b.display_name) {
                    return 1;
                } else if (a.display_name < b.display_name) {
                    return -1;
                }
                return 0;
            });
        }
    });
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/models/custom_sync_xblock_info.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/models/xblock_info.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (XBlockInfo) {
    var CustomSyncXBlockInfo = XBlockInfo.extend({
        sync: function sync(method, model, options) {
            options.url = (this.urlRoots[method] || this.urlRoot) + '/' + this.get('id');
            return XBlockInfo.prototype.sync.call(this, method, model, options);
        }
    });
    return CustomSyncXBlockInfo;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/models/xblock_container_info.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/models/custom_sync_xblock_info.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (CustomSyncXBlockInfo) {
    var XBlockContainerInfo = CustomSyncXBlockInfo.extend({
        urlRoots: {
            read: '/xblock/container'
        }
    });
    return XBlockContainerInfo;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/components/add_xblock.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * This is a simple component that renders add buttons for all available XBlock template types.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./common/static/common/js/components/utils/view_utils.js"), __webpack_require__("./cms/static/js/views/components/add_xblock_button.js"), __webpack_require__("./cms/static/js/views/components/add_xblock_menu.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, gettext, BaseView, ViewUtils, AddXBlockButton, AddXBlockMenu) {
    var AddXBlockComponent = BaseView.extend({
        events: {
            'click .new-component .new-component-type .multiple-templates': 'showComponentTemplates',
            'click .new-component .new-component-type .single-template': 'createNewComponent',
            'click .new-component .cancel-button': 'closeNewComponent',
            'click .new-component-templates .new-component-template .button-component': 'createNewComponent',
            'click .new-component-templates .cancel-button': 'closeNewComponent'
        },

        initialize: function initialize(options) {
            BaseView.prototype.initialize.call(this, options);
            this.template = this.loadTemplate('add-xblock-component');
        },

        render: function render() {
            if (!this.$el.html()) {
                var that = this;
                this.$el.html(this.template({}));
                this.collection.each(function (componentModel) {
                    var view, menu;

                    view = new AddXBlockButton({ model: componentModel });
                    that.$el.find('.new-component-type').append(view.render().el);

                    menu = new AddXBlockMenu({ model: componentModel });
                    that.$el.append(menu.render().el);
                });
            }
        },

        showComponentTemplates: function showComponentTemplates(event) {
            var type;
            event.preventDefault();
            event.stopPropagation();
            type = $(event.currentTarget).data('type');
            this.$('.new-component').slideUp(250);
            this.$('.new-component-' + type).slideDown(250);
            this.$('.new-component-' + type + ' div').focus();
        },

        closeNewComponent: function closeNewComponent(event) {
            event.preventDefault();
            event.stopPropagation();
            type = $(event.currentTarget).data('type');
            this.$('.new-component').slideDown(250);
            this.$('.new-component-templates').slideUp(250);
            this.$('ul.new-component-type li button[data-type=' + type + ']').focus();
        },

        createNewComponent: function createNewComponent(event) {
            var self = this,
                $element = $(event.currentTarget),
                saveData = $element.data(),
                oldOffset = ViewUtils.getScrollOffset(this.$el);
            event.preventDefault();
            this.closeNewComponent(event);
            ViewUtils.runOperationShowingMessage(gettext('Adding'), _.bind(this.options.createComponent, this, saveData, $element)).always(function () {
                // Restore the scroll position of the buttons so that the new
                // component appears above them.
                ViewUtils.setScrollOffset(self.$el, oldOffset);
            });
        }
    });

    return AddXBlockComponent;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/components/add_xblock_button.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/views/baseview.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (BaseView) {
    return BaseView.extend({
        tagName: 'li',
        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
            this.template = this.loadTemplate('add-xblock-component-button');
            this.$el.html(this.template({
                type: this.model.type,
                templates: this.model.templates,
                display_name: this.model.display_name
            }));
        }
    });
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/components/add_xblock_menu.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, BaseView, HtmlUtils) {
    return BaseView.extend({
        className: function className() {
            return 'new-component-templates new-component-' + this.model.type;
        },
        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
            var template_name = this.model.type === 'problem' ? 'add-xblock-component-menu-problem' : 'add-xblock-component-menu';
            var support_indicator_template = this.loadTemplate('add-xblock-component-support-level');
            var support_legend_template = this.loadTemplate('add-xblock-component-support-legend');
            this.template = this.loadTemplate(template_name);
            HtmlUtils.setHtml(this.$el, HtmlUtils.HTML(this.template({
                type: this.model.type, templates: this.model.templates,
                support_legend: this.model.support_legend,
                support_indicator_template: support_indicator_template,
                support_legend_template: support_legend_template,
                HtmlUtils: HtmlUtils
            })));
            // Make the tabs on problems into "real tabs"
            this.$('.tab-group').tabs();
        }
    });
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/container.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__("./cms/static/js/views/xblock.js"), __webpack_require__("./cms/static/js/utils/module.js"), __webpack_require__(3), __webpack_require__("./common/static/common/js/components/views/feedback_notification.js"), __webpack_require__("./common/static/js/vendor/jquery-ui.min.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, XBlockView, ModuleUtils, gettext, NotificationView) {
    'use strict';

    var studioXBlockWrapperClass = '.studio-xblock-wrapper';

    var ContainerView = XBlockView.extend({
        // Store the request token of the first xblock on the page (which we know was rendered by Studio when
        // the page was generated). Use that request token to filter out user-defined HTML in any
        // child xblocks within the page.
        requestToken: '',

        new_child_view: 'reorderable_container_child_preview',

        xblockReady: function xblockReady() {
            var reorderableClass,
                reorderableContainer,
                newParent,
                oldParent,
                self = this;
            XBlockView.prototype.xblockReady.call(this);

            this.requestToken = this.$('div.xblock').first().data('request-token');
            reorderableClass = this.makeRequestSpecificSelector('.reorderable-container');

            reorderableContainer = this.$(reorderableClass);
            reorderableContainer.sortable({
                handle: '.drag-handle',

                start: function start() {
                    // Necessary because of an open bug in JQuery sortable.
                    // http://bugs.jqueryui.com/ticket/4990
                    reorderableContainer.sortable('refreshPositions');
                },

                stop: function stop() {
                    var saving, hideSaving, removeFromParent;

                    if (_.isUndefined(oldParent)) {
                        // If no actual change occurred,
                        // oldParent will never have been set.
                        return;
                    }

                    saving = new NotificationView.Mini({
                        title: gettext('Saving')
                    });
                    saving.show();

                    hideSaving = function hideSaving() {
                        saving.hide();
                    };

                    // If moving from one container to another,
                    // add to new container before deleting from old to
                    // avoid creating an orphan if the addition fails.
                    if (newParent) {
                        removeFromParent = oldParent;
                        self.updateChildren(newParent, function () {
                            self.updateChildren(removeFromParent, hideSaving);
                        });
                    } else {
                        // No new parent, only reordering within same container.
                        self.updateChildren(oldParent, hideSaving);
                    }

                    oldParent = undefined;
                    newParent = undefined;
                },
                update: function update(event, ui) {
                    // When dragging from one ol to another, this method
                    // will be called twice (once for each list). ui.sender will
                    // be null if the change is related to the list the element
                    // was originally in (the case of a move within the same container
                    // or the deletion from a container when moving to a new container).
                    var parent = $(event.target).closest(studioXBlockWrapperClass);
                    if (ui.sender) {
                        // Move to a new container (the addition part).
                        newParent = parent;
                    } else {
                        // Reorder inside a container, or deletion when moving to new container.
                        oldParent = parent;
                    }
                },
                helper: 'original',
                opacity: '0.5',
                placeholder: 'component-placeholder',
                forcePlaceholderSize: true,
                axis: 'y',
                items: '> .is-draggable',
                connectWith: reorderableClass,
                tolerance: 'pointer'

            });
        },

        updateChildren: function updateChildren(targetParent, successCallback) {
            var children,
                childLocators,
                xblockInfo = this.model;

            // Find descendants with class "studio-xblock-wrapper" whose parent === targetParent.
            // This is necessary to filter our grandchildren, great-grandchildren, etc.
            children = targetParent.find(studioXBlockWrapperClass).filter(function () {
                var parent = $(this).parent().closest(studioXBlockWrapperClass);
                return parent.data('locator') === targetParent.data('locator');
            });

            childLocators = _.map(children, function (child) {
                return $(child).data('locator');
            });
            $.ajax({
                url: ModuleUtils.getUpdateUrl(targetParent.data('locator')),
                type: 'PUT',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({
                    children: childLocators
                }),
                success: function success() {
                    // change data-parent on the element moved.
                    if (successCallback) {
                        successCallback();
                    }
                    // Update publish and last modified information from the server.
                    xblockInfo.fetch();
                }
            });
        },

        acknowledgeXBlockDeletion: function acknowledgeXBlockDeletion(locator) {
            this.notifyRuntime('deleted-child', locator);
        },

        refresh: function refresh() {
            var sortableInitializedClass = this.makeRequestSpecificSelector('.reorderable-container.ui-sortable');
            this.$(sortableInitializedClass).sortable('refresh');
        },

        makeRequestSpecificSelector: function makeRequestSpecificSelector(selector) {
            return 'div.xblock[data-request-token="' + this.requestToken + '"] > ' + selector;
        }
    });

    return ContainerView;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/modals/move_xblock_modal.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * The MoveXblockModal to move XBlocks in course.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(2), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./cms/static/js/views/utils/xblock_utils.js"), __webpack_require__("./cms/static/js/views/utils/move_xblock_utils.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js"), __webpack_require__("./common/static/common/js/components/views/feedback.js"), __webpack_require__("./cms/static/js/models/xblock_info.js"), __webpack_require__("./cms/static/js/views/modals/base_modal.js"), __webpack_require__("./cms/static/js/views/move_xblock_list.js"), __webpack_require__("./cms/static/js/views/move_xblock_breadcrumb.js"), __webpack_require__("./cms/templates/js/move-xblock-modal.underscore")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, Backbone, _, gettext, BaseView, XBlockViewUtils, MoveXBlockUtils, HtmlUtils, StringUtils, Feedback, XBlockInfoModel, BaseModal, MoveXBlockListView, MoveXBlockBreadcrumbView, MoveXblockModalTemplate) {
    'use strict';

    var MoveXblockModal = BaseModal.extend({
        events: _.extend({}, BaseModal.prototype.events, {
            'click .action-move:not(.is-disabled)': 'moveXBlock'
        }),

        options: $.extend({}, BaseModal.prototype.options, {
            modalName: 'move-xblock',
            modalSize: 'lg',
            showEditorModeButtons: false,
            addPrimaryActionButton: true,
            primaryActionButtonType: 'move',
            viewSpecificClasses: 'move-modal',
            primaryActionButtonTitle: gettext('Move'),
            modalSRTitle: gettext('Choose a location to move your component to')
        }),

        initialize: function initialize() {
            var self = this;
            BaseModal.prototype.initialize.call(this);
            this.sourceXBlockInfo = this.options.sourceXBlockInfo;
            this.sourceParentXBlockInfo = this.options.sourceParentXBlockInfo;
            this.targetParentXBlockInfo = null;
            this.XBlockURLRoot = this.options.XBlockURLRoot;
            this.XBlockAncestorInfoURL = StringUtils.interpolate('{urlRoot}/{usageId}?fields=ancestorInfo', { urlRoot: this.XBlockURLRoot, usageId: this.sourceXBlockInfo.get('id') });
            this.outlineURL = this.options.outlineURL;
            this.options.title = this.getTitle();
            this.fetchCourseOutline().done(function (courseOutlineInfo, ancestorInfo) {
                $('.ui-loading').addClass('is-hidden');
                $('.breadcrumb-container').removeClass('is-hidden');
                self.renderViews(courseOutlineInfo, ancestorInfo);
            });
            this.listenTo(Backbone, 'move:breadcrumbRendered', this.focusModal);
            this.listenTo(Backbone, 'move:enableMoveOperation', this.enableMoveOperation);
            this.listenTo(Backbone, 'move:hideMoveModal', this.hide);
        },

        getTitle: function getTitle() {
            return StringUtils.interpolate(gettext('Move: {displayName}'), { displayName: this.sourceXBlockInfo.get('display_name') });
        },

        getContentHtml: function getContentHtml() {
            return _.template(MoveXblockModalTemplate)({});
        },

        show: function show() {
            BaseModal.prototype.show.apply(this, [false]);
            this.updateMoveState(false);
            MoveXBlockUtils.hideMovedNotification();
        },

        hide: function hide() {
            if (this.moveXBlockListView) {
                this.moveXBlockListView.remove();
            }
            if (this.moveXBlockBreadcrumbView) {
                this.moveXBlockBreadcrumbView.remove();
            }
            BaseModal.prototype.hide.apply(this);
            Feedback.prototype.outFocus.apply(this);
        },

        resize: function resize() {
            // Do Nothing. Overridden to use our own styling instead of one provided by base modal
        },

        focusModal: function focusModal() {
            Feedback.prototype.inFocus.apply(this, [this.options.modalWindowClass]);
            $(this.options.modalWindowClass).focus();
        },

        fetchCourseOutline: function fetchCourseOutline() {
            return $.when(this.fetchData(this.outlineURL), this.fetchData(this.XBlockAncestorInfoURL));
        },

        fetchData: function fetchData(url) {
            var deferred = $.Deferred();
            $.ajax({
                url: url,
                contentType: 'application/json',
                dataType: 'json',
                type: 'GET'
            }).done(function (data) {
                deferred.resolve(data);
            }).fail(function () {
                deferred.reject();
            });
            return deferred.promise();
        },

        renderViews: function renderViews(courseOutlineInfo, ancestorInfo) {
            this.moveXBlockBreadcrumbView = new MoveXBlockBreadcrumbView({});
            this.moveXBlockListView = new MoveXBlockListView({
                model: new XBlockInfoModel(courseOutlineInfo, { parse: true }),
                sourceXBlockInfo: this.sourceXBlockInfo,
                ancestorInfo: ancestorInfo
            });
        },

        updateMoveState: function updateMoveState(isValidMove) {
            var $moveButton = this.$el.find('.action-move');
            if (isValidMove) {
                $moveButton.removeClass('is-disabled');
            } else {
                $moveButton.addClass('is-disabled');
            }
        },

        isValidCategory: function isValidCategory(targetParentXBlockInfo) {
            var basicBlockTypes = ['course', 'chapter', 'sequential', 'vertical'],
                sourceParentType = this.sourceParentXBlockInfo.get('category'),
                targetParentType = targetParentXBlockInfo.get('category'),
                sourceParentHasChildren = this.sourceParentXBlockInfo.get('has_children'),
                targetParentHasChildren = targetParentXBlockInfo.get('has_children');

            // Treat source parent component as vertical to support move child components under content experiment
            // and other similar xblocks.
            if (sourceParentHasChildren && !_.contains(basicBlockTypes, sourceParentType)) {
                sourceParentType = 'vertical'; // eslint-disable-line no-param-reassign
            }

            // Treat target parent component as a vertical to support move to parentable target parent components.
            // Also, moving a component directly to content experiment is not allowed, we need to visit to group level.
            if (targetParentHasChildren && !_.contains(basicBlockTypes, targetParentType) && targetParentType !== 'split_test') {
                targetParentType = 'vertical'; // eslint-disable-line no-param-reassign
            }
            return targetParentType === sourceParentType;
        },

        enableMoveOperation: function enableMoveOperation(targetParentXBlockInfo) {
            var isValidMove = false;

            // update target parent on navigation
            this.targetParentXBlockInfo = targetParentXBlockInfo;
            if (this.isValidCategory(targetParentXBlockInfo) && this.sourceParentXBlockInfo.id !== targetParentXBlockInfo.id && // same parent case
            this.sourceXBlockInfo.id !== targetParentXBlockInfo.id) {
                // same source item case
                isValidMove = true;
            }
            this.updateMoveState(isValidMove);
        },

        moveXBlock: function moveXBlock() {
            MoveXBlockUtils.moveXBlock({
                sourceXBlockElement: $("li.studio-xblock-wrapper[data-locator='" + this.sourceXBlockInfo.id + "']"),
                sourceDisplayName: this.sourceXBlockInfo.get('display_name'),
                sourceLocator: this.sourceXBlockInfo.id,
                sourceParentLocator: this.sourceParentXBlockInfo.id,
                targetParentLocator: this.targetParentXBlockInfo.id
            });
        }
    });

    return MoveXblockModal;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/move_xblock_breadcrumb.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * MoveXBlockBreadcrumb show breadcrumbs to move back to parent.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(2), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js"), __webpack_require__("./cms/templates/js/move-xblock-breadcrumb.underscore")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, Backbone, _, gettext, HtmlUtils, StringUtils, MoveXBlockBreadcrumbViewTemplate) {
    'use strict';

    var MoveXBlockBreadcrumb = Backbone.View.extend({
        el: '.breadcrumb-container',

        events: {
            'click .parent-nav-button': 'handleBreadcrumbButtonPress'
        },

        initialize: function initialize() {
            this.template = HtmlUtils.template(MoveXBlockBreadcrumbViewTemplate);
            this.listenTo(Backbone, 'move:childrenRendered', this.render);
        },

        render: function render(options) {
            HtmlUtils.setHtml(this.$el, this.template(options));
            Backbone.trigger('move:breadcrumbRendered');
            return this;
        },

        /**
         * Event handler for breadcrumb button press.
         *
         * @param {Object} event
         */
        handleBreadcrumbButtonPress: function handleBreadcrumbButtonPress(event) {
            Backbone.trigger('move:breadcrumbButtonPressed', $(event.target).data('parentIndex'));
        }
    });

    return MoveXBlockBreadcrumb;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/move_xblock_list.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * XBlockListView shows list of XBlocks in a particular category(section, subsection, vertical etc).
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(2), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js"), __webpack_require__("./cms/static/js/views/utils/xblock_utils.js"), __webpack_require__("./cms/templates/js/move-xblock-list.underscore")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, Backbone, _, gettext, HtmlUtils, StringUtils, XBlockUtils, MoveXBlockListViewTemplate) {
    'use strict';

    var XBlockListView = Backbone.View.extend({
        el: '.xblock-list-container',

        // parent info of currently displayed children
        parentInfo: {},
        // currently displayed children XBlocks info
        childrenInfo: {},
        // list of visited parent XBlocks, needed for backward navigation
        visitedAncestors: null,

        // parent to child relation map
        categoryRelationMap: {
            course: 'section',
            section: 'subsection',
            subsection: 'unit',
            unit: 'component'
        },

        categoriesText: {
            section: gettext('Sections'),
            subsection: gettext('Subsections'),
            unit: gettext('Units'),
            component: gettext('Components'),
            group: gettext('Groups')
        },

        events: {
            'click .button-forward': 'renderChildren'
        },

        initialize: function initialize(options) {
            this.visitedAncestors = [];
            this.template = HtmlUtils.template(MoveXBlockListViewTemplate);
            this.sourceXBlockInfo = options.sourceXBlockInfo;
            this.ancestorInfo = options.ancestorInfo;
            this.listenTo(Backbone, 'move:breadcrumbButtonPressed', this.handleBreadcrumbButtonPress);
            this.renderXBlockInfo();
        },

        render: function render() {
            HtmlUtils.setHtml(this.$el, this.template({
                sourceXBlockId: this.sourceXBlockInfo.id,
                xblocks: this.childrenInfo.children,
                noChildText: this.getNoChildText(),
                categoryText: this.getCategoryText(),
                parentDisplayname: this.parentInfo.parent.get('display_name'),
                XBlocksCategory: this.childrenInfo.category,
                currentLocationIndex: this.getCurrentLocationIndex()
            }));
            Backbone.trigger('move:childrenRendered', this.breadcrumbInfo());
            Backbone.trigger('move:enableMoveOperation', this.parentInfo.parent);
            return this;
        },

        /**
         * Forward button press handler. This will render all the childs of an XBlock.
         *
         * @param {Object} event
         */
        renderChildren: function renderChildren(event) {
            this.renderXBlockInfo('forward', $(event.target).closest('.xblock-item').data('itemIndex'));
        },

        /**
         * Breadcrumb button press event handler. Render all the childs of an XBlock.
         *
         * @param {any} newParentIndex  Index of a parent XBlock
         */
        handleBreadcrumbButtonPress: function handleBreadcrumbButtonPress(newParentIndex) {
            this.renderXBlockInfo('backward', newParentIndex);
        },

        /**
         * Render XBlocks based on `forward` or `backward` navigation.
         *
         * @param {any} direction           `forward` or `backward`
         * @param {any} newParentIndex      Index of a parent XBlock
         */
        renderXBlockInfo: function renderXBlockInfo(direction, newParentIndex) {
            if (direction === undefined) {
                this.parentInfo.parent = this.model;
            } else if (direction === 'forward') {
                // clicked child is the new parent
                this.parentInfo.parent = this.childrenInfo.children[newParentIndex];
            } else if (direction === 'backward') {
                // new parent will be one of visitedAncestors
                this.parentInfo.parent = this.visitedAncestors[newParentIndex];
                // remove visited ancestors
                this.visitedAncestors.splice(newParentIndex);
            }

            this.visitedAncestors.push(this.parentInfo.parent);

            if (this.parentInfo.parent.get('child_info')) {
                this.childrenInfo.children = this.parentInfo.parent.get('child_info').children;
            } else {
                this.childrenInfo.children = [];
            }

            this.setDisplayedXBlocksCategories();
            this.render();
        },

        /**
         * Set parent and child XBlock categories.
         */
        setDisplayedXBlocksCategories: function setDisplayedXBlocksCategories() {
            var childCategory = 'component';
            this.parentInfo.category = XBlockUtils.getXBlockType(this.parentInfo.parent.get('category'));
            if (!_.contains(_.keys(this.categoryRelationMap), this.parentInfo.category)) {
                if (this.parentInfo.category === 'split_test') {
                    childCategory = 'group'; // This is just to show groups text on group listing.
                }
                this.categoryRelationMap[this.parentInfo.category] = childCategory;
            }
            this.childrenInfo.category = this.categoryRelationMap[this.parentInfo.category];
        },

        /**
         * Get index of source XBlock.
         *
         * @returns {any} Integer or undefined
         */
        getCurrentLocationIndex: function getCurrentLocationIndex() {
            var self = this,
                currentLocationIndex;
            _.each(self.childrenInfo.children, function (xblock, index) {
                if (xblock.get('id') === self.sourceXBlockInfo.id) {
                    currentLocationIndex = index;
                } else {
                    _.each(self.ancestorInfo.ancestors, function (ancestor) {
                        if (ancestor.display_name === xblock.get('display_name') && ancestor.id === xblock.get('id')) {
                            currentLocationIndex = index;
                        }
                    });
                }
            });

            return currentLocationIndex;
        },

        /**
         * Get category text for currently displayed children.
         *
         * @returns {String}
         */
        getCategoryText: function getCategoryText() {
            return this.categoriesText[this.childrenInfo.category];
        },

        /**
         * Get text when a parent XBlock has no children.
         *
         * @returns {String}
         */
        getNoChildText: function getNoChildText() {
            return StringUtils.interpolate(gettext('This {parentCategory} has no {childCategory}'), {
                parentCategory: this.parentInfo.category,
                childCategory: this.categoriesText[this.childrenInfo.category].toLowerCase()
            });
        },

        /**
         * Construct breadcurmb info.
         *
         * @returns {Object}
         */
        breadcrumbInfo: function breadcrumbInfo() {
            return {
                breadcrumbs: _.map(this.visitedAncestors, function (ancestor) {
                    return ancestor.get('category') === 'course' ? gettext('Course Outline') : ancestor.get('display_name');
                })
            };
        }
    });

    return XBlockListView;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/pages/base_page.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * This is the base view that all Studio pages extend from.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__("./cms/static/js/views/baseview.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, BaseView) {
    var BasePage = BaseView.extend({

        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
        },

        /**
         * Returns true if this page is currently showing any content. If this returns false
         * then the page will unhide the div with the class 'no-content'.
         */
        hasContent: function hasContent() {
            return true;
        },

        /**
         * This renders the page's content and returns a promise that will be resolved once
         * the rendering has completed.
         * @returns {jQuery promise} A promise representing the rendering of the page.
         */
        renderPage: function renderPage() {
            return $.Deferred().resolve().promise();
        },

        /**
         * Renders the current page while showing a loading indicator. Note that subclasses
         * of BasePage should implement renderPage to perform the rendering of the content.
         * If the page has no content (i.e. it returns false for hasContent) then the
         * div with the class 'no-content' will be shown.
         */
        render: function render() {
            var self = this;
            this.$('.ui-loading').removeClass('is-hidden');
            this.renderPage().done(function () {
                if (!self.hasContent()) {
                    self.$('.no-content').removeClass('is-hidden');
                }
            }).always(function () {
                self.$('.ui-loading').addClass('is-hidden');
            });
            return this;
        }
    });

    return BasePage;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/pages/container.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * XBlockContainerPage is used to display Studio's container page for an xblock which has children.
 * This page allows the user to understand and manipulate the xblock and its children.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__(2), __webpack_require__(3), __webpack_require__("./cms/static/js/views/pages/base_page.js"), __webpack_require__("./common/static/common/js/components/utils/view_utils.js"), __webpack_require__("./cms/static/js/views/container.js"), __webpack_require__("./cms/static/js/views/xblock.js"), __webpack_require__("./cms/static/js/views/components/add_xblock.js"), __webpack_require__("./cms/static/js/views/modals/edit_xblock.js"), __webpack_require__("./cms/static/js/views/modals/move_xblock_modal.js"), __webpack_require__("./cms/static/js/models/xblock_info.js"), __webpack_require__("./cms/static/js/views/xblock_string_field_editor.js"), __webpack_require__("./cms/static/js/views/xblock_access_editor.js"), __webpack_require__("./cms/static/js/views/pages/container_subviews.js"), __webpack_require__("./cms/static/js/views/unit_outline.js"), __webpack_require__("./cms/static/js/views/utils/xblock_utils.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, Backbone, gettext, BasePage, ViewUtils, ContainerView, XBlockView, AddXBlockComponent, EditXBlockModal, MoveXBlockModal, XBlockInfo, XBlockStringFieldEditor, XBlockAccessEditor, ContainerSubviews, UnitOutlineView, XBlockUtils) {
    'use strict';

    var XBlockContainerPage = BasePage.extend({
        // takes XBlockInfo as a model

        events: {
            'click .edit-button': 'editXBlock',
            'click .access-button': 'editVisibilitySettings',
            'click .duplicate-button': 'duplicateXBlock',
            'click .move-button': 'showMoveXBlockModal',
            'click .delete-button': 'deleteXBlock',
            'click .new-component-button': 'scrollToNewComponentButtons'
        },

        options: {
            collapsedClass: 'is-collapsed',
            canEdit: true // If not specified, assume user has permission to make changes
        },

        view: 'container_preview',

        defaultViewClass: ContainerView,

        // Overridable by subclasses-- determines whether the XBlock component
        // addition menu is added on initialization. You may set this to false
        // if your subclass handles it.
        components_on_init: true,

        initialize: function initialize(options) {
            BasePage.prototype.initialize.call(this, options);
            this.viewClass = options.viewClass || this.defaultViewClass;
            this.isLibraryPage = this.model.attributes.category === 'library';
            this.nameEditor = new XBlockStringFieldEditor({
                el: this.$('.wrapper-xblock-field'),
                model: this.model
            });
            this.nameEditor.render();
            if (!this.isLibraryPage) {
                this.accessEditor = new XBlockAccessEditor({
                    el: this.$('.wrapper-xblock-field')
                });
                this.accessEditor.render();
            }
            if (this.options.action === 'new') {
                this.nameEditor.$('.xblock-field-value-edit').click();
            }
            this.xblockView = this.getXBlockView();
            this.messageView = new ContainerSubviews.MessageView({
                el: this.$('.container-message'),
                model: this.model
            });
            this.messageView.render();
            // Display access message on units and split test components
            if (!this.isLibraryPage) {
                this.containerAccessView = new ContainerSubviews.ContainerAccess({
                    el: this.$('.container-access'),
                    model: this.model
                });
                this.containerAccessView.render();

                this.xblockPublisher = new ContainerSubviews.Publisher({
                    el: this.$('#publish-unit'),
                    model: this.model,
                    // When "Discard Changes" is clicked, the whole page must be re-rendered.
                    renderPage: this.render
                });
                this.xblockPublisher.render();

                this.publishHistory = new ContainerSubviews.PublishHistory({
                    el: this.$('#publish-history'),
                    model: this.model
                });
                this.publishHistory.render();

                this.viewLiveActions = new ContainerSubviews.ViewLiveButtonController({
                    el: this.$('.nav-actions'),
                    model: this.model
                });
                this.viewLiveActions.render();

                this.unitOutlineView = new UnitOutlineView({
                    el: this.$('.wrapper-unit-overview'),
                    model: this.model
                });
                this.unitOutlineView.render();
            }

            this.listenTo(Backbone, 'move:onXBlockMoved', this.onXBlockMoved);
        },

        getViewParameters: function getViewParameters() {
            return {
                el: this.$('.wrapper-xblock'),
                model: this.model,
                view: this.view
            };
        },

        getXBlockView: function getXBlockView() {
            return new this.viewClass(this.getViewParameters());
        },

        render: function render(options) {
            var self = this,
                xblockView = this.xblockView,
                loadingElement = this.$('.ui-loading'),
                unitLocationTree = this.$('.unit-location'),
                hiddenCss = 'is-hidden';

            loadingElement.removeClass(hiddenCss);

            // Hide both blocks until we know which one to show
            xblockView.$el.addClass(hiddenCss);

            // Render the xblock
            xblockView.render({
                done: function done() {
                    // Show the xblock and hide the loading indicator
                    xblockView.$el.removeClass(hiddenCss);
                    loadingElement.addClass(hiddenCss);

                    // Notify the runtime that the page has been successfully shown
                    xblockView.notifyRuntime('page-shown', self);

                    if (self.components_on_init) {
                        // Render the add buttons. Paged containers should do this on their own.
                        self.renderAddXBlockComponents();
                    }

                    // Refresh the views now that the xblock is visible
                    self.onXBlockRefresh(xblockView);
                    unitLocationTree.removeClass(hiddenCss);

                    // Re-enable Backbone events for any updated DOM elements
                    self.delegateEvents();
                },
                block_added: options && options.block_added
            });
        },

        findXBlockElement: function findXBlockElement(target) {
            return $(target).closest('.studio-xblock-wrapper');
        },

        getURLRoot: function getURLRoot() {
            return this.xblockView.model.urlRoot;
        },

        onXBlockRefresh: function onXBlockRefresh(xblockView, block_added, is_duplicate) {
            this.xblockView.refresh(xblockView, block_added, is_duplicate);
            // Update publish and last modified information from the server.
            this.model.fetch();
        },

        renderAddXBlockComponents: function renderAddXBlockComponents() {
            var self = this;
            if (self.options.canEdit) {
                this.$('.add-xblock-component').each(function (index, element) {
                    var component = new AddXBlockComponent({
                        el: element,
                        createComponent: _.bind(self.createComponent, self),
                        collection: self.options.templates
                    });
                    component.render();
                });
            } else {
                this.$('.add-xblock-component').remove();
            }
        },

        editXBlock: function editXBlock(event, options) {
            var xblockElement = this.findXBlockElement(event.target),
                self = this,
                modal = new EditXBlockModal(options);
            event.preventDefault();

            modal.edit(xblockElement, this.model, {
                readOnlyView: !this.options.canEdit,
                refresh: function refresh() {
                    self.refreshXBlock(xblockElement, false);
                }
            });
        },

        editVisibilitySettings: function editVisibilitySettings(event) {
            this.editXBlock(event, {
                view: 'visibility_view',
                // Translators: "title" is the name of the current component or unit being edited.
                titleFormat: gettext('Editing access for: %(title)s'),
                viewSpecificClasses: '',
                modalSize: 'med'
            });
        },

        duplicateXBlock: function duplicateXBlock(event) {
            event.preventDefault();
            this.duplicateComponent(this.findXBlockElement(event.target));
        },

        showMoveXBlockModal: function showMoveXBlockModal(event) {
            var xblockElement = this.findXBlockElement(event.target),
                parentXBlockElement = xblockElement.parents('.studio-xblock-wrapper'),
                modal = new MoveXBlockModal({
                sourceXBlockInfo: XBlockUtils.findXBlockInfo(xblockElement, this.model),
                sourceParentXBlockInfo: XBlockUtils.findXBlockInfo(parentXBlockElement, this.model),
                XBlockURLRoot: this.getURLRoot(),
                outlineURL: this.options.outlineURL
            });

            event.preventDefault();
            modal.show();
        },

        deleteXBlock: function deleteXBlock(event) {
            event.preventDefault();
            this.deleteComponent(this.findXBlockElement(event.target));
        },

        createPlaceholderElement: function createPlaceholderElement() {
            return $('<div/>', { class: 'studio-xblock-wrapper' });
        },

        createComponent: function createComponent(template, target) {
            // A placeholder element is created in the correct location for the new xblock
            // and then onNewXBlock will replace it with a rendering of the xblock. Note that
            // for xblocks that can't be replaced inline, the entire parent will be refreshed.
            var parentElement = this.findXBlockElement(target),
                parentLocator = parentElement.data('locator'),
                buttonPanel = target.closest('.add-xblock-component'),
                listPanel = buttonPanel.prev(),
                scrollOffset = ViewUtils.getScrollOffset(buttonPanel),
                $placeholderEl = $(this.createPlaceholderElement()),
                requestData = _.extend(template, {
                parent_locator: parentLocator
            }),
                placeholderElement;
            placeholderElement = $placeholderEl.appendTo(listPanel);
            return $.postJSON(this.getURLRoot() + '/', requestData, _.bind(this.onNewXBlock, this, placeholderElement, scrollOffset, false)).fail(function () {
                // Remove the placeholder if the update failed
                placeholderElement.remove();
            });
        },

        duplicateComponent: function duplicateComponent(xblockElement) {
            // A placeholder element is created in the correct location for the duplicate xblock
            // and then onNewXBlock will replace it with a rendering of the xblock. Note that
            // for xblocks that can't be replaced inline, the entire parent will be refreshed.
            var self = this,
                parentElement = self.findXBlockElement(xblockElement.parent()),
                scrollOffset = ViewUtils.getScrollOffset(xblockElement),
                $placeholderEl = $(self.createPlaceholderElement()),
                placeholderElement;

            placeholderElement = $placeholderEl.insertAfter(xblockElement);
            XBlockUtils.duplicateXBlock(xblockElement, parentElement).done(function (data) {
                self.onNewXBlock(placeholderElement, scrollOffset, true, data);
            }).fail(function () {
                // Remove the placeholder if the update failed
                placeholderElement.remove();
            });
        },

        deleteComponent: function deleteComponent(xblockElement) {
            var self = this,
                xblockInfo = new XBlockInfo({
                id: xblockElement.data('locator')
            });
            XBlockUtils.deleteXBlock(xblockInfo).done(function () {
                self.onDelete(xblockElement);
            });
        },

        onDelete: function onDelete(xblockElement) {
            // get the parent so we can remove this component from its parent.
            var xblockView = this.xblockView,
                parent = this.findXBlockElement(xblockElement.parent());
            xblockElement.remove();

            // Inform the runtime that the child has been deleted in case
            // other views are listening to deletion events.
            xblockView.acknowledgeXBlockDeletion(parent.data('locator'));

            // Update publish and last modified information from the server.
            this.model.fetch();
        },

        /*
        After move operation is complete, updates the xblock information from server .
         */
        onXBlockMoved: function onXBlockMoved() {
            this.model.fetch();
        },

        onNewXBlock: function onNewXBlock(xblockElement, scrollOffset, is_duplicate, data) {
            ViewUtils.setScrollOffset(xblockElement, scrollOffset);
            xblockElement.data('locator', data.locator);
            return this.refreshXBlock(xblockElement, true, is_duplicate);
        },

        /**
         * Refreshes the specified xblock's display. If the xblock is an inline child of a
         * reorderable container then the element will be refreshed inline. If not, then the
         * parent container will be refreshed instead.
         * @param element An element representing the xblock to be refreshed.
         * @param block_added Flag to indicate that new block has been just added.
         */
        refreshXBlock: function refreshXBlock(element, block_added, is_duplicate) {
            var xblockElement = this.findXBlockElement(element),
                parentElement = xblockElement.parent(),
                rootLocator = this.xblockView.model.id;
            if (xblockElement.length === 0 || xblockElement.data('locator') === rootLocator) {
                this.render({ refresh: true, block_added: block_added });
            } else if (parentElement.hasClass('reorderable-container')) {
                this.refreshChildXBlock(xblockElement, block_added, is_duplicate);
            } else {
                this.refreshXBlock(this.findXBlockElement(parentElement));
            }
        },

        /**
         * Refresh an xblock element inline on the page, using the specified xblockInfo.
         * Note that the element is removed and replaced with the newly rendered xblock.
         * @param xblockElement The xblock element to be refreshed.
         * @param block_added Specifies if a block has been added, rather than just needs
         * refreshing.
         * @returns {jQuery promise} A promise representing the complete operation.
         */
        refreshChildXBlock: function refreshChildXBlock(xblockElement, block_added, is_duplicate) {
            var self = this,
                xblockInfo,
                TemporaryXBlockView,
                temporaryView;
            xblockInfo = new XBlockInfo({
                id: xblockElement.data('locator')
            });
            // There is only one Backbone view created on the container page, which is
            // for the container xblock itself. Any child xblocks rendered inside the
            // container do not get a Backbone view. Thus, create a temporary view
            // to render the content, and then replace the original element with the result.
            TemporaryXBlockView = XBlockView.extend({
                updateHtml: function updateHtml(element, html) {
                    // Replace the element with the new HTML content, rather than adding
                    // it as child elements.
                    this.$el = $(html).replaceAll(element); // xss-lint: disable=javascript-jquery-insertion
                }
            });
            temporaryView = new TemporaryXBlockView({
                model: xblockInfo,
                view: self.xblockView.new_child_view,
                el: xblockElement
            });
            return temporaryView.render({
                success: function success() {
                    self.onXBlockRefresh(temporaryView, block_added, is_duplicate);
                    temporaryView.unbind(); // Remove the temporary view
                },
                initRuntimeData: this
            });
        },

        scrollToNewComponentButtons: function scrollToNewComponentButtons(event) {
            event.preventDefault();
            $.scrollTo(this.$('.add-xblock-component'), { duration: 250 });
        }
    });

    return XBlockContainerPage;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/pages/container_subviews.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Subviews (usually small side panels) for XBlockContainerPage.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./common/static/common/js/components/utils/view_utils.js"), __webpack_require__("./cms/static/js/views/utils/xblock_utils.js"), __webpack_require__("./cms/static/js/views/utils/move_xblock_utils.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, gettext, BaseView, ViewUtils, XBlockViewUtils, MoveXBlockUtils, HtmlUtils) {
    'use strict';

    var disabledCss = 'is-disabled';

    /**
     * A view that refreshes the view when certain values in the XBlockInfo have changed
     * after a server sync operation.
     */
    var ContainerStateListenerView = BaseView.extend({

        // takes XBlockInfo as a model
        initialize: function initialize() {
            this.model.on('sync', this.onSync, this);
        },

        onSync: function onSync(model) {
            if (this.shouldRefresh(model)) {
                this.render();
            }
        },

        shouldRefresh: function shouldRefresh(model) {
            return false;
        },

        render: function render() {}
    });

    var ContainerAccess = ContainerStateListenerView.extend({
        initialize: function initialize() {
            ContainerStateListenerView.prototype.initialize.call(this);
            this.template = this.loadTemplate('container-access');
        },

        shouldRefresh: function shouldRefresh(model) {
            return ViewUtils.hasChangedAttributes(model, ['has_partition_group_components', 'user_partitions']);
        },

        render: function render() {
            HtmlUtils.setHtml(this.$el, HtmlUtils.HTML(this.template({
                hasPartitionGroupComponents: this.model.get('has_partition_group_components'),
                userPartitionInfo: this.model.get('user_partition_info')
            })));
            return this;
        }
    });

    var MessageView = ContainerStateListenerView.extend({
        initialize: function initialize() {
            ContainerStateListenerView.prototype.initialize.call(this);
            this.template = this.loadTemplate('container-message');
        },

        shouldRefresh: function shouldRefresh(model) {
            return ViewUtils.hasChangedAttributes(model, ['currently_visible_to_students']);
        },

        render: function render() {
            HtmlUtils.setHtml(this.$el, HtmlUtils.HTML(this.template({ currentlyVisibleToStudents: this.model.get('currently_visible_to_students') })));
            return this;
        }
    });

    /**
     * A controller for updating the "View Live" button.
     */
    var ViewLiveButtonController = ContainerStateListenerView.extend({
        shouldRefresh: function shouldRefresh(model) {
            return ViewUtils.hasChangedAttributes(model, ['published']);
        },

        render: function render() {
            var viewLiveAction = this.$el.find('.button-view');
            if (this.model.get('published')) {
                viewLiveAction.removeClass(disabledCss).attr('aria-disabled', false);
            } else {
                viewLiveAction.addClass(disabledCss).attr('aria-disabled', true);
            }
        }
    });

    /**
     * Publisher is a view that supports the following:
     * 1) Publishing of a draft version of an xblock.
     * 2) Discarding of edits in a draft version.
     * 3) Display of who last edited the xblock, and when.
     * 4) Display of publish status (published, published with changes, changes with no published version).
     */
    var Publisher = BaseView.extend({
        events: {
            'click .action-publish': 'publish',
            'click .action-discard': 'discardChanges',
            'click .action-staff-lock': 'toggleStaffLock'
        },

        // takes XBlockInfo as a model

        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
            this.template = this.loadTemplate('publish-xblock');
            this.model.on('sync', this.onSync, this);
            this.renderPage = this.options.renderPage;
        },

        onSync: function onSync(model) {
            if (ViewUtils.hasChangedAttributes(model, ['has_changes', 'published', 'edited_on', 'edited_by', 'visibility_state', 'has_explicit_staff_lock'])) {
                this.render();
            }
        },

        render: function render() {
            HtmlUtils.setHtml(this.$el, HtmlUtils.HTML(this.template({
                visibilityState: this.model.get('visibility_state'),
                visibilityClass: XBlockViewUtils.getXBlockVisibilityClass(this.model.get('visibility_state')),
                hasChanges: this.model.get('has_changes'),
                editedOn: this.model.get('edited_on'),
                editedBy: this.model.get('edited_by'),
                published: this.model.get('published'),
                publishedOn: this.model.get('published_on'),
                publishedBy: this.model.get('published_by'),
                released: this.model.get('released_to_students'),
                releaseDate: this.model.get('release_date'),
                releaseDateFrom: this.model.get('release_date_from'),
                hasExplicitStaffLock: this.model.get('has_explicit_staff_lock'),
                staffLockFrom: this.model.get('staff_lock_from'),
                course: window.course,
                HtmlUtils: HtmlUtils
            })));

            return this;
        },

        publish: function publish(e) {
            var xblockInfo = this.model;
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            ViewUtils.runOperationShowingMessage(gettext('Publishing'), function () {
                return xblockInfo.save({ publish: 'make_public' }, { patch: true });
            }).always(function () {
                xblockInfo.set('publish', null);
                // Hide any move notification if present.
                MoveXBlockUtils.hideMovedNotification();
            }).done(function () {
                xblockInfo.fetch();
            });
        },

        discardChanges: function discardChanges(e) {
            var xblockInfo = this.model,
                renderPage = this.renderPage;
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            ViewUtils.confirmThenRunOperation(gettext('Discard Changes'), gettext('Are you sure you want to revert to the last published version of the unit? You cannot undo this action.'), gettext('Discard Changes'), function () {
                ViewUtils.runOperationShowingMessage(gettext('Discarding Changes'), function () {
                    return xblockInfo.save({ publish: 'discard_changes' }, { patch: true });
                }).always(function () {
                    xblockInfo.set('publish', null);
                    // Hide any move notification if present.
                    MoveXBlockUtils.hideMovedNotification();
                }).done(function () {
                    renderPage();
                });
            });
        },

        toggleStaffLock: function toggleStaffLock(e) {
            var xblockInfo = this.model,
                self = this,
                enableStaffLock,
                hasInheritedStaffLock,
                saveAndPublishStaffLock,
                revertCheckBox;
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            enableStaffLock = !xblockInfo.get('has_explicit_staff_lock');
            hasInheritedStaffLock = xblockInfo.get('ancestor_has_staff_lock');

            revertCheckBox = function revertCheckBox() {
                self.checkStaffLock(!enableStaffLock);
            };

            saveAndPublishStaffLock = function saveAndPublishStaffLock() {
                // Setting staff lock to null when disabled will delete the field from this xblock,
                // allowing it to use the inherited value instead of using false explicitly.
                return xblockInfo.save({
                    publish: 'republish',
                    metadata: { visible_to_staff_only: enableStaffLock ? true : null } }, { patch: true }).always(function () {
                    xblockInfo.set('publish', null);
                }).done(function () {
                    xblockInfo.fetch();
                }).fail(function () {
                    revertCheckBox();
                });
            };

            this.checkStaffLock(enableStaffLock);
            if (enableStaffLock && !hasInheritedStaffLock) {
                ViewUtils.runOperationShowingMessage(gettext('Hiding from Students'), _.bind(saveAndPublishStaffLock, self));
            } else if (enableStaffLock && hasInheritedStaffLock) {
                ViewUtils.runOperationShowingMessage(gettext('Explicitly Hiding from Students'), _.bind(saveAndPublishStaffLock, self));
            } else if (!enableStaffLock && hasInheritedStaffLock) {
                ViewUtils.runOperationShowingMessage(gettext('Inheriting Student Visibility'), _.bind(saveAndPublishStaffLock, self));
            } else {
                ViewUtils.confirmThenRunOperation(gettext('Make Visible to Students'), gettext('If the unit was previously published and released to students, any changes you made to the unit when it was hidden will now be visible to students. Do you want to proceed?'), gettext('Make Visible to Students'), function () {
                    ViewUtils.runOperationShowingMessage(gettext('Making Visible to Students'), _.bind(saveAndPublishStaffLock, self));
                }, function () {
                    // On cancel, revert the check in the check box
                    revertCheckBox();
                });
            }
        },

        checkStaffLock: function checkStaffLock(check) {
            this.$('.action-staff-lock i').removeClass('fa-check-square-o fa-square-o');
            this.$('.action-staff-lock i').addClass(check ? 'fa-check-square-o' : 'fa-square-o');
        }
    });

    /**
     * PublishHistory displays when and by whom the xblock was last published, if it ever was.
     */
    var PublishHistory = BaseView.extend({
        // takes XBlockInfo as a model

        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
            this.template = this.loadTemplate('publish-history');
            this.model.on('sync', this.onSync, this);
        },

        onSync: function onSync(model) {
            if (ViewUtils.hasChangedAttributes(model, ['published', 'published_on', 'published_by'])) {
                this.render();
            }
        },

        render: function render() {
            HtmlUtils.setHtml(this.$el, HtmlUtils.HTML(this.template({
                published: this.model.get('published'),
                published_on: this.model.get('published_on'),
                published_by: this.model.get('published_by')
            })));

            return this;
        }
    });

    return {
        MessageView: MessageView,
        ViewLiveButtonController: ViewLiveButtonController,
        Publisher: Publisher,
        PublishHistory: PublishHistory,
        ContainerAccess: ContainerAccess
    };
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/unit_outline.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * The UnitOutlineView is used to render the Unit Outline component on the unit page. It shows
 * the ancestors of the unit along with its direct siblings. It also has a single "New Unit"
 * button to allow a new sibling unit to be added.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(1), __webpack_require__("./cms/static/js/views/xblock_outline.js"), __webpack_require__("./cms/static/js/views/unit_outline_child.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (_, XBlockOutlineView, UnitOutlineChildView) {
    var UnitOutlineView = XBlockOutlineView.extend({
        // takes XBlockInfo as a model

        templateName: 'unit-outline',

        render: function render() {
            XBlockOutlineView.prototype.render.call(this);
            this.renderAncestors();
            return this;
        },

        renderAncestors: function renderAncestors() {
            var i,
                listElement,
                ancestors,
                ancestor,
                ancestorView = this,
                previousAncestor = null;
            if (this.model.get('ancestor_info')) {
                ancestors = this.model.get('ancestor_info').ancestors;
                listElement = this.getListElement();
                // Note: the ancestors are processed in reverse order because the tree wants to
                // start at the root, but the ancestors are ordered by closeness to the unit,
                // i.e. subsection and then section.
                for (i = ancestors.length - 1; i >= 0; i--) {
                    ancestor = ancestors[i];
                    ancestorView = this.createChildView(ancestor, previousAncestor, { parentView: ancestorView, currentUnitId: this.model.get('id') });
                    ancestorView.render();
                    listElement.append(ancestorView.$el);
                    previousAncestor = ancestor;
                    listElement = ancestorView.getListElement();
                }
            }
            return ancestorView;
        },

        getChildViewClass: function getChildViewClass() {
            return UnitOutlineChildView;
        },

        getTemplateContext: function getTemplateContext() {
            return _.extend(XBlockOutlineView.prototype.getTemplateContext.call(this), { currentUnitId: this.model.get('id') });
        }
    });

    return UnitOutlineView;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/unit_outline_child.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * The UnitOutlineChildView is used to render each Section,
 * Subsection, and Unit within the Unit Outline component on the unit
 * page.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(1), __webpack_require__("./cms/static/js/views/xblock_outline.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (_, XBlockOutlineView) {
    var UnitOutlineChildView = XBlockOutlineView.extend({
        initialize: function initialize() {
            XBlockOutlineView.prototype.initialize.call(this);
            this.currentUnitId = this.options.currentUnitId;
        },

        getTemplateContext: function getTemplateContext() {
            return _.extend(XBlockOutlineView.prototype.getTemplateContext.call(this), { currentUnitId: this.currentUnitId });
        },

        getChildViewClass: function getChildViewClass() {
            return UnitOutlineChildView;
        },

        createChildView: function createChildView(childInfo, parentInfo, options) {
            options = _.isUndefined(options) ? {} : options;
            return XBlockOutlineView.prototype.createChildView.call(this, childInfo, parentInfo, _.extend(options, { currentUnitId: this.currentUnitId }));
        }
    });

    return UnitOutlineChildView;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define()

/***/ }),

/***/ "./cms/static/js/views/utils/move_xblock_utils.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Provides utilities for move xblock.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__(2), __webpack_require__("./common/static/common/js/components/views/feedback.js"), __webpack_require__("./common/static/common/js/components/views/feedback_alert.js"), __webpack_require__("./cms/static/js/views/utils/xblock_utils.js"), __webpack_require__("./cms/static/js/views/utils/move_xblock_utils.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js"), __webpack_require__("./common/static/js/vendor/jquery.smooth-scroll.min.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, Backbone, Feedback, AlertView, XBlockViewUtils, MoveXBlockUtils, StringUtils) {
    'use strict';

    var redirectLink, moveXBlock, undoMoveXBlock, showMovedNotification, hideMovedNotification;

    redirectLink = function redirectLink(link) {
        window.location.href = link;
    };

    moveXBlock = function moveXBlock(data) {
        XBlockViewUtils.moveXBlock(data.sourceLocator, data.targetParentLocator).done(function (response) {
            // hide modal
            Backbone.trigger('move:hideMoveModal');
            // hide xblock element
            data.sourceXBlockElement.hide();
            showMovedNotification(StringUtils.interpolate(gettext('Success! "{displayName}" has been moved.'), {
                displayName: data.sourceDisplayName
            }), {
                sourceXBlockElement: data.sourceXBlockElement,
                sourceDisplayName: data.sourceDisplayName,
                sourceLocator: data.sourceLocator,
                sourceParentLocator: data.sourceParentLocator,
                targetParentLocator: data.targetParentLocator,
                targetIndex: response.source_index
            });
            Backbone.trigger('move:onXBlockMoved');
        });
    };

    undoMoveXBlock = function undoMoveXBlock(data) {
        XBlockViewUtils.moveXBlock(data.sourceLocator, data.sourceParentLocator, data.targetIndex).done(function () {
            // show XBlock element
            data.sourceXBlockElement.show();
            showMovedNotification(StringUtils.interpolate(gettext('Move cancelled. "{sourceDisplayName}" has been moved back to its original location.'), {
                sourceDisplayName: data.sourceDisplayName
            }));
            Backbone.trigger('move:onXBlockMoved');
        });
    };

    showMovedNotification = function showMovedNotification(title, data) {
        var movedAlertView;
        // data is provided when we click undo move button.
        if (data) {
            movedAlertView = new AlertView.Confirmation({
                title: title,
                actions: {
                    primary: {
                        text: gettext('Undo move'),
                        class: 'action-save',
                        click: function click() {
                            undoMoveXBlock({
                                sourceXBlockElement: data.sourceXBlockElement,
                                sourceDisplayName: data.sourceDisplayName,
                                sourceLocator: data.sourceLocator,
                                sourceParentLocator: data.sourceParentLocator,
                                targetIndex: data.targetIndex
                            });
                        }
                    },
                    secondary: [{
                        text: gettext('Take me to the new location'),
                        class: 'action-cancel',
                        click: function click() {
                            redirectLink('/container/' + data.targetParentLocator);
                        }
                    }]
                }
            });
        } else {
            movedAlertView = new AlertView.Confirmation({
                title: title
            });
        }
        movedAlertView.show();
        // scroll to top
        $.smoothScroll({
            offset: 0,
            easing: 'swing',
            speed: 1000
        });
        movedAlertView.$('.wrapper').first().focus();
        return movedAlertView;
    };

    hideMovedNotification = function hideMovedNotification() {
        var movedAlertView = Feedback.active_alert;
        if (movedAlertView) {
            AlertView.prototype.hide.apply(movedAlertView);
        }
    };

    return {
        redirectLink: redirectLink,
        moveXBlock: moveXBlock,
        undoMoveXBlock: undoMoveXBlock,
        showMovedNotification: showMovedNotification,
        hideMovedNotification: hideMovedNotification
    };
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/xblock_access_editor.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * XBlockAccessEditor is a view that allows the user to restrict access at the unit level on the container page.
 * This view renders the button to restrict unit access into the appropriate place in the unit page.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (BaseView, HtmlUtils) {
    'use strict';

    var XBlockAccessEditor = BaseView.extend({
        // takes XBlockInfo as a model
        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
            this.template = this.loadTemplate('xblock-access-editor');
        },

        render: function render() {
            HtmlUtils.append(this.$el, HtmlUtils.HTML(this.template({})));
            return this;
        }
    });

    return XBlockAccessEditor;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/xblock_outline.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * The XBlockOutlineView is used to render an xblock and its children based upon the information
 * provided in the XBlockInfo model. It is a recursive set of views where each XBlock has its own instance.
 *
 * The class provides several opportunities to override the default behavior in subclasses:
 *  - shouldRenderChildren defaults to true meaning that the view should also create child views
 *  - shouldExpandChildren defaults to true meaning that the view should show itself as expanded
 *  - refresh is called when a server change has been made and the view needs to be refreshed
 *
 * The view can be constructed with an initialState option which is a JSON structure representing
 * the desired initial state. The parameters are as follows:
 *  - locator_to_show - the locator for the xblock which is the one being explicitly shown
 *  - scroll_offset - the scroll offset to use for the locator being shown
 *  - edit_display_name - true if the shown xblock's display name should be in inline edit mode
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./common/static/common/js/components/utils/view_utils.js"), __webpack_require__("./cms/static/js/views/utils/xblock_utils.js"), __webpack_require__("./cms/static/js/views/xblock_string_field_editor.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/string-utils.js"), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, gettext, BaseView, ViewUtils, XBlockViewUtils, XBlockStringFieldEditor, StringUtils, HtmlUtils) {
    'use strict';

    var XBlockOutlineView = BaseView.extend({
        // takes XBlockInfo as a model

        options: {
            collapsedClass: 'is-collapsed'
        },

        templateName: 'xblock-outline',

        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
            this.initialState = this.options.initialState;
            this.expandedLocators = this.options.expandedLocators;
            this.template = this.options.template;
            if (!this.template) {
                this.template = this.loadTemplate(this.templateName);
            }
            this.parentInfo = this.options.parentInfo;
            this.parentView = this.options.parentView;
            this.renderedChildren = false;
            this.model.on('sync', this.onSync, this);
        },

        render: function render() {
            this.renderTemplate();
            this.addButtonActions(this.$el);
            this.addNameEditor();

            // For cases in which we need to suppress the header controls during rendering, we'll
            // need to add the current model's id/locator to the set of expanded locators
            if (this.model.get('is_header_visible') !== null && !this.model.get('is_header_visible')) {
                var locator = this.model.get('id');
                if (!_.isUndefined(this.expandedLocators) && !this.expandedLocators.contains(locator)) {
                    this.expandedLocators.add(locator);
                    this.refresh();
                }
            }

            if (this.shouldRenderChildren() && this.shouldExpandChildren()) {
                this.renderChildren();
            } else {
                this.renderedChildren = false;
            }
            return this;
        },

        renderTemplate: function renderTemplate() {
            var html = this.template(this.getTemplateContext());
            if (this.parentInfo) {
                this.setElement($(html));
            } else {
                HtmlUtils.setHtml(this.$el, HtmlUtils.HTML(html));
            }
        },

        getTemplateContext: function getTemplateContext() {
            var xblockInfo = this.model,
                childInfo = xblockInfo.get('child_info'),
                parentInfo = this.parentInfo,
                xblockType = XBlockViewUtils.getXBlockType(this.model.get('category'), this.parentInfo),
                xblockTypeDisplayName = XBlockViewUtils.getXBlockType(this.model.get('category'), this.parentInfo, true),
                parentType = parentInfo ? XBlockViewUtils.getXBlockType(parentInfo.get('category')) : null,
                addChildName = null,
                defaultNewChildName = null,
                isCollapsed = this.shouldRenderChildren() && !this.shouldExpandChildren();
            if (childInfo) {
                addChildName = StringUtils.interpolate(gettext('New {component_type}'), {
                    component_type: childInfo.display_name
                }, true);
                defaultNewChildName = childInfo.display_name;
            }
            /* globals course */
            return {
                xblockInfo: xblockInfo,
                visibilityClass: XBlockViewUtils.getXBlockVisibilityClass(xblockInfo.get('visibility_state')),
                typeListClass: XBlockViewUtils.getXBlockListTypeClass(xblockType),
                parentInfo: this.parentInfo,
                xblockType: xblockType,
                xblockTypeDisplayName: xblockTypeDisplayName,
                parentType: parentType,
                childType: childInfo ? XBlockViewUtils.getXBlockType(childInfo.category, xblockInfo) : null,
                childCategory: childInfo ? childInfo.category : null,
                addChildLabel: addChildName,
                defaultNewChildName: defaultNewChildName,
                isCollapsed: isCollapsed,
                includesChildren: this.shouldRenderChildren(),
                hasExplicitStaffLock: this.model.get('has_explicit_staff_lock'),
                staffOnlyMessage: this.model.get('staff_only_message'),
                course: course
            };
        },

        renderChildren: function renderChildren() {
            var self = this,
                parentInfo = this.model;
            if (parentInfo.get('child_info')) {
                _.each(this.model.get('child_info').children, function (childInfo) {
                    var childOutlineView = self.createChildView(childInfo, parentInfo);
                    childOutlineView.render();
                    self.addChildView(childOutlineView);
                });
            }
            this.renderedChildren = true;
        },

        getListElement: function getListElement() {
            return this.$('> .outline-content > ol');
        },

        addChildView: function addChildView(childView, xblockElement) {
            if (xblockElement) {
                childView.$el.insertAfter(xblockElement);
            } else {
                this.getListElement().append(childView.$el);
            }
        },

        addNameEditor: function addNameEditor() {
            var self = this,
                xblockField = this.$('.wrapper-xblock-field'),
                XBlockOutlineFieldEditor,
                nameEditor;
            if (xblockField.length > 0) {
                // Make a subclass of the standard xblock string field editor which refreshes
                // the entire section that this view is contained in. This is necessary as
                // changing the name could have caused the section to change state.
                XBlockOutlineFieldEditor = XBlockStringFieldEditor.extend({
                    refresh: function refresh() {
                        self.refresh();
                    }
                });
                nameEditor = new XBlockOutlineFieldEditor({
                    el: xblockField,
                    model: this.model
                });
                nameEditor.render();
            }
        },

        toggleExpandCollapse: function toggleExpandCollapse(event) {
            // The course outline page tracks expanded locators. The unit location sidebar does not.
            if (this.expandedLocators) {
                var locator = this.model.get('id');
                var wasExpanded = this.expandedLocators.contains(locator);
                if (wasExpanded) {
                    this.expandedLocators.remove(locator);
                } else {
                    this.expandedLocators.add(locator);
                }
            }
            // Ensure that the children have been rendered before expanding
            this.ensureChildrenRendered();
            BaseView.prototype.toggleExpandCollapse.call(this, event);
        },

        /**
         * Verifies that the children are rendered (if they should be).
         */
        ensureChildrenRendered: function ensureChildrenRendered() {
            if (!this.renderedChildren && this.shouldRenderChildren()) {
                this.renderChildren();
            }
        },

        /**
         * Adds handlers to the each button in the header's panel. This is managed outside of
         * Backbone's own event registration so that the handlers don't get scoped to all the
         * children of this view.
         * @param element The root element of this view.
         */
        addButtonActions: function addButtonActions(element) {
            var self = this;
            element.find('.delete-button').click(_.bind(this.handleDeleteEvent, this));
            element.find('.duplicate-button').click(_.bind(this.handleDuplicateEvent, this));
            element.find('.button-new').click(_.bind(this.handleAddEvent, this));
        },

        shouldRenderChildren: function shouldRenderChildren() {
            return true;
        },

        shouldExpandChildren: function shouldExpandChildren() {
            return true;
        },

        getChildViewClass: function getChildViewClass() {
            return XBlockOutlineView;
        },

        createChildView: function createChildView(childInfo, parentInfo, options) {
            var viewClass = this.getChildViewClass();
            return new viewClass(_.extend({
                model: childInfo,
                parentInfo: parentInfo,
                parentView: this,
                initialState: this.initialState,
                expandedLocators: this.expandedLocators,
                template: this.template
            }, options));
        },

        onSync: function onSync(event) {
            var hasChangedAttributes = ViewUtils.hasChangedAttributes(this.model, ['visibility_state', 'child_info', 'display_name', 'highlights']);
            if (hasChangedAttributes) {
                this.onXBlockChange();
            }
        },

        onXBlockChange: function onXBlockChange() {
            var oldElement = this.$el,
                viewState = this.initialState;
            this.render();
            if (this.parentInfo) {
                oldElement.replaceWith(this.$el);
            }
            if (viewState) {
                this.setViewState(viewState);
            }
        },

        setViewState: function setViewState(viewState) {
            var locatorToShow = viewState.locator_to_show,
                scrollOffset = viewState.scroll_offset || 0,
                editDisplayName = viewState.edit_display_name,
                locatorElement;
            if (locatorToShow) {
                if (locatorToShow === this.model.id) {
                    locatorElement = this.$el;
                } else {
                    locatorElement = this.$('.outline-item[data-locator="' + locatorToShow + '"]');
                }
                if (locatorElement.length > 0) {
                    ViewUtils.setScrollOffset(locatorElement, scrollOffset);
                } else {
                    console.error('Failed to show item with locator ' + locatorToShow + '');
                }
                if (editDisplayName) {
                    locatorElement.find('> div[class$="header"] .xblock-field-value-edit').click();
                }
            }
            this.initialState = null;
        },

        /**
         * Refresh the view's model from the server, which will cause the view to refresh.
         * @returns {jQuery promise} A promise representing the refresh operation.
         */
        refresh: function refresh() {
            return this.model.fetch();
        },

        onChildAdded: function onChildAdded(locator, category) {
            // For units, redirect to the new page, and for everything else just refresh inline.
            if (category === 'vertical') {
                this.onUnitAdded(locator);
            } else {
                this.refresh();
            }
        },

        onUnitAdded: function onUnitAdded(locator) {
            ViewUtils.redirect('/container/' + locator + '?action=new');
        },

        onChildDeleted: function onChildDeleted() {
            this.refresh();
        },

        handleDeleteEvent: function handleDeleteEvent(event) {
            var self = this,
                parentView = this.parentView,
                xblockType = XBlockViewUtils.getXBlockType(this.model.get('category'), parentView.model, true);
            event.preventDefault();
            XBlockViewUtils.deleteXBlock(this.model, xblockType).done(function () {
                if (parentView) {
                    parentView.onChildDeleted(self, event);
                }
            });
        },

        /**
         * Finds appropriate parent element for an xblock element.
         * @param {jquery Element}  xblockElement  The xblock element to be duplicated.
         * @param {String}  xblockType The front-end terminology of the xblock category.
         * @returns {jquery Element} Appropriate parent element of xblock element.
         */
        getParentElement: function getParentElement(xblockElement, xblockType) {
            var xblockMap = {
                unit: 'subsection',
                subsection: 'section',
                section: 'course'
            },
                parentXblockType = xblockMap[xblockType];
            return xblockElement.closest('.outline-' + parentXblockType);
        },

        /**
         * Duplicate event handler.
         */
        handleDuplicateEvent: function handleDuplicateEvent(event) {
            var self = this,
                xblockType = XBlockViewUtils.getXBlockType(self.model.get('category'), self.parentView.model),
                xblockElement = $(event.currentTarget).closest('.outline-item'),
                parentElement = self.getParentElement(xblockElement, xblockType);

            event.preventDefault();
            XBlockViewUtils.duplicateXBlock(xblockElement, parentElement).done(function (data) {
                if (self.parentView) {
                    self.parentView.onChildDuplicated(data.locator, xblockType, xblockElement);
                }
            });
        },

        handleAddEvent: function handleAddEvent(event) {
            var self = this,
                $target = $(event.currentTarget),
                category = $target.data('category');
            event.preventDefault();
            XBlockViewUtils.addXBlock($target).done(function (locator) {
                self.onChildAdded(locator, category, event);
            });
        }
    });

    return XBlockOutlineView;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/static/js/views/xblock_string_field_editor.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * XBlockStringFieldEditor is a view that allows the user to inline edit an XBlock string field.
 * Clicking on the field value will hide the text and replace it with an input to allow the user
 * to change the value. Once the user leaves the field, a request will be sent to update the
 * XBlock field's value if it has been changed. If the user presses Escape, then any changes will
 * be removed and the input hidden again.
 */
!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./cms/static/js/views/utils/xblock_utils.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (BaseView, XBlockViewUtils) {
    var XBlockStringFieldEditor = BaseView.extend({
        events: {
            'click .xblock-field-value-edit': 'showInput',
            'click button[name=submit]': 'onClickSubmit',
            'click button[name=cancel]': 'onClickCancel',
            'click .xblock-string-field-editor': 'onClickEditor',
            'change .xblock-field-input': 'updateField',
            'focusout .xblock-field-input': 'onInputFocusLost',
            'keyup .xblock-field-input': 'handleKeyUp'
        },

        // takes XBlockInfo as a model

        initialize: function initialize() {
            BaseView.prototype.initialize.call(this);
            this.fieldName = this.$el.data('field');
            this.fieldDisplayName = this.$el.data('field-display-name');
            this.template = this.loadTemplate('xblock-string-field-editor');
            this.model.on('change:' + this.fieldName, this.onChangeField, this);
        },

        render: function render() {
            this.$el.append(this.template({
                value: this.model.escape(this.fieldName),
                fieldName: this.fieldName,
                fieldDisplayName: this.fieldDisplayName
            }));
            return this;
        },

        getLabel: function getLabel() {
            return this.$('.xblock-field-value');
        },

        getInput: function getInput() {
            return this.$('.xblock-field-input');
        },

        onInputFocusLost: function onInputFocusLost() {
            var currentValue = this.model.get(this.fieldName);
            if (currentValue === this.getInput().val()) {
                this.hideInput();
            }
        },

        onClickSubmit: function onClickSubmit(event) {
            event.preventDefault();
            event.stopPropagation();
            this.updateField();
        },

        onClickCancel: function onClickCancel(event) {
            event.preventDefault();
            event.stopPropagation();
            this.cancelInput();
        },

        onClickEditor: function onClickEditor(event) {
            event.stopPropagation();
        },

        onChangeField: function onChangeField() {
            var value = this.model.get(this.fieldName);
            this.getLabel().text(value);
            this.getInput().val(value);
            this.hideInput();
        },

        showInput: function showInput(event) {
            var input = this.getInput();
            event.preventDefault();
            event.stopPropagation();
            this.$el.addClass('is-editing');
            input.focus().select();
        },

        hideInput: function hideInput() {
            this.$el.removeClass('is-editing');
        },

        cancelInput: function cancelInput() {
            this.getInput().val(this.model.get(this.fieldName));
            this.hideInput();
        },

        /**
         * Refresh the model from the server so that it gets the latest publish and last modified information.
         */
        refresh: function refresh() {
            this.model.fetch();
        },

        updateField: function updateField() {
            var self = this,
                xblockInfo = this.model,
                newValue = this.getInput().val().trim(),
                oldValue = xblockInfo.get(this.fieldName);
            // TODO: generalize this as not all xblock fields want to disallow empty strings...
            if (newValue === '' || newValue === oldValue) {
                this.cancelInput();
                return;
            }
            return XBlockViewUtils.updateXBlockField(xblockInfo, this.fieldName, newValue).done(function () {
                self.refresh();
            });
        },

        handleKeyUp: function handleKeyUp(event) {
            if (event.keyCode === 27) {
                // Revert the changes if the user hits escape
                this.cancelInput();
            }
        }
    });

    return XBlockStringFieldEditor;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__)); // end define();

/***/ }),

/***/ "./cms/templates/js/move-xblock-breadcrumb.underscore":
/***/ (function(module, exports) {

module.exports = "<nav class=\"breadcrumbs\" aria-label=\"Course Outline breadcrumb\">\n    <% _.each(breadcrumbs.slice(0, -1), function (breadcrumb, index, items) { %>\n        <ol class=\"bc-container bc-<%- index %>\">\n            <li class=\"bc-container-content\">\n                <button class=\"parent-nav-button\" data-parent-index=\"<%- index %>\">\n                    <%- breadcrumb %>\n                </button>\n                <span class=\"fa fa-angle-right breadcrumb-fa-icon\" aria-hidden=\"true\"></span>\n            </li>\n        </ol>\n    <% }) %>\n    <ol class=\"bc-container bc-<%- breadcrumbs.length - 1 %> last\">\n        <li class=\"bc-container-content\">\n            <span class=\"parent-displayname\"><%- breadcrumbs[breadcrumbs.length - 1] %></span>\n        </li>\n    </ol>\n</nav>\n"

/***/ }),

/***/ "./cms/templates/js/move-xblock-list.underscore":
/***/ (function(module, exports) {

module.exports = "<div class=\"xblock-items-category\">\n    <span class=\"sr\">\n        <%\n        // Translators: message will be like `Units in Homework - Question Styles`, `Subsections in Example 1 - Getting started` etc.\n        %>\n        <%- StringUtils.interpolate(\n                gettext(\"{categoryText} in {parentDisplayname}\"),\n                {categoryText: categoryText, parentDisplayname: parentDisplayname}\n            )\n        %>\n    </span>\n    <span class=\"category-text\" aria-hidden=\"true\">\n        <%- categoryText %>:\n    </span>\n</div>\n<ul class=\"xblock-items-container\" data-items-category=\"<%- XBlocksCategory %>\">\n    <% for (var i = 0; i < xblocks.length; i++) {\n        var xblock = xblocks[i];\n    %>\n        <li class=\"xblock-item\" data-item-index=\"<%- i %>\">\n            <% if (sourceXBlockId !== xblock.id && (xblock.get('child_info') || XBlocksCategory !== 'component')) { %>\n                <button class=\"button-forward\" >\n                    <span class=\"xblock-displayname truncate\">\n                        <%- xblock.get('display_name') %>\n                    </span>\n                    <% if(currentLocationIndex === i) { %>\n                        <span class=\"current-location\">\n                            (<%- gettext('Current location') %>)\n                        </span>\n                    <% } %>\n                    <span class=\"icon fa fa-arrow-right forward-sr-icon\" aria-hidden=\"true\"></span>\n                    <span class=\"sr forward-sr-text\"><%- gettext(\"View child items\") %></span>\n                </button>\n            <% } else { %>\n                <span class=\"component\">\n                    <span class=\"xblock-displayname truncate\">\n                        <%- xblock.get('display_name') %>\n                    </span>\n                    <% if(currentLocationIndex === i) { %>\n                        <span class=\"current-location\">\n                            (<%- gettext('Currently selected') %>)\n                        </span>\n                    <% } %>\n                </span>\n            <% } %>\n        </li>\n    <% } %>\n    <% if(xblocks.length === 0) { %>\n        <span class=\"xblock-no-child-message\">\n            <%- noChildText %>\n        </span>\n    <% } %>\n</ul>\n"

/***/ }),

/***/ "./cms/templates/js/move-xblock-modal.underscore":
/***/ (function(module, exports) {

module.exports = "<div class=\"ui-loading\">\n    <p>\n        <span class=\"spin\">\n            <span class=\"icon fa fa-refresh\" aria-hidden=\"true\"></span>\n        </span>\n        <span class=\"copy\"><%- gettext('Loading') %></span>\n    </p>\n</div>\n<div class='breadcrumb-container is-hidden'></div>\n<div class='xblock-list-container'></div>\n"

/***/ }),

/***/ "./common/static/common/js/components/views/feedback_alert.js":
/***/ (function(module, exports, __webpack_require__) {

"use strict";
var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;


!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(0), __webpack_require__(1), __webpack_require__("./common/static/common/js/vendor/underscore.string.js"), __webpack_require__("./common/static/common/js/components/views/feedback.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function ($, _, str, SystemFeedbackView) {
    var Alert = SystemFeedbackView.extend({
        options: $.extend({}, SystemFeedbackView.prototype.options, {
            type: 'alert'
        }),
        slide_speed: 900,
        show: function show() {
            SystemFeedbackView.prototype.show.apply(this, arguments);
            this.$el.hide();
            this.$el.slideDown(this.slide_speed);
            return this;
        },
        hide: function hide() {
            this.$el.slideUp({
                duration: this.slide_speed
            });
            setTimeout(_.bind(SystemFeedbackView.prototype.hide, this, arguments), this.slideSpeed);
        }
    });

    // create Alert.Warning, Alert.Confirmation, etc
    var capitalCamel, intents;
    capitalCamel = _.compose(str.capitalize, str.camelize);
    intents = ['warning', 'error', 'confirmation', 'announcement', 'step-required', 'help', 'mini'];
    _.each(intents, function (intent) {
        var subclass;
        subclass = Alert.extend({
            options: $.extend({}, Alert.prototype.options, {
                intent: intent
            })
        });
        Alert[capitalCamel(intent)] = subclass;
    });

    return Alert;
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

/***/ }),

/***/ 4:
/***/ (function(module, exports) {

(function() { module.exports = window["URI"]; }());

/***/ })

},["./cms/static/js/factories/container.js"])));
//# sourceMappingURL=container.js.map