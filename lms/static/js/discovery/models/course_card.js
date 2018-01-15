;(function (define) {

define(['backbone'], function (Backbone) {
    'use strict';

    return Backbone.Model.extend({
        defaults: {
            modes: [],
            course: '',
            enrollment_start: '',
            number: '',
            content: {
                display_name: '',
                number: ''
            },
            start: '',
            image_url: '',
            org: '',
            id: '',
            status: ''
        }
    });

});

})(define || RequireJS.define);
