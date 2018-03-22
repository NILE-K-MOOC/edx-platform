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

    $("#question").click(function(){
        location.href = '/comm_faqrequest/' + sel_title;
    });
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
                html += "   <div>" + data[i].content + "</div>";
                html += "</dd>";
            }
            $(".faq-list").html(html);

            view_content();

        },
        "json");
}

function tab_click() {
    $(".faq-tab a").click(function () {
        $("#search").val('');
        search($(this).data('value'));
        sel_title = $(this).data('value');
    });
}

function view_content() {
    $(".faq-list dt").click(function () {
        if($(this).next().is(":visible")){
            $(this).next().slideUp();
        }else{
            $("dd:visible").slideUp();
            $(this).next().slideDown();
        }
    });
}