(function(define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'backbone',
        'edx-ui-toolkit/js/utils/html-utils',
        'text!templates/student_account/account_settings_section.underscore'
    ], function(gettext, $, _, Backbone, HtmlUtils, sectionTemplate) {
        var AccountSectionView = Backbone.View.extend({

            initialize: function(options) {
                this.options = options;
                _.bindAll(this, 'render', 'renderFields');
            },

            render: function() {

                var tab_gubun = null;

                try{
                    tab_gubun = (this.options.sections).length;
                }
                catch(e) {
                    tab_gubun = 5;
                }

                // tab_gubun == 1 --> 연결된 계정 클릭 시
                // tab_gubun == 2 --> 계정 정보 클릭 시
                // tab_gubun == 5 --> 예외처리

                if(tab_gubun == 1 && $('#lock').html() != "멀티사이트 연동 계정") {
                    var subject = '<div class="account-settings-sections" id="tmp" style="margin-left:60px;margin-bottom: 20px;"><h3 id="lock" class="section-header" title="check_title_멀티사이트 연동 계정">멀티사이트 연동 계정</h3></div>' +
                        '<div class="multisite_inner" style="display: flex"><div>';

                    $('.account-settings-container').append(subject);

                    var user_id = $('#user_id').text();

                    $.post( "/api/get_multisite_list", {
                        user_id: user_id
                    })
                    .done(function( data ) {

                        if(data.return == 'zero'){
                            var html = '<div class="multisite_inner" style="font-size: 90%;margin-bottom: 50px;margin-left: 60px;">멀티사이트에 연동 된 계정이 존재하지 않습니다</div>';
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
                                '<div class="a" id="'+ arr[i][0] +'" style="margin-left: 70px; margin-right: 20px; margin-bottom:50px; background-color:rgb(245, 245, 245); width:24%; padding:20px; position:none; float:left;">\n'+
                                    '<div class="b" style="font-size: 20px;font-weight: bold; text-align: center;margin-bottom: 20px;">\n'+
                                      arr[i][0] + '\n'+
                                    '</div>\n'+
                                    '<div class="c" style="text-align: center;margin-bottom: 20px;font-size: 75%;">\n'+
                                      '해당 기관에 연동된 사번은 ' + arr[i][1] + '입니다\n'+
                                    '</div>\n'+
                                    '<button onclick="multisite(this)" type="button" class="btn multisite" id="' + arr[i][0] + '" style="border: 1px solid #0079bc;width: 100%;color:#0079bc;padding: 10px;">연동 해제</button>\n'+
                                '</div>\n'+

                                '<div class="line">\n'+
                                '</div>';

                                $('.multisite_inner').append(html);
                            }
                        }
                    });
                }
                if(tab_gubun != 1) {
                    $('#tmp').remove();
                    $('.multisite_inner').remove();
                }

                // survey
                console.log('yes -> ', $('#aaa').hasClass('active'));


                $( "#aaa" ).click(function() {
                  $('.survey-container').show();
                });
                $( "#accounts-tab" ).click(function() {
                  $('.survey-container').hide();
                });
                $( "#about-tab" ).click(function() {
                  $('.survey-container').hide();
                });



                /*
                if($('#aaa').hasClass('active') == true){
                    $('.survey-container').show();
                }
                else{
                    $('.survey-container').hide();
                }
                */


                this.$el.html(_.template(sectionTemplate)({
                    HtmlUtils: HtmlUtils,
                    sections: this.options.sections,
                    tabName: this.options.tabName,
                    tabLabel: this.options.tabLabel
                }));

                this.renderFields();
            },

            renderFields: function() {
                var view = this;

                _.each(view.$('.' + view.options.tabName + '-section-body'), function(sectionEl, index) {
                    _.each(view.options.sections[index].fields, function(field) {
                        $(sectionEl).append(field.view.render().el);
                    });
                });
                return this;
            }
        });

        return AccountSectionView;
    });
}).call(this, define || RequireJS.define);
