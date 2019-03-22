;(function (define) {

    define([
        'underscore',
        'backbone',
        'js/discovery/models/course_card',
        'js/discovery/models/facet_option',
    ], function (_, Backbone, CourseCard, FacetOption) {
        'use strict';

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
                this.courseCards.add(_.pluck(courses, 'data'));

                this.set({
                    totalCount: response.total,
                    latestCount: courses.length
                });

                var options = this.facetOptions;

                _(facets).each(function (obj, key) {
                    // console.log(obj);
                    if (key == 'org') {

                        var count2 = 0;
                        var count3 = 0;

                        // skp, smu hard coding
                        //console.log("_(obj.terms) ==>"+_(obj.terms));

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

                    } else if (key == 'fourth_industry_yn' || key == 'linguistics' || key == 'job_edu_yn') {
                        // 4차 산업, 직업교육, 한국학을 하나의 카테고리로 표현하고 해당하는 내용만 표시되도록 함
                        _(obj.terms).each(function (count, term) {
                            let v;
                            if (key == 'fourth_industry_yn' && term === 'Y')
                                v = 'fourth_industry_y'
                            else if (key == 'job_edu_yn' && term == 'Y')
                                v = 'job_edu_y'
                            else if (key == 'linguistics' && term == 'Y')
                                v = 'linguistics_y'
                            else
                                return true;

                            options.add({
                                facet: 'etc',
                                term: v,
                                count: count
                            }, {merge: false});
                        });

                    } else {
                        _(obj.terms).each(function (count, term) {
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