;(function (define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'backbone',
        'text!templates/student_account/account_settings_section.underscore'
    ], function (gettext, $, _, Backbone, sectionTemplate) {

        var AccountSectionView = Backbone.View.extend({

            initialize: function (options) {

                console.log('check 11 --------------------------- s');
                console.log(options);
                console.log('check 11 --------------------------- e');

                this.options = options;
            },

            render: function () {
                console.log('check 1 --------------------------- s');
                console.log(this.options.sections);
                console.log('check 1 --------------------------- e');

                this.$el.html(_.template(sectionTemplate)({
                    sections: this.options.sections,
                    activeTabName: this.options.activeTabName
                }));
            }
        });

        return AccountSectionView;
    });
}).call(this, define || RequireJS.define);
