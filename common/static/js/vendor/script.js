var window_W = 0;

$(document).ready(function() {
	var agent = navigator.userAgent.toLowerCase();

	console.log("script.js :: document.ready !");
	console.log('browser ::' + navigator.userAgent);
	window_W = $(window).width();
	$(window).resize(resize);
	/***
	 $(".univ-more").on("click", function() {
		$(this).toggleClass('on');
		if(window_W>768) {
			$(".university-listing [data-hidden]").toggle();
		} else {
			$(".university-listing [data-hidden=true]").toggle();
		}
		return false;
	});
	 ***/
	$(".community-container-wrap > a").on("click", function() {
		//$(".community-container-wrap > a").removeClass("on");
		//$(this).addClass("on");
		//return false;
	});

	$(".faq-list dt > a").on("click", function() {
		$(".faq-list dt").removeClass("on");
		$(this).parent().addClass("on");
		return false;
	});

	$(".kmooc-tab a").on("click", function() {
		$(".kmooc-tab a").removeClass("on");
		$(this).addClass("on");
		$(".kmooc-box").hide();
		$($(this).attr("href")).show();
		return false;
	});

	$(".main-tab").click(function (e) {
		e.preventDefault();
		$(".main-tab").removeClass("on");
		$(this).addClass("on");
		var cla_id = $(this).attr('id');
		$(".course-classfy").css({'display': 'none'});
		$(".course-classfy#" + cla_id).css({'display': 'block'});

	});

	$('.slider').each(function() {
		var $this = $(this);
		var $group = $this.find('.slide_group');
		var $slides = $this.find('.slide');
		var bulletArray = [];
		var currentIndex = 0;
		var timeout;


		function move(newIndex) {
			var animateLeft, slideLeft;

			advance();

			if ($group.is(':animated') || currentIndex === newIndex) {
				return;
			}

			bulletArray[currentIndex].removeClass('active');
			bulletArray[newIndex].addClass('active');

			if (newIndex > currentIndex) {
				slideLeft = '100%';
				animateLeft = '-100%';
			} else {
				slideLeft = '-100%';
				animateLeft = '100%';
			}

			$slides.eq(newIndex).css({
				display: 'block',
				left: slideLeft
			});
			$group.animate({
				left: animateLeft
			}, function() {
				$slides.eq(currentIndex).css({
					display: 'none'
				});
				$slides.eq(newIndex).css({
					left: 0
				});
				$group.css({
					left: 0
				});
				currentIndex = newIndex;
			});
		}

		function advance() {
			clearTimeout(timeout);
			timeout = setTimeout(function() {
				if (currentIndex < ($slides.length - 1)) {
					move(currentIndex + 1);
				} else {
					move(0);
				}
			}, 4000);
		}

		$('.next_btn').on('click', function() {
			if (currentIndex < ($slides.length - 1)) {
				move(currentIndex + 1);
			} else {
				move(0);
			}
		});

		$('.previous_btn').on('click', function() {
			if (currentIndex !== 0) {
				move(currentIndex - 1);
			} else {
				move(3);
			}
		});

		$.each($slides, function(index) {
			if(index.length == 0){
				var $button = $('');
			}else{
				if ( (navigator.appName == 'Netscape' && navigator.userAgent.search('Trident') != -1) || (agent.indexOf("msie") != -1) ) {
					var $button = $('<div style="display: inline-flex; position: relative; max-width: 80%; width: 80%; justify-content: space-around; align-items: center;"><a class="slide_btn" style="position: relative;" id=zone'+index+'><span style="text-align: center;">'+$("#pop_title"+index).val()+'</span></a></div>');
				} else if ((agent.indexOf("safari") != -1 && agent.indexOf("chrome") == -1)){
					var $button = $('<div style="display: inline-flex; position: relative; max-width: 80%; width: 80%; justify-content: space-around; align-items: center;"><a class="slide_btn" style="left: 0;" id=zone'+index+'><span style="text-align: center;">'+$("#pop_title"+index).val()+'</span></a></div>');
				}
				else {
					var $button = $('<div style="display: inline-flex; position: relative; max-width: 80%; width: 80%; justify-content: space-around; align-items: center;"><a class="slide_btn" id=zone'+index+'><span style="text-align: center;">'+$("#pop_title"+index).val()+'</span></a></div>');
				}
			}

			if (index === currentIndex) {
				$button.addClass('active');
			}
			$button.on('click', function() {
				move(index);
			}).appendTo('.slide_buttons');
			bulletArray.push($button);
		});

		advance();
	});

});


var univ_bx;
$(window).load(function() {
	console.log("script.js :: window.load !");

	//univ list random
	var idx = 0;
	var newHtml = "";
	var univArr = new Array();
	$(".university-listing-item").each(function(index){
		univArr.push("<li class='university-listing-item'>" + $(this).html() + "</li>");
	});

	$.each(univArr, function(){
		idx = Math.floor(Math.random()*univArr.length);
		newHtml += univArr[idx];
		univArr.splice(idx, 1);
	});

	$(".university-listing").html(newHtml).show();

	if($(".slider-back").length>0) {
		$(".header-slider").bxSlider({
			pager : false,
			mode : "fade",
			auto : true,
			controls : false,
			speed : 1000
		});
	}

	if($(".university-listing").length>0) {
		univ_bx = $(".university-listing").bxSlider({
			pager : false,
			auto : false,
			controls : true,
			minSlides: 5,
			maxSlides: 5,
			slideMargin: 0,
			slideWidth : 250
		});
	}
});

function resize() {
	window_W = $(window).width();
	if(window_W<=768) {
		univ_bx.reloadSlider({
			pager : false,
			auto : false,
			controls : true,
			minSlides: 3,
			maxSlides: 3,
			slideMargin: 0,
			slideWidth : 250
		});
	} else if(window_W>768) {
		univ_bx.reloadSlider({
			pager : false,
			auto : false,
			controls : true,
			minSlides: 5,
			maxSlides: 5,
			slideMargin: 0,
			slideWidth : 250
		});
	}
}
