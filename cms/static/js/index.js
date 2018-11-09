define(["domReady", "jquery", "underscore", "js/utils/cancel_on_escape", "js/views/utils/create_course_utils",
    "js/views/utils/create_library_utils", "common/js/components/utils/view_utils"],
    function (domReady, $, _, CancelOnEscape, CreateCourseUtilsFactory, CreateLibraryUtilsFactory, ViewUtils) {
        "use strict";
        var CreateCourseUtils = new CreateCourseUtilsFactory({
            name: '.new-course-name',
            org: '.new-course-org',
            number: '.new-course-number',
            run: '.new-course-run',
            save: '.new-course-save',
            errorWrapper: '.create-course .wrap-error',
            errorMessage: '#course_creation_error',
            tipError: '.create-course span.tip-error',
            error: '.create-course .error',
            allowUnicode: '.allow-unicode-course-id',
            classfy: '.new-course-classfy',
            middle_classfy: '.new-course-middle-classfy',

            classfy_sub1: '.new-course-classfy-sub1',
            classfy_sub2: '.new-course-classfy-sub2',
            classfy_sub3: '.new-course-classfy-sub3',
            middle_classfy_sub1: '.new-course-middle-classfy-sub1',
            middle_classfy_sub2: '.new-course-middle-classfy-sub2',
            middle_classfy_sub3: '.new-course-middle-classfy-sub3',
            linguistics: '.new-course-linguistics',
            course_period: '.new-course-period'
        }, {
            shown: 'is-shown',
            showing: 'is-showing',
            hiding: 'is-hiding',
            disabled: 'is-disabled',
            error: 'error'
        });

        var CreateLibraryUtils = new CreateLibraryUtilsFactory({
            name: '.new-library-name',
            org: '.new-library-org',
            number: '.new-library-number',
            save: '.new-library-save',
            errorWrapper: '.create-library .wrap-error',
            errorMessage: '#library_creation_error',
            tipError: '.create-library  span.tip-error',
            error: '.create-library .error',
            allowUnicode: '.allow-unicode-library-id'
        }, {
            shown: 'is-shown',
            showing: 'is-showing',
            hiding: 'is-hiding',
            disabled: 'is-disabled',
            error: 'error'
        });

        var saveNewCourse = function (e) {
            e.preventDefault();

            if (CreateCourseUtils.hasInvalidRequiredFields()) {
                return;
            }

            var $newCourseForm = $(this).closest('#create-course-form');
            var display_name = $newCourseForm.find('.new-course-name').val();
            var org = $newCourseForm.find('.new-course-org').val();
            var number = $newCourseForm.find('.new-course-number').val();
            var run = $newCourseForm.find('.new-course-run').val();

            var classfy = $newCourseForm.find(".new-course-classfy").val();
            var middle_classfy = $newCourseForm.find(".new-course-middle-classfy").val();
            var difficult_degree = "";

            // mih update
            var csub1 = $newCourseForm.find(".new-course-classfy-sub1").val();
            var csub2 = $newCourseForm.find(".new-course-classfy-sub2").val();
            var csub3 = $newCourseForm.find(".new-course-classfy-sub3").val();

            var msub1 = $newCourseForm.find(".new-course-middle-classfy-sub1").val();
            var msub2 = $newCourseForm.find(".new-course-middle-classfy-sub2").val();
            var msub3 = $newCourseForm.find(".new-course-middle-classfy-sub3").val();

            var classfysub = "";
            //var classfysub = csub1+"+"+csub2+"+"+csub3;

            var middle_classfysub = "";
            //var middle_classfysub = msub1+"+"+msub2+"+"+msub3;


            if(csub1 != null && csub1 != "" && csub1 != "null")
                classfysub = csub1;
            if(csub2 != null && csub2 != "" && csub2 != "null")
                classfysub += ","+csub2;
            if(csub3 != null && csub3 != "" && csub3 != "null")
                classfysub += ","+csub3;

            if(msub1 != null && msub1 != "" && msub1 != "null")
                middle_classfysub = msub1;
            if(msub2 != null && msub2 != "" && msub2 != "null")
                middle_classfysub += ","+msub2;
            if(msub3 != null && msub3 != "" && msub3 != "null")
                middle_classfysub += ","+msub3;
            var linguistics = $newCourseForm.find(".new-course-linguistics").val();
            var period = $newCourseForm.find(".new-course-period").val();


            var course_info = {
                org: org,
                number: number,
                display_name: display_name,
                run: run,
                classfy: classfy,
                classfysub: classfysub,                 // Maeng Ilhee add
                middle_classfy: middle_classfy,
                middle_classfysub: middle_classfysub,   // Maeng Ilhee add
                difficult_degree: difficult_degree,     // Maeng Ilhee add
                linguistics: linguistics,
                period: period
            };

            $("span.tip").css({"color": "#ccc"});

            if (!middle_classfy || middle_classfy == "null")
                $("span[id='tip-new-course-classfy']").css({"color": "#b20610"});

            if (!linguistics)
                $("span[id='tip-new-course-linguistics']").css({"color": "#b20610"});

            if (!period)
                $("span[id='tip-new-course-period']").css({"color": "#b20610"});

            if (!classfy || !middle_classfy || middle_classfy == "null" || !linguistics || !period){
                console.log(classfy);
                console.log(classfysub);            // Maeng Ilhee add
                console.log(middle_classfy);
                console.log(middle_classfysub);     // Maeng Ilhee add
                console.log(difficult_degree);      // Maeng Ilhee add
                console.log(linguistics);
                console.log(period);

                return;
            }

            analytics.track('Created a Course', course_info);
            CreateCourseUtils.create(course_info, function (errorMessage) {
                $('.create-course .wrap-error').addClass('is-shown');
                $('#course_creation_error').html('<p>' + errorMessage + '</p>');
                $('.new-course-save').addClass('is-disabled').attr('aria-disabled', true);
            });

        };

        var makeCancelHandler = function (addType) {
            return function(e) {
                e.preventDefault();
                $('.new-'+addType+'-button').removeClass('is-disabled').attr('aria-disabled', false);
                $('.wrapper-create-'+addType).removeClass('is-shown');
                // Clear out existing fields and errors
                $('#create-'+addType+'-form input[type=text]').val('');
                $('#'+addType+'_creation_error').html('');
                $('.create-'+addType+' .wrap-error').removeClass('is-shown');
                $('.new-'+addType+'-save').off('click');
            };
        };

        var addNewCourse = function (e) {
            e.preventDefault();
            $('.new-course-button').addClass('is-disabled').attr('aria-disabled', true);
            $('.new-course-save').addClass('is-disabled').attr('aria-disabled', true);
            var $newCourse = $('.wrapper-create-course').addClass('is-shown');
            var $cancelButton = $newCourse.find('.new-course-cancel');
            var $courseName = $('.new-course-name');
            $courseName.focus().select();
            $('.new-course-save').on('click', saveNewCourse);
            $cancelButton.bind('click', makeCancelHandler('course'));
            CancelOnEscape($cancelButton);
            //CreateCourseUtils.setupOrgAutocomplete();
            CreateCourseUtils.configureHandlers();
        };

        var saveNewLibrary = function (e) {
            e.preventDefault();

            if (CreateLibraryUtils.hasInvalidRequiredFields()) {
                return;
            }

            var $newLibraryForm = $(this).closest('#create-library-form');
            var display_name = $newLibraryForm.find('.new-library-name').val();
            var org = $newLibraryForm.find('.new-library-org').val();
            var number = $newLibraryForm.find('.new-library-number').val();

            var lib_info = {
                org: org,
                number: number,
                display_name: display_name,
            };

            analytics.track('Created a Library', lib_info);
            CreateLibraryUtils.create(lib_info, function (errorMessage) {
                $('.create-library .wrap-error').addClass('is-shown');
                $('#library_creation_error').html('<p>' + errorMessage + '</p>');
                $('.new-library-save').addClass('is-disabled').attr('aria-disabled', true);
            });
        };

        var addNewLibrary = function (e) {
            e.preventDefault();
            $('.new-library-button').addClass('is-disabled').attr('aria-disabled', true);
            $('.new-library-save').addClass('is-disabled').attr('aria-disabled', true);
            var $newLibrary = $('.wrapper-create-library').addClass('is-shown');
            var $cancelButton = $newLibrary.find('.new-library-cancel');
            var $libraryName = $('.new-library-name');
            $libraryName.focus().select();
            $('.new-library-save').on('click', saveNewLibrary);
            $cancelButton.bind('click', makeCancelHandler('library'));
            CancelOnEscape($cancelButton);

            CreateLibraryUtils.configureHandlers();
        };

        var showTab = function(tab) {
          return function(e) {
            e.preventDefault();
            $('.courses-tab').toggleClass('active', tab === 'courses');
            $('.libraries-tab').toggleClass('active', tab === 'libraries');
            $('.programs-tab').toggleClass('active', tab === 'programs');

            // Also toggle this course-related notice shown below the course tab, if it is present:
            $('.wrapper-creationrights').toggleClass('is-hidden', tab !== 'courses');
          };
        };

        var onReady = function () {

            console.log('js/index.js onReady');

            $('.new-course-button').bind('click', addNewCourse);
            $('.new-library-button').bind('click', addNewLibrary);

            $('.dismiss-button').bind('click', ViewUtils.deleteNotificationHandler(function () {
                ViewUtils.reload();
            }));

            $('.action-reload').bind('click', ViewUtils.reload);

            $('#course-index-tabs .courses-tab').bind('click', showTab('courses'));
            $('#course-index-tabs .libraries-tab').bind('click', showTab('libraries'));
            $('#course-index-tabs .programs-tab').bind('click', showTab('programs'));
        };

        domReady(onReady);

        return {
            onReady: onReady
        };
    });
