;(function (define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'backbone',
        'edx-ui-toolkit/js/utils/html-utils',
        'js/student_account/views/account_section_view',
        'text!templates/student_account/account_settings.underscore'
    ], function (gettext, $, _, Backbone, HtmlUtils, AccountSectionView, accountSettingsTemplate) {

        var AccountSettingsView = Backbone.View.extend({

            navLink: '.account-nav-link',
            activeTab: 'aboutTabSections',
            accountSettingsTabs: [
                {name: 'aboutTabSections', id: 'about-tab', label: gettext('Account Information'), class: 'active'},
                {name: 'accountsTabSections', id: 'accounts-tab', label: gettext('Linked Accounts')},
            ],
            events: {
                'click .account-nav-link': 'changeTab',
                'click #nicecheck': 'nicecheck'
            },

            initialize: function (options) {
                this.options = options;
                _.bindAll(this, 'render', 'changeTab', 'renderFields', 'showLoadingError');
            },

            render: function () {

                console.log('render 3');

                HtmlUtils.setHtml(this.$el, HtmlUtils.template(accountSettingsTemplate)({
                    accountSettingsTabs: this.accountSettingsTabs
                }));
                this.renderSection(this.options.tabSections[this.activeTab]);
                return this;
            },

            nicecheck: function(e) {

                if(confirm(gettext("Once you have verified your name, you can not cancel it. Do you want to proceed?"))){
                    window.open('', 'popupNICE', 'width=450, height=550, top=100, left=100, fullscreen=no, menubar=no, status=no, toolbar=no, titlebar=yes, location=no, scrollbar=no');
                    document.form2.target = "popupNICE";
                    document.form2.submit();
                }
            },

            changeTab: function(e) {
                var $currentTab;

                e.preventDefault();
                $currentTab = $(e.target);
                this.activeTab = $currentTab.data('name');
                this.renderSection(this.options.tabSections[this.activeTab]);
                this.renderFields();

                $(this.navLink).removeClass('active');
                $currentTab.addClass('active');

                $(this.navLink).removeAttr('aria-describedby');
                $currentTab.attr('aria-describedby', 'header-subtitle-'+this.activeTab);
            },

            renderSection: function (tabSections) {
                var accountSectionView = new AccountSectionView({
                    activeTabName: this.activeTab,
                    sections: tabSections,
                    el: '.account-settings-sections'
                });

                accountSectionView.render();
            },

            renderFields: function () {
                var view = this;
                view.$('.ui-loading-indicator').addClass('is-hidden');

                _.each(view.$('.account-settings-section-body'), function (sectionEl, index) {
                    _.each(view.options.tabSections[view.activeTab][index].fields, function (field) {
                        if (field.view.enabled) {
                            $(sectionEl).append(field.view.render().el);
                        }
                    });

                    if(view.$('.account-settings-section-body').size() == 2 && index == 0){
                        var html = "";
                        html += "<div class='u-field u-field-button u-field-password'>";
                        html += "    <div class='u-field-value field'>";
                        html += "        <span class='u-field-title field-label'>회원탈퇴</span>";
                        html += "        <a href='/remove_account_view'><button class='u-field-link u-field-link-title-password ' id='secession-btn' aria-describedby='u-field-message-help-password'>회원탈퇴하기</button></a>";
                        html += "    </div>";
                        html += "</div>";

                        $(sectionEl).append(html);
                    }
                });

                return this;
            },

            showLoadingError: function () {
                this.$('.ui-loading-indicator').addClass('is-hidden');
                this.$('.ui-loading-error').removeClass('is-hidden');
            }
        });

        return AccountSettingsView;
    });
}).call(this, define || RequireJS.define);
