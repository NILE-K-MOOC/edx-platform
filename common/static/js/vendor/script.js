var window_W = 0;
var course_slider;

var main_slider;
var sub_slider;
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
  nextText: '<i class="fa fa-2x fa-chevron-right" aria-hidden="true"></i>',
  prevText: '<i class="fa fa-2x fa-chevron-left" aria-hidden="true"></i>',
  onSliderLoad: function(){
    $('.kr01_movie_slider').css({'visibility': 'visible'});
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
    nextText: '<i class="fa fa-chevron-right" aria-hidden="true"></i>',
    prevText: '<i class="fa fa-chevron-left" aria-hidden="true"></i>',
  };


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
    controls: true,
    nextText: '<i class="fa fa-2x fa-chevron-right" aria-hidden="true"></i>',
    prevText: '<i class="fa fa-2x fa-chevron-left" aria-hidden="true"></i>',
    pager: ($('.kr01_mainslider li').length > 1) ? true : false,
    onSliderLoad: function(currentIndex) {
      // $(".slider-txt").html($('.kr01_mainslider li').eq(currentIndex).find("img").attr("alt"));
      $('.kr01_mainslider_area').css({'visibility': 'visible'});
    },
    onSlideBefore: function($slideElement, oldIndex, newIndex) {
      $(".kr01_mainslider_captions .slider-txt").html($slideElement.find("img").attr("alt"));
    }
    // slideWidth: 1730
  });

  if(window_W < 440){
    slide_footer.maxSlides = 1;
    slide_footer.minSlides = 1;
  } else if(window_W >= 440 && window_W < 630){
    slide_footer.maxSlides = 2;
    slide_footer.minSlides = 2;
  } else if(window_W >= 630 && window_W < 890){
    slide_footer.maxSlides = 3;
    slide_footer.minSlides = 3;
  } else if(window_W >= 890 && window_W < 1250) {
    slide_footer.maxSlides = 4;
    slide_footer.minSlides = 4;
  } else {
    slide_footer.maxSlides = 5;
    slide_footer.minSlides = 5;
  }

  if(window_W <= 471) {
    slide_option.minSlides = 1;
    slide_option.maxSlides = 1;
    slide_option.slideWidth = 422;
  } else if(window_W < 720 && window_W > 471){
    slide_option.minSlides = 2;
    slide_option.maxSlides = 2;
    slide_option.slideWidth = 290;
  } else if(window_W >= 720 && window_W < 991) {
    slide_option.minSlides = 3;
    slide_option.maxSlides = 3;
    slide_option.slideWidth = 290;
  } else {
    slide_option.minSlides = 4;
    slide_option.maxSlides = 4;
    slide_option.slideWidth = 290;
  }

  slide_option.pager = ($("#main_slider li").length > slide_option.maxSlides) ? true : false;

  main_slider = $("#main_slider").bxSlider(slide_option);
  sub_slider = $("#sub_slider").bxSlider(slide_option);
  footer_slider = $('.kr01-ft-familysite').bxSlider(slide_footer);
  $(window).resize(slide_resize);
});

function slide_resize() {
  window_W = $(window).width();
  if(window_W <= 471){
    slide_option.minSlides = 1;
    slide_option.maxSlides = 1;
    slide_option.slideWidth = 422;
  }else if (window_W < 720 && window_W > 471) {
    slide_option.minSlides = 2;
    slide_option.maxSlides = 2;
    slide_option.slideWidth = 290;
  } else if(window_W >= 720 && window_W < 991) {
    slide_option.minSlides = 3;
    slide_option.maxSlides = 3;
    slide_option.slideWidth = 290;
  } else {
    slide_option.minSlides = 4;
    slide_option.maxSlides = 4;
    slide_option.slideWidth = 290;
  }

  if(window_W < 440){
    slide_footer.maxSlides = 1;
    slide_footer.minSlides = 1;
  } else if(window_W >= 440 && window_W < 630){
    slide_footer.maxSlides = 2;
    slide_footer.minSlides = 2;
  } else if(window_W >= 630 && window_W < 890){
    slide_footer.maxSlides = 3;
    slide_footer.minSlides = 3;
  } else if(window_W >= 890 && window_W < 1250) {
    slide_footer.maxSlides = 4;
    slide_footer.minSlides = 4;
  } else {
    slide_footer.maxSlides = 5;
    slide_footer.minSlides = 5;
  }

  main_slider.reloadSlider(slide_option);
  sub_slider.reloadSlider(slide_option);
  footer_slider.reloadSlider(slide_footer);

}
