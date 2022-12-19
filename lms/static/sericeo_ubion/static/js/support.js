$(function(){

	//탭메뉴 
	function support_tabmenu(){
		var sectionIds = $('.support-tabmenu button');
		$(document).scroll(function(){
			let  t_tabmenu = $(".support-tabmenu").offset().top;
			let w_scroll = $(window).scrollTop();
			if(w_scroll >= t_tabmenu){$(".support-tabmenu").addClass("fix");}else{$(".support-tabmenu").removeClass("fix");}
			sectionIds.each(function(){
				var container = $(this).data('id');
				var containerOffset = $('section.'+container).offset().top;
				var containerHeight = $('section.'+container).outerHeight();
				var containerBottom = containerOffset + containerHeight;
				var scrollPosition = $(document).scrollTop();
				if(scrollPosition < containerBottom - 40 && scrollPosition >= containerOffset - 40){
					$(this).addClass('is-active');
				} else{
					$(this).removeClass('is-active');
				}
			});
		});
		sectionIds.on('click',function(){
			let offsettop = $('section.'+$(this).data('id')).offset().top;
			$('html').animate({scrollTop : offsettop - 35}, 600);
		});
	}support_tabmenu();

	$.get('../static/sericeo_ubion/support.txt').done(function(data){
		data.forEach((a,i) => {
			a.support.forEach((e,j) => {
				let desc = e.desc.replace(/(\n|\r\n)/g, '<br>');
				let title = e.title.replace(/(\n|\r\n)/g, '<br>');
				$("#support-list"+a.id).append(`
					<li>
						<article>
							<a href="${e.href}" target="_blank">
								<div class="over-view">
									<p><strong>${title}</strong></p>
									<p>${desc}</p>
									<p>강의 보기 <i></i></p>
								</div>
								<div class="thum"><img src="../static/sericeo_ubion/static/image/support/support${a.id}_thum${j+1}.jpg" alt="${title}"></div>
								<div class="title"><strong>${title}</strong></div>
							</a>
						</article>
					</li>
				`);
			});
			
		});
	});


});