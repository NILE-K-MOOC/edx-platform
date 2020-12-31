(function(define) {
    'use strict';
    define([
        'jquery',
        'underscore',
        'backbone',
        'common/js/utils/edx.utils.validate',
        'edx-ui-toolkit/js/utils/html-utils',
        'edx-ui-toolkit/js/utils/string-utils',
        'text!templates/student_account/form_errors.underscore'
    ], function($, _, Backbone, EdxUtilsValidate, HtmlUtils, StringUtils, formErrorsTpl) {
        return Backbone.View.extend({
            tagName: 'form',
            el: '',
            tpl: '',
            fieldTpl: '#form_field-tpl',
            formErrorsTpl: formErrorsTpl,
            formErrorsJsHook: 'js-form-errors',
            defaultFormErrorsTitle: gettext('An error occurred.'),
            events: {},
            errors: [],
            formType: '',
            $form: {},
            fields: [],
            liveValidationFields: [],
            // String to append to required label fields
            requiredStr: '',
            /*
                Translators: This string is appended to optional field labels on the student login, registration, and
                profile forms.
            */
            optionalStr: gettext('(optional)'),
            submitButton: '',

            initialize: function(data) {
                this.model = data.model;
                this.preRender(data);

                this.tpl = $(this.tpl).html();
                this.fieldTpl = $(this.fieldTpl).html();

                this.buildForm(data.fields);

                this.listenTo(this.model, 'error', this.saveError);
            },

            /* Allows extended views to add custom
             * init steps without needing to repeat
             * default init steps
             */
            preRender: function(data) {
                /* Custom code goes here */
                return data;
            },

            render: function(html) {
                var fields = html || '';

                $(this.el).html(_.template(this.tpl)({
                    fields: fields
                }));

                this.postRender();

                return this;
            },

            postRender: function() {
                var $container = $(this.el);
                this.$form = $container.find('form');
                this.$formFeedback = $container.find('.js-form-feedback');
                this.$submitButton = $container.find(this.submitButton);
            },

            buildForm: function(data) {
                var html = [],
                    i,
                    len = data.length,
                    fieldTpl = this.fieldTpl;

                this.fields = data;

                for (i = 0; i < len; i++) {
                    if (data[i].errorMessages) {
                        data[i].errorMessages = this.escapeStrings(data[i].errorMessages);
                    }

                    html.push(HtmlUtils.template(fieldTpl)($.extend(data[i], {
                        form: this.formType,
                        requiredStr: this.requiredStr,
                        optionalStr: this.optionalStr,
                        supplementalText: data[i].supplementalText || '',
                        supplementalLink: data[i].supplementalLink || ''
                    })));
                }

                this.render(html.join(''));
            },

            /* Helper method to toggle display
             * including accessibility considerations
             */
            element: {
                hide: function($el) {
                    if ($el) {
                        $el.addClass('hidden');
                    }
                },

                scrollTop: function($el) {
                    // Scroll to top of selected element
                    $('html,body').animate({
                        scrollTop: $el.offset().top
                    }, 'slow');
                },

                show: function($el) {
                    if ($el) {
                        $el.removeClass('hidden');
                    }
                }
            },

            escapeStrings: function(obj) {
                _.each(obj, function(val, key) {
                    obj[key] = _.escape(val);
                });

                return obj;
            },

            forgotPassword: function(event) {
                event.preventDefault();

                this.trigger('password-help');
            },

            getFormData: function(target) {
                if (target) {
                        var obj = {},
                            $form = this.$form,
                            $el,
                            $label,
                            errors = [],
                            test = {};
                        $el = $("input[name=" + target + "]");
                        $label = $form.find('label[for=' + $el.attr('id') + ']');

                        if (target) {
                            test = this.validate($el);
                            if (test.isValid) {
                                obj[target] = $el.attr('type') === 'checkbox' ? $el.is(':checked') : $el.val();
                                $el.removeClass('error');
                                $label.removeClass('error');
                            } else {
                                errors.push(test.message);
                                $("input").removeClass('error');
                                $("label").removeClass('error');
                                $el.addClass('error');
                                $label.addClass('error');
                            }
                        }

                    } else {
                        var obj = {},
                            $form = this.$form,
                            elements = $form[0].elements,
                            i,
                            len = elements.length,
                            $el,
                            $label,
                            key = '',
                            errors = [],
                            test = {};

                        for (i = 0; i < len; i++) {

                            $el = $(elements[i]);
                            $label = $form.find('label[for=' + $el.attr('id') + ']');
                            key = $el.attr('name') || false;

                            if (key) {
                                test = this.validate(elements[i]);
                                if (test.isValid) {
                                    obj[key] = $el.attr('type') === 'checkbox' ? $el.is(':checked') : $el.val();
                                    $el.removeClass('error');
                                    $label.removeClass('error');
                                } else {
                                    errors.push(test.message);
                                    $el.addClass('error');
                                    $label.addClass('error');
                                }
                            }
                        }
                    }
                    this.errors = _.uniq(errors);
                    return obj;
            },

            saveError: function(error) {
                this.errors = [
                    StringUtils.interpolate(
                            '<li>{error}</li>', {
                                error: error.responseText
                            }
                        )
                ];
                this.renderErrors(this.defaultFormErrorsTitle, this.errors);
                this.scrollToFormFeedback();
                this.toggleDisableButton(false);
            },

            /* Wrapper for renderFormFeedback provided for convenience since the majority of
             * our calls to renderFormFeedback are for rendering error messages.
             */
            renderErrors: function(title, errorMessages) {
                this.clearFormErrors();
                this.renderFormFeedback(this.formErrorsTpl, {
                    jsHook: this.formErrorsJsHook,
                    title: title,
                    messagesHtml: HtmlUtils.HTML(errorMessages.join(''))
                });
            },

            renderFormFeedback: function(template, context) {
                var tpl = HtmlUtils.template(template);
                HtmlUtils.prepend(this.$formFeedback, tpl(context));
            },

            /* Allows extended views to add non-form attributes
             * to the data before saving it to model
             */
            setExtraData: function(data) {
                return data;
            },

            submitForm: function(event,target) {

                $(window).unbind("beforeunload");
                $('.submission-error h4').removeClass('hidden');
                var data = this.getFormData(target);
                if (!_.isUndefined(event)) {
                    event.preventDefault();
                }

                this.toggleDisableButton(true);

                // 보조 이메일의 값이 동일하다면 오류 메세지 추가
                if($("#register-subemail").length && $("#register-email").val() == $("#register-subemail").val()){
                    this.errors.push("<li>"+ gettext('Secondary email must be different from email.') +"</li>");
                } else {
                    $(".email-subemail").find("*").each(function(){
                        $(this).removeClass("error");
                    });
                }

                // 비밀번호를 재입력값이 동일한지 확인하고 오류 메세지를 표시하도록 함
                if($("#register-password2").length && $("#register-password").val() != $("#register-password2").val()){
                    this.errors.push("<li>"+ gettext('is not correct bettween passwords') +"</li>");
                    $("label[for='register-password']").addClass("error");
                    $("#register-password2").addClass("error");
                }else{
                    $("label[for='register-password']").removeClass("error");
                    $("#register-password2").removeClass("error");
                }

                if (!_.compact(this.errors).length) {
                    data = this.setExtraData(data);
                    this.model.set(data);
                    this.model.save();
                    this.clearFormErrors();
                } else {
                    this.renderErrors(this.defaultFormErrorsTitle, this.errors);
                    this.scrollToFormFeedback();
                    this.toggleDisableButton(false);
                }

                this.postFormSubmission();
            },

            /* Allows extended views to add custom
             * code after form submission
             */
            postFormSubmission: function() {
                return true;
            },

            resetValidationVariables: function() {
                return true;
            },

            clearFormErrors: function() {
                var query = '.' + this.formErrorsJsHook;
                this.clearFormFeedbackItems(query);
            },

            clearFormFeedbackItems: function(query) {
                var $items = this.$formFeedback.find(query);
                if ($items.length > 0) {
                    $items.remove();
                }
            },

            /**
             * If a form button is defined for this form, this will disable the button on
             * submit, and re-enable the button if an error occurs.
             *
             * Args:
             *      disabled (boolean): If set to TRUE, disable the button.
             *
             */
            toggleDisableButton: function(disabled) {
                if (this.$submitButton) {
                    this.$submitButton.attr('disabled', disabled);
                }
            },

            scrollToFormFeedback: function() {
                var self = this;
                // Scroll to feedback container
                $('html,body').animate({
                    scrollTop: this.$formFeedback.offset().top
                }, 'slow', function() {
                    self.resetValidationVariables();
                });

                // Focus on the feedback container to ensure screen readers see the messages.
                this.$formFeedback.focus();
            },

            validate: function($el) {

                return EdxUtilsValidate.validate($el);
            },

            liveValidate: function($el, url, dataType, data, method, model) {

                $.ajax({
                    url: url,
                    dataType: dataType,
                    data: data,
                    method: method,
                    success: function(response) {
                        model.trigger('validation', $el, response);
                    }
                });
            },

            inLiveValidationFields: function($el) {
                var i,
                    name = $el.attr('name') || false;
                for (i = 0; i < this.liveValidationFields.length; ++i) {
                    if (this.liveValidationFields[i] === name) {
                        return true;
                    }
                }
                return false;
            }
        });
    });
}).call(this, define || RequireJS.define);
