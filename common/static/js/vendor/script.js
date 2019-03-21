var window_W = 0;
var course_slider;

var main_slider;
var sub_slider;
var option_4 = {
  auto: true,
  autoHover: true,
  moveSlides: 1,
  minSlides: 4,
  maxSlides: 4,
  slideMargin: 0,
  slideWidth: 270,
  speed: 700,
  pager: false,
}

var option_2 = {
  auto: true,
  autoHover: true,
  moveSlides: 1,
  minSlides: 2,
  maxSlides: 2,
  slideMargin: 0,
  slideWidth: 270,
  speed: 700,
  pager: true,
}

var option_3 = {
  auto: true,
  autoHover: true,
  moveSlides: 1,
  minSlides: 3,
  maxSlides: 3,
  slideMargin: 0,
  slideWidth: 270,
  speed: 700,
  pager: true,
}

var option_1 = {
  auto: true,
  autoHover: true,
  moveSlides: 1,
  minSlides: 1,
  maxSlides: 1,
  slideMargin: 0,
  slideWidth: 422,
  speed: 700,
  pager: true,
}

$(window).load(function () {
  window_W = $(window).width();
  var agent = navigator.userAgent.toLowerCase();

  console.log("script.js :: document.ready !!!");
  console.log('browser ::' + navigator.userAgent);
  console.log('kr01_mainslider size check:::  ' + $('.kr01_mainslider').size());
  $('.kr01_mainslider').bxSlider({
    mode: 'horizontal',
    auto: true,
    autoHover: true,
    captions: true,
    controls: true,
    pager: ($('.kr01_mainslider li').length > 1) ? true : false,
    // slideWidth: 1730
  });

  var option_list = [option_1, option_2, option_3, option_4];

  for(var i=0; i < option_list.length; i++) {
    option_list[i].pager = ($("#main_slider li").length > option_list[i].maxSlides) ? true : false;
  }

  $(window).resize(slide_resize);
  if(window_W <= 471) {
    main_slider = $("#main_slider").bxSlider(option_1);
    sub_slider = $("#sub_slider").bxSlider(option_1);
  } else if(window_W < 720 && window_W > 471){
    main_slider = $("#main_slider").bxSlider(option_2);
    sub_slider = $("#sub_slider").bxSlider(option_2);
  } else if(window_W >= 720 && window_W < 991) {
    main_slider = $("#main_slider").bxSlider(option_3);
    sub_slider = $("#sub_slider").bxSlider(option_3);
  } else {
    main_slider = $("#main_slider").bxSlider(option_4);
    sub_slider = $("#sub_slider").bxSlider(option_4);
  }
});

function slide_resize() {
  window_W = $(window).width();
  if(window_W <= 471){
    main_slider.reloadSlider(option_1);
    sub_slider.reloadSlider(option_1);
  }else if (window_W < 720 && window_W > 471) {
    main_slider.reloadSlider(option_2);
    sub_slider.reloadSlider(option_2);
  } else if(window_W >= 720 && window_W < 991) {
    main_slider.reloadSlider(option_3);
    sub_slider.reloadSlider(option_3);
  } else {
    main_slider.reloadSlider(option_4);
    sub_slider.reloadSlider(option_4);
  }

}
