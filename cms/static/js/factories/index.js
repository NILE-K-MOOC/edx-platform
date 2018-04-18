define(['jquery.form', 'js/index', 'xmodule_js/common_static/js/vendor/jquery-ui.min'], function () {
    'use strict';
    return function (courseNames) {

        // DEBUG
        //console.log('courseNames --- s');
        //console.log(courseNames);
        //console.log('courseNames --- e');

        // 검색 자동 완성 (bug)
        /*
        $("#cms_text").autocomplete({
                source: courseNames
        });
        */

        // 강좌 검색 핵심 함수
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
                if (course_tag.indexOf(cms_text) == -1) {
                    $('.course-item').eq(i).hide()
                }
            }

            if (cms_text == "" || cms_text == null) {
                for (var i = 0; i < cnt; i++) {
                    $('.course-item').eq(i).show();
                }
            }
        }

        // 강좌 엔터 시 검색 이벤트
        $("*").keydown(function (event) {
            if (event.which === 13 && $("#cms_text").is(":focus") == true) {
                console.log("event call start");
                studio_search();
                console.log("event call end");
                $("#cms_text").blur();
            }
        });

        // 강좌 클릭 시 검색 이벤트
        $('#cms_search').click(function (event) {
            studio_search();
        });

        // -------------------------------------------------------> EDX 기존 로직 [s]
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
        // -------------------------------------------------------> EDX 기존 로직 [e]
    };
});