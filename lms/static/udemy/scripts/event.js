$(document).ready(function(){
	// 구독권신청 페이지 - 강의 섹션
	// 선택된 태그
	var subscription_selected_tag = "program";
	var $main_subscription = $("main.subscription");
	var $section_info = $main_subscription.find("section.info");
	var $lecture_slides = $section_info.find("div.lecture_slides");
	var currentIndex = 0;
	$section_info.find("ul.box_tags > li.tag").on("click",function() {
		$(this).siblings('li').removeClass('selected');
		$(this).addClass('selected');
		subscription_selected_tag = $(this).attr('data-tag');

		if ($lecture_slides.find('div.item').not('.slick-cloned').length > 0) {
			$lecture_slides.find('div.item').not('.slick-cloned').each(function(index) {
				if (subscription_selected_tag) {
					var $this = $(this);
					if ($this.attr('data-card') == subscription_selected_tag) {
						currentIndex = index;
					}
				}
			})
		}
		
		$("div[data-slide=lecture]",$section_info).slick("slickGoTo", currentIndex); //해당 카드로 슬라이드 이동
	});
	
	// 슬라이드 좌/우버튼 클릭 시 해당 태그 selected
	$(document).on("click","div.lecture_slides button.slick-prev, div.lecture_slides button.slick-next",$lecture_slides, function() {
		var current_card = $lecture_slides.find('div.item.slick-current').attr("data-card");
		
		$section_info.find("ul.box_tags > li.tag").removeClass("selected");
		if ($section_info.find("ul.box_tags > li.tag[data-tag="+current_card+"]").length > 0) {
			$section_info.find("ul.box_tags > li.tag[data-tag="+current_card+"]").addClass("selected");
		}
	});
	
	$("div[data-slide=lecture]",$section_info).slick({
		autoplay:false,
		dots:false,
		speed:500,
		slidesToShow: 1,
		slidesToScroll: 1,
		initialSlide:0,
		responsive: [
			{
				breakpoint: 1200,
				settings: {
				slidesToShow: 1
				}
			},{
				breakpoint: 760,
				settings: {
				slidesToShow: 1,
				}
			},{
				breakpoint: 460,
				settings: {
				arrows:false
				}
			}
		]
	});
});