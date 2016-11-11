$(document).ready(function(){
    var value_list;
    var board_id = $('#board_id').text();

    $.ajax({
        url : '/comm_k_news_view/'+board_id,
            data : {
                method : 'view'
            }
    }).done(function(data){
        //console.log(data);
        value_list = data.toString().split(',');
        for(var i=0; i<value_list.length; i++){
            if(i==0){

                $('#title').html(value_list[i]);
            }
            else if(i==1){
                $('#context').html(value_list[i]);
            }
            else{
                $('#reg_date').html(value_list[i]);
            }
        }


    });
});

$(document).on('click', '#list', function(){
    location.href='/comm_k_news'
});



