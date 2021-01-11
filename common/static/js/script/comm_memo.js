/**
 * Created by dev on 2016. 11. 8..
 * Modified by redukyo on 2018. 1. 1
 */
var total_page = "";
var cur_page = "";
var start_page = 1;

$(document).ready(function () {
    search(1);

    $("#search").click(function () {
        search(1);
    });

    $("#search_search").keyup(function (e) {
        if (e.keyCode == 13)
            search(1);
    });
});

Date.prototype.yyyymmdd = function () {
    var mm = this.getUTCMonth() + 1; // getMonth() is zero-based
    var dd = this.getUTCDate();

    var rt_date = [this.getFullYear(), '/', (mm > 9 ? '' : '0') + mm, '/', (dd > 9 ? '' : '0') + dd].join('');

    console.log("-------------------> date prototype s");
    console.log("mm = " + mm);
    console.log("dd = " + dd);
    console.log("rt_date = " + rt_date);
    console.log("-------------------> date prototype s");

    return rt_date;
};

// 쪽지 목록으로
function to_list(){
    location.href = '/memo';
}

function search(page_no) {
    
    console.log("----------------> s");
    console.log("page_no = " + page_no);
    console.log("----------------> e");

    if (page_no > 1 && $("#curr_page").val() == page_no) {
        console.log("----------------> if 1");
        return;
    }

    if (page_no){
        console.log("----------------> if 2");
        $("#curr_page").val(page_no);
    }

    $.post(document.location.pathname,
        {
            'page_size': 10,
            'curr_page': $("#curr_page").val(),
            'search_str': $("#search_search").val(),
            'search_con': $("#search_con").val()
        },
        function (context) {
            var data = context.curr_data;
            var total_cnt = context.total_cnt;
            var all_pages = context.all_pages;
            var yesterday = new Date();
            var curr_page = Number($("#curr_page").val());
            $("#all_pages").val(all_pages);
            yesterday.setDate(yesterday.getDate() - 7); // 일주일 이내 등록글은 new 이미지 표시

            //for table
            var html = "";

            if(total_cnt === 0){
                html += "<li class='tbody'>";
                html += "새로운 알림이 존재하지 않습니다.";
                html += "</li>";
            }

            for (var i = 0; i < data.length; i++) {

                var reg_date = new Date(data[i].regist_date);
                var red_date = new Date(data[i].read_date);

                if(data[i].read_date == null){
                    var out_red_date = '<img style="height: 15px; width: 20px;" src="/static/images/memo.png"/>';
                }
                else{
                    var out_red_date = '<img style="height: 15px; width: 20px;" src="/static/images/memo_open.png"/>';
                }

                console.log("-------------------> red date s");
                console.log("red_date = " + data[i].read_date);
                console.log("-------------------> red date e");

                if(data[i].memo_gubun == '1'){
                    gubun = '단체';
                }
                else if(data[i].memo_gubun == '2') {
                    gubun = '관심강좌개설';
                }
                else if(data[i].memo_gubun == '3') {
                    gubun = '공지사항변경';
                }
                else if(data[i].memo_gubun == '4') {
                    gubun = '게시판팔로우';
                }
                else if(data[i].memo_gubun == '5') {
                    gubun = '청강신규개설';
                }
                else if(data[i].memo_gubun == '6') {
                    gubun = '과제제출';
                }
                else if(data[i].memo_gubun == '7') {
                    gubun = '교수자';
                }
                else{
                    gubun = '미분류';
                }

                var memo_link = '#';

                var total_cnt_paging = total_cnt - (10 * (curr_page - 1) + i)

                html += "<li class='tbody'>";
                html += "   <span class='check'>" + '<input type="checkbox" class="check_all" id="' + data[i].memo_id + '"/>' + "</span>";
                // html += "   <span class='no'> " + eval(total_cnt - (10 * (curr_page - 1) + i)) + "</span>";
                html += "   <span class='no'> " + total_cnt_paging + "</span>";
                html += "   <span class='gubun'>" + gubun + "</span>";

                if (data[i].memo_gubun != '1'){
                    memo_link = 'http://' + data[i].contents;
                }
                else {
                    memo_link = '/memo_view/'+data[i].memo_id;
                }

                html += "   <span class='title'><a href='" + memo_link + "'>" + data[i].title + " </a>";
                if (reg_date > yesterday)
                    html += "<img src='/static/images/new.jpeg' height='15px;'/>"
                html += "   </span>";
                html += "   <span class='send_date'>" + reg_date.yyyymmdd() + "</span>";
                html += "   <span class='read_date'>" + out_red_date + "</span>";
                html += "</li>";
            }//end for

            //for paging
            var paging = "";
            var page_size = 5;

            //페이징 10건씩 보이기
            var minNum = Math.floor((curr_page - 1) / page_size) * page_size + 1;
            var maxNum = minNum + page_size - 1;

            if (maxNum > all_pages)
                maxNum = all_pages;

            console.log(minNum + ":" + maxNum);

            paging += "<a href='#' class='first' id='first' title='처음으로'>first</a>";
            paging += "<a href='#' class='prev' id='prev' title='이전'>prev</a>";
            for (var i = minNum; i <= maxNum; i++) {
                if (i == curr_page)
                    paging += "<a href='#' class='page current' id='" + i + "' title='" + i + " 페이지'>" + i + "</a>";
                else
                    paging += "<a href='#' class='page' id='" + i + "' title='" + i + " 페이지'>" + i + "</a>";
            }
            paging += "<a href='#' class='next' id='next' title='다음'>next</a>";
            paging += "<a href='#' class='last' id='last' title='마지막으로'>last</a>";

            //console.log(paging);

            $('#tbody').html(html);
            $('#paging').html(paging);

            fnPaging();
        },
        "json");
}

function fnPaging() {
    $("#paging a").click(function () {
        var id = $(this).attr("id");
        var all_pages = $("#all_pages").val();
        var curr_page = $("#curr_page").val();
        var curr_page = $("#curr_page").val();
        var prev_page = Number($("#curr_page").val()) - 1 > 0 ? Number($("#curr_page").val()) - 1 : 1;
        var next_page = Number($("#curr_page").val()) + 1 <= all_pages ? Number($("#curr_page").val()) + 1 : all_pages;
        var last_page = all_pages;

        if (id == curr_page)
            return;
        if (id == 'first' && curr_page == '1')
            return;
        if (id == 'prev' && curr_page == prev_page)
            return;
        if (id == 'next' && curr_page == next_page)
            return;
        if (id == 'last' && curr_page == last_page)
            return;

        if (id == 'first')
            search(1);
        else if (id == 'prev')
            search(prev_page);
        else if (id == 'next')
            search(next_page);
        else if (id == 'last')
            search(last_page);
        else
            search(id);


        console.debug('id: ' + id);
        console.debug('curr_page: ' + curr_page);
        console.debug('prev_page: ' + prev_page);
        console.debug('next_page: ' + next_page);
        console.debug('last_page: ' + last_page);

    });
}
