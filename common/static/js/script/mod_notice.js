$(document).ready(function(){
    var value_list;
    var board_id = $('#board_id').text();
    var html = "";

    $.ajax({
        url : '/comm_notice_view/'+board_id,
            data : {
                method : 'view'
            }
    }).done(function(data){
        //console.log(data[8]);
        var title = data[4]+data[0];
        $('#title').html(title);
        $('#context').html(data[1].replace(/\&\^\&/g, ','));
        $('#reg_date').html('작성일[등록일] : '+data[2]);
        $('#mod_date').html('수정일 : '+data[3]);

        if(data[5] != '' && data[5] != null){
            value_list = data[5].toString().split(',');
            for(var i=0; i<value_list.length; i++){
                html += "<li><a href='#' id='download' >"+value_list[i]+"</a></li>";
            }
            $('#file').html(html);
        }else{
            $('#file_li').css('display','none');
        }
    });

});

$(document).on('click', '#list', function(){
    location.href='/comm_notice'
});

$(document).on('click', '#file > li > a', function(){
    var file_name = $(this).text();
    var board_id = $('#board_id').text();

    $.ajax({
        url : '/comm_notice_view/'+board_id,
            data : {
                method : 'file_download',
                file_name : file_name
            }
    }).done(function(data){
        //console.log(data);
        $("#download").prop("href", data);
        location.href=$("#download").attr('href');
    });
});



//<li class="contents" id="file"></li>