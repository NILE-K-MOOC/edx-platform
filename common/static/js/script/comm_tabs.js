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
                html += `
                    <div style="min-height: 30px;">
                    <input type="button" value="닫기" title="닫기" style="float: right; background: #ccc; border: 0;">
                    </div>
                `;
                html += "   </div>";

                html += "</dd>";
            }
            $(".faq-list").html(html);

            view_content();

        },
        "json");
}

function tab_click() {
    $(".faq-tab>a")
        .prop({"tabindex": "0", "href": "#"})
        .click(function () {
            $('#faq_header').text($(this).attr('title'));
            $("#search").val('');
            search($(this).data('value'));
            sel_title = $(this).data('value');
        });
}

function view_content() {
    $(".faq-list>dt>a")
        .prop({"tabindex": "0", "href": "#"})
        .click(function (e) {
            let k = e.keyCode || e.which;

            if ($(this).parent().next().is(":visible")) {
                $(this).parent().next().slideUp();
            } else {
                $("dd:visible").slideUp();
                $(this).parent().next().slideDown(function () {
                    $(this).prop({"tabindex": "0"})
                });
            }
        });

    $("dd input:button").click(function (e) {
        if ($(this).parent().next().is(":visible")) {
            $(this).parent().next().slideUp();
        } else {
            $("dd:visible").slideUp();
            $(this).parent().next().slideDown(function () {
                $(this).prop({"tabindex": "0"})
            });
        }
    });

}




