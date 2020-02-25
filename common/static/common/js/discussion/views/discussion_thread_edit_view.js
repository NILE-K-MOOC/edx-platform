/* globals DiscussionTopicMenuView, DiscussionUtil */
(function () {
    'use strict';
    if (Backbone) {
        this.DiscussionThreadEditView = Backbone.View.extend({
            tagName: 'form',
            events: {
                submit: 'updateHandler',
                'click .post-cancel': 'cancelHandler'
            },

            attributes: {
                class: 'discussion-post edit-post-form'
            },

            initialize: function (options) {
                this.container = options.container || $('.thread-content-wrapper');
                this.mode = options.mode || 'inline';
                this.startHeader = options.startHeader;
                this.course_settings = options.course_settings;
                this.threadType = this.model.get('thread_type');
                this.topicId = this.model.get('commentable_id');
                this.context = options.context || 'course';
                _.bindAll(this, 'updateHandler', 'cancelHandler');
                return this;
            },

            render: function () {
                var formId = _.uniqueId('form-'),
                    threadTypeTemplate = edx.HtmlUtils.template($('#thread-type-template').html()),
                    $threadTypeSelector = $(threadTypeTemplate({form_id: formId}).toString()),
                    context,
                    mainTemplate = edx.HtmlUtils.template($('#thread-edit-template').html());
                context = $.extend({mode: this.mode, startHeader: this.startHeader}, this.model.attributes);
                edx.HtmlUtils.setHtml(this.$el, mainTemplate(context));
                this.container.append(this.$el);
                this.$submitBtn = this.$('.post-update');
                this.addField($threadTypeSelector);
                this.$('#' + formId + '-post-type-' + this.threadType).attr('checked', true);
                // Only allow the topic field for course threads, as standalone threads
                // cannot be moved.
                if (this.isTabMode()) {
                    this.topicView = new DiscussionTopicMenuView({
                        topicId: this.topicId,
                        course_settings: this.course_settings
                    });
                    this.addField(this.topicView.render());
                }
                DiscussionUtil.makeWmdEditor(this.$el, $.proxy(this.$, this), 'edit-post-body');
                return this;
            },

            addField: function ($fieldView) {
                this.$('.forum-edit-post-form-wrapper').append($fieldView);
                return this;
            },

            isTabMode: function () {
                return this.mode === 'tab';
            },

            save: function () {

                // xss 취약점 방어 소스

                var title = this.$('.edit-post-title').val(),
                    body = this.$('.edit-post-body textarea').val();

                var pattern_list = ['<script', '<iframe', ' FSCommand', ' onAbort', ' onActivate', ' onAfterPrint', ' onAfterUpdate', ' onBeforeActivate', ' onBeforeCopy', ' onBeforeCut',
                    ' onBeforeDeactivate', ' onBeforeEditFocus', ' onBeforePaste', ' onBeforePrint', ' onBeforeUnload', ' onBeforeUpdate', ' onBegin', ' onBlur', ' onBounce', ' onCellChange',
                    ' onChange', ' onClick', ' onContextMenu', ' onControlSelect', ' onCopy', ' onCut', ' onDataAvailable', ' onDataSetChanged', ' onDataSetComplete', ' onDblClick', ' onDeactivate',
                    ' onDrag', ' onDragEnd', ' onDragLeave', ' onDragEnter', ' onDragOver', ' onDragDrop', ' onDragStart', ' onDrop', ' onEnd', ' onError', ' onErrorUpdate', ' onFilterChange',
                    ' onFinish', ' onFocus', ' onFocusIn', ' onFocusOut', ' onHashChange', ' onHelp', ' onInput', ' onKeyDown', ' onKeyPress', ' onKeyUp', ' onLayoutComplete', ' onLoad',
                    ' onLoseCapture', ' onMediaComplete', ' onMediaError', ' onMessage', ' onMouseDown', ' onMouseEnter', ' onMouseLeave', ' onMouseMove', ' onMouseOut', ' onMouseOver', ' onMouseUp',
                    ' onMouseWheel', ' onMove', ' onMoveEnd', ' onMoveStart', ' onOffline', ' onOnline', ' onOutOfSync', ' onPaste', ' onPause', ' onPopState', ' onProgress', ' onPropertyChange',
                    ' onReadyStateChange', ' onRedo', ' onRepeat', ' onReset', ' onResize', ' onResizeEnd', ' onResizeStart', ' onResume', ' onReverse', ' onRowsEnter', ' onRowExit', ' onRowDelete',
                    ' onRowInserted', ' onScroll', ' onSeek', ' onSelect', ' onSelectionChange', ' onSelectStart', ' onStart', ' onStop', ' onStorage', ' onSyncRestored', ' onSubmit', ' onTimeError',
                    ' onTrackChange', ' onUndo', ' onUnload', ' onURLFlip', ' seekSegmentTime', 'document.cookie', 'prompt', 'confirm', 'alert'];

                var pattern = new RegExp(pattern_list.join('|'), 'ig');

                var _title = title.match(pattern);
                var _body = body.match(pattern);

                if (_title) {
                    _title.forEach(function (e) {
                        var re = new RegExp(e, 'g');
                        title = title.replace(re, e.slice(0, e.length).concat('*'));
                    });
                }

                if (_body) {
                    _body.forEach(function (e) {
                        var re = new RegExp(e, 'g');
                        body = body.replace(re, e.slice(0, e.length).concat('*'));
                    });
                }

                var threadType = this.$('.input-radio:checked').val(),
                    postData = {
                        title: title,
                        thread_type: threadType,
                        body: body
                    };

                // var pattern = /<script|<iframe|\.xml|\.xmp|\.on|\sonclick|\sondblclick|\sonmousedown|\sonmouseup|\sonmouseover|\sonmouseout|\sonmousemove|\sonkeydown|\sonkeyup|\sonkeypress|\sonsubmit|\sonreset|\sonchange|\sonfocus|\sonblur|\sonselect|\sonload|\sonreadystatechange|\sonDOMContentLoaded|\sonresize|\sonscroll|\sonunload/ig;

                var _body = body.match(pattern);

                if (_body) {
                    _body.forEach(function (e) {
                        var re = new RegExp(e, 'g');
                        // body = body.replace(re, '_'.concat(e));
                        body = body.replace(re, e.slice(0, e.length).concat('*'));
                    });
                }

                if (!body.trim().length) {
                    return;
                }

                if (this.topicView) {
                    postData.commentable_id = this.topicView.getCurrentTopicId();
                }

                return DiscussionUtil.safeAjax({
                    $elem: this.$submitBtn,
                    $loading: this.$submitBtn,
                    url: DiscussionUtil.urlFor('update_thread', this.model.id),
                    type: 'POST',
                    dataType: 'json',
                    data: postData,
                    error: DiscussionUtil.formErrorHandler(this.$('.post-errors')),
                    success: function () {
                        this.$('.edit-post-title').val('').attr('prev-text', '');
                        this.$('.edit-post-body textarea').val('').attr('prev-text', '');
                        this.$('.wmd-preview p').html('');
                        if (this.topicView) {
                            postData.courseware_title = this.topicView.getFullTopicName();
                        }
                        this.model.set(postData).unset('abbreviatedBody');
                        this.trigger('thread:updated');
                        if (this.threadType !== threadType) {
                            this.model.set('thread_type', threadType);
                            this.model.trigger('thread:thread_type_updated');
                            this.trigger('comment:endorse');
                        }
                    }.bind(this)
                });
            },

            updateHandler: function (event) {
                event.preventDefault();
                // this event is for the moment triggered and used nowhere.
                this.trigger('thread:update', event);
                this.save();
                return this;
            },

            cancelHandler: function (event) {
                event.preventDefault();
                this.trigger('thread:cancel_edit', event);
                this.remove();
                return this;
            }
        });
    }
}).call(window);
