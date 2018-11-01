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

            // console.log(data);

            //var nDate = formatDate(new Date());
            //var sDate = formatDate(new Date(data.start));
            //var eDate = formatDate(new Date(data.end));

            var nDate = formatDateFull(new Date());
            var sDate = formatDateFull(new Date(data.start));
            var eDate = formatDateFull(new Date(data.end));

            data.start = formatDate(new Date(data.start));
            data.enrollment_start = formatDate(new Date(data.enrollment_start));
            data.end = formatDate(new Date(data.end));

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
            } else if (eDate < nDate){
                data.status = 'end';
            }else{
                data.status = 'none';
            }
            this.$el.html(this.tpl(data));
            return this;
        }

    });

});

})(define || RequireJS.define);
