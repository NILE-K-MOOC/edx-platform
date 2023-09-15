(function (define) {
    'use strict';
    define([
        'jquery',
        'backbone',
        'jquery.url'
    ], function ($, Backbone) {
        return Backbone.Model.extend({
            defaults: {
                email: '',
                password: '',
                remember: false
            },

            ajaxType: '',
            urlRoot: '',

            initialize: function (attributes, options) {
                this.ajaxType = options.method;
                this.urlRoot = options.url;
            },

            sync: function (method, model) {
                var headers = {'X-CSRFToken': $.cookie('csrftoken')},
                    data = {},
                    analytics,
                    courseId = $.url('?course_id');

                // If there is a course ID in the query string param,
                // send that to the server as well so it can be included
                // in analytics events.
                if (courseId) {
                    analytics = JSON.stringify({
                        enroll_course_id: decodeURIComponent(courseId)
                    });
                }

                // Include all form fields and analytics info in the data sent to the server
                $.extend(data, model.attributes, {analytics: analytics});

                $.ajax({
                    url: model.urlRoot,
                    type: model.ajaxType,
                    data: data,
                    headers: headers,
                    success: function (d) {
                        if (d.ssodata) {
                            $('<form/>', {
                                id: 'form_for_redirect',
                                method: 'post',
                                action: "https://new.kmooc.kr/sso"
                            }).appendTo("body");

                            $('<input/>', {
                                type: 'hidden',
                                name: 'sdata',
                                value: d.ssodata
                            }).appendTo("#form_for_redirect");
                            $("#form_for_redirect").submit();
                        } else {
                            let search = document.location.search;
                            let search_array = search.substring(1).split("&");
                            let is_redirect = false;

                            for (let i in search_array) {
                                let str = search_array[i];

                                if (str === "") continue;

                                let key = str.split("=")[0];
                                let val = str.split("=")[1];

                                if (key === "callback") {
                                    is_redirect = true;

                                    $('<form/>', {
                                        id: 'form_for_redirect',
                                        method: 'post',
                                        action: decodeURIComponent(val)
                                    }).appendTo("body");

                                    $('<input/>', {
                                        type: 'hidden',
                                        name: 'data',
                                        value: d.data
                                    }).appendTo("#form_for_redirect");

                                    // console.log(decodeURIComponent(val));
                                    // console.log(d);
                                    // alert($("#form_for_redirect").html());

                                    $("#form_for_redirect").submit();
                                    // document.location.href = decodeURIComponent(val);
                                }
                            }
                            if (!is_redirect) model.trigger('sync');
                        }


                    },
                    error: function (error) {
                        model.trigger('error', error);
                    }
                });
            }
        });
    });
}).call(this, define || RequireJS.define);
