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
