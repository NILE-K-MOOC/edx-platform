/**
 * Created by ahn on 2017. 8. 3..
 */
$(document).ready(function(){
                  mainImgChg();

                  //layer popup..
                  showNotice();

                  /*
                   $("body").prepend("<div id='mask' style='position: absolute; left: 0; top: 0; z-index: 10000; display: none; opacity: 0.4; background:#363636;'></div>");

                   var videoHtml = "";
                   videoHtml += "  <video id='indexVideo' width='640' height='360' poster='' controls='controls' style='position: absolute; z-index:10001;top: 200px; display:none; left: calc(50% - 320px);'>";
                   videoHtml += "      <source src='http://vod.kmoocs.kr/vod/2015/09/30/6098c795-39a8-5ec5-9683-49f12ba48dfd.mp4' type='video/mp4' />";
                   videoHtml += "  </video>";

                   $("body").prepend(videoHtml);

                   $("#mask").click(function(){
                   $("#indexVideo").hide();
                   $("#indexVideo").currentTime = 0;
                   $("#mask").fadeOut(200);
                   var video = document.getElementById("indexVideo");
                   video.pause();
                   });

                   videoResize();

                   //position control
                   $(window).resize(function(){
                   videoResize();

                   var maskHeight = $(document).height();
                   var maskWidth = $(window).width();
                   $("#mask").css({"width":maskWidth,"height":maskHeight});
                   });
                   */

              });

              var idx = 1;
              function mainImgChg(){
                  //return;          //#e6e6e6 url("./images/main_img1.png") no-repeat scroll center top  
                  // console.log($("#mainImg").size()); 
                  var imgUrl = "";
                  var textUrl = "";
                  if(idx == 0) {
                      imgUrl = "static/images/main_img1.png";
                      textUrl = "static/images/main_text1.png";
                  }else if(idx == 1) {
                      imgUrl = "static/images/main_img2.png";
                      textUrl = "static/images/main_text2.png";
                  }else if(idx == 2) {
                      imgUrl = "static/images/main_img3.png";
                      textUrl = "static/images/main_text3.png";
                  }else if(idx == 3) {
                      imgUrl = "static/images/main_img4.png";
                      textUrl = "static/images/main_text4.png";
                  }
                  $("#mainImg").css("background-color","#e6e6e6");
                  $("#mainImg").animate({
                      opacity: 0
                  }, 4000, "easeInExpo", function(){
                      console.log("imgUrl = " + imgUrl);
                      console.log("imgText = " + textUrl);
                      $(this).css("background", "url("+imgUrl+") no-repeat scroll center top");
                      $("#mainText").attr("src", textUrl);
                      console.log("check >>>>>>>>>>>>>>>>>> " + $("#mainText").attr("src"));
                      console.log("css change done.");
                      $(this).animate({
                          opacity: 1
                      },4000, "easeOutQuint", function(){
                          idx++;
                          if(idx == 4)
                              idx = 0;
                          mainImgChg();
                      });
                  });
              }

              function showNotice(){

                  var d = new Date();
                  if((d.getDay() == 2 || d.getDay() == 5) && d.getHours() == 8 && ( d.getMinutes() >= 0 && d.getMinutes() <= 30)){

                      setTimeout(showNotice, 10000);

                      if($("#noticeLayer").length)
                          return;

                      //notice string
                      var str = "금일 AM08:00 ~ AM08:30중 업데이트가 진행예정입니다.<br/> 일시적으로 화면이 틀어지거나 로그인이 안될 수 있습니다. <br/> 양해 부탁 드립니다. 감사합니다.";
                      var noticeHtml = "<div id='noticeLayer' " +
                              "style='position: absolute; " +
                              "       left: 25px; " +
                              "       top: 20px; " +
                              "       z-index: 10010; " +
                              "       display: block; " +
                              "       border:2px solid #b2b2b2; " +
                              "       opacity: 1; " +
                              "       background:#f2f2f2;" +
                              "       font-size: 30px;" +
                              "       line-height: 55px;" +
                              "       padding:50px;'>" +
                              "       <b>"+str+"</b>" +
                              "       <div style='width:100%; text-align:right;font-size:22px;'>" +
                              "       <a href='javascript:noticeLayerHide();'>[ 닫기 ]</a>" +
                              "       </div>" +
                              "</div>" ;
                      $("body").prepend(noticeHtml);

                      $("#noticeLayer").dblclick(function(){
                          $(this).hide();
                      });

                  } else {
                      $("#noticeLayer").remove();
                  }

              }

              function noticeLayerHide(){
                  $("#noticeLayer").hide();
              }


              function playVideo(){
                  var video = document.getElementById("indexVideo");
                  var maskHeight = $(document).height();
                  var maskWidth = $(window).width();

                  video.currentTime = 0;
                  $("#mask").css({"width":maskWidth+"px","height":maskHeight+"px", "text-align":"center", "vertical-align":"middle"});
                  $("#innerMask").css({"width":(maskWidth/2)+"px","height":(maskHeight/2)+"px", "margin":(maskHeight/3)+"px", "display":"inline-block"});
                  $("#mask").fadeIn(200);
                  $("#indexVideo").fadeIn(300, function(){
                      video.play();
                  });
              }

              function videoResize(){
                  if($(window).width() < 640){
                      $("#indexVideo").prop("width", $(window).width() - 6).css("left", "3px");
                  }else{
                      $("#indexVideo").prop("width", "640").css("left", "calc(50% - 320px)");
                  }
              }