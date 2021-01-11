/**
 * Created by dev on 2016. 11. 8..
 */
var total_page = "";
var cur_page = "";
var start_page =1;
$(document).ready(function(){
    var value_list = [];
    var html = "";
    var html2 = "";
    //var date_list = [];
    $.ajax({
        url : '/comm_notice',
        data : {
            method : 'notice_list'
        }
    }).done(function(data){
        html = "";
        for(var i = 0; i < data.length; i++){
            html += "<li class='tbody'>";
            html += "<span class='no'>"+(data[i][0]-i)+"</span>";
            if(data[i][5] == 1){
                html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
            }else{
                html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
            }
            html += "<span class='date'>"+data[i][2]+"</span>";
            total_page = data[i][3];
            html += "</li>"
        }
        $('#tbody').html(html);
        html2 += "<a href='#' class='first' id='first' title='처음으로'>first</a>";
        html2 += "<a href='#' class='prev' id='prev' title='이전'>prev</a>";
        for(var t=0;t<total_page; t++){
            if(t==0){
                html2 += "<a href='#' class='current' id='"+(t+1)+"' title='"+(t+1)+" 페이지'>"+(t+1)+"</a>"
            }
            else{
                html2 += "<a href='#' id='"+(t+1)+"' title='"+(t+1)+" 페이지'>"+(t+1)+"</a>"
            }
        }
        html2 += "<a href='#' class='next' id='next' title='다음'>next</a>";
        html2 += "<a href='#' class='last' id='last' title='마지막으로'>last</a>";
        $('.paging').html(html2);
    });

    //페이지 클릭시 처리
    $('.paging').click(function(e){
        var click_el = e.target.text;
        //alert($('.current').text());
        cur_page = $('.current').text();
        //if ($.isNumeric(click_el)|| click_el == 'first' || click_el == 'prev' || click_el == 'next' || click_el == 'last'){

        if ($.isNumeric(click_el)){
            $('.current').removeClass('current');
            $('#'+click_el+'').addClass('current');

            $.ajax({
                url : '/comm_notice',
                data : {
                    method : 'notice_list',
                    cur_page : click_el
                }
            }).done(function(data){
                //console.log(data);
                html = "";
                for(var i = 0; i < data.length; i++){
                    html += "<li class='tbody'>";
                    html += "<span class='no'>"+(data[i][0]-i)+"</span>";
                    if(data[i][5] == 1){
                        html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
                    }else{
                        html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
                    }
                    html += "<span class='date'>"+data[i][2]+"</span>";
                    total_page = data[i][3];
                    html += "</li>"
                }
                $('#tbody').html(html);
            });
        }
        else if(click_el == 'last'){
            //alert(total_page);
            $('.current').removeClass('current');
            $('#'+total_page+'').addClass('current');
            $.ajax({
                url : '/comm_notice',
                data : {
                    method : 'notice_list',
                    cur_page : total_page
                }
            }).done(function(data){
                //console.log(data);
                html = "";
                for(var i = 0; i < data.length; i++){
                    html += "<li class='tbody'>";
                    html += "<span class='no'>"+(data[i][0]-i)+"</span>";
                    if(data[i][5] == 1){
                        html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
                    }else{
                        html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
                    }
                    html += "<span class='date'>"+data[i][2]+"</span>";
                    total_page = data[i][3];
                    html += "</li>"
                }
                $('#tbody').html(html);
            });
        }
        else if(click_el == 'prev'){
            var prev_page = Number(cur_page)-1;
            //alert(cur_page);
            if(cur_page != start_page){
                $('.current').removeClass('current');
                $('#'+prev_page+'').addClass('current');
                $.ajax({
                    url : '/comm_notice',
                    data : {
                        method : 'notice_list',
                        cur_page : prev_page
                    }
                }).done(function(data){
                    //console.log(data);
                    html = "";
                    for(var i = 0; i < data.length; i++){
                        html += "<li class='tbody'>";
                        html += "<span class='no'>"+(data[i][0]-i)+"</span>";
                        if(data[i][5] == 1){
                            html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
                        }else{
                            html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
                        }
                        html += "<span class='date'>"+data[i][2]+"</span>";
                        total_page = data[i][3];
                        html += "</li>"
                    }
                    $('#tbody').html(html);
                });
            }
            else{
                alert('처음 페이지입니다.');
            }
        }
        else if(click_el == 'first'){
            $('.current').removeClass('current');
            $('#1').addClass('current');
            $.ajax({
                url : '/comm_notice',
                data : {
                    method : 'notice_list',
                    cur_page : 1
                }
            }).done(function(data){
                //console.log(data);
                html = "";
                for(var i = 0; i < data.length; i++){
                    html += "<li class='tbody'>";
                    html += "<span class='no'>"+(data[i][0]-i)+"</span>";
                    if(data[i][5] == 1){
                        html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
                    }else{
                        html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
                    }
                    html += "<span class='date'>"+data[i][2]+"</span>";
                    total_page = data[i][3];
                    html += "</li>"
                }
                $('#tbody').html(html);
            });
        }
        else if(click_el == 'next'){
            var next_page = Number(cur_page)+1;
            //alert(next_page);
            //alert(cur_page);
            if(cur_page != total_page){
                $('.current').removeClass('current');
                $('#'+next_page+'').addClass('current');
                $.ajax({
                    url : '/comm_notice',
                    data : {
                        method : 'notice_list',
                        cur_page : next_page
                    }
                }).done(function(data){
                    //console.log(data);
                    html = "";
                    for(var i = 0; i < data.length; i++){
                        html += "<li class='tbody'>";
                        html += "<span class='no'>"+(data[i][0]-i)+"</span>";
                        if(data[i][5] == 1){
                            html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
                        }else{
                            html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
                        }
                        html += "<span class='date'>"+data[i][2]+"</span>";
                        total_page = data[i][3];
                        html += "</li>"
                    }
                    $('#tbody').html(html);
                });
            }
            else{
                alert('끝 페이지 입니다.');
            }
        }
    });
});
function onKeyDown()
{
    console.log('1234')
     if(event.keyCode == 13)
     {
		 search();
     }
}

//검색처리
$(document).on('click', '#search', search);
function search(){
    var search_con = $('#search_con option:selected').attr('id');
    var search_search = $('#search_search').val();
    var html = "";
    var html2 = "";
    var value_list =[];
    search_search = search_search.replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/\'/g, "&#39;")
    .replace(/\"/g,"&quot;");

    if(search_search != '' && search_search != null){
        $.ajax({
            url : '/comm_notice',
            data : {
                method : 'search_list',
                cur_page : '1',
                search_con : search_con,
                search_search : search_search
            }
        }).done(function(data){
            //console.log(data);
            html = "";
            for(var i = 0; i < data.length; i++){
                html += "<li class='tbody'>";
                html += "<span class='no'>"+(data[i][0]-i)+"</span>";
                if(data[i][5] == 1){
                    html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
                }else{
                    html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
                }
                html += "<span class='date'>"+data[i][2]+"</span>";
                total_page = data[i][3];
                html += "</li>"
            }
            $('#tbody').html(html);
            html2 += "<a href='#' class='first' id='first'>first</a>";
            html2 += "<a href='#' class='prev' id='prev'>prev</a>";
            for(var t=0;t<total_page; t++){
                if(t==0){
                    html2 += "<a href='#' class='current' id='"+(t+1)+"'>"+(t+1)+"</a>"
                }
                else{
                    html2 += "<a href='#' id='"+(t+1)+"'>"+(t+1)+"</a>"
                }
            }
            html2 += "<a href='#' class='next' id='next'>next</a>";
            html2 += "<a href='#' class='last' id='last'>last</a>";
            $('.paging').html(html2);
        });
    }else{
        $.ajax({
        url : '/comm_notice',
            data : {
                method : 'notice_list'
            }
        }).done(function(data){
            //console.log(data);
            html = "";
            for(var i = 0; i < data.length; i++){
                html += "<li class='tbody'>";
                html += "<span class='no'>"+(data[i][0]-i)+"</span>";
                if(data[i][5] == 1){
                    html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+" <img src='/static/images/new.jpeg' height='15px;'></a></span>";
                }else{
                    html += "<span class='title'><a href='/comm_notice_view/"+data[i][4]+"'>"+data[i][6]+data[i][1]+"</a></span>";
                }
                html += "<span class='date'>"+data[i][2]+"</span>";
                total_page = data[i][3];
                html += "</li>"
            }
            $('#tbody').html(html);
            html2 += "<a href='#' class='first' id='first'>first</a>";
            html2 += "<a href='#' class='prev' id='prev'>prev</a>";
            for(var t=0;t<total_page; t++){
                if(t==0){
                    html2 += "<a href='#' class='current' id='"+(t+1)+"'>"+(t+1)+"</a>"
                }
                else{
                    html2 += "<a href='#' id='"+(t+1)+"'>"+(t+1)+"</a>"
                }
            }
            html2 += "<a href='#' class='next' id='next'>next</a>";
            html2 += "<a href='#' class='last' id='last'>last</a>";
            $('.paging').html(html2);
        });
    }
}




