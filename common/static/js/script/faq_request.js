/**
 * Created by dev on 2016. 11. 21..
 */
$(document).ready(function(){

});

$(document).on('click', '#request', function(){
    var regExp = /^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;
    var flag = '';
    var email = $('#email').val()+'@'+$('#sel_email option:selected').val();
    var option = $('#search_con option:selected').attr('id');
    var request_con = $('#request_con').val();



    if(email.match(regExp) != null){
        flag = true;
    }else{
        flag = false;
    }

    if(option == 'login_'){
        option = 'login'
    }

    if(option != 'null' && flag == true){
        $('#request').attr('disabled', 'true');
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
                location.href='/comm_faq/1/'
            }else{
                alert('문의하기가 정상적으로 되지않았습니다. 잠시 후에 시도해주세요.');
            }
        });
    }
    else if(flag == false){
        alert('이메일을 정확히 입력해주세요.');
    }
    else{
        alert('문의 내용의 종류를 선택해주세요.');
    }


});


$(document).on('click', '#cancel', function(){
    location.href='/comm_faq/1/'
});