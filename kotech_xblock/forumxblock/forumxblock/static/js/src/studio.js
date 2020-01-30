function ForumXBlock(runtime, element) {

  var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

  $(element).find('.save-button').bind('click', function() {
    var form_data = new FormData();
    // var has_score = $(element).find('select[name=has_score]').val();
    var display_name = $(element).find('input[name=display_name]').val();
    var write_count = $(element).find('input[name=write_count]').val();
    var give_point = $(element).find('input[name=give_point]').val();

    // form_data.append('has_score', has_score);
    form_data.append('display_name', display_name);
    form_data.append('write_count', write_count);
    form_data.append('give_point', give_point);
    runtime.notify('save', {state: 'start'});

    $.ajax({
      url: handlerUrl,
      dataType: 'text',
      cache: false,
      contentType: false,
      processData: false,
      data: form_data,
      type: "POST",
      success: function(response){
        runtime.notify('save', {state: 'end'});
      }
    });

  });

  $(element).find('.cancel-button').bind('click', function() {
    runtime.notify('cancel', {});
  });

}