;(function (define) {

    define([
        'underscore',
        'backbone',
        'js/discovery/models/course_card',
        'js/discovery/models/facet_option',
    ], function (_, Backbone, CourseCard, FacetOption) {
        'use strict';
        var facet_row_temp = {};
        var facet_row_temp_set = {};
        var facet_row_set = {};


        return Backbone.Model.extend({
            url: '/search/course_discovery/',
            jqhxr: null,

            defaults: {
                totalCount: 0,
                latestCount: 0
            },

            initialize: function () {
                this.courseCards = new Backbone.Collection([], {model: CourseCard});
                this.facetOptions = new Backbone.Collection([], {model: FacetOption});
            },

            parse: function (response) {
                var courses = response.results || [];
                var facets = response.facets || {};

                Date.prototype.addHours = function (h) {
                    this.setTime(this.getTime() + (h * 60 * 60 * 1000));
                    return this;
                }
                for (var i = 0; i < courses.length; i++) {
                    console.log("courses object courses[i]");
                    let enrollment_start = courses[i].data.enrollment_start;
                    let enrollment_end = courses[i].data.enrollment_end;
                    let start = courses[i].data.start;
                    let end = courses[i].data.end;

                    let kst_enrollment_start = new Date(enrollment_start).addHours(9);
                    let kst_enrollment_end = new Date(enrollment_end).addHours(9);
                    let kst_start = new Date(start).addHours(9);
                    let kst_end = new Date(end).addHours(9);

                    courses[i].data.enrollment_start = kst_enrollment_start;
                    courses[i].data.enrollment_end = kst_enrollment_end;
                    courses[i].data.start = kst_start;
                    courses[i].data.end = kst_end;
                }

                let coursesByEnd = courses.sort((a,b) => (b.data.start - a.data.start));
                // this.courseCards.add(_.pluck(courses, 'data'));
                this.courseCards.add(_.pluck(coursesByEnd, 'data'));


                this.set({
                    totalCount: response.total,
                    latestCount: coursesByEnd.length,
                    // latestCount: courses.length
                });

                var options = this.facetOptions;
                var cnt = 0;

                facet_row_temp = {};
                facet_row_temp_set = {};
                facet_row_set = {};

                _(facets).each(function (obj, key) {
                    console.log("obj: " + obj + ", key: " + key + "  [case 1 ]");
                    if (key == 'org') {
                        var count2 = 0;
                        var count3 = 0;

                        // skp, smu hard coding
                        console.log("_(obj.terms) ==>"+_(obj.terms));
                        _(obj.terms).each(function (count, term) {
                            //console.log("1 _(obj.terms).each --------" + "term:" + term + ", count:" + count);
                            if (term.match(/^SKP.*/)) {
                                count2 += count;
                                return true;
                            }
                            if (term === 'SMUk' || term === 'SMUCk') {
                                count3 += count;
                                return true;
                            }
                            options.add({
                                facet: key,
                                term: term,
                                count: count
                            }, {merge: true});
                        });

                        // skp, smu hard coding
                        if (count2 > 0) {
                            options.add({
                                facet: key,
                                term: 'SKP',
                                count: count2
                            }, {merge: true});
                        }
                        if (count3 > 0) {
                            options.add({
                                facet: key,
                                term: 'SMUk',
                                count: count3
                            }, {merge: true});
                        }
                    } else if (key == 'classfysub' || key == 'middle_classfysub') {
                        return true;
                    } else {
                        _(obj.terms).each(function (count, term) {
                            if (key == 'fourth_industry_yn' && (term == 'Y' || term == 'y'))
                                term = 'fourth_industry_y';
                            else if (key == 'job_edu_yn' && (term == 'Y' || term == 'y'))
                                term = 'job_edu_y';
                            else if (key == 'ai_sec_yn' && (term == 'Y' || term == 'y'))
                                term = 'ai_sec_y';
                            else if (key == 'basic_science_sec_yn' && (term == 'Y' || term == 'y'))
                                term = 'basic_science_sec_y';
                            else if (key == 'ribbon_yn' && (term == 'Y' || term == 'y'))
                                term = 'ribbon_y';
                            else if (key == 'ribbon_yn' && (term == 'N' || term == 'n'))
                                term = 'ribbon_n';
                            else if (key == 'liberal_arts_yn' && (term == 'Y' || term == 'y' || term == 'liberal_arts_y'))
                                term = 'liberal_arts_y';
                            else if (key == 'career_readiness_competencies_yn' && (term == 'Y' || term == 'y' || term == 'career_readiness_competencies_y'))
                                term = 'career_readiness_competencies_y';
                            else if (key == 'matchup_yn' && (term == 'Y' || term == 'y' || term == 'matchup_y'))
                                term = 'matchup_y';
                            else if (key == 'matchup_yn' && (term == 'N' || term == 'n' || term == 'matchup_n'))
                                term = 'matchup_n';
                            options.add({
                                facet: key,
                                term: term,
                                count: count
                            }, {merge: true});
                        });
                    }
                });

                /* 융복합의 경우 하위 분류에 해당하는 내용으로 데이터를 업데이트 */
                _(facets).each(function (obj, key) {
                    if (key == 'classfysub') {
                        _(obj.terms).each(function (count, term) {
                            // 융복합이 아닌경우 term 이 공백으로 넘어옴
                            if (term) {
                                let t = term.split(',');
                                for (let i in t) {
                                    if (options.get(t[i])) {
                                        options.get(t[i]).attributes.count += 1;
                                    } else {
                                        options.add({
                                            facet: 'classfy',
                                            term: t[i],
                                            count: 1
                                        }, {merge: true});
                                    }
                                }
                            }
                        });

                    } else if (key == 'middle_classfysub') {
                        _(obj.terms).each(function (count, term) {
                            // 융복합이 아닌경우 term 이 공백으로 넘어옴
                            if (term) {
                                let t = term.split(',');
                                for (let i in t) {
                                    if (options.get(t[i])) {
                                        options.get(t[i]).attributes.count += 1;
                                    } else {
                                        options.add({
                                            facet: 'middle_classfy',
                                            term: t[i],
                                            count: 1
                                        }, {merge: true});
                                    }
                                }
                            }
                        });
                    }
                });

            },

            reset: function () {
                this.set({
                    totalCount: 0,
                    latestCount: 0
                });
                this.courseCards.reset();
                this.facetOptions.reset();
            },

            latest: function () {
                return this.courseCards.last(this.get('latestCount'));
            }

        });

    });


})(define || RequireJS.define);
