/* Javascript for ForumXBlock. */
function ForumXBlock(runtime, element) {

    function currentCount(result) {
        $('#current_count').html(result.current_count);
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');

    $( document ).ready(function() {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({}),
            success: currentCount
        });
    });
}
