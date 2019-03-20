var window_W = 0;
var course_slider;

var main_slider;
var sub_slider;
var option_4 = {
    auto: true,
    autoHover: true,
    minSlides: 4,
    maxSlides: 4,
    slideMargin: 0,
    slideWidth: 280,
    speed: 700
}

var option_2 = {
    auto: true,
    autoHover: true,
    minSlides: 2,
    maxSlides: 2,
    slideMargin: 0,
    slideWidth: 250,
    speed: 700
}
$(document).ready(function () {
    window_W = $(window).width();
    var agent = navigator.userAgent.toLowerCase();

    console.log("script.js :: document.ready !!!");
    console.log('browser ::' + navigator.userAgent);

    $(window).resize(slide_resize);
    if(window_W <= 991){
        main_slider = $("#main_slider").bxSlider(option_2);
        sub_slider = $("#sub_slider").bxSlider(option_2);
    } else {
        main_slider = $("#main_slider").bxSlider(option_4);
        sub_slider = $("#sub_slider").bxSlider(option_4);
    }
});

function slide_resize() {
    window_W = $(window).width();
    if (window_W <= 991) {
        main_slider.reloadSlider(option_2);
        sub_slider.reloadSlider(option_2);
    } else {
        main_slider.reloadSlider(option_4);

        sub_slider.reloadSlider(option_4);
    }

}
