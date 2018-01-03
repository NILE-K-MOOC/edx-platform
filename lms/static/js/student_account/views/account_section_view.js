(function(define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'backbone',
        'text!templates/student_account/account_settings_section.underscore'
    ], function(gettext, $, _, Backbone, sectionTemplate) {
        var AccountSectionView = Backbone.View.extend({

<<<<<<< HEAD
            initialize: function (options) {

                console.log('check 11 --------------------------- s');
                console.log(options);
                console.log('check 11 --------------------------- e');

=======
            initialize: function(options) {
>>>>>>> origin
                this.options = options;
                _.bindAll(this, 'render', 'renderFields');
            },

<<<<<<< HEAD
            render: function () {
                console.log('check 1 --------------------------- s');
                console.log(this.options.sections);
                console.log('check 1 --------------------------- e');

=======
            render: function() {
>>>>>>> origin
                this.$el.html(_.template(sectionTemplate)({
                    sections: this.options.sections,
                    tabName: this.options.tabName,
                    tabLabel: this.options.tabLabel
                }));

                this.renderFields();
            },

            renderFields: function() {
                var view = this;

                _.each(view.$('.' + view.options.tabName + '-section-body'), function(sectionEl, index) {
                    _.each(view.options.sections[index].fields, function(field) {
                        $(sectionEl).append(field.view.render().el);
                    });
                });
                return this;
            }
        });

        return AccountSectionView;
    });
}).call(this, define || RequireJS.define);
