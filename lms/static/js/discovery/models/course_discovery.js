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

                    //console.log("obj:" + obj + ", key:" + key);

                    if (key == 'org') {

                        var count2 = 0;
                        var count3 = 0;
                        var term2 = "sum_test";

                        // skp, smu hard coding
                        _(obj.terms).each(function (count, term) {
                            if (term.match(/^SKP.*/)) {
                                count2 += count;
                                return true;
                            }
                            //if (term === 'SMUk' || term === 'SMUCk') {
                            //    count3 += count;
                            //    return true;
                            //}
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
