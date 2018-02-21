;(function (define) {
    'use strict';
    define([
            'jquery',
            'underscore',
            'js/student_account/views/FormView'
        ],
        function($, _, FormView) {

        return FormView.extend({
            el: '#register-form',

            tpl: '#register-tpl',

            events: {
                'click .js-register': 'submitForm',
                'click .login-provider': 'thirdPartyAuth',
                'blur input': 'blur_validate'
            },

            formType: 'register',

            submitButton: '.js-register',

            blur_validate: function(event){
                var check_index = $(event.currentTarget).attr('name');
                var target_id = $(event.currentTarget).attr('id');
                var target_value = $(event.currentTarget).val();
                var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                var email = target_value;

                if (check_index == 'email' && !re.test(target_value)) {
                    $('.email').remove();
                    $('.submission-error h4').attr('class','hidden');
                    $('.submission-error').removeClass('hidden');
                    $('#'+target_id).attr('class','error');
                    $('#'+target_id).prev().attr('class','error');
                    $('.submission-error ul').append('<li class="error_flag email">이메일 주소 포맷이 잘 못 되었습니다.</li>');
                }
                else if(check_index == 'email' && target_value == '') {
                    $('.email').remove();
                    $('.submission-error h4').attr('class','hidden');
                    $('.submission-error').removeClass('hidden');
                    $('#'+target_id).attr('class','error');
                    $('#'+target_id).prev().attr('class','error');
                    $('.submission-error ul').append('<li class="error_flag email">이메일(Email) 항목을 입력해 주십시요.</li>');

                }
                else if( check_index == 'email' ) {
                    $('#'+target_id).removeClass('error');
                    $('#'+target_id).prev().removeClass('error');
                    $('.email').remove();
                }
                else if(check_index == 'name' && target_value == '') {
                    $('.name').remove();
                    $('.submission-error h4').attr('class','hidden');
                    $('.submission-error').removeClass('hidden');
                    $('#'+target_id).attr('class','error');
                    $('#'+target_id).prev().attr('class','error');
                    $('.submission-error ul').append('<li class="error_flag name">이름(Full name) 항목을 입력해 주십시요.</li>');
                }
                else if(check_index == 'name') {
                    $('#'+target_id).removeClass('error');
                    $('#'+target_id).prev().removeClass('error');
                    $('.name').remove();
                }
                else if(check_index == 'username' && target_value == '') {
                    $('.username').remove();
                    $('.submission-error h4').attr('class','hidden');
                    $('.submission-error').removeClass('hidden');
                    $('#'+target_id).attr('class','error');
                    $('#'+target_id).prev().attr('class','error');
                    $('.submission-error ul').append('<li class="error_flag username">아이디(Username) 항목을 입력해 주십시요.</li>');
                }
                else if(check_index == 'username') {
                    $('#'+target_id).removeClass('error');
                    $('#'+target_id).prev().removeClass('error');
                    $('.username').remove();
                }
                else if((check_index == 'password2' && target_value == '') || (check_index == 'password' && target_value == '')) {
                    $('.password2').remove();
                    $('.submission-error h4').attr('class','hidden');
                    $('.submission-error').removeClass('hidden');
                    $('.js-register').attr('disabled',true);
                    if(check_index == 'password') {
                        $('#'+target_id).addClass('error');
                        $('#'+target_id).prev().addClass('error');
                    }
                    else if(check_index == 'password2') {
                        $('#'+target_id).addClass('error');
                        $('#'+target_id).prev().prev().addClass('error');
                    }

                    $('.submission-error ul').append('<li class="error_flag password2">비밀번호(Password) 항목을 입력해 주십시요.</li>');
                }

                else if ((check_index == 'password2' &&  $('#register-password').val() != target_value) || (check_index == 'password' &&  $('#register-password2').val() != target_value)){
                    $('.password2').remove();
                    $('.submission-error h4').attr('class','hidden');
                    $('.submission-error').removeClass('hidden');
                    if(check_index == 'password') {
                        $('#'+target_id).addClass('error');
                        $('#'+target_id).prev().addClass('error');
                        $('#'+target_id).next().addClass('error');
                    }
                    else if(check_index == 'password2') {
                        $('#'+target_id).addClass('error');
                        $('#'+target_id).prev().addClass('error');
                        $('#'+target_id).prev().prev().addClass('error');
                    }
                    $('.submission-error ul').append('<li class="error_flag password2">비밀번호가 일치하지 않습니다.</li>');
                }
                else if (check_index == 'password2' || check_index == 'password'){
                    $('.password2').remove();
                    if(check_index == 'password') {
                        $('#'+target_id).removeClass('error');
                        $('#'+target_id).prev().removeClass('error');
                    }
                    else if(check_index == 'password2') {
                        $('#'+target_id).removeClass('error');
                        $('#'+target_id).prev().removeClass('error');
                        $('#'+target_id).prev().prev().removeClass('error');
                    }
                }

                if( $('.message-copy li').size() == 0) {
                    $('.js-register').attr('disabled',false);
                    $('.submission-error').addClass('hidden');
                }
                else {
                    $('.js-register').attr('disabled',true);
                    $('.submission-error').removeClass('hidden');
                }
            },

            preRender: function( data ) {
                this.providers = data.thirdPartyAuth.providers || [];
                this.hasSecondaryProviders = (
                    data.thirdPartyAuth.secondaryProviders && data.thirdPartyAuth.secondaryProviders.length
                );
                this.currentProvider = data.thirdPartyAuth.currentProvider || '';
                this.errorMessage = data.thirdPartyAuth.errorMessage || '';
                this.platformName = data.platformName;
                this.autoSubmit = data.thirdPartyAuth.autoSubmitRegForm;

                this.listenTo( this.model, 'sync', this.saveSuccess );
            },

            render: function( html ) {
                var fields = html || '';

                $(this.el).html(_.template(this.tpl)({
                    /* We pass the context object to the template so that
                     * we can perform variable interpolation using sprintf
                     */
                    context: {
                        fields: fields,
                        currentProvider: this.currentProvider,
                        errorMessage: this.errorMessage,
                        providers: this.providers,
                        hasSecondaryProviders: this.hasSecondaryProviders,
                        platformName: this.platformName
                    }
                }));

                this.postRender();

                if (this.autoSubmit) {
                    $(this.el).hide();
                    $('#register-honor_code').prop('checked', true);
                    this.submitForm();
                }

                return this;
            },

            thirdPartyAuth: function( event ) {
                var providerUrl = $(event.currentTarget).data('provider-url') || '';

                if ( providerUrl ) {
                    window.location.href = providerUrl;
                }
            },

            saveSuccess: function() {
                this.trigger('auth-complete');
            },

            saveError: function( error ) {
                $(this.el).show(); // Show in case the form was hidden for auto-submission
                this.errors = _.flatten(
                    _.map(
                        // Something is passing this 'undefined'. Protect against this.
                        JSON.parse(error.responseText || "[]"),
                        function(error_list) {
                            return _.map(
                                error_list,
                                function(error) { return '<li>' + error.user_message + '</li>'; }
                            );
                        }
                    )
                );
                this.setErrors();
                this.toggleDisableButton(false);
            },

            postFormSubmission: function() {
                if (_.compact(this.errors).length) {
                    // The form did not get submitted due to validation errors.
                    $(this.el).show(); // Show in case the form was hidden for auto-submission
                }
            }
        });
    });
}).call(this, define || RequireJS.define);
