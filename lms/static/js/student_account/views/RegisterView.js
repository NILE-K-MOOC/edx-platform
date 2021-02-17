(function (define) {
    'use strict';
    define([
            'jquery',
            'underscore',
            'gettext',
            'edx-ui-toolkit/js/utils/string-utils',
            'edx-ui-toolkit/js/utils/html-utils',
            'js/student_account/views/FormView',
            'text!templates/student_account/form_status.underscore'
        ],
        function (
            $, _, gettext,
            StringUtils,
            HtmlUtils,
            FormView,
            formStatusTpl
        ) {
            return FormView.extend({
                el: '#register-form',
                tpl: '#register-tpl',
                validationUrl: '/api/user/v1/validation/registration',
                events: {
                    'click .js-register': 'submitForm',
                    'click .login-provider': 'thirdPartyAuth',
                    'click input[required][type="checkbox"]': 'liveValidateHandler',
                    'blur input[required], textarea[required], select[required]': 'liveValidateHandler',
                    'blur input[name="subemail"], input[name="password2"]': 'liveValidateHandler2',
                    'focus input[required], textarea[required], select[required]': 'handleRequiredInputFocus',
                    'click .check-browser-version': 'checkBrowserVersion',
                    'click .identity': 'identity',
                    'click #kakao_identity': 'kakao_identity',
                    'click #all_agree': 'all_agree',
                    'click #kakao_form_submit': 'kakao_form_submit',
                    'click #kakao_confirm_submit': 'kakao_confirm_submit',
                    'click .kakao_close': 'kakao_close',

                },
                liveValidationFields: [
                    'name',
                    'username',
                    'password',
                    'email',
                    'confirm_email',
                    'country',
                    'honor_code',
                    'terms_of_service'
                ],
                formType: 'register',
                formStatusTpl: formStatusTpl,
                authWarningJsHook: 'js-auth-warning',
                defaultFormErrorsTitle: gettext('We couldn\'t create your account.'),
                submitButton: '.js-register',
                positiveValidationIcon: 'fa-check',
                negativeValidationIcon: 'fa-exclamation',
                successfulValidationDisplaySeconds: 3,
                // These are reset to true on form submission.
                positiveValidationEnabled: true,
                negativeValidationEnabled: true,

                preRender: function (data) {
                    this.providers = data.thirdPartyAuth.providers || [];
                    this.hasSecondaryProviders = (
                        data.thirdPartyAuth.secondaryProviders && data.thirdPartyAuth.secondaryProviders.length
                    );
                    this.currentProvider = data.thirdPartyAuth.currentProvider || '';
                    this.syncLearnerProfileData = data.thirdPartyAuth.syncLearnerProfileData || false;
                    this.errorMessage = data.thirdPartyAuth.errorMessage || '';
                    this.platformName = data.platformName;
                    this.autoSubmit = data.thirdPartyAuth.autoSubmitRegForm;
                    this.hideAuthWarnings = data.hideAuthWarnings;
                    this.autoRegisterWelcomeMessage = data.thirdPartyAuth.autoRegisterWelcomeMessage || '';
                    this.registerFormSubmitButtonText =
                        data.thirdPartyAuth.registerFormSubmitButtonText || _('Create Account');

                    this.listenTo(this.model, 'sync', this.saveSuccess);
                    this.listenTo(this.model, 'validation', this.renderLiveValidations);
                },


                renderFields: function (fields, className) {
                    var html = [],
                        i,
                        fieldTpl = this.fieldTpl;

                    html.push(HtmlUtils.joinHtml(
                        HtmlUtils.HTML('<div class="'),
                        className,
                        HtmlUtils.HTML('">')
                    ));
                    for (i = 0; i < fields.length; i++) {
                        html.push(HtmlUtils.template(fieldTpl)($.extend(fields[i], {
                            form: this.formType,
                            requiredStr: this.requiredStr,
                            optionalStr: this.optionalStr,
                            supplementalText: fields[i].supplementalText || '',
                            supplementalLink: fields[i].supplementalLink || ''
                        })));
                    }
                    html.push('</div>');
                    return html;
                },

                buildForm: function (data) {
                    var html = [],
                        i,
                        field,
                        len = data.length,
                        requiredFields = [],
                        optionalFields = [];

                    this.fields = data;

                    this.hasOptionalFields = false;
                    for (i = 0; i < len; i++) {
                        field = data[i];
                        if (field.errorMessages) {
                            // eslint-disable-next-line no-param-reassign
                            field.errorMessages = this.escapeStrings(field.errorMessages);
                        }

                        if (field.required) {
                            requiredFields.push(field);
                        } else {
                            if (field.type !== 'hidden') {
                                // For the purporse of displaying the optional field toggle,
                                // the form should be considered to have optional fields
                                // only if all of the optional fields are being rendering as
                                // input elements that are visible on the page.
                                this.hasOptionalFields = true;
                            }
                            optionalFields.push(field);
                        }
                    }

                    html = this.renderFields(requiredFields, 'required-fields');

                    html.push.apply(html, this.renderFields(optionalFields, 'optional-fields'));

                    this.render(html.join(''));
                },

                render: function (html) {

                    var org_list = function () {
                        var tmp = null;
                        $.ajax({
                            'async': false,
                            'type': "GET",
                            'global': false,
                            'url': "/api/get_org_list",
                            'data': {},
                            'success': function (data) {
                                tmp = data.result;

                            }
                        });
                        return tmp;
                    }();

                    var org_count = function () {
                        var tmp = null;
                        $.ajax({
                            'async': false,
                            'type': "GET",
                            'global': false,
                            'url': "/api/get_org_list",
                            'data': {},
                            'success': function (data) {
                                tmp = data.count;

                            }
                        });
                        return tmp;
                    }();


                    var fields = html || '',
                        formErrorsTitle = gettext('An error occurred.');

                    $(this.el).html(_.template(this.tpl)({
                        /* We pass the context object to the template so that
                         * we can perform variable interpolation using sprintf
                         */
                        context: {
                            org_list: org_list,
                            org_count: org_count,
                            fields: fields,
                            currentProvider: this.currentProvider,
                            syncLearnerProfileData: this.syncLearnerProfileData,
                            providers: this.providers,
                            hasSecondaryProviders: this.hasSecondaryProviders,
                            platformName: this.platformName,
                            autoRegisterWelcomeMessage: this.autoRegisterWelcomeMessage,
                            registerFormSubmitButtonText: this.registerFormSubmitButtonText
                        }
                    }));

                    this.postRender();

                    // Must be called after postRender, since postRender sets up $formFeedback.
                    if (this.errorMessage) {
                        this.renderErrors(formErrorsTitle, [this.errorMessage]);
                    } else if (this.currentProvider && !this.hideAuthWarnings) {
                        this.renderAuthWarning();
                    }

                    if (this.autoSubmit) {
                        $(this.el).hide();
                        $('#register-honor_code, #register-terms_of_service').prop('checked', true);
                        this.submitForm();
                    }

                    return this;
                },

                postRender: function () {


                    var inputs = this.$('.form-field'),
                        inputSelectors = 'input, select, textarea',
                        inputTipSelectors = ['tip error', 'tip tip-input'],
                        inputTipSelectorsHidden = ['tip error hidden', 'tip tip-input hidden'],
                        onInputFocus = function () {
                            // // Apply on focus styles to input
                            // $(this).find('label').addClass('focus-in')
                            //     .removeClass('focus-out');
                            //
                            // // Show each input tip
                            // $(this).children().each(function() {
                            //     if (inputTipSelectorsHidden.indexOf($(this).attr('class')) >= 0) {
                            //         $(this).removeClass('hidden');
                            //     }
                            // });
                        },
                        onInputFocusOut = function () {
                            // If input has no text apply focus out styles
                            // if ($(this).find(inputSelectors).val().length === 0) {
                            //     $(this).find('label').addClass('focus-out')
                            //         .removeClass('focus-in');
                            // }
                            //
                            // // Hide each input tip
                            // $(this).children().each(function() {
                            //     if (inputTipSelectors.indexOf($(this).attr('class')) >= 0) {
                            //         $(this).addClass('hidden');
                            //     }
                            // });
                        },
                        handleInputBehavior = function (input) {
                            // Initially put label in input
                            // if (input.find(inputSelectors).val().length === 0) {
                            //     input.find('label').addClass('focus-out')
                            //         .removeClass('focus-in');
                            // }
                            //
                            // // Initially hide each input tip
                            // input.children().each(function() {
                            //     if (inputTipSelectors.indexOf($(this).attr('class')) >= 0) {
                            //         $(this).addClass('hidden');
                            //     }
                            // });
                            //
                            // input.focusin(onInputFocus);
                            // input.focusout(onInputFocusOut);
                        },
                        handleAutocomplete = function () {
                            // $(inputs).each(function() {
                            //     var $input = $(this),
                            //         isCheckbox = $input.attr('class').indexOf('checkbox') !== -1;
                            //
                            //     if (!isCheckbox) {
                            //         if ($input.find(inputSelectors).val().length === 0
                            //             && !$input.is(':-webkit-autofill')) {
                            //             $input.find('label').addClass('focus-out')
                            //                 .removeClass('focus-in');
                            //         } else {
                            //             $input.find('label').addClass('focus-in')
                            //                 .removeClass('focus-out');
                            //         }
                            //     }
                            // });
                        };

                    FormView.prototype.postRender.call(this);
                    $('.optional-fields').addClass('');
                    // $('#toggle_optional_fields').change(function() {
                    //     window.analytics.track('edx.bi.user.register.optional_fields_selected');
                    //     $('.optional-fields').toggleClass('hidden');
                    // });

                    // We are swapping the order of these elements here because the honor code agreement
                    // is a required checkbox field and the optional fields toggle is a cosmetic
                    // improvement so that we don't have to show all the optional fields.
                    // xss-lint: disable=javascript-jquery-insert-into-target
                    $('.checkbox-optional_fields_toggle').insertAfter('.required-fields');
                    if (!this.hasOptionalFields) {
                        $('.checkbox-optional_fields_toggle').addClass('hidden');
                    }
                    // xss-lint: disable=javascript-jquery-insert-into-target
                    $('.checkbox-honor_code').insertAfter('.optional-fields');
                    // xss-lint: disable=javascript-jquery-insert-into-target
                    $('.checkbox-terms_of_service').insertAfter('.optional-fields');

                    // Clicking on links inside a label should open that link.
                    $('label a').click(function (ev) {
                        ev.stopPropagation();
                        ev.preventDefault();
                        window.open($(this).attr('href'), $(this).attr('target'));
                    });
                    $('.form-field').each(function () {
                        $(this).find('option:first').html('');
                    });
                    $(inputs).each(function () {
                        var $input = $(this),
                            isCheckbox = $input.attr('class').indexOf('checkbox') !== -1;
                        if ($input.length > 0 && !isCheckbox) {
                            handleInputBehavior($input);
                        }
                    });
                    setTimeout(handleAutocomplete, 1000);
                },

                hideRequiredMessageExceptOnError: function ($el) {
                    // We only handle blur if not in an error state.
                    if (!$el.hasClass('error')) {
                        this.hideRequiredMessage($el);
                    }
                },

                hideRequiredMessage: function ($el) {
                    this.doOnInputLabel($el, function ($label) {
                        $label.addClass('hidden');
                    });
                },

                doOnInputLabel: function ($el, action) {
                    var $label = this.getRequiredTextLabel($el);
                    action($label);
                },

                handleRequiredInputFocus: function (event) {
                    var $el = $(event.currentTarget);
                    // Avoid rendering for required checkboxes.
                    if ($el.attr('type') !== 'checkbox') {
                        this.renderRequiredMessage($el);
                    }
                    if ($el.hasClass('error')) {
                        this.doOnInputLabel($el, function ($label) {
                            $label.addClass('error');
                        });
                    }
                },

                renderRequiredMessage: function ($el) {
                    this.doOnInputLabel($el, function ($label) {
                        //$label.removeClass('hidden').text(gettext('(required)'));
                    });
                },

                getRequiredTextLabel: function ($el) {
                    return $('#' + $el.attr('id') + '-required-label');
                },

                renderLiveValidations: function ($el, decisions) {
                    var $label = this.getLabel($el),
                        $requiredTextLabel = this.getRequiredTextLabel($el),
                        $icon = this.getIcon($el),
                        $errorTip = this.getErrorTip($el),
                        name = $el.attr('name'),
                        type = $el.attr('type'),
                        isCheckbox = type === 'checkbox',
                        hasError = decisions.validation_decisions[name] !== '',
                        error = isCheckbox ? '' : decisions.validation_decisions[name];

                    if (hasError && this.negativeValidationEnabled) {
                        this.renderLiveValidationError($el, $label, $requiredTextLabel, $icon, $errorTip, error);
                    } else if (this.positiveValidationEnabled) {
                        this.renderLiveValidationSuccess($el, $label, $requiredTextLabel, $icon, $errorTip);
                    }
                },

                getLabel: function ($el) {
                    return this.$form.find('label[for=' + $el.attr('id') + ']');
                },

                getIcon: function ($el) {
                    //return $('#' + $el.attr('id') + '-validation-icon');
                    return $('#' + $el.attr('id'));
                },

                getErrorTip: function ($el) {
                    return $('#' + $el.attr('id') + '-validation-error-msg');
                },

                getFieldTimeout: function ($el) {
                    return $('#' + $el.attr('id')).attr('timeout-id') || null;
                },

                setFieldTimeout: function ($el, time, action) {
                    $el.attr('timeout-id', setTimeout(action, time));
                },

                clearFieldTimeout: function ($el) {
                    var timeout = this.getFieldTimeout($el);
                    if (timeout) {
                        clearTimeout(this.getFieldTimeout($el));
                        $el.removeAttr('timeout-id');
                    }
                },

                renderLiveValidationError: function ($el, $label, $req, $icon, $tip, error) {
                    this.removeLiveValidationIndicators(
                        $el, $label, $req, $icon,
                        'success', this.positiveValidationIcon
                    );
                    this.addLiveValidationIndicators(
                        $el, $label, $req, $icon, $tip,
                        'error', this.negativeValidationIcon, error
                    );
                    this.renderRequiredMessage($el);
                },

                renderLiveValidationSuccess: function ($el, $label, $req, $icon, $tip) {
                    var self = this,
                        validationFadeTime = this.successfulValidationDisplaySeconds * 1000;
                    this.removeLiveValidationIndicators(
                        $el, $label, $req, $icon,
                        'error', this.negativeValidationIcon
                    );
                    this.addLiveValidationIndicators(
                        $el, $label, $req, $icon, $tip,
                        'success', this.positiveValidationIcon, ''
                    );
                    this.hideRequiredMessage($el);

                    // Hide success indicators after some time.
                    this.clearFieldTimeout($el);
                    this.setFieldTimeout($el, validationFadeTime, function () {
                        self.removeLiveValidationIndicators(
                            $el, $label, $req, $icon,
                            'success', self.positiveValidationIcon
                        );
                        self.clearFieldTimeout($el);
                    });
                },

                addLiveValidationIndicators: function ($el, $label, $req, $icon, $tip, indicator, icon, msg) {
                    $el.addClass(indicator);
                    $label.addClass(indicator);
                    $req.addClass(indicator);
                    $icon.addClass(indicator + ' ' + icon);
                    $tip.text(msg);
                },

                removeLiveValidationIndicators: function ($el, $label, $req, $icon, indicator, icon) {
                    $el.removeClass(indicator);
                    $label.removeClass(indicator);
                    $req.removeClass(indicator);
                    $icon.removeClass(indicator + ' ' + icon);
                },

                thirdPartyAuth: function (event) {
                    var providerUrl = $(event.currentTarget).data('provider-url') || '';

                    if (providerUrl) {
                        window.location.href = providerUrl;
                    }
                },

                saveSuccess: function () {
                    this.trigger('auth-complete');
                },

                saveError: function (error) {
                    $(this.el).show(); // Show in case the form was hidden for auto-submission
                    this.errors = _.flatten(
                        _.map(
                            // Something is passing this 'undefined'. Protect against this.
                            JSON.parse(error.responseText || '[]'),
                            function (errorList) {
                                return _.map(
                                    errorList,
                                    function (errorItem) {
                                        return StringUtils.interpolate('<li>{error}</li>', {
                                            error: errorItem.user_message
                                        });
                                    }
                                );
                            }
                        )
                    );
                    this.renderErrors(this.defaultFormErrorsTitle, this.errors);
                    this.scrollToFormFeedback();
                    this.toggleDisableButton(false);
                },

                postFormSubmission: function () {
                    if (_.compact(this.errors).length) {
                        // The form did not get submitted due to validation errors.
                        $(this.el).show(); // Show in case the form was hidden for auto-submission
                    }
                },

                resetValidationVariables: function () {
                    this.positiveValidationEnabled = true;
                    this.negativeValidationEnabled = true;
                },

                renderAuthWarning: function () {
                    var msgPart1 = gettext('You\'ve successfully signed into %(currentProvider)s.'),
                        msgPart2 = gettext(
                            'We just need a little more information before you start learning with %(platformName)s.'
                        ),
                        fullMsg = _.sprintf(
                            msgPart1 + ' ' + msgPart2,
                            {currentProvider: this.currentProvider, platformName: this.platformName}
                        );

                    this.renderFormFeedback(this.formStatusTpl, {
                        jsHook: this.authWarningJsHook,
                        message: fullMsg
                    });
                },

                submitForm: function (event) { // eslint-disable-line no-unused-vars


                    $.ajax({
                        'type': "POST",
                        'url': "/org_check",
                        'data': {
                            'org_check': $('#org_chk').prop("checked"),
                            'org_value': $("#org_select_option").val()
                        }
                    });


                    var elements = this.$form[0].elements,
                        $el,
                        i;

                    // As per requirements, disable positive validation for submission.
                    this.positiveValidationEnabled = false;

                    for (i = 0; i < elements.length; i++) {
                        $el = $(elements[i]);

                        // Simulate live validation.
                        if ($el.attr('required')) {
                            $el.blur();
                        }
                    }

                    FormView.prototype.submitForm.apply(this, arguments);
                },

                getFormData: function () {
                    var obj = FormView.prototype.getFormData.apply(this, arguments),
                        $emailElement = this.$form.find('input[name=email]'),
                        $confirmEmail = this.$form.find('input[name=confirm_email]');

                    if ($confirmEmail.length) {
                        if (!$confirmEmail.val() || ($emailElement.val() !== $confirmEmail.val())) {
                            this.errors.push(StringUtils.interpolate('<li>{error}</li>', {
                                error: $confirmEmail.data('errormsg-required')
                            }));
                        }
                        obj.confirm_email = $confirmEmail.val();
                    }

                    return obj;
                },

                liveValidateHandler: function (event) {
                    var $el = $(event.currentTarget);
                    // Until we get a back-end that can handle all available
                    // registration fields, we do some generic validation here.
                    if (this.inLiveValidationFields($el)) {
                        if ($el.attr('type') === 'checkbox') {
                            this.liveValidateCheckbox($el);
                        } else {
                            this.liveValidate($el);
                        }
                    } else {
                        this.genericLiveValidateHandler($el);
                    }
                    // On blur, we do exactly as the function name says, no matter which input.
                    this.hideRequiredMessageExceptOnError($el);
                },

                liveValidateHandler2: function (event) {

                    var $el = $(event.currentTarget);

                    if ($el.attr("name") === 'subemail') {
                        let email1 = $("#register-email").val();
                        let email2 = $el.val();

                        $("#register-sub-email-validation-error").remove();

                        // 보조이메일을 입력했을 경우 일치한다면 경고 후 삭제
                        if (email2) {

                            // 이메일 형식이 아니라면 오류 처리
                            var emailRule = /^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;//이메일 정규식

                            if (!emailRule.test(email2)) {
                                $("div.email-subemail").find("span, input").each(function () {
                                    $(this).removeClass("success");
                                    $(this).addClass("error");
                                });

                            } else if (email1 == email2) {


                                var errorHtml = '<span id="register-sub-email-validation-error" aria-live="assertive">' +
                                    '<span id="register-email-validation-error-msg" class="tip error" >이메일과 보조 이메일은 같을 수 없습니다.</span>' +
                                    '</span>';

                                $("#register-subemail").after(errorHtml);

                                // div.email-subemail 안의 span 과 input 에서 error 클래스 추가
                                $("div.email-subemail").find(".label-text, .label-optional, input").each(function () {
                                    $(this).removeClass("success");
                                    $(this).addClass("error");
                                });

                            } else {
                                // div.email-subemail 안의 span 과 input 에서 success 클래스 추가 후 3초후 삭제

                                $("div.email-subemail").find("span, input").each(function () {
                                    $(this).removeClass("error");
                                    $(this).addClass("success");

                                    setTimeout(function () {
                                        $("div.email-subemail").find("span, input").each(function () {
                                            $(this).removeClass("success");
                                        });

                                    }, 2000);
                                });


                            }
                        }

                        console.log("check email: " + email1 + " : " + email2);

                    } else if ($el.attr("name") === 'password2') {
                        let pw1 = $("#register-password").val();
                        let pw2 = $el.val();

                        console.log("check password: " + pw1 == pw2);

                    }

                },

                liveValidate: function ($el) {
                    var data = {},
                        field,
                        i;
                    for (i = 0; i < this.liveValidationFields.length; ++i) {
                        field = this.liveValidationFields[i];
                        data[field] = $('#register-' + field).val();
                    }
                    FormView.prototype.liveValidate(
                        $el, this.validationUrl, 'json', data, 'POST', this.model
                    );
                },

                liveValidateCheckbox: function ($checkbox) {
                    var validationDecisions = {validation_decisions: {}},
                        decisions = validationDecisions.validation_decisions,
                        name = $checkbox.attr('name'),
                        checked = $checkbox.is(':checked'),
                        error = $checkbox.data('errormsg-required');
                    decisions[name] = checked ? '' : error;
                    this.renderLiveValidations($checkbox, validationDecisions);
                },

                genericLiveValidateHandler: function ($el) {
                    var elementType = $el.attr('type');
                    if (elementType === 'checkbox') {
                        // We are already validating checkboxes in a generic way.
                        this.liveValidateCheckbox($el);
                    } else {
                        this.genericLiveValidate($el);
                    }
                },

                genericLiveValidate: function ($el) {
                    var validationDecisions = {validation_decisions: {}},
                        decisions = validationDecisions.validation_decisions,
                        name = $el.attr('name'),
                        error = $el.data('errormsg-required');
                    decisions[name] = $el.val() ? '' : error;
                    this.renderLiveValidations($el, validationDecisions);
                },

                checkBrowserVersion: function () {
                    navigator.sayswho = (function () {
                        var ua = navigator.userAgent, tem,
                            M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
                        if (/trident/i.test(M[1])) {
                            tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
                            return 'IE ' + (tem[1] || '');
                        }
                        if (M[1] === 'Chrome') {
                            tem = ua.match(/\b(OPR|Edge)\/(\d+)/);
                            if (tem != null) return tem.slice(1).join(' ').replace('OPR', 'Opera');
                        }
                        M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
                        if ((tem = ua.match(/version\/(\d+)/i)) != null) M.splice(1, 1, tem[1]);
                        return M.join(' ');
                    })();

                    let v = navigator.sayswho.split(' '); // outputs: `Chrome 62`
                    let browser = v[0];
                    let no = v[v.length - 1];
                    let minNo = 0;
                    let link = '';
                    switch (browser) {
                        case 'Firefox':
                            minNo = 83;
                            link = 'https://www.mozilla.org/ko/firefox/new/';
                            break;
                        case 'Chrome':
                            minNo = 86;
                            link = 'https://www.google.co.kr/chrome/';
                            break;
                        case 'Opera':
                            minNo = 72;
                            link = 'https://www.opera.com/ko';
                            break;
                        case 'Edge':
                            minNo = 18;
                            link = 'https://www.microsoft.com/ko-kr/edge';
                            break;
                        case 'Safari':
                            minNo = 13;
                            link = 'https://safari.softonic.kr/mac';
                            break;
                        case 'IE':
                            minNo = 10;
                            link = 'https://www.microsoft.com/ko-kr/download/internet-explorer.aspx';
                            break;
                    }

                    console.log("check browser: " + browser + " - " + no);

                    if (Number(no) < minNo) {
                        console.log('downlaod link: ' + link);

                        // 기준 브라우저 버전 보다 낮은경우 알림
                        swal({
                            title: gettext("Check browser version"),
                            text: gettext("We recommend updating your browser."),
                            icon: "warning",
                            buttons: {
                                confirm: {
                                    text: gettext("Confirm"),
                                    value: true,
                                    className: "action action-primary"
                                }
                            }
                        }).then(function (isConfirm) {
                            console.log('isConfirm:' + isConfirm);

                            $(".info_div a").css({
                                "text-decoration": "none",
                                "color": "#222"
                            }).removeAttr("href");
                            $(".check-browser-version").remove();
                            $(".info_div").append("<div style='text-align: center; margin-top: 10px;'><a href='" + link + "' target='_blank'>" + gettext("Go to the browser download page") + "</a></div>");

                        });
                    } else {
                        $(".info_div a").css({
                            "text-decoration": "none",
                            "color": "#222"
                        }).removeAttr("href");
                        $(".check-browser-version").remove();

                        $(".info_div").append("<div style='text-align: center; margin-top: 10px;'>" + gettext("This is the latest version.") + "</div>");
                    }

                },

                identity: function () {
                    window.open('', 'popupNICE', 'width=450, height=550, top=100, left=100, fullscreen=no, menubar=no, status=no, toolbar=no, titlebar=yes, location=no, scrollbar=no');
                    document.form2.target = "popupNICE";
                    document.form2.submit();
                },

                kakao_identity: function () {

                    if ($("#kakao_form").css('display') == 'none') {
                        $("#kakao_form").show();
                    } else {
                        $("#kakao_form").hide();
                    }

                },

                kakao_form_submit: function () {

                    var year = $.trim($(".kakao_year_text").val()).replace(/\s+/g, '')
                    var gender = $.trim($(".kakao_gender_text").val()).replace(/\s+/g, '')
                    var phone = $.trim($(".kakao_phone_text").val()).replace(/\s+/g, '')
                    var name = $.trim($(".kakao_name_text").val()).replace(/\s+/g, '')

                    console.log("seon woo debug =======> s");
                    console.log(year);
                    console.log(gender);
                    console.log(phone);
                    console.log(name);
                    console.log("seon woo debug ======> e");
                    //
                    // if(name == ""){
                    //     alert("이름을 입력해주세요.");
                    //     $(".kakao_name_text").focus();
                    //     return;
                    // } else if(year == ""){
                    //     alert("생년월일을 입력해주세요.");
                    //     $(".kakao_year_text").focus();
                    //     return;
                    // } else if(gender == ""){
                    //     alert("성별을 입력해주세요.");
                    //     $(".kakao_gender_text").focus();
                    //     return;
                    // } else if(phone == ""){
                    //     alert("핸드폰번호을 입력해주세요.");
                    //     $(".kakao_phone_text").focus();
                    //     return;
                    // }
                    //
                    // // 숫자인지 체크
                    // if(isNaN(year) == true){
                    //     alert("올바른 생년월일을 입력해주세요.")
                    //     return;
                    // }else if(isNaN(gender) == true){
                    //     alert("올바른 성별을 입력해주세요.")
                    //     return;
                    // }else if(isNaN(phone) == true){
                    //     alert("올바른 핸드폰 번호를 입력해주세요.")
                    //     return;
                    // }
                    //
                    // if(year.length != 8){
                    //     alert("올바른 생년월일을 입력해주세요.")
                    //     return;
                    // }else if(phone.length != 11){
                    //     alert("올바른 핸드폰 번호를 입력해주세요.")
                    //     return;
                    // }
                    //
                    // var message = [];
                    //
                    // $("input:checkbox[name='kakao_agree']:not(:checked)").each(function () {
                    //     message.push($(this).parent().find("label").text())
                    // })
                    //
                    // if(message[0]){
                    //     alert(message[0] + "에 동의해 주십시오.")
                    //     return;
                    // }

                    $("#kakao_form").hide();
                    $("#kakao_confirm").show();

                    $.ajax({
                        'type': "GET",
                        'url': "/api/kakao/form",
                        'data': {
                            'name': name,
                            'year': year,
                            'gender': gender,
                            'phone': phone
                        },
                    }).done(function (data) {
                        if (data.success) {
                            $("#kakao_receiptId").val(data.receiptId)
                            $("#kakao_name").val(name)
                            $("#kakao_year").val(year)
                            $("#kakao_gender").val(gender)
                            $("#kakao_phone").val(phone)
                        } else {
                            swal("인증실패", "사용자 정보가 올바르지 않습니다.\n 확인 후 재시도 해주세요. \n 카카오톡 지갑에 가입하지 않으셨다면 \n 가입 후 이용 바랍니다.", "info");
                            $("#kakao_confirm").hide();
                        }
                    });
                },

                kakao_confirm_submit: function () {

                    $.ajax({
                        'type': "GET",
                        'url': "/api/kakao/confirm",
                        'data': {
                            'receiptId': $("#kakao_receiptId").val()
                        }
                    }).done(function (data) {
                        if (data) {
                            if (data.state == 1) {

                                var name = $("#kakao_name").val();
                                var gender = $("#kakao_gender").val();
                                var year = $("#kakao_year").val().substring(0, 4);

                                $.ajax({
                                    'type': "GET",
                                    'url': "/api/kakao/cert",
                                    'data': {
                                        'receiptId': $("#kakao_receiptId").val(),
                                        'name': name,
                                        'gender': gender,
                                        'year': year,
                                        'phone': $("#kakao_phone").val()
                                    }
                                }).done(function (data) {

                                    if (data.success) {
                                        if ($("#kakao_name").val()) {
                                            $("#register-name").val(name).prop("readonly", true);
                                        }
                                        if ($("#kakao_gender").val()) {

                                            if (gender == 1 || gender == 3) {
                                                $("#register-gender").val('m');
                                            } else if (gender == 2 || gender == 4) {
                                                $("#register-gender").val('f');
                                            }

                                            $("#register-gender option").attr('disabled', true);
                                        }
                                        if ($("#kakao_year").val()) {
                                            $("#register-year_of_birth").val(year);
                                            $("#register-year_of_birth option").attr('disabled', true);
                                        }

                                        $("#kakao_confirm").hide();

                                        $(".identity").text(gettext("Authentication complete")).prop("disabled", true);
                                        $("#kakao_identity").text(gettext("Authentication complete")).prop("disabled", true);
                                    }else{
                                        swal("인증오류", "앱에서 인증을 완료해주세요 \n 앱에서 알림이 오지 않았다면 \n 인증창 종료 후 다시 진행해 주시기 바랍니다.", "info");
                                    }

                                })

                            } else if (data.state == 2) {
                                swal("시간만료", "요청시간내에 인증처리가 되지 않았습니다. \n 다시 진행해 주시기 바랍니다.", "info");
                                return;
                            } else {
                                swal("인증오류", "앱에서 인증을 완료해주세요 \n 앱에서 알림이 오지 않았다면 \n 인증창 종료 후 다시 진행해 주시기 바랍니다.", "info");
                                return;
                            }
                        }
                    });
                },

                kakao_close: function () {

                    if ($("#kakao_form").css('display') == 'block') {
                        $("#kakao_form").hide();
                    } else {
                        $("#kakao_confirm").hide();
                    }

                    $("#kakao_name").val('');
                    $("#kakao_year").val('');
                    $("#kakao_gender").val('');
                    $("#kakao_phone").val('');

                },

                all_agree: function () {

                    if ($("input:checkbox[name='kakao_agree']:checked").length > 0) {
                        $("input:checkbox[name='kakao_agree']").prop("checked", false);
                    } else {
                        $("input:checkbox[name='kakao_agree']").prop("checked", true);
                    }

                }
            });
        });
}).call(this, define || RequireJS.define);
