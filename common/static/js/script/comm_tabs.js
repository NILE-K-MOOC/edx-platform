/**
 * Created by dev on 2016. 11. 8..
 * Modiffy by redukyo on 2018. 1. 2.
 */
var sel_title = '';
$(document).ready(function () {

    tab_click();
    view_content();

    $("#search").keyup(function (e) {
        if (e.keyCode == 13)
        //search($(".faq-tab a.on").data('value'));
            search('total_f');
    });
    $("#search_btn").click(function () {
        //search($(".faq-tab a.on").data('value'));
        search('total_f');
    });

    $("#question").click(function () {
        location.href = '/comm_faqrequest/' + sel_title;
    });

    $("#questionLink").click(function (e) {
        let k = e.keyCode || e.which;
        if (k == 1 || k == 13) {
            location.href = '/comm_faqrequest/' + sel_title;
        }
    });

    $('.mobile-comm-select').change(function(e){
        e.preventDefault();
        $("#search").val('');
        search($(this).val());
    })

});

function search(head_title) {
    $.post("/comm_tabs/" + head_title + "/",
        {
            'head_title': head_title,
            'search_str': $("#search").val()
        },
        function (data) {
            $(".faq-list").html("");

            $(".faq-tab a").removeClass("on");
            $(".faq-tab a[data-value=" + head_title + "]").addClass("on");

            if (data.length == 0) {
                $(".faq-list").html("<div style='text-align: center'><h3>저장된 데이터가 없습니다.</h3></div>");
                return;
            }

            var html = "";
            for (var i = 0; i < data.length; i++) {
                html += "<dt><a href='#'>" + data[i].subject + "</a></dt>";
                html += "<dd>";
                html += "   <div>";
                html += data[i].content;
                html += '       <div style="min-height: 30px;">';
                html += '           <input type="button" value="닫기" title="닫기" style="float: right; background: #ccc; border: 0;">';
                html += '       </div>';
                html += "   </div>";

                html += "</dd>";
            }
            $(".faq-list").html(html);

            view_content();

        },
        "json");
}

function tab_click() {
    $(".faq-tab>a").click(function (e) {
        e.preventDefault();
        $('#faq_header').text($(this).attr('title'));
        $("#search").val('');
        search($(this).data('value'));
        sel_title = $(this).data('value');
    });
}

function view_content() {
    $(".faq-list>dt>a").click(function (e) {
        e.preventDefault();
        if ($(this).parent().next().is(":visible")) {
            $(this).parent().next().slideUp();
        } else {
            $("dd:visible").slideUp();
            $(this).parent().next().slideDown();
        }
    });
    //클릭시 현재탭 alt 추가
    $(".faq-list>dt>a").click(function (e) {
          $(".faq-list>dt>a").removeAttr("alt");
          $(this).attr("alt","현재탭");
    });

    $("dd input:button").click(function (e) {
        e.preventDefault();
        let t = $("dd:visible");
        let p = t.prev().find("a").get(0);
        $(t).slideUp(function(){
            setTimeout(function(){
                $(p).focus();
            }, 1);
        });
    });

}




