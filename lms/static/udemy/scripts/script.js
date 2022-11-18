$(document).ready(function(){
	var posY = 0; //window.scrollTop담을 변수
	
	// 셀렉트박스 스타일 커스텀
	$("div[data-type=select] select").css("display","none");
	let selectFlag;
	$(".custom-select").on("click", function() {
		$(this).toggleClass("selected");
		if($(this).hasClass("selected")) {
			$(this).siblings(".custom-select-list").addClass("extend");
			$(this).siblings(".custom-select-list").show();
		} else {
			$(this).siblings(".custom-select-list").removeClass("extend");
			$(this).siblings(".custom-select-list").hide();
		}
	})

	$(".custom-select").on("focusin", function() {
	// $(".language > .custom-select").on("focusin", function() {
		$(this).siblings(".custom-select-list").show();
	});

	$(".custom-select").on("focusout", function() {
	// $(".language > .custom-select").on("focusout", function() {
		if(!selectFlag) {
		  $(this).siblings(".custom-select-list").hide();
		}
		$(this).removeClass("selected");
	});



	$(".custom-select-option").on("mouseenter", function() {
		selectFlag = true;
	});

	$(".custom-select-option").on("mouseout", function() {
		selectFlag = false;
	});

	$(".custom-select-option").on("click", function() {
		let value = $(this).attr("data-value");

		$(this).parent("ul").siblings("div.custom-select").find(".custom-select-text").text($(this).text());
		$(this).parent("ul").siblings(".select-origin").val(value);
		$(this).parent("ul.custom-select-list").hide();

		$(this).parent("ul").siblings(".select-origin").find("option").each(function(index, el) {
			if($(el).attr("value") == value) {
				$(el).attr("selected", "selected");
			} else {
				$(el).removeAttr("selected");
			}
		});
	});

	// top버튼
	$('[data-action=top]').click(function (e) {
		event.preventDefault();
		$('html, body').animate({ scrollTop: 0 }, 500);
	});

	// lazy loading
	$('.lazy_img').Lazy({
		effect: "fadeIn",
		effectTime:1000,
		// threshold: 0,
		onError: function(element) {
			console.log('error loading ' + element.data('src'));
		}
	});
	
	// 팝업 닫기 (box_popup에 data-role:popup, data-type구분)
	$("div[data-role=popup] button[data-role=close]").on("click",function() {
		var type = $(this).closest('div.box_popup').attr("data-type");
		closeModal(type);
	});
});

// open popup
function openPopupKmooc(target) {
	var target_class = ".box_popup."+target;
	$(target_class).hide();
	
	posY = $(window).scrollTop();

	$("html, body").addClass("not_scroll"); //overflow, fixed
	$("main").css("top",-posY); //body 최상단 div에 posY 값을 줌
	$(target_class).show(); //팝업띄우기
}

//팝업 닫기
function closeModal(target) {
	var target_class = $("div.box_popup."+target);

	$("html, body").removeClass("not_scroll"); //스크롤 해제
	var mainSteyl = $("main").prop("style");
	mainSteyl.removeProperty("top"); //메인 태그에 style-top제거
	$(window).scrollTop(posY); //팝업 띄우기 전 위치로
	$(target_class).hide();
}