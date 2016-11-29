/**
 * Created by dev on 2016. 11. 21..
 */
$(document).ready(function(){

});

$(document).on('click', '#request', function(){
    var email = $('#email').val();
    var option = $('#search_con option:selected').attr('id');
    var request_con = $('#request_con').val();
    if(option != 'null'){
        $.ajax({
            url : 'comm_faqrequest',
            data : {
                method : 'request',
                email : email,
                option : option,
                request_con : request_con
            }
        }).done(function(data){
            if(data == 'success'){
                alert('문의가 성공적으로 전송되었습니다.');
                location.href='/comm_faq'
            }else{
                alert('문의하기가 정상적으로 되지않았습니다. 잠시 후에 시도해주세요.');
            }
        });
    }
    else{
        alert('내용을 선택하세요.');
    }


});


$(document).on('click', '#cancel', function(){
    location.href='/comm_faq'
});