/**
 * Created by dev on 2016. 11. 21..
 */

$(document).ready(function(){
    var sel_title = $("#title_val").val();
    $("#search_con").val(sel_title).attr('selected', 'selected');
});

$(document).on('change', '#sel_email', function(){
    if($('#sel_email option:selected').attr('id') != 'direct' && $('#sel_email option:selected').attr('id') != 'null'){
        $('#email_txt').attr('disabled', 'true');
    }else if($('#sel_email option:selected').attr('id') == 'direct'){
        $('#email_txt').removeAttr('disabled').focus();
    }
});

$(document).on('click', '#request', function(){
    var regExp = /^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;
    var flag = '';
    var sel_email = '';
    var email = '';
    if($('#sel_email option:selected').attr('id') != 'direct' && $('#sel_email option:selected').attr('id') != 'null'){
        sel_email = $('#sel_email option:selected').val();
        email = $('#email').val()+'@'+sel_email;
    }else if($('#sel_email option:selected').attr('id') == 'direct'){
        sel_email = $('#email_txt').val();
        email = $('#email').val()+'@'+$('#email_txt').val();
    }

    if(email.match(regExp) != null){
        flag = true;
    }else{
        flag = false;
    }
    email = email.replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/\'/g, "&#39;")
    .replace(/\"/g,"&quot;");

    var option = $('#search_con option:selected').attr('id');
    var request_con = $('#request_con').val();

    request_con = request_con.replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/\'/g, "&#39;")
    .replace(/\"/g,"&quot;");

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
                alert('문의 내용을 담은 이메일이  K-MOOC운영팀으로 발송되었습니다. 답변에는 보통 업무일 기준 1~2일이 소요되니 양해부탁드립니다.');
                location.href='/comm_faq/1/'
            }else{
                alert('문의하기가 정상적으로 되지않았습니다. 잠시 후에 시도해주세요.');
                location.href='/comm_faq/1/'
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