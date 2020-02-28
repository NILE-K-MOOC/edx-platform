define(['jquery.form', 'js/index'], function () {
    'use strict';
    return function (courseNames) {

        // for case insensitive
        $.expr[":"].contains = $.expr.createPseudo(function (arg) {
            return function (elem) {
                return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
            };
        });

        var search_data = {
            "course_tab": courses_list($(".courses .course-title")),
            "archived_tab": courses_list($('.archived-courses .course-title')),
            "libraries_tab": courses_list($('.libraries .course-title'))
        };
        // 검색 자동 완성

        // let title_list = $(".course-title:visible").map(function(){return this.innerText});
        //
        // console.log(title_list);
        //
        // for(let i=0; title_list.length; i++){
        //     console.log(title_list[i]);
        // }

        let titles = $(".course-title:visible").map(function () {
            return $(this).text()
        }).get();

        $("#cms_text").autocomplete({
            source: titles,
            appendTo: '.search_div'
        });

        $('#course-index-tabs li').click(function () {
            // 탭 아이디
            var clickId = $(this).attr('id');
            // 이전탭 검색 초기화
            $("#cms_text").val('');
            studio_search();
            // search_data에 탭 아이디로 값을 가져와 변경
            if ($(this).hasClass('active')) {
                $("#cms_text").autocomplete(
                    "option", {
                        source: function (request, response) {
                            var term = $.ui.autocomplete.escapeRegex(request.term)
                                , startsWithMatcher = new RegExp("^" + term, "i")
                                , startsWith = $.grep(search_data[clickId], function (value) {
                                return startsWithMatcher.test(value.label || value.value || value);
                            })
                                , containsMatcher = new RegExp(term, "i")
                                , contains = $.grep(search_data[clickId], function (value) {
                                return $.inArray(value, startsWith) < 0 &&
                                    containsMatcher.test(value.label || value.value || value);
                            });

                            response(startsWith.concat(contains));


                        },
                        appendTo: '.search_div'
                    }
                )
            }
        });

        // 강좌 검색 핵심 함수
        function studio_search() {
            console.time('studio_search');

            var cms_text = $('#cms_text').val();
            // var cnt = $('.course-item').length;

            if (cms_text) {
                $(".course-title:visible").parents('.course-item').hide();
                $(".course-title:contains(" + cms_text + ")").parents('.course-item').show();
            } else {
                $(".course-title").parents('.course-item').show();
            }
            setTimeout(function () {
                $("#cms_text").focus();
            }, 100);


            /*
            for (var i = 0; i < cnt; i++) {
                $('.course-item').eq(i).show();
            }

            for (var i = 0; i < cnt; i++) {
                var course_tag = $('.course-item').eq(i).children('a').children('.course-title').text();
                if (course_tag.indexOf(cms_text) == -1) {
                    $('.course-item').eq(i).hide();
                }
            }

            if (cms_text == "" || cms_text == null) {
                for (var i = 0; i < cnt; i++) {
                    $('.course-item').eq(i).show();
                }
            }
            */

            console.timeEnd('studio_search');
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

        $("#cms_text").on('autocompleteselect', function (e, ui) {
            $("#cms_text").val(ui.item.value);
            studio_search();
            console.log('You selected: ' + ui.item.value);
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
    };
});

function courses_list(courseTab) {
    var course_list = [];
    for (var i = 0; i < courseTab.length; i++) {
        var title = [courseTab][0][i].textContent;
        if ($.inArray(title, course_list) === -1) course_list.push(title)
    }

    return course_list;
}
