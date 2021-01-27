define(['domReady', 'jquery', 'underscore', 'js/views/utils/create_course_utils', 'common/js/components/utils/view_utils'],
    function(domReady, $, _, CreateCourseUtilsFactory, ViewUtils) {
        var CreateCourseUtils = new CreateCourseUtilsFactory({
            name: '.rerun-course-name',
            org: '.rerun-course-org',
            number: '.rerun-course-number',
            run: '.rerun-course-run',
            save: '.rerun-course-save',
            errorWrapper: '.wrapper-error',
            errorMessage: '#course_rerun_error',
            tipError: 'span.tip-error',
            error: '.error',
            allowUnicode: '.allow-unicode-course-id',
            classfy: '.rerun-course-classfy',
            classfy_plus: '.classfy_plus',
            middle_classfy: '.middle_classfy',
            teacher_name: '.teacher_name',
            preview_video: '.preview_video',
        }, {
            shown: 'is-shown',
            showing: 'is-showing',
            hiding: 'is-hidden',
            disabled: 'is-disabled',
            error: 'error'
        });

        var saveRerunCourse = function(e) {
            e.preventDefault();

            if (CreateCourseUtils.hasInvalidRequiredFields()) {
                return;
            }

            var $newCourseForm = $(this).closest('#rerun-course-form');
            var display_name = $newCourseForm.find('.rerun-course-name').val();
            var org = $newCourseForm.find('.rerun-course-org').val();
            var number = $newCourseForm.find('.rerun-course-number').val();
            var run = $newCourseForm.find('.rerun-course-run').val();
            var classfy = $newCourseForm.find('.rerun-course-classfy').val()
            var classfy_plus = $newCourseForm.find('.rerun-course-classfy_plus').val()
            var preview_video = $newCourseForm.find('.rerun-course-preview_video').val()
            var middle_classfy = $newCourseForm.find('.rerun-course-middle_classfy').val()
            var teacher_name = $newCourseForm.find('.rerun-course-teacher_name').val()
            var course_period = $newCourseForm.find('.rerun-course-course_period').val()

            course_info = {
                source_course_key: source_course_key,
                org: org,
                number: number,
                display_name: display_name,
                run: run,
                classfy: classfy,
                classfy_plus: classfy_plus,
                middle_classfy: middle_classfy,
                teacher_name: teacher_name,
                course_period: course_period,
                preview_video: preview_video ,
            };

            analytics.track('Reran a Course', course_info);
            CreateCourseUtils.create(course_info, function(errorMessage) {
                $('.wrapper-error').addClass('is-shown').removeClass('is-hidden');
                $('#course_rerun_error').html('<p>' + errorMessage + '</p>');
                $('.rerun-course-save').addClass('is-disabled').attr('aria-disabled', true).removeClass('is-processing').html(gettext('Create Re-run'));
                $('.action-cancel').removeClass('is-hidden');
            });

            // Go into creating re-run state
            $('.rerun-course-save').addClass('is-disabled').attr('aria-disabled', true).addClass('is-processing').html(
               '<span class="icon fa fa-refresh fa-spin" aria-hidden="true"></span>' + gettext('Processing Re-run Request')  // eslint-disable-line max-len
            );
            $('.action-cancel').addClass('is-hidden');
        };

        var cancelRerunCourse = function(e) {
            e.preventDefault();
            // Clear out existing fields and errors
            $('.rerun-course-run').val('');
            $('#course_rerun_error').html('');
            $('wrapper-error').removeClass('is-shown').addClass('is-hidden');
            $('.rerun-course-save').off('click');
            ViewUtils.redirect('/course/');
        };

        var onReady = function() {
            var $cancelButton = $('.rerun-course-cancel');
            var $courseRun = $('.rerun-course-run');
            $courseRun.focus().select();
            $('.rerun-course-save').on('click', saveRerunCourse);
            $cancelButton.bind('click', cancelRerunCourse);
            $('.cancel-button').bind('click', cancelRerunCourse);

            CreateCourseUtils.configureHandlers();
        };

        domReady(onReady);

        // Return these functions so that they can be tested
        return {
            saveRerunCourse: saveRerunCourse,
            cancelRerunCourse: cancelRerunCourse,
            onReady: onReady
        };
    });
