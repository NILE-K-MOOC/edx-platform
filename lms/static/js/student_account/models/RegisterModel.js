;(function (define) {
    'use strict';
    define(['jquery', 'backbone', 'jquery.url'],
        function($, Backbone) {

        return Backbone.Model.extend({
            defaults: {
                email: '',
                name: '',
                username: '',
                password: '',
                password2: '',
                level_of_education: '',
                gender: '',
                year_of_birth: '',
                mailing_address: '',
                goals: ''
            },
            ajaxType: '',
            urlRoot: '',

            initialize: function( attributes, options ) {
                console.log('initialize ==========')
                console.log(attributes)
                console.log(options)
                console.log('initialize ==========')
                this.ajaxType = options.method;
                this.urlRoot = options.url;
            },

            sync: function(method, model) {
                var headers = { 'X-CSRFToken': $.cookie('csrftoken') },
                    data = {},
                    courseId = $.url( '?course_id' );

                // If there is a course ID in the query string param,
                // send that to the server as well so it can be included
                // in analytics events.
                if ( courseId ) {
                    data.course_id = decodeURIComponent(courseId);
                }

                // Include all form fields and analytics info in the data sent to the server
                $.extend( data, model.attributes);

                function guid() {
                    function s4() {
                      return ((1 + Math.random()) * 0x10000 | 0).toString(16).substring(1);
                    }
                    return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
                }
                //test data
                var email_index = '';
                var name_index = '';
                var username_index = '';
                var password_index = '';
                console.log('Testindesx=====================')
                console.log(data)
                console.log(method)
                console.log(model)
                console.log('Testindesx=====================')
                $('input').each(function() {
                    var check_index = $(this).attr('name');
                    if( check_index == 'email') {
                        console.log($(this).attr('name'))
                        email_index = $(this).val();
                        name_index = guid();
                        username_index = guid().substring(10);
                        password_index = guid();
                    }
                    else if (check_index == 'name') {
                        console.log($(this).attr('name'))
                        email_index = guid() + '@example.com';
                        name_index = $(this).val();
                        username_index = guid().substring(10);
                        password_index = guid();
                    }
                    else if (check_index == 'username') {
                        console.log($(this).attr('name'))
                        email_index = guid() + '@example.com';
                        name_index = guid().substring(10);
                        username_index = $(this).val();
                        password_index = guid();
                    }
                })
                data = {
                    'email': email_index,
                    'name': name_index,
                    'username': username_index,
                    'password': password_index,
                    'password2': password_index
                }


                $.ajax({
                    url: model.urlRoot,
                    type: model.ajaxType,
                    data: data,
                    headers: headers,
                    success: function() {
                        model.trigger('sync');
                    },
                    error: function( error ) {
                        model.trigger('error', error);
                    }
                });
            }
        });
    });
}).call(this, define || RequireJS.define);
