var window_W = 0;
var course_slider;

var main_slider;
var sub_slider;
var today_slider;
var footer_slider;

var slide_option = {
    auto: false,
    autoHover: true,
    moveSlides: 0,
    minSlides: 1,
    maxSlides: 1,
    slideMargin: 0,
    slideWidth: 1,
    speed: 700,
    pager: false,
    nextText: '<i class="fa fa-2x fa-chevron-right" aria-hidden="true" tabindex="-1"></i><span class="hidden_head">' + gettext('Next') + '</span>',
    prevText: '<i class="fa fa-2x fa-chevron-left" aria-hidden="true" tabindex="-1"></i><span class="hidden_head">' + gettext('Previous') + '</span>',
    onSliderLoad: function () {
        $('.kr01_movie_slider').css({'visibility': 'visible'});
        $('.bx-clone').find('article').prop('tabindex', '-1');
    },
    onSlideAfter: function () {
        $(".course-card-slider").children("li").each(function () {
            if ($(this).attr("aria-hidden") == "false") {
                $(this).find("article").prop("tabindex", "0");
            } else {
                $(this).find("article").prop("tabindex", "-1");
            }
        });
    }
};

var slide_footer = {
    mode: 'horizontal',
    adaptiveHeight: true,
    auto: false,
    autoHover: true,
    maxSlides: 5,
    minSlides: 5,
    pager: false,
    slideWidth: 250,
    height: 50,
    // slideMargin: 0,
    // nextSelector: '#ft_next',
    // prevSelector: '#ft_prev',
    nextText: '<i class="fa fa-chevron-right" aria-hidden="true"></i><span class="hidden_head">' + gettext('Next') + '</span>',
    prevText: '<i class="fa fa-chevron-left" aria-hidden="true"></i><span class="hidden_head">' + gettext('Previous') + '</span>',
};


$(window).load(function () {
    // 웹 접근성 추가
    dropdown_keyboard_access('.nav-community');

    $('.show-course-data').keydown(function (e) {
        if (e.keyCode === 13 || e.keyCode === 32) {
            show_course_popup();
        }
    });

    $('.close-course-data').keydown(function (e) {
        if (e.keyCode === 13 || e.keyCode === 32) {
            close_course_detail_popup();
        }
    });

    window_W = $(window).width();
    var agent = navigator.userAgent.toLowerCase();

    console.log("script.js :: document.ready !!!");
    console.log('browser ::' + navigator.userAgent);
    console.log('kr01_mainslider size check:::  ' + $('.kr01_mainslider').size());
    var mainSlider = $('.kr01_mainslider').bxSlider({
        mode: 'horizontal',
        auto: true,
        autoHover: true,
        controls: true,
        nextText: '<i class="fa fa-2x fa-chevron-right" aria-hidden="true"></i><span class="hidden_head">' + gettext('Next') + '</span>',
        prevText: '<i class="fa fa-2x fa-chevron-left" aria-hidden="true"></i><span class="hidden_head">' + gettext('Previous') + '</span>',
        // pager: ($('.kr01_mainslider li').length > 1) ? true : false,
        pager: false,
        touchEnabled : (navigator.maxTouchPoints > 0),
        onSliderLoad: function (currentIndex) {
            // $(".slider-txt").html($('.kr01_mainslider li').eq(currentIndex).find("img").attr("alt"));
            $('.kr01_mainslider_area').css({'visibility': 'visible'});
            $('.bx-clone').find('a').prop('tabindex', '-1');
        },
        onSlideBefore: function ($slideElement, oldIndex, newIndex) {
            $(".kr01_mainslider_captions .slider-txt").html($slideElement.find("img").attr("alt"));
        },
        onSlideAfter: function () {
            $(".kr01_mainslider").children("li").each(function () {
                if ($(this).attr("aria-hidden") == "false") {
                    $(this).find("a").prop("tabindex", "0");
                } else {
                    $(this).find("a").prop("tabindex", "-1");
                }
            });
        }
        // slideWidth: 1730
    });

    // 접근성 슬라이더 수정
    $('.kr01_mainslider_area li').focusin(function () {
        $('.kr01_mainslider_area li').removeClass('focus');
        $(this).parents('li').addClass('focus');
        mainSlider.stopAuto();
        if ($('.kr01_mainslider_area li:first-child').hasClass('focus')) {
            mainSlider.css('transform', 'translate3d(0, 0px, 0px)');
        }
    });

    $('.kr01_mainslider_area .bx-pager-link').focusin(function () {
        $(this).parent().focus();
    });

    $('article.main-course-card').keydown(function (e) {
        if (e.keyCode === 13 || e.keyCode === 32) {
            location.href = $(this).children('a').attr('href');
        }
    });


    if (window_W < 440) {
        slide_footer.maxSlides = 1;
        slide_footer.minSlides = 1;
    } else if (window_W >= 440 && window_W < 630) {
        slide_footer.maxSlides = 2;
        slide_footer.minSlides = 2;
    } else if (window_W >= 630 && window_W < 890) {
        slide_footer.maxSlides = 3;
        slide_footer.minSlides = 3;
    } else if (window_W >= 890 && window_W < 1250) {
        slide_footer.maxSlides = 4;
        slide_footer.minSlides = 4;
    } else {
        slide_footer.maxSlides = 5;
        slide_footer.minSlides = 5;
    }

    if (window_W <= 471) {
        slide_option.minSlides = 1;
        slide_option.maxSlides = 1;
        slide_option.slideWidth = 422;
    } else if (window_W < 720 && window_W > 471) {
        slide_option.minSlides = 2;
        slide_option.maxSlides = 2;
        slide_option.slideWidth = 290;
    } else if (window_W >= 720 && window_W < 991) {
        slide_option.minSlides = 3;
        slide_option.maxSlides = 3;
        slide_option.slideWidth = 290;
    } else {
        slide_option.minSlides = 4;
        slide_option.maxSlides = 4;
        slide_option.slideWidth = 290;
    }

    slide_option.pager = ($("#main_slider li").length > slide_option.maxSlides) ? true : false;

    if ($("#main_slider").size() != 0) {
        main_slider = $("#main_slider").bxSlider(slide_option);
    }
    if ($("#sub_slider").size() != 0) {
        sub_slider = $("#sub_slider").bxSlider(slide_option);
    }
    if ($("#today_slider").size() != 0) {
        today_slider = $("#today_slider").bxSlider(slide_option);
    }

    if($('.kr01-ft-familysite').length){
        footer_slider = $('.kr01-ft-familysite').bxSlider(slide_footer);
    }
    $(window).resize(slide_resize);

});

function slide_resize() {
    window_W = $(window).width();
    if (window_W <= 471) {
        slide_option.minSlides = 1;
        slide_option.maxSlides = 1;
        slide_option.slideWidth = 422;
    } else if (window_W < 720 && window_W > 471) {
        slide_option.minSlides = 2;
        slide_option.maxSlides = 2;
        slide_option.slideWidth = 290;
    } else if (window_W >= 720 && window_W < 991) {
        slide_option.minSlides = 3;
        slide_option.maxSlides = 3;
        slide_option.slideWidth = 290;
    } else {
        slide_option.minSlides = 4;
        slide_option.maxSlides = 4;
        slide_option.slideWidth = 290;
    }

    if (window_W < 440) {
        slide_footer.maxSlides = 1;
        slide_footer.minSlides = 1;
    } else if (window_W >= 440 && window_W < 630) {
        slide_footer.maxSlides = 2;
        slide_footer.minSlides = 2;
    } else if (window_W >= 630 && window_W < 890) {
        slide_footer.maxSlides = 3;
        slide_footer.minSlides = 3;
    } else if (window_W >= 890 && window_W < 1250) {
        slide_footer.maxSlides = 4;
        slide_footer.minSlides = 4;
    } else {
        slide_footer.maxSlides = 5;
        slide_footer.minSlides = 5;
    }

    if ($("#main_slider").size() != 0) {
        main_slider.reloadSlider(slide_option);
    }
    if ($("#sub_slider").size() != 0) {
        sub_slider.reloadSlider(slide_option);
    }
    if ($("#today_slider").size() != 0) {
        today_slider.reloadSlider(slide_option);
    }

    footer_slider.reloadSlider(slide_footer);
}

function dropdown_keyboard_access(nav) {
    $('.nav-community-link').click(function (e) {
        let k = e.keyCode || e.which;

        if (k === 1 || k === 13 || k === 32) {
            var menuParent = $(this).parents(nav);
            if (!$(menuParent).hasClass('dropdown-visible')) {
                $(menuParent).addClass('dropdown-visible');
            } else {
                $(menuParent).removeClass('dropdown-visible');
            }
        }
    });

}
