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
<<<<<<< HEAD
                {name: 'aboutTabSections', id: 'about-tab', label: gettext('Account Information'), class: 'active'},
                {name: 'accountsTabSections', id: 'accounts-tab', label: gettext('Linked Accounts')},
                //{name: 'ordersTabSections', id: 'orders-tab', label: gettext('Order History')}
            ],
            events: {
                'click .account-nav-link': 'changeTab',
                'click #nicecheck': 'nicecheck'
=======
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
                },
                {
                    name: 'ordersTabSections',
                    id: 'orders-tab',
                    label: gettext('Order History'),
                    tabindex: -1,
                    selected: false,
                    expanded: false
                }
            ],
            events: {
                'click .account-nav-link': 'switchTab',
                'keydown .account-nav-link': 'keydownHandler'
>>>>>>> origin
            },

            initialize: function(options) {
                this.options = options;
                _.bindAll(this, 'render', 'switchTab', 'setActiveTab', 'showLoadingError');
            },

<<<<<<< HEAD
            render: function () {

                console.log('render 3');

=======
            render: function() {
                var tabName,
                    view = this;
>>>>>>> origin
                HtmlUtils.setHtml(this.$el, HtmlUtils.template(accountSettingsTemplate)({
                    accountSettingsTabs: this.accountSettingsTabs
                }));
                _.each(view.accountSettingsTabs, function(tab) {
                    tabName = tab.name;
                    view.renderSection(view.options.tabSections[tabName], tabName, tab.label);
                });
                return this;
            },

<<<<<<< HEAD
            nicecheck: function(e) {
                if(confirm(gettext("Once you have verified your name, you can not cancel it. Do you want to proceed?"))){
                    window.open('', 'popupNICE', 'width=450, height=550, top=100, left=100, fullscreen=no, menubar=no, status=no, toolbar=no, titlebar=yes, location=no, scrollbar=no');
                    document.form2.target = "popupNICE";
                    document.form2.submit();
                }
            },

            changeTab: function(e) {
                var $currentTab;
=======
            switchTab: function(e) {
                var $currentTab,
                    $accountNavLink = $('.account-nav-link');

                if (e) {
                    e.preventDefault();
                    $currentTab = $(e.target);
                    this.activeTab = $currentTab.data('name');

                    _.each(this.$('.account-settings-tabpanels'), function(tabPanel) {
                        $(tabPanel).addClass('hidden');
                    });

                    $('#' + this.activeTab + '-tabpanel').removeClass('hidden');

                    $accountNavLink.attr('tabindex', -1);
                    $accountNavLink.attr('aria-selected', false);
                    $accountNavLink.attr('aria-expanded', false);
>>>>>>> origin

                    $currentTab.attr('tabindex', 0);
                    $currentTab.attr('aria-selected', true);
                    $currentTab.attr('aria-expanded', true);

                    $(this.navLink).removeClass('active');
                    $currentTab.addClass('active');
                }
            },

            setActiveTab: function() {
                this.switchTab();
            },

            renderSection: function(tabSections, tabName, tabLabel) {
                var accountSectionView = new AccountSectionView({
                    tabName: tabName,
                    tabLabel: tabLabel,
                    sections: tabSections,
                    el: '#' + tabName + '-tabpanel'
                });

                accountSectionView.render();
            },

<<<<<<< HEAD
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
=======
            showLoadingError: function() {
>>>>>>> origin
                this.$('.ui-loading-error').removeClass('is-hidden');
            }
        });

        return AccountSettingsView;
    });
}).call(this, define || RequireJS.define);
