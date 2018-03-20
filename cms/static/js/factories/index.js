define(['jquery.form', 'js/index', 'xmodule_js/common_static/js/vendor/jquery-ui.min'], function () {
    'use strict';
    return function (courseNames) {

        console.log('courseNames --- s');
        console.log(courseNames);
        console.log('courseNames --- e');

        $("#cms_text").off().unbind().autocomplete({
                source: courseNames,
                minLength: 0
            })
            .data("ui-autocomplete")._renderItem = function (ul, item) {
            return $("<div>")
                .data("ui-autocomplete-item", item)
                .append("<span>" + item.label + "</span>")
                .appendTo(ul);
        };

        console.log($("#cms_text").size());

        //console.log('courseNames --- s');
        //console.log(courseNames);
        //console.log('courseNames --- e');


        // showing/hiding creation rights UI

        function studio_search() {
            var cms_text = $('#cms_text').val();
            var cnt = $('.course-item').length;

            console.log('cms_text --> ');
            console.log(cms_text);

            for (var i = 0; i < cnt; i++) {
                $('.course-item').eq(i).show();
            }

            for (var i = 0; i < cnt; i++) {
                var course_tag = $('.course-item').eq(i).children('.course-link').children('.course-title').text();
                //if(cms_text != course_tag){
                if (course_tag.indexOf(cms_text) == -1) {
                    $('.course-item').eq(i).hide()
                }
                console.log(course_tag);
            }

            if (cms_text == "" || cms_text == null) {
                for (var i = 0; i < cnt; i++) {
                    $('.course-item').eq(i).show();
                }
            }
        }

        $("input").keydown(function (event) {
            if (event.which === 13) {
                studio_search();
            }
        });

        $('#cms_search').click(function (event) {
            studio_search();
        });

        $('.show-creationrights').click(function (e) {
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

        var showError = function () {
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

        $('#request-coursecreator-submit').click(function (event) {
            $(this)
                .toggleClass('is-disabled is-submitting')
                .attr('aria-disabled', $(this).hasClass('is-disabled'))
                .find('.label')
                .text('Submitting Your Request');
        });

        console.log('js/factories/index.js loaded 1  : ' + new Date());
        $("#cms_text").off().unbind();
        console.log('event remove done');
        $("#cms_text").autocomplete({
            source: courseNames
        });
        console.log('js/factories/index.js loaded 2  : ' + new Date());
    };
});
