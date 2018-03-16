define(["js/views/validation", "codemirror", "underscore", "jquery", "jquery.ui", "js/utils/date_utils",
    "js/models/uploads", "js/views/uploads", "js/views/license", "js/models/license",
    "common/js/components/views/feedback_notification", "jquery.timepicker", "date", "gettext",
    "js/views/learning_info", "js/views/instructor_info", "edx-ui-toolkit/js/utils/string-utils"],
       function(ValidatingView, CodeMirror, _, $, ui, DateUtils, FileUploadModel,
                FileUploadDialog, LicenseView, LicenseModel, NotificationView,
                timepicker, date, gettext, LearningInfoView, InstructorInfoView, StringUtils) {

var DetailsView = ValidatingView.extend({
    // Model class is CMS.Models.Settings.CourseDetails
    events : {
        "input input" : "updateModel",
        "input textarea" : "updateModel",
        // Leaving change in as fallback for older browsers
        "change input" : "updateModel",
        "change textarea" : "updateModel",
        "change select" : "updateModel",
        'click .remove-course-introduction-video' : "removeVideo",
        'focus #course-overview' : "codeMirrorize",
        'mouseover .timezone' : "updateTime",
        // would love to move to a general superclass, but event hashes don't inherit in backbone :-(
        'focus :input' : "inputFocus",
        'blur :input' : "inputUnfocus",

        //'focus #field-course-overview' : "updateOverview",
        'click .toggleOverviewLayer': "toggleOverviewLayer",
        'click #createOverview': "createOverview",
        'click .tabs>div': "tabChange",

        'click .action-upload-image': "uploadImage",
        'click .add-course-learning-info': "addLearningFields",
        'click .add-course-instructor-info': "addInstructorFields",

        //setEffort event 관련
        'blur #course-effort-hh': "setEffort",
        'blur #course-effort-mm': "setEffort",
        'blur #course-video-hh': "setEffort",
        'blur #course-video-mm': "setEffort",
        'blur #course-effort-week': "setEffort",
        'change #course-effort-hh': "setEffort",
        'change #course-effort-mm': "setEffort",
        'change #course-video-hh': "setEffort",
        'change #course-video-mm': "setEffort",
        'change #course-effort-week': "setEffort",

        //강좌 운영진 소개의 추가 및 삭제 이벤트
        'click #overview-tab3 .remove-item': "delStaffItem",
        'click #overview-tab3 .add-item': "addStaffItem",

        //FAQ 추가 및 삭제 이벤트
        'click #overview-tab5 .remove-item': "delQuestionItem",
        'click #overview-tab5 .add-item': "addQuestionItem",

    },

    initialize : function(options) {
        //강좌 운영진 추가 기본 템플릿 초기화
        this.staff_row_template = $("#course-instructor").clone();
        this.question_row_template = $("#course-question").clone();

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

        //개발용 탭 초기화
        //$(".tabs div:eq(2)").click();

    },
    addStaffItem: function(event){
        event.preventDefault();
        $("#course-instructor").append($(this.staff_row_template).html());
    },
    delStaffItem: function(event){
        event.preventDefault();
        $(event.currentTarget).parent().parent().remove();
    },
    addQuestionItem: function(event){
        event.preventDefault();
        $("#course-question").append($(this.question_row_template).html());
    },
    delQuestionItem: function(event){
        event.preventDefault();
        $(event.currentTarget).parent().parent().remove();
    },
    overviewLayerSetting: function(){
        //overviewLayerEditor 상에 표시될 항목들을 셋팅한다.
        var regex = /<br\s*[\/]?>/gi;

        // overview object
        var ov = $.parseHTML(this.model.get('overview'));
        // 수업내용/목표
        var goal = $(ov).find(".goal:eq(0)").html().replace(regex, "\n");
        // 홍보영상/예시강의
        var vurl = $(ov).find(".video:eq(0)").attr("src");
        // 강좌 계획
        var syllabus = $(ov).find(".syllabus_table:eq(0)");
        // 강좌운영진
        var team = $(ov).find(".course-staff:eq(0)").html();
        // 이수/평가정보
        var evaluation = $(ov).find(".grade_table:eq(0)");
        // 강좌 수준 및 선수요건
        var level = $(ov).find("#course-level").html().replace(regex, "\n");
        // 교재 및 참고문헌
        var reference = $(ov).find("#course-reference").html().replace(regex, "\n");
        // FAQ
        var faq = $(ov).find(".faq article");
        // 사용자 추가 내용
        var user_content = $(ov).find(".user_add").html();

        // ------------------------------------------------
        //syllabus table 에 에디터 안에서의 크기조절을 위한 속성 추가
        syllabus.find("table").attr("style", "width: 100%;");
        evaluation.find("table").attr("style", "width: 100%;");
        // ------------------------------------------------

        // debug s
        console.log('overviewLayerSetting --- s');
        console.log(goal);
        console.log(vurl);
        console.log(syllabus.html());
        console.log('overviewLayerSetting --- e');
        // debug e

        //tinymce 에디터 사용시 getContent 함수 이용을 위해 textarea 의 아이디를 지정하요 사용
        $("#overview-tab1 textarea").text(goal);
        $("#overview-tab1 input").val(vurl);
        $("#course_plan").text(syllabus.html());
        $("#grade_table").text(evaluation.html());

        $("#overview-tab4 textarea:eq(1)").text(level);
        $("#overview-tab4 textarea:eq(2)").text(reference);

        this.tinymceInit('#course_plan');
        this.tinymceInit('#user_content');
        this.tinymceInit('#grade_table');

        //tinymce.get('course_plan').setContent(syllabus.html());

    },
    tinymceInit: function (selector) {
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
        var hh = $("#course-effort-hh").val();
        var mm = $("#course-effort-mm").val();
        var week = $("#course-effort-week").val();
        var video_hh = $("#course-video-hh").val();
        var video_mm = $("#course-video-mm").val();

        if(isNaN(hh) || isNaN(mm)|| isNaN(week)){
            $("#course-effort").trigger("change");
            return;
        }

        if(!hh || hh == null || hh == ""){
            hh = "00";
        }

        if(!mm || mm == null || mm == ""){
            mm = "00";
        }

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

        var video = video_hh + ":" + video_mm;

        if(hh && mm && week){
            // 총 이수시간 계산 및 표시
            var total_time = (Number(hh) * Number(week)) + (Number(mm)/60 * Number(week));
            if(total_time.toString().indexOf(".") > 0){
                var arr = total_time.toString().split(".");
                var hour = arr[0];
                var minute = Math.round(Number(arr[1]) / 10 * 60).toString().substr(0, 2);

                $("#Calculated").val(hour + "시간 " + minute + "분");
            }else{
                $("#Calculated").val(total_time + "시간");
            }
        }

        var val = hh + ":" + mm;

        if(week && week != "")
            val = val + "@" + week;

        if(video && video != "")
            val = val + "#" + video;

        $("#course-effort").val(val);
        $("#course-effort").trigger("change");
    },
    createOverview: function(event){
        var course_plan = $.parseHTML(tinymce.get('course_plan').getContent());

        //make html source
        var ov = $.parseHTML(this.model.get('overview'));
        $(ov).find(".goal:eq(0)").html($("#overview-tab1 textarea").val().replace(/\n/g, "<br>"));
        $(ov).find(".video:eq(0)").attr("src", $("#course-sample-video-url").val());
        $(ov).find(".syllabus_table:eq(0)").html($('<table>').append(course_plan).html());

        // 강좌운영진
        $(ov).find(".course-staff:eq(0)").html("<h2><i class=\"fa fa-group (alias)\"></i>강좌운영진 소개</h2>");
        $("#course-instructor li").each(function(){
            var staff_photo = $(this).find("#staff-photo").val();
            var staff_name = $(this).find("#staff-name").val();

            if(staff_name === "")
                return true;

            var careers = $(this).find("textarea").val().split(/\n/g);
            var careers_text = "";

            for (var i=0; i<careers.length;i++){
                if(careers[i])
                    careers_text += "<dd>" + careers[i] + "</dd>";
            }

            var staff_template = "" +
            "<article>" +
            "	<h3><i class='fa fa-user'></i>교수자</h3>" +
            "	<article class='staff'>" +
            "		<div class='teacher_image'>" +
            "			<img src='" + staff_photo + "' align='left' alt=''>" +
            "		</div>" +
            "		<div class='staff_descript'>" +
            "			<dl>" +
            "				<dt>" +
            "				 <i class='fa fa-angle-double-right'></i>대표교수 : " + staff_name + " 교수" +
            "			  </dt>" +
            "				" + careers_text +
            "			</dl>" +
            "		</div>" +
            "	</article>" +
            "</article>";

            $(ov).find(".course-staff:eq(0)").append(staff_template);
        });

        $("#course-ta li").each(function(){
            var staff_photo = $(this).find("#staff-photo").val();
            var staff_name = $(this).find("#staff-name").val();

            if(staff_name === "")
                return true;

            var careers = $(this).find("textarea").val().split(/\n/g);
            var careers_text = "";

            for (var i=0; i<careers.length;i++){
                if(careers[i])
                    careers_text += "<dd>" + careers[i] + "</dd>";
            }

            var staff_template = "" +
            "<article>" +
            "	<h3><i class='fa fa-user'></i>강좌지원팀</h3>" +
            "	<article class='staff'>" +
            "		<div class='ta_image'>" +
            "			<img src='" + staff_photo + "' align='left' alt=''>" +
            "		</div>" +
            "		<div class='staff_descript'>" +
            "			<dl>" +
            "				<dt>" +
            "				 <i class='fa fa-angle-double-right'></i>학습 지원 : " + staff_name+
            "			  </dt>" +
            "				" + careers_text +
            "			</dl>" +
            "		</div>" +
            "	</article>" +
            "</article>";

            $(ov).find(".course-staff:eq(0)").append(staff_template);
        });

        // 이수/평가정보
        var grade_table = $.parseHTML(tinymce.get('grade_table').getContent());

        //make html source
        $(ov).find(".grade_table:eq(0)").html($('<table>').append(grade_table).html());

        // 강좌 수준 및 선수요건
        $(ov).find("#course-level:eq(0)").html($("#overview-tab4 textarea:eq(1)").val().replace(/\n/g, "<br>"));

        // 교재 및 참고문헌
        $(ov).find("#course-reference:eq(0)").html($("#overview-tab4 textarea:eq(2)").val().replace(/\n/g, "<br>"));

        // FAQ
        $(ov).find(".faq:eq(0)").html("<h2><i class=\"fa fa-question-circle\"></i>자주 묻는 질문</h2>");
        $("#course-question li").each(function(){
            var question = $(this).find("#faq-question").val();
            var answer = $(this).find("#faq-answer").val();

            console.log('question: ' + question);
            console.log('answer: ' + answer);

            var template = "" +
            "<article class='question'>" +
            "	<h4>" + question + "</h4>" +
            "	<p>" + answer + "</p>" +
            "</article>";
            $(ov).find(".faq:eq(0)").append(template);
        });

        // 사용자 추가 내용
        $(ov).find(".user_add:eq(0)").html($("#user_content").val().replace(/\n/g, "<br>"));

        //this.model.set('overview', '<div id="course-info">' + $("<div>").append($(ov).clone()).html() + '</div>');

        var html_format_options = {
          "indent":"yes",
          "indent-spaces":2,
          "wrap":80,
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
        }

        var html = $("<div>").append($(ov).clone()).html();
        var result = tidy_html5(html, html_format_options);

        this.model.set('overview', result);
        $("#overviewEditLayer").toggle();
        this.render();

    },
    toggleOverviewLayer: function(event){
        event.preventDefault();
        $("#overviewEditLayer").toggle();
        if($("#overviewEditLayer").is(":visible")){
            var top = parseInt($(window).scrollTop());
            $(".overview-modal").prop("style", "top: " + (top - 50) + "px;");

            this.overviewLayerSetting();
        }
    },
    tabChange: function(event){
        event.preventDefault();
        var t = event.currentTarget.getAttribute('data-target');
        $(".tabs>div").removeClass("on")
        $(event.target).addClass("on");
        $("#overviewEditLayer div[id^='overview-tab']").hide();
        $("#" + t).show();
    },
    isEditable: function(){
        //수정 가능조건 확인후 직접 수정 또는 템플릿 이용 구분
        return true;

    },
    render: function() {
        //console.log("render start --- s");
        //console.log(this.model.get('overview'));
        //console.log("render start --- e");
        // Clear any image preview timeouts set in this.updateImagePreview
        clearTimeout(this.imageTimer);

        DateUtils.setupDatePicker('start_date', this);
        DateUtils.setupDatePicker('end_date', this);
        DateUtils.setupDatePicker('enrollment_start', this);
        DateUtils.setupDatePicker('enrollment_end', this);

        this.$el.find('#' + this.fieldToSelectorMap['overview']).val(this.model.get('overview'));
        this.codeMirrorize(null, $('#course-overview')[0]);

        if (this.model.get('title') !== '') {
            this.$el.find('#' + this.fieldToSelectorMap.title).val(this.model.get('title'));
        } else {
            var displayName = this.$el.find('#' + this.fieldToSelectorMap.title).attr('data-display-name');
            this.$el.find('#' + this.fieldToSelectorMap.title).val(displayName);
        }
        this.$el.find('#' + this.fieldToSelectorMap.subtitle).val(this.model.get('subtitle'));
        this.$el.find('#' + this.fieldToSelectorMap.duration).val(this.model.get('duration'));
        this.$el.find('#' + this.fieldToSelectorMap.description).val(this.model.get('description'));

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
            //console.log("time1 --> " + time);
            //console.log("time2 --> " + time.length);
            //console.log("time3 --> " + time.indexOf("@"));
            //console.log("time4 --> " + time.indexOf("#"));

            if(time.indexOf("@") > 0 && time.indexOf("#") > 0){
                var arr1 = time.split("@");
                var arr2 = arr1[0].split(":");
                var week = arr1[1].split("#")[0];
                var arr3 = arr1[1].split("#")[1].split(":");

                $("#course-effort-hh").val(arr2[0]);
                $("#course-effort-mm").val(arr2[1]);
                $("#course-effort-week").val(week);
                $("#course-video-hh").val(arr3[0]);
                $("#course-video-mm").val(arr3[1]);
            }else if(time.indexOf("@") > 0){
                var arr1 = time.split("@");
                var arr2 = arr1[0].split(":");
                var week = arr1[1];

                $("#course-effort-hh").val(arr2[0]);
                $("#course-effort-mm").val(arr2[1]);
                $("#course-effort-week").val(week);
            }else if(time.indexOf("#") > 0){
                var arr1 = time.split("#");
                var arr2 = arr1[0].split(":");
                var arr3 = arr1[1].split(":");

                $("#course-effort-hh").val(arr2[0]);
                $("#course-effort-mm").val(arr2[1]);
                $("#course-video-hh").val(arr3[0]);
                $("#course-video-mm").val(arr3[1]);
            }else{
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
            if(total_time.toString().indexOf(".") > 0){
                var arr = total_time.toString().split(".");
                var hour = arr[0];
                var minute = Math.round(Number(arr[1]) / 10 * 60).toString().substr(0, 2);

                $("#Calculated").val(hour + "시간 " + minute + "분");
            }else{
                $("#Calculated").val(total_time + "시간");
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
            *   -수업주차,주간학습권장시간,총동영상 재생시간
                -수강신청시작일/마감일, 개강일/종강일
                -강좌 언어
                -강좌 불러오기 메뉴 비활성화(내보내기는 가능하게 그대로 둠)
            * */

            $("#course-start-date,#course-start-time").attr("disabled", true).css("background", "#ccc");
            $("#course-end-date,#course-end-time").attr("disabled", true).css("background", "#ccc");
            $("#course-enrollment-start-date,#course-enrollment-start-time").attr("disabled", true).css("background", "#ccc");
            $("#course-enrollment-end-date,#course-enrollment-end-time").attr("disabled", true).css("background", "#ccc");

            $("#course-language").attr("disabled", true).css("background", "#ccc");
            $("#field-course-effort input").attr("disabled", true).css("background", "#ccc");

        }

        /*
        if(start_date < now_utc){
            //console.log("disabled on1");
            $("#course-start-date,#course-start-time").attr("disabled", true).css("background", "#ccc");
        }
        if(end_date < now_utc){
            //console.log("disabled on2");
            $("#course-end-date,#course-end-time").attr("disabled", true).css("background", "#ccc");
        }
        if(enroll_start_date < now_utc){
            //console.log("disabled on3");
            $("#course-enrollment-start-date,#course-enrollment-start-time").attr("disabled", true).css("background", "#ccc");
        }
        if(enroll_end_date < now_utc){
            //console.log("disabled on4");
            $("#course-enrollment-end-date,#course-enrollment-end-time").attr("disabled", true).css("background", "#ccc");
        }
        */

        return this;
    },
    fieldToSelectorMap : {
        'language' : 'course-language',
        'start_date' : "course-start",
        'end_date' : 'course-end',
        'enrollment_start' : 'enrollment-start',
        'enrollment_end' : 'enrollment-end',
        'overview' : 'course-overview',
        'title': 'course-title',
        'subtitle': 'course-subtitle',
        'duration': 'course-duration',
        'description': 'course-description',
        'short_description' : 'course-short-description',
        'intro_video' : 'course-introduction-video',
        'effort' : "course-effort",
        'course_image_asset_path': 'course-image-url',
        'banner_image_asset_path': 'banner-image-url',
        'video_thumbnail_image_asset_path': 'video-thumbnail-image-url',
        'pre_requisite_courses': 'pre-requisite-course',
        'entrance_exam_enabled': 'entrance-exam-enabled',
        'entrance_exam_minimum_score_pct': 'entrance-exam-minimum-score-pct',
        'course_settings_learning_fields': 'course-settings-learning-fields',
        'add_course_learning_info': 'add-course-learning-info',
        'add_course_instructor_info': 'add-course-instructor-info',
        'course_learning_info': 'course-learning-info'
    },

    addLearningFields: function() {
        /*
        * Add new course learning fields.
        * */
        var existingInfo = _.clone(this.model.get('learning_info'));
        existingInfo.push('');
        this.model.set('learning_info', existingInfo);
    },

    addInstructorFields: function() {
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

    updateTime : function(e) {
        var now = new Date(),
            hours = now.getUTCHours(),
            minutes = now.getUTCMinutes(),
            currentTimeText = StringUtils.interpolate(
                gettext('{hours}:{minutes} (current UTC time)'),
                {
                    'hours': hours,
                    'minutes': minutes
                }
            );

        $(e.currentTarget).attr('title', currentTimeText);
    },
    updateModel: function(event) {
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
            if($(event.currentTarget).is(":checked")){
                this.$('.div-grade-requirements').show();
            }else{
                this.$('.div-grade-requirements').hide();
            }
            this.setField(event);
            break;
        case 'entrance-exam-minimum-score-pct':
            // If the val is an empty string then update model with default value.
            if ($(event.currentTarget).val() === '') {
                this.model.set('entrance_exam_minimum_score_pct', this.model.defaults.entrance_exam_minimum_score_pct);
            }
            else {
                this.setField(event);
            }
            break;
        case 'pre-requisite-course':
            var value = $(event.currentTarget).val();
            value = value == "" ? [] : [value];
            this.model.set('pre_requisite_courses', value);
            break;
        // Don't make the user reload the page to check the Youtube ID.
        // Wait for a second to load the video, avoiding egregious AJAX calls.
        case 'course-introduction-video':
            this.clearValidationErrors();
            var previewsource = this.model.set_videosource($(event.currentTarget).val());
            clearTimeout(this.videoTimer);
            this.videoTimer = setTimeout(_.bind(function() {
                this.$el.find(".current-course-introduction-video iframe").attr("src", previewsource);
                if (this.model.has('intro_video')) {
                    this.$el.find('.remove-course-introduction-video').show();
                }
                else {
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
        case 'course-description':
        case 'course-short-description':
            this.setField(event);
            break;
        default: // Everything else is handled by datepickers and CodeMirror.
            break;
        }
    },
    updateImageField: function(event, image_field, selector) {
        this.setField(event);
        var url = $(event.currentTarget).val();
        var image_name = _.last(url.split('/'));
        // If image path is entered directly, we need to strip the asset prefix
        image_name = _.last(image_name.split('block@'));
        this.model.set(image_field, image_name);
        this.updateImagePreview(event.currentTarget, selector);
    },
    updateImagePreview: function(imagePathInputElement, previewSelector) {
        // Wait to set the image src until the user stops typing
        clearTimeout(this.imageTimer);
        this.imageTimer = setTimeout(function() {
            $(previewSelector).attr('src', $(imagePathInputElement).val());
        }, 1000);
    },
    removeVideo: function(event) {
        event.preventDefault();
        if (this.model.has('intro_video')) {
            this.model.set_videosource(null);
            this.$el.find(".current-course-introduction-video iframe").attr("src", "");
            this.$el.find('#' + this.fieldToSelectorMap['intro_video']).val("");
            this.$el.find('.remove-course-introduction-video').hide();
        }
    },
    codeMirrors : {},
    updateOverview: function () {
        console.log("codeMirrorizeTest called2");
        this.model.set('overview', '<h3>Hello, World!!!!</h3>');
        this.render();
    },
    showOverviewLayer: function(event) {
        event.preventDefault();
        console.log("showOverviewLayer called2");

    },
    codeMirrorize: function (e, forcedTarget) {

        var thisTarget;
        if (forcedTarget) {
            thisTarget = forcedTarget;
            thisTarget.id = $(thisTarget).attr('id');
        } else if (e !== null) {
            thisTarget = e.currentTarget;
        } else
        {
            // e and forcedTarget can be null so don't deference it
            // This is because in cases where we have a marketing site
            // we don't display the codeMirrors for editing the marketing
            // materials, except we do need to show the 'set course image'
            // workflow. So in this case e = forcedTarget = null.
            return;
        }

        if (!this.codeMirrors[thisTarget.id]) {

            var cachethis = this;
            var field = this.selectorToField[thisTarget.id];
            this.codeMirrors[thisTarget.id] = CodeMirror.fromTextArea(thisTarget, {
                mode: "text/html", lineNumbers: true, lineWrapping: true});
            this.codeMirrors[thisTarget.id].on('change', function (mirror) {
                    mirror.save();
                    cachethis.clearValidationErrors();
                    var newVal = mirror.getValue();
                    if (cachethis.model.get(field) != newVal) {
                        cachethis.setAndValidate(field, newVal);
                    }
            });

            //codeMirror readOnly set
            if(this.isEditable())
                this.codeMirrors[thisTarget.id].setOption("readOnly", true);

        }else{
            $("#field-course-overview .CodeMirror").remove();
            CodeMirror.fromTextArea(thisTarget, {mode: "text/html", lineNumbers: true, lineWrapping: true});
        }
    },

    revertView: function() {

        //alert('revertView s!!!!');
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
                self.licenseModel.setFromString(self.model.get("license"), {silent: true});
                self.licenseView.render()
            },
            reset: true,
            silent: true});

        //alert('revertView e!!!!');

    },
    setAndValidate: function(attr, value) {
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
        // We always call showNotificationBar with the same args, just
        // delegate to superclass
        ValidatingView.prototype.showNotificationBar.call(this,
                                                          this.save_message,
                                                          _.bind(this.saveView, this),
                                                          _.bind(this.revertView, this));
    },

    uploadImage: function(event) {
        event.preventDefault();
        var title = "", selector = "", image_key = "", image_path_key = "";
        switch (event.currentTarget.id) {
            case 'upload-course-image':
                title = gettext("Upload your course image.");
                selector = "#course-image";
                image_key = 'course_image_name';
                image_path_key = 'course_image_asset_path';
                break;
            case 'upload-banner-image':
                title = gettext("Upload your banner image.");
                selector = "#banner-image";
                image_key = 'banner_image_name';
                image_path_key = 'banner_image_asset_path';
                break;
            case 'upload-video-thumbnail-image':
                title = gettext("Upload your video thumbnail image.");
                selector = "#video-thumbnail-image";
                image_key = 'video_thumbnail_image_name';
                image_path_key = 'video_thumbnail_image_asset_path';
                break;
        }

        var upload = new FileUploadModel({
            title: title,
            message: gettext("Files must be in JPEG or PNG format."),
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
        this.showNotificationBar();
        this.model.set("license", this.licenseModel.toString());
    }
});

return DetailsView;

}); // end define()