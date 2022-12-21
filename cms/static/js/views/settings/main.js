define(['js/views/validation', 'codemirror', 'underscore', 'jquery', 'jquery.ui', 'js/utils/date_utils',
        'js/models/uploads', 'js/views/uploads', 'js/views/license', 'js/models/license',
        'common/js/components/views/feedback_notification', 'jquery.timepicker', 'date', 'gettext',
        'js/views/learning_info', 'js/views/instructor_info', 'edx-ui-toolkit/js/utils/string-utils'],
    function(ValidatingView, CodeMirror, _, $, ui, DateUtils, FileUploadModel,
             FileUploadDialog, LicenseView, LicenseModel, NotificationView,
             timepicker, date, gettext, LearningInfoView, InstructorInfoView, StringUtils) {
        var DetailsView = ValidatingView.extend({

            wtf: '',

            // 이벤트 바인딩 명시
            events: {
                "keypress input" : "submitDisable",
                "keypress select" : "submitDisable",
                'input input': 'updateModel',
                'input textarea': 'updateModel',
                'change input': 'updateModel',
                'change textarea': 'updateModel',
                'change select': 'updateModel',
                'click .remove-course-introduction-video': 'removeVideo',
                'focus #course-overview': 'codeMirrorize',
                'focus #course-about-sidebar-html': 'codeMirrorize',
                'mouseover .timezone': 'updateTime',
                'blur #course-effort-hh': "setEffort",
                'blur #course-effort-mm': "setEffort",
                'blur #course-video-hh': "setEffort",
                'blur #course-video-mm': "setEffort",
                'blur #course-effort-week': "setEffort",
                'blur #Calculated': "setEffort",
                'blur #Calculated_mm': "setEffort",
                'change #course-effort-hh': "setEffort",
                'change #course-effort-mm': "setEffort",
                'change #course-video-hh': "setEffort",
                'change #course-video-mm': "setEffort",
                'change #course-effort-week': "setEffort",
                'change #Calculated': "setEffort",
                'change #Calculated_mm': "setEffort",
                'focus :input': 'inputFocus',
                'blur :input': 'inputUnfocus',
                'click .action-upload-image': 'uploadImage',
                'click .add-course-learning-info': 'addLearningFields',
                'click .add-course-instructor-info': 'addInstructorFields',
                'click #overview-tab3 .remove-item': "delStaffItem",
                'click #overview-tab3 .add-item': "addStaffItem",
                'click .toggleOverviewLayer': "toggleOverviewLayer",
                'click #createOverview': "createOverview",
                'click .tabs>div': "tabChange",
                'change #course_edit_check': "updateModel",
                'click #overview-tab5 .remove-item': "delQuestionItem",
                'click #overview-tab5 .add-item': "addQuestionItem",
                'change #teacher_name': "modi_teacher_name",
                'change #preview_video': "modi_preview_video",
                'change #selectfixid': "modi_course_level",
                'change #subtitle_list': "subtitle_box",
                'change #course-language': "modi_course_language",
                'click #edit_check': "course_editor_html",
                'click #edit_check_reverse': "course_editor_html_reverse",
                'click #subtitle_add': "subtitle_add",
                'click #subtitle_remove': "subtitle_remove",
                'click #add_vtt': "add_vtt",
                'click #del_vtt': "del_vtt",
                'click #preview_video_add': "preview_video_add",
                'click #preview_video_cancel': "preview_video_cancel",
                'click .video_regist': "video_regist",
                'click #course_preview_video_save': "course_preview_video_save",
                'click #usePreCourses': "usePreCourses",
            },
            usePreCourses: function () {
                if (confirm("저장되지 않은 수정 내용은 사라집니다. 진행 하시겠습니까?")){
                    //document.location.href = document.location + "?use_pre_courses=Y";
                    var url = new URL(document.location);
                    // If your expected result is "http://foo.bar/?x=1&y=2&x=42"
                    url.searchParams.append('use_pre_courses', 'Y');
                    console.log(url);
                    document.location.href = url;
                }
            },
            add_vtt: function (){
                var box = ''+
                '<div id="vtt_box" class="vtt_box" style="padding: 10px; margin-top: 8px; border-radius: 5px;">'+
                '    <div style="display: flex;">'+
                '        <select id="vtt_sel" style="flex: 3;">'+
                '            <option value="ko">한국어</option>'+
                '            <option value="en">영어</option>'+
                '            <option value="ja">일본어</option>'+
                '            <option value="zh">중국어</option>'+
                '        </select>'+
                '        <div style="flex: 0.2; margin-left: 15px; font-size: 22px;">'+
                '            <span id="del_vtt" style="color: #f44336; cursor: pointer;" class="icon fa fa-minus-circle" aria-hidden="true"></span>'+
                '        </div>'+
                '    </div>'+
                '    <div style="margin-top: 5px;">'+
                '       <input id="vtt_txt" type="text" placeholder="/asset-v1:KMOOC+exam+001+type@asset+block@chinese_subtitles.vtt">'+
                '    </div>'+
                '</div>';
                $('#vtt_list').append(box);
            },

            del_vtt: function (e){
                console.log('e -> ', e);
                var x = $(event.target).parents('#vtt_box');
                console.log('x -> ', x);
                x.remove();
            },

            course_editor_html: function(e){
                console.log('call trace -> course_editor_html');
                swal({
                    html: '<b>HTML 직접 입력</b>을 사용하시겠습니까?<br>'+
                          '만약 <b>에디터 이용하기</b>를 다시 사용하려면 내용 초기화가 필요합니다<br>',
                    title: '',
                    type: 'warning',
                    focusConfirm: false,
                    showCancelButton: true,
                    cancelButtonText: '취소',
                    confirmButtonText: '사용',
                    reverseButtons: true,
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    //closeOnClickOutside: false,
                    //closeOnEsc: false,
                }).then(function (check) {
                    if(check.value == true){
                        var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                        var addinfo_user_id = $('#addinfo_user_id').text();
                        $(".CodeMirror-scroll").css({'pointer-events': 'all', 'opacity': 1});
                        var json_data = {
                            // csrfmiddlewaretoken: $.cookie('csrftoken'),
                            user_edit: {
                                "hidden": "false",
                                "deprecated": "false",
                                "display_name": "user_edit",
                                "help": "Y또는 N을 입력합니다. Y를 입력할 경우 에디터를 이용한 수정이 불가합니다.",
                                "value": "Y"
                            }
                        };
                        $.ajax({
                            url: "/settings/advanced/" + addinfo_course_id,
                            type: "POST",
                            dataType: "json",
                            contentType: 'application/json; charset=utf-8',
                            data: JSON.stringify(json_data)
                        }).done(function(data){
                            if(data.user_edit.value == 'Y'){
                                $("#course_edit_check").val("Y");
                                $("#course_edit_check").trigger('change');
                                $(".CodeMirror").prop('id', '');
                                $(".x-over").hide();
                                $('.ue_n').hide();
                                $('.ue_y').show();
                                $(".CodeMirror").css('background', '#ffffff');
                            }
                        });
                    } else {
                        return;
                    }
                });
            },

            course_editor_html_reverse: function(e){
                console.log('call trace -> course_editor_html_reverse');
                swal({
                    html: '<b>에디터 이용하기</b>를 사용하시겠습니까?<br>'+
                          '<b>HTML 직접 입력</b>에서 작성한 내용은 초기화 됩니다<br>',
                    title: '',
                    type: 'warning',
                    focusConfirm: false,
                    showCancelButton: true,
                    cancelButtonText: '취소',
                    confirmButtonText: '사용',
                    reverseButtons: true,
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    //closeOnClickOutside: false,
                    //closeOnEsc: false,
                }).then(function (check) {
                    if(check.value == true){
                        // 사용자가 동의할경우 기본 html 을 조회하여 셋팅

                        var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                        var addinfo_user_id = $('#addinfo_user_id').text();
                        $(".CodeMirror-scroll").css({'pointer-events': 'all', 'opacity': 1});
                        var json_data = {
                            // csrfmiddlewaretoken: $.cookie('csrftoken'),
                            user_edit: {
                                "hidden": "false",
                                "deprecated": "false",
                                "display_name": "user_edit",
                                "help": "Y또는 N을 입력합니다. Y를 입력할 경우 에디터를 이용한 수정이 불가합니다.",
                                "value": "N"
                            }
                        };
                        $.ajax({
                            url: "/settings/advanced/" + addinfo_course_id,
                            type: "POST",
                            dataType: "json",
                            contentType: 'application/json; charset=utf-8',
                            data: JSON.stringify(json_data)
                        }).done(function(data){
                            if(data.user_edit.value == 'N'){
                                $("#course_edit_check").val("N");
                                $("#course_edit_check").trigger('change');
                                $(".CodeMirror").prop('id', '');
                                $(".x-over").show();
                                $('.ue_n').show();
                                $('.ue_y').hide();
                                $(".CodeMirror").css('background', '#c1c1c1');
                                wtf.model.set('overview', data.overview_template);
                                $('.action-save').click();
                                document.location.reload();
                            }
                        });
                    } else {
                        return;
                    }
                });
            },

            addStaffItem: function(event){
                console.log('call trace -> addStaffItem');
                event.preventDefault();
                // 교수자와 TA 분리하여 입력란 추가되도록 수정
                if($("#course-ta").css('display') == 'none'){
                    $("#course-instructor").append($(this.instructor_row_template).html());
                } else {
                    $("#course-ta").append($(this.ta_row_template).html());
                }
            },

            delStaffItem: function(event){
                console.log('call trace -> delStaffItem');
                event.preventDefault();
                $(event.currentTarget).parent().parent().remove();
            },

            addQuestionItem: function(event){
                console.log('call trace -> addQuestionItem');
                event.preventDefault();
                $("#course-question").append($(this.question_row_template).html());
            },

            delQuestionItem: function(event){
                console.log('call trace -> delQuestionItem');
                event.preventDefault();
                var faq_len = $(event.currentTarget).parent().parent().parent().find('li').length;
                if(faq_len > 1){
                    $(event.currentTarget).parent().parent().remove();
                } else {
                    $(event.currentTarget).parent().parent().parent().find('li:eq(0) #faq-question').val('');
                    $(event.currentTarget).parent().parent().parent().find('li:eq(0) #faq-answer').val('');
                }
            },

            createOverview: function(event){
                console.log('call trace -> createOverview');

                event.preventDefault();
                if(!this.overviewLayerValidate()){
                    return;
                }

                var regex = /(?:\r\n|\r|\n)/g;
                var course_plan = $.parseHTML(tinymce.get('course_plan').getContent());
                var ov = $.parseHTML(this.model.get('overview'));

                $(ov).find(".goal:eq(0)").html($("#overview-tab1 textarea").val().replace(regex, "<br>"));
                $(ov).find(".video source:eq(0)").attr("src", $("#course-sample-video-url").val());
                $(ov).find(".syllabus_table:eq(0)").html($('<table>').append(course_plan).html());

                // 홍보영상 자막 추가
                var source = $(ov).find(".video").html();
                source = source.replace(/<(\/track|track)([^>]*)>/gi,"");
                console.log('------------------------------------------');
                console.log('source = ', source);
                console.log('------------------------------------------');
                var track_set = '';
                $('.vtt_box').each(function(idx){
                    var vtt_name = $(this).find('option:selected').text();
                    var vtt_code = $(this).find("#vtt_sel").val();
                    var vtt_txt = $(this).find("#vtt_txt").val();
                    var track = '<track label="' + vtt_name + '" kind="subtitles" srclang="' + vtt_code + '" src="' + vtt_txt + '">';
                    track_set += track;
                })
                console.log('------------------------------------------');
                console.log('source + track_set = ', source + track_set);
                console.log('------------------------------------------');
                $(ov).find(".video").html(source + track_set);

                // 운영진 사진 http 체크
                const url_pattern = /^http/gi;
                // 강좌운영진
                var staff_templates = "";
                $("#course-instructor li").each(function(index){
                    var staff_photo = $(this).find("#staff-photo").val();
                    if(staff_photo.match(url_pattern) == null){
                        staff_photo = 'http://' + staff_photo;
                    }
                    var staff_name = $(this).find("#staff-name").val();
                    var careers = $(this).find("textarea").val().replace(regex, '\n').split(/\n/g);
                    var careers_text = "";
                    for (var i=0; i<careers.length;i++){
                        if(i != careers.length -1 && careers[i] != ''){
                            careers_text += "<dd>" + careers[i] + "</dd>";
                        } else if(i == careers.length -1 && careers[careers.length -1] != ''){
                            careers_text += "<dd>" + careers[i] + "</dd>";
                        } else if(careers.length -1 == 0 && careers[careers.length -1] == ''){
                            careers_text += '';
                        } else {
                            careers_text += "<dd><br></dd>"
                        }
                    }
                    var staff_template = "" +
                        "<article>";
                    if(index == 0){
                        staff_template += "	<h3><i class='fa fa-user'></i>교수자</h3>";
                    }
                    staff_template += "" +
                        "	<article class='professor'>" +
                        "		<div class='teacher_image'>" +
                        "			<img src='" + staff_photo + "' align='left' alt='" + staff_name + " " + gettext("professor") + "'>" +
                        "		</div>" +
                        "		<div class='staff_descript'>" +
                        "			<dl>" +
                        "			  <dt>" +
                        "				 <i class='fa fa-angle-double-right'></i><i class='staff-name'>" + staff_name + "</i> 교수" +
                        "			  </dt>" +
                        "				" + careers_text +
                        "			</dl>" +
                        "		</div>" +
                        "	</article>" +
                        "</article>";
                    staff_templates += staff_template;
                });

                $("#course-ta li").each(function(index){
                    var staff_photo = $(this).find("#staff-photo").val();
                    var staff_name = $(this).find("#staff-name").val();
                    if(staff_photo.match(url_pattern) == null){
                        staff_photo = 'http://' + staff_photo;
                    }
                    var careers = $(this).find("textarea").val().replace(regex, '\n').split(/\n/g);
                    var careers_text = "";
                    for (var i=0; i<careers.length;i++){
                        if(i != careers.length -1 && careers[i] != ''){
                            careers_text += "<dd>" + careers[i] + "</dd>";
                        } else if(i == careers.length -1 && careers[careers.length -1] != ''){
                            careers_text += "<dd>" + careers[i] + "</dd>";
                        } else if(careers.length -1 == 0 && careers[careers.length -1] == ''){
                            careers_text += '';
                        } else {
                            careers_text += "<dd><br></dd>"
                        }
                    }
                    var staff_template = "" +
                        "<article>";
                    if(index == 0){
                        staff_template += "	<h3><i class='fa fa-user'></i>강좌지원팀</h3>";
                    }
                    staff_template += "" +
                        "	<article class='staff'>" +
                        "		<div class='ta_image'>" +
                        "			<img src='" + staff_photo + "' align='left' alt='" + staff_name + "'>" +
                        "		</div>" +
                        "		<div class='staff_descript'>" +
                        "			<dl>" +
                        "				<dt>" +
                        "				 <i class='fa fa-angle-double-right'></i><i class='staff-name'>" + staff_name+ "</i>" +
                        "			  </dt>" +
                        "				" + careers_text +
                        "			</dl>" +
                        "		</div>" +
                        "	</article>" +
                        "</article>";
                    staff_templates += staff_template;
                });
                if(staff_templates){
                    $(ov).find(".course-staff:eq(0)").html("<h2><i class=\"fa fa-group (alias)\"></i>강좌운영팀 소개</h2>");
                    $(ov).find(".course-staff:eq(0)").append(staff_templates);
                }
                // 이수/평가정보
                var grade_table = $.parseHTML(tinymce.get('grade_table').getContent());
                //make html source
                $(ov).find(".grade_table:eq(0)").html($('<table>').append(grade_table).html());
                // 강좌 수준 및 선수요건
                $(ov).find("#course-level:eq(0)").html($("#overview-tab4 textarea:eq(1)").val().replace(regex, "<br>"));
                // 교재 및 참고문헌
                $(ov).find("#course-reference:eq(0)").html($("#overview-tab4 textarea:eq(2)").val().replace(regex, "<br>"));
                // FAQ
                var faqs = "";
                $("#course-question li").each(function(){
                    var question = $(this).find("#faq-question").val();
                    var answer = $(this).find("#faq-answer").val();
                    var faq = "" +
                        "<article class='question'>" +
                        "	<h4><i class='fa fa-chevron-right'></i>" + question + "</h4>" +
                        "	<p>" + answer + "</p>" +
                        "</article>";
                    faqs += faq;
                });
                if(faqs){
                    $(ov).find(".faq:eq(0)").html("<h2><i class=\"fa fa-question-circle\"></i>자주 묻는 질문</h2>");
                    $(ov).find(".faq:eq(0)").append(faqs);
                }
                // 사용자 추가 내용
                //$(ov).find(".user_add:eq(0)").html($("#user_content").val().replace(/\n/g, "<br>"));
                var user_add_index = tinymce.get('user_content').getContent();
                user_add_index = user_add_index.replace(/<h2>/gi, '<h2><i class="fa fa-plus-circle"></i>');
                user_add_index = user_add_index.replace(/<h3>/gi, '<h3><i class="fa fa-chevron-right"></i>');
                $(ov).find(".user_add:eq(0)").html($.parseHTML(user_add_index));
                //this.model.set('overview', '<div id="course-info">' + $("<div>").append($(ov).clone()).html() + '</div>');
                var html_format_options = {
                    // "indent":"yes",
                    // "indent-spaces":2,
                    // "wrap":80,
                    "markup":true,
                    "output-xml":false,
                    "numeric-entities":false,
                    "quote-marks":false,
                    "quote-nbsp":false,
                    "show-body-only":true,
                    "quote-ampersand":false,
                    "break-before-br":false,
                    "uppercase-tags":false,
                    "uppercase-attributes":false,
                    "drop-font-tags":false,
                    "tidy-mark":false,
                    "drop-empty-elements": false
                };
                var html = $("<div>").attr("id", "course-info").append($(ov).clone()).html();
                var result = tidy_html5(html, html_format_options);
                this.model.set('overview', result);
                $("#overviewEditLayer").toggle();
                this.render();
            },

            textareaTrim: function(text){
                console.log('call tracef -> textareaTrim');
                // textarea에서 공백 처리
                var text_lines = text.split('\n');
                var return_txt = 'text   first line';
                for(var i = 0 ; i < text_lines.length; i++){
                    if(text_lines[i].trim() != ''){
                        return_txt += text_lines[i].trim() + '\n';
                    } else if(i == text_lines.length -1){
                        return_txt += text_lines[i].trim();
                    } else {
                        return_txt += '\n';
                    }
                }
                return_txt = return_txt.replace(/text   first line\n/g, '').replace(/text   first line/g, '');

                return return_txt;
            },

            tinymceInit: function (selector) {
                console.log('call trace -> tinymceInit');
                tinymce.init({
                    selector: selector,
                    entity_encoding: 'raw',
                    menubar: false,
                    statusbar: false,
                    plugins: "codemirror, table, link, image",
                    codemirror: {
                        path: "" + baseUrl + "/js/vendor"
                    },
                    toolbar_items_size: 'small',
                    extended_valid_elements: "iframe[src|frameborder|style|scrolling|class|width|height|name|align|id]",
                    toolbar: "fontselect | fontsizeselect | bold italic underline forecolor wrapAsCode | table link | bullist numlist outdent indent blockquote | link unlink image | code",
                    resize: true,
                    fontsize_formats: '8pt 10pt 12pt 14pt 18pt 24pt 36pt',
                    min_height: 300,
                    setup: function (ed) {
                        ed.on('click', function (e) {
                            tinymce.execCommand('mceFocus', false, '.new-update-form:eq(0) textarea');
                        });
                    },
                    block_formats: interpolate("%(paragraph)s=p;%(preformatted)s=pre;%(heading3)s=h3;%(heading4)s=h4;%(heading5)s=h5;%(heading6)s=h6", {
                        paragraph: gettext("Paragraph"),
                        preformatted: gettext("Preformatted"),
                        heading3: gettext("Heading 3"),
                        heading4: gettext("Heading 4"),
                        heading5: gettext("Heading 5"),
                        heading6: gettext("Heading 6")
                    }, true),
                });
            },

            overviewLayerValidate: function(){ // 에디터 내 유효성
                console.log('call trace -> overviewLayerValidate');
                $(".overview-modal").find(".message-error").remove();
                return true;
            },

            toggleOverviewLayer: function(event){
                console.log('call trace -> toggleOverviewLayer');
                event.preventDefault();
                $("#overviewEditLayer").toggle();
                if($("#overviewEditLayer").is(":visible")){
                    var top = parseInt($(window).scrollTop());
                    $(".overview-modal").prop("style", "top: " + (top - 50) + "px;");
                    this.overviewLayerSetting();
                }
            },

            tabChange: function(event){
                console.log('call trace -> tabChange');
                event.preventDefault();
                var t = event.currentTarget.getAttribute('data-target');
                $(".tabs>div").removeClass("on")
                $(event.target).addClass("on");
                $("#overviewEditLayer div[id^='overview-tab']").hide();
                $("#" + t).show();
            },

            initialize : function(options) {
                wtf = this;
                console.log('call trace -> initialize');
                $(function () {
                    $(".tab_content").hide();
                    $(".tab_content:first").show();
                    $("ul.tabs li").click(function () {
                        $("ul.tabs li").removeClass("active").css("color", "#333").css("background-color", "#fafafa");
                        $(this).addClass("active").css("color", "darkred").css("background-color", "#ffbe60");
                        $(".tab_content").hide()
                        var activeTab = $(this).attr("rel");
                        $("#" + activeTab).fadeIn()
                    });
                    degree_js();
                    $("ul.info_tabs li").click(function () {
                        if ($(this).text() == '교수자') {
                            $('#info_add1').css("display", "inline-block");
                            $('#info_del1').css("display", "inline-block");
                            $('#info_add2').css("display", "none");
                            $('#info_del2').css("display", "none");
                            $('#info_div1').css("display", "inline-block");
                            $('#info_div2').css("display", "none");
                        }
                        else if ($(this).text() == '강좌지원팀') {
                            $('#info_add1').css("display", "none");
                            $('#info_del1').css("display", "none");
                            $('#info_add2').css("display", "inline-block");
                            $('#info_del2').css("display", "inline-block");
                            $('#info_div1').css("display", "none");
                            $('#info_div2').css("display", "inline-block");
                        }
                        $("ul.info_tabs li").removeClass("active").css("color", "#333").css("background-color", "#fafafa");
                        $(this).addClass("active").css("color", "#5B7484").css("background-color", "#AAAAAA");
                        var activeTab = $(this).attr("rel");
                        $("#" + activeTab).fadeIn()
                    });
                });
                options = options || {};
                // fill in fields
                this.$el.find("#course-language").val(this.model.get('language'));
                this.$el.find("#course-organization").val(this.model.get('org'));
                this.$el.find("#course-number").val(this.model.get('course_id'));
                this.$el.find("#course-name").val(this.model.get('run'));
                this.$el.find('.set-date').datepicker({ 'dateFormat': 'm/d/yy' });
                // Avoid showing broken image on mistyped/nonexistent image
                this.$el.find('img').error(function() {
                    $(this).hide();
                });
                this.$el.find('img').load(function() {
                    $(this).show();
                });
                this.listenTo(this.model, 'invalid', this.handleValidationError);
                this.listenTo(this.model, 'change', this.showNotificationBar);
                this.selectorToField = _.invert(this.fieldToSelectorMap);
                // handle license separately, to avoid reimplementing view logic
                this.licenseModel = new LicenseModel({"asString": this.model.get('license')});
                this.licenseView = new LicenseView({
                    model: this.licenseModel,
                    el: this.$("#course-license-selector").get(),
                    showPreview: true
                });
                this.listenTo(this.licenseModel, 'change', this.handleLicenseChange);
                if (options.showMinGradeWarning || false) {
                    new NotificationView.Warning({
                        title: gettext("Course Credit Requirements"),
                        message: gettext("The minimum grade for course credit is not set."),
                        closeIcon: true
                    }).show();
                }
                this.learning_info_view = new LearningInfoView({
                    el: $(".course-settings-learning-fields"),
                    model: this.model
                });
                this.instructor_info_view = new InstructorInfoView({
                    el: $(".course-instructor-details-fields"),
                    model: this.model
                });
                $("input:radio[name='staff-type']").click(function(){
                    if($(this).val() == 'instructor'){
                        $("#course-instructor").show();
                        $("#course-ta").hide();
                    }else{
                        $("#course-instructor").hide();
                        $("#course-ta").show();
                    }
                });
                //강좌 운영진 추가 기본 템플릿 초기화
                this.instructor_row_template = $("#course-instructor").clone();
                this.ta_row_template = $("#course-ta").clone();
                this.question_row_template = $("#course-question").clone();
            },

            overviewLayerSetting: function(){
                console.log('call trace -> overviewLayerSetting');
                //overviewLayerEditor 상에 표시될 항목들을 셋팅한다.
                var regex = /<br\s*[\/]?>/g;
                var regex_line = /(?:\r\n|\r|\n)/g;
                // overview object
                var ov = $.parseHTML(this.model.get('overview'));
                // 수업내용/목표
                var goal = $(ov).find(".goal:eq(0)").html().replace(regex_line, '').replace(regex, "\n");
                // 홍보영상/예시강의
                var vurl = $(ov).find(".video source:eq(0)").attr("src");
                // 강좌 계획
                var syllabus = $(ov).find(".syllabus_table:eq(0)");
                // 강좌운영진
                var team = $(ov).find(".course-staff:eq(0)").html();

                // 홍보영상 자막
                $('#vtt_list').empty();
                var vtt_list = $(ov).find(".video track");
                $(vtt_list).each(function(idx){
                    console.log('idx = ', idx);
                    var vtt_src = $(this).attr("src");
                    var vtt_srclang = $(this).attr("srclang");
                    var vtt_label = $(this).attr("label");
                    console.log('vtt_src = ', vtt_src);
                    console.log('vtt_srclang = ', vtt_srclang);
                    console.log('vtt_label = ', vtt_label);

                    var box = ''+
                    '<div id="vtt_box" class="vtt_box" style="padding: 10px; margin-top: 8px; border-radius: 5px;">'+
                    '    <div style="display: flex;">'+
                    '        <select id="vtt_sel" style="flex: 3;">'+
                    '            <option value="ko">한국어</option>'+
                    '            <option value="en">영어</option>'+
                    '            <option value="ja">일본어</option>'+
                    '            <option value="zh">중국어</option>'+
                    '        </select>'+
                    '        <div style="flex: 0.2; margin-left: 15px; font-size: 22px;">'+
                    '            <span id="del_vtt" style="color: #f44336; cursor: pointer;" class="icon fa fa-minus-circle" aria-hidden="true"></span>'+
                    '        </div>'+
                    '    </div>'+
                    '    <div style="margin-top: 5px;">'+
                    '       <input placeholder="/asset-v1:KMOOC+exam+001+type@asset+block@chinese_subtitles.vtt" id="vtt_txt" type="text" value="' + vtt_src + '">'+
                    '    </div>'+
                    '</div>';

                    console.log('before box = ', box);

                    if (vtt_srclang == 'ko') { box = box.replace('<option value="ko">', '<option selected value="ko">'); }
                    if (vtt_srclang == 'en') { box = box.replace('<option value="en">', '<option selected value="en">'); }
                    if (vtt_srclang == 'ja') { box = box.replace('<option value="ja">', '<option selected value="ja">'); }
                    if (vtt_srclang == 'zh') { box = box.replace('<option value="zh">', '<option selected value="zh">'); }

                    console.log('after box = ', box);

                    $('#vtt_list').append(box);
                })

                var professor_len = $(ov).find("article.professor");
                var professor_html = '';
                for(var j = 0 ; j < professor_len.length ; j++){
                    var staff1 = $(ov).find("article.professor:eq("+j+") img").attr('src');
                    var staff2 = $(ov).find("article.professor:eq("+j+") .staff_descript i.staff-name").text();
                    var staff3 = '';
                    var row_len =  $(ov).find("article.professor:eq("+j+") .staff_descript dd").length;
                    $(ov).find("article.professor:eq("+j+") .staff_descript dd").each(function(idx) {
                        let prof_row = $(this).html().replace(regex, '');
                        if(idx != row_len -1)
                            staff3 += prof_row.trim() + '\n';
                        else if(idx == row_len -1){
                            staff3 += prof_row.trim();
                        }
                    });
                    professor_html += '' +
                            '<li class="field-group course-grading-assignment-list-item">' +
                            '<div style="width: 34%; float: left;">' +
                            '<div class="field text" id="field-course-grading-assignment-name" style="width: 100%;">' +
                            '<label for="staff-photo">사진 URL</label>' +
                            '<input type="text" class="long" id="staff-photo" value="'+ staff1 +'" placeholder="http://example.com/photo.jpg">' +
                            '<span class="tip tip-stacked">웹 에서 접근 가능한 주소</span>' +
                            '</div>' +
                            '<br>' +
                            '<div class="field text" id="field-course-grading-assignment-shortname" style="width: 100%;">' +
                            '<label for="staff-name">성명</label>' +
                            '<input type="text" class="short" id="staff-name" value="'+ staff2 +'" placeholder="교수">' +
                            '<span class="tip tip-stacked">표시될 이름</span>' +
                            '</div>' +
                            '</div>' +
                            '<div style="width: 64%; float: right;">'+
                            '<div style="width: 100%;">'+
                            '<label for="staff-career">약력</label>'+
                            '<textarea id="staff-career" style="width: 96%; height: 135px;">'+ staff3 +'</textarea>'+
                            '<span class="tip tip-stacked">화면에 표시될 경력 사항</span>'+
                            '</div>'+
                            '</div>'+
                            '<div class="actions">'+
                            '<a href="#" class="button delete-button standard remove-item"><span class="delete-icon"></span>삭제</a>'+
                            '</div>'+
                            '</li>';

                }
                if(professor_len.length != 0)
                    $("#course-instructor").html(professor_html);
                var staff_len = $(ov).find("article.staff");
                var staff_html = '';
                for(var j = 0 ; j < staff_len.length ; j++){
                    var staff1 = $(ov).find("article.staff:eq("+j+") img").attr('src');
                    var staff2 = $(ov).find("article.staff:eq("+j+") .staff_descript i.staff-name").text();
                    var staff3 = '';
                    var staff_row_len =  $(ov).find("article.staff:eq("+j+") .staff_descript dd").length;
                    $(ov).find("article.staff:eq("+j+") .staff_descript dd").each(function(idx) {
                        let staff_row = $(this).html().replace(regex, '');
                        if(idx != staff_row_len -1)
                            staff3 += staff_row.trim() + '\n';
                        else if(idx == staff_row_len -1)
                            staff3 += staff_row.trim();
                    });
                    staff_html += '' +
                            '<li class="field-group course-grading-assignment-list-item">' +
                            '<div style="width: 34%; float: left;">' +
                            '<div class="field text" id="field-course-grading-assignment-name" style="width: 100%;">' +
                            '<label for="staff-photo">사진 URL</label>' +
                            '<input type="text" class="long" id="staff-photo" value="'+ staff1 +'" placeholder="http://example.com/photo.jpg">' +
                            '<span class="tip tip-stacked">웹 에서 접근 가능한 주소</span>' +
                            '</div>' +
                            '<br>' +
                            '<div class="field text" id="field-course-grading-assignment-shortname" style="width: 100%;">' +
                            '<label for="staff-name">성명</label>' +
                            '<input type="text" class="short" id="staff-name" value="'+ staff2 +'" placeholder="조교">' +
                            '<span class="tip tip-stacked">표시될 이름</span>' +
                            '</div>' +
                            '</div>' +
                            '<div style="width: 64%; float: right;">'+
                            '<div style="width: 100%;">'+
                            '<label for="staff-career">약력</label>'+
                            '<textarea id="staff-career" style="width: 96%; height: 135px;">'+ staff3 +'</textarea>'+
                            '<span class="tip tip-stacked">화면에 표시될 경력 사항</span>'+
                            '</div>'+
                            '</div>'+
                            '<div class="actions">'+
                            '<a href="#" class="button delete-button standard remove-item"><span class="delete-icon"></span>삭제</a>'+
                            '</div>'+
                            '</li>';
                }
                if(staff_len.length != 0)
                    $("#course-ta").html(staff_html);
                // 이수/평가정보
                var evaluation = $(ov).find(".grade_table:eq(0)");
                // 강좌 수준 및 선수요건
                var level = $(ov).find("#course-level").html().replace(regex_line, '').replace(regex, "\n");
                // 교재 및 참고문헌
                var reference = $(ov).find("#course-reference").html().replace(regex_line, '').replace(regex, "\n");
                // FAQ
                var faq = $(ov).find(".faq article");
                var faq_form = '';
                // FAQ 데이터 출력
                $(faq).each(function(){
                    var question = $(this).find("h4").text().trim();
                    var answer = $(this).find("p").text().trim();
                    faq_form +=  '' +
                            '<li class="field-group course-grading-assignment-list-item">' +
                            '<div>' +
                            '<div class="field text" id="field-course-grading-assignment-name" style="width: 100%;">' +
                            '<label for="faq-question">질문</label>' +
                            '<input type="text" class="long" id="faq-question" value="' + question + '" placeholder="강좌 교재가 따로 있나요?">' +
                            '</div>' +
                            '<div class="field text" id="field-course-grading-assignment-shortname" style="width: 100%;">' +
                            '<label for="faq-answer">답변</label>' +
                            '<input type="text" class="short" id="faq-answer" value="' + answer + '" placeholder="네. 있습니다.">' +
                            '</div>' +
                            '</div>' +
                            '<div class="actions">' +
                            '<a href="#" class="button delete-button standard remove-item"><span class="delete-icon"></span>삭제</a>' +
                            '</div>' +
                            '</li>';
                });
                if(faq.length != 0){
                    $("#overview-tab5 ol#course-question").html(faq_form);
                }
                // 사용자 추가 내용
                var user_content = $(ov).find(".user_add:eq(0)");
                // ------------------------------------------------
                //syllabus table 에 에디터 안에서의 크기조절을 위한 속성 추가
                syllabus.find("table").attr("style", "width: 100%;");
                evaluation.find("table").attr("style", "width: 100%;");
                // ------------------------------------------------
                //홍보영상
                // console.log('video url s ==============================')
                // console.log($(ov).find(".video source:eq(0)").attr("src"));
                // console.log('video url e ==============================')
                //tinymce 에디터 사용시 getContent 함수 이용을 위해 textarea 의 아이디를 지정하요 사용
                // console.log('goal start --- s');
                // console.log(goal);
                // console.log('goal start --- e');
                $("#overview-tab1 textarea").val(goal.trim());
                try {
                    $("#course-sample-video-url").val(vurl.trim());
                } catch(e) {
                    $("#course-sample-video-url").val(vurl);
                }
                $("#course_plan").val(syllabus.html());
                $("#grade_table").val(evaluation.html());
                $("#user_content").val(user_content.html());
                $("#overview-tab4 textarea:eq(1)").val(level.trim());
                $("#overview-tab4 textarea:eq(2)").val(reference.trim());
                this.tinymceInit('#course_plan');
                this.tinymceInit('#grade_table');
                this.tinymceInit('#user_content');
                //tinymce.get('course_plan').setContent(syllabus.html());
            },

            tinymceInit: function (selector) {
                console.log('call trace -> tinymceInit');
                tinymce.init({
                    selector: selector,
                    entity_encoding: 'raw',
                    menubar: false,
                    statusbar: false,
                    plugins: "codemirror, table, link, image",
                    codemirror: {
                        path: "" + baseUrl + "/js/vendor"
                    },
                    toolbar_items_size: 'small',
                    extended_valid_elements: "iframe[src|frameborder|style|scrolling|class|width|height|name|align|id]",
                    toolbar: "fontselect | fontsizeselect | bold italic underline forecolor wrapAsCode | table link | bullist numlist outdent indent blockquote | link unlink image | code",
                    resize: true,
                    fontsize_formats: '8pt 10pt 12pt 14pt 18pt 24pt 36pt',
                    min_height: 300,
                    setup: function (ed) {
                        ed.on('click', function (e) {
                            tinymce.execCommand('mceFocus', false, '.new-update-form:eq(0) textarea');
                        });
                    },
                    block_formats: interpolate("%(paragraph)s=p;%(preformatted)s=pre;%(heading3)s=h3;%(heading4)s=h4;%(heading5)s=h5;%(heading6)s=h6", {
                        paragraph: gettext("Paragraph"),
                        preformatted: gettext("Preformatted"),
                        heading3: gettext("Heading 3"),
                        heading4: gettext("Heading 4"),
                        heading5: gettext("Heading 5"),
                        heading6: gettext("Heading 6")
                    }, true),
                });
            },

            setEffort:function(){
                console.log('call trace -> setEffort');
                var hh = $("#course-effort-hh").val();
                var mm = $("#course-effort-mm").val();
                var week = $("#course-effort-week").val();
                var video_hh = $("#course-video-hh").val();
                var video_mm = $("#course-video-mm").val();
                var Calculated = $("#Calculated").val();
                var Calculated_mm = $("#Calculated_mm").val();
                if (mm > 60) {
                    $("#course-effort-mm").val('');
                    return false;
                }
                if (Calculated_mm > 59) {
                    alert("60분을 초과하여 입력하실수 없습니다");
                    $("#Calculated_mm").val('');
                    return false;
                }
                if(Calculated>50 && Calculated_mm < 60){
                    alert("학습인정시간은 50시간 이내만 입력 가능합니다");
                    $("#Calculated").val('');
                    $("#Calculated_mm").val('');
                    return false;
                }
                if(Calculated == 50){
                    $("#Calculated_mm").val('00');
                    Calculated_mm = $("#Calculated_mm").val();
                    $("#Calculated_mm").attr('disabled', 'disabled');
                    // return false;
                }
                else {
                    $("#Calculated_mm").removeAttr('disabled');
                }
                if (Calculated>50){
                    alert("학습인정시간은 50시간 이내만 입력 가능합니다");
                    $("#Calculated").val('');
                    return false;
                }
                $('#Calculated').keyup(function () {
                    this.value = this.value.replace(/[^0-9]/g,'');
                });
                $('#Calculated_mm').keyup(function () {
                    this.value = this.value.replace(/[^0-9]/g,'');
                });
                if(hh && hh.length == 1)
                    hh = "0" + hh;
                if(mm && mm.length == 1)
                    mm = "0" + mm;
                if(week && week.length == 1)
                    week = "0" + week;
                if(video_hh && video_hh.length == 1)
                    video_hh = "0" + video_hh;
                if(video_mm && video_mm.length == 1)
                    video_mm = "0" + video_mm;
                if(Calculated && Calculated.length == 1)
                    Calculated = "0" + Calculated;
                if(Calculated_mm && Calculated_mm.length == 1)
                    Calculated_mm = "0" + Calculated_mm;
                if(hh)
                    $("#course-effort-hh").val(hh);
                if(mm)
                    $("#course-effort-mm").val(mm);
                if(week)
                    $("#course-effort-week").val(week);
                if(video_hh)
                    $("#course-video-hh").val(video_hh);
                if(video_mm)
                    $("#course-video-mm").val(video_mm);
                if(Calculated)
                    $("#Calculated").val(Calculated);
                if(Calculated_mm){
                    $("#Calculated_mm").val(Calculated_mm);
                }
                var video = video_hh + ":" + video_mm;
                var calculated_total = Calculated + ':' + Calculated_mm;
                //if(hh && mm && week){
                //    // 총 이수시간 계산 및 표시
                //    //var total_time = (Number(hh) * Number(week)) + (Number(mm)/60 * Number(week));
                //    var total_min = (((Number(hh) * 60) + Number(mm)) * Number(week));
                //    var real_hour = Math.floor(total_min/60);
                //    var real_min = total_min%60;
                //
                //    console.log("real_min = " + real_min);
                //
                //    if(real_min == 0){
                //        $("#Calculated").val(real_hour + "시간 ");
                //    }
                //    else{
                //        $("#Calculated").val(real_hour + "시간 " + real_min + "분");
                //    }
                //}
                var val = hh + ":" + mm;
                if(week && week != "")
                    val = val + "@" + week;
                if(video && video != "")
                    val = val + "#" + video;
                if(calculated_total && calculated_total != ""){
                    val = val + "$" + calculated_total;
                }
                $("#course-effort").val(val);
                $("#course-effort").trigger("change");
                var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                var addinfo_user_id = $('#addinfo_user_id').text();
                var course_period = $("#course-effort-week").val();
                var Calculated_mmm = '';
                if ($("#Calculated_mm").val()==''){
                    Calculated_mmm = '00';
                }
                else{
                    Calculated_mmm = $("#Calculated_mm").val();
                }
            },

            submitDisable: function (e) {
                console.log('call trace -> submitDisable');
                if(e.keyCode == 13){
                    e.preventDefault();
                }
            },

            modi_course_language: function (e){
                console.log('call trace -> modi_course_language');
                // this.model.set('course-language', $('#course-language').val());
                $('.action-primary').click(function() {
                    var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                    var addinfo_user_id = $('#addinfo_user_id').text();
                    var course_language = $('#course-language option:selected').text();
                    $.post("/modi_course_language", {
                        csrfmiddlewaretoken: $.cookie('csrftoken'),
                        addinfo_course_id: addinfo_course_id,
                        addinfo_user_id: addinfo_user_id,
                        course_language: course_language
                    });
                });
            },

            modi_course_level: function (e){
                console.log('call trace -> modi_course_level');
                this.model.set('course_level', $('#selectfixid').val());
                $('.action-primary').click(function() {
                    var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                    var addinfo_user_id = $('#addinfo_user_id').text();
                    var course_level = $('#selectfixid').val();
                    $.post("/modi_course_level", {
                        csrfmiddlewaretoken: $.cookie('csrftoken'),
                        addinfo_course_id: addinfo_course_id,
                        addinfo_user_id: addinfo_user_id,
                        course_level: course_level,
                        method: 'addinfo',
                    });
                });
            },

            subtitle_add: function (e) {
                console.log('call trace -> subtitle_add');
                var selected_code = $('#subtitle_list').val();
                var subtitle_box = $('#subtitle_box').val();
                if (selected_code != '') {
                    var idx = subtitle_box.search(selected_code);
                    if (idx == -1) {
                        if (subtitle_box.length != 0) {
                            subtitle_box += ', ' + selected_code
                            $('#subtitle_box').val(subtitle_box);
                        } else {
                            subtitle_box += selected_code
                            $('#subtitle_box').val(subtitle_box);
                        }
                        this.model.set('subtitle_box', $('#subtitle_box').val());
                        $('.action-primary').click(function() {
                            var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                            var addinfo_user_id = $('#addinfo_user_id').text();
                            $.post( "/modi_subtitle", {
                                subtitle: subtitle_box,
                                addinfo_course_id: addinfo_course_id,
                                addinfo_user_id: addinfo_user_id
                            })
                            .done(function( data ) {
                                if (data.result == 200) {
                                    // success
                                } else {
                                    alert(data.msg);
                                }
                            });

                        });
                    } else {
                        alert('이미 추가된 자막 언어 입니다')
                    }
                } else {
                    alert('자막 언어를 선택해주십시오');
                }
            },

            subtitle_remove: function (e) {
                console.log('call trace -> subtitle_remove');
                var selected_code = $('#subtitle_list').val();
                var subtitle_box = $('#subtitle_box').val();
                var idx = subtitle_box.search(selected_code);
                if (selected_code == "") {
                    alert('자막 언어를 선택해주십시오');
                    return false;
                }
                if (idx != -1) {
                    if (idx == 0) {
                        subtitle_box = subtitle_box.replace(selected_code + ", ", "");
                        subtitle_box = subtitle_box.replace(selected_code, "");
                        console.log(subtitle_box[-1]);
                        $('#subtitle_box').val(subtitle_box);
                    } else {
                        subtitle_box = subtitle_box.replace(", " + selected_code, "");
                        subtitle_box = subtitle_box.replace(selected_code, "");
                        console.log(subtitle_box[-1]);
                        $('#subtitle_box').val(subtitle_box);
                    }
                    this.model.set('subtitle_box', $('#subtitle_box').val());
                    $('.action-primary').click(function() {
                        $.post( "/modi_subtitle", {
                            subtitle: subtitle_box,
                            addinfo_course_id: addinfo_course_id,
                            addinfo_user_id: addinfo_user_id
                        })
                        .done(function( data ) {
                            if (data.result == 200) {
                                // success
                            } else {
                                alert(data.msg);
                            }
                        });
                    });
                } else {
                    alert('등록되지 않은 강좌 자막 언어는 지울 수 없습니다');
                }
            },

            modi_teacher_name: function (e) {
                console.log('call trace -> modi_teacher_name');
                this.model.set('modi_teacher_name', 'modi_teacher_name');
                $('.action-primary').click(function() {
                    var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                    var addinfo_user_id = $('#addinfo_user_id').text();
                    var teacher_name = $('#teacher_name').val();
                    console.log(teacher_name);
                    $.post("/modi_teacher_name", {
                        csrfmiddlewaretoken: $.cookie('csrftoken'),
                        addinfo_course_id: addinfo_course_id,
                        addinfo_user_id: addinfo_user_id,
                        teacher_name: teacher_name,
                        method : 'addinfo',
                    });
                });
            },

            modi_preview_video: function (e) {
                console.log('call trace -> modi_preview_video');
                this.model.set('modi_preview_video', 'modi_preview_video');
                $('.action-primary').click(function() {
                    var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                    var addinfo_user_id = $('#addinfo_user_id').text();
                    var teacher_name = $('#teacher_name').val();
                    var video_url = $('#preview_video').val();
                    console.log(video_url)
                    console.log(teacher_name);
                    $.post("/modi_preview_video", {
                        csrfmiddlewaretoken: $.cookie('csrftoken'),
                        addinfo_course_id: addinfo_course_id,
                        addinfo_user_id: addinfo_user_id,
                        teacher_name: teacher_name,
                        video_url: video_url,
                        method : 'addinfo',
                    });
                });
            },

            render: function() {
                console.log('call trace -> render');
                clearTimeout(this.imageTimer);
                DateUtils.setupDatePicker('start_date', this);
                DateUtils.setupDatePicker('end_date', this);
                DateUtils.setupDatePicker('enrollment_start', this);
                DateUtils.setupDatePicker('enrollment_end', this);
                this.$el.find('#' + this.fieldToSelectorMap['subtitle_box']).val(this.model.get('subtitle_box'));
                this.$el.find('#' + this.fieldToSelectorMap['overview']).val(this.model.get('overview'));
                // var fuck = '<div id="course-info"><section class="about"><h2><i class="fa fa-university"></i>강좌소개</h2><article><h3><i class="fa fa-pencil-square-o"></i>수업내용/목표</h3><div class="article_contents goal">이강좌의수업내용/목표에대한내용이표시됩니다.</div></article><article><h3><i class="fa fa-video-camera"></i>홍보/예시영상</h3><div class="article_contents"><div class="youtubewrap"><video class="video"title="홍보/예시 영상"width="100%"height="100%"controls controlsList="nodownload"><source src="http://vod.kmoocs.kr/vod/2017/09/29/512eedf0-e5c5-4c88-977b-be74c2fc1f4e.mp4"type="video/mp4"></video></div></div></article></section><section class="course-plan"><h2><i class="fa fa-calendar"></i>강좌운영계획</h2><article class="syllabus"><div class="article_contents"><input type="checkbox"name="toggle"id="toggle"/><label for="toggle"></label><div class="syllabus_table"><table summary="강좌 전체에 대한 주차별 차시별 내용 및 과제를 요약해서 보여주는 강의계획서"border="1"cellspacing="0"cellpadding="0"><caption>강의계획서</caption><colgroup><col width="5%"/><col width="30%"/><col width=""/><col width="15%"/></colgroup><thead><tr><th>주차</th><th>주차명</th><th>차시명</th><th>과제</th></tr></thead><tbody><tr><td rowspan="2"class="cts">1</td><td rowspan="2">주차1</td><td>차시1</td><td class="cts">퀴즈1</td></tr><tr><td>차시2</td><td class="cts">토론</td></tr><tr><td class="cts">2</td><td>주차2</td><td>차시1</td><td class="cts">토론</td></tr><tr><td colspan="4"class="bgcolor cts">중간시험</td></tr><tr><td class="cts">3</td><td>주차3</td><td>차시1</td><td class="cts">상호평가</td></tr><tr><td colspan="4"class="cts bgcolor">기말시험</td></tr></tbody></table></div></div></article></section><section class="course-staff"><h2><i class="fa fa-group (alias)"></i>강좌운영팀소개</h2><article><h3><i class="fa fa-user"></i>교수자</h3><article class="professor"><div class="teacher_image"><img src="http://www.kmooc.kr/static/images/placeholder-faculty.png"align="left"alt=""></div><div class="staff_descript"><dl><dt><i class="fa fa-angle-double-right"></i><i class="staff-name"></i>교수</dt><dd>현)한국대학교전산학과교수</dd><dd>전)S기업연구원</dd><dd>한국대학교.컴퓨터공학박사</dd><dd>E-mail:abc@example.com</dd></dl></div></article></article><article><h3><i class="fa fa-user"></i>강좌지원팀</h3><article class="staff"><div class="ta_image"><img src="http://www.kmooc.kr/static/images/placeholder-faculty.png"align="left"alt=""></div><div class="staff_descript"><dl><dt><i class="fa fa-angle-double-right"></i><i class="staff-name">조교</i></dt><dd>한국대학교전산학박사과정</dd><dd>E-mail:abc@example.com</dd></dl></div></article></article></section><section class="info"><h2><i class="fa fa-info-circle"></i>강좌수강정보</h2><article><h3><i class="fa fa-graduation-cap"></i>이수/평가정보</h3><div class="grade_table"><table style="width: 100%;"border="1"summary="이수/평가정보"cellspacing="0"cellpadding="0"><caption>이수/평가정보</caption><colgroup><col width="20%"><col width="20%"><col width="20%"><col width="20%"><col width="20%"><col width="20%"></colgroup><thead><tr><th>과제명</th><th>퀴즈</th><th>토론</th><th>중간고사</th><th>기말고사</th></tr></thead><tbody style="text-align: center;"><tr><td style="font-weight: bold;">반영비율</td><td>%</td><td>%</td><td>%</td><td>%</td></tr></tbody></table><b>※&nbsp;총60%이상점수획득시,이수증을발급받을수있습니다.</b></div></article><article><h3><i class="fa fa-sort-amount-desc"></i>강좌수준및선수요건</h3><p id="course-level">이강좌는유익한내용이다수포함되어있습니다.</p></article><article><h3><i class="fa fa-book"></i>교재및참고문헌</h3><p id="course-reference">이강좌는여러가지참고자료가많이있습니다.</p></article></section><section class="faq"><h2><i class="fa fa-question-circle"></i>자주묻는질문</h2><article class="question"><h4><i class=\'fa fa-chevron-right\'></i>강좌교재가따로있나요?</h4><p>네.있습니다.</p></article><article class="question"><h4><i class=\'fa fa-chevron-right\'></i>강좌교재가따로있나요?</h4><p>네.있습니다.</p></article></section><section class="user_add"><h2><i class="fa fa-plus-circle"></i>제목</h2><article class="question"><h3><i class=\'fa fa-chevron-right\'></i>소제목</h3><p>내용</p></article><br></section></div>';
                // this.$el.find('#' + this.fieldToSelectorMap['overview']).val(fuck);
                this.codeMirrorize(null, $('#course-overview')[0]);
                this.$el.find('#' + this.fieldToSelectorMap['course_level']).val(this.model.get('course_level'));
                if (this.model.get('title') !== '') {
                    this.$el.find('#' + this.fieldToSelectorMap.title).val(this.model.get('title'));
                } else {
                    var displayName = this.$el.find('#' + this.fieldToSelectorMap.title).attr('data-display-name');
                    this.$el.find('#' + this.fieldToSelectorMap.title).val(displayName);
                }
                this.$el.find('#' + this.fieldToSelectorMap.subtitle).val(this.model.get('subtitle'));
                this.$el.find('#' + this.fieldToSelectorMap.duration).val(this.model.get('duration'));
                this.$el.find('#' + this.fieldToSelectorMap.description).val(this.model.get('description'));
                //교수자명
                this.$el.find('#' + this.fieldToSelectorMap['teacher_name']).val(this.model.get('teacher_name'));
                //강좌미리보기
                // this.$el.find('#' + this.fieldToSelectorMap['preview_video']).val(this.model.get('preview_video'));
                this.$el.find('#' + this.fieldToSelectorMap['short_description']).val(this.model.get('short_description'));
                this.$el.find('.current-course-introduction-video iframe').attr('src', this.model.videosourceSample());
                this.$el.find('#' + this.fieldToSelectorMap['intro_video']).val(this.model.get('intro_video') || '');
                if (this.model.has('intro_video')) {
                    this.$el.find('.remove-course-introduction-video').show();
                }
                else this.$el.find('.remove-course-introduction-video').hide();
                this.$el.find('#' + this.fieldToSelectorMap['effort']).val(this.model.get('effort'));
                var courseImageURL = this.model.get('course_image_asset_path');
                this.$el.find('#course-image-url').val(courseImageURL);
                this.$el.find('#course-image').attr('src', courseImageURL);
                var bannerImageURL = this.model.get('banner_image_asset_path');
                this.$el.find('#banner-image-url').val(bannerImageURL);
                this.$el.find('#banner-image').attr('src', bannerImageURL);
                var videoThumbnailImageURL = this.model.get('video_thumbnail_image_asset_path');
                this.$el.find('#video-thumbnail-image-url').val(videoThumbnailImageURL);
                this.$el.find('#video-thumbnail-image').attr('src', videoThumbnailImageURL);
                var pre_requisite_courses = this.model.get('pre_requisite_courses');
                pre_requisite_courses = pre_requisite_courses.length > 0 ? pre_requisite_courses : '';
                this.$el.find('#' + this.fieldToSelectorMap['pre_requisite_courses']).val(pre_requisite_courses);
                if (this.model.get('entrance_exam_enabled') == 'true') {
                    this.$('#' + this.fieldToSelectorMap['entrance_exam_enabled']).attr('checked', this.model.get('entrance_exam_enabled'));
                    this.$('.div-grade-requirements').show();
                }
                else {
                    this.$('#' + this.fieldToSelectorMap['entrance_exam_enabled']).removeAttr('checked');
                    this.$('.div-grade-requirements').hide();
                }
                this.$('#' + this.fieldToSelectorMap['entrance_exam_minimum_score_pct']).val(this.model.get('entrance_exam_minimum_score_pct'));
                var selfPacedButton = this.$('#course-pace-self-paced'),
                    instructorPacedButton = this.$('#course-pace-instructor-paced'),
                    paceToggleTip = this.$('#course-pace-toggle-tip');
                (this.model.get('self_paced') ? selfPacedButton : instructorPacedButton).attr('checked', true);
                if (this.model.canTogglePace()) {
                    selfPacedButton.removeAttr('disabled');
                    instructorPacedButton.removeAttr('disabled');
                    paceToggleTip.text('');
                }
                else {
                    selfPacedButton.attr('disabled', true);
                    instructorPacedButton.attr('disabled', true);
                    paceToggleTip.text(gettext('Course pacing cannot be changed once a course has started.'));
                }
                this.licenseView.render();
                this.learning_info_view.render();
                this.instructor_info_view.render();
                var time = $("#course-effort").val();
                if(time){
                    if (time.indexOf("@") > 0 && time.indexOf("#") > 0 && time.indexOf("$") > 0) {
                        var arr1 = time.split("@");
                        var arr2 = arr1[0].split(":");
                        var week = arr1[1].split("#")[0];
                        var arr3 = arr1[1].split("#")[1].split("$")[0].split(":");
                        var arr4 = arr1[1].split("$")[1].split(":");
                        $("#course-effort-hh").val(arr2[0]);
                        $("#course-effort-mm").val(arr2[1]);
                        $("#course-effort-week").val(week);
                        $("#course-video-hh").val(arr3[0]);
                        $("#course-video-mm").val(arr3[1]);
                        $("#Calculated").val(arr4[0]);
                        $("#Calculated_mm").val(arr4[1]);
                    } else if(time.indexOf("@") > 0 && time.indexOf("#") > 0) {
                        var arr1 = time.split("@");
                        var arr2 = arr1[0].split(":");
                        var week = arr1[1].split("#")[0];
                        var arr3 = arr1[1].split("#")[1].split(":");
                        $("#course-effort-hh").val(arr2[0]);
                        $("#course-effort-mm").val(arr2[1]);
                        $("#course-effort-week").val(week);
                        $("#course-video-hh").val(arr3[0]);
                        $("#course-video-mm").val(arr3[1]);
                    } else if(time.indexOf("@") > 0) {
                        var arr1 = time.split("@");
                        var arr2 = arr1[0].split(":");
                        var week = arr1[1];
                        $("#course-effort-hh").val(arr2[0]);
                        $("#course-effort-mm").val(arr2[1]);
                        $("#course-effort-week").val(week);
                    } else if(time.indexOf("#") > 0) {
                        var arr1 = time.split("#");
                        var arr2 = arr1[0].split(":");
                        var arr3 = arr1[1].split(":");
                        $("#course-effort-hh").val(arr2[0]);
                        $("#course-effort-mm").val(arr2[1]);
                        $("#course-video-hh").val(arr3[0]);
                        $("#course-video-mm").val(arr3[1]);
                    } else {
                        $("#course-effort-hh").val(time.split(':')[0]);
                        $("#course-effort-mm").val(time.split(':')[1]);
                    }
                }
                var hh = $("#course-effort-hh").val();
                var mm = $("#course-effort-mm").val();
                var week = $("#course-effort-week").val();
                if(hh && mm && week){
                    // 총 이수시간 계산 및 표시
                    var total_time = (Number(hh) * Number(week)) + (Number(mm)/60 * Number(week));
                    if (total_time.toString().indexOf(".") > 0) {
                        var arr = total_time.toString().split(".");
                        var hour = arr[0];
                        var minute = Math.round(Number(arr[1]) / 10 * 60).toString().substr(0, 2);
                    } else {
                        // pass
                    }
                }

                // 현재 날짜 기준 (UTC) 과 강좌 일정을 비교하여 수정이 안되도록 수정
                var now = new Date();
                var now_utc = new Date(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(),  now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds());
                var start_date_value = $("#course-start-date").val() + " " + $("#course-start-time").val();
                var end_date_value = $("#course-end-date").val() + " " + $("#course-end-time").val();
                var enroll_start_date_value = $("#course-enrollment-start-date").val() + " " + $("#course-enrollment-start-time").val();
                var enroll_end_date_value = $("#course-enrollment-end-date").val() + " " + $("#course-enrollment-end-time").val();
                var start_date = new Date(start_date_value);
                var end_date = new Date(end_date_value);
                var enroll_start_date = new Date(enroll_start_date_value);
                var enroll_end_date = new Date(enroll_end_date_value);
                if(this.model.get('need_lock') == 1){
                    /*
                        -수업주차,주간학습권장시간,총동영상 재생시간
                        -수강신청시작일/마감일, 개강일/종강일
                        -강좌 언어
                        -강좌 불러오기 메뉴 비활성화(내보내기는 가능하게 그대로 둠)
                    */
                    $("#course-start-date,#course-start-time").attr("disabled", true).css("background", "#ccc");
                    $("#course-end-date,#course-end-time").attr("disabled", true).css("background", "#ccc");
                    $("#course-enrollment-start-date,#course-enrollment-start-time").attr("disabled", true).css("background", "#ccc");
                    $("#course-enrollment-end-date,#course-enrollment-end-time").attr("disabled", true).css("background", "#ccc");
                    $("#course-language").attr("disabled", true).css("background", "#ccc");
                    $("#field-course-effort input").attr("disabled", true).css("background", "#ccc");
                    $("#teacher_name").attr("disabled", true).css("background", "#ccc");
                    $("#selectfixid").attr("disabled", true).css("background", "#ccc");
                }
                // 강좌 개요 서버사이드 렌더링 처리
                var user_edit = $("#course_edit_check").val();
                if (user_edit == 'Y') {
                    $(".CodeMirror-scroll").css({'pointer-events': 'all', 'opacity': 1});
                    $(".CodeMirror").removeProp('id');
                    $(".x-over").hide();
                    $('.ue_n').hide();
                    $('.ue_y').show();
                    $(".CodeMirror").css('background', '#ffffff');
                } else {
                    $(".CodeMirror").css('background', '#c1c1c1');
                    $('.ue_n').show();
                    $('.ue_y').hide();
                }
                return this;
            },

            fieldToSelectorMap: {
                language: 'course-language',
                start_date: 'course-start',
                end_date: 'course-end',
                enrollment_start: 'enrollment-start',
                enrollment_end: 'enrollment-end',
                certificate_available_date: 'certificate-available',
                overview: 'course-overview',
                title: 'course-title',
                subtitle: 'course-subtitle',
                duration: 'course-duration',
                description: 'course-description',
                about_sidebar_html: 'course-about-sidebar-html',
                //교수자명
                teacher_name: 'teacher_name',
                //강좌 미리보기
                preview_video: 'preview_video',
                short_description: 'course-short-description',
                intro_video: 'course-introduction-video',
                //강좌 난이도
                subtitle_box: 'subtitle_box',
                course_level: 'selectfixid',
                effort: 'course-effort',
                course_image_asset_path: 'course-image-url',
                banner_image_asset_path: 'banner-image-url',
                video_thumbnail_image_asset_path: 'video-thumbnail-image-url',
                pre_requisite_courses: 'pre-requisite-course',
                entrance_exam_enabled: 'entrance-exam-enabled',
                entrance_exam_minimum_score_pct: 'entrance-exam-minimum-score-pct',
                course_settings_learning_fields: 'course-settings-learning-fields',
                add_course_learning_info: 'add-course-learning-info',
                add_course_instructor_info: 'add-course-instructor-info',
                course_learning_info: 'course-learning-info',
                user_edit: 'course_edit_check',
            },

            addLearningFields: function() {
                console.log('call trace -> addLearningFields');
                /*
                * Add new course learning fields.
                * */
                var existingInfo = _.clone(this.model.get('learning_info'));
                existingInfo.push('');
                this.model.set('learning_info', existingInfo);
            },

            addInstructorFields: function() {
                console.log('call trace -> addInstructorFields');
                /*
                * Add new course instructor fields.
                * */
                var instructors = this.model.get('instructor_info').instructors.slice(0);
                instructors.push({
                    name: '',
                    title: '',
                    organization: '',
                    image: '',
                    bio: ''
                });
                this.model.set('instructor_info', {instructors: instructors});
            },

            updateTime: function(e) {
                console.log('call trace -> updateTime');
                var now = new Date(),
                    hours = now.getUTCHours(),
                    minutes = now.getUTCMinutes(),
                    currentTimeText = StringUtils.interpolate(
                        gettext('{hours}:{minutes} (current UTC time)'),
                        {
                            hours: hours,
                            minutes: minutes
                        }
                    );
                $(e.currentTarget).attr('title', currentTimeText);
            },

            updateModel: function(event) {
                console.log('call trace -> updateModel');
                var value;
                var index = event.currentTarget.getAttribute('data-index');

                switch (event.currentTarget.id) {
                    case 'course-learning-info-' + index:
                        value = $(event.currentTarget).val();
                        var learningInfo = this.model.get('learning_info');
                        learningInfo[index] = value;
                        this.showNotificationBar();
                        break;
                    case 'course-instructor-name-' + index:
                    case 'course-instructor-title-' + index:
                    case 'course-instructor-organization-' + index:
                    case 'course-instructor-bio-' + index:
                        value = $(event.currentTarget).val();
                        var field = event.currentTarget.getAttribute('data-field'),
                            instructors = this.model.get('instructor_info').instructors.slice(0);
                        instructors[index][field] = value;
                        this.model.set('instructor_info', {instructors: instructors});
                        this.showNotificationBar();
                        break;
                    case 'course-instructor-image-' + index:
                        instructors = this.model.get('instructor_info').instructors.slice(0);
                        instructors[index].image = $(event.currentTarget).val();
                        this.model.set('instructor_info', {instructors: instructors});
                        this.showNotificationBar();
                        this.updateImagePreview(event.currentTarget, '#course-instructor-image-preview-' + index);
                        break;
                    case 'course-image-url':
                        this.updateImageField(event, 'course_image_name', '#course-image');
                        break;
                    case 'banner-image-url':
                        this.updateImageField(event, 'banner_image_name', '#banner-image');
                        break;
                    case 'video-thumbnail-image-url':
                        this.updateImageField(event, 'video_thumbnail_image_name', '#video-thumbnail-image');
                        break;
                    case 'entrance-exam-enabled':
                        if ($(event.currentTarget).is(':checked')) {
                            this.$('.div-grade-requirements').show();
                        } else {
                            this.$('.div-grade-requirements').hide();
                        }
                        this.setField(event);
                        break;
                    case 'entrance-exam-minimum-score-pct':
                        // If the val is an empty string then update model with default value.
                        if ($(event.currentTarget).val() === '') {
                            this.model.set('entrance_exam_minimum_score_pct', this.model.defaults.entrance_exam_minimum_score_pct);
                        } else {
                            this.setField(event);
                        }
                        break;
                    case 'pre-requisite-course':
                        var value = $(event.currentTarget).val();
                        value = value == '' ? [] : [value];
                        this.model.set('pre_requisite_courses', value);
                        break;
                    // Don't make the user reload the page to check the Youtube ID.
                    // Wait for a second to load the video, avoiding egregious AJAX calls.
                    case 'course-introduction-video':
                        this.clearValidationErrors();
                        var previewsource = this.model.set_videosource($(event.currentTarget).val());
                        clearTimeout(this.videoTimer);
                        this.videoTimer = setTimeout(_.bind(function() {
                            this.$el.find('.current-course-introduction-video iframe').attr('src', previewsource);
                            if (this.model.has('intro_video')) {
                                this.$el.find('.remove-course-introduction-video').show();
                            } else {
                                this.$el.find('.remove-course-introduction-video').hide();
                            }
                        }, this), 1000);
                        break;
                    case 'course-pace-self-paced':
                    // Fallthrough to handle both radio buttons
                    case 'course-pace-instructor-paced':
                        this.model.set('self_paced', JSON.parse(event.currentTarget.value));
                        break;
                    case 'course-language':
                    case 'course-effort':
                    case 'course-title':
                    case 'course-subtitle':
                    case 'course-duration':
                    case 'subtitle_box':
                    case 'teacher_name':
                    case 'course-description':
                    case 'preview_video':
                    case 'course-short-description':
                        this.setField(event);
                        break;
                    default: // Everything else is handled by datepickers and CodeMirror.
                        break;
                }
            },

            updateImageField: function(event, image_field, selector) {
                console.log('call trace -> updateImageField');
                this.setField(event);
                var url = $(event.currentTarget).val();
                var image_name = _.last(url.split('/'));
                // If image path is entered directly, we need to strip the asset prefix
                image_name = _.last(image_name.split('block@'));
                this.model.set(image_field, image_name);
                this.updateImagePreview(event.currentTarget, selector);
            },

            updateImagePreview: function(imagePathInputElement, previewSelector) {
                console.log('call trace -> updateImagePreview');
                // Wait to set the image src until the user stops typing
                clearTimeout(this.imageTimer);
                this.imageTimer = setTimeout(function() {
                    $(previewSelector).attr('src', $(imagePathInputElement).val());
                }, 1000);
            },

            removeVideo: function(event) {
                console.log('call trace -> removeVideo');
                event.preventDefault();
                if (this.model.has('intro_video')) {
                    this.model.set_videosource(null);
                    this.$el.find('.current-course-introduction-video iframe').attr('src', '');
                    this.$el.find('#' + this.fieldToSelectorMap.intro_video).val('');
                    this.$el.find('.remove-course-introduction-video').hide();
                }
            },

            codeMirrors: {},

            codeMirrorize: function(e, forcedTarget) {
                console.log('call trace -> codeMirrorize');
                var thisTarget, cachethis, field, cmTextArea;
                if (forcedTarget) {
                    thisTarget = forcedTarget;
                    thisTarget.id = $(thisTarget).attr('id');
                } else if (e !== null) {
                    thisTarget = e.currentTarget;
                } else {
                    // e and forcedTarget can be null so don't deference it
                    // This is because in cases where we have a marketing site
                    // we don't display the codeMirrors for editing the marketing
                    // materials, except we do need to show the 'set course image'
                    // workflow. So in this case e = forcedTarget = null.
                    return;
                }
                if (!this.codeMirrors[thisTarget.id]) {
                    cachethis = this;
                    field = this.selectorToField[thisTarget.id];
                    this.codeMirrors[thisTarget.id] = CodeMirror.fromTextArea(thisTarget, {
                        mode: 'text/html', lineNumbers: true, lineWrapping: true});
                    this.codeMirrors[thisTarget.id].on('change', function(mirror) {
                        mirror.save();
                        cachethis.clearValidationErrors();
                        var newVal = mirror.getValue();
                        if (cachethis.model.get(field) != newVal) {
                            cachethis.setAndValidate(field, newVal);
                        }
                    });
                    cmTextArea = this.codeMirrors[thisTarget.id].getInputField();
                    cmTextArea.setAttribute('id', thisTarget.id + '-cm-textarea');
                }
            },

            revertView: function() {
                console.log('call trace -> revertView');
                // Make sure that the CodeMirror instance has the correct
                // data from its corresponding textarea
                var self = this;
                this.model.fetch({
                    success: function() {
                        self.render();
                        _.each(self.codeMirrors, function(mirror) {
                            var ele = mirror.getTextArea();
                            var field = self.selectorToField[ele.id];
                            mirror.setValue(self.model.get(field));
                        });
                        self.licenseModel.setFromString(self.model.get('license'), {silent: true});
                        self.licenseView.render();
                    },
                    reset: true,
                    silent: true});
            },

            setAndValidate: function(attr, value) {
                console.log('call trace -> setAndValidate');
                // If we call model.set() with {validate: true}, model fields
                // will not be set if validation fails. This puts the UI and
                // the model in an inconsistent state, and causes us to not
                // see the right validation errors the next time validate() is
                // called on the model. So we set *without* validating, then
                // call validate ourselves.
                this.model.set(attr, value);
                this.model.isValid();
            },

            showNotificationBar: function() {
                console.log('call trace -> showNotificationBar');
                // We always call showNotificationBar with the same args, just
                // delegate to superclass
                ValidatingView.prototype.showNotificationBar.call(this,
                    this.save_message,
                    _.bind(this.saveView, this),
                    _.bind(this.revertView, this));
            },

            uploadImage: function(event) {
                console.log('call trace -> uploadImage');
                event.preventDefault();
                var title = '',
                    selector = '',
                    image_key = '',
                    image_path_key = '';
                switch (event.currentTarget.id) {
                    case 'upload-course-image':
                        title = gettext('Upload your course image.');
                        selector = '#course-image';
                        image_key = 'course_image_name';
                        image_path_key = 'course_image_asset_path';
                        break;
                    case 'upload-banner-image':
                        title = gettext('Upload your banner image.');
                        selector = '#banner-image';
                        image_key = 'banner_image_name';
                        image_path_key = 'banner_image_asset_path';
                        break;
                    case 'upload-video-thumbnail-image':
                        title = gettext('Upload your video thumbnail image.');
                        selector = '#video-thumbnail-image';
                        image_key = 'video_thumbnail_image_name';
                        image_path_key = 'video_thumbnail_image_asset_path';
                        break;
                }
                var upload = new FileUploadModel({
                    title: title,
                    message: gettext('Files must be in JPEG or PNG format.'),
                    mimeTypes: ['image/jpeg', 'image/png']
                });
                var self = this;
                var modal = new FileUploadDialog({
                    model: upload,
                    onSuccess: function(response) {
                        var options = {};
                        options[image_key] = response.asset.display_name;
                        options[image_path_key] = response.asset.url;
                        self.model.set(options);
                        self.render();
                        $(selector).attr('src', self.model.get(image_path_key));
                    }
                });
                modal.show();
            },

            handleLicenseChange: function() {
                console.log('call trace -> handleLicenseChange');
                this.showNotificationBar();
                this.model.set('license', this.licenseModel.toString());
            },
            preview_video_add: function(){
                var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();

                $(".video_regist").each(function () {
                    if($("#course-preview-video-url").val() == $(this).data('video-url')){
                        $(this).attr('disabled', true);
                    }else{
                        $(this).attr('disabled', false);
                    }
                })

                $("#previewCourseEditLayer").toggle();
                if($("#previewCourseEditLayer").is(":visible")){
                    var top = parseInt($(window).scrollTop());
                    $(".overview-modal").prop("style", "top: " + (top - 50) + "px;");
                }
            },
            preview_video_cancel: function (event) {

                event.preventDefault();
                $("#previewCourseEditLayer").toggle();
            },
            video_regist: function (event) {
                event.preventDefault();

                $("#video-url").val(event.currentTarget.getAttribute('data-video-url'))

                $(".video_regist").each(function () {
                    $(this).attr('disabled', false);
                })

                event.currentTarget.setAttribute('disabled', 'disabled')
            },
            course_preview_video_save: function () {

                event.preventDefault();

                $("#previewCourseEditLayer").toggle();

                $("#preview_video").val($("#video-url").val());

                this.model.set('modi_preview_video', 'modi_preview_video');

                $('.action-primary').click(function() {
                    var addinfo_course_id = 'course-v1:' + $('#course-organization').val() + '+' + $('#course-number').val() + '+' + $('#course-name').val();
                    var addinfo_user_id = $('#addinfo_user_id').text();
                    var teacher_name = $('#teacher_name').val();
                    var video_url = $('#video-url').val();
                    $.post("/modi_preview_video", {
                        csrfmiddlewaretoken: $.cookie('csrftoken'),
                        addinfo_course_id: addinfo_course_id,
                        addinfo_user_id: addinfo_user_id,
                        teacher_name: teacher_name,
                        video_url: video_url,
                        method : 'addinfo',
                    });
                });
            }
        });

        return DetailsView;
    }); // end define()
