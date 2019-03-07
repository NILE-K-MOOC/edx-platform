(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([8,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74],{

/***/ "./cms/static/js/collections/chapter.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__("./cms/static/js/models/chapter.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, ChapterModel) {
    var ChapterCollection = Backbone.Collection.extend({
        model: ChapterModel,
        comparator: 'order',
        nextOrder: function nextOrder() {
            if (!this.length) return 1;
            return this.last().get('order') + 1;
        },
        isEmpty: function isEmpty() {
            return this.length === 0 || this.every(function (m) {
                return m.isEmpty();
            });
        }
    });
    return ChapterCollection;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/collections/textbook.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__("./cms/static/js/models/textbook.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, TextbookModel) {
    var TextbookCollection = Backbone.Collection.extend({
        model: TextbookModel,
        url: function url() {
            return CMS.URL.TEXTBOOKS;
        }
    });
    return TextbookCollection;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/factories/textbooks.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony export (immutable) */ __webpack_exports__["default"] = TextbooksFactory;
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TextbooksFactory", function() { return TextbooksFactory; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_gettext__ = __webpack_require__(3);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_gettext___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_gettext__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_models_section__ = __webpack_require__("./cms/static/js/models/section.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_models_section___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_js_models_section__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_js_collections_textbook__ = __webpack_require__("./cms/static/js/collections/textbook.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_js_collections_textbook___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_js_collections_textbook__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_js_views_list_textbooks__ = __webpack_require__("./cms/static/js/views/list_textbooks.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_js_views_list_textbooks___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_js_views_list_textbooks__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__base__ = __webpack_require__("./cms/static/js/factories/base.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__base___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4__base__);






'use strict';
function TextbooksFactory(textbooksJson) {
    var textbooks = new __WEBPACK_IMPORTED_MODULE_2_js_collections_textbook__(textbooksJson, { parse: true }),
        tbView = new __WEBPACK_IMPORTED_MODULE_3_js_views_list_textbooks__({ collection: textbooks });

    $('.content-primary').append(tbView.render().el);
    $('.nav-actions .new-button').click(function (event) {
        tbView.addOne(event);
    });
    $(window).on('beforeunload', function () {
        var dirty = textbooks.find(function (textbook) {
            return textbook.isDirty();
        });
        if (dirty) {
            return __WEBPACK_IMPORTED_MODULE_0_gettext__('You have unsaved changes. Do you really want to leave this page?');
        }
    });
};


/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(0)))

/***/ }),

/***/ "./cms/static/js/models/chapter.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__(3), __webpack_require__("./node_modules/backbone-associations/backbone-associations-min.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, gettext) {
    var Chapter = Backbone.AssociatedModel.extend({
        defaults: function defaults() {
            return {
                name: '',
                asset_path: '',
                order: this.collection ? this.collection.nextOrder() : 1
            };
        },
        isEmpty: function isEmpty() {
            return !this.get('name') && !this.get('asset_path');
        },
        parse: function parse(response) {
            if ('title' in response && !('name' in response)) {
                response.name = response.title;
                delete response.title;
            }
            if ('url' in response && !('asset_path' in response)) {
                response.asset_path = response.url;
                delete response.url;
            }
            return response;
        },
        toJSON: function toJSON() {
            return {
                title: this.get('name'),
                url: this.get('asset_path')
            };
        },
        // NOTE: validation functions should return non-internationalized error
        // messages. The messages will be passed through gettext in the template.
        validate: function validate(attrs, options) {
            if (!attrs.name && !attrs.asset_path) {
                return {
                    message: gettext('Chapter name and asset_path are both required'),
                    attributes: { name: true, asset_path: true }
                };
            } else if (!attrs.name) {
                return {
                    message: gettext('Chapter name is required'),
                    attributes: { name: true }
                };
            } else if (!attrs.asset_path) {
                return {
                    message: gettext('asset_path is required'),
                    attributes: { asset_path: true }
                };
            }
        }
    });
    return Chapter;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/models/section.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__(3), __webpack_require__("./common/static/common/js/components/views/feedback_notification.js"), __webpack_require__("./cms/static/js/utils/module.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, gettext, NotificationView, ModuleUtils) {
    var Section = Backbone.Model.extend({
        defaults: {
            name: ''
        },
        validate: function validate(attrs, options) {
            if (!attrs.name) {
                return gettext('You must specify a name');
            }
        },
        urlRoot: ModuleUtils.urlRoot,
        toJSON: function toJSON() {
            return {
                metadata: {
                    display_name: this.get('name')
                }
            };
        },
        initialize: function initialize() {
            this.listenTo(this, 'request', this.showNotification);
            this.listenTo(this, 'sync', this.hideNotification);
        },
        showNotification: function showNotification() {
            if (!this.msg) {
                this.msg = new NotificationView.Mini({
                    title: gettext('Saving')
                });
            }
            this.msg.show();
        },
        hideNotification: function hideNotification() {
            if (!this.msg) {
                return;
            }
            this.msg.hide();
        }
    });
    return Section;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/models/textbook.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function($) {var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(2), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./cms/static/js/models/chapter.js"), __webpack_require__("./cms/static/js/collections/chapter.js"), __webpack_require__("./node_modules/backbone-associations/backbone-associations-min.js"), __webpack_require__("./cms/static/cms/js/main.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (Backbone, _, gettext, ChapterModel, ChapterCollection) {
    var Textbook = Backbone.AssociatedModel.extend({
        defaults: function defaults() {
            return {
                name: '',
                chapters: new ChapterCollection([{}]),
                showChapters: false,
                editing: false
            };
        },
        relations: [{
            type: Backbone.Many,
            key: 'chapters',
            relatedModel: ChapterModel,
            collectionType: ChapterCollection
        }],
        initialize: function initialize() {
            this.setOriginalAttributes();
            return this;
        },
        setOriginalAttributes: function setOriginalAttributes() {
            this._originalAttributes = this.parse(this.toJSON());
        },
        reset: function reset() {
            this.set(this._originalAttributes, { parse: true });
        },
        isDirty: function isDirty() {
            return !_.isEqual(this._originalAttributes, this.parse(this.toJSON()));
        },
        isEmpty: function isEmpty() {
            return !this.get('name') && this.get('chapters').isEmpty();
        },
        urlRoot: function urlRoot() {
            return CMS.URL.TEXTBOOKS;
        },
        parse: function parse(response) {
            var ret = $.extend(true, {}, response);
            if ('tab_title' in ret && !('name' in ret)) {
                ret.name = ret.tab_title;
                delete ret.tab_title;
            }
            if ('url' in ret && !('chapters' in ret)) {
                ret.chapters = { url: ret.url };
                delete ret.url;
            }
            _.each(ret.chapters, function (chapter, i) {
                chapter.order = chapter.order || i + 1;
            });
            return ret;
        },
        toJSON: function toJSON() {
            return {
                tab_title: this.get('name'),
                chapters: this.get('chapters').toJSON()
            };
        },
        // NOTE: validation functions should return non-internationalized error
        // messages. The messages will be passed through gettext in the template.
        validate: function validate(attrs, options) {
            if (!attrs.name) {
                return {
                    message: gettext('Textbook name is required'),
                    attributes: { name: true }
                };
            }
            if (attrs.chapters.length === 0) {
                return {
                    message: gettext('Please add at least one chapter'),
                    attributes: { chapters: true }
                };
            } else {
                // validate all chapters
                var invalidChapters = [];
                attrs.chapters.each(function (chapter) {
                    if (!chapter.isValid()) {
                        invalidChapters.push(chapter);
                    }
                });
                if (!_.isEmpty(invalidChapters)) {
                    return {
                        message: gettext('All chapters must have a name and asset'),
                        attributes: { chapters: invalidChapters }
                    };
                }
            }
        }
    });
    return Textbook;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(0)))

/***/ }),

/***/ "./cms/static/js/views/edit_chapter.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/* global course */

!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(1), __webpack_require__(0), __webpack_require__(3), __webpack_require__("./node_modules/edx-ui-toolkit/src/js/utils/html-utils.js"), __webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__("./cms/static/js/models/uploads.js"), __webpack_require__("./cms/static/js/views/uploads.js"), __webpack_require__("./cms/templates/js/edit-chapter.underscore")], __WEBPACK_AMD_DEFINE_RESULT__ = function (_, $, gettext, HtmlUtils, BaseView, FileUploadModel, UploadDialogView, editChapterTemplate) {
    'use strict';

    var EditChapter = BaseView.extend({
        initialize: function initialize() {
            this.template = HtmlUtils.template(editChapterTemplate);
            this.listenTo(this.model, 'change', this.render);
        },
        tagName: 'li',
        className: function className() {
            return 'field-group chapter chapter' + this.model.get('order');
        },
        render: function render() {
            HtmlUtils.setHtml(this.$el, this.template({
                name: this.model.get('name'),
                asset_path: this.model.get('asset_path'),
                order: this.model.get('order'),
                error: this.model.validationError
            }));
            return this;
        },
        events: {
            'change .chapter-name': 'changeName',
            'change .chapter-asset-path': 'changeAssetPath',
            'click .action-close': 'removeChapter',
            'click .action-upload': 'openUploadDialog',
            submit: 'uploadAsset'
        },
        changeName: function changeName(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.set({
                name: this.$('.chapter-name').val()
            }, { silent: true });
            return this;
        },
        changeAssetPath: function changeAssetPath(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.set({
                asset_path: this.$('.chapter-asset-path').val()
            }, { silent: true });
            return this;
        },
        removeChapter: function removeChapter(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.collection.remove(this.model);
            return this.remove();
        },
        openUploadDialog: function openUploadDialog(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.set({
                name: this.$('input.chapter-name').val(),
                asset_path: this.$('input.chapter-asset-path').val()
            });
            var msg = new FileUploadModel({
                title: _.template(gettext('Upload a new PDF to “<%= name %>”'))({ name: course.escape('name') }),
                message: gettext('Please select a PDF file to upload.'),
                mimeTypes: ['application/pdf']
            });
            var that = this;
            var view = new UploadDialogView({
                model: msg,
                onSuccess: function onSuccess(response) {
                    var options = {};
                    if (!that.model.get('name')) {
                        options.name = response.asset.displayname;
                    }
                    options.asset_path = response.asset.portable_url;
                    that.model.set(options);
                }
            });
            view.show();
        }
    });

    return EditChapter;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/edit_textbook.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__(1), __webpack_require__(0), __webpack_require__("./cms/static/js/views/edit_chapter.js"), __webpack_require__("./common/static/common/js/components/views/feedback_notification.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (BaseView, _, $, EditChapterView, NotificationView) {
    var EditTextbook = BaseView.extend({
        initialize: function initialize() {
            this.template = this.loadTemplate('edit-textbook');
            this.listenTo(this.model, 'invalid', this.render);
            var chapters = this.model.get('chapters');
            this.listenTo(chapters, 'add', this.addOne);
            this.listenTo(chapters, 'reset', this.addAll);
            this.listenTo(chapters, 'all', this.render);
        },
        tagName: 'section',
        className: 'textbook',
        render: function render() {
            this.$el.html(this.template({
                name: this.model.get('name'),
                error: this.model.validationError
            }));
            this.addAll();
            return this;
        },
        events: {
            'change input[name=textbook-name]': 'setName',
            submit: 'setAndClose',
            'click .action-cancel': 'cancel',
            'click .action-add-chapter': 'createChapter'
        },
        addOne: function addOne(chapter) {
            var view = new EditChapterView({ model: chapter });
            this.$('ol.chapters').append(view.render().el);
            return this;
        },
        addAll: function addAll() {
            this.model.get('chapters').each(this.addOne, this);
        },
        createChapter: function createChapter(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.setValues();
            this.model.get('chapters').add([{}]);
        },
        setName: function setName(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.set('name', this.$('#textbook-name-input').val(), { silent: true });
        },
        setValues: function setValues() {
            this.setName();
            var that = this;
            _.each(this.$('li'), function (li, i) {
                var chapter = that.model.get('chapters').at(i);
                if (!chapter) {
                    return;
                }
                chapter.set({
                    name: $('.chapter-name', li).val(),
                    asset_path: $('.chapter-asset-path', li).val()
                });
            });
            return this;
        },
        setAndClose: function setAndClose(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.setValues();
            if (!this.model.isValid()) {
                return;
            }
            var saving = new NotificationView.Mini({
                title: gettext('Saving')
            }).show();
            var that = this;
            this.model.save({}, {
                success: function success() {
                    that.model.setOriginalAttributes();
                    that.close();
                },
                complete: function complete() {
                    saving.hide();
                }
            });
        },
        cancel: function cancel(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.reset();
            return this.close();
        },
        close: function close() {
            var textbooks = this.model.collection;
            this.remove();
            if (this.model.isNew()) {
                // if the textbook has never been saved, remove it
                textbooks.remove(this.model);
            }
            // don't forget to tell the model that it's no longer being edited
            this.model.set('editing', false);
            return this;
        }
    });
    return EditTextbook;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/list_textbooks.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__(0), __webpack_require__("./cms/static/js/views/edit_textbook.js"), __webpack_require__("./cms/static/js/views/show_textbook.js"), __webpack_require__("./common/static/common/js/components/utils/view_utils.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (BaseView, $, EditTextbookView, ShowTextbookView, ViewUtils) {
    var ListTextbooks = BaseView.extend({
        initialize: function initialize() {
            this.emptyTemplate = this.loadTemplate('no-textbooks');
            this.listenTo(this.collection, 'all', this.render);
            this.listenTo(this.collection, 'destroy', this.handleDestroy);
        },
        tagName: 'div',
        className: 'textbooks-list',
        render: function render() {
            var textbooks = this.collection;
            if (textbooks.length === 0) {
                this.$el.html(this.emptyTemplate());
            } else {
                this.$el.empty();
                var that = this;
                textbooks.each(function (textbook) {
                    var view;
                    if (textbook.get('editing')) {
                        view = new EditTextbookView({ model: textbook });
                    } else {
                        view = new ShowTextbookView({ model: textbook });
                    }
                    that.$el.append(view.render().el);
                });
            }
            return this;
        },
        events: {
            'click .new-button': 'addOne'
        },
        addOne: function addOne(e) {
            var $sectionEl, $inputEl;
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.collection.add([{ editing: true }]); // (render() call triggered here)
            // find the outer 'section' tag for the newly added textbook
            $sectionEl = this.$el.find('section:last');
            // scroll to put this at top of viewport
            ViewUtils.setScrollOffset($sectionEl, 0);
            // find the first input element in this section
            $inputEl = $sectionEl.find('input:first');
            // activate the text box (so user can go ahead and start typing straight away)
            $inputEl.focus().select();
        },
        handleDestroy: function handleDestroy(model, collection, options) {
            collection.remove(model);
        }
    });
    return ListTextbooks;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ "./cms/static/js/views/show_textbook.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function($) {var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__("./cms/static/js/views/baseview.js"), __webpack_require__(1), __webpack_require__(3), __webpack_require__("./common/static/common/js/components/views/feedback_notification.js"), __webpack_require__("./common/static/common/js/components/views/feedback_prompt.js")], __WEBPACK_AMD_DEFINE_RESULT__ = function (BaseView, _, gettext, NotificationView, PromptView) {
    var ShowTextbook = BaseView.extend({
        initialize: function initialize() {
            this.template = _.template($('#show-textbook-tpl').text());
            this.listenTo(this.model, 'change', this.render);
        },
        tagName: 'section',
        className: 'textbook',
        events: {
            'click .edit': 'editTextbook',
            'click .delete': 'confirmDelete',
            'click .show-chapters': 'showChapters',
            'click .hide-chapters': 'hideChapters'
        },
        render: function render() {
            var attrs = $.extend({}, this.model.attributes);
            attrs.bookindex = this.model.collection.indexOf(this.model);
            attrs.course = window.course.attributes;
            this.$el.html(this.template(attrs));
            return this;
        },
        editTextbook: function editTextbook(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.set('editing', true);
        },
        confirmDelete: function confirmDelete(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            var textbook = this.model;
            new PromptView.Warning({
                title: _.template(gettext('Delete “<%= name %>”?'))({ name: textbook.get('name') }),
                message: gettext("Deleting a textbook cannot be undone and once deleted any reference to it in your courseware's navigation will also be removed."),
                actions: {
                    primary: {
                        text: gettext('Delete'),
                        click: function click(view) {
                            view.hide();
                            var delmsg = new NotificationView.Mini({
                                title: gettext('Deleting')
                            }).show();
                            textbook.destroy({
                                complete: function complete() {
                                    delmsg.hide();
                                }
                            });
                        }
                    },
                    secondary: {
                        text: gettext('Cancel'),
                        click: function click(view) {
                            view.hide();
                        }
                    }
                }
            }).show();
        },
        showChapters: function showChapters(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.set('showChapters', true);
        },
        hideChapters: function hideChapters(e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            this.model.set('showChapters', false);
        }
    });
    return ShowTextbook;
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(0)))

/***/ }),

/***/ "./cms/templates/js/edit-chapter.underscore":
/***/ (function(module, exports) {

module.exports = "<div class=\"input-wrap field text required field-add-chapter-name chapter<%- order %>-name\n    <% if (error && error.attributes && error.attributes.name) { print('error'); } %>\">\n  <label for=\"chapter<%- order %>-name\"><%- gettext(\"Chapter Name\") %></label>\n  <input id=\"chapter<%- order %>-name\" name=\"chapter<%- order %>-name\" class=\"chapter-name short\" placeholder=\"<%- StringUtils.interpolate(gettext(\"Chapter {order}\"), {order: order}) %>\" value=\"<%- name %>\" type=\"text\">\n  <span class=\"tip tip-stacked\"><%- gettext(\"provide the title/name of the chapter that will be used in navigating\") %></span>\n</div>\n<div class=\"input-wrap field text required field-add-chapter-asset chapter<%- order %>-asset\n    <% if (error && error.attributes && error.attributes.asset_path) { print('error'); } %>\">\n  <label for=\"chapter<%- order %>-asset-path\"><%- gettext(\"Chapter Asset\") %></label>\n  <input id=\"chapter<%- order %>-asset-path\" name=\"chapter<%- order %>-asset-path\" class=\"chapter-asset-path\" placeholder=\"<%- StringUtils.interpolate(gettext(\"path/to/introductionToCookieBaking-CH{order}.pdf\"), {order: order}) %>\" value=\"<%- asset_path %>\" type=\"text\" dir=\"ltr\">\n  <span class=\"tip tip-stacked\"><%- gettext(\"upload a PDF file or provide the path to a Studio asset file\") %></span>\n<button class=\"action action-upload\"><%- gettext(\"Upload PDF\") %></button>\n</div>\n<a href=\"\" class=\"action action-close\"><span class=\"icon fa fa-times-circle\" aria-hidden=\"true\"></span> <span class=\"sr\"><%- gettext(\"delete chapter\") %></span></a>\n"

/***/ }),

/***/ "./node_modules/backbone-associations/backbone-associations-min.js":
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;(function(q,f){if(true)!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(1),__webpack_require__(2)], __WEBPACK_AMD_DEFINE_RESULT__ = function(g,i){return f(q,i,g)}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));else if("undefined"!==typeof exports){var g=require("underscore"),i=require("backbone");f(q,i,g);"undefined"!==typeof module&&module.exports&&(module.exports=i);exports=i}else f(q,q.Backbone,q._)})(this,function(q,f,g){var i,p,t,w,n,v,D,E,k,z,F,s={};i=f.Model;p=f.Collection;t=i.prototype;n=p.prototype;w=f.Events;f.Associations={VERSION:"0.6.2"};f.Associations.scopes=[];var G=function(){return k},
A=function(a){if(!g.isString(a)||1>g.size(a))a=".";k=a;D=RegExp("[\\"+k+"\\[\\]]+","g");E=RegExp("[^\\"+k+"\\[\\]]+","g")};try{Object.defineProperty(f.Associations,"SEPARATOR",{enumerable:!0,get:G,set:A})}catch(J){}f.Associations.Many=f.Many="Many";f.Associations.One=f.One="One";f.Associations.Self=f.Self="Self";f.Associations.SEPARATOR=".";f.Associations.getSeparator=G;f.Associations.setSeparator=A;f.Associations.EVENTS_BUBBLE=!0;f.Associations.EVENTS_WILDCARD=!0;f.Associations.EVENTS_NC=!1;A();
v=f.AssociatedModel=f.Associations.AssociatedModel=i.extend({relations:void 0,_proxyCalls:void 0,constructor:function(a,c){c&&c.__parents__&&(this.parents=[c.__parents__]);i.apply(this,arguments)},on:function(a,c,d){var b=w.on.apply(this,arguments);if(f.Associations.EVENTS_NC)return b;var l=/\s+/;g.isString(a)&&a&&!l.test(a)&&c&&(l=B(a))&&(s[l]="undefined"===typeof s[l]?1:s[l]+1);return b},off:function(a,c,d){if(f.Associations.EVENTS_NC)return w.off.apply(this,arguments);var b=/\s+/,l=this._events,
e={},h=l?g.keys(l):[],m=!a&&!c&&!d,i=g.isString(a)&&!b.test(a);if(m||i)for(var b=0,j=h.length;b<j;b++)e[h[b]]=l[h[b]]?l[h[b]].length:0;var p=w.off.apply(this,arguments);if(m||i){b=0;for(j=h.length;b<j;b++)(m=B(h[b]))&&(s[m]=l[h[b]]?s[m]-(e[h[b]]-l[h[b]].length):s[m]-e[h[b]])}return p},get:function(a){var c=this.__attributes__,d=t.get.call(this,a),c=c?x(d)?d:c[a]:d;return x(c)?c:this._getAttr.apply(this,arguments)},set:function(a,c,d){var b;g.isObject(a)||null==a?(b=a,d=c):(b={},b[a]=c);a=this._set(b,
d);this._processPendingEvents();return a},_set:function(a,c){var d,b,l,e,h=this;if(!a)return this;this.__attributes__=a;for(d in a)if(b||(b={}),d.match(D)){var f=H(d);e=g.initial(f);f=f[f.length-1];e=this.get(e);e instanceof i&&(e=b[e.cid]||(b[e.cid]={model:e,data:{}}),e.data[f]=a[d])}else e=b[this.cid]||(b[this.cid]={model:this,data:{}}),e.data[d]=a[d];if(b)for(l in b)e=b[l],this._setAttr.call(e.model,e.data,c)||(h=!1);else h=this._setAttr.call(this,a,c);delete this.__attributes__;return h},_setAttr:function(a,
c){var d;c||(c={});if(c.unset)for(d in a)a[d]=void 0;this.parents=this.parents||[];this.relations&&g.each(this.relations,function(b){var d=b.key,e=b.scope||q,h=this._transformRelatedModel(b,a),m=this._transformCollectionType(b,h,a),u=g.isString(b.map)?C(b.map,e):b.map,j=this.attributes[d],k=j&&j.idAttribute,o,r,n=!1;o=b.options?g.extend({},b.options,c):c;if(a[d]){e=g.result(a,d);e=u?u.call(this,e,m?m:h):e;if(x(e))if(b.type===f.Many)j?(j._deferEvents=!0,j[o.reset?"reset":"set"](e instanceof p?e.models:
e,o),h=j):(n=!0,e instanceof p?h=e:(h=this._createCollection(m||p,b.collectionOptions||(h?{model:h}:{})),h[o.reset?"reset":"set"](e,o)));else if(b.type===f.One)b=e instanceof i?e.attributes.hasOwnProperty(k):e.hasOwnProperty(k),m=e instanceof i?e.attributes[k]:e[k],j&&b&&j.attributes[k]===m?(j._deferEvents=!0,j._set(e instanceof i?e.attributes:e,o),h=j):(n=!0,e instanceof i?h=e:(o.__parents__=this,h=new h(e,o),delete o.__parents__));else throw Error("type attribute must be specified and have the values Backbone.One or Backbone.Many");
else h=e;r=a[d]=h;if(n||r&&!r._proxyCallback)r._proxyCallback||(r._proxyCallback=function(){return f.Associations.EVENTS_BUBBLE&&this._bubbleEvent.call(this,d,r,arguments)}),r.on("all",r._proxyCallback,this)}a.hasOwnProperty(d)&&this._setupParents(a[d],this.attributes[d])},this);return t.set.call(this,a,c)},_bubbleEvent:function(a,c,d){var b=d[0].split(":"),g=b[0],e="nested-change"==d[0],h="change"===g,m=d[1],u=-1,j=c._proxyCalls,b=b[1],n=!b||-1==b.indexOf(k),o;if(!e&&(n&&(F=B(d[0])||a),f.Associations.EVENTS_NC||
s[F])){if(f.Associations.EVENTS_WILDCARD&&/\[\*\]/g.test(b))return this;if(c instanceof p&&(h||b))u=c.indexOf(z||m);this instanceof i&&(z=this);b=a+(-1!==u&&(h||b)?"["+u+"]":"")+(b?k+b:"");f.Associations.EVENTS_WILDCARD&&(o=b.replace(/\[\d+\]/g,"[*]"));e=[];e.push.apply(e,d);e[0]=g+":"+b;f.Associations.EVENTS_WILDCARD&&b!==o&&(e[0]=e[0]+" "+g+":"+o);j=c._proxyCalls=j||{};if(this._isEventAvailable.call(this,j,b))return this;j[b]=!0;h&&(this._previousAttributes[a]=c._previousAttributes,this.changed[a]=
c);this.trigger.apply(this,e);f.Associations.EVENTS_NC&&(h&&this.get(b)!=d[2])&&(a=["nested-change",b,d[1]],d[2]&&a.push(d[2]),this.trigger.apply(this,a));j&&b&&delete j[b];z=void 0;return this}},_isEventAvailable:function(a,c){return g.find(a,function(a,b){return-1!==c.indexOf(b,c.length-b.length)})},_setupParents:function(a,c){a&&(a.parents=a.parents||[],-1==g.indexOf(a.parents,this)&&a.parents.push(this));c&&(0<c.parents.length&&c!=a)&&(c.parents=g.difference(c.parents,[this]),c._proxyCallback&&
c.off("all",c._proxyCallback,this))},_createCollection:function(a,c){var c=g.defaults(c,{model:a.model}),d=new a([],g.isFunction(c)?c.call(this):c);d.parents=[this];return d},_processPendingEvents:function(){this._processedEvents||(this._processedEvents=!0,this._deferEvents=!1,g.each(this._pendingEvents,function(a){a.c.trigger.apply(a.c,a.a)}),this._pendingEvents=[],g.each(this.relations,function(a){(a=this.attributes[a.key])&&a._processPendingEvents&&a._processPendingEvents()},this),delete this._processedEvents)},
_transformRelatedModel:function(a,c){var d=a.relatedModel,b=a.scope||q;d&&!(d.prototype instanceof i)&&(d=g.isFunction(d)?d.call(this,a,c):d);d&&g.isString(d)&&(d=d===f.Self?this.constructor:C(d,b));if(a.type===f.One){if(!d)throw Error("specify a relatedModel for Backbone.One type");if(!(d.prototype instanceof f.Model))throw Error("specify an AssociatedModel or Backbone.Model for Backbone.One type");}return d},_transformCollectionType:function(a,c,d){var b=a.collectionType,l=a.scope||q;if(b&&g.isFunction(b)&&
b.prototype instanceof i)throw Error("type is of Backbone.Model. Specify derivatives of Backbone.Collection");b&&!(b.prototype instanceof p)&&(b=g.isFunction(b)?b.call(this,a,d):b);b&&g.isString(b)&&(b=C(b,l));if(b&&!b.prototype instanceof p)throw Error("collectionType must inherit from Backbone.Collection");if(a.type===f.Many&&!c&&!b)throw Error("specify either a relatedModel or collectionType");return b},trigger:function(a){this._deferEvents?(this._pendingEvents=this._pendingEvents||[],this._pendingEvents.push({c:this,
a:arguments})):t.trigger.apply(this,arguments)},toJSON:function(a){var c={},d;c[this.idAttribute]=this.id;this.visited||(this.visited=!0,c=t.toJSON.apply(this,arguments),a&&a.serialize_keys&&(c=g.pick(c,a.serialize_keys)),this.relations&&g.each(this.relations,function(b){var f=b.key,e=b.remoteKey,h=this.attributes[f],i=!b.isTransient,b=b.serialize||[],k=g.clone(a);delete c[f];i&&(b.length&&(k?k.serialize_keys=b:k={serialize_keys:b}),d=h&&h.toJSON?h.toJSON(k):h,c[e||f]=g.isArray(d)?g.compact(d):d)},
this),delete this.visited);return c},clone:function(a){return new this.constructor(this.toJSON(a))},cleanup:function(a){a=a||{};g.each(this.relations,function(a){if(a=this.attributes[a.key])a._proxyCallback&&a.off("all",a._proxyCallback,this),a.parents=g.difference(a.parents,[this])},this);!a.listen&&this.off()},destroy:function(a){var a=a?g.clone(a):{},a=g.defaults(a,{remove_references:!0,listen:!0}),c=this;if(a.remove_references&&a.wait){var d=a.success;a.success=function(b){d&&d(c,b,a);c.cleanup(a)}}var b=
t.destroy.apply(this,[a]);a.remove_references&&!a.wait&&c.cleanup(a);return b},_getAttr:function(a){var c=this,d=this.__attributes__,a=H(a),b,f;if(!(1>g.size(a))){for(f=0;f<a.length;f++){b=a[f];if(!c)break;c=c instanceof p?isNaN(b)?void 0:c.at(b):d?x(c.attributes[b])?c.attributes[b]:d[b]:c.attributes[b]}return c}}});var H=function(a){return""===a?[""]:g.isString(a)?a.match(E):a||[]},B=function(a){if(!a)return a;a=a.split(":");return 1<a.length?(a=a[a.length-1],a=a.split(k),1<a.length?a[a.length-1].split("[")[0]:
a[0].split("[")[0]):""},C=function(a,c){var d,b=[c];b.push.apply(b,f.Associations.scopes);for(var i,e=0,h=b.length;e<h;++e)if(i=b[e])if(d=g.reduce(a.split(k),function(a,b){return a[b]},i))break;return d},I=function(a,c,d){var b,f;g.find(a,function(a){if(b=g.find(a.relations,function(b){return a.get(b.key)===c},this))return f=a,!0},this);return b&&b.map?b.map.call(f,d,c):d},x=function(a){return!g.isUndefined(a)&&!g.isNull(a)},y={};g.each(["set","remove","reset"],function(a){y[a]=p.prototype[a];n[a]=
function(c,d){this.model.prototype instanceof v&&this.parents&&(arguments[0]=I(this.parents,this,c));return y[a].apply(this,arguments)}});y.trigger=n.trigger;n.trigger=function(a){this._deferEvents?(this._pendingEvents=this._pendingEvents||[],this._pendingEvents.push({c:this,a:arguments})):y.trigger.apply(this,arguments)};n._processPendingEvents=v.prototype._processPendingEvents;n.on=v.prototype.on;n.off=v.prototype.off;return f});


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

},["./cms/static/js/factories/textbooks.js"])));
//# sourceMappingURL=textbooks.js.map