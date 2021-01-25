;(function (define) {

define([
    'jquery',
    'underscore',
    'backbone',
    'gettext',
    'date'
], function ($, _, Backbone, gettext, Date) {
    'use strict';

    function formatDate(date) {
        return dateUTC(date).toString('yyyy/MM/dd');
        //return gettext(dateUTC(date).toString('yyyy/MM/dd'));
    }

    function formatDateNowFull(date) {
        return new Date(date).toString('yyyyMMddHHmmss');
        //return gettext(dateUTC(date).toString('yyyy/MM/dd'));
    }


    function formatDateFull(date) {
        return dateUTC(date).toString('yyyyMMddHHmmss');
        //return gettext(dateUTC(date).toString('yyyy/MM/dd'));
    }

    // Return a date object using UTC time instead of local time
    function dateUTC(date) {
        return new Date(
            date.getUTCFullYear(),
            date.getUTCMonth(),
            date.getUTCDate(),
            date.getUTCHours(),
            date.getUTCMinutes(),
            date.getUTCSeconds()
        );
    }

    function formatTeacherName(teacher_name) {
        var teacher_str = '';
        if(teacher_name == null || teacher_name == 'all'){
            teacher_str = '';
        }else if(teacher_name.indexOf(',') != -1 && teacher_name.split(',').length != 1){
            const t_arr = teacher_name.split(',');
            teacher_str = _.template(gettext('<%= t_name %> and <%= t_len %> others'))({t_name: t_arr[0], t_len: t_arr.length -1});
        }else{
            teacher_str = teacher_name;
        }

        return teacher_str
    }

    return Backbone.View.extend({

        tagName: 'li',
        templateId: '#course_card-tpl',
        templateId_mobile: '#mobile_course_card-tpl',
        className: 'courses-listing-item',

        initialize: function () {
            if($('#course_card-tpl').length == 1) {
                this.tpl = _.template($(this.templateId).html());
            }
            else if ($('#mobile_course_card-tpl').length == 1) {
                this.tpl = _.template($(this.templateId_mobile).html());
            }
        },

        render: function () {
            var data = _.clone(this.model.attributes);

            //var nDate = formatDate(new Date());
            //var sDate = formatDate(new Date(data.start));
            //var eDate = formatDate(new Date(data.end));

            // 강좌 시작일의 값이 기본적으로 KST 로 조회되면서 비교 조건 수정
            var nDate = formatDateNowFull(new Date());
            var sDate = formatDateFull(new Date(data.start));
            var eDate = formatDateFull(new Date(data.end));

            data.start = formatDate(new Date(data.start));
            data.enrollment_start = formatDate(new Date(data.enrollment_start));
            data.end = formatDate(new Date(data.end));
            data.teacher_name = formatTeacherName(data.teacher_name);

            console.log('------------------------------------------ s');
            console.log('nDate: ' + nDate);
            console.log('sDate: ' + sDate);
            console.log('eDate: ' + eDate);
            console.log('------------------------------------------ s');

            if (eDate != null && nDate > eDate) {
                data.course_end = 'Y';
            } else {
                data.course_end = 'N';
            }

            if (sDate == null || eDate == null) {
                data.status = 'none';
            } else if (nDate < sDate) {
                data.status = 'ready';
            } else if (nDate < eDate) {
                data.status = 'ing';
            } else if (eDate > nDate){
                data.status = 'end';
            }else{
                data.status = 'none';
            }

            // org translate
            var lang = document.documentElement.lang;
            data.org_name = gettext(data.org);
            if(data.org_kname != null && lang == 'ko-kr'){
                data.org_name = data.org_kname;
            } else if(data.org_ename != null && lang == 'en'){
                data.org_name = data.org_ename;
            }

            this.$el.html(this.tpl(data));
            return this;
        }

    });

});

})(define || RequireJS.define);
