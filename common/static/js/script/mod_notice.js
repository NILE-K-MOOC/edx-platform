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
        data[1] = data[1].replace(/\/manage\/home\/static\/upload\//g,'/static/file_upload/');
        data[1] = data[1].replace(/\/home\/project\/management\/home\/static\/upload\//g,'/static/file_upload/');
        //data[1] = data[1].replace(/\/manage\/home\/static\/excel\/notice_file\//g,'/static/file_upload/');
        $('#context').html(data[1].replace(/\&\^\&/g, ','));
        $('#reg_date').html('작성일[등록일] : '+data[2]);
        $('#mod_date').html('수정일 : '+data[3]);

        if(data[5] != '' && data[5] != null){
            value_list = data[5].toString().split(',');
            for(var i=0; i<value_list.length; i++){
                html += "<li><a href='#' id='download' title='새창열림'>"+value_list[i]+"</a></li>";
            }
            $('#file').html(html);
            $('#file_li').css('display','inline');
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
        window.open(data,'_blank');
        //$("#download").prop("href", data);
        //location.href=$("#download").attr('href');
    });
});



//<li class="contents" id="file"></li>