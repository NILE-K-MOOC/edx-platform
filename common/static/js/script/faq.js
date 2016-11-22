/**
 * Created by dev on 2016. 11. 8..
 */
var window_W = 0;
$(document).ready(function(){
    window_W = $(window).width();
	$(window).resize(resize);
	var html = "";
	var head_html = "";
    var value_list = [];
    $.ajax({
        url : 'comm_faq',
        data : {
            method : 'faq_list',
			head_title : '학교 관련'
        }
    }).done(function(data){
		html="";
		head_html="";
        for(var i=0; i<data.length; i++){
            value_list = data[i].toString().split(',');
			//console.log(value_list[2]);
			//if(i == 0){
			//	head_html += "<a href='#' class='on'>"+value_list[2]+"</a>";
			//}
			//head_html += "<a href='#'>"+value_list[2]+"</a>";

			html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
            for(var j=1; j<value_list.length; j++){
				html += "<dd>";
				html += "<div>"+value_list[1]+"</div>";
				html += "</dd>";
            }
        }
		//console.log(head_html);
		//$('.faq-tab').html(head_html);
		$('.faq-list').html(html);

    });

	$(document).on('click', '.faq-tab a', function(){
		//alert($(this).text());
		$(".faq-tab a").removeClass("on");
		$(this).addClass("on");

		var html = "";
		var head_html = "";
		var value_list = [];
		var head_title = $(this).text();
		$.ajax({
			url : 'comm_faq',
			data : {
				method : 'faq_list',
				head_title : head_title
			}
		}).done(function(data){
			html="";
			head_html="";
			console.log(data.length);
			if(data != '' && data.length >3){
				for(var i=0; i<data.length; i++){
					value_list = data[i].toString().split(',');
					html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
					for(var j=1; j<value_list.length; j++){
						html += "<dd>";
						html += "<div>"+value_list[1]+"</div>";
						html += "</dd>";
					}
				}
				$('dl').css('height', '');
			}else if(data != '' && data.length <3){
				for(var j=0; j<data.length; j++){
					value_list = data[j].toString().split(',');
					html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
					html += "<dd>";
					html += "<div>"+value_list[1]+"</div>";
					html += "</dd>";
				}
				$('dl').css('height', '265px');
			}else{
				html += "<div style='text-align: center'>" +
						"<h3>저장된 데이터가 없습니다.</h3>" +
						"</div>";
				$('dl').css('height', '265px');
			}
			$('.faq-list').html(html);
		});
	});

	//$(document).on('click', '#search_btn', function(){
	//	var html = "";
	//	var head_html = "";
	//	var value_list = [];
	//	var head_title = $('.on').text().substring(3);
	//	var search = $('#search').val();
	//	if(search == '' || search == null){
	//		$(".faq-tab a").removeClass("on");
	//		$('#school').addClass("on");
    //
	//		$.ajax({
	//			url : 'comm_faq',
	//			data : {
	//				method : 'faq_list',
	//				head_title : '학교 관련'
	//				//head_title : head_title
	//			}
	//		}).done(function(data){
	//			html="";
	//			head_html="";
	//			for(var i=0; i<data.length; i++){
	//				value_list = data[i].toString().split(',');
	//				html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
	//				for(var j=1; j<value_list.length; j++){
	//					html += "<dd>";
	//					html += "<div>"+value_list[1]+"</div>";
	//					html += "</dd>";
	//				}
	//			}
	//			$('.faq-list').html(html);
	//		});
	//	}else{
	//		$.ajax({
	//			url : 'comm_faq',
	//			data : {
	//				method : 'faq_list',
	//				search : search,
	//				head_title : head_title
	//			}
	//		}).done(function(data){
	//			html="";
	//			head_html="";
	//			for(var i=0; i<data.length; i++){
	//				value_list = data[i].toString().split(',');
	//				html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
	//				for(var j=1; j<value_list.length; j++){
	//					html += "<dd>";
	//					html += "<div>"+value_list[1]+"</div>";
	//					html += "</dd>";
	//				}
	//			}
	//			$('.faq-list').html(html);
	//		});
	//	}
	//});




	window_W = $(window).width();


	$(document).on('click', '.faq-list dt > a', function(){
		$(".faq-list dt").removeClass("on");
		$(this).parent().addClass("on");
		return false;
	});

	$(document).on('click', '.univ-more', function(){
		$(this).toggleClass('on');
		if(window_W>768) {
			$(".university-listing [data-hidden]").toggle();
		} else {
			$(".university-listing [data-hidden=true]").toggle();
		}
		return false;
	});

	$(document).on('click', '.community-container-wrap > a', function(){
		$(".community-container-wrap > a").removeClass("on");
		$(this).addClass("on");
		return false;
	});

	$(document).on('click', '.kmooc-tab a', function(){
		$(".kmooc-tab a").removeClass("on");
		$(this).addClass("on");
		$(".kmooc-box").hide();
		$($(this).attr("href")).show();
		return false;
	});

});

function resize() {
	window_W = $(window).width();
}

$(document).on('click', '#question', function(){
	location.href='/comm_faqrequest'
});

function onKeyDown()
{
     if(event.keyCode == 13)
     {
		 search();
     }
}
$(document).on('click', '#search_btn',search);
function search(){
	var html = "";
	var head_html = "";
	var value_list = [];
	var head_title = $('.on').text().substring(3);
	var search = $('#search').val();
	if(search == '' || search == null){
		$(".faq-tab a").removeClass("on");
		$('#school').addClass("on");

		$.ajax({
			url : 'comm_faq',
			data : {
				method : 'faq_list',
				//head_title : '학교 관련'
				head_title : head_title
			}
		}).done(function(data){
			html="";
			head_html="";
			for(var i=0; i<data.length; i++){
				value_list = data[i].toString().split(',');
				html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
				for(var j=1; j<value_list.length; j++){
					html += "<dd>";
					html += "<div>"+value_list[1]+"</div>";
					html += "</dd>";
				}
			}
			$('.faq-list').html(html);
		});
	}else{
		$.ajax({
			url : 'comm_faq',
			data : {
				method : 'faq_list',
				search : search,
				head_title : head_title
			}
		}).done(function(data){
			html="";
			head_html="";
			for(var i=0; i<data.length; i++){
				value_list = data[i].toString().split(',');
				html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
				for(var j=1; j<value_list.length; j++){
					html += "<dd>";
					html += "<div>"+value_list[1]+"</div>";
					html += "</dd>";
				}
			}
			$('.faq-list').html(html);
		});
	}
}



