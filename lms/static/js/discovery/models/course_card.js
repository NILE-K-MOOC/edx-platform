(function(define) {
    define(['backbone'], function(Backbone) {
        'use strict';

        return Backbone.Model.extend({
            defaults: {
                modes: [],
                course: '',
                enrollment_start: '',
                number: '',
                content: {
                    display_name: '',
                    overview: '',
                    number: '',
                    catalog_visibility: ''
                },
                start: '',
                image_url: '',
                org: '',
                org_kname: '',
                org_ename: '',
                teacher_name: '',
                id: '',
                status: '',
                audit_yn: '',
                ribbon_yn: '',
                ribbon_year:'',
                matchup_yn:''
            }
        });
    });
}(define || RequireJS.define));
