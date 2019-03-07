var window_W = 0;
var course_slider;
$(document).ready(function() {
	var agent = navigator.userAgent.toLowerCase();

	console.log("script.js :: document.ready !");
	console.log('browser ::' + navigator.userAgent);
  $(window).resize(slide_resize);

  course_slider = $('.course-card-slider').bxSlider({
    auto: true,
    autoHover: true,
    minSlides: 4,
    maxSlides: 4,
    slideWidth: 280,
    speed: 700
  });

});

function slide_resize() {

  window_W = $(window).width();
  if(window_W<=991) {
    // alert(window_W);
    course_slider.reloadSlider({
      auto: true,
      autoHover: true,
      minSlides: 2,
      maxSlides: 2,
      slideWidth: 250,
      speed: 700
    });
  } else if(window_W>768) {

  }
}
