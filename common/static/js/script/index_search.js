/**
 * Created by kotech on 2018. 3. 20..
 */
$(document).ready(function () {
    $.ajax({
        url: '/course_search_list',
    }).done(function (data) {
        var search_arr = data.course_search_list;
        var $elem = $(".msearch_input").autocomplete({
                source: search_arr,
                appendTo: ".msearch_area",
                matchContains: true,
                open: function(event, ui) {
                    console.log(this);
                    $(this).autocomplete("widget").css({
                        "width": "100%",
                        "opacity": 0.7,
                        "position": "absolute",
                        "z-index": 1000
                    });
                    $(this).autocomplete("widget").children('li').css({
                        "margin-top": "10px",
                        "margin-left": "10px",
                        "font-family": '"Nanum Gothic","Open Sans"',
                        "color": 'block',
                        //"font-weight": 'bold',
                        "font-style": 'normal',
                        "font-size": '15px'

                    });
                },
                focus: function(event, ui) {
                    return false;
                    //event.preventDefault();
                }
            }),
            elemAutocomplete = $elem.data("ui-autocomplete") || $elem.data("autocomplete");
        if (elemAutocomplete) {
            elemAutocomplete._renderItem = function (ul, item) {
                var newText = String(item.value).replace(
                    new RegExp(this.term, "gi"),
                    "<span class='ui-state-highlight' style='border: #4587c2; color: #4587c2; font-weight: 900'>$&</span>");

                return $("<li></li>")
                    .data("item.autocomplete", item)
                    .append("<a>" + newText + "</a>")
                    .appendTo(ul);
            };
        }
    });

});
