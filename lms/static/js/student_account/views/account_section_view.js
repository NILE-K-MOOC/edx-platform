;(function (define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'backbone',
        'text!templates/student_account/account_settings_section.underscore'
    ], function (gettext, $, _, Backbone, sectionTemplate) {

        var AccountSectionView = Backbone.View.extend({

            initialize: function (options) {

                //console.log('check 11 --------------------------- s');
                //console.log(options);
                //console.log('check 11 --------------------------- e');

                this.options = options;
            },

            render: function () {

                var tab_gubun = (this.options.sections).length;

                // tab_gubun == 1 --> 연결된 계정 클릭 시
                // tab_gubun == 2 --> 계정 정보 클릭 시

                console.log((this.options.sections).length);
                console.log('check 1 --------------------------- e');

                if(tab_gubun == 1){

                    var subject = '<div class="account-settings-sections" id="tmp"><h3 class="section-header" title="check_title_멀티사이트 연동 계정">멀티사이트 연동 계정</h3></div>' +
                        '<div class="multisite_inner"><div>';

                    $('.account-settings-container').append(subject);

                    var user_id = $('#user_id').text();

                    $.post( "/multisite_api", {
                        user_id: user_id
                    })
                    .done(function( data ) {

                        if(data.return == 'zero'){
                            var html = '<div class="multisite_inner" style="font-size: 90%;margin-bottom: 50px;">멀티사이트에 연동 된 계정이 존재하지 않습니다</div>';
                            $('.multisite_inner').append(html);
                        }
                        else{
                            var arr = data.return
                            console.log(arr[0]);
                            console.log(arr[1]);
                            console.log(arr[0][0]);
                            console.log(arr[0][1]);

                            for(var i=0; i<arr.length; i++){
                                console.log(arr[i][0]);
                                console.log(arr[i][1]);

                                var html = ''+
                                '<div class="a" id="'+ arr[i][0] +'" style="margin-right: 20px; margin-bottom:50px; background-color:#dde4e8; width:30%; padding:20px; position:none; float:left;">\n'+
                                    '<div class="b" style="font-weight: bold; text-align: center;margin-bottom: 20px;">\n'+
                                      arr[i][0] + '\n'+
                                    '</div>\n'+
                                    '<div class="c" style="text-align: center;margin-bottom: 20px;font-size: 75%;">\n'+
                                      '해당 기관에 연동된 사번은 ' + arr[i][1] + '입니다\n'+
                                    '</div>\n'+
                                    '<button onclick="multisite(this)" type="button" class="btn multisite" id="' + arr[i][0] + '" style="border: 1px solid #0079bc;width: 100%;">연동 해제</button>\n'+
                                '</div>\n'+

                                '<div class="line">\n'+
                                '</div>';

                                $('.multisite_inner').append(html);
                            }
                        }
                    });

                    /*
                    var html = ''+
                        '<div class="a" style="margin-right: 20px; margin-bottom:50px; background-color:#dde4e8; width:30%; padding:20px; position:none; float:left;">\n'+
                            '<div class="b" style="font-weight: bold; text-align: center;margin-bottom: 20px;">\n'+
                              '네이버\n'+
                            '</div>\n'+
                            '<div class="c" style="text-align: center;margin-bottom: 20px;">\n'+
                              '해당 기관에 연동된 이메일은 93immm@naver.com 입니다\n'+
                            '</div>\n'+
                            '<button type="button" class="btn" style="border: 1px solid #0079bc;width: 100%;">연동 해제</button>\n'+
                        '</div>\n'+

                        '<div class="line">\n'+
                        '</div>';


                    $('.multisite_inner').append(html);
                    $('.multisite_inner').append(html);
                    $('.multisite_inner').append(html);
                    $('.multisite_inner').append(html);
                    $('.multisite_inner').append(html);
                    $('.multisite_inner').append(html);
                    */
                }
                if(tab_gubun == 2) {
                    $('#tmp').remove();
                    $('.multisite_inner').remove();
                }

                this.$el.html(_.template(sectionTemplate)({
                    sections: this.options.sections,
                    activeTabName: this.options.activeTabName
                }));


            }
        });

        return AccountSectionView;
    });
}).call(this, define || RequireJS.define);
