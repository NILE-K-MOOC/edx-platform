(function(define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'common/js/components/views/tabbed_view',
        'edx-ui-toolkit/js/utils/html-utils',
        'js/student_account/views/account_section_view',
        'text!templates/student_account/account_settings.underscore'
    ], function(gettext, $, _, TabbedView, HtmlUtils, AccountSectionView, accountSettingsTemplate) {
        var AccountSettingsView = TabbedView.extend({

            navLink: '.account-nav-link',
            activeTab: 'aboutTabSections',
            accountSettingsTabs: [
                {
                    name: 'aboutTabSections',
                    id: 'about-tab',
                    label: gettext('Account Information'),
                    class: 'active',
                    tabindex: 0,
                    selected: true,
                    expanded: true
                },
                {
                    name: 'accountsTabSections',
                    id: 'accounts-tab',
                    label: gettext('Linked Accounts'),
                    tabindex: -1,
                    selected: false,
                    expanded: false
                }
                /*
                ,
                {
                    name: 'aaa',
                    id: 'aaa',
                    label: gettext('Survey'),
                    tabindex: -2,
                    selected: false,
                    expanded: false
                }
                */
            ],
            events: {
                'click .account-nav-link': 'switchTab',
                'click #nicecheck': 'nicecheck',
                'click #kakaocheck': 'kakao_identity',
                'click #all_agree': 'all_agree',
                'click #kakao_form_submit': 'kakao_form_submit',
                'click #kakao_confirm_submit': 'kakao_confirm_submit',
                'click .kakao_close': 'kakao_close',
                'click .agree_text': 'agree_text',
                'click .kakao_pop_close': 'kakao_pop_close',
                'keydown .account-nav-link': 'keydownHandler'
            },

            initialize: function(options) {
                this.options = options;
                _.bindAll(this, 'render', 'switchTab', 'renderFields', 'setActiveTab', 'showLoadingError');
            },

            render: function() {
console.log('account_settings_view.js render -------');
                var tabName,
                    view = this;
                HtmlUtils.setHtml(this.$el, HtmlUtils.template(accountSettingsTemplate)({
                    accountSettingsTabs: this.accountSettingsTabs
                }));
                _.each(view.accountSettingsTabs, function(tab) {
                    tabName = tab.name;
//console.log('account_settings_view.js render tabName-------', tabName);
                    view.renderSection(view.options.tabSections[tabName], tabName, tab.label);
                });
                this.renderFields();
                return this;
            },

            nicecheck: function(e) {
                if(confirm(gettext("Once you have verified your name, you can not cancel it. Do you want to proceed?"))){
                    window.open('', 'popupNICE', 'width=450, height=550, top=100, left=100, fullscreen=no, menubar=no, status=no, toolbar=no, titlebar=yes, location=no, scrollbar=no');
                    document.form2.target = "popupNICE";
                    document.form2.submit();
                }
            },

            kakao_identity: function () {

                $("#register_kakao_name").val('')
                $("#register_kakao_year").val('')
                $("#register_kakao_gender").val('')
                $("#register_kakao_phone").val('')

                if ($("#kakao_form").css('display') == 'none') {
                    $("#kakao_form").show();
                } else {
                    $("#kakao_form").hide();
                }

                $('textarea').keydown(function(event){
                    if(event.keyCode == 13){
                        return false;
                    }
                });

            },

            kakao_form_submit: function () {

                var year = $.trim($(".kakao_year_text").val()).replace(/\s+/g, '')
                var gender = $.trim($(".kakao_gender_text").val()).replace(/\s+/g, '')
                var phone = $.trim($(".kakao_phone_text").val()).replace(/\s+/g, '')
                var name = $.trim($(".kakao_name_text").val()).replace(/\s+/g, '')

                if(name == ""){
                    alert("이름을 입력해주세요.");
                    $(".kakao_name_text").focus();
                    return;
                } else if(year == ""){
                    alert("생년월일을 입력해주세요.");
                    $(".kakao_year_text").focus();
                    return;
                } else if(gender == ""){
                    alert("성별을 입력해주세요.");
                    $(".kakao_gender_text").focus();
                    return;
                } else if(phone == ""){
                    alert("핸드폰번호을 입력해주세요.");
                    $(".kakao_phone_text").focus();
                    return;
                }

                // 숫자인지 체크
                if(isNaN(year) == true){
                    alert("올바른 생년월일을 입력해주세요.");
                    return;
                }else if(isNaN(gender) == true){
                    alert("올바른 성별을 입력해주세요.");
                    return;
                }else if(isNaN(phone) == true){
                    alert("올바른 핸드폰 번호를 입력해주세요.");
                    return;
                }

                if(year.length != 8){
                    alert("올바른 생년월일을 입력해주세요.");
                    return;
                }else if(phone.length != 11){
                    alert("올바른 핸드폰 번호를 입력해주세요.");
                    return;
                }

                var message = [];

                $("input:checkbox[name='kakao_agree']:not(:checked)").each(function () {
                    message.push($(this).parent().find("label").text());
                })

                if(message[0]){
                    alert(message[0] + "에 동의해 주십시오.");
                    return;
                }

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
                        $("#kakao_receiptId").val(data.receiptId);
                        $("#kakao_name").val(name);
                        $("#kakao_year").val(year);
                        $("#kakao_gender").val(gender);
                        $("#kakao_phone").val(phone);
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

                            console.log(year)

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

                                    $.ajax({
                                        'type':"GET",
                                        'url': "/api/kakao/account_update"
                                    }).done(function(){
                                        location.reload();
                                    })
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

                $(".kakao_year_text").val('');
                $(".kakao_gender_text").val('');
                $(".kakao_phone_text").val('');
                $(".kakao_name_text").val('');

            },

            agree_text:function(event){

                console.log(event.currentTarget.id)

                if(event.currentTarget.id == 'privacy_text_button'){
                    $(".black_bg").show();
                    $("#privacy_text_area").show();
                }else if(event.currentTarget.id == 'third_party_text_button'){
                    $(".black_bg").show();
                    $("#third_party_area").show();
                }
            },

            all_agree: function () {

                if ($("input:checkbox[name='kakao_agree']:checked").length > 0) {
                    $("input:checkbox[name='kakao_agree']").prop("checked", false);
                } else {
                    $("input:checkbox[name='kakao_agree']").prop("checked", true);
                }

            },

            kakao_pop_close: function (event) {

                var current_id = event.target.parentElement.parentElement.parentElement.id;

                $("#"+current_id).hide();
                $(".black_bg").hide();
            },

            switchTab: function(e) {
                var $currentTab,
                    $accountNavLink = $('.account-nav-link');
//console.log('account_settings_view.js swithcTab -------');
                if (e) {
                    e.preventDefault();
                    $currentTab = $(e.target);
                    this.activeTab = $currentTab.data('name');
                    this.renderSection(this.options.tabSections[this.activeTab]);
                    this.renderFields();

                    _.each(this.$('.account-settings-tabpanels'), function(tabPanel) {
                        $(tabPanel).addClass('hidden');
                    });

                    $('#' + this.activeTab + '-tabpanel').removeClass('hidden');

                    $(this.navLink).removeClass('active');
                    $currentTab.addClass('active');

                    $(this.navLink).removeAttr('aria-describedby');

                    $accountNavLink.attr('tabindex', -1);
                    $accountNavLink.attr('aria-selected', false);
                    $accountNavLink.attr('aria-expanded', false);

                    $currentTab.attr('tabindex', 0);
                    $currentTab.attr('aria-selected', true);
                    $currentTab.attr('aria-expanded', true);

                }
            },

            setActiveTab: function() {
//console.log('account_settings_view.js setActiveTab -------');
                this.switchTab();
            },

            renderSection: function(tabSections, tabName, tabLabel) {
//console.log('account_settings_view.js renderSection -------');
                var accountSectionView = new AccountSectionView({
                    tabName: tabName,
                    tabLabel: tabLabel,
                    sections: tabSections,
                    el: '#' + tabName + '-tabpanel'
                });
                accountSectionView.render();
            },

            renderFields: function () {
                var view = this;
//console.log('account_settings_view.js renderFields -------');
                view.$('.ui-loading-indicator').addClass('is-hidden');

                _.each(view.$('.account-settings-section-body'), function (sectionEl, index) {

//console.log(view.options.tabSections[view.activeTab][index]);
//console.log(view.$('.account-settings-section-body').size());
//                    _.each(view.options.tabSections[view.activeTab][index].fields, function (field) {
//                        if (field.view.enabled) {
//                            $(sectionEl).append(field.view.render().el);
//                        }
//                    });

                    if(view.$('.account-settings-section-body').size() == 3 && index == 0){
                        if (view.$('.u-account-remove').size() < 1){
                            var html = "";
                            html += "<div class='u-field u-field-button u-field-password u-account-remove'>";
                            html += "    <div class='u-field-value field'>";
                            html += "        <span class='u-field-title field-label'>회원탈퇴</span>";
                            html += "        <a href='/remove_account_view'><button class='u-field-link u-field-link-title-password ' id='secession-btn' aria-describedby='u-field-message-help-password'>회원탈퇴하기</button></a>";
                            html += "    </div>";
                            html += "</div>";

                            $(sectionEl).append(html);
                         }
                    }

                });

                return this;
            },

            showLoadingError: function() {
                this.$('.ui-loading-error').removeClass('is-hidden');
            }
        });

//console.log('account_settings_view.js return -------');
        return AccountSettingsView;
    });
}).call(this, define || RequireJS.define);
