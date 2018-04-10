/**
 * Created by kotech on 2018. 3. 20..
 */
$(document).ready(function () {
    $.ajax({
        url: '/course_search_list',
    }).done(function (data) {
        var search_arr = data.course_search_list;
        var $elem = $(".msearch_input").autocomplete({
                //source: search_arr,
                source: function (request, response) {
                    var term = $.ui.autocomplete.escapeRegex(request.term)
                        , startsWithMatcher = new RegExp("^" + term, "i")
                        , startsWith = $.grep(search_arr, function(value) {
                        return startsWithMatcher.test(value.label || value.value || value);
                    })
                        , containsMatcher = new RegExp(term, "i")
                        , contains = $.grep(search_arr, function (value) {
                        return $.inArray(value, startsWith) < 0 &&
                            containsMatcher.test(value.label || value.value || value);
                    });

                    response(startsWith.concat(contains));
                },
                appendTo: ".msearch_area",
                matchContains: true,
                sortResults: false,
                open: function(event, ui) {
                    $(this).autocomplete("widget").css({
                        "width": "100%",
                        "position": "absolute",
                        //"z-index": "1000 !important;"
                    });
                    $(this).autocomplete("widget").children('li').css({
                        "margin-top": "10px",
                        "margin-left": "10px",
                        "font-family": '"Nanum Gothic","Open Sans"',
                        "color": 'block',
                        //"font-weight": 'bold',
                        "font-style": 'normal',
                        "font-size": '15px',
                        'text-align': '-webkit-match-parent',
                        'white-space': 'nowrap',
                        'text-overflow': 'ellipsis',
                        'max-width': '100%',
                        'overflow': 'hidden'

                    });
                },
                focus: function(event, ui) {
                    return false;
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

    var select_search = "";
    $('.msearch_input').on('autocompleteselect', function (e, ui) {
        select_search = ui.item.value;
        $(".msearch_input").val(select_search);
        $("#main_form").submit();
        console.log('You selected: ' + ui.item.value);
    });

});
