$(function(){

	//탭메뉴 
	function coursera_tabmenu(){
		var sectionIds = $('.coursera-tabmenu button');
		sectionIds.on('click',function(){
			let offsettop = $('section.'+$(this).data('id')).offset().top;
			$('html').animate({scrollTop : offsettop - 10}, 600);
		});
	}coursera_tabmenu();

	$.get('../static/coursera_ubion/coursera.txt').done(function(data){
		data.forEach((a,i) => {
			a.coursera.forEach((e,j) => {
				let desc = e.desc.replace(/(\n|\r\n)/g, '<br>');
				let title = e.title.replace(/(\n|\r\n)/g, '<br>');
				$("#coursera-list"+a.id).append(`
					<li>
						<article>
							<a href="${e.href}">
								<div class="over-view">
									<p><strong>${title}</strong></p>
									<p>${desc}</p>
									<p>강의 보기 <i></i></p>
								</div>

								<div class="thum"><img src="../static/coursera_ubion/static/image/coursera/coursera${a.id}_thum${j+1}.jpg" alt="${title}"></div>
								<div class="title"><strong>${title}</strong></div>
							</a>
						</article>
					</li>
				`);
			});
			
		});
	});


});