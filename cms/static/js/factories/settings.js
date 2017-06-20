define([
    'jquery', 'js/models/settings/course_details', 'js/views/settings/main'
], function($, CourseDetailsModel, MainView) {
    'use strict';
    return function (detailsUrl, showMinGradeWarning) {
        var model;
        // highlighting labels when fields are focused in
        $('form :input')
            .focus(function() {
                // 설정일된 날짜가 과거이면 비활성화 한다. 170620 이종호.
                console.log('HERE 232 !!!!!!!!!!!!!');
                console.log(this.id);
                console.log($(this).val());
                $('label[for="' + this.id + '"]').addClass('is-focused');
            })
            .blur(function() {
                $('label').removeClass('is-focused');
            });

        model = new CourseDetailsModel();
        model.urlRoot = detailsUrl;
        model.fetch({
            success: function(model) {
                var editor = new MainView({
                    el: $('.settings-details'),
                    model: model,
                    showMinGradeWarning: showMinGradeWarning
                });
                editor.render();
            },
            reset: true
        });
    };
});
