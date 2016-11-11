/**
 * Created by dev on 2016. 11. 8..
 */
var window_W = 0;
$(document).ready(function(){
    window_W = $(window).width();
	$(window).resize(resize);
	var html = "";
    var value_list = [];
    $.ajax({
        url : 'comm_faq',
        data : {
            method : 'faq_list'
        }
    }).done(function(data){
		html="";
        for(var i=0; i<data.length; i++){
            value_list = data[i].toString().split(',');
			//console.log(value_list[0]);
			html += "<dt><a href='#' >"+value_list[0]+"</a></dt>";
            for(var j=1; j<value_list.length; j++){
				html += "<dd>";
				html += "<div>"+value_list[j]+"</div>";
				html += "</dd>";
            }
        }
		//console.log(html);
		$('.faq-list').html(html);
    });

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
	alert('dd');
});