(function(define) {
    'use strict';

    define([
        'jquery',
        'logger'
    ],
        function($, Logger) {
            return function() {
                // This function performs all actions common to all courseware.
                // 1. adding an event to all link clicks.
                $('a:not([href^="#"])').click(function(event) {
                    Logger.log(
                        'edx.ui.lms.link_clicked',
                        {
                            current_url: window.location.href,
                            target_url: event.currentTarget.href
                        });
                });

                // svg 의 문항 내용을 input 의 title 로 지정
                setTimeout(function(){
                    console.log("field size: " + $(".field:has('svg')").size());

                    $(".field:has('svg')").each(function(){
                        let i = $(this).find("input");
                        let t = $(this).find(".MJX_Assistive_MathML").text();

                        if(t){
                            i.prop('title', t);
                            console.log(i.prop('title'));
                        }else{
                            console.log('pass:' + i.prop('name'));
                        }
                    });

                }, 1000);


            };
        }
    );
}).call(this, define || RequireJS.define);
