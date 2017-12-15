define(['jquery.form', 'js/index'], function() {
    'use strict';
    return function () {
        // showing/hiding creation rights UI

        $('#cms_search').click(function(event){
            var cms_text = $('#cms_text').val();
            var cnt = $('.course-item').length;

            console.log(cms_text);

            for(var i=0; i<cnt; i++){
                $('.course-item').eq(i).show();
            }

            for(var i=0; i<cnt; i++){
                var course_tag = $('.course-item').eq(i).children('.course-link').children('.course-title').text();
                //if(cms_text != course_tag){
                if(course_tag.indexOf(cms_text) == -1){
                    $('.course-item').eq(i).hide()
                }
                console.log(course_tag);
            }

            if(cms_text=="" || cms_text==null){
                for(var i=0; i<cnt; i++){
                    $('.course-item').eq(i).show();
                }
            }

        });

        $('.show-creationrights').click(function(e) {
            e.preventDefault();
            $(this)
                .closest('.wrapper-creationrights')
                    .toggleClass('is-shown')
                .find('.ui-toggle-control')
                    .toggleClass('current');
        });

        var reloadPage = function () {
            location.reload();
        };

        var showError = function ()  {
            $('#request-coursecreator-submit')
                .toggleClass('has-error')
                .find('.label')
                    .text('Sorry, there was error with your request');
            $('#request-coursecreator-submit')
                .find('.fa-cog')
                    .toggleClass('fa-spin');
        };

        $('#request-coursecreator').ajaxForm({
            error: showError,
            success: reloadPage
        });

        $('#request-coursecreator-submit').click(function(event){
            $(this)
                .toggleClass('is-disabled is-submitting')
                .attr('aria-disabled', $(this).hasClass('is-disabled'))
                .find('.label')
                .text('Submitting Your Request');
        });
    };
});
